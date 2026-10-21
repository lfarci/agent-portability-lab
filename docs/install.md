# Install the tools

This lab tests one APM custom agent across **GitHub Copilot CLI**, **OpenCode CLI**, and optionally **Codex CLI**. You can inspect APM output without installing all three harnesses.

Prefer running everything in the **same environment** (WSL/Linux *or* native Windows). An app installed on Windows is not automatically available inside WSL.

## Prerequisites

- Git
- A terminal (WSL/Linux is a good default; PowerShell also works)
- Node.js **22+** for the npm-based Copilot CLI installation
- A GitHub Copilot account with CLI access for Copilot tests
- A configured model provider for OpenCode tests
- .NET 8 SDK is **optional**: the intentionally buggy C# fixture can be reviewed without compiling it

Confirm basics:

```bash
git --version
node --version
npm --version
```

## 1. Install Microsoft APM

### WSL / Linux / macOS

Use the [official APM installer](https://microsoft.github.io/apm/getting-started/installation/):

```bash
curl -fsSL https://aka.ms/apm-unix -o /tmp/apm-install.sh
# Review /tmp/apm-install.sh before running it
sh /tmp/apm-install.sh
```

Open a fresh terminal if `apm` isn't found. The standalone installer normally uses `~/.local/bin`.

### Windows PowerShell

Via WinGet:

```powershell
winget install --id Microsoft.APM --exact --source winget
```

Alternatively, follow the official APM PowerShell installer instructions. Verify:

```text
apm --version
apm install --help
```

## 2. Install GitHub Copilot CLI

Cross-platform (Node.js 22+):

```bash
npm install -g @github/copilot
copilot --version
```

Windows alternative: `winget install GitHub.Copilot`.

Then, from this repository, launch `copilot` and use `/login` to authenticate. Organizational Copilot subscriptions may require an administrator to enable CLI access.

Official guide: [GitHub Copilot CLI quickstart](https://docs.github.com/en/copilot/get-started/cli-quickstart).

## 3. Install OpenCode CLI

Cross-platform npm installation:

```bash
npm install -g opencode-ai
opencode --version
```

Linux/WSL alternative: use the installer documented at [OpenCode](https://docs.opencode.ai/docs/). You can configure a model provider through the interactive `opencode` interface; your desktop app installation does not by itself guarantee the CLI is on `PATH`.

## 4. (Optional) Install Codex CLI

```bash
npm install -g @openai/codex
codex --version
```

Start `codex` once to configure authentication. If Codex is unavailable, **still generate and inspect its TOML output**, but label runtime validation *Not tested*.

Official reference: [Codex CLI repository](https://github.com/openai/codex).

## 5. Run Experiment 01

Clone the lab (or use your existing checkout):

```bash
git clone https://github.com/lfarci/agent-portability-lab.git
cd agent-portability-lab
```

If Experiment 01 is not yet merged, check out `experiment/01-basic-agent-portability` after fetching it.

Record versions before running APM:

```bash
apm --version
copilot --version
opencode --version
codex --version  # optional
```

Missing optional tools should be recorded as *Not tested*. Run APM **locally** in the lab directory, not with `--global`:

```bash
apm install --dry-run --target copilot,codex,opencode
apm install --target copilot,codex,opencode
```

Check `apm install --help` if your installed APM release differs.

Then follow [Experiment 01](experiments/01-basic-portability.md) to inspect generated files, invoke the reviewer and complete the [results template](results/01-basic-portability.md).

## Notes

- The CLIs may consume **AI credits or API usage**. Don't run repeated tests automatically before assessing cost.
- APM file generation and actual agent invocation are **separate checks**.
- Keep these trials inside this throwaway repo, not personal dotfiles or production code.
- No APM or harness execution was performed while creating these instructions.
