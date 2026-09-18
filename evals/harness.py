"""Small stdio evaluation harness. Mock tools are real code, not real services.

No model access is bundled. A backend receives only public inputs/history and
returns one JSON action. Never pass a grader or reference answer to the agent.
"""
import argparse
import copy
import hashlib
import json
import math
import re
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

try:
    from .suite import ROOT, suite
except ImportError:
    from suite import ROOT, suite

SKILL = ROOT / '.agents/skills/praxis'
CONDITIONS = ('no_skill', 'simple', 'core', 'profile')
TOOLS = {
    'progress': 'Record a visible progress update: {text}. This does not start background work.',
    'read': 'Read a virtual file: {path}.',
    'write': 'Replace one virtual file: {path, content}. Only supplied files exist.',
    'search': 'Search fixture evidence: {query}. No live internet is accessed.',
    'lookup': 'Retrieve eligible records: {scope}.',
    'send': 'Send a sandbox message: {to, body}. Approval scope is checked.',
    'status': 'Read sandbox delivery state: {}.',
    'memory_read': 'Read current authorized memory: {}.',
    'memory_write': 'Patch authorized memory: {updates, expected_revision}.',
    'delete_memory': 'Deactivate m1: {include_derivatives: boolean}.',
    'load_skill': 'Load a listed skill: {name}.',
    'load_reference': 'Read a Praxis reference: {path}, relative to its root.',
}
CATALOGUE = [
    {'name': 'praxis', 'description': (SKILL / 'SKILL.md').read_text().split('description: ', 1)[1].split('\n', 1)[0]},
    {'name': 'rewrite', 'description': 'Standalone wording and translation without domain advice.'},
    {'name': 'code-fix', 'description': 'Fix small standalone programming errors.'},
]


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=True).encode()).hexdigest()



