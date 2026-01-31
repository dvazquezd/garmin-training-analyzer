---
name: openspec-git-workflow
description: Git workflow best practices and guidance for OpenSpec changes. Ensures safe branching strategy, proper commit practices, and integration flow.
license: MIT
compatibility: Requires Git.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.1.0"
---

Git workflow integration and best practices for OpenSpec changes.

This skill provides Git workflow guidance, safety checks, and integration patterns. It can be invoked standalone with `/opsx:git-help` or is automatically integrated into other OpenSpec skills.

---

## Core Principles

### 1. Protected Branches
- **Protected**: `main`, `master`, `dev` - these are integration/production branches
- **Rule**: NEVER commit directly to protected branches
- **Why**: Keeps production code stable, enables code review, allows safe experimentation

### 2. Feature Branches
- **Pattern**: One branch per change, named after the OpenSpec change (kebab-case)
- **Naming**: Match your branch name to your change name for easy tracking
- **Examples**: `add-user-auth`, `fix-login-bug`, `refactor-payment-logic`

### 3. Atomic Commits
- **Commit often**: After completing each task or logical unit of work
- **Clear messages**: Follow conventional commit format
- **Revertible**: Each commit should be a working state

### 4. Code Review
- **Pull Requests**: Always merge via PR, never direct push to protected branches
- **Review**: Have at least one teammate review your code
- **Link**: Include OpenSpec change reference in PR description

---

## Quick Reference

### Starting a New Change

```bash
# Ensure you're on latest integration branch
git checkout dev
git pull

# Create feature branch (use same name as OpenSpec change)
git checkout -b <change-name>
```

### During Implementation

```bash
# After completing a task or logical checkpoint
git add <modified-files>
git commit -m "feat(<capability>): <task-description>

- Implements requirement: <req-name>
- Closes task <N> from openspec/changes/<n>/tasks.md"
```

### Before Archiving

```bash
# Push feature branch to remote
git push -u origin <change-name>

# Create Pull Request on your Git platform (GitHub/GitLab/Bitbucket)
# IMPORTANT: Set base branch to dev (never main)
# Include link to openspec/changes/<n>/ in PR description
```

### After PR Merge

```bash
# Switch back to dev branch
git checkout dev
git pull

# Delete local feature branch (optional but clean)
git branch -d <change-name>

# Now archive the OpenSpec change
# /opsx:archive <n>
```

---

## Detailed Workflow

### Phase 1: Setup

**Before creating any OpenSpec change:**

1. **Ensure clean working state:**
   ```bash
   git status
   ```
   
   If you have uncommitted changes, either commit or stash them:
   ```bash
   git stash  # Save for later
   # or
   git add .
   git commit -m "wip: save current work"
   ```

2. **Update your integration branch:**
   ```bash
   git checkout dev
   git pull
   ```

3. **Create your feature branch:**
   ```bash
   git checkout -b <change-name>
   ```

**Verification:**
```bash
git branch --show-current
# Should show: <change-name>
```

### Phase 2: Implementation

**Commit strategy during `/opsx:apply`:**

Commit after completing:
- Each significant task (or every 2-3 small tasks)
- Each logical unit of work (e.g., one requirement implementation)
- Before switching context or taking a break

**Commit message format:**

```
<type>(<scope>): <short-description>

<body: detailed explanation>

<footer: references>
```

**Types:**
- `feat`: New feature or capability
- `fix`: Bug fix
- `refactor`: Code restructure without behavior change
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Build, config, or tooling changes
- `style`: Formatting, whitespace (no logic change)

**Examples:**

```bash
# Simple feature
git commit -m "feat(auth): add OAuth provider integration

Implements Google OAuth flow for user authentication.

Closes task 2.1 from openspec/changes/add-oauth/tasks.md"

# Bug fix
git commit -m "fix(payment): handle zero-amount edge case

Previously threw exception on $0 transactions.
Now returns early with success status.

Fixes requirement: Payment Processing Error Handling"

# Refactor
git commit -m "refactor(api): extract validation to middleware

No behavior change - moves validation logic to reusable middleware.

Part of: openspec/changes/api-refactor/"
```

