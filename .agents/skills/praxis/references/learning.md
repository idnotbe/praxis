# Scoped learning and memory

Read before proposing or performing persistent knowledge changes. Default to
session-only use unless storage is available and the user or a valid standing
policy authorizes the write. Do not create a database to simulate memory.

## Classify before storing

| Kind | Meaning | Example |
|---|---|---|
| Preference | A user's output default, not a fact | Lead internal reports with the decision |
| Project fact | A dated claim in one scope | Project Delta's review is on October 2 |
| User-supplied domain knowledge | A claim with an owner and source | This account requires finance approval |
| Case or observation | An event, not a universal rule | A specific proposal advanced after a workshop |
| Candidate heuristic | A hypothesis needing evaluation | Earlier sponsor mapping may reduce rework |
| Approved pack rule | Reviewed, versioned guidance | A pattern accepted by the pack owner |

The latest explicit task overrides a general preference, within actual policy
and permission boundaries. Repetition may justify proposing a preference;
it does not itself authorize storage. One customer's experience stays scoped
unless authorized review produces a genuinely de-identified reusable pattern.

## Change lifecycle

Observe -> propose -> classify and scope -> check evidence and conflicts ->
authorize -> write -> read back -> use under its stated status -> review or retire.

For each retained item, track an ID, kind, statement, source, owner, subject
scope, observed and verified dates, confidence, status, expiry/review condition,
version, and any superseded item. Keep consent to store, factual confidence,
permission to use, and authority to make a policy distinct.

Make a bounded update to the correct scope. Do not rewrite the global skill
because the user requested a longer answer today. Do not store secrets or raw
client conversations in this public repository. Use a host-approved private
store outside the installation directory. A local ignore rule is not security.

## Corrections, deletion, and failure

Mark a corrected claim superseded and prevent it from competing as active
knowledge. Resolve concurrent updates against the latest version; do not silently
overwrite someone else's correction. Retain history only when policy permits.

A deletion must stop future use in originals, derived summaries, indexes,
caches, and queued work under the host's control. Deactivate first, then purge
or recompute derivatives. Distinguish logical removal from physical erasure and
report any inaccessible copies or retention limits. A rollback reactivates only
still-authorized knowledge; it does not restore revoked permissions.

If a write fails, report that nothing was confirmed saved. If retrieval is
unavailable, use current-session facts and state the limit. If the host cannot
isolate private scopes or propagate deletion, do not enable that memory feature.
Never say "I will remember" without a confirmed persistence result.

## Handoff is not long-term learning

A handoff preserves the active task, exact identifiers, constraints, decisions,
source references, approval bounds, completed actions and checks, blockers, and
next steps. Exclude private reasoning. It is a scoped working summary, not a new
policy or permission to retain all conversation history.