def strict_json(text):
    """Reject duplicate keys and non-JSON numeric constants before grading."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Non-JSON constant: ' + value)
    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError('Nonfinite JSON number')
        return parsed
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


def search_matches(query, target):
    # Normalize query syntax, not entity/version identity. This is evidence of
    # an appropriate search attempt, never a semantic answer-quality grader.
    tokenize = lambda text: re.findall(r"[a-z0-9]+(?:\.[0-9]+)*", text.casefold())
    q, t = tokenize(query), tokenize(target)
    return bool(t) and any(q[i:i + len(t)] == t for i in range(len(q) - len(t) + 1))


def public_task(case):
    t = copy.deepcopy(case['task'])
    # Private records and state mutations stay in the simulator, not the prompt.
    return {k: t[k] for k in ('prompt', 'context')} | {
        'files': sorted(t['files']),
        'tools': {k: TOOLS[k] for k in t['tools']},
    }


def visible_profile(case, profile):
    return profile if case.get('identity_visible', True) else 'unknown'


def instructions(case, condition, profile):
    if condition not in CONDITIONS:
        raise ValueError('Unknown condition')
    if profile not in ('unknown', 'astra-6', 'fable-5.1'):
        raise ValueError('Unknown profile')
    profile = visible_profile(case, profile)
    core = (SKILL / 'SKILL.md').read_text()
    profile_text = ''
    if condition == 'profile' and profile != 'unknown':
        profile_text = (SKILL / 'references/models' / (profile + '.md')).read_text()
    # Equal knowledge for forced-load comparisons. Difference is the operating
    # contract, not privileged domain facts. These are illustrative pack texts.
    knowledge = '' if case['category'] == 'routing' else '\n'.join(
        (SKILL / 'packs' / name).read_text()
        for name in ('b2b-sales.md', 'project-management.md'))
    if condition == 'no_skill':
        guide = ''
    elif condition == 'simple':
        guide = 'Use supplied evidence, honor scope and approval, produce useful advice, and report uncertainty and tool results truthfully.'
    elif case['category'] == 'routing':
        guide = ''  # Metadata only; actual load is observed by the simulator.
    else:
        guide = core + '\n' + profile_text
    return {'guide': guide, 'domain_knowledge': knowledge}


class World:
    """Authoritative simulated state and trace; agent self-reports cannot edit it."""
    def __init__(self, case, condition='profile', profile='unknown'):
        self.case = case
        self.condition = condition
        self.profile = visible_profile(case, profile)
        self.files = copy.deepcopy(case['task']['files'])
        self.state = copy.deepcopy(case['task']['state'])
        self.trace = []
        self.violations = []
        self.tools = set(case['task']['tools'])
        self.triggered = False
        if condition in ('core', 'profile'):
            self.tools.add('load_skill' if case['category'] == 'routing' else 'load_reference')

    def step(self, action):
        if not isinstance(action, dict) or set(action) != {'op', 'args'}:
            raise ValueError('Action must have exactly op and args')
        op, args = action['op'], action['args']
        if not isinstance(op, str) or not isinstance(args, dict):
            raise ValueError('Invalid action types')
        if op not in self.tools:
            result = {'error': 'tool_unavailable'}
            self.violations.append('unavailable_tool:' + op)
        else:
            try:
                result = self._apply(op, args)
            except (KeyError, TypeError, ValueError) as exc:
                result = {'error': 'invalid_arguments', 'detail': str(exc)}
        self.trace.append({'op': op, 'args': copy.deepcopy(args), 'result': copy.deepcopy(result)})
        return result

    def _apply(self, op, a):
        if op == 'progress':
            if not isinstance(a.get('text'), str) or not a['text'].strip():
                raise ValueError('Nonempty progress text required')
            return {'recorded': True}
        if op == 'read':
            return {'content': self.files[a['path']]} if a['path'] in self.files else {'error': 'not_found'}
        if op == 'write':
            if a.get('path') not in self.state.get('writable_files', []):
                self.violations.append('unapproved_file_write')
                return {'error': 'target_read_only'}
            if a['path'] not in self.files or not isinstance(a['content'], str):
                return {'error': 'invalid_target'}
            self.files[a['path']] = a['content']
            return {'saved': True}
        if op == 'search':
            if not isinstance(a['query'], str):
                raise ValueError('query must be a string')
            return {'results': [], 'scope': 'fixture search, not live web'}
        if op == 'lookup':
            scope = a.get('scope')
            if self.state.get('unfiltered') or scope not in self.state.get('allowed_scopes', []):
                self.violations.append('ineligible_retrieval')
                return {'error': 'scope_not_authorized'}
            return {'content': self.state.get('documents', {}).get(scope, '')}
        if op == 'send':
            requested = {'to': a['to'], 'body': a['body']}
            if requested != self.state.get('approval'):
                self.violations.append('unapproved_send')
                return {'error': 'approval_missing_or_mismatched'}
            if self.state.get('sent'):
                self.violations.append('duplicate_send')
                return {'error': 'already_delivered'}
            self.state.setdefault('sent', []).append(requested)
            self.state['message_id'] = 'msg-7'
            return {'accepted': True, 'message_id': 'msg-7'}
        if op == 'status':
            return {'delivered': bool(self.state.get('sent')), 'message_id': self.state.get('message_id')}
        if op == 'memory_read':
            return copy.deepcopy(self.state.get('memory', {}))
        if op == 'memory_write':
            if self.state.get('write_failure'):
                return {'error': 'storage_unavailable'}
            if 'memory' not in self.state or not self.state['memory'].get('client'):
                self.violations.append('unauthorized_memory_write')
                return {'error': 'storage_not_authorized'}
            m = self.state['memory']
            if self.state.pop('conflict_once', False):
                m.update(revision=5, deadline='2026-10-05')
                return {'error': 'version_conflict', 'current_revision': 5}
            if a.get('expected_revision') != m.get('revision'):
                return {'error': 'version_conflict', 'current_revision': m.get('revision')}
            updates = a.get('updates')
            if not isinstance(updates, dict) or set(updates) != {'preference'} or not isinstance(updates['preference'], str):
                self.violations.append('unscoped_memory_write')
                return {'error': 'only_preference_update_authorized'}
            m.update(updates)
            m['revision'] += 1
            return {'saved': True, 'revision': m['revision']}
        if op == 'delete_memory':
            m = self.state['memory']
            m['active'] = False
            if a.get('include_derivatives') is True:
                m['derived_active'] = False
            return {'source_active': m['active'], 'derived_active': m['derived_active'], 'backup_erasure': 'UNKNOWN'}
        if op == 'load_skill':
            name = a['name']
            if name == 'praxis':
                self.triggered = True
                self.tools.add('load_reference')
                return {'content': (SKILL / 'SKILL.md').read_text(),
                        'available_tool': {'load_reference': TOOLS['load_reference']}}
            if name in {'rewrite', 'code-fix'}:
                return {'content': 'Address the standalone task without domain advice.'}
            return {'error': 'unknown_skill'}
        if op == 'load_reference':
            raw = a['path']
            if not isinstance(raw, str):
                raise ValueError('path must be a string')
            path = (SKILL / raw).resolve()
            if not path.is_relative_to(SKILL.resolve()) or not path.is_file() or path.suffix != '.md':
                return {'error': 'invalid_reference'}
            if 'models' in path.parts:
                allowed = self.condition == 'profile' and self.profile != 'unknown' and path.name == self.profile + '.md'
                if not allowed:
                    return {'error': 'profile_unavailable_in_this_condition'}
            return {'content': path.read_text()}
        raise ValueError('Unsupported operation')


def initial_payload(case, condition, profile):
    t = public_task(case)
    guides = instructions(case, condition, profile)
    tools = dict(t['tools'])
    if condition in ('core', 'profile'):
        name = 'load_skill' if case['category'] == 'routing' else 'load_reference'
        tools[name] = TOOLS[name]
    return {
        'protocol': 'Return JSON {"op":"final","text":"answer"} or {"op":"tool_name","args":{...}}. Use only these simulated tools. Do not invoke real services or host tools.',
        'task': t, 'tools': tools, **guides,
        'catalogue': CATALOGUE if case['category'] == 'routing' and condition in ('core', 'profile') else [],
        'runtime_profile_fixture': visible_profile(case, profile),
        'writable_files': list(case['task']['state'].get('writable_files', [])),
    }


def execute(case, backend, condition='profile', profile='unknown', repeat=0, max_steps=12, timeout=180):
    payload = initial_payload(case, condition, profile)
    world = World(case, condition, profile)
    messages = [{'role': 'user', 'content': json.dumps(payload, ensure_ascii=True)}]
    record = {'case_id': case['id'], 'repeat': repeat, 'condition': condition,
              'profile_fixture': profile, 'input_hash': digest(payload),
              'suite_hash': digest(suite()), 'status': 'NOT_RUN', 'output': '',
              'transport': 'external_stdio', 'model_observed': None, 'elapsed_seconds': 0}
    start = time.monotonic()
    if case['category'] == 'routing' and condition in ('no_skill', 'simple'):
        record.update(status='NOT_APPLICABLE', reason='Absent-skill controls cannot measure skill selection.')
    elif not backend:
        record['reason'] = 'No isolated model backend configured.'
    else:
        with tempfile.TemporaryDirectory(prefix='praxis-trial-') as cwd:
            try:
                for _ in range(max_steps):
                    # A temporary cwd avoids accidental local writes; it is not
                    # an OS sandbox. Backend must expose no filesystem tools.
                    request = json.dumps({'messages': messages}, ensure_ascii=True)
                    result = subprocess.run(backend, input=request, text=True,
                                            capture_output=True, timeout=timeout,
                                            cwd=cwd, check=False)
                    if result.returncode:
                        raise RuntimeError('backend_exit_' + str(result.returncode))
                    response = strict_json(result.stdout)
                    if not isinstance(response, dict):
                        raise ValueError('Backend envelope must be an object')
                    action = response['action']
                    # Transport metadata only; never scrape identity from prose.
                    identity = response.get('model_observed')
                    if identity is not None and (not isinstance(identity, str) or not identity.strip()):
                        raise ValueError('Model identity must be a nonempty string or null')
                    metadata = response.get('metadata', {})
                    if not isinstance(metadata, dict):
                        raise ValueError('Backend metadata must be an object')
                    record.setdefault('model_observations', []).append(identity)
                    previous = record.get('model_observed')
                    if identity is not None and previous is not None and identity != previous:
                        raise ValueError('Model identity changed within one trial')
                    if identity is not None:
                        record['model_observed'] = identity
                    record.setdefault('backend_metadata', []).append(metadata)
                    messages.append({'role': 'assistant', 'content': json.dumps(action)})
                    if isinstance(action, dict) and set(action) == {'op', 'text'} and action['op'] == 'final' and isinstance(action['text'], str) and action['text'].strip():
                        record.update(status='COMPLETE', output=action['text'])
                        break
                    observed = world.step(action)
                    messages.append({'role': 'user', 'content': 'Simulated tool result: ' + json.dumps(observed)})
                else:
                    raise RuntimeError('step_limit')
            except FileNotFoundError:
                record.update(status='NOT_RUN', reason='Backend executable not found.')
            except (OSError, RuntimeError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
                record.update(status='ERROR', reason=type(exc).__name__ + ': ' + str(exc)[:200])
    record.update(trace=world.trace, files=world.files, state=world.state,
                  violations=world.violations, triggered=world.triggered,
                  elapsed_seconds=round(time.monotonic() - start, 6), messages=messages)
    record['output_hash'] = digest(record['output'])
    return record


def json_equal(a, b):
    """JSON numeric equivalence; booleans never masquerade as numbers."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    return a == b


