# Agent Portability Lab

A small reproducible lab investigating how [Microsoft Agent Package Manager (APM)](https://microsoft.github.io/apm/) distributes **agent profiles** across GitHub Copilot, OpenCode, and Codex.

**Status: two experiments completed (October 21, 2026).** The first demonstrated basic instruction portability; the second found gaps in tool-restriction translation. Runtime security enforcement was **not** tested.

## Experiments and evidence

| Experiment | Result | Instructions | Observations |
| --- | --- | --- | --- |
| 01 — Basic agent portability | Generated reviewer profiles worked for the same C# bug review across three harnesses; a source update propagated to all three | [Runbook](docs/experiments/01-basic-portability.md) | [Results](docs/results/01-basic-portability.md) |
| 02 — Tool-restriction portability | APM copied an invalid Copilot `tools` mapping, did not generate OpenCode v2 native permission rules, and warned that Codex dropped tool restrictions | [Runbook](docs/experiments/02-tool-restrictions.md) | [Results](docs/results/02-tool-restrictions.md) |

**These are narrow tests of APM 0.34.0, not a claim of universal cross-harness compatibility.** In particular, generating an agent file does not establish that a harness accepts or enforces all its settings.

## How to reproduce

The source definitions live in [`.apm/agents/`](.apm/agents/), and the intentionally flawed C# fixture is [`src/ScoreCalculator.cs`](src/ScoreCalculator.cs). From the repository root, with APM installed:

```bash
apm install --target copilot,codex,opencode --verbose
```

The generated definitions are committed under [`.github/agents/`](.github/agents/), [`.opencode/agents/`](.opencode/agents/), and [`.codex/agents/`](.codex/agents/). Don't edit those generated files manually; regenerate them from the canonical source.

Experiment 02 includes a **focused** Python compatibility check. It needs PyYAML and, for OpenCode, the installed major version. On OpenCode v2:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyyaml
python scripts/validate-experiment-02.py --opencode v2
```

The validator is **expected to report three incompatibility findings and exit nonzero** for the deliberately nonportable `restricted-reviewer` fixture. It is not a full vendor schema validator or proof of runtime permissions. If `venv` is unavailable on Ubuntu, install the matching Python `python3.x-venv` package first.

Read the runbooks and results before executing an agent or interpreting a generated restriction as a security boundary.
