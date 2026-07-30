# ScubaMob Claude Project Pack

This pack contains the files needed to give Claude.ai or Claude Code durable project context and safe development instructions.

## Included

- `CLAUDE.md`
- `.claude/settings.json`
- reusable Claude commands under `.claude/commands/`
- project, architecture, domain, security, testing, workflow, roadmap, and task-tracking documentation
- `.env.example`
- recommended `.gitignore` additions
- Claude.ai setup instructions

## Installation

Copy the contents of this pack into the root of the ScubaMob repository.

Do not replace an existing `.gitignore` blindly. Merge the entries from `.gitignore.claude-additions`.

Review `.claude/settings.json` before using it. Permission behavior may vary by Claude Code version and local environment.

## Important

This pack is based on the current ScubaMob product direction, modernization roadmap, and pinned Python dependencies. Claude must still inspect the actual source code and migrations before implementing changes.
