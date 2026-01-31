---
name: openspec-onboard
description: Guided onboarding for OpenSpec - walk through a complete workflow cycle with narration and real codebase work.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.1.0"
---

Guide the user through their first complete OpenSpec workflow cycle. This is a teaching experience—you'll do real work in their codebase while explaining each step.

---

## Preflight

Before starting, check if OpenSpec is initialized:

```bash
openspec status --json 2>&1 || echo "NOT_INITIALIZED"
```

**If not initialized:**
> OpenSpec isn't set up in this project yet. Run `openspec init` first, then come back to `/opsx:onboard`.

Stop here if not initialized.

---

## Phase 1: Welcome

Display:

```
## Welcome to OpenSpec!

I'll walk you through a complete change cycle—from idea to implementation—using a real task in your codebase. Along the way, you'll learn the workflow by doing it.

**What we'll do:**
1. Pick a small, real task in your codebase
2. Explore the problem briefly
3. Create a change (the container for our work)
4. Build the artifacts: proposal → specs → design → tasks
5. Set up proper Git workflow (feature branch)
6. Implement the tasks
7. Archive the completed change

**Time:** ~15-20 minutes

Let's start by finding something to work on.
```

---

## Phase 2: Task Selection

### Codebase Analysis

Scan the codebase for small improvement opportunities. Look for:

1. **TODO/FIXME comments** - Search for `TODO`, `FIXME`, `HACK`, `XXX` in code files
2. **Missing error handling** - `catch` blocks that swallow errors, risky operations without try-catch
3. **Functions without tests** - Cross-reference `src/` with test directories
4. **Type issues** - `any` types in TypeScript files (`: any`, `as any`)
5. **Debug artifacts** - `console.log`, `console.debug`, `debugger` statements in non-debug code
6. **Missing validation** - User input handlers without validation

Also check recent git activity:
```bash
git log --oneline -10 2>/dev/null || echo "No git history"
```

### Present Suggestions

From your analysis, present 3-4 specific suggestions:

```
## Task Suggestions

Based on scanning your codebase, here are some good starter tasks:

**1. [Most promising task]**
   Location: `src/path/to/file.ts:42`
   Scope: ~1-2 files, ~20-30 lines
   Why it's good: [brief reason]

**2. [Second task]**
   Location: `src/another/file.ts`
   Scope: ~1 file, ~15 lines
   Why it's good: [brief reason]

**3. [Third task]**
   Location: [location]
   Scope: [estimate]
   Why it's good: [brief reason]

**4. Something else?**
   Tell me what you'd like to work on.

Which task interests you? (Pick a number or describe your own)
```

**If nothing found:** Fall back to asking what the user wants to build:
> I didn't find obvious quick wins in your codebase. What's something small you've been meaning to add or fix?

### Scope Guardrail

If the user picks or describes something too large (major feature, multi-day work):

```
That's a valuable task, but it's probably larger than ideal for your first OpenSpec run-through.

For learning the workflow, smaller is better—it lets you see the full cycle without getting stuck in implementation details.

**Options:**
1. **Slice it smaller** - What's the smallest useful piece of [their task]? Maybe just [specific slice]?
2. **Pick something else** - One of the other suggestions, or a different small task?
3. **Do it anyway** - If you really want to tackle this, we can. Just know it'll take longer.

What would you prefer?
```

Let the user override if they insist—this is a soft guardrail.

---

## Phase 3: Explore Demo

Once a task is selected, briefly demonstrate explore mode:

```
Before we create a change, let me quickly show you **explore mode**—it's how you think through problems before committing to a direction.
```

Spend 1-2 minutes investigating the relevant code:
- Read the file(s) involved
- Draw a quick ASCII diagram if it helps
- Note any considerations

```
## Quick Exploration

[Your brief analysis—what you found, any considerations]

┌─────────────────────────────────────────┐
│   [Optional: ASCII diagram if helpful]  │
└─────────────────────────────────────────┘

Explore mode (`/opsx:explore`) is for this kind of thinking—investigating before implementing. You can use it anytime you need to think through a problem.

Now let's create a change to hold our work.
```

**PAUSE** - Wait for user acknowledgment before proceeding.

---

## Phase 4: Create the Change

**EXPLAIN:**
```
## Creating a Change

A "change" in OpenSpec is a container for all the thinking and planning around a piece of work. It lives in `openspec/changes/<name>/` and holds your artifacts—proposal, specs, design, tasks.

Let me create one for our task.
```

**DO:** Create the change with a derived kebab-case name:
```bash
openspec new change "<derived-name>"
```

