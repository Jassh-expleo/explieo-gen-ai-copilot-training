# Agent Workflow

This folder contains reusable templates and per-run review artifacts for staged agent execution.

## Recommended Structure

- `templates/`
  - `approval-board-template.md`
  - `architecture-review-template.md`
  - `planning-review-template.md`
  - `implementation-review-template.md`
- `runs/<run-name>/`
  - `approval-board.md`
  - `architecture-review.md`
  - `planning-review.md`
  - `implementation-review.md`

## Usage Pattern

1. Start a new run for each feature, TODO, bug fix, or refactor.
2. Keep the board short and readable.
3. Put detailed stage output in separate review files.
4. Approve each stage only after reviewing its dedicated file.
5. Resume an existing run by reopening the same run folder.

## Example Run Names

- `todo1-email-validation`
- `bugfix-auth-timeout`
- `refactor-csv-loader`
- `feature-user-export`