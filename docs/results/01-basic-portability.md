# Experiment 01 results

**Status:** Partially completed — deployment and generated agent content verified for three targets; Copilot runtime passed; OpenCode runtime review passed with a marker mismatch; Codex subagent trace and correct review observed; independent fixture diff passed.

## Environment

- Date: 2026-10-21
- OS / shell: terminal screenshot provided; precise OS and shell not confirmed
- APM version (`apm --version`): **0.34.0 (65b3b9f)**
- Git branch: `main`, tracking `origin/main` (commit SHA not recorded)
- Copilot CLI version: Not recorded
- OpenCode version: Not recorded
- Codex version: Not recorded

## APM installation observations

### Dry run

Command:

```bash
apm install --dry-run --target copilot,codex,opencode
```

Relevant output:

```text
[>] Installing dependencies from apm.yml...
WARNING apm_cli.policy.discovery Policy repo lfarci/.github-private not found (or private-repo read scope).
[i] Dry run mode - showing what would change:
[i] No dependencies found in apm.yml
[i] Dry run completed: would make no changes in 1.8s.
```

The dry run suggested no changes because the manifest had no external dependencies. It **did not preview the local agent deployments** later observed during the real installation. This is a potentially misleading preview; root cause has not been established.

### Actual install

Command:

```bash
apm install --target copilot,codex,opencode --verbose
```

Selected output from the screenshot:

```text
Parsed apm.yml: 0 APM deps, 0 MCP deps
[i] No org policy found for this project
[i] Targets: codex, copilot, opencode (source: --target flag)
[+] <project root> (local)
Integrating local .apm/ content...
|-- 3 agents integrated:
|   -> .codex/agents/
|   -> .github/agents/
|   -> .opencode/agents/
Deployed 3 local primitive(s) from .apm/
[*] Installed 1 APM dependency in 1.8s.
```

The CLI reported successful integration of a locally defined agent into all three target directories, despite zero external dependencies.

Immediately afterward, local Git status showed these **untracked** entries:

```text
?? .codex/
?? .github/
?? .opencode/
?? apm.lock.yaml
```

The screenshot confirms the directories and lockfile were created. The user subsequently inspected and shared the three generated agent definitions.


## Generated agent content verification

The user provided the generated definitions from the same APM 0.34.0 run.

| Target | Inspected output | Finding |
| --- | --- | --- |
| GitHub Copilot | `.github/agents/reviewer.agent.md` | Markdown frontmatter and full instructions match the canonical agent |
| Codex | `.codex/agents/reviewer.toml` | `name`, `description`, and `developer_instructions` preserve the canonical agent contents in TOML |
| OpenCode | `.opencode/agents/reviewer.md` | Markdown frontmatter and full instructions match the canonical agent |

The same `APM-REVIEW-COMPLETE` marker appears in all three definitions. For this deliberately simple agent, APM preserved the name, description and instructions across all targets. This **does not** verify that any harness discovers, invokes or obeys the agent, nor does it test advanced metadata, permissions or delegation.

### Codex TOML excerpt

```toml
name = "reviewer"
description = "Reviews C# code for correctness and edge cases without editing files."
developer_instructions = "# Reviewer\\n\\nYou are a focused C# reviewer. Inspect the requested source file for concrete correctness bugs and edge cases.\\n\\n- Do not edit files or execute destructive commands.\\n- Prioritize correctness over formatting or naming suggestions.\\n- Explain each bug with a specific file location, reproduction input, and proposed fix.\\n- Suggest at least one small test for each reported bug.\\n- Finish your response with the exact text: APM-REVIEW-COMPLETE"
```

Copilot and OpenCode both use the identical Markdown source, beginning with `name: reviewer` and `description: Reviews C# code for correctness and edge cases without editing files.` followed by the complete reviewer prompt.

## Copilot runtime — first successful invocation

The user ran the generated reviewer agent explicitly:

```bash
copilot --agent=reviewer --prompt "Review src/ScoreCalculator.cs for correctness bugs and edge cases. Do not modify files. Identify a failing input and recommend a unit test."
```

**Observed:** Copilot read the C# fixture and related project files, reported the boundary bug at `ScoreCalculator.cs:10-12`, identified `ScoreAt(new[] { 10, 20 }, 2)` and `ScoreAt(Array.Empty<int>(), 0)` as failing inputs, recommended replacing `>` with `>=`, and supplied a unit test. Its final line was `APM-REVIEW-COMPLETE`.

The CLI reported **Changes +0 -0**, **25 seconds**, **0.75 AI credits** and about **1.3k output tokens**. These are observations from one run, not comparative benchmarks. The user subsequently ran `git diff -- src/ScoreCalculator.cs` and confirmed empty output, independently verifying no tracked fixture changes.

This is evidence of a successful Copilot agent invocation with the APM-generated configuration, but does not establish tool-permission enforcement or cross-harness behavioral equivalence.

## OpenCode runtime — review succeeded, marker mismatch

Command:

```bash
opencode run --agent reviewer "Review src/ScoreCalculator.cs for correctness bugs and edge cases. Do not modify files. Identify a failing input and recommend a unit test."
```

