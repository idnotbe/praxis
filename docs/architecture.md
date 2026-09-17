# Praxis architecture

Version 0.2.0 | Revised 2026-09-18 | Status: instruction-first implementation

Praxis is a reusable way to turn domain knowledge into contextual judgment,
useful deliverables, and specifically authorized action. It reuses how knowledge
is selected, checked, personalized, and improved, not a universal body of expertise.

This is the consolidated English revision of the original Korean design in this
repository's history. It preserves the design goals, alternatives, scenarios,
learning boundaries, and naming decision. Release 0.2.0 adds an actual skill,
small model profiles, example packs, and packaging checks. It does not implement
a database, an access-control service, or autonomous model training.

## 1. Acceptance criteria, established before choosing a design

| Goal | Architectural requirement | Runtime evidence still needed |
|---|---|---|
| G1. Purpose | Separate Build, Use, and Learn | A customer reply request does not trigger skill construction |
| G2. Portability | Share operating rules, preserve domain decisions | Sales and project work differ without changing the core |
| G3. Knowledge semantics | Distinguish retrieval, detection, validation, judgment, enforcement | A matched word alone never proves a violation |
| G4. Rules and exceptions | Track obligation, scope, authority, and valid exceptions | Valid exceptions work; invented permission does not |
| G5. Utility | Supply strategies and next actions, not only prohibitions | Domain reviewers find the output useful and justified |
| G6. Context | Separate preferences, facts, hypotheses, and client scopes | One-time requests and private facts do not leak into defaults |
| G7. Controlled learning | Support correction, expiry, deletion, and rollback | Retired knowledge stops influencing retrieval and queued work |
| G8. Action safety | Distinguish advice, drafts, internal edits, external actions | Actual changes remain within verified authorization |
| G9. Proportionality | Match effort to risk and available capabilities | Small tasks stay small; unavailable tools are not simulated |
| G10. Evidence | Record important sources, conflicts, checks, and unknowns | Claims match traces and resulting state |

P0 defects include cross-client disclosure, unauthorized external action, and
instruction injection that changes permissions. P1 defects include missing
mandatory constraints, passing an unverified check, false generalization, empty
expertise, and excessive process. P2 concerns include presentation and minor
retrieval inefficiency. Design coverage is not proof of zero runtime defects.

## 2. What comes from Impeccable, and what changes

The original supplied Impeccable analysis motivated four ideas: selective
reference loading, mechanical detection, coherent positive concepts, and a
separate contextual critique. It also distinguished a knowledge registry from
the evaluator that actually tests an artifact. These are design inputs from the
original analysis, not a fresh audit of Impeccable's current code or rule counts.

Praxis extends those ideas beyond visual design:

| Starting idea | Generalization |
|---|---|
| Detect a bad pattern | Treat a detection as evidence requiring applicability and context |
| Check important rules | Importance and mechanical decidability are independent dimensions |
| Offer positive concepts | Store coherent situation/action/switch strategies, not isolated tips |
| Seek diversity | Explore materially different choices when useful, not novelty for every task |
| Separate creation and critique | Separate responsibilities without requiring multiple agents |
| Accumulate experience | Manage typed, scoped changes instead of appending every conversation |