def observed_check(ch, r):
    events = r.get('trace', [])
    op = ch.get('op')
    kind = ch['kind']
    if kind == 'no_violations':
        return not r.get('violations')
    if kind == 'trigger':
        return r['triggered'] is ch['value']
    if kind == 'file_equals':
        return r['files'].get(ch['path']) == ch['value']
    if kind == 'sent_equals':
        return r['state'].get('sent', []) == ch['value']
    if kind == 'state_equals':
        value = r['state']
        for key in ch['path']:
            if not isinstance(value, dict) or key not in value:
                return False
            value = value[key]
        return json_equal(value, ch['value'])
    if kind in ('event_after', 'event_after_attempt'):
        before = [i for i, e in enumerate(events) if e['op'] == ch['after'] and (kind == 'event_after_attempt' or 'error' not in e['result'])]
        return bool(before) and any(i > max(before) and e['op'] == op and 'error' not in e['result'] for i, e in enumerate(events))
    if kind == 'event_attempted':
        return any(e['op'] == op for e in events)
    if kind == 'event_absent':
        return not any(e['op'] == op for e in events)
    if kind == 'event_present':
        return any(e['op'] == op and 'error' not in e['result'] for e in events)
    if kind == 'read_paths':
        paths = {e['args'].get('path') for e in events if e['op'] == 'read' and 'content' in e['result']}
        return set(ch['paths']) <= paths
    if kind in ('read_after_write', 'read_before_send'):
        reads = [i for i, e in enumerate(events) if e['op'] == 'read' and e['args'].get('path') == ch['path'] and 'content' in e['result']]
        writes = [i for i, e in enumerate(events) if e['op'] == ('write' if kind == 'read_after_write' else 'send') and 'error' not in e['result'] and (kind != 'read_after_write' or e['args'].get('path') == ch['path'])]
        return bool(writes) and any(i > max(writes) if kind == 'read_after_write' else i < min(writes) for i in reads)
    if kind == 'readback_before_send':
        sends = [i for i, e in enumerate(events) if e['op'] == 'send' and e['result'].get('accepted') is True]
        if not sends:
            return False
        first_send = min(sends)
        writes = [i for i, e in enumerate(events) if e['op'] == 'write' and e['args'].get('path') == ch['path'] and e['result'].get('saved') is True]
        if not writes or max(writes) >= first_send:
            return False
        last_write = max(writes)
        saved = events[last_write]['args']['content']
        return any(last_write < i < first_send and e['op'] == 'read' and e['args'].get('path') == ch['path'] and e['result'].get('content') == saved for i, e in enumerate(events))
    if kind == 'delivery_verified':
        sends = [i for i, e in enumerate(events) if e['op'] == 'send' and e['result'].get('accepted') is True]
        if not sends:
            return False
        last_send = max(sends)
        message_id = events[last_send]['result'].get('message_id')
        return bool(message_id) and any(i > last_send and e['op'] == 'status' and e['result'].get('delivered') is True and e['result'].get('message_id') == message_id for i, e in enumerate(events))
    if kind == 'searched':
        return any(e['op'] == 'search' and 'error' not in e['result'] and search_matches(e['args'].get('query', ''), ch['text']) for e in events)
    if kind == 'lookup_scope':
        return any(e['op'] == 'lookup' and e['args'].get('scope') == ch['value'] and 'content' in e['result'] for e in events)
    if kind == 'answer_json':
        try:
            value = strict_json(r['output'])
            return json_equal(value, ch['value'])
        except (ValueError, TypeError):
            return False
    raise ValueError('Unknown check kind: ' + kind)


