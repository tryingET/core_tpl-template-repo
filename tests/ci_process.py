#!/usr/bin/env python3
"""Bounded Linux managed-group capture, independent of observational IO failures.

Only the new process group is managed. Detached sessions and SIGKILL/runner loss
remain outside the cleanup/evidence guarantee. Raw logs are not redacted.
"""
from __future__ import annotations

import codecs
from contextlib import contextmanager
import ctypes
import errno
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

if __package__:
    from .ci_profile_io import checked_target, open_artifact
else:
    from ci_profile_io import checked_target, open_artifact

ROOT = Path(__file__).resolve().parents[1]
GRACE_SECONDS = 0.3
KILL_WAIT_SECONDS = 1.0
READ_BYTES = 65536
FINAL_DRAIN_BYTES = 262144
FINAL_DRAIN_ITERATIONS = 16
FINAL_DRAIN_SECONDS = 0.05


def error_record(stage, failure):
    return {"stage": stage, "type": type(failure).__name__,
            "errno": getattr(failure, "errno", None), "message": str(failure)}


def write_json(path, packet):
    with open_artifact(path) as output:
        json.dump(packet, output, indent=2, sort_keys=True)
        output.write("\n")


@contextmanager
def adopt_descendants():
    """Adopt orphaned group members and restore the caller's subreaper setting."""
    if sys.platform != "linux":
        raise ValueError("managed capture requires Linux child-subreaper support")
    libc = ctypes.CDLL(None, use_errno=True)
    previous = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(previous), 0, 0, 0) or libc.prctl(36, 1, 0, 0, 0):
        raise OSError(ctypes.get_errno(), "cannot establish child subreaper")
    try:
        yield
    finally:
        if libc.prctl(36, previous.value, 0, 0, 0):
            raise OSError(ctypes.get_errno(), "cannot restore child subreaper")


def shell_status(code):
    return 128 - code if code is not None and code < 0 else code


class Drain:
    """One nonblocking read per call; an IO failure disables further draining."""
    def __init__(self, pipe, output, selector):
        self.pipe = pipe
        self.output = output
        self.selector = selector
        self.decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self.errors = []
        self.disabled = False
        self.eof = False
        os.set_blocking(pipe.fileno(), False)
        selector.register(pipe, selectors.EVENT_READ)

    def fail(self, stage, failure):
        self.errors.append(error_record(stage, failure))
        self.disabled = True

    def pump(self, wait, *, display=True):
        if self.disabled or self.eof:
            return 0
        try:
            ready = self.selector.select(wait)
        except OSError as failure:
            self.fail("select", failure)
            return 0
        if not ready:
            return 0
        try:
            block = os.read(self.pipe.fileno(), READ_BYTES)
        except BlockingIOError:
            return 0
        except OSError as failure:
            self.fail("read", failure)
            return 0
        if not block:
            self.eof = True
            return 0
        try:
            if self.output.buffer.write(block) != len(block):
                raise OSError(errno.EIO, "short profile-log write")
            self.output.buffer.flush()
        except OSError as failure:
            self.fail("log.write/flush", failure)
            return len(block)
        if display:
            try:
                sys.stdout.write(self.decoder.decode(block))
                sys.stdout.flush()
            except OSError as failure:
                self.fail("display", failure)
        return len(block)

    def finish_display(self):
        if self.disabled:
            return
        try:
            sys.stdout.write(self.decoder.decode(b"", final=True))
            sys.stdout.flush()
        except OSError as failure:
            self.fail("display.finish", failure)


def teardown(process, pump, signum):
    """Signal/grace/KILL/reap never depends on successful reading or logging."""
    reaped = 0
    drain_errors = []
    draining = True

    def alive():
        nonlocal reaped
        if process.poll() is not None:
            while True:
                try:
                    pid, _ = os.waitpid(-process.pid, os.WNOHANG)
                except ChildProcessError:
                    break
                if not pid:
                    break
                reaped += 1
        try:
            os.killpg(process.pid, 0)
            return True
        except ProcessLookupError:
            return False

    def send(value):
        try:
            os.killpg(process.pid, value)
        except ProcessLookupError:
            pass

    def safe_pump():
        nonlocal draining
        if not draining:
            return 0
        try:
            return pump(0)
        except BaseException as failure:
            drain_errors.append(error_record("teardown.drain", failure))
            draining = False
            return 0

    def wait_until(deadline):
        while alive() and time.perf_counter() < deadline:
            safe_pump()
            # Failed/disabled/nonblocking draining must not become a busy loop.
            time.sleep(min(0.01, max(0, deadline - time.perf_counter())))

    escalated = False
    if alive():
        send(signum)
        wait_until(time.perf_counter() + GRACE_SECONDS)
        if alive():
            escalated = True
            send(signal.SIGKILL)
            wait_until(time.perf_counter() + KILL_WAIT_SECONDS)
    gone = not alive()
    # An escaped setsid writer may keep this pipe readable forever. Cap all
    # final reads and then close the pipe, without pretending the log is complete.
    deadline = time.perf_counter() + FINAL_DRAIN_SECONDS
    drained_bytes = iterations = 0
    while (draining and drained_bytes < FINAL_DRAIN_BYTES and
           iterations < FINAL_DRAIN_ITERATIONS and time.perf_counter() < deadline):
        count = safe_pump()
        if not count:
            break
        iterations += 1
        drained_bytes += count
    limited = (drained_bytes >= FINAL_DRAIN_BYTES or iterations >= FINAL_DRAIN_ITERATIONS or
               time.perf_counter() >= deadline)
    return {"initial_signal": int(signum), "escalated": escalated,
            "descendants_reaped": reaped, "process_group_gone": gone,
            "grace_seconds": GRACE_SECONDS, "kill_wait_seconds": KILL_WAIT_SECONDS,
            "drain_errors": drain_errors, "final_drain_bytes": drained_bytes,
            "final_drain_iterations": iterations, "final_drain_limited": limited}


