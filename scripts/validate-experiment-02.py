#!/usr/bin/env python3
"""Focused static checks for Experiment 02 generated reviewer agents.

Not a complete vendor JSON/YAML schema validator, and not an enforcement test.
Requires PyYAML: python -m pip install pyyaml
"""
import argparse
from pathlib import Path
import sys
import tomllib

import yaml

AGENT = "restricted-reviewer"
ROOT = Path(__file__).resolve().parents[1]


def frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        raise ValueError("YAML frontmatter delimited by --- is missing")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("YAML frontmatter must be an object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opencode", choices=("v1", "v2"), default="v1",
                        help="Installed OpenCode agent schema; select based on opencode --version")
    args = parser.parse_args()
    failures = []
    warnings = []

    def fail(target, message):
        failures.append(f"{target}: {message}")

    def warn(target, message):
        warnings.append(f"{target}: {message}")

    paths = {
        "source": ROOT / ".apm/agents" / f"{AGENT}.agent.md",
        "copilot": ROOT / ".github/agents" / f"{AGENT}.agent.md",
        "opencode": ROOT / ".opencode/agents" / f"{AGENT}.md",
        "codex": ROOT / ".codex/agents" / f"{AGENT}.toml",
    }
    for target, path in paths.items():
        if not path.is_file():
            fail(target, f"missing file: {path.relative_to(ROOT)}")
    if failures:
        for item in failures:
            print("FAIL", item)
        return 1

    try:
        source = frontmatter(paths["source"])
        copilot = frontmatter(paths["copilot"])
        opencode = frontmatter(paths["opencode"])
        codex = tomllib.loads(paths["codex"].read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError, UnicodeError) as exc:
        print("FAIL cannot parse configuration:", exc)
        return 1

    # GitHub Copilot documents tools as a list of strings or a comma-separated string.
    ct = copilot.get("tools")
    if ct is not None and not (isinstance(ct, str) or
                               (isinstance(ct, list) and all(isinstance(x, str) for x in ct))):
        fail("copilot", "tools must be a string or array of strings (received mapping)")
    if not isinstance(copilot.get("description"), str):
        fail("copilot", "description must be a string")

    # OpenCode has version-dependent frontmatter permission contracts.
    ot = opencode.get("tools")
    if ot is not None:
        warn("opencode", "legacy tools mapping present; not proof of modern permission enforcement")
        if not isinstance(ot, dict) or not all(
            isinstance(k, str) and isinstance(v, bool) for k, v in ot.items()
        ):
            fail("opencode", "legacy tools must be a boolean mapping")

    if args.opencode == "v1":
        policy = opencode.get("permission")
        if not isinstance(policy, dict):
            fail("opencode", "v1 requires an explicit permission mapping for this restricted fixture")
        elif policy.get("edit") != "deny" or policy.get("bash") != "deny":
            fail("opencode", "v1 permission must deny edit and bash")
    else:
        policy = opencode.get("permissions")
        if not isinstance(policy, list):
            fail("opencode", "v2 requires permissions as a rule array for this restricted fixture")
        else:
            denied = {rule.get("action") for rule in policy
                      if isinstance(rule, dict) and rule.get("effect") == "deny"
                      and rule.get("resource") == "*"}
            if not {"edit", "shell"} <= denied:
                fail("opencode", "v2 permissions must deny edit and shell for resource '*'")

    if codex.get("name") != AGENT:
        fail("codex", "generated name mismatch")
    if not isinstance(codex.get("developer_instructions"), str):
        fail("codex", "developer_instructions missing or not a string")
    if "tools" in source and "tools" not in codex:
        fail("codex", "canonical tool restrictions were dropped (APM-reported loss)")
    if "tools" in codex:
        warn("codex", "tools key present; validity and enforcement unverified")

    for item in warnings:
        print("WARN", item)
    for item in failures:
        print("FAIL", item)
    if failures:
        print(f"Result: {len(failures)} incompatibility finding(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS focused checks ({len(warnings)} warning(s)); this does not prove runtime permissions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
