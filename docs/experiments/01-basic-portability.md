# Experiment 01: one agent, three harnesses

**Status: completed for the basic portability scope on 2026-10-21.** See the [recorded results](../results/01-basic-portability.md) for passes, caveats and remaining questions.

## Question

Can Microsoft APM take one custom-agent definition in `.apm/agents/reviewer.agent.md`, deploy it for GitHub Copilot, Codex and OpenCode, and let each installed harness discover and execute the same reviewer?

This experiment covers basic names, descriptions and instructions. Tool restrictions, model mapping and delegation are separate experiments.

## Prerequisites

- Clone the repository and use the `main` branch. The experiment scaffold was merged in PR #2; no experiment branch is needed.
- Install [Microsoft APM](https://microsoft.github.io/apm/) and your harness CLIs following [the lab installation guide](../install.md).
- Have the GitHub Copilot CLI and/or OpenCode available. Codex is optional: static-file verification is still useful.
- For the C# fixture, .NET 8 SDK is optional; no compilation is needed to identify the intentional bug.
- Run everything **locally inside this repository**, not with APM's `--global` option.

## Run

Clone the repository (or use your existing checkout) and run the experiment on **`main`**:

```bash
git clone https://github.com/lfarci/agent-portability-lab.git
cd agent-portability-lab
git switch main
git pull --ff-only
```

If you have existing local edits, do not run `git pull` until you've reviewed or preserved them. Record the tested commit with `git rev-parse HEAD`; the initial run used `0c559e7` on `main`.

Verify the installed tools and record their versions (missing optional CLIs are **Not tested**, not failures):

```bash
git rev-parse HEAD
apm --version
copilot --version
opencode --version
codex --version  # optional
```

From the repository root run:

```bash
apm install --dry-run --target copilot,codex,opencode
apm install --target copilot,codex,opencode --verbose
```

The manifest intentionally declares no external packages, so the test focuses on the repository's own `.apm/agents/` source. **Observed with APM 0.34.0:** the dry run said it would make no changes, but the actual install integrated all three local agents. Do not treat the dry-run result as proof that no local files will be generated.

Check the expected outputs:

```bash
ls -l .github/agents/reviewer.agent.md .codex/agents/reviewer.toml .opencode/agents/reviewer.md
cat .github/agents/reviewer.agent.md
cat .codex/agents/reviewer.toml
cat .opencode/agents/reviewer.md
git status --short  # generated files may be untracked; git diff won't display untracked content
```

Observed in the initial APM 0.34.0 run:

| Target | Generated file | Observed transformation |
| --- | --- | --- |
| Copilot | `.github/agents/reviewer.agent.md` | Markdown copied |
| Codex | `.codex/agents/reviewer.toml` | Markdown converted to TOML (body as `developer_instructions`) |
| OpenCode | `.opencode/agents/reviewer.md` | Markdown copied |

Record what was **actually** produced. Do not mark a runtime success just because a file exists.

## Runtime check

Use **the same prompt** in every installed harness:

> Review `src/ScoreCalculator.cs` for correctness bugs and edge cases. Do not edit files. Identify a failing input and recommend a unit test.

- **Copilot CLI:** run:

  ```bash
  copilot --agent=reviewer --prompt "Review src/ScoreCalculator.cs for correctness bugs and edge cases. Do not modify files. Identify a failing input and recommend a unit test."
  ```

- **OpenCode:** run:

  ```bash
  opencode run --agent reviewer "Review src/ScoreCalculator.cs for correctness bugs and edge cases. Do not modify files. Identify a failing input and recommend a unit test."
  ```

- **Codex:** run `codex` interactively from the repository root and request:

  > Delegate the review of `src/ScoreCalculator.cs` to the custom `reviewer` subagent defined in `.codex/agents/reviewer.toml`. Do not modify files. Identify a failing input and recommend a unit test. Return the subagent's findings and its exact completion marker.

  Inspect the agent-spawn trace: a good review by the main agent alone does **not** demonstrate delegation. The observed Codex 0.163.0 trace spawned `/root/custom_reviewer`; that display name does not by itself prove every TOML setting was used.

Observe whether the response catches the intentional **off-by-one**: `index == scores.Length` passes the guard but causes an `IndexOutOfRangeException`. The safe boundary is `index >= scores.Length`.

Check whether the response ends with `APM-REVIEW-COMPLETE`. This marker supports, but cannot alone prove, agent selection. After **each** harness run, run `git diff -- src/ScoreCalculator.cs` and verify the output is empty. Use `git status --short` to distinguish edits from the APM-generated untracked files.

## Propagation check

Edit only the canonical `.apm/agents/reviewer.agent.md`, adding:

> - For each bug, include the expected return value or exception.

Rerun `apm install --target copilot,codex,opencode`, then check for the instruction in all three outputs:

```bash
grep -F "For each bug, include the expected return value or exception." \
  .github/agents/reviewer.agent.md \
  .codex/agents/reviewer.toml \
  .opencode/agents/reviewer.md
```

Expect three matching files, including the instruction within Codex's TOML `developer_instructions`. Capture any overwrite warning. Do not use `--force` to conceal unexpected conflicts.

## Capture results

The actual initial run and outcomes are documented in [Experiment 01 results](../results/01-basic-portability.md). For a rerun, record versions, tested `main` commit, command output, exact marker, Git diff checks and any changed behavior. Generated files and the lockfile were kept local during the first run; add them to a separate evidence PR only if needed for reproducibility.

## References

- [APM `install` command](https://microsoft.github.io/apm/reference/cli/install/)
- [APM agent primitives and target paths](https://microsoft.github.io/apm/producer/author-primitives/instructions-and-agents/)
- [Project scope](../overview.md)
- [APM candidate notes](../apm.md)
