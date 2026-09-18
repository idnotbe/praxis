"""Replay recorded assistant decisions through mock tools; never call an LLM.

This proves reproducibility of diagnostic tool observations, not model quality.
The manifest is gold-contaminated historical evidence, never backend input.
"""
import argparse
import json
from pathlib import Path

try:
    from . import harness as h
except ImportError:
    import harness as h

MANIFEST = Path(__file__).with_name('results') / 'replay-2.2.json'


def replay(manifest):
    if manifest['suite_hash'] != h.digest(h.suite()):
        raise ValueError('Diagnostic belongs to a different suite revision')
    cases = {c['id']: c for c in h.suite()['cases']}
    records, grades = [], []
    for row in manifest['responses']:
        case = cases[row['case_id']]
        payload = h.initial_payload(case, 'core', 'unknown')
        if row['input_hash'] != h.digest(payload):
            raise ValueError('Diagnostic public input changed')
        world = h.World(case, 'core', 'unknown')
        for action in row['actions']:
            world.step(action)
        r = dict(case_id=case['id'], repeat=0, condition='core', profile_fixture='unknown',
                 input_hash=row['input_hash'], suite_hash=manifest['suite_hash'],
                 status='COMPLETE', output=row['output'], output_hash=h.digest(row['output']),
                 transport='same_session_action_replay', model_observed=None,
                 trace=world.trace, files=world.files, state=world.state,
                 violations=world.violations, triggered=world.triggered)
        if h.observation_hash(r) != row['observation_hash']:
            raise ValueError('Diagnostic observation changed: ' + case['id'])
        records.append(r)
        # Deliberately do not manufacture semantic judgments for these answers.
        grades.append(h.grade(case, r))
    return dict(kind='recorded_diagnostic_replay_not_model_inference',
                limitations=manifest['limitations'], records=records,
                grades=grades, summary=h.summary(grades))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists():
        parser.error('Refusing to overwrite existing evidence')
    result = replay(h.strict_json(MANIFEST.read_text(encoding='utf-8')))
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
