# Agent Workflow Approval Board

Use this file as the human-readable approval surface for any feature, TODO, bug fix, refactor, or design task.

## Workflow Metadata
- Run name: `todo1-email-validation`
- Request: `Implement validate_customer_email — TODO 1`
- Target files: `6AprilOnwardsTraining/lab_starter_Day1.py`
- Started by: `user`
- Last updated: `Stage A — Architecture (Pending Re-run after Rejection)`
- Status: `In Progress`

## Review Files

- Architecture review: `architecture-review.md`
- Planning review: `planning-review.md` ✅ Written
- Implementation review: `implementation-review.md`

## Stage Status

| Stage | Status | Owner | Summary | Decision |
| --- | --- | --- | --- | --- |
| Architecture | ✅ Approved | Architect Agent | Manual string parsing; 1 public fn + 1 private helper; stdlib only; 20 edge cases; 14+ tests | **Approved** |
| Planning | ✅ Approved | Planning Agent | 6 tasks (T1–T6); T1→T2→T3→T4→T5→T6 sequential; ≥20 tests; stdlib only; key risk R4 (empty allowlist) flagged | **Approved** |
| Implementation | 🟡 In Progress | Developer Agent | T1 ✅ T2 ✅ — normalization stage complete | **T2 Done** |

## Task Tracking

| Task ID | Title | Status | Validation | Notes |
| --- | --- | --- | --- | --- |
| T1 | Scaffold function stub | ✅ Done | `python -c "from lab_starter_Day1 import validate_customer_email; result = validate_customer_email('test@example.com'); print('OK:', result)"` → `OK: False` | `from __future__ import annotations` added for Python 3.8 compat |
| T2 | Normalization stage | ✅ Done | All 3 checks passed: whitespace/case, no mutation, clean import | `_normalize_email_inputs` added; no new imports |
| T3 | Structural validation | Not Started | - | - |
| T4 | Domain authorization | Not Started | - | - |
| T5 | Wire all stages | Not Started | - | - |
| T6 | Unit test suite | Not Started | - | - |

## Approval Log

- [ ] Architecture approved
- [ ] Planning approved
- [ ] Implementation approved

## Open Questions

- What specific changes are required to the architecture? (User rejected first design — awaiting feedback)

## How To Use

1. Start one run folder per feature or task.
2. Read the detailed review files before approving any stage.
3. Record your decision in this board.
4. Reply in chat with `Approve`, `Request Changes`, or `Hold`.
5. Continue stage by stage.
