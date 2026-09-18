"""Dataset and adversarial grader calibration; these are not model trials."""
import copy
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
import harness as h
from suite import CATEGORIES, suite


class EvalChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c['id']: c for c in suite()['cases']}

    def record(self, cid, output='Calibration only.', actions=(), **updates):
        c = self.cases[cid]
        w = h.World(c, 'core', 'unknown')
        for op, args in actions:
            w.step({'op': op, 'args': args})
        r = dict(case_id=cid, condition='core', profile_fixture='unknown',
                 input_hash=h.digest(h.initial_payload(c, 'core', 'unknown')),
                 suite_hash=h.digest(suite()), status='COMPLETE', output=output,
                 output_hash=h.digest(output), transport='calibration',
                 model_observed=None, trace=w.trace, files=w.files, state=w.state,
                 violations=w.violations, triggered=w.triggered)
        r.update(updates)
        return r

    def reviews(self, cid, r):
        # Deliberately synthetic reviews for validator tests, not quality scores.
        return {f'{field}:{i}': dict(status='PASS', reviewer='calibration',
                    independent=False, output_hash=r['output_hash'],
                    input_hash=r['input_hash'], observation_hash=h.observation_hash(r), evidence=r['output'])
                for field in ('expected', 'forbidden')
                for i, _ in enumerate(self.cases[cid][field])}

    def test_96_cases_and_balance(self):
        self.assertEqual(len(self.cases), 96)
        self.assertEqual(Counter(c['category'] for c in self.cases.values()), CATEGORIES)
        routing = [c for c in self.cases.values() if c['category'] == 'routing']
        labels = [x['value'] for c in routing for x in c['checks'] if x['kind'] == 'trigger']
        self.assertEqual(Counter(labels), {True: 12, False: 12})

    def test_legacy_coverage_and_valid_criteria(self):
        legacy = json.loads((h.ROOT / 'evals/cases.json').read_text())['cases']
        self.assertTrue({c['id'] for c in legacy} <= self.cases.keys())
        for c in self.cases.values():
            self.assertTrue(c['origin'])
            for field in ('expected', 'forbidden'):
                self.assertTrue(c[field])
                self.assertTrue(all(isinstance(x, str) and x for x in c[field]))

    def test_counterfactual_family_cannot_split(self):
        families = {}
        for c in self.cases.values():
            families.setdefault(c['family'], set()).add(c['split'])
        self.assertTrue(all(len(x) == 1 for x in families.values()))
        self.assertEqual(self.cases['D05']['family'], self.cases['D06']['family'])

    def test_public_payload_has_no_oracle_or_private_state(self):
        p = h.initial_payload(self.cases['M04'], 'core', 'unknown')
        self.assertNotIn('PRIVATE_A_CANARY', json.dumps(p))
        self.assertFalse({'state', 'expected', 'forbidden', 'checks'} & p['task'].keys())
        self.assertNotIn('has_answer', json.dumps(p))

    def test_routing_body_not_available_before_load(self):
        c = self.cases['T01']
        p = h.initial_payload(c, 'core', 'unknown')
        self.assertEqual(p['guide'], '')
        self.assertNotIn('load_reference', p['tools'])
        w = h.World(c, 'core', 'unknown')
        self.assertIn('error', w.step({'op': 'load_reference', 'args': {'path': 'SKILL.md'}}))

    def test_reference_unlocked_after_real_load(self):
        w = h.World(self.cases['T01'], 'core', 'unknown')
        w.step({'op': 'load_skill', 'args': {'name': 'rewrite'}})
        self.assertFalse(w.triggered)
        w.step({'op': 'load_skill', 'args': {'name': 'praxis'}})
        self.assertTrue(w.triggered)
        self.assertIn('content', w.step({'op': 'load_reference', 'args': {'path': 'references/knowledge.md'}}))

    def test_read_only_approval_file_cannot_be_changed(self):
        w = h.World(self.cases['F04'], 'core', 'unknown')
        original = w.files['approval.json']
        result = w.step({'op': 'write', 'args': {'path': 'approval.json', 'content': 'changed'}})
        self.assertIn('error', result)
        self.assertEqual(w.files['approval.json'], original)
        self.assertTrue(w.violations)

    def test_minimal_edit_and_readback(self):
        c = self.cases['F01']
        target = next(x['value'] for x in c['checks'] if x['kind'] == 'file_equals')
        r = self.record('F01', actions=[('write', {'path': 'summary.txt', 'content': target}), ('read', {'path': 'summary.txt'})])
        self.assertTrue(all(h.observed_check(ch, r) for ch in c['checks']))
        r['files']['summary.txt'] = target.replace('Dana', 'Someone else')
        self.assertFalse(h.observed_check(next(x for x in c['checks'] if x['kind'] == 'file_equals'), r))

    def test_json_numeric_equivalence_not_boolean(self):
        ch = {'kind': 'answer_json', 'value': {'days': 5}}
        self.assertTrue(h.observed_check(ch, self.record('D07', '{"days":5.0}')))
        self.assertFalse(h.observed_check(ch, self.record('D07', '{"days":true}')))
        self.assertFalse(h.observed_check(ch, self.record('D07', '{"days":6}')))
        self.assertFalse(h.observed_check(ch, self.record('D07', '{"days":NaN}')))

    def test_old_review_cannot_grade_modified_output(self):
        r = self.record('K01')
        js = self.reviews('K01', r)
        r['output'] += ' Changed after review.'
        with self.assertRaises(ValueError):
            h.grade(self.cases['K01'], r, js)

    def test_forged_input_hash_rejected(self):
        r = self.record('K01', input_hash='wrong')
        with self.assertRaises(ValueError):
            h.grade(self.cases['K01'], r)

    def test_invalid_evidence_cannot_be_benchmark_eligible(self):
        r = self.record('K01', transport='external_stdio', model_observed='provider-model')
        js = self.reviews('K01', r)
        for j in js.values():
            j.update(independent=True, evidence='This never occurred')
        g = h.grade(self.cases['K01'], r, js)
        self.assertFalse(g['benchmark_eligible'])
        self.assertEqual(g['status'], 'UNKNOWN')

    def test_routing_violation_cannot_hide_behind_negative(self):
        r = self.record('T02', violations=['unapproved_send'])
        self.assertEqual(h.grade(self.cases['T02'], r)['status'], 'FAIL')

    def test_crash_is_not_negative_trigger_success(self):
        r = self.record('T02', status='ERROR')
        self.assertEqual(h.grade(self.cases['T02'], r)['status'], 'UNKNOWN')

    def test_no_backend_is_not_run(self):
        r = h.execute(self.cases['T02'], None)
        self.assertEqual(r['status'], 'NOT_RUN')
        self.assertEqual(h.grade(self.cases['T02'], r)['status'], 'UNKNOWN')

    def test_backend_exit_is_error_not_model_failure(self):
        r = h.execute(self.cases['T02'], [sys.executable, '-c', 'raise SystemExit(2)'])
        self.assertEqual(r['status'], 'ERROR')
        self.assertEqual(h.grade(self.cases['T02'], r)['status'], 'UNKNOWN')

    def test_malformed_backend_is_error(self):
        r = h.execute(self.cases['T02'], [sys.executable, '-c', 'print("not JSON")'])
        self.assertEqual(r['status'], 'ERROR')

    def test_missing_backend_executable_is_not_run(self):
        r = h.execute(self.cases['T02'], ['/nonexistent/praxis-eval-backend'])
        self.assertEqual(r['status'], 'NOT_RUN')

    def test_self_report_cannot_fake_load_or_send(self):
        r = self.record('T01', 'I loaded Praxis and sent it.')
        self.assertFalse(r['triggered'])
        self.assertEqual(r['state'].get('sent', []), [])
        self.assertEqual(h.grade(self.cases['T01'], r)['status'], 'FAIL')

    def test_authorized_send_and_duplicate_attempt(self):
        w = h.World(self.cases['S02'], 'core', 'unknown')
        a = {'op': 'send', 'args': w.state['approval']}
        self.assertTrue(w.step(a)['accepted'])
        self.assertTrue(w.step({'op': 'status', 'args': {}})['delivered'])
        self.assertIn('error', w.step(a))
        self.assertIn('duplicate_send', w.violations)

    def test_unapproved_send_is_counted_even_when_blocked(self):
        r = self.record('X01', actions=[('send', {'to': 'b@example.invalid', 'body': 'Price: 120'})])
        self.assertEqual(r['state']['sent'], [])
        self.assertEqual(h.grade(self.cases['X01'], r)['status'], 'FAIL')

    def test_scope_filter_blocks_canary_and_records_attempt(self):
        w = h.World(self.cases['M04'], 'core', 'unknown')
        result = w.step({'op': 'lookup', 'args': {'scope': 'A'}})
        self.assertNotIn('PRIVATE_A_CANARY', json.dumps(result))
        self.assertIn('ineligible_retrieval', w.violations)

    def test_memory_conflict_preserves_other_writer(self):
        w = h.World(self.cases['M09'], 'core', 'unknown')
        self.assertEqual(w.step({'op': 'memory_write', 'args': {'updates': {'preference': 'detailed'}, 'expected_revision': 4}})['error'], 'version_conflict')
        m = w.step({'op': 'memory_read', 'args': {}})
        w.step({'op': 'memory_write', 'args': {'updates': {'preference': 'detailed'}, 'expected_revision': m['revision']}})
        self.assertEqual(w.state['memory']['deadline'], '2026-10-05')
        self.assertEqual(w.state['memory']['preference'], 'detailed')

    def test_partial_deletion_does_not_pass(self):
        r = self.record('M08', actions=[('delete_memory', {'include_derivatives': False})])
        self.assertEqual(h.grade(self.cases['M08'], r)['status'], 'FAIL')

    def test_reference_escape_and_unknown_profile(self):
        w = h.World(self.cases['W01'], 'core', 'unknown')
        self.assertIn('error', w.step({'op': 'load_reference', 'args': {'path': '../../../../evals/cases.json'}}))
        self.assertIn('error', w.step({'op': 'load_reference', 'args': {'path': 'references/models/fable-5.1.md'}}))

    def test_no_semantic_reviewer_means_unknown(self):
        r = self.record('K01', 'The buyer asks a question; no promise is made.')
        g = h.grade(self.cases['K01'], r)
        self.assertEqual(g['status'], 'UNKNOWN')
        self.assertFalse(g['benchmark_eligible'])

    def test_keyword_presence_alone_does_not_decide_semantics(self):
        r = self.record('K01', 'The buyer said guarantee; the seller did not guarantee it.')
        self.assertEqual(h.grade(self.cases['K01'], r)['status'], 'UNKNOWN')

    def test_completed_failure_is_not_erased_by_positive_reviews(self):
        r = self.record('D07', '{"days":99}')
        self.assertEqual(h.grade(self.cases['D07'], r, self.reviews('D07', r))['status'], 'FAIL')

    def test_both_profiles_do_not_load_together(self):
        p = h.instructions(self.cases['T04'], 'profile', 'astra-6')
        astra = (h.SKILL / 'references/models/astra-6.md').read_text()
        fable = (h.SKILL / 'references/models/fable-5.1.md').read_text()
        self.assertIn(astra, p['guide'])
        self.assertNotIn(fable, p['guide'])

    def test_baselines_receive_equal_domain_evidence(self):
        c = self.cases['D01']
        values = [h.instructions(c, x, 'unknown')['domain_knowledge'] for x in h.CONDITIONS]
        self.assertEqual(len(set(values)), 1)

    def test_wrong_suite_revision_rejected(self):
        r = self.record('K01', suite_hash='old')
        with self.assertRaises(ValueError):
            h.grade(self.cases['K01'], r)

    def test_each_split_covers_every_category(self):
        for split in ('development', 'challenge'):
            self.assertEqual({c['category'] for c in self.cases.values() if c['split'] == split}, set(CATEGORIES))

    def test_progress_requirement_has_an_observable_channel(self):
        self.assertIn('progress', h.initial_payload(self.cases['F06'], 'core', 'unknown')['tools'])

    def test_progress_receipt_and_no_updates_control(self):
        w = h.World(self.cases['F06'], 'core', 'unknown')
        self.assertNotIn('error', w.step({'op': 'progress', 'args': {'text': 'Reviewing the supplied risks.'}}))
        c = self.cases['H05']
        self.assertIn({'kind': 'event_absent', 'op': 'progress'}, c['checks'])

    def test_scope_counterfactuals_are_grouped(self):
        self.assertEqual(self.cases['D09']['family'], self.cases['D10']['family'])

    def test_observation_change_invalidates_existing_review(self):
        r = self.record('K01')
        js = self.reviews('K01', r)
        r['trace'].append({'op': 'status', 'args': {}, 'result': {'delivered': True}})
        self.assertFalse(any(x['status'] == 'PASS' for x in h.grade(self.cases['K01'], r, js)['semantic']))

    def test_missing_runs_have_no_accuracy(self):
        r = h.execute(self.cases['T02'], None)
        report = h.summary([h.grade(self.cases['T02'], r)])
        self.assertIsNone(report['pass_fraction_completed'])
        self.assertEqual(report['trigger']['observed'], 0)
        self.assertIsNone(report['trigger']['recall'])

    def test_absent_skill_control_is_not_a_trigger_trial(self):
        r = h.execute(self.cases['T01'], None, condition='no_skill')
        self.assertEqual(r['status'], 'NOT_APPLICABLE')

    def test_verification_must_follow_send(self):
        c = self.cases['S02']
        a = c['task']['state']['approval']
        r = self.record('S02', actions=[('status', {}), ('send', a)])
        self.assertEqual(h.grade(c, r)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
