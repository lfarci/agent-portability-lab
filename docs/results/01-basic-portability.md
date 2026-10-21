# Experiment 01 results

**Status:** Partially completed — APM deployment observed; generated contents and harness runtime behavior not yet inspected.

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

The screenshot confirms the directories and lockfile were created, but the individual files' names and contents have **not yet been read or validated**.

## Per-harness findings

| Check | Copilot | Codex | OpenCode |
| --- | --- | --- | --- |
| APM reported agent deployment to target directory | Pass | Pass | Pass |
| Target directory appeared in Git status | Pass | Pass | Pass |
| Expected file present and content verified | Not tested | Not tested | Not tested |
| Agent discovered by harness | Not tested | Not tested | Not tested |
| Explicitly invoked | Not tested | Not tested | Not tested |
| Off-by-one bug identified | Not tested | Not tested | Not tested |
| Marker present in response | Not tested | Not tested | Not tested |
| Fixture unchanged after agent execution | Not tested | Not tested | Not tested |
| Propagation works after source edit | Not tested | Not tested | Not tested |

## Findings so far

1. **Local source deployment works at least at the directory-integration level** with APM 0.34.0; `apm.yml` does not need third-party packages to trigger local `.apm/` integration.
2. **Dry-run preview differed from actual installation.** It reported no changes even though the actual install deployed three local agent primitives.
3. The missing `lfarci/.github-private` policy warning did not block this run. The actual install said no organization policy was found.
4. **No portability conclusion yet:** success at deployment does not establish that the converted Codex TOML is correct, OpenCode accepts its frontmatter, or any harness actually uses the agent.

## Next steps

1. Inspect `.github/agents/reviewer.agent.md`, `.codex/agents/reviewer.toml`, and `.opencode/agents/reviewer.md`.
2. Verify the names, descriptions, reviewer instructions and `APM-REVIEW-COMPLETE` marker.
3. Explicitly invoke the reviewer in available harnesses, using the same C# fixture.
4. Test whether editing only the canonical agent propagates correctly.
5. Record actual versions, outputs, unexpected warnings, and generated-file diffs in a follow-up PR.

**Evidence:** user-provided console dry-run output and screenshot of a verbose successful APM 0.34.0 run. The generated files and lockfile remain local and are not included in this PR.
