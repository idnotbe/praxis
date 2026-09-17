# Project management pack

Version: 0.1.0. Status: illustrative, review-required. Owner: deployment operator.
These are Praxis-designed examples and proposed heuristics, not an approved
project methodology or a substitute for the project's actual governance.

## Scope and decision model

Support kickoff decisions, change requests, and schedule-recovery proposals.
Produce a decision-ready plan, impact assessment, or stakeholder update.
Do not make resource assignments, baseline changes, or customer commitments
unless the request and actual permissions authorize those actions.

Identify the approved baseline, present forecast, dependencies, acceptance
criteria, available capacity, scope boundaries, risks, decision owners, and
source dates. Separate work time from waiting and approval time. Distinguish
facts, estimates, and options; do not report a proposed date as an approved one.

## Mandatory constraints

Use the project's actual change-control, disclosure, approval, and access rules.
No approval threshold, staffing entitlement, or contractual tolerance is supplied
by this pack. Missing policy access is UNKNOWN, not permission to rebaseline.
A recovery draft can proceed with assumptions while an external change remains
blocked on specific missing authority or evidence.

## P-01: Explain the delay mechanism

Applicability: delivery is behind baseline.
Strategy: identify the blocked or extended dependency, remaining work, waiting,
capacity, and downstream effects. Compare recovery options through their actual
tradeoffs: reduce scope, change sequence, add suitable capacity, or revise the
date. Do not assume extra people shorten an indivisible task.

Bad: "Increase parallelism and return to the original deadline."
Better: "The approval dependency accounts for the forecast slip. Parallelizing
independent preparation may help, but it does not remove the approval wait."
Near-miss: two tasks on different systems can still depend on the same reviewer.

Detection: inspect task links, stated durations, and dated status evidence.
Judgment: test feasibility and the delay mechanism. If no scheduling tool or
calendar is available, label any arithmetic and date assumptions explicitly.

## P-02: Turn a change request into a decision

Applicability: a stakeholder asks for additional scope or a new deadline.
Strategy: describe the requested delta, expected benefit, affected deliverables,
cost/capacity and dependency impacts, alternatives, and the accountable decision.
Separate options from approvals. Switch to clarification when the requested
change cannot be distinguished from the existing acceptance criteria.

Bad: "The change is minor, so the team will absorb it."
Better: "The additional report changes the acceptance scope. Assess capacity and
obtain the designated owner's decision before changing the baseline."
Near-miss: a correction already required by accepted scope is not automatically
a new commercial change; check the actual agreement.

## P-03: Make kickoff assumptions reviewable

Align the objective, in/out scope, acceptance evidence, owner responsibilities,
dependencies, and immediate decisions. Do not turn the kickoff into an exhaustive
framework presentation. Unresolved facts should have an owner or a bounded
assumption, not a fabricated answer.

## Completion and learning

The result must make a concrete decision possible and distinguish baseline,
forecast, and option. Owner/date completeness is a structural check, not proof
of feasible recovery. If an approved message changes materially before sending,
recheck authorization. After a timeout, inspect state before repeating updates.
Capture learning only in the authorized project scope; a successful recovery
is an observation, not proof that the same tactic works on every project.