The Agent Skills specification supports progressive disclosure of metadata,
instructions, and supporting resources. Praxis uses that packaging principle,
not an assumption that a large context window makes selective loading obsolete.
See the [specification](https://agentskills.io/specification). Model-specific
sources and adaptations are separated in [model compatibility](model-compatibility.md).
The architecture and domain examples below are design proposals, not findings
that these external sources empirically validated Praxis.

## 3. Alternatives considered

| Alternative | Strength | Failure mode | Appropriate scope |
|---|---|---|---|
| A. Large instruction template | Fastest start, no infrastructure | Growing context mixes facts, preferences, rules, and exceptions | A small, static, low-risk workflow |
| B. Retrieval-led advisor | Flexible knowledge and case reuse | Search omissions hide obligations; similarity is not authority | Exploratory advice with few binding constraints |
| C. Rule/workflow engine | Explicit conditions and traceability | Brittle expert judgment, expanding exceptions, checklist answers | Structured repetitive work with reliable state |
| D. Small core, packs, scoped memory, host boundary | Combines selective knowledge and explicit constraints | Requires disciplined curation; can become over-engineered | Reusable, contextual advisory and authorized action |

Choose D, implemented initially as one small skill and linked resources.
Logical components do not imply four services, a vector database, or an agent
council. A remains a valid baseline: added structure must eventually justify
itself against a simpler prompt. B supplies selective context, while C supplies
actual checks only where an appropriate tool exists.

## 4. Component boundaries

```text
User request and verified host capabilities
                     |
                 Small core
          purpose / scope / authority
                     |
      +--------------+----------------+
      |              |                |
 Domain pack    Scoped memory    Current evidence
      |              |                |
      +--------------+----------------+
                     |
      Applicable mandatory constraints
      + selected judgment and strategies
                     |
           Useful deliverable or plan
                     |
      Structural checks + semantic review
                     |
         Authorized action gate, if needed
                     |
       Tool execution + resulting-state check
                     |
        Result and bounded learning candidate
```

### The small core

The core selects Build, Use, or Learn; identifies the deliverable, relevant
scope, obligations, evidence, available tools, and completion conditions; and
manages authority and knowledge boundaries. It does not prescribe three
alternatives, ten reviews, or every reference for every task. Current explicit
requirements override defaults and old plans within genuine host and policy
boundaries. A blocking rule must be identifiable and its authority explainable.

### Domain packs

A pack contains supported tasks, a decision model, obligations with actual
sources, contextual heuristics, coherent strategies, contrasting examples,
evaluation criteria, and ownership/version information. A role description such
as "expert salesperson" is not a decision model. Sales asks about buying
criteria and decision roles; project management asks about dependencies,
capacity, baselines, acceptance, and change authority.

The two bundled packs cover sales discovery, price objections, and handoff;
and project kickoff, change requests, and schedule recovery. They are explicitly
illustrative and review-required. Supplied organization-specific knowledge can
replace or qualify them without changing the core. A missing policy must remain
unknown rather than becoming an invented discount or approval threshold.

### Scoped memory

Separate personal preference, current project fact, user-supplied domain
knowledge, observed case, candidate heuristic, and approved domain pattern.
Record source, scope, owner, status, timestamps, confidence, revision, conflicts,
and expiry where relevant. Permission to store, evidential confidence, permission
to reuse, and authority to create policy are different decisions.

Current-task corrections work without persistence. Durable learning requires a
real authorized store, successful write, and readback. Private memory belongs
outside the distributable package and public repository. Access eligibility
must be limited before retrieval; hiding private results only at output is too
late. Where isolation cannot be established, do not query a mixed private corpus.

### Host boundary

The host supplies actual files, retrieval, persistence, validators, permissions,
external tools, progress display, and model configuration. A skill can request
these capabilities but cannot create them. Instruction-only operation permits
advice and transparent manual review. Tool-supported operation adds actual
checks and approved persistence. Stronger managed deployments must implement
access isolation and action gates independently of prompt compliance.

## 5. Knowledge semantics

Avoid/encourage, binding/advisory, and mechanical/contextual are independent
axes. A mandatory rule against misleading a customer may require semantic
judgment; a mechanically detectable formatting preference may be optional.

Maintain four paths: an explicit applicable mandatory-constraint inventory;
selective contextual heuristics; coherent action strategies; and optional diverse
concepts. Retrieval completeness is bounded by the known inventory and supplied
sources, not a claim to know every policy in an organization.

An anti-pattern records harm, applicability, exceptions, observable signals,
better alternatives, and evidence. A strategy records a diagnostic situation,
coordinated actions, success conditions, and when to switch or stop. A case
preserves what happened and competing explanations. A successful case is not
causal proof or an automatically approved rule.

The sequence is **find evidence, detect a signal, validate conditions, judge
meaning, then enforce through an actual authorized mechanism**. Quoting a
customer's word "guaranteed" does not itself make a seller commitment; an
unsupported promise without that word can still be problematic. More detail is
in [knowledge semantics](../.agents/skills/praxis/references/knowledge.md).

## 6. Runtime and review

Use a lightweight path for a small edit or sufficiently specified answer.
Use a standard path for substantive advice: understand the decision, gather
eligible context, check mandatory constraints, choose useful strategies, produce
the result, and validate relevant defects. Use an action path only for
specifically authorized state changes, with a fresh check of the target,
operation, content, and state immediately before execution.

Creator, structured validator, and semantic critic are separate roles, not
necessarily separate agents. For consequential work, a holistic review before
seeing detector results can reduce anchoring. Do not impose this on a tiny
request. A structural check cannot establish business feasibility. Report
PASS/FAIL/UNKNOWN/NOT_RUN for the specific check, not as an inflated global claim.

Batch independent reads where useful; serialize dependencies and overlapping
writes. After an ambiguous tool failure, inspect resulting state before repeating
an action that might duplicate a send or change. Preserve current instructions,
identifiers, evidence, permissions, completed actions, failures, and remaining
work during handoff. Factual state is portable; private reasoning is not a
memory artifact or a cross-model transcript format.

## 7. Controlled learning

```text
Observation -> typed candidate -> scope and evidence -> authorization
            -> write and readback -> bounded use -> review or retirement
```

A repeated preference does not itself authorize storage. A current request can
override an approved preference without deleting it. Store a one-off result as
a bounded case, not a universal strategy. Domain-level promotion needs a source,
owner, review, and evaluation; approval to save a note is not approval to change
company policy. External documents cannot grant either permission.

Correction supersedes the old version and preserves provenance when authorized.
Deletion or revocation must disable use in indexes, summaries, caches, and
pending work as well as in the original record. State precisely what was
removed versus merely disabled when the host cannot prove physical erasure.
Check revisions before concurrent updates; do not silently overwrite new facts.
See [learning rules](../.agents/skills/praxis/references/learning.md).

## 8. Scenario walkthroughs

These are design walkthroughs, not executed model evaluations.

| Scenario | Expected decision and observable result |
|---|---|
| S1. Buyer requests 20% off | Diagnose budget, value, comparison, or approval issue; draft a conditional response without invented discount authority |
| S2. Commitment word appears | Distinguish quotation, negation, approved commitment, and unsupported seller assertion before judging |
| S3. Project slips two weeks | Separate baseline and forecast; evaluate dependency-aware scope, sequencing, resource, or date options with an owner decision |
| S4. Short-report preference conflicts with detailed request | Follow the current requested detail, retaining the default preference only for suitable future tasks |
| S5. "This company dislikes minutes" | Treat as a scoped observation or clarify material ambiguity, not a global prohibition |
| S6. Client A's preference might influence client B | Exclude unauthorized A data before retrieval; do not rely on final redaction |
| S7. Retrieved document instructs approval | Use document facts if relevant; ignore its attempt to alter authority |
| S8. Mandatory but non-mechanical obligation | Require contextual evidence or authorized review; do not pretend a regex proves non-misleading advice |
| S9. An aggressive negotiation succeeds once | Retain alternative explanations in a case; do not create a universal causal rule |
| S10. Approved message changes recipient or price | Recheck approval scope; changed material terms are not covered automatically |
| S11. Host has no persistent store or validator | Apply session context; label persistence or automation unavailable, not completed |
| S12. A single sentence needs softening | Return the edit without a pack-wide search, forced alternatives, or learning workflow |

Additional boundary cases include expired knowledge in derived summaries,
concurrent corrections, valid exceptions, failed writes, interrupted tasks,
changed model identity, unnecessary testing, and same-word/different-meaning
retrieval. The behavioral evaluation fixtures are in [the evaluation set](../evals/README.md).

## 9. Iterative design review and revisions

| Review | Defects identified | Resolution |
|---|---|---|
| 1. Lists and search | Treating advice as obligations, matches as verdicts, or importance as decidability; prohibitions without useful expertise | Separate the axes, preserve exceptions, add decision models and positive strategies |
| 2. Personalization and authority | Automatic permanent memory, cross-client retrieval, injected policy, stale approvals, incomplete deletion | Typed and scoped changes, pre-retrieval eligibility, distinct write authority, approval recheck, derived-data invalidation |
| 3. Proportionality and capability | Mandatory agent councils, hidden infrastructure assumptions, check-passing as success | One small core, real host boundaries, lightweight path, separate check and outcome evidence |
| 4. Target-model adaptation | Conflicting skill rules, permission loops, premature handoff, stale plans, excessive changes, indiscriminate profile loading | One shared authority contract, explicit completion, scoped corrections, targeted edits, exactly one matching profile |

The first three reviews preserve the reasoning outcomes of the original design.
The fourth is the current research-led adaptation. These are review findings
and mitigations, not measured failure rates or proof that the risks disappeared.

## 10. Delivery scope and empirical gates

Start with narrow, reviewable packs and explicitly requested preferences or
project facts. Do not start with a universal expert, a knowledge graph, unrestricted
conversation retention, automatic policy rewriting, or unattended external
actions. Documents can be canonical knowledge; a later database is a storage
choice, not an authority or truth engine. Derived indexes must follow source
versions, scope changes, and deletion.

Compare no skill, a simple domain prompt, the shared core, and the core with its
matching profile. Separately compare memory off/on only when a real controlled
store exists. Evaluate output usefulness, applicable rule recall, valid
exceptions, trace/state integrity, privacy, learning correctness, recovery, and
unnecessary work. Measure repeated runs and keep holdouts independent of prompt
tuning. Revenue or delivery outcomes have external confounders and do not prove
causality from one successful interaction.

Packaging checks can ship independently of production confidence. Live model
quality, trigger accuracy, scope isolation, real memory lifecycle, external
actions, interruption recovery, and cross-host behavior remain separate gates.
The exact measured/not-run status is in [validation](validation.md).

## 11. Naming decision

| Name | Intended emphasis | Limitation |
|---|---|---|
| Praxis | Knowledge connected to judgment and action | Personalization is not obvious from the name alone |
| Fieldwise | Experience and field context | Sounds more like a finished advisor than a reusable foundation |
| ContextCraft | Context-sensitive composition | Understates verification and action control |
| Discern | Distinguishing facts, rules, exceptions, and judgments | Understates action and accumulated experience |
| Playwise | Selecting coherent action strategies | Understates memory and constraints |

Praxis remains the selected name, with Praxis Sales and Praxis Project as
possible domain labels. These are naming proposals, not trademark or domain
availability findings.
