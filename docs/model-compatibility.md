# Model compatibility and research record

Reviewed 2026-09-18. Targets: GPT-6 Astra and Claude Fable 5.1.

This release is **research-informed, not paired-model benchmark-validated**.
Vendor-described tendencies motivate compact adaptations; they are not universal
traits or measurements of this repository. The operator selects the actual model.
A skill profile cannot change the model, grant tools, or set API parameters.

## What changed

| Concern | Implementation decision | Evidence boundary |
|---|---|---|
| Instruction conflicts and unnecessary blocking | One shared authority contract; Astra profile qualifies defaults and makes blockers specific | Adaptation of OpenAI's Astra guidance, not permission to override host constraints |
| Stopping before requested work is complete | Explicit authorized completion and truthful blocked status | Adaptation of Fable's completion guidance, not unlimited autonomy |
| Excess process or edits | Lightweight tasks, targeted changes, no unrelated features or test expansion | Design constraint; requested work still has to be completed and verified |
| Sparse progress and dense prose | Visible milestone updates and readable user-requested output | Prompt-level behavior; transport/display settings belong to the host |
| Search and tool scheduling | Exact-name verification for material current facts; parallel independent reads, ordered dependent writes | Real tools only; low-effort runs need separate evaluation |
| Model switching and context loss | One trusted-identity profile, factual handoff, latest-request precedence | No claim that provider reasoning blocks transfer between models |

The executable wording lives in the
[Astra profile](../.agents/skills/praxis/references/models/astra-6.md) and
[Fable profile](../.agents/skills/praxis/references/models/fable-5.1.md).
Do not load both profiles or the research document for every task. The common
core remains the source of authority, memory, and action rules; profiles only
supply behavioral adjustments. An unknown model uses the common baseline.

## Host/operator settings, not skill instructions

| Setting | Verified source information | Praxis integration decision |
|---|---|---|
| Astra identity and effort | OpenAI lists `gpt-6-astra` and `low`, `medium`, `high`, `xhigh`, `max` | Select a supported host setting; compare workloads rather than hardcoding maximum effort |
| Fable identity and effort | Anthropic lists `claude-fable-5-1`, always-on adaptive thinking, and default `high` | Start from a documented host setting; evaluate cheaper/faster settings on the same cases |
| Fable conversation history | The model overview identifies incompatibilities involving forced tool use, earlier models reading its thinking blocks, and edits to prior turns | Use the provider's supported continuation/migration mechanisms; never fabricate or edit signed reasoning to make history portable |
| Progress display | The Fable overview lists a beta for readable between-tool updates | Check the actual client/API version; adding prose to SKILL.md does not configure this feature |
| Compaction | Anthropic documents explicit summary instructions and preserved task state | Keep a factual handoff; use native compaction where supported, not a promise of limitless memory |
| Skills installation | Official Codex and Claude Code documentation describe different discovery paths | Distribute one self-contained directory and install it in the appropriate host location |

These are dated documentation checks, not assertions that every subscription,
app, deployment, or client exposes every feature. Do not set invented frontmatter
fields such as a universal model, effort, or memory backend. If the client already
manages model history and compaction, do not replace it with a second harness.

## Sources and claim provenance

The following are primary sources. No community anecdote is presented as a
measured target-model characteristic. The links are portable repository citations;
chat-only citation tokens are intentionally absent.

| Source | Use in this release |
|---|---|
| [OpenAI: latest-model guide](https://developers.openai.com/api/docs/guides/latest-model) | Astra-specific instruction sensitivity, clarification, and behavior guidance; older-model sections are not automatically extrapolated |
| [OpenAI: GPT-6 Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra) | Actual model identifier and supported effort values |
| [Anthropic: prompting Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) | Fable profile motivations: completion, scope, progress, formatting, search, and edits |
| [Anthropic: Fable 5.1 overview](https://platform.claude.com/docs/en/models/fable-5-1/overview) | Identity, adaptive thinking, default effort, and integration incompatibilities |
| [Anthropic: parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) | Distinguishing independent calls from dependency chains |
| [Anthropic: compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) | Explicit factual task-state preservation |
| [Agent Skills specification](https://agentskills.io/specification) | Portable SKILL.md metadata and progressive disclosure |
| [OpenAI: Codex skills](https://developers.openai.com/codex/skills) | Project skill discovery and invocation |
| [Anthropic: Claude Code skills](https://code.claude.com/docs/en/skills) | Project/personal installation, support files, and invocation |

The domain packs, authority model, learning lifecycle, scenario expectations,
and choice of architecture are Praxis design proposals. They are not vendor
endorsements or official sales/project-management rules. Original conceptual
material remains available in repository history; this revision does not rely
on unverified Impeccable rule counts or an inaccessible blog as current evidence.

## Validation and maintenance

Run the [behavioral protocol](../evals/README.md) against the exact deployed
model and host version. Log real model identity, effort, skill commit, tool
availability, context, outputs, traces, and final state. Evaluate shared-core
and profile versions separately to detect both benefit and prompt overhead.
A simulation with another model is not a run of the named target.

Review this document when the target model, host discovery rules, tool transport,
or memory backend changes. Update the profile only for supported, relevant
behavior and rerun the affected cases. Keep accepted examples and independently
prepared holdouts separate. Do not retune expected answers merely to make the
latest output pass. See [validation status](validation.md) before making claims.
