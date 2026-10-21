# Experiment 02: portable tool restrictions

**Status: Phase A completed on 2026-10-21.** See [recorded results](../results/02-tool-restrictions.md). Phase B remains untested.

## Question

When APM deploys a custom agent with an explicit `tools` allow/deny mapping, do GitHub Copilot, OpenCode and Codex receive usable restrictions? Are warnings issued when equivalent enforcement cannot be generated?

Experiment 01 established that the three harnesses can use a basic agent. This experiment tests whether *permission-bearing metadata* travels correctly, not whether a model voluntarily follows "do not edit" instructions.

## Documented expectations (verify against installed APM)

APM documentation says `model` and `tools` agent frontmatter are passed to Copilot and OpenCode **verbatim**, but Codex conversion keeps only the agent name, description and Markdown body, warning that restricted tools are not preserved. OpenCode expects `tools` to be a boolean mapping; Copilot's supported tool selection format may differ. An output file existing does not imply a valid or enforced policy.

Reference: [APM agent workflows](https://microsoft.github.io/apm/guides/agent-workflows/) and [targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/).

## Fixture

A **new** canonical file, `.apm/agents/restricted-reviewer.agent.md`, deliberately uses a boolean mapping:

```yaml
tools:
  read: true
  grep: true
  edit: false
  bash: false
```

This probes OpenCode's documented mapping format, Copilot's treatment of that same format, and Codex's loss of tool restrictions. Tool identifiers are not claimed to map equivalently between harnesses. Keep the Experiment 01 reviewer and buggy `src/ScoreCalculator.cs` unchanged.

## Phase A: static conversion (no AI credits)

For the initial run, use **`experiment/02-tool-restrictions`** until PR #6 is merged; afterward use `main`. In the repository root:

```bash
git rev-parse --short HEAD
apm --version
apm install --target copilot,codex,opencode --verbose 2>&1 | tee /tmp/apm-experiment-02-install.log
```

Use the **normal install**, not only `--dry-run`: Experiment 01 found that APM 0.34.0 dry run did not preview local agent integration. Inspect any warnings, particularly Copilot validation, OpenCode validation and Codex restriction-loss diagnostics.

Inspect generated definitions without modifying them:

```bash
cat .github/agents/restricted-reviewer.agent.md
cat .opencode/agents/restricted-reviewer.md
cat .codex/agents/restricted-reviewer.toml
git status --short
```

Inspect the emitted `tools` fields (or their absence). A string match alone is **not** evidence that the harness interprets or enforces them. If a generated file is missing, record that instead of guessing why.

The outcome to record for each target is:
- generated file present?
- `tools` retained, transformed, dropped or warned about?
- format valid according to the harness's documented schema?
- what security property, if any, has actually been demonstrated? (For Phase A: **none**.)

Do not stage generated outputs until reviewing `apm.lock.yaml` and checking for sensitive content. Do not use `--force` to hide conflicts.

## Focused schema validation

After the APM install, run the lightweight validator from the repository root. It checks the observed generated **restricted reviewer** against selected documented contracts, not every possible vendor field:

```bash
sudo apt install python3.14-venv  # Ubuntu 26.04, if ensurepip is missing
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pyyaml
opencode --version
python scripts/validate-experiment-02.py --opencode v2
```

If your installed OpenCode is **v1**, replace `--opencode v2` with `--opencode v1`. OpenCode [v1 agent permissions](https://opencode.ai/docs/agents/#permissions) use a `permission` mapping, while [v2 agent docs](https://opencode.ai/v2/docs/agents) show a `permissions` list of rules. Use the matching version rather than conflating schemas.

**Expected for our deliberately incompatible fixture:** the validator exits nonzero, reporting (1) Copilot requires a list/string rather than a mapping, (2) no explicit OpenCode native permission-denial rules, and (3) the Codex restriction loss. The APM warning and validator findings are separate evidence. The script is a focused experiment diagnostic, **not** a comprehensive vendor schema validator or security enforcement test.

## Phase B: later, separate controlled enforcement test

Only after studying the Phase A result, design a minimal runtime test involving a **disposable, untracked, isolated fixture**. Set independent host-level restrictions where needed. Determine whether a request to modify the fixture is blocked **by tool availability or sandbox policy**, allowed, or merely declined because of instructions. Test one harness at a time with explicit opt-in to any AI-credit usage.

Do **not** interpret an unchanged file as proof that a permission boundary was enforced. Avoid giving an agent access to sensitive project material or relying on portable agent metadata as a security boundary.

## Record results

The actual initial output is recorded in [Experiment 02 results](../results/02-tool-restrictions.md). For reruns record the installed versions, exact commands, warnings and outputs. Leave unexecuted steps as **Not tested**.