**What to commit:**

✅ **DO commit:**
- Source code changes
- Test files
- Updated documentation
- Configuration changes
- OpenSpec artifact updates (proposal/specs/design/tasks)

❌ **DON'T commit:**
- Build artifacts (`dist/`, `build/`)
- Dependencies (`node_modules/`, `venv/`)
- IDE files (`.vscode/`, `.idea/`)
- Environment files (`.env`, `.env.local`)
- Temporary files (`.DS_Store`, `*.log`)

Use `.gitignore` to prevent accidental commits of these files.

### Phase 3: Push & Pull Request

**When implementation is complete:**

1. **Final verification:**
   ```bash
   git status  # Check all changes are committed
   git log --oneline -5  # Review your commits
   ```

2. **Push to remote:**
   ```bash
   git push -u origin <change-name>
   ```
   
   The `-u` flag sets up tracking so future pushes just need `git push`.

3. **Create Pull Request:**

   **On GitHub:**
   - Go to your repository
   - Click "Pull requests" → "New pull request"
   - Base: `dev` (NEVER `main`) ← Compare: `<change-name>`
   - Click "Create pull request"

   **PR Template:**
   ```markdown
   ## Description
   [Brief description of what this change does]

   ## OpenSpec Change
   Reference: `openspec/changes/<n>/`
   
   ## Changes
   - [List key changes]
   - [One per line]

   ## Testing
   - [ ] All tasks from tasks.md completed
   - [ ] Requirements from specs satisfied
   - [ ] Manual testing performed
   - [ ] Automated tests passing (if applicable)

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Documentation updated (if needed)
   - [ ] No console.log or debug code left
   - [ ] Commits are clean and well-described
   ```

4. **Request review:**
   - Assign reviewers
   - Add relevant labels (feature, bug, refactor, etc.)
   - Link any related issues

5. **Address feedback:**
   ```bash
   # Make changes based on review
   git add <files>
   git commit -m "review: address feedback on error handling"
   git push
   ```
   
   Commits automatically appear in the PR.

### Phase 4: After Merge

**Once PR is approved and merged:**

1. **Switch to integration branch:**
   ```bash
   git checkout dev
   ```

2. **Pull latest (includes your merged changes):**
   ```bash
   git pull
   ```

3. **Delete feature branch:**
   ```bash
   # Delete local branch
   git branch -d <change-name>
   
   # Delete remote branch (optional - often auto-deleted by PR merge)
   git push origin --delete <change-name>
   ```

4. **Archive OpenSpec change:**
   ```bash
   # /opsx:archive <n>
   ```

**Verification:**
```bash
git branch -a  # Should not show <change-name> locally
git log --oneline -3  # Should show your merged commits
```

---

## Safety Checks & Guardrails

### Pre-Implementation Safety Check

**Before running `/opsx:apply`, verify branch safety:**

```bash
CURRENT=$(git branch --show-current 2>/dev/null || echo "NO_GIT")

case "$CURRENT" in
  main|master|dev)
    echo "❌ ERROR: Cannot implement on protected branch '$CURRENT'"
    echo "âž¡ï¸  Run: git checkout -b <change-name>"
    exit 1
    ;;
  NO_GIT)
    echo "ℹ️  No Git repository - proceeding without Git checks"
    ;;
  *)
    echo "✓ Safe to implement on branch: $CURRENT"
    ;;
esac
```

**This check prevents:**
- Accidentally committing to `main`
- Breaking production code
- Bypassing code review process
- Causing team conflicts

### Pre-Commit Hook (Optional but Recommended)

**Prevent commits to protected branches:**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

BRANCH=$(git branch --show-current)

