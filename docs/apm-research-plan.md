# APM custom-agent portability: research plan and discussion record

**Status:** Proposed; experiments not yet executed  
**Recorded:** 2026-10-21  
**Scope:** GitHub Copilot, Codex, OpenCode; Claude Code optional for static output inspection

## Why this project exists

The starting point is the October 15, 2026 article [Beyond GitHub Copilot: Can You Reuse Your AI Setup?](https://www.loganfarci.com/) ([article source](https://github.com/lfarci/loganfarci.com/blob/main/content/articles/from-copilot-to-opencode-configuration-portability.md)). It compares repository instructions, skills, custom agents, MCP and harness settings. Its key outstanding concern was **custom-agent portability**: the same role often needs different file locations, metadata, and configuration formats in Copilot, OpenCode, Codex and Claude Code.

The initial idea was to create a small converter that takes a canonical agent definition and emits harness-native configurations. Before building it, we discovered [Microsoft Agent Package Manager (APM)](https://microsoft.github.io/apm/), which already manages multi-target agent assets. We therefore decided to **evaluate APM first**, not assume either that it solves all portability problems or that a new converter is necessary.

[Thomas Thornton's APM walkthrough](https://thomasthornton.cloud/manage-skills-and-plugins-across-claude-code-codex-and-github-copilot-with-apm/) is a useful companion reference for centralizing skills and plugin dependencies. Our question is narrower: how well does APM handle **custom agent definitions and behavior**, rather than only installing skills?

## Research questions

1. Can one canonical agent definition produce discoverable configurations for Copilot, Codex and OpenCode?
2. How much transformation does APM perform, versus copying files into target directories?
3. Which metadata survive: description, model, tools, permissions, handoffs/delegation?
4. Does each harness actually load and run the resulting agent?
5. Can one source edit be propagated without manual editing of every generated file?
6. Are APM's remaining gaps worth addressing upstream, with a validator/extension, or with an independent converter?

**Do not conflate generated files with runtime compatibility.** All runtime claims require harness-specific tests. Pin the APM version and retain generated artifacts.

## Working hypotheses, not yet test results

APM documents installation of agent files for multiple targets, including Copilot, Codex and OpenCode. The Copilot and OpenCode paths are Markdown-based; Codex agent definitions use TOML, requiring translation. That does **not** imply faithful conversion of model IDs, tool permissions or delegation semantics. Some copied YAML frontmatter might be unsupported by a receiving harness.

We will independently verify:
- the exact APM CLI flags and manifest schema in the **installed version** with `apm --help`, `apm install --help`, and the [official docs](https://microsoft.github.io/apm/);
- the generated filenames/paths and whether any files are overwritten;
- the behavior of tool restrictions (a potential safety issue if silently discarded);
- whether the instructions are activated by selecting the named agent, not merely repeated by a default assistant.

## Experimental setup

Keep the project disposable and separate from personal [dotfiles](https://github.com/lfarci/dotfiles). The existing dotfiles use `skills.sh`, vendored skills and `.skill-lock.json`; do **not** let two managers independently own those same global directories.

Proposed layout (paths are targets to verify, not evidence of successful generation):

```text
agent-portability-lab/
├── README.md
├── apm.yml                         # add during experiment
├── apm.lock.yaml                   # generated/pinned when applicable
├── .apm/agents/reviewer.agent.md   # canonical definition
├── .github/agents/                 # Copilot output
├── .codex/agents/                  # Codex output
├── .opencode/agents/               # OpenCode output
├── src/ScoreCalculator.cs          # intentionally buggy fixture
├── docs/
│   ├── apm-research-plan.md        # this document
│   └── results/                    # fill with observed runs
└── scripts/                        # optional reproducible verification
```

### Minimal canonical reviewer

Create `.apm/agents/reviewer.agent.md`:

```markdown
---
name: reviewer
description: Reviews C# code for bugs and edge cases without editing files.
---

You are a focused C# code reviewer.
- Do not modify files.
- Prioritize correctness over style.
- Report concrete findings with file locations and suggested fixes.
- Finish with: APM-REVIEW-COMPLETE
```

The marker checks that the instruction *may* have loaded; it is not sufficient proof by itself. Verify actual agent selection and file changes too.

### Suggested procedure

1. Install and record `apm --version`; inspect CLI help before using any proposed flags. Record OS, CLI versions and git commit.
2. Initialize a minimal manifest with targets for `copilot`, `codex`, `opencode` according to the installed APM documentation. Prefer project-local output, not `--global`.
3. Run an APM dry run if supported, then install. Capture stdout/stderr, generated paths and content, and relevant git diff.
4. Inspect each generated agent: identity, prompt body, metadata, permissions, model field, and unsupported keys.
5. Test in GitHub Copilot: explicitly select `reviewer`, request review of the intentionally buggy C# fixture; check report, marker and `git status`.
6. Repeat in OpenCode. If Codex is available, select/delegate to its generated agent and repeat. Otherwise label Codex **generation only; runtime not tested**.
7. Edit **only** the canonical definition (e.g., require a suggested unit test per bug), reinstall, and compare changes to all target files.
8. Record exact commands, output, compatibility observations and failures in `docs/results/`.

Do not automatically run potentially dangerous generated agents against sensitive projects; this is a throwaway test repository.

## Planned experiments and acceptance criteria

| Experiment | What changes | What counts as evidence |
| --- | --- | --- |
| 01 — Basic deployment | Minimal name, description, instructions | Three generated files; correct bodies; agent discovered and independently invoked where installed |
| 02 — Metadata and restrictions | Add tool constraints, model values, harness-specific frontmatter | Explicit per-target diff, validation errors/warnings and actual access-boundary checks where safe |
| 03 — Delegation | Reviewer-to-implementer workflow | Demonstrated supported native handoff/delegation, or a documented gap; do not infer from filenames |
| 04 — Update propagation | One edit to canonical source | All expected outputs change; no hand-edited target files; reproducible lock/version record |

Record each status as **Pass**, **Fail**, **Partial**, or **Not tested** and attach evidence. A syntactically valid artifact is not a pass for runtime behavior.

### Results template

For each run create `docs/results/YYYY-MM-DD-<experiment>.md` containing:

```markdown
# Experiment: <name>
- Date / OS:
- APM version / manifest commit:
- Harness names and versions:
- Exact commands:
- Inputs and canonical source:
- Generated file paths and relevant diffs:
- Discovery and invocation steps:
- Actual observations:
- Status per harness (Pass / Fail / Partial / Not tested):
- Missing metadata or changed semantics:
- Reproduction notes and open issues:
```

## How we'll decide: adopt APM or build our own?

**Default: prefer APM if it meets the reproducible needs.** Do not build a competing converter based only on speculation.

- **Adopt APM:** common agent definitions deploy cleanly, are discoverable and preserve the semantics we actually need.
- **Use APM plus small validation:** deployment succeeds, but unsupported metadata needs linting, guardrails or explicit per-harness overlays.
- **Contribute upstream:** a well-defined transformation gap can be fixed or discussed in APM.
- **Consider a custom converter:** only if essential portability requirements repeatedly fail and upstream/extension solutions cannot reasonably cover them.

A **portability validator** is a more plausible first custom tool than reimplementing installation and format conversion.

## Publication plan

After the experiments, write a follow-up article for [loganfarci.com](https://www.loganfarci.com) tentatively titled **One AI Agent, Multiple Harnesses: Putting Microsoft APM to the Test**. Link the lab, capture exact tested versions, show input-to-output diffs, distinguish file deployment from behavioral equivalence, and publish the decision *after* collecting results. Reference the earlier article and Thomas Thornton's skills/plugin setup without presenting his walkthrough as evidence of custom-agent semantic conversion.

## References

- [Microsoft APM documentation](https://microsoft.github.io/apm/)
- [APM target support matrix](https://microsoft.github.io/apm/reference/targets-matrix/)
- [APM instructions and agents](https://microsoft.github.io/apm/producer/author-primitives/instructions-and-agents/)
- [Original agent portability article, source](https://github.com/lfarci/loganfarci.com/blob/main/content/articles/from-copilot-to-opencode-configuration-portability.md)
- [Thomas Thornton: Manage Skills and Plugins Across Claude Code, Codex, and GitHub Copilot with APM](https://thomasthornton.cloud/manage-skills-and-plugins-across-claude-code-codex-and-github-copilot-with-apm/)

## Conversation decisions captured

- Focus on **custom agents**, not an exhaustive comparison of skills managers.
- Target Copilot, Codex and OpenCode first; Claude Code can be added later.
- Maintain the experiment and observed evidence in a dedicated public repository.
- Keep personal dotfiles and vendored skills unchanged during the test.
- Do not write the final conclusions or build an independent converter until the evidence is available.
