# Validation record

Release 0.2.0 | 2026-09-18

## Executed checks

Command: `python -m unittest discover -s tests -v`

Result: **12 tests passed, 0 failures** in the task-local staging directory.
No target-model endpoint was called by these tests.

| Check | What was actually established |
|---|---|
| Metadata and size | Required skill fields, version, and bounded core/profile length |
| Current source text | ASCII portability, no Korean filename suffixes, no chat-only citations; authoring was also manually reviewed in English |
| Local references | Repository links resolve; packaged skill links stay inside the portable skill directory |
| Negative checker cases | Missing links and package-escape links are rejected |
| License | Original MIT license blob preserved exactly and bundled with the skill |
| Copy layout | Copies under both host directory layouts retain their support files; an existing destination is not overwritten by the test |
| Scenario integrity | 32 unique cases, valid schema, explicit outcomes and critical-risk/category coverage |

ASCII is not an English-language detector. Local link validation does not prove
external websites are reachable. Copy-layout tests do not run Codex, Claude Code,
or the PowerShell installation command. The scenario checker does not run the
prompts, evaluate answers, or enforce tool permissions.

## Design review

The review checked that advisory examples cannot create binding company policy,
that current requests can override skill defaults without bypassing real authority,
and that completion nudges do not authorize unrequested sends or changes.
It also checked that both model profiles are not indiscriminately loaded and
that a simulated profile cannot be reported as a real target-model run.

Fixture review preserved valid exceptions and negative trigger cases, separated
UNKNOWN from NOT_RUN, and required actual trace evidence for privacy, parallelism,
write success, and duplicate prevention. Expectations are semantic; no required
phrase or self-reported compliance is treated as a behavioral pass.

The Korean architecture was replaced by a consolidated English revision. Its
acceptance goals, four alternatives, twelve walkthroughs, three earlier review
rounds, controlled-learning boundaries, and five naming options were retained.
The original remains in Git history; no historical rewrite is required.

## Not executed

| Gate | Status | Missing evidence |
|---|---|---|
| Actual GPT-6 Astra behavior | NOT_RUN | Target-model outputs, traces, repeated baseline comparisons |
| Actual Claude Fable 5.1 behavior | NOT_RUN | Target-model outputs, traces, repeated baseline comparisons |
| Live skill discovery and installation | NOT_RUN | Codex/Claude Code execution in the user's environment |
| Persistent learning, isolation, deletion | NOT_RUN | Configured store and state/trace verification across sessions |
| Real external-action controls | NOT_RUN | Authorized sandbox integration and resulting-state checks |
| Efficiency or business improvement | NOT_RUN | Measured quality, latency, cost, and outcome comparisons |

No dual-model execution harness or credentials were available in this task.
The release is an installable instruction package with research-informed
adaptations, not proof of higher success rates or production-grade enforcement.
Follow the [evaluation protocol](../evals/README.md) before making such claims.