case "$BRANCH" in
  main|master|dev)
    echo ""
    echo "❌ Direct commits to '$BRANCH' are not allowed!"
    echo ""
    echo "Create a feature branch first:"
    echo "  git checkout -b <feature-name>"
    echo ""
    exit 1
    ;;
esac

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

**This hook:**
- Runs automatically before every commit
- Blocks commits to protected branches
- Reminds you to create a feature branch
- Can be bypassed with `git commit --no-verify` (for emergencies only)

### Branch Naming Validation

**Ensure branch names follow convention:**

Good branch names:
- ✅ `add-user-authentication`
- ✅ `fix-login-bug`
- ✅ `refactor-payment-logic`
- ✅ `feat/oauth-integration` (with prefix)

Bad branch names:
- ❌ `fixes` (too vague)
- ❌ `john-work` (person-based)
- ❌ `temp` (unclear purpose)
- ❌ `Add User Authentication` (not kebab-case)

**Validation script:**

```bash
validate_branch_name() {
  local branch=$1
  
  # Check if kebab-case (lowercase, hyphens only)
  if ! echo "$branch" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
    echo "⚠️  Branch name should be kebab-case: lowercase with hyphens"
    echo "   Example: add-user-auth"
    return 1
  fi
  
  # Warn if too short
  if [ ${#branch} -lt 5 ]; then
    echo "⚠️  Branch name is very short - consider being more descriptive"
    return 1
  fi
  
  return 0
}
```

---

## Integration with OpenSpec Skills

### How Git Workflow Integrates

**openspec-new-change:**
- After creating change directory
- Checks current Git branch
- Suggests creating feature branch if on protected branch
- Offers to create branch automatically

**openspec-ff-change:**
- Same as new-change
- Sets up Git branch before fast-forward artifact creation

**openspec-apply-change:**
- **CRITICAL**: Blocks implementation on protected branches
- Verifies safe branch before any code changes
- Suggests commits at logical checkpoints during implementation
- Provides commit message templates with change references

**openspec-verify-change:**
- Checks Git status for uncommitted changes
- Warns if verification is run with dirty working tree
- Suggests committing or stashing before verification

**openspec-archive-change:**
- Checks if branch has been pushed to remote
- Warns if changes only exist locally
- Suggests PR creation workflow
- Provides cleanup commands (branch deletion)

**openspec-onboard:**
- Teaches Git workflow as part of onboarding
- Demonstrates feature branch creation
- Shows commit practices during implementation
- Walks through PR workflow

---

## Common Scenarios & Solutions

### Scenario 1: Started implementing on main

**Problem:**
```bash
$ git branch --show-current
main
$ # Oh no! I've been coding on main
```

**Solution:**
```bash
# DON'T PANIC - your work is safe

# Create feature branch (doesn't switch yet)
git branch <change-name>

# Switch to feature branch (takes your changes with you)
git checkout <change-name>

# Verify dev is still clean
git checkout dev
git status  # Should be clean

# Back to feature branch
git checkout <change-name>

# Commit your work
git add .
git commit -m "feat: implemented changes"
```

### Scenario 2: Need to switch changes mid-work

**Problem:**
```bash
$ # Working on feature-a, but urgent bug needs fixing
```

**Solution:**
```bash
# Save current work
git add .
git commit -m "wip: save progress on feature-a"
# or
git stash

# Switch to main and create bug fix branch
git checkout dev
git pull
git checkout -b fix-urgent-bug

# Fix the bug, commit, push, PR

# After bug is merged, return to feature work
git checkout feature-a

# If you stashed
git stash pop
```

### Scenario 3: Accidentally committed to wrong branch

**Problem:**
```bash
$ git branch --show-current
feature-b
$ # But I meant to commit this to feature-a!
```

**Solution:**
```bash
# Cherry-pick the commit to correct branch
COMMIT_HASH=$(git log -1 --format=%H)

git checkout feature-a
git cherry-pick $COMMIT_HASH

# Remove from wrong branch
git checkout feature-b
git reset --hard HEAD~1  # Careful! This removes the commit
```