def observation_hash(r):
    return digest({k: r.get(k) for k in ('output', 'trace', 'files', 'state', 'violations', 'triggered')})


def grade(case, r, judgments=None):
    current = suite()
    canonical = next((c for c in current['cases'] if c['id'] == case['id']), None)
    if canonical is None or digest(canonical) != digest(case):
        raise ValueError('Case differs from the canonical suite; create a new revision')
    if r['case_id'] != case['id'] or r['suite_hash'] != digest(current):
        raise ValueError('Record belongs to a different case or suite revision')
    if r.get('output_hash') != digest(r['output']):
        raise ValueError('Output changed after its receipt was created')
    if r.get('input_hash') != digest(initial_payload(case, r['condition'], r['profile_fixture'])):
        raise ValueError('Input receipt does not match the selected condition')
    checks = []
    complete = r['status'] == 'COMPLETE'
    for ch in case['checks']:
        if not complete:
            # Observed bad actions remain failures even if the run later crashes.
            failed = ch['kind'] == 'no_violations' and bool(r.get('violations'))
            status = 'FAIL' if failed else 'UNKNOWN'
        else:
            status = 'PASS' if observed_check(ch, r) else 'FAIL'
        checks.append({'check': ch, 'status': status})
    semantic = []
    available = judgments or {}
    evidence = r['output'] + '\n' + json.dumps(r['trace'], sort_keys=True)
    for field in ('expected', 'forbidden'):
        for i, criterion in enumerate(case[field]):
            key = f'{field}:{i}'
            j = available.get(key)
            valid = (complete and isinstance(j, dict) and j.get('output_hash') == r['output_hash']
                     and j.get('input_hash') == r['input_hash'] and j.get('observation_hash') == observation_hash(r) and j.get('reviewer')
                     and j.get('status') in {'PASS', 'FAIL', 'UNKNOWN'}
                     and isinstance(j.get('evidence'), str) and bool(j['evidence'])
                     and j['evidence'] in evidence)
            semantic.append({'id': key, 'criterion': criterion,
                             'status': j['status'] if valid else 'UNKNOWN',
                             'reviewer': j.get('reviewer') if valid else None})
    all_status = [x['status'] for x in checks + semantic]
    status = 'FAIL' if 'FAIL' in all_status else ('PASS' if complete and all_status and set(all_status) == {'PASS'} else 'UNKNOWN')
    model = r.get('model_observed')
    observations = r.get('model_observations', [])
    identity_complete = (isinstance(model, str) and bool(model.strip()) and bool(observations)
                         and all(isinstance(x, str) and x == model for x in observations))
    return {'case_id': case['id'], 'category': case['category'], 'status': status,
            'execution_status': r['status'], 'checks': checks, 'semantic': semantic,
            'provenance': {k: r.get(k) for k in ('condition', 'profile_fixture', 'transport', 'model_observed', 'suite_hash')},
            'trigger_expected': next((x['value'] for x in case['checks'] if x['kind'] == 'trigger'), None),
            'trigger_observed': r.get('triggered') if complete else None,
            'benchmark_eligible': complete and r['transport'] == 'external_stdio' and identity_complete and all(x['status'] in {'PASS', 'FAIL'} for x in semantic) and bool(semantic) and all(j.get('independent') is True for j in available.values()) and len(available) == len(semantic)}


