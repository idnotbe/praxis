# Adversarial review and execution record

Date: September 18, 2026. Skill held fixed at
`d722b35154b86c0123d2a1b07311b84a626a5fd2`. Evaluation candidate versions advanced
from 2.0.0 through 2.0.1 and 2.0.2 to **2.1.0**. All review was by the same
assistant, not an independent human or separately instantiated reviewer.

## Initial dataset review

The prior 32 cases described desired behavior but did not supply enough concrete
state for several actions. Missing translation language, missing approved dates,
unspecified files and memory versions, and claimed parallel capability made
model failures indistinguishable from fixture defects. Corrected cases preserve
the original intent and IDs. The suite expanded to 96 balanced cases before the
pilot. Private state and answer criteria were separated from public inputs.

## Executed review/fix cycles

| Cycle | Reproduced defect | Severity | Correction and evidence |
|---|---|---|---|
| 1 | Reference reader exposed the skill body before observed discovery | P0 | Gate reference access until `load_skill`; regression verifies the bypass is blocked |
| 1 | Approval files were writable despite narrower task authority | P0 | Explicit virtual write allowlist, independent of model text |
| 1 | Valid JSON number 5.0 failed an expected numeric 5 | P1 | Typed recursive JSON comparison; reject booleans and nonstandard NaN |
| 1 | Modified outputs or forged input receipts could reuse old review | P1 | Recompute input and output hashes before grading |
| 1 | Invalid evidence could still set the external-record eligibility flag | P1 | Require valid, complete semantic judgments as well as external metadata |
| 1 | Routing violations could hide behind a negative trigger result | P0 | Universal attempted-violation checks, including incomplete runs |
| 2 | Public challenge split omitted knowledge and safety categories | P1 | Curated family groups with every category represented in both splits |
| 2 | Progress was required but no observable progress channel existed | P1 | Add a virtual progress event plus a no-updates negative control |
| 2 | The two scope-change counterfactuals had unrelated split families | P1 | Group them before assigning splits |
| 2 | Changing the tool trace did not invalidate semantic judgments | P1 | Bind judgments to the full output/state/trace observation hash |
| 2 | No completed runs had no explicit undefined accuracy/trigger result | P1 | Report completion, status counts and nullable completed-run/trigger metrics |
| 3 | Absent-skill control could be mistaken for a comparable trigger trial | P1 | Mark its routing trials NOT_APPLICABLE rather than false negatives |
| 3 | A status call before a send could satisfy verification | P1 | Require delivery status after the new send; preserve timeout-before-retry control |

Executable regressions actually produced the following sequence:

| Candidate checkpoint | Tests run | Failures | Errors |
|---|---:|---:|---:|
| First adversarial tests | 43 | 7 | 0 |
| First corrections | 43 | 0 | 0 |
| Second adversarial tests | 49 | 5 | 1 |
| Second corrections | 49 | 0 | 0 |
| Third adversarial tests | 51 | 2 | 0 |
| Final corrections | 51 | 0 | 0 |

Test count includes the 12 pre-existing package checks. Two progress regressions
exercise the same underlying defect. These are evaluator tests, not 51 LLM runs.
The final audit also checked source/gold separation, family leakage, permitted
and prohibited actions, invocation self-reporting, path escape, reference limits,
failed storage, partial deletion, write conflicts, malformed backends, semantic
unknowns, baseline evidence equality and profile separation.

Two wording corrections removed a contradictory day-zero dependency description
and clarified that H09 describes a hypothetical model switch, rather than
pretending the simulator can change a real runtime. Neither changed the skill.

## Actual diagnostic pilot

The current conversation assistant generated 16 early responses, then another
16 after corrections, choosing actions that Python executed against the virtual
files, scoped records, approval state and memory store. The two groups overlap
on eight cases, giving **24 distinct cases and 32 recorded case responses**.
They are not 32 independent API calls. The later group covers all seven categories.
It includes four mock-discovery queries, approved and blocked sends, minimal edits,
a concurrent write conflict, numeric answers and semantic quotation controls.

The later run's public inputs are unchanged by the final grader-only fixes.
They were explicitly re-scored, retaining the original execution revision hash;
this is **not** another model run. All structured checks passed. Same-author
review judged the 16 later responses to meet their authored semantic criteria.
This result is diagnostic, not a success-rate estimate or an improvement claim.
Actual output texts and state/action receipts are in
[the diagnostic report](results/diagnostic.json).

The author saw the gold labels and the earlier conversation supplied the full
skill. Therefore even the mock routing examples are contaminated: they test the
instrumented boundary and a model decision, not spontaneous native discovery.
No clean baseline, independent reviewer, fresh session, verified model API
identity, or Fable execution was available. Code tests and current-session
answers cannot substitute for those missing experiments.

## Final review decision and remaining gates

No known P0/P1 **dataset or tested mock-harness** finding remains open after the
recorded fixes and final regression run. This bounded statement does not certify
absence of undiscovered bugs or production risk. The evaluation framework can be
merged; target-model effectiveness remains unqualified.

Before a production conclusion, run both target models with audited isolated
backends and matched controls; inspect provider model identifiers; calibrate a
blinded grader against independent domain review; add unseen family-level tests;
and run real-host discovery, progress, compaction, memory and action integration.
The generic stdio backend is a trust boundary, not a security sandbox. Native
host behaviors and real enforcement remain NOT_RUN, not silently passed.

## Repository and cleanup scope

Only evaluation data, harness, tests, provenance and reporting are changed. The
skill and domain packs are deliberately unchanged so failures cannot be hidden
by tuning the treatment to the same test set. All new tracked text is English.
Keep generated/raw runs outside tracked source unless deliberately sanitized.

Publication uses a reviewed branch, a parent pinned to current main, a verified
Git tree and an expected-head merge. Remove only task-owned temporary files after
preserving the audit archive. Check merged PR state and unchanged branch head
before deleting a remote branch. If the connected tool cannot delete refs,
retain the branch and report that limitation rather than claiming cleanup or
attempting a force-push workaround. Never alter unrelated user worktrees.