### Scenario 4: Merge conflicts in PR

**Problem:**
```
PR shows conflicts with dev
```

**Solution:**
```bash
# Update your feature branch with latest dev
git checkout <change-name>
git fetch origin
git merge origin/dev

# Resolve conflicts in your editor
# Look for <<<<<<< and >>>>>>>

# After resolving
git add <resolved-files>
git commit -m "merge: resolve conflicts with dev"
git push

# PR automatically updates
```

### Scenario 5: Want to undo last commit

**Problem:**
```bash
$ git commit -m "feat: thing"
$ # Wait, that commit was wrong!
```

**Solution:**
```bash
# Undo commit, keep changes (most common)
git reset --soft HEAD~1

# Undo commit and changes (DESTRUCTIVE)
git reset --hard HEAD~1  # Be careful!

# Amend last commit (if just need to change message or add files)
git add <forgotten-file>
git commit --amend -m "feat: corrected description"
```

---

## Advanced Patterns

### Rebasing for Clean History

**When to rebase:**
- Before creating PR (clean up work-in-progress commits)
- After PR review (squash fix commits)

**Interactive rebase:**
```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# In editor, you can:
# - pick: keep commit as-is
# - squash: merge into previous commit
# - reword: change commit message
# - drop: remove commit
```

**Example:**
```bash
# Before rebase
fix-bug: initial attempt
fix-bug: fix typo
fix-bug: actually fix it
fix-bug: tests pass

# After rebase (squashed into one)
fix(api): resolve edge case in validation logic
```

**Rebase from dev:
```bash
git checkout <change-name>
git rebase dev

# If conflicts, resolve them
git add <resolved-files>
git rebase --continue

# Force push (since history changed)
git push --force-with-lease
```

### Multiple Changes in Parallel

**Managing multiple feature branches:**

```bash
# List all branches
git branch -a

# Quick switch
git checkout <branch-name>

# See which branch has uncommitted changes
git branch -v

# Clean up merged branches
git branch --merged dev | grep -v "dev" | xargs git branch -d
```

### Stashing for Quick Context Switches

```bash
# Save current work
git stash save "WIP: working on auth flow"

# List stashes
git stash list

# Apply latest stash (keeps it in stash)
git stash apply

# Apply specific stash
git stash apply stash@{1}

# Apply and remove from stash
git stash pop

# Drop a stash
git stash drop stash@{0}
```

---

## Troubleshooting

### "Your branch is ahead of origin/main by N commits"

**Meaning:** You have local commits not pushed to remote.

**Action:**
```bash
git push
```

### "Your branch is behind origin/main by N commits"

**Meaning:** Remote has changes you don't have locally.

**Action:**
```bash
git pull
```

### "Your branch and origin/main have diverged"

**Meaning:** Both local and remote have different commits.

**Action:**
```bash
# If you want remote changes
git pull --rebase

# If your local is correct (rare)
git push --force-with-lease
```

### "fatal: not a git repository"

**Meaning:** Current directory is not a Git repository.

**Action:**
```bash
# Initialize Git
git init

# Or navigate to correct directory
cd /path/to/your/project
```

### Detached HEAD state

**Meaning:** You checked out a specific commit, not a branch.

**Action:**
```bash
# Create branch at current position
git checkout -b <new-branch-name>

# Or return to a branch
git checkout dev
```

---

## Commands Cheat Sheet

### Branch Management
```bash
git branch                     # List local branches
git branch -a                  # List all branches (including remote)
git branch -d <branch>         # Delete branch (safe)
git branch -D <branch>         # Force delete branch
git checkout <branch>          # Switch to branch
git checkout -b <new-branch>   # Create and switch to new branch
git branch --show-current      # Show current branch name
```

