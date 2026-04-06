# Agent Workflow Approval Board

Use this file as the human-readable approval surface for any feature, TODO, bug fix, refactor, or design task.

## Workflow Metadata
- Run name: `<run-name>`
- Request: `<feature or task summary>`
- Target files: `<one or more files>`
- Started by: `<user>`
- Last updated: `<timestamp or stage>`
- Status: `In Progress`

## Review Files

- Architecture review: `architecture-review.md`
- Planning review: `planning-review.md`
- Implementation review: `implementation-review.md`

## Stage Status

| Stage | Status | Owner | Summary | Decision |
| --- | --- | --- | --- | --- |
| Architecture | Not Started | Architect Agent | - | Approve / Request Changes / Hold |
| Planning | Not Started | Planning Agent | - | Approve / Request Changes / Hold |
| Implementation | Not Started | Developer Agent | - | Approve / Request Changes / Hold |

## Task Tracking

| Task ID | Title | Status | Validation | Notes |
| --- | --- | --- | --- | --- |
| T1 | - | Not Started | - | - |

## Approval Log

- [ ] Architecture approved
- [ ] Planning approved
- [ ] Implementation approved

## Open Questions

- None yet.

## How To Use

1. Start one run folder per feature or task.
2. Read the detailed review files before approving any stage.
3. Record your decision in this board.
4. Reply in chat with `Approve`, `Request Changes`, or `Hold`.
5. Continue stage by stage.