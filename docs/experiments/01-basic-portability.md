# Experiment 01: one agent, three harnesses

**Status: not run.** This is a hands-on experiment, not a claim of compatibility.

## Question

Can Microsoft APM take one custom-agent definition in `.apm/agents/reviewer.agent.md`, deploy it for GitHub Copilot, Codex and OpenCode, and let each installed harness discover and execute the same reviewer?

This experiment covers basic names, descriptions and instructions. Tool restrictions, model mapping and delegation are separate experiments.

## Prerequisites

- Clone the repository and check out this experiment branch (or merge it first).
- Install [Microsoft APM](https://microsoft.github.io/apm/) using its [installation guide](https://microsoft.github.io/apm/installation/).
- Have the GitHub Copilot CLI and/or OpenCode available. Codex is optional: static-file verification is still useful.
- For the C# fixture, .NET 8 SDK is optional; no compilation is needed to identify the intentional bug.
- Run everything **locally inside this repository**, not with APM's `--global` option.

## Run

From the repository root:

```bash
apm --version
apm install --help
apm install --dry-run --target copilot,codex,opencode
apm install --target copilot,codex,opencode
```

These flags are documented by APM, but capture your installed version and any differences before continuing. The manifest intentionally declares no external packages, so the test focuses on the repository's own `.apm/agents/` source.

Check the expected outputs:

```bash
ls -l .github/agents/reviewer.agent.md .codex/agents/reviewer.toml .opencode/agents/reviewer.md
cat .github/agents/reviewer.agent.md
cat .codex/agents/reviewer.toml
cat .opencode/agents/reviewer.md
git status --short
git diff -- .github/agents .codex/agents .opencode/agents apm.lock.yaml
```

Expected *on paper*, based on APM documentation:

| Target | Expected file | Expected transformation |
| --- | --- | --- |
| Copilot | `.github/agents/reviewer.agent.md` | Markdown copied |
| Codex | `.codex/agents/reviewer.toml` | Markdown converted to TOML (body as `developer_instructions`) |
| OpenCode | `.opencode/agents/reviewer.md` | Markdown copied |

Record what was **actually** produced. Do not mark a runtime success just because a file exists.

## Runtime check

Use **the same prompt** in every installed harness:

> Review `src/ScoreCalculator.cs` for correctness bugs and edge cases. Do not edit files. Identify a failing input and recommend a unit test.

- **Copilot CLI:** explicitly select the `reviewer` agent (for example via `/agent` or the version-appropriate `--agent` option) and issue the prompt.
- **OpenCode:** open the repository, invoke `@reviewer`, and issue the prompt.
- **Codex:** if available, explicitly delegate the review to the `reviewer` agent using that installed version's supported mechanism. Otherwise record “Not tested”.

Observe whether the response catches the intentional **off-by-one**: `index == scores.Length` passes the guard but causes an `IndexOutOfRangeException`. The safe boundary is `index >= scores.Length`.

Check whether the response ends with `APM-REVIEW-COMPLETE`. This marker supports, but cannot alone prove, agent selection. Finally run `git status --short` to make sure the agent didn't edit the fixture.

## Propagation check

Edit only the canonical `.apm/agents/reviewer.agent.md`, adding:

> For each bug, include an explicit example of the expected return value or exception.

Rerun `apm install --target copilot,codex,opencode`; check that the relevant generated files reflect the change. Capture any file-ownership or overwrite warning. Do not use `--force` to conceal unexpected conflicts.

## Capture results

Copy [the results template](../results/01-basic-portability.md) and fill out the environment details, exact commands, generated diffs and runtime observations. Commit generated output and the lockfile in a separate evidence PR **after** running APM, not as fabricated initial results.

## References

- [APM `install` command](https://microsoft.github.io/apm/reference/cli/install/)
- [APM agent primitives and target paths](https://microsoft.github.io/apm/producer/author-primitives/instructions-and-agents/)
- [Project scope](../overview.md)
- [APM candidate notes](../apm.md)
