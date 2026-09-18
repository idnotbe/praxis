# Evaluation revision 2.2: integrity review and execution evidence

Date: September 18, 2026. Base repository commit:
`f6957ee3baa31e40eb5bf9133db54321dcb67c72`.
Skill version 0.2.0 and its domain packs are unchanged. This revision repairs the
existing evaluation suite; it does not train the skill on its own answer key.

## Scope, acceptance, and reuse

The inherited 96 cases already cover routing (24; 12 positive and 12 negative),
workflow, knowledge, memory, safety, domain usefulness, and host/model boundaries
(12 each). Keep those counts and IDs rather than inflate coverage with superficial
variants. Preserve the family-locked public challenge split. Public challenge is
not a secret holdout, and equal category counts do not imply production frequency.

Before edits, the review criterion was: public inputs must not contain evaluator
answers; tasks must be answerable; required behavior must be observable; normal
controls must pass while invalid counterparts fail; attempted violations, errors,
unreviewed results and missing execution must remain distinguishable. A changed
oracle needs a reason independent of whether the skill passed. Preserve prior
records and rerun only affected checks, then freeze and fully verify.

Reuse remains first: the original 32 Praxis scenarios, the existing 64 additions,
and their provenance and licenses are retained. No claim is made that these are
96 independently imported benchmark tasks. `SOURCES.md` documents the distinction
between concrete task adaptation and methodological inspiration.

Additional primary-source checks before editing:

- [OpenAI's skill-evaluation guide](https://developers.openai.com/blog/eval-skills): distinguish invocation, process, outcome and efficiency; capture traces and artifacts.
- [Anthropic's agent-evaluation guide](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): distinguish grader evidence, outcomes and trials; inspect failures rather than rely on a single success score.
- [SkillsBench 1.1](https://www.skillsbench.ai/blogs/skillsbench-1-1): paired skill/no-skill evaluation and separated agent-visible material and verification are relevant; its entire environment is not transplanted into this advisory simulator.
- [tau2 retail tasks](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/retail/tasks.json): re-read original IDs 0 and 1, blob `e95a9f898b2d1f6568ea8faec78edc3767ce747d`. Both ask for a keyboard AND thermostat replacement. That precondition had been lost in the local adaptation.

## Reproduced defects and corrections

| Finding | Severity | Correction |
|---|---|---|
| Routing contexts explicitly explained whether the skill should trigger | P0 | Remove classification commentary from all 24 public contexts; retain actual hiring notes where needed |
| Quotation/negation and benign-document contexts supplied the intended classification | P0 | Keep source content and remove evaluator explanations |
| Save failure, search absence and a future concurrent update were announced before tool execution | P1 | Keep outcomes in private fixture state; reveal them through actual simulated tool results |
| Doing nothing could satisfy the failed-save state check | P1 | Require a write attempt and subsequent readback; a read before the failed write is insufficient |
| Deletion passed without verifying the resulting state | P1 | Require readback after deletion and deactivation of derivatives |
| Notification could occur before the saved file was reread | P1 | Require successful write, matching readback, then notification in that order |
| Any status call could count as delivery verification | P1 | Require delivered=true for the same message ID after the send |
| Exact-case substring matching rejected valid quoted/lowercase searches | P1 | Normalize search syntax while preserving entity and version identity; retain wrong-version negative control |
| Retail gold required an unrequested thermostat | P1 | Restore both replacement needs from the inspected upstream tasks; preserve accepted/rejected fallback counterfactual |
| A merely permitted progress update was compulsory in gold | P1 | Explicitly request one progress update; retain the no-updates control |
| Memo gold required an unrequested title | P1 | Make the title optional rather than penalize a valid two-paragraph memo |
| Unknown-identity cases were preloaded with named-model profiles | P1 | Hide runtime profile identity for those cases in both initial context and reference access |
| Model changes or incomplete identity evidence could qualify a trial | P1 | Validate stable string identities per response; require complete identity observations for eligibility |
| Caller could replace a case's gold without changing the recorded suite | P1 | Verify the entire case against the canonical current suite before grading |
| Duplicate keys, numeric overflow and boolean/numeric equality admitted invalid data | P1 | Strict JSON parsing and typed recursive comparisons |
| Permission errors could abort a batch; existing output was checked only after execution | P1 | Record backend OS errors; reject an existing destination before execution and write exclusively |
| Missing/unreviewed trials appeared as zero accuracy | P1 | Keep aggregate fractions undefined until their denominator is adjudicated; publish coverage separately |
| Different treatments, models or diagnostic transports could be pooled | P1 | Carry provenance into grades and reject mixed groups in summary |

P0 here means evaluation contamination or concealed critical violations, not an
assertion that a real customer's data leaked. P1 means a defect capable of changing
a material evaluation conclusion. Keyword matching is still not a semantic judge.

## Actual correction cycles

These are Python evaluator tests, not model calls. Failures are unittest failure
records, including subtests, rather than counts of unique root causes.

| Checkpoint | Test methods | Failures | Errors |
|---|---:|---:|---:|
| Unchanged baseline | 51 | 0 | 0 |
| Round 1: new adversarial tests before fixes | 21 | 40 | 2 |
| Round 1: affected evaluation tests after fixes | 60 | 0 | 0 |
| Round 2: expanded adversarial tests before fixes | 33 | 5 | 0 |
| Round 2: affected evaluation tests after fixes | 72 | 0 | 0 |
| Round 3: provenance aggregation tests before fixes | 38 | 3 | 1 |
| Round 3: affected evaluation tests after fixes | 77 | 0 | 0 |
| Recorded-replay integrity checks | 41 | 0 | 0 |

The 40 first-round failures include one subtest for each routing context. The full
suite now contains 92 methods: the original 51 and 41 new integrity checks.
A read-only CI workflow was prepared, but its upload was blocked by the tool
security gate. It was not published or rerouted through another mechanism.
Final local verification runs 91 methods and explicitly skips the one full-repo
local-link test because unchanged historical documentation is not fully mounted.
All executable test/skill/evaluation inputs are pinned to their verified Git
blobs. References in the available Markdown are checked separately against the
verified remote tree; this is not a claim of a complete local checkout or CI run.

Review was performed by the same assistant, not by an independent reviewer or a
separately instantiated model. No known P0/P1 finding in the inspected dataset and
tested simulator paths remains unresolved after these corrections. This is a
bounded review statement, not certification of absence of undiscovered defects.

## What actually ran, and what did not

The current assistant authored 28 diagnostic answers and action sequences after
seeing the skill and gold. Python executed their actions against virtual files,
scoped retrieval, approval state, and memory. There are four responses in each of
the seven categories. All their structural/observable checks passed. Their
semantic grades remain UNKNOWN: no independent semantic judgments were created.
`benchmark_eligible` is zero. No accuracy-improvement estimate is reported.

The responses and receipt hashes are in `results/replay-2.2.json`. Run:

```sh
python evals/replay.py --out evals/runs/replay-2.2.json
```

This replays recorded decisions; it does NOT call a model or constitute another
LLM trial. The runner reconstructs mock-tool observations and verifies the stored
input and observation hashes. It refuses changed inputs, outputs or observations.
The original `results/diagnostic.json` is left untouched as historical 2.1 evidence.
Do not reuse its scores against 2.2 inputs or describe a rescore as a fresh run.

Independent Astra 6 and Fable 5.1 runs remain NOT_RUN. The environment had no
Codex/Claude executable, no configured OpenAI/Anthropic API key, and no installed
isolated-inference connector. Container network access also failed. The GitHub
connector was available for repository operations, not for model inference.
Backend-free preflight executed for all 96 cases under each target profile and
returned NOT_RUN, not failed model answers. These 192 placeholders are not LLM
calls. No paid provider access, account changes, or unsupported identity claims
were introduced.

## Remaining empirical gates

Use the audited stdio backend contract in README for isolated model trials. Hold
model, sampling/effort, tools, budgets and evidence constant across no_skill,
simple, core and profile conditions. Preserve raw request/response and provider
identity evidence. Natural triggering is a separate metadata-only experiment;
forced loading cannot answer that question. The unknown-identity fixtures hide
the profile from the agent without pretending to change the backend model.

A blinded, calibrated semantic reviewer and independent domain review are still
needed. Test generated child packs on new downstream tasks in fresh contexts,
not only inspect their structure. Native discovery, actual progressive loading,
long-context compaction, multilingual transfer, real memory across sessions,
permission enforcement and model-switch integration remain unexecuted host gates.
Current scenarios exercise their bounded decision contracts, not those full
systems. Do not advertise these absent experiments as covered by a unit-test pass.

Use new, unseen families for generalization claims. Analyze paired differences
and family-level uncertainty; do not treat paraphrases as independent samples.
Report usefulness, over-refusal and action failures alongside cost and latency.
Never pool contaminated diagnostic replay with independently executed trials.

## Scope and cleanup

The skill, packs, frozen seed cases, existing source attribution and licenses are
unchanged. New authoring is English. No CI workflow, provider key, account
change, branch-deletion automation, or paid model access is introduced. The
blocked CI attempt remains a verification limitation, not a successful check.

Publish on one task branch, verify expected head and merge tree, then remove only
task-owned temporary material after preserving evidence. If remote-ref deletion
is unavailable, report the remaining merged branch instead of force-pushing or
inventing cleanup. User-machine worktrees and unrelated dirty files are outside
this execution environment and must remain untouched.
