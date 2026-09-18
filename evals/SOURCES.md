# Sources, reuse and attribution

Reviewed September 18, 2026. Reuse means the specific adaptation stated below,
not a claim to have run any complete upstream benchmark. Source inspection came
before dataset construction. Upstream source files were read, not just search
snippets. Git blob IDs pin inspected file contents even when a branch changes.

| Source | Inspected artifact / blob | Used here |
|---|---|---|
| [Praxis v1](https://github.com/idnotbe/praxis/tree/d722b35154b86c0123d2a1b07311b84a626a5fd2/evals) | `evals/cases.json`, `31a12517b4632e84630efab42dd434ffdad85fa9` | All 32 IDs retained and made executable where possible; additional variants preserve per-case lineage |
| [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | `scripts/run_eval.py`, `e58c70bea39d5b252a1e819f242bbdcdf20e8b87` | Discovery-event protocol and positive/negative queries; no code copied |
| [skill-creator issue 1478](https://github.com/anthropics/skills/issues/1478) | Failure-to-False trigger reporting defect | H07 and executable crash/unknown calibration; crash cannot become a true negative |
| [SkillsBench](https://github.com/benchflow-ai/skillsbench) | `tasks/citation-check/task.md`, `6d2329776af71e21a9739be1e8ae7cddf162c02d` | K08-K10 adapt the citation-integrity task motif, not its bibliography or verifier |
| [tau2-bench](https://github.com/sierra-research/tau2-bench) | `data/tau2/domains/retail/tasks.json`, `e95a9f898b2d1f6568ea8faec78edc3767ce747d`; original task IDs `0`, `1` | D05-D06 preserve the permitted-versus-rejected keyboard fallback counterfactual, replacing account data, stock and actions with a small advisory fixture |
| [LongMemEval](https://github.com/xiaowu0162/LongMemEval) | README, `3490db4f796c14903788ecb3e33f056cab438bb0` | M10-M12 use synthetic timestamp/update/abstention histories inspired by its schema; no original dataset rows copied |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Public benchmark description and methodology | S03-S04 pair an injection with legitimate document requirements; method-inspired synthetic inputs, not imported attack rows |
| [Anthropic agent-evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Official engineering article | Evaluate outcomes and traces, preserve isolation, calibrate graders and balance positive/negative controls |

## What changed, and why not import an entire benchmark?

Praxis already had 32 domain-relevant scenarios, so those were the first source.
The unchanged v1 data remains in `cases.json`; `suite.py` applies explicit
corrections rather than silently editing the historical fixtures. For example,
a translation now states its target language; approved dates, files, memory
revisions and authority scopes are supplied; unavailable capabilities are not
required. This preserves intent while removing impossible or ambiguous tasks.

The tau2 pair originally involves account lookup and a retail exchange in a
large simulated store. D05 and D06 retain its decision-changing fallback preference
but use synthetic, self-contained stock information and prohibit transactions.
This tests whether an advisor respects user constraints; it does not test tau2's
retail environment, user simulator, policy corpus or official reward function.
The two variants share one split family.

The SkillsBench task originally asks for fake academic citation titles from a
BibTeX file. K08-K10 instead provide a closed business evidence fixture, classify
verified/contradicted/unverified claims, and separate a missing source from a
contradiction. No original BibTeX records, paper titles, Docker image, oracle or
verifier are redistributed. The motif is retained, but the label system is
modified to prevent false accusations of fabrication from search absence.

LongMemEval supplies a useful taxonomy, not facts about these synthetic clients.
Oracle fields such as answer-session labels must not enter agent inputs. Real
long-context and cross-session persistence remain host-integration work.
AgentDojo informs the attack/benign-utility pairing, not a claim that these simple
fixtures reproduce its adversarial difficulty. Much of SkillsBench targets tools
and environments unrelated to this small advisory skill; importing those tasks
wholesale would measure environment support more than Praxis behavior.

There are 32 corrected repository rows, 2 concrete external task adaptations,
3 external task-motif adaptations, and 59 additional lineage-derived or
method-inspired synthetic variants. `origin` identifies the starting source,
not an assertion that 96 upstream rows were downloaded. Counts are not counts of
independent problem families. No upstream benchmark score is reported.

## Licenses and notices

Praxis and its original cases retain the repository MIT license. The tau2-derived
pair is modified from Sierra Research's MIT-licensed work. Its inspected license
blob is `f0323a32227c1327820da33d2fb9d3338a27ac84`; the required notice follows.

MIT License

Copyright (c) 2025 Sierra Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

SkillsBench's inspected repository license is Apache-2.0, blob
`261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`. The task credits Xuandong Zhao.
K08-K10 are modified task-motif adaptations by Praxis; original task text and
bibliography are not copied. A full [Apache-2.0 license](licenses/Apache-2.0.txt)
is included conservatively with this attribution. Anthropic, AgentDojo and
LongMemEval code/data are not vendored; their methodologies are cited above.