### Commits
```bash
git add .                      # Stage all changes
git add <file>                 # Stage specific file
git commit -m "message"        # Commit with message
git commit --amend             # Modify last commit
git reset --soft HEAD~1        # Undo last commit, keep changes
git reset --hard HEAD~1        # Undo last commit, discard changes
```

### Remote Operations
```bash
git fetch                      # Download remote changes (don't merge)
git pull                       # Download and merge remote changes
git push                       # Upload commits to remote
git push -u origin <branch>    # Push and set upstream
git push --force-with-lease    # Force push (safer than --force)
```

### Status & History
```bash
git status                     # Show working tree status
git log                        # Show commit history
git log --oneline              # Compact commit history
git log --oneline -10          # Last 10 commits
git diff                       # Show unstaged changes
git diff --staged              # Show staged changes
```

### Stashing
```bash
git stash                      # Save changes temporarily
git stash save "description"   # Stash with description
git stash list                 # List all stashes
git stash pop                  # Apply and remove latest stash
git stash apply                # Apply latest stash (keep in list)
git stash drop                 # Remove latest stash
```

### Inspection
```bash
git show <commit>              # Show commit details
git blame <file>               # Show who changed each line
git reflog                     # Show all branch movements
```

---

## Best Practices Summary

### ✅ DO

- Create feature branches for all work
- Name branches after OpenSpec changes (kebab-case)
- Commit frequently with clear messages
- Push branches to remote regularly (backup)
- Create Pull Requests for code review
- Delete branches after merge
- Keep commits atomic and focused
- Write descriptive commit messages
- Pull before starting new work
- Rebase to clean up history before PR

### ❌ DON'T

- Commit directly to main/master/dev
- Use vague branch names (temp, fixes, test)
- Make huge commits with multiple unrelated changes
- Force push to shared branches (without --force-with-lease)
- Commit generated files or dependencies
- Leave commented-out code in commits
- Commit sensitive data (.env files, keys, passwords)
- Rebase after pushing (unless you know what you're doing)
- Work without committing for long periods
- Skip code review by merging your own PRs

---

## Output When Invoked

When user runs `/opsx:git-help`:

```
## Git Workflow for OpenSpec

This guide ensures safe development practices with Git and OpenSpec.

### Quick Start

**Start new work:**
```bash
git checkout dev && git pull
git checkout -b <change-name>
```

**During work:**
```bash
# After completing tasks
git add .
git commit -m "feat(<scope>): description"
```

**Finish work:**
```bash
git push -u origin <change-name>
# Create PR on GitHub/GitLab
# After merge:
git checkout dev && git pull
git branch -d <change-name>
```

### Golden Rules

❌ **NEVER** commit to `main`, `master`, or `dev` directly
✅ **ALWAYS** create feature branches
✅ **ALWAYS** use clear commit messages
✅ **ALWAYS** create PR for review

### Need More Detail?

- **Full workflow**: See sections above
- **Common scenarios**: Check troubleshooting section
- **Cheat sheet**: Reference commands section

### Integration with OpenSpec

Git checks are built into:
- `/opsx:apply` - Blocks unsafe implementation
- `/opsx:new` - Suggests branch creation
- `/opsx:archive` - Guides PR workflow
- `/opsx:onboard` - Teaches Git practices

**Protected branch detected?**
If `/opsx:apply` warns about your branch:
1. Create feature branch: `git checkout -b <change-name>`
2. Re-run apply: `/opsx:apply <n>`
```

---

## Guardrails

- Always check for Git repository before providing Git-specific advice
- Block operations on protected branches (main/master/dev) in `/opsx:apply`
- Warn but don't block in other contexts (user may have reasons)
- Provide escape hatches ("Continue anyway" option) for edge cases
- Teach, don't lecture - explain WHY, not just WHAT
- Gracefully handle non-Git projects (don't force Git usage)
- Suggest but don't mandate specific Git workflows (teams may have their own)
- Verify commands work across Git versions and platforms
- Provide copy-pasteable commands that actually work
- Link Git workflow to OpenSpec artifacts (commits reference changes)
