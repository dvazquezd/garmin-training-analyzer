---
name: openspec-apply-change
description: Implement tasks from an OpenSpec change. Use when the user wants to start implementing, continue implementation, or work through tasks.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.1.0"
---

Implement tasks from an OpenSpec change.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx:apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for others)

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - Context file paths (varies by schema - could be proposal/specs/design/tasks or spec/tests/implementation/docs)
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message, suggest using openspec-continue-change
   - If `state: "all_done"`: congratulate, suggest archive
   - Otherwise: proceed to implementation

4. **Read context files**

   Read the files listed in `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output

5. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Dynamic instruction from CLI

6. **Git branch safety check (if using Git)**

   Before implementing any tasks, verify the Git branch is safe:

   ```bash
   git rev-parse --git-dir >/dev/null 2>&1 && echo "GIT_REPO" || echo "NO_GIT"
   ```

   **If Git repository detected:**

   Check current branch:
   ```bash
   git branch --show-current
   ```

   **If on protected branch (`main`, `master`, or `dev`):**
   
   Display warning:
   ```
   ⚠️  Git Branch Safety Check

   You're currently on branch: <current-branch>

   **Best Practice:** Never implement changes directly on protected branches (main/master/dev).
   
   **Recommended action:**
   Create a feature branch for this change:
   ```bash
   git checkout -b <change-name>
   ```

   **Options:**
   1. Create feature branch now (recommended)
   2. Continue anyway (not recommended - violates Git workflow best practices)
   3. Cancel and let me create the branch manually

   What would you like to do?
   ```

   Use **AskUserQuestion tool** to get user choice.

   - **If option 1 (create branch):**
     ```bash
     git checkout -b <change-name>
     ```
     Display: "✓ Created and switched to feature branch: <change-name>"
     Proceed to implementation.

   - **If option 2 (continue anyway):**
     Display: "⚠️  Proceeding on <current-branch> (not recommended)"
     Proceed to implementation.

   - **If option 3 (cancel):**
     Display: "Stopped. Create your feature branch and run `/opsx:apply <name>` again when ready."
     STOP here.

   **If already on a feature branch (not main/master/dev):**
   
   Display: "✓ Git branch check passed: <current-branch>"
   
   **If branch name doesn't match change name:**
   Display note: "ℹ️  Note: Branch name '<current-branch>' differs from change name '<change-name>'. This is okay, but matching names helps track work."

   **If no Git repository:**
   
   Skip Git checks silently, proceed to implementation.

7. **Implement tasks (loop until done or blocked)**

   For each pending task:
   - Show which task is being worked on
   - Make the code changes required
   - Keep changes minimal and focused
   - Mark task complete in the tasks file: `- [ ]` → `- [x]`
   - Continue to next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

8. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: suggest next steps (commit changes, verify, archive)
   - If paused: explain why and wait for guidance

   **If all tasks complete and Git repository detected:**
   ```
   ## Next Steps

   All tasks complete! ✓

   **Recommended workflow:**
   1. Commit your changes:
      ```bash
      git add .
      git commit -m "feat(<capability>): <brief-description>
      
      Implements change: <change-name>
      Completes all tasks from openspec/changes/<name>/tasks.md"
      ```

   2. Verify implementation (optional):
      `/opsx:verify <name>`

   3. Push and create Pull Request to dev:
      ```bash
      git push -u origin <branch-name>
      ```
      **IMPORTANT:** When creating the PR, set base branch to `dev` (not `main`)

   4. After PR is merged to dev, archive the change:
      `/opsx:archive <name>`
   ```

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

✓ Git branch check passed: <branch-name>

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete

Working on task 4/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete! 

**Next Steps:**
1. Commit changes: `git add . && git commit -m "..."`
2. Verify: `/opsx:verify <name>`
3. Create PR to dev: `git push -u origin <branch>` (then PR to `dev`)
4. Archive after merge: `/opsx:archive <name>`
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Verify Git branch safety before any implementation
- Block or warn strongly when on protected branches (main/master/dev)
- Suggest creating feature branch named after the change
- **Always guide users to create PRs to `dev` branch, never to `main`**
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- Use contextFiles from CLI output, don't assume specific file names
- Provide clear next steps including Git workflow after completion

**Fluid Workflow Integration**

This skill supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly
- **Git-aware**: Integrates with Git workflow when repository is detected, gracefully handles non-Git projects
- **Dev-first**: Always promotes PR to `dev` branch to maintain main branch stability
