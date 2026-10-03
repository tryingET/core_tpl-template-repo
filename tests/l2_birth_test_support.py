"""Controlled pinned L0 renderer for wrapper argv tests (no Copier/network)."""
import os
import shutil
import subprocess
from pathlib import Path

import yaml


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value))


def stub_l0(root: Path, source: Path) -> tuple[Path, str]:
    l0 = root / "stub-l0"
    l0.mkdir()
    for template in source.joinpath("copier").iterdir():
        if not template.is_dir():
            continue
        target = l0 / "copier-template/copier" / template.name
        target.mkdir(parents=True)
        shutil.copy2(template / "copier.yml", target / "copier.yml")
    script = l0 / "scripts/render-l1.sh"
    script.parent.mkdir()
    script.write_text('''#!/bin/sh
set -eu
mkdir -p "$2/contracts"
cp -R "$(dirname "$0")/../copier-template/copier" "$2/copier"
printf 'template:\\n  source_sha: %s\\nrender:\\n  repo_slug: %s\\n' "$(git rev-parse HEAD)" "$3" > "$2/contracts/provenance-seal.yml"
''')
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for args in [("init", "-q"), ("add", "."), ("-c", "user.name=test", "-c", "user.email=test@example.org", "commit", "-qm", "stub owner renderer")]:
        subprocess.run(["git", "-C", str(l0), *args], env=env, check=True, capture_output=True)
    pin = subprocess.check_output(["git", "-C", str(l0), "rev-parse", "HEAD"], env=env, text=True).strip()
    return l0, pin


def company_seal(l1: Path, pin: str, repo_slug: str) -> None:
    dump(l1 / "contracts/provenance-seal.yml", {
        "schema": "ai-society.template-provenance.v1",
        "template": {"source_repository": "core/tpl-template-repo", "source_sha": pin},
        "render": {"repo_slug": repo_slug, "layer": "L1"},
    })


def native_uv_pair(root: Path) -> Path:
    """Actual executables relocated like setup-uv; not a Copier transport double."""
    directory = root / "external-native-bin"
    directory.mkdir()
    uvx = Path(shutil.which("uvx")).resolve(strict=True)
    for name, path in (("uvx", uvx), ("uv", uvx.with_name("uv"))):
        with path.open("rb") as file:
            if file.read(4) != b"\x7fELF":
                raise AssertionError("native uv/uvx executables required for relocation proof")
        shutil.copy2(path, directory / name)
    return directory
