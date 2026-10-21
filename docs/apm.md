# Microsoft Agent Package Manager (APM)

[APM](https://microsoft.github.io/apm/) is one possible answer to the [custom-agent portability problem](overview.md). We want to try it before writing our own converter.

APM supports distributing agent assets to different harness targets. It can put Markdown agent definitions in the locations expected by Copilot and OpenCode and transform supported definitions into Codex TOML. That is promising, but **generating a file is not proof of full compatibility**.

Useful references:
- [APM docs](https://microsoft.github.io/apm/)
- [Supported targets](https://microsoft.github.io/apm/reference/targets-matrix/)
- [Instructions and agents](https://microsoft.github.io/apm/producer/author-primitives/instructions-and-agents/)
- [Thomas Thornton's related skills and plugins example](https://thomasthornton.cloud/manage-skills-and-plugins-across-claude-code-codex-and-github-copilot-with-apm/) (helpful for package management, not proof of custom-agent conversion)

## First experiment: one reviewer, three harnesses

We'll use a disposable C# project with a small, intentionally buggy file. Define just one agent at `.apm/agents/reviewer.agent.md`:

```markdown
---
name: reviewer
description: Reviews C# code for correctness and edge cases.
---

You review C# code for correctness and edge cases.
Do not modify files.
Report concrete bugs with locations and suggested fixes.
End with: APM-REVIEW-COMPLETE
```

Then:
1. Install APM and record `apm --version`, OS and harness versions.
2. Check `apm install --help` and set up the manifest/targets for **Copilot, Codex and OpenCode** using the installed version's syntax.
3. Install into this repository (not globally) and save the generated files and command output.
4. Check that each file retains the identity, description and reviewer instructions; inspect the generated Codex TOML.
5. In each installed harness, explicitly select or invoke the reviewer and ask it to review the same buggy C# file. Record whether the agent is discovered, whether it finds the bug, includes the marker, and leaves files unchanged.
6. Change **only the source agent**, regenerate, and check that all target configurations reflect the update.

If a harness isn't installed, mark its runtime check **not tested**. The marker alone doesn't prove the right agent ran; also verify explicit agent selection and file behavior.

### What we'll compare

| Check | Copilot | Codex | OpenCode |
| --- | --- | --- | --- |
| Output generated | Not tested | Not tested | Not tested |
| Agent discovered | Not tested | Not tested | Not tested |
| Reviewer used on fixture | Not tested | Not tested | Not tested |
| Single-source updates work | Not tested | Not tested | Not tested |

## Later experiments

**Tools and permissions:** add metadata to the source, inspect whether each target translates or merely copies it, and test effective restrictions where safe. In particular, loss of tool restrictions must not be treated as harmless.

**Handoffs and delegation:** use a second agent to see whether an orchestration relationship has a real cross-harness equivalent or needs custom configuration.

**Reproducibility:** record the exact APM version, input, generated diff, commands and results. Keep APM away from existing global `skills.sh`-managed directories during these experiments.

## What would make APM good enough?

It would be a good fit if ordinary agent definitions can be kept in one place and regenerated reliably, with clear warnings or escape hatches for unsupported semantics.

If APM deploys files but drops critical restrictions or delegation behavior, we'd first consider documenting the gaps, adding validation, or contributing upstream. An independent converter remains an option, not the default.

**Current status:** no local APM experiments have been performed yet. Everything above is a proposed test, not a compatibility result.
