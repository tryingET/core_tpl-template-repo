---
summary: "Company-level programs: notes and dated records for work that spans several of this company's repos. Open work lives in Agent Kernel, not here."
read_when:
  - "Read when changing L1 template output related to company-level programs."
  - "You are recording a program that spans several of this company's repos."
type: "reference"
---

# Company-Level Programs

Notes for programs that span several of this company's repos: their scope, the AK task and decision ids,
dated results and the closeout.

## What this folder is not

- **Not a queue.** Every piece of a program's work is an AK task (`ak task create -r <repo> ...`); its
  state lives in AK.
- **Not a work-items store.** No `work-items.json` here or anywhere else (Decision 127).
- **Not a decision record.** Decisions are AK decisions (`ak decision ...`); a note cites their ids.

## Layout

One folder or one dated Markdown file per program:

```
programs/
├── <program-id>/
│   └── README.md           # scope, AK task and decision ids, status
└── YYYY-MM-DD-<slug>.md    # a dated record, e.g. a rollout's results
```

A program may keep machine-readable results (JSON next to its Markdown). They record outcomes, not
open work.

## Adding a program

1. Create its AK tasks, and an AK decision if the program needs one.
2. Add `programs/<program-id>/README.md` or `programs/YYYY-MM-DD-<slug>.md` citing their ids.
3. Record results and the closeout there as the program runs.

## Related

- Governance overview: `../README.md`
- Society-level coordination items: FCOS, the coordination board (Leitstand), in
  `holdingco/fcos-control-board/`; it never decides