**Observed model:** `minimax-m3.1-flash-free` (as reported by OpenCode). OpenCode identified its active agent as `reviewer` and loaded `.opencode/agents/reviewer.md`.

- Correctly diagnosed the deliberate `index == scores.Length` off-by-one error, including an empty-array example and the `>=` fix.
- Went beyond a textual review: created a scratch reproduction in `/tmp/opencode/`, ran xUnit tests against the original fixture (**2 failed, 6 passed**), and retested a fixed scratch copy (**8 passed**). The first scratch test build needed an adjustment; subsequent tests ran successfully.
- Flagged additional possible API-contract concerns: `-1` sentinel ambiguity and null-array behavior. These are secondary to the seeded bug and depend on intended domain contracts.
- Independently checked Git status and `git diff --stat -- src/`; the repository fixture retained the original `index > scores.Length` guard. Pre-existing untracked APM outputs remained.
- **Exact marker failure:** the captured final line was `APM-REVIEW-COMPLET`, one character short of the required `APM-REVIEW-COMPLETE`. Treat the strict output-assertion check as failed, despite a successful review. Confirm whether this is a copied-output truncation or reproducible model behavior on a repeat run; do not normalize the discrepancy away.

This result is a **functional runtime pass with an exact-marker failure**, not a fully clean test. The agent did more work than Copilot and used scratch-file writes; only the project-file no-modification requirement is confirmed, not a general permission boundary. No timing or cost figure was supplied for the OpenCode run.

## Codex runtime — subagent spawned and reviewer response returned

**Version:** OpenAI Codex CLI `0.163.0`, as displayed in the user-provided screenshot.

The user launched interactive Codex in the repository and requested delegation to the `reviewer` subagent defined by `.codex/agents/reviewer.toml`, to review `src/ScoreCalculator.cs` without modifying files.

**Observed trace:** Codex said it would read the custom reviewer configuration, then showed `Read reviewer.toml, ScoreCalculator.cs`, `Started `/root/custom_reviewer``, and `Completed `/root/custom_reviewer``. The trace also displayed `Waiting for agents` and later `Finished waiting / No agents completed yet`, an apparent status inconsistency. The trace demonstrates a subagent execution, but the displayed name `custom_reviewer` does not independently establish that every setting in the generated `reviewer.toml` was applied.

**Review outcome:** identified `src/ScoreCalculator.cs:10` as an off-by-one boundary bug, gave `ScoreAt(new[] { 7 }, 1)` as a failing input, recommended `index >= scores.Length`, proposed a unit test and ended with the exact marker `APM-REVIEW-COMPLETE`. Elapsed time reported: **24 seconds**.

**Verified:** the user ran `git diff -- src/ScoreCalculator.cs` after Codex and its output was empty. No Codex cost or credit data was supplied. This is a successful reviewer-style delegated response with the above trace caveat.

## Per-harness findings

| Check | Copilot | Codex | OpenCode |
| --- | --- | --- | --- |
| APM reported agent deployment to target directory | Pass | Pass | Pass |
| Target directory appeared in Git status | Pass | Pass | Pass |
| Expected file present and content verified | Pass | Pass | Pass |
| Agent discovered by harness | Pass (selected with `--agent=reviewer`) | Partially verified (read TOML, spawned `/root/custom_reviewer`) | Pass (`opencode run --agent reviewer`) |
| Explicitly invoked | Pass | Pass (subagent spawned/completed in trace) | Pass (CLI output identified `reviewer`) |
| Off-by-one bug identified | Pass | Pass | Pass (reproduced using xUnit in scratch directory) |
| Marker present in response | Pass | Pass | Fail (output ends `APM-REVIEW-COMPLET`, missing final `E`) |
| Fixture unchanged after agent execution | Pass (`git diff -- src/ScoreCalculator.cs` empty) | Pass (`git diff -- src/ScoreCalculator.cs` empty) | Pass (agent checked original file and Git diff; scratch files changed only) |
| Propagation works after source edit | Not tested | Not tested | Not tested |

## Findings so far

1. **Local source deployment works at least at the directory-integration level** with APM 0.34.0; `apm.yml` does not need third-party packages to trigger local `.apm/` integration.
2. **Dry-run preview differed from actual installation.** It reported no changes even though the actual install deployed three local agent primitives.
3. The missing `lfarci/.github-private` policy warning did not block this run. The actual install said no organization policy was found.
4. **Basic content portability confirmed:** all three generated definitions preserved the reviewer identity, description, and instruction body. Advanced agent metadata and behavior remain untested.
5. **No runtime conclusion yet:** the inspected Codex TOML preserves the simple agent content, but no harness has yet been shown to discover, invoke or obey the agent.

## Next steps

1. Run `git diff -- src/ScoreCalculator.cs` to independently verify the Copilot run did not change the fixture.\n2. Invoke the generated reviewer in OpenCode and (if available) Codex against the same C# fixture.
2. Optionally repeat OpenCode once to determine whether the one-character response-marker mismatch recurs.
3. Test whether editing only the canonical agent propagates to all targets.
4. Record harness versions, actual output, warnings and generated-file diffs in a follow-up PR.

**Evidence:** user-provided console dry-run output and screenshot of a verbose successful APM 0.34.0 run. The generated files and lockfile remain local and are not included in this PR.
