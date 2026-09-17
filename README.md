# Praxis

An adaptive domain skill for **GPT-6 Astra** and **Claude Fable 5.1**.
Praxis connects principles, contrasting examples, contextual strategies,
verification, and deliberately scoped experience.

**Release 0.2.0:** an installable, instruction-first skill with model-specific
profiles and two illustrative domain packs. It is not an implemented memory
server, autonomous policy engine, or benchmark-proven performance improvement.
See [validation status](docs/validation.md) for exactly what was checked.

## Use it

The canonical package is [.agents/skills/praxis](.agents/skills/praxis/SKILL.md).
Copy the whole directory, including its license and references, not just SKILL.md.
No Python, Node.js, SQLite, MCP server, or paid API integration is required to
read the skill. The host must support skills and access the packaged files.
Actual retrieval, persistence, validation, and actions use the host's real tools.

### Codex and GPT-6 Astra

In this repository, the package already occupies the documented project-skill
location. Open the repository in Codex, select GPT-6 Astra using the host's model
controls, and invoke `$praxis` or select Praxis in the skill picker.
For another project, copy the directory to that project's `.agents/skills/praxis`.

Example: `$praxis Draft a response to this buyer's price objection. Do not send it.`

### Claude Code and Claude Fable 5.1

Copy the package to `.claude/skills/praxis` in the target project, or to
`~/.claude/skills/praxis` for personal use. Select Fable 5.1 through the host's
model controls and invoke `/praxis`.

From this repository root, a first-time personal installation in PowerShell is:

```powershell
$source = (Resolve-Path '.agents/skills/praxis').Path
$parent = Join-Path $HOME '.claude/skills'
$target = Join-Path $parent 'praxis'
if (Test-Path -LiteralPath $target) { throw 'Praxis already exists. Review and back up that installation before replacing it.' }
New-Item -ItemType Directory -Path $parent -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Recurse
```

Check the host's skill picker after installation; start a new session if needed.
For updates, preserve local customizations, compare versions, then replace the
reviewed copy. Do not keep editing two canonical copies. The ignored project
copy under `.claude/skills/praxis` is a local installation, not the source.

Example: `/praxis Prepare recovery options for this delayed project. Keep the approved baseline unchanged.`

Installation paths and discovery behavior are documented by
[OpenAI](https://developers.openai.com/codex/skills) and
[Anthropic](https://code.claude.com/docs/en/skills). Local CLI installation does
not automatically install a skill into a web chat or cloud account. In a chat
host, use its supported skill-upload mechanism where available; merely pasting
SKILL.md is not equivalent to installing references, tools, or persistent memory.

## What it does

| Mode | Deliverable |
|---|---|
| Build | A reusable domain pack grounded in supplied knowledge |
| Use | Contextual advice, a draft, a review, or a specifically authorized action |
| Learn | A scoped correction or a confirmed, authorized memory update |

Only the matching model profile is loaded. Unknown models use the shared core;
loading a profile never selects a model or changes API settings. The bundled
sales and project-management packs are explicit starting examples, not company
policy or independently validated domain expertise.

Read the [architecture](docs/architecture.md),
[model research and host boundaries](docs/model-compatibility.md), and
[behavioral evaluation protocol](evals/README.md).

## Contribute and verify

All tracked text, examples, comments, and new commit/PR messages are in English.
Answers produced by the skill still follow the end user's requested language.
Keep private user/client memory outside the package and public repository.
Historical commits are preserved; the English-only rule applies to the current
source tree and new contributions, not a destructive history rewrite.

Run the dependency-free package checks with Python 3.10 or newer:

```sh
python -m unittest discover -s tests -v
```

These check packaging and evaluation fixtures, not live model behavior. The
behavioral cases require actual target-model runs with trace inspection.
Do not report an unrun model test as passing or treat structural checks as ROI.
Keep changes scoped, inspect the diff, and use a reviewed PR. Before cleanup,
confirm the merge and compare the expected tree. Remove only task-owned temporary
files and verified merged branches; never discard unrelated dirty work or
force-push public history as routine cleanup.

License: [MIT](LICENSE).