def capture(command, target, *, env=None, root=ROOT, artifact_opener=None, packet_writer=None):
    """Cleanup and close first; attempt JSON only after all process/global cleanup."""
    opener = artifact_opener or open_artifact
    writer = packet_writer or write_json
    target = checked_target(target)
    log = target.with_suffix(".log")
    if target.exists() or log.exists():
        raise ValueError("command artifacts already exist")
    started = time.perf_counter()
    process = drain = cleanup = pending = None
    interrupted = None
    stopping = False
    error = None
    io_errors = []
    managed = (signal.SIGINT, signal.SIGTERM)
    handlers = {s: signal.getsignal(s) for s in managed}

    def interrupt(signum, _frame):
        nonlocal interrupted
        interrupted = interrupted or signum
        # Flag-only until cleanup: no fork/assignment race or inherited blocked mask.
        if stopping and process is not None:
            try:
                os.killpg(process.pid, signum)
            except ProcessLookupError:
                pass

    with adopt_descendants():
        try:
            with opener(log) as output, selectors.DefaultSelector() as selector:
                for s in managed:
                    signal.signal(s, interrupt)
                try:
                    if not interrupted:
                        process = subprocess.Popen(command, cwd=root, env=env, start_new_session=True,
                                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        drain = Drain(process.stdout, output, selector)
                    while process is not None and process.poll() is None and not interrupted and not drain.disabled:
                        drain.pump(0.05)
                except KeyboardInterrupt:
                    interrupted = interrupted or signal.SIGINT
                except BaseException as failure:
                    error = str(failure)
                    if isinstance(failure, OSError):
                        io_errors.append(error_record("capture", failure))
                    else:
                        pending = failure
                finally:
                    stopping = True
                    if process is not None:
                        try:
                            pump = (lambda wait: drain.pump(wait, display=False)) if drain else (lambda wait: 0)
                            cleanup = teardown(process, pump, interrupted or signal.SIGTERM)
                        finally:
                            # Even failed draining/teardown or later JSON IO cannot skip pipe closure.
                            process.stdout.close()
                    if drain is not None:
                        drain.finish_display()
        except OSError as failure:
            # Includes log flush/close failure, after the process cleanup finally.
            io_errors.append(error_record("artifact/selector context", failure))
            error = error or str(failure)
        finally:
            for s, handler in handlers.items():
                signal.signal(s, handler)
    if drain is not None:
        io_errors.extend(drain.errors)
    if cleanup is not None:
        io_errors.extend(cleanup["drain_errors"])
    raw = process.returncode if process is not None else None
    complete = bool(drain and drain.eof and not io_errors and cleanup and not cleanup["final_drain_limited"])
    code = 128 + interrupted if interrupted else shell_status(raw)
    if code is None or error or io_errors or not complete or (cleanup and not cleanup["process_group_gone"]):
        code = 128 + interrupted if interrupted else 1 if process is not None else 127
        error = error or (io_errors[0]["message"] if io_errors else "capture/managed cleanup incomplete")
    effective_env = os.environ if env is None else env
    packet = {
        "schema": "l0.profile-command/1", "command": command, "cwd": str(root),
        "raw_child_returncode": raw, "child_exit_code": shell_status(raw), "exit_code": code,
        "interrupted_signal": interrupted, "teardown": cleanup, "io_errors": io_errors,
        "output_complete": complete, "wall_seconds": time.perf_counter() - started,
        "log": log.name, "error": error, "condition": effective_env.get("L0_PROFILE_CONDITION"),
        "tmpdir": effective_env.get("TMPDIR"),
    }
    writer(target, packet)  # Cleanup, pipe closure, and global restoration precede JSON IO.
    if pending is not None:
        raise pending
    return packet
