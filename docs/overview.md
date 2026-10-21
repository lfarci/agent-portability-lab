# Agent portability

## Where this came from

This project follows my article, [Beyond GitHub Copilot: Can You Reuse Your AI Setup?](https://github.com/lfarci/loganfarci.com/blob/main/content/articles/from-copilot-to-opencode-configuration-portability.md), published in October 2026.

The article looked at how much configuration can be reused when switching from GitHub Copilot to other coding-agent harnesses such as OpenCode, Codex and Claude Code.

Some pieces already have common conventions: `AGENTS.md` for instructions and `.agents/skills/` for skills. **Custom agents remain harder to share.** Each harness has different locations, metadata, tools, permissions and delegation behavior.

The idea at the end of the article was straightforward: could a shared agent definition be converted into the native configurations of several harnesses?

## The problem

I don't want to maintain four slightly different versions of the same agent in every repository, but sharing a prompt alone isn't enough.

For example:
- Copilot uses `.github/agents/*.agent.md`.
- OpenCode uses `.opencode/agents/*.md`.
- Codex uses `.codex/agents/*.toml`.
- Claude Code uses `.claude/agents/*.md`.

Moving content between directories might solve discovery without preserving the agent's actual behavior. Fields like allowed tools, model, permissions, and handoffs may require translation or may have no equivalent.

## Scope

**Main focus:** reusable custom-agent definitions across harnesses.

Initial harnesses: GitHub Copilot, OpenCode and Codex, because they are useful for local testing. Claude Code can be evaluated later or inspected statically if unavailable.

We want to understand:
1. Can one source generate the native agent files each harness expects?
2. Can each harness discover and run the generated agent?
3. What gets lost or changes during conversion, especially permissions, tools and delegation?
4. Can we update the source and regenerate without maintaining multiple copies?

Skills, general instructions, MCP servers and plugin management are related background, **not the primary goal**. Keep the experiment small, reproducible and separate from personal dotfiles.

## Possible approaches

- **Use an existing tool:** [Microsoft Agent Package Manager](apm.md) is the first candidate to try.
- **Contribute to an existing tool:** if there's a specific missing adapter or conversion.
- **Build a small validator or adapter:** if installation works but compatibility risks remain.
- **Build our own converter:** only if the important requirements cannot be met reasonably with existing options.

We haven't chosen a solution yet. APM's existence changes the question from *how do we build a converter?* to *does something already solve enough of the problem?*

## What we'll publish

Keep the input definitions, generated outputs, exact CLI versions and observed test results in this repository. Clearly distinguish **generated successfully** from **works in the target harness**.

After testing, write a follow-up article on [loganfarci.com](https://www.loganfarci.com) showing what worked, what didn't and whether it makes sense to use APM, contribute to it, or implement something ourselves. No conclusion in advance.
