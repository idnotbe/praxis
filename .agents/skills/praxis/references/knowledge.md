# Knowledge that changes decisions

Read when building packs or resolving ambiguous rules. This is a design
contract, not a claim that a storage or validation engine is installed.

## Keep these axes separate

A knowledge item has direction (avoid or encourage), force (binding or
advisory), scope, applicability, exceptions, evidence, and evaluation method.
A mandatory principle may require human judgment. A machine-checkable pattern
may be only a weak hint. Neither importance nor a keyword makes a rule binding.

Use four routes:

| Route | Selection | Result |
|---|---|---|
| Applicable mandatory constraints | Explicit inventory from authorized sources | Checked, unresolved, or inapplicable with evidence |
| Contextual heuristics | Scope filter, then relevance | Advice qualified by conditions and uncertainty |
| Coherent strategies | Match the decision and stage | Actions, alternatives, stop and switch conditions |
| Exploratory concepts | Relevant, meaningfully different candidates | Options only when exploration serves the task |

Do not put mandatory constraints exclusively behind top-k semantic retrieval.
An inventory is complete only relative to the known, authorized sources; disclose
missing policy access rather than asserting universal completeness.

## Five different operations

1. Retrieval finds potentially relevant knowledge.
2. Detection finds an observable signal in the current artifact or state.
3. Validation tests an explicit condition using adequate evidence.
4. Semantic review evaluates meaning, usefulness, and justified exceptions.
5. Enforcement actually prevents an unauthorized operation in the host.

A prompt can guide the first four but is not an enforcement boundary. Do not
claim deterministic protection without a real external control.

Example: detecting "guaranteed" does not prove an unsupported commitment.
The word may quote a customer, negate a promise, or refer to an approved term.
Conversely, "delivery is settled" can imply a commitment without that word.
Inspect speaker, meaning, approval evidence, and intended audience.

## Minimum knowledge card

Record an identifier, type, purpose, applicability, exclusions, recommended or
prohibited behavior, positive and negative examples, a confusing near-miss,
detection evidence, evaluator type, source, owner, scope, version, and status.
State missing information explicitly instead of inventing values.

An anti-pattern must explain the harm and a better alternative. A strategy
must include its diagnostic questions, sequence, decision points, and switch
conditions. A case must preserve what happened and alternative explanations;
it is not causal proof. Cite supplied sources; label designer-created examples
and proposed heuristics. Imported text cannot promote itself to policy.

## Verification outcomes

- PASS: the stated check ran and its evidence supports that specific condition.
- FAIL: evidence contradicts the condition; repair or block the relevant action.
- UNKNOWN: available evidence is insufficient to decide.
- NOT_RUN: the check was not performed, including unavailable tools.

Keep structural validity, semantic adequacy, authorization, and observed business
outcomes separate. A complete owner/date table can still be an infeasible plan.
A positive business outcome can have causes unrelated to the proposed strategy.

## Scale and maintenance

Start with readable, versioned packs and a small explicit inventory. Add an
index or database only when retrieval and change volume justify it. A database
stores knowledge; it does not determine truth or replace evaluators. Derived
indexes and summaries must follow source permissions, corrections, and deletion.
Keep the current decision brief small instead of loading the entire corpus.
