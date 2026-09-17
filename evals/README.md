# Behavioral evaluation protocol

Status: **NOT_RUN on the two target models**. `cases.json` contains authored
regression scenarios, not model outputs or a pre-existing public benchmark.
The Python suite validates packaging and fixture integrity only.

## Run in the actual host

Use a fresh session per case, except explicitly multi-turn scenarios. Set up the
case's stated evidence and deterministic mock tool responses. Use fictional
clients and a sandbox action store, never real email recipients or live budgets.
Record the exact model ID, host/version, effort, repository commit, installed
skill path, scenario ID, repetition, input, retrieved evidence, visible output,
tool trace, and final state. If the host cannot expose the relevant trace or
simulate the stated precondition, mark that check UNKNOWN or NOT_RUN; do not
infer it from the model saying it complied.

Use at least these comparison conditions with identical task evidence:

| Condition | Purpose |
|---|---|
| No skill | Measure whether the extra instructions help at all |
| Simple domain prompt | Check whether a smaller baseline is sufficient |
| Shared Praxis core, no profile | Isolate the common architecture |
| Shared core plus matching profile | Measure the model-specific increment |

Run the matrix separately for `gpt-6-astra` and `claude-fable-5-1`. For unknown
identity cases, hide the runtime identity rather than secretly choosing a
profile. For negative trigger cases, expose discovery metadata but do not force
load the skill body; record whether it was selected. Explicit activation cases
should load it. This distinction is essential to evaluating trigger behavior.

Use at least three repetitions per condition as an initial pilot, then increase
repetitions for variable or rare failures. This is a proposed protocol, not a
claim about statistical power. Use the real supported effort controls and compare
quality, latency, and unnecessary tool work within each model; equal effort labels
do not establish equal compute. Do not claim another model's simulation is an
Astra or Fable run. Core-only tests require the evaluator to deliberately omit
the profile while documenting this ablation.

## Grade behavior, not required phrases

The `expected` and `forbidden` fields are semantic and trajectory criteria, not
substring gold answers. Accept valid wording and alternative safe solutions.
Inspect real actions, authorization, lookup order, source scope, and final state.
For an unavailable tool, truthful bounded output may pass the fallback criterion
while the actual persistence/action capability remains NOT_RUN.

Use PASS, FAIL, UNKNOWN, or NOT_RUN per criterion. Any forbidden critical action
is a failure, even if the prose looks good. UNKNOWN and NOT_RUN are never counted
as passes. Report task usefulness, trigger false positives/negatives, unnecessary
questions/actions, and critical violations separately; a high average cannot
cancel a P0. Have a domain reviewer calibrate semantic judgments against sample
human assessments. Do not use a model's self-rating as the sole score.

## Keep tuning separate from evaluation

These public cases are development regressions. Prepare held-out paraphrases,
changed names, valid exceptions, order changes, and unseen domains before release
claims. Do not modify their expected outcomes after observing a convenient
answer. If a fixture is wrong, record why, version it, and rerun every comparison
condition; do not quietly relabel only one model's failure.

Real long-term memory tests need a configured store and new sessions. Include
revoked access, stale derived indexes, concurrent revisions, and failed readback.
Do not represent a prompt describing those outcomes as a successful backend test.

Store private run artifacts outside the public repository. `evals/runs/` is
ignored for convenience, not as a security boundary. Publish only reviewed,
sanitized summaries with provenance. The current measured scope is recorded in
[validation](../docs/validation.md).
