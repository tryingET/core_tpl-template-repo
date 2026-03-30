---
summary: "Cross-repo AK fanout for removing template-shipped/local rocs_cli GitLab baseline-resolution paths."
read_when:
  - "When executing or reviewing the GitLab baseline-resolution removal fanout"
---

# GitLab baseline-resolution removal fanout

Decision: `ak decision #5`

## Task fanout

| Task | Repo | Priority | Depends on | Title |
|------|------|----------|------------|-------|
| #279 | `core/ontology-kernel` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #280 | `core/prompt-vault` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #281 | `core/tpl-template-repo` | 1 | - | Remove template-shipped rocs_cli GitLab baseline-resolution from tpl-project-repo |
| #282 | `healthco` | 1 | 281 | Remove embedded tpl-project-repo rocs_cli GitLab baseline-resolution from L1 template repo |
| #283 | `healthco/agents` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #284 | `healthco/data` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #285 | `healthco/data/health-records` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #286 | `holdingco` | 1 | 281 | Remove embedded tpl-project-repo rocs_cli GitLab baseline-resolution from L1 template repo |
| #287 | `holdingco/agents` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #288 | `holdingco/contrib` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #289 | `holdingco/infra` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #290 | `holdingco/infra/template-propagator` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #291 | `holdingco/ontology` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #292 | `holdingco/owned` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #293 | `holdingco/projects/rocs-dogfood` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #294 | `softwareco` | 1 | 281 | Remove embedded tpl-project-repo rocs_cli GitLab baseline-resolution from L1 template repo |
| #295 | `softwareco/contrib` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #296 | `softwareco/contrib/codemapper` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #297 | `softwareco/contrib/local/pilot-contrib-strict-l2-20260212` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #298 | `softwareco/contrib/pi-mono` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #299 | `softwareco/fork` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #300 | `softwareco/fork/pi-mono` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #301 | `softwareco/infra` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #302 | `softwareco/infra/ds1621-admin` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #303 | `softwareco/infra/hooks-logging` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #304 | `softwareco/infra/issue-tracker` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #305 | `softwareco/infra/pilot-infra-strict-l2-20260212` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #306 | `softwareco/infra/provisioning` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #307 | `softwareco/infra/workstation` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #308 | `softwareco/ontology` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #309 | `softwareco/owned` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #310 | `softwareco/owned/agent-kernel` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #311 | `softwareco/owned/agent-kernel-review-state` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #312 | `softwareco/owned/apex-cathedral` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #313 | `softwareco/owned/crawlgithub` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #314 | `softwareco/owned/dep-diet` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #315 | `softwareco/owned/dep-viz` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #316 | `softwareco/owned/dotfiles-managed` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #317 | `softwareco/owned/dspx` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #318 | `softwareco/owned/fcos-proving-lane` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #319 | `softwareco/owned/glimpseui-linux` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #320 | `softwareco/owned/lehrplan-viz` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #321 | `softwareco/owned/nexus-workflow-platform` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #322 | `softwareco/owned/pi-extensions-template` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #323 | `softwareco/owned/runtime-trace-insights` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #324 | `softwareco/owned/semantic-flow-diff` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #325 | `softwareco/owned/test-capabilities` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #326 | `softwareco/owned/ts-quality` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #327 | `softwareco/owned/voice-dictation` | 2 | - | Remove repo-local rocs_cli GitLab baseline-resolution compatibility path |
| #328 | `teachingco` | 1 | 281 | Remove embedded tpl-project-repo rocs_cli GitLab baseline-resolution from L1 template repo |
