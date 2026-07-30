# Using This Repository in Claude.ai

## Create the Project

1. Create a new Claude.ai Project named `ScubaMob`.
2. Upload the repository source archive or connect the repository using an available integration.
3. Add the files from this pack to the repository, preserving their paths.
4. Upload the roadmap and important design documents to the Claude.ai Project knowledge area if the repository is not connected.
5. Use `CLAUDE.md` as the primary project instruction file.

## Recommended Project Knowledge

At minimum, Claude.ai should have access to:

- `CLAUDE.md`
- `requirements.txt`
- `docs/claude/PROJECT_CONTEXT.md`
- `docs/claude/ARCHITECTURE.md`
- `docs/claude/DOMAIN_MODEL.md`
- `docs/claude/MODERNIZATION_ROADMAP.md`
- `docs/claude/SECURITY.md`
- `docs/claude/TESTING.md`
- `docs/claude/DEVELOPMENT_WORKFLOW.md`
- the actual source tree;
- current migrations;
- current tests.

## Suggested First Prompt

```text
Read CLAUDE.md and every file under docs/claude. Then inspect the repository without changing anything. Produce a current-state audit that identifies:

1. Django apps and their responsibilities.
2. Current models and migration status.
3. External API call locations.
4. Test structure and any live-network dependencies.
5. Configuration and secret-handling issues.
6. Which modernization-roadmap items are already complete.
7. The smallest recommended next implementation task.

Do not claim commands were run unless you actually ran them. List exact files examined.
```

## Suggested Implementation Prompt

```text
Implement the next unchecked task from Phase 0 or Phase 1 of docs/claude/MODERNIZATION_ROADMAP.md.

Before editing, inspect all relevant source, tests, settings, and migrations. Make the smallest coherent change. Add or update tests. Run the relevant validation commands. Update TASK_TRACKER.md only after verified completion.

Return the required task report from CLAUDE.md and list only files actually changed.
```

## Repository Upload Notes

Claude.ai Project knowledge can provide context, but it does not automatically synchronize local code changes. For implementation work, use a repository integration or Claude Code in a checked-out repository. Commit and push completed changes so the Claude.ai Project and other devices can reference the same state.