**SHOW:**
```
Created: `openspec/changes/<name>/`

The folder structure:
```
openspec/changes/<name>/
├── proposal.md    ← Why we're doing this (empty, we'll fill it)
├── design.md      ← How we'll build it (empty)
├── specs/         ← Detailed requirements (empty)
└── tasks.md       ← Implementation checklist (empty)
```

Now let's fill in the first artifact—the proposal.
```

---

## Phase 5: Proposal

**EXPLAIN:**
```
## The Proposal

The proposal captures **why** we're making this change and **what** it involves at a high level. It's the "elevator pitch" for the work.

I'll draft one based on our task.
```

**DO:** Draft the proposal content (don't save yet):

```
Here's a draft proposal:

---

## Why

[1-2 sentences explaining the problem/opportunity]

## What Changes

[Bullet points of what will be different]

## Capabilities

### New Capabilities
- `<capability-name>`: [brief description]

### Modified Capabilities
<!-- If modifying existing behavior -->

## Impact

- `src/path/to/file.ts`: [what changes]
- [other files if applicable]

---

Does this capture the intent? I can adjust before we save it.
```

**PAUSE** - Wait for user approval/feedback.

After approval, save the proposal:
```bash
openspec instructions proposal --change "<name>" --json
```
Then write the content to `openspec/changes/<name>/proposal.md`.

```
Proposal saved. This is your "why" document—you can always come back and refine it as understanding evolves.

Next up: specs.
```

---

## Phase 6: Specs

**EXPLAIN:**
```
## Specs

Specs define **what** we're building in precise, testable terms. They use a requirement/scenario format that makes expected behavior crystal clear.

For a small task like this, we might only need one spec file.
```

**DO:** Create the spec file:
```bash
mkdir -p openspec/changes/<name>/specs/<capability-name>
```

Draft the spec content:

```
Here's the spec:

---

## ADDED Requirements

### Requirement: <Name>

<Description of what the system should do>

#### Scenario: <Scenario name>

- **WHEN** <trigger condition>
- **THEN** <expected outcome>
- **AND** <additional outcome if needed>

---

This format—WHEN/THEN/AND—makes requirements testable. You can literally read them as test cases.
```

Save to `openspec/changes/<name>/specs/<capability>/spec.md`.

---

## Phase 7: Design

**EXPLAIN:**
```
## Design

The design captures **how** we'll build it—technical decisions, tradeoffs, approach.

For small changes, this might be brief. That's fine—not every change needs deep design discussion.
```

**DO:** Draft design.md:

```
Here's the design:

---

## Context

[Brief context about the current state]

## Goals / Non-Goals

**Goals:**
- [What we're trying to achieve]

**Non-Goals:**
- [What's explicitly out of scope]

## Decisions

### Decision 1: [Key decision]

[Explanation of approach and rationale]

---

For a small task, this captures the key decisions without over-engineering.
```

Save to `openspec/changes/<name>/design.md`.

---

## Phase 8: Tasks

**EXPLAIN:**
```
## Tasks

Finally, we break the work into implementation tasks—checkboxes that drive the apply phase.

These should be small, clear, and in logical order.
```

**DO:** Generate tasks based on specs and design:

```
Here are the implementation tasks:

---

## 1. [Category or file]

- [ ] 1.1 [Specific task]
- [ ] 1.2 [Specific task]

## 2. Verify

- [ ] 2.1 [Verification step]

---

Each checkbox becomes a unit of work in the apply phase. Ready to implement?
```

**PAUSE** - Wait for user to confirm they're ready to implement.

Save to `openspec/changes/<name>/tasks.md`.

---

## Phase 9: Git Branch Setup

**EXPLAIN:**
```
## Git Best Practice: Feature Branches

Before we implement, let's follow a key Git best practice: **never commit directly to main or dev**.

We'll create a feature branch for this change. This:
- Keeps main/dev stable and deployable
- Makes code review easier
- Allows parallel work on multiple changes
- Prevents accidental breaking changes in production branches

This is industry-standard Git workflow.
```

**DO:** Check if Git repository exists and current branch:

```bash
# Check if Git repo exists
if git rev-parse --git-dir >/dev/null 2>&1; then
  echo "GIT_DETECTED"
  CURRENT_BRANCH=$(git branch --show-current)
  echo "Current branch: $CURRENT_BRANCH"
else
  echo "NO_GIT"
fi
```

**If Git repository detected:**

**SHOW:**
```
## Git Workflow

**Current status:** You're on branch `<current-branch>`

```
main/dev ────────────────────────────► (protected - never commit here)
           ╲
            ╲
             <change-name> ──► (our feature branch - safe to commit)
```

**Protected Branch Strategy:**

| Branch Type | Examples | Purpose | Can commit? |
|------------|----------|---------|-------------|
| Protected | `main`, `master`, `dev` | Integration, production code | ❌ Never |
| Feature | `add-user-auth`, `fix-login-bug` | Development work | ✅ Yes |

```

**If on protected branch (main/master/dev):**

```
⚠️  You're currently on `<current-branch>` - this is a protected branch.

Let me create a feature branch for you:
```

**DO:**
```bash
git checkout -b <change-name>
```

**SHOW:**
```
✓ Created and switched to feature branch: `<change-name>`

Now we can safely implement without touching <original-branch>.
```

**If already on a non-protected branch:**

```
✓ Git branch check passed: `<current-branch>`

You're already on a feature branch. Good practice!
```

**If branch name doesn't match change name:**
```
ℹ️  Note: Your branch name '<current-branch>' differs from the change name '<change-name>'.

This is okay, but matching names makes it easier to track which branch goes with which change.
```

**If no Git repository:**

```
ℹ️  No Git repository detected - skipping branch setup.

If you're using Git, these are the commands you'd run:
```bash
git checkout -b <change-name>  # Create feature branch
git add .                       # Stage changes
git commit -m "..."            # Commit work
```
```

**PAUSE** - Wait for user acknowledgment before proceeding.

---

## Phase 10: Apply (Implementation)

**EXPLAIN:**
```
## Implementation

Now we implement each task, checking them off as we go. I'll announce each one and occasionally note how the specs/design informed the approach.

After each significant change, you'll want to commit. I'll remind you when it makes sense.
```

**DO:** For each task:

1. Announce: "Working on task N: [description]"
2. Implement the change in the codebase
3. Reference specs/design naturally: "The spec says X, so I'm doing Y"
4. Mark complete in tasks.md: `- [ ]` → `- [x]`
5. Brief status: "✓ Task N complete"

**After 2-3 tasks (or logical checkpoint), suggest a commit:**

```
💡 **Good checkpoint for a commit**

You've completed [tasks completed]. Let's save this progress:

```bash
git add <files-changed>
git commit -m "feat(<capability>): <brief-description>

- Completed tasks <N>-<M>
- Implements requirement: <req-name>"
```

This keeps your history clean and makes it easy to revert if needed.
```

Keep narration light—don't over-explain every line of code.

After all tasks:

```
## Implementation Complete

All tasks done:
- [x] Task 1
- [x] Task 2
- [x] ...

The change is implemented! Let's commit the final changes.
```

**DO:** Guide final commit:
```bash
git add .
git commit -m "feat(<capability>): complete <change-name>

Implements all tasks from openspec/changes/<name>/tasks.md

- [Summary of what was done]
- All requirements from specs satisfied
- Ready for review"
```

```
✓ Changes committed to branch `<branch-name>`

Next step: archive the change and optionally create a Pull Request.
```

---

## Phase 11: Archive & PR Workflow

**EXPLAIN:**
```
## Archiving & Pull Request Workflow

When a change is complete, we archive it. This moves it from `openspec/changes/` to `openspec/changes/archive/YYYY-MM-DD-<name>/`.

Archived changes become your project's decision history—you can always find them later to understand why something was built a certain way.

**If using Git:** You'll typically want to:
1. Push your branch to remote
2. Create a Pull Request for code review
3. After PR is merged, archive the change
```

**If Git repository detected:**

**SHOW:**
```
## Recommended Git Workflow

**1. Push your feature branch:**
```bash
git push -u origin <branch-name>
```

**2. Create Pull Request:**
- Go to your Git hosting platform (GitHub/GitLab/Bitbucket)
- **IMPORTANT:** Create PR from `<branch-name>` → `dev` (never to `main`)
- Link to the change: `openspec/changes/<name>/`
- Request review from teammates

**3. After PR is merged:**
```bash
# Switch back to dev branch
git checkout dev
git pull

# Delete local feature branch
git branch -d <branch-name>

# Archive the OpenSpec change
```

**Options:**
1. **Archive now** (if you'll merge without review, or archive before PR)
2. **Wait for PR merge** (archive after merge - recommended for team workflows)
3. **Just show me the archive command** (I'll do it manually later)

What would you like to do?
```

Use **AskUserQuestion tool** to get user choice.

**Based on choice:**

**Option 1 or 2:** Proceed with archive
**Option 3:** Show command and stop

**If no Git:**

Proceed directly to archive.

**DO:**
```bash
mkdir -p openspec/changes/archive
mv openspec/changes/<name> openspec/changes/archive/$(date +%Y-%m-%d)-<name>
```

**SHOW:**
```
Archived to: `openspec/changes/archive/YYYY-MM-DD-<name>/`

The change is now part of your project's history. The code is in your codebase, the decision record is preserved.
```

---

## Phase 12: Recap & Next Steps

```
## Congratulations!

You just completed a full OpenSpec cycle with Git best practices:

1. **Explore** - Thought through the problem
2. **New** - Created a change container
3. **Proposal** - Captured WHY
4. **Specs** - Defined WHAT in detail
5. **Design** - Decided HOW
6. **Tasks** - Broke it into steps
7. **Git Branch** - Set up safe feature branch ✨ NEW
8. **Apply** - Implemented the work with commits ✨ NEW
9. **Archive** - Preserved the record
10. **PR Workflow** - Ready for team review ✨ NEW

This same rhythm works for any size change—a small fix or a major feature.

---

## Command Reference

| Command | What it does |
|---------|--------------|
| `/opsx:explore` | Think through problems before/during work |
| `/opsx:new` | Start a new change, step through artifacts |
| `/opsx:ff` | Fast-forward: create all artifacts at once |
| `/opsx:continue` | Continue working on an existing change |
| `/opsx:apply` | Implement tasks from a change |
| `/opsx:verify` | Verify implementation matches artifacts |
| `/opsx:archive` | Archive a completed change |

---

## Git Workflow Recap

**Golden Rules:**
- ❌ Never commit to `main`, `master`, or `dev` directly
- ✅ Always create feature branches: `git checkout -b <change-name>`
- ✅ Commit often with clear messages
- ✅ Push and create PR for review: `git push -u origin <branch-name>`
- ✅ Delete branch after merge: `git branch -d <branch-name>`

**Commit Message Format:**
```
feat(<scope>): <brief-description>

- Detailed point 1
- Detailed point 2

Implements: openspec/changes/<name>/
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## What's Next?

Try `/opsx:new` or `/opsx:ff` on something you actually want to build. You've got the rhythm now—including the Git workflow!

**Pro tip:** Run `/opsx:git-help` anytime you need a Git workflow reminder.
```

---

## Graceful Exit Handling

### User wants to stop mid-way

If the user says they need to stop, want to pause, or seem disengaged:

```
No problem! Your change is saved at `openspec/changes/<name>/`.

To pick up where we left off later:
- `/opsx:continue <name>` - Resume artifact creation
- `/opsx:apply <name>` - Jump to implementation (if tasks exist)

**Git status:** You're on branch `<branch-name>`
- Your work is saved in Git (if you committed)
- To resume: `git checkout <branch-name>`

The work won't be lost. Come back whenever you're ready.
```

Exit gracefully without pressure.

### User just wants command reference

If the user says they just want to see the commands or skip the tutorial:

```
## OpenSpec Quick Reference

| Command | What it does |
|---------|--------------|
| `/opsx:explore` | Think through problems (no code changes) |
| `/opsx:new <name>` | Start a new change, step by step |
| `/opsx:ff <name>` | Fast-forward: all artifacts at once |
| `/opsx:continue <name>` | Continue an existing change |
| `/opsx:apply <name>` | Implement tasks |
| `/opsx:verify <name>` | Verify implementation |
| `/opsx:archive <name>` | Archive when done |
| `/opsx:git-help` | Git workflow best practices |

## Git Workflow

```bash
# Start new work
git checkout -b <change-name>

# Commit frequently
git add .
git commit -m "feat: description"

# Push and create PR
git push -u origin <change-name>

# After merge, cleanup
git checkout main
git pull
git branch -d <change-name>
```

Try `/opsx:new` to start your first change, or `/opsx:ff` if you want to move fast.
```

Exit gracefully.

---

## Guardrails

- **Follow the EXPLAIN → DO → SHOW → PAUSE pattern** at key transitions (after explore, after proposal draft, after tasks, after Git setup, after archive)
- **Teach Git workflow explicitly** - this is a core software development skill
- **Verify Git branch safety** before any implementation
- **Suggest commits at logical checkpoints** during implementation
- **Provide full PR workflow guidance** for team environments
- **Keep narration light** during implementation—teach without lecturing
- **Don't skip phases** even if the change is small—the goal is teaching the workflow
- **Pause for acknowledgment** at marked points, but don't over-pause
- **Handle exits gracefully**—never pressure the user to continue
- **Use real codebase tasks**—don't simulate or use fake examples
- **Adjust scope gently**—guide toward smaller tasks but respect user choice
- **Gracefully handle non-Git projects** - show what would be done without blocking workflow
