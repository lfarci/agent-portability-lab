# Experiment 02 results: tool-restriction portability

**Status:** Phase A (generation and focused static validation) completed locally on `experiment/02-tool-restrictions`, 2026-10-21. Phase B (runtime permission enforcement) **not tested**.

## Environment

- OS: Ubuntu 26.04 on WSL
- Python: 3.14.4
- APM: 0.34.0 (65b3b9f)
- OpenCode: v2.0.30
- Git branch: `experiment/02-tool-restrictions` (exact tested commit not recorded)
- GitHub Copilot and Codex versions: not recorded for this run

## APM generation

Command:

```bash
apm install --target copilot,codex,opencode --verbose 2>&1 | tee /tmp/apm-experiment-02-install.log
```

APM reported targets `codex, copilot, opencode`, integrated the local agents, and completed installation in about 1.8 seconds. It emitted **one lossy agent compilation warning**:

```text
Codex agent restricted-reviewer.agent.md: frontmatter field 'tools' was dropped; the agent may inherit all project/session MCP servers.
Fix: remove 'tools' if unrestricted access is intentional; otherwise do not use the generated agent with Codex.
```

A separate `lfarci/.github-private` policy discovery warning was non-blocking.

## Static configuration findings

| Check | GitHub Copilot | Codex | OpenCode v2 |
| --- | --- | --- | --- |
| Generated agent file | Observed | APM reported generation; output not pasted separately | Observed |
| Canonical `tools` preserved | Yes, verbatim mapping | No, dropped with warning | Yes, verbatim legacy mapping |
| Native restriction translation | No | No | No modern `permissions` generated |
| Schema / focused contract | Invalid `tools` type | Restricted semantics lost | No native v2 `permissions` rules |
| Runtime enforcement | Not tested | Not tested | Not tested |

The VS Code Copilot schema diagnostic stated: **“The 'tools' attribute must be an array or a comma separated string.”** The generated agent carried the original boolean mapping instead.

OpenCode's generated Markdown likewise preserved `tools: { read: true, grep: true, edit: false, bash: false }`, rather than a v2 `permissions` rules array. This is evidence of missing native translation, **not proof that OpenCode ignores the legacy mapping at runtime**.

## Focused validator run

Command:

```bash
python scripts/validate-experiment-02.py --opencode v2
```

Observed output:

```text
WARN opencode: legacy tools mapping present; not proof of modern permission enforcement
FAIL copilot: tools must be a string or array of strings (received mapping)
FAIL opencode: v2 requires permissions as a rule array for this restricted fixture
FAIL codex: canonical tool restrictions were dropped (APM-reported loss)
Result: 3 incompatibility finding(s), 1 warning(s)
```

The intentionally nonzero exit status is the expected **test detection outcome**, not a validator crash. The script checks a small selection of known fields and fixture policy requirements; it is **not a complete upstream schema validator**.

## Conclusion

APM 0.34.0 distributes simple agent instructions across all three harnesses, but the canonical restricted-reviewer tool policy was **not portably transformed**: invalid Copilot metadata, no modern OpenCode v2 permission translation, and an explicit Codex field-loss warning. No runtime permission enforcement was tested.

The APM team's broader tool-neutral agent semantic model is deferred under [microsoft/apm#2108](https://github.com/microsoft/apm/issues/2108); the current product priority is native plugin delivery under [#3094](https://github.com/microsoft/apm/issues/3094).

## Follow-up

- Keep this deliberately incompatible fixture as reproducible evidence.
- Consider separate native configurations and **controlled** runtime enforcement tests as Experiment 03, not part of Phase A.
- Investigate a narrowly scoped schema/compatibility diagnostic without treating policy portability as guaranteed.