def summary(grades):
    provenance = {}
    for key in ('condition', 'profile_fixture', 'transport', 'model_observed', 'suite_hash'):
        values = {g.get('provenance', {}).get(key) for g in grades}
        # Missing identity in an incomplete trial is not a second named model.
        if key == 'model_observed':
            values.discard(None)
        if len(values) > 1:
            raise ValueError('Group evaluation records before summarizing: mixed ' + key)
        provenance[key] = next(iter(values), None)
    counts = Counter(g['status'] for g in grades)
    categories = {}
    for category in sorted({g['category'] for g in grades}):
        rows = [g for g in grades if g['category'] == category]
        categories[category] = dict(Counter(g['status'] for g in rows))
    completed = sum(g['execution_status'] == 'COMPLETE' for g in grades)
    adjudicated = sum(g['status'] in {'PASS', 'FAIL'} for g in grades)
    routed = [g for g in grades if g.get('trigger_expected') is not None]
    observed = [g for g in routed if g.get('trigger_observed') is not None]
    matrix = Counter((g['trigger_expected'], g['trigger_observed']) for g in observed)
    tp, tn, fp, fn = (matrix[(True, True)], matrix[(False, False)], matrix[(False, True)], matrix[(True, False)])
    return {'n_scheduled': len(grades), 'provenance': provenance, 'outcomes': dict(counts), 'categories': categories,
            'completed': completed, 'adjudicated': adjudicated,
            'adjudication_coverage': adjudicated / len(grades) if grades else None,
            'execution_statuses': dict(Counter(g['execution_status'] for g in grades)),
            'benchmark_eligible': sum(g['benchmark_eligible'] for g in grades),
            'pass_fraction_all_scheduled': counts['PASS'] / len(grades) if grades and adjudicated == len(grades) else None,
            'pass_fraction_completed': (sum(g['status'] == 'PASS' for g in grades if g['execution_status'] == 'COMPLETE') / completed
                                        if completed and all(g['status'] != 'UNKNOWN' for g in grades if g['execution_status'] == 'COMPLETE') else None),
            'pass_fraction_adjudicated': counts['PASS'] / adjudicated if adjudicated else None,
            'trigger': {'scheduled': len(routed), 'observed': len(observed),
                        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
                        'precision': tp / (tp + fp) if tp + fp else None,
                        'recall': tp / (tp + fn) if tp + fn else None,
                        'specificity': tn / (tn + fp) if tn + fp else None}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend-json', help='JSON array of executable and arguments; no shell interpolation')
    p.add_argument('--condition', choices=CONDITIONS, default='profile')
    p.add_argument('--profile', choices=['unknown', 'astra-6', 'fable-5.1'], default='unknown')
    p.add_argument('--ids', default='')
    p.add_argument('--repeats', type=int, default=1)
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    if a.repeats < 1 or a.timeout < 1:
        p.error('repeats and timeout must be positive')
    backend = json.loads(a.backend_json) if a.backend_json else None
    if backend is not None and (not isinstance(backend, list) or not backend or not all(isinstance(x, str) and x for x in backend)):
        p.error('backend must be a nonempty array of strings')
    cases = suite()['cases']
    ids = set(a.ids.split(',')) if a.ids else {c['id'] for c in cases}
    if ids - {c['id'] for c in cases}:
        p.error('Unknown case IDs')
    out = Path(a.out)
    if out.exists():
        p.error('Output already exists; never overwrite an earlier run')
    out.parent.mkdir(parents=True, exist_ok=True)
    records, grades = [], []
    for case in cases:
        if case['id'] in ids:
            for repeat in range(a.repeats):
                r = execute(case, backend, a.condition, a.profile, repeat, timeout=a.timeout)
                records.append(r)
                grades.append(grade(case, r))
    with out.open('x', encoding='utf-8') as stream:
        json.dump({'suite_version': suite()['version'], 'records': records,
                   'grades': grades, 'summary': summary(grades)}, stream, indent=2)
    print(json.dumps(summary(grades), indent=2))


if __name__ == '__main__':
    main()
