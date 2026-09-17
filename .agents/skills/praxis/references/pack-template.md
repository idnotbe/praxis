# Domain pack authoring contract

Use this template for Build tasks; do not force it onto ordinary advice.
Populate only what supplied evidence supports. Mark gaps and proposed heuristics.
Keep the pack portable and do not modify the shared core for a domain preference.

## Identity and operating scope

State the pack name, version, owner, status, supported decisions, excluded tasks,
expected deliverables, activation examples, and near-miss non-activation examples.
List the domain sources and their dates, applicability, and limitations.
Identify actual tools, validators, and memory integrations separately from
planned capabilities. A tool name in a document does not install it.

## Decision model

Describe the entities, states, relationships, and uncertainties that change a
recommendation. Explain what questions matter and why. Distinguish information
needed to draft from information required before acting. Avoid a persona-only
instruction such as "be an expert" without decision criteria.

## Mandatory-constraint inventory

For every claimed binding rule, record its source, authority, scope, condition,
valid exceptions, and verification method. Do not populate invented company
thresholds. Mark unavailable evidence UNKNOWN. When no policy source has been
provided, say so; use illustrative advice without pretending it is mandatory.

## Principles and anti-patterns

For each item, supply a stable ID, rationale, applicability, exclusions,
recommended alternative, good example, bad example, confusing near-miss, and
how to check it. Distinguish detection from judgment and enforcement. Include
both avoiding failure and achieving a useful positive outcome.

## Coherent strategies

Connect a situation to a diagnosis, actions, dependencies, decision owners,
stop/switch conditions, and evidence of progress. Make alternatives substantively
different. Do not combine unrelated tips into a strategy merely for variety.

## Cases and learning

Preserve context, choice, result, uncertainty, and alternative explanations.
Specify who can propose, approve, retire, or correct knowledge. Link cases to
patterns without automatically generalizing them. Keep customer facts outside
the reusable public pack.

## Evaluation and acceptance

Define supported-task success, known failure cases, exceptions, adversarial
inputs, missing tools, and a simple baseline. Use observable outputs and tool
traces rather than required wording. Keep held-out cases separate from examples.
Validate on the target host and model; record versions and unrun tests honestly.

A first useful pack has a clear supported task, an actual decision model, at
least one actionable strategy, contrasting examples, an explicit authority
boundary, and a checkable completion condition. More cards are not inherently
better. Deliver the pack and its limitations, not just this blank template.
