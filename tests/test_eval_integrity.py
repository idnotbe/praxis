"""Adversarial controls for false scores, leaked gold, and side-effect order."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
import harness as h
from suite import suite


class IntegrityChecks(unittest.TestCase):
    def setUp(self):
        self.cases = {c['id']: c for c in suite()['cases']}

    def record(self, cid, actions=(), output='Synthetic calibration; not a model run.', **updates):
        case = self.cases[cid]
        world = h.World(case, 'core', 'unknown')
        for op, args in actions:
            world.step({'op': op, 'args': args})
        r = dict(case_id=cid, condition='core', profile_fixture='unknown',
                 input_hash=h.digest(h.initial_payload(case, 'core', 'unknown')),
                 suite_hash=h.digest(suite()), status='COMPLETE', output=output,
                 output_hash=h.digest(output), transport='calibration',
                 model_observed=None, trace=world.trace, files=world.files,
                 state=world.state, violations=world.violations, triggered=world.triggered)
        r.update(updates)
        return r

    def test_route_context_contains_source_not_classification(self):
        for case in self.cases.values():
            if case['category'] == 'routing':
                with self.subTest(case=case['id']):
                    context = case['task']['context']
                    allowed = ('Notes: judge demonstrated work; do not infer ability from employer prestige.'
                               if case['id'] == 'R03' else '')
                    self.assertEqual(context, allowed)

    def test_future_memory_failure_is_not_in_agent_input(self):
        context = self.cases['M02']['task']['context'].lower()
        self.assertNotIn('always fails', context)
        self.assertNotIn('old value', context)
        self.assertTrue(self.cases['M02']['task']['state']['write_failure'])

    def test_failed_save_requires_an_attempt_and_readback(self):
        case = self.cases['M02']
        r = self.record('M02')
        self.assertFalse(all(h.observed_check(ch, r) for ch in case['checks']))

    def test_delete_requires_readback(self):
        r = self.record('M08', [('delete_memory', {'include_derivatives': True})])
        self.assertFalse(all(h.observed_check(ch, r) for ch in self.cases['M08']['checks']))

    def test_search_accepts_case_and_quotes_without_changing_identity(self):
        case = self.cases['F05']
        ch = next(c for c in case['checks'] if c['kind'] == 'searched')
        r = self.record('F05', [('search', {'query': '"northstar" "relay 9.3" private deployment official'})])
        self.assertTrue(h.observed_check(ch, r))
        r = self.record('F05', [('search', {'query': 'Northstar Relay 9.2 deployment'})])
        self.assertFalse(h.observed_check(ch, r))

    def test_readback_must_precede_notification(self):
        case = self.cases['F04']
        approval = case['task']['state']['approval']
        r = self.record('F04', [('read', {'path': 'approval.json'}),
            ('write', {'path': 'forecast.txt', 'content': approval['body']}),
            ('send', approval), ('read', {'path': 'forecast.txt'}), ('status', {})])
        self.assertFalse(all(h.observed_check(ch, r) for ch in case['checks']))

    def test_correct_notification_sequence_is_accepted(self):
        case = self.cases['F04']
        approval = case['task']['state']['approval']
        r = self.record('F04', [('read', {'path': 'approval.json'}),
            ('write', {'path': 'forecast.txt', 'content': approval['body']}),
            ('read', {'path': 'forecast.txt'}), ('send', approval), ('status', {})])
        self.assertTrue(all(h.observed_check(ch, r) for ch in case['checks']))

    def test_missing_runs_do_not_report_zero_accuracy(self):
        r = h.execute(self.cases['T02'], None)
        result = h.summary([h.grade(self.cases['T02'], r)])
        self.assertIsNone(result['pass_fraction_all_scheduled'])
        self.assertIsNone(result['pass_fraction_completed'])

    def test_unreviewed_completed_runs_have_no_semantic_accuracy(self):
        r = self.record('K01')
        result = h.summary([h.grade(self.cases['K01'], r)])
        self.assertIsNone(result['pass_fraction_completed'])

    def test_case_oracle_cannot_be_replaced_without_a_revision(self):
        case = copy.deepcopy(self.cases['K01'])
        r = self.record('K01')
        case['expected'] = ['An unrelated replacement oracle.']
        with self.assertRaises(ValueError):
            h.grade(case, r)

    def test_duplicate_json_keys_are_not_a_valid_answer(self):
        r = self.record('D07', output='{"days":99,"days":5}')
        self.assertFalse(h.observed_check({'kind': 'answer_json', 'value': {'days': 5}}, r))

    def test_state_boolean_is_not_zero(self):
        r = self.record('M08')
        r['state']['memory']['active'] = 0
        self.assertFalse(h.observed_check({'kind': 'state_equals', 'path': ['memory', 'active'], 'value': False}, r))

    def test_empty_object_cannot_impersonate_a_delivery_status(self):
        r = self.record('S02')
        r['trace'] = [{'op': 'send', 'args': {}, 'result': {'accepted': True}},
                      {'op': 'status', 'args': {}, 'result': {'delivered': False}}]
        check = next((c for c in self.cases['S02']['checks'] if c['kind'] == 'delivery_verified'), None)
        self.assertIsNotNone(check)
        self.assertFalse(h.observed_check(check, r))

    def test_backend_identity_must_not_change_between_steps(self):
        code = ('import sys,json; x=json.load(sys.stdin); n=len(x["messages"]); '
                'print(json.dumps({"model_observed":"model-a" if n==1 else "model-b",'
                '"action":{"op":"progress","args":{"text":"Working"}} if n==1 '
                'else {"op":"final","text":"Done"}}))')
        r = h.execute(self.cases['F06'], [sys.executable, '-c', code])
        self.assertEqual(r['status'], 'ERROR')

    def test_nonobject_backend_response_is_recorded_not_a_batch_crash(self):
        r = h.execute(self.cases['K01'], [sys.executable, '-c', 'print("null")'])
        self.assertEqual(r['status'], 'ERROR')

    def test_permission_error_is_recorded_not_a_batch_crash(self):
        with patch.object(h.subprocess, 'run', side_effect=PermissionError('denied')):
            r = h.execute(self.cases['K01'], [sys.executable, '-c', 'pass'])
        self.assertEqual(r['status'], 'ERROR')

    def test_existing_output_is_rejected_before_backend_execution(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'result.json'
            out.write_text('previous result')
            args = ['harness', '--ids', 'K01', '--out', str(out)]
            with patch.object(sys, 'argv', args), patch.object(h, 'execute') as execute:
                with self.assertRaises(SystemExit):
                    h.main()
            execute.assert_not_called()
            self.assertEqual(out.read_text(), 'previous result')

    def test_backend_requires_a_real_string_model_identity(self):
        code = 'import json; print(json.dumps({"model_observed":True,"action":{"op":"final","text":"Done"}}))'
        r = h.execute(self.cases['K01'], [sys.executable, '-c', code])
        self.assertEqual(r['status'], 'ERROR')

    def test_future_search_outcome_is_private(self):
        self.assertNotIn('returns no', self.cases['F05']['task']['context'].lower())

    def test_retail_pair_states_both_requested_replacements(self):
        for cid in ('D05', 'D06'):
            self.assertIn('needs replacement keyboard and thermostat', self.cases[cid]['task']['context'])

    def test_progress_requirement_is_explicit_not_just_permitted(self):
        self.assertIn('Provide one brief progress update', self.cases['F06']['task']['context'])

    def test_semantic_context_does_not_supply_the_answer(self):
        self.assertNotIn('not a seller statement', self.cases['K01']['task']['context'])
        self.assertNotIn('negates a guarantee', self.cases['K06']['task']['context'])
        self.assertNotIn('not a host-policy override', self.cases['S04']['task']['context'])

    def test_unknown_identity_case_cannot_receive_named_profile(self):
        for cid in ('H02', 'X04'):
            for profile in ('astra-6', 'fable-5.1'):
                p = h.initial_payload(self.cases[cid], 'profile', profile)
                self.assertEqual(p['runtime_profile_fixture'], 'unknown')
                self.assertNotIn((h.SKILL / ('references/models/' + profile + '.md')).read_text(), p['guide'])
                w = h.World(self.cases[cid], 'profile', profile)
                self.assertIn('error', w.step({'op': 'load_reference', 'args': {'path': 'references/models/' + profile + '.md'}}))

    def test_missing_per_turn_identity_cannot_be_benchmark_eligible(self):
        c = self.cases['K01']
        r = self.record('K01', transport='external_stdio', model_observed='provider-model',
                        model_observations=[None, 'provider-model'])
        js = {f'{field}:{i}': dict(status='PASS', reviewer='synthetic-reviewer', independent=True,
              input_hash=r['input_hash'], output_hash=r['output_hash'],
              observation_hash=h.observation_hash(r), evidence=r['output'])
              for field in ('expected', 'forbidden') for i, _ in enumerate(c[field])}
        self.assertFalse(h.grade(c, r, js)['benchmark_eligible'])

    def test_failed_save_positive_control(self):
        r = self.record('M02', [('memory_read', {}),
            ('memory_write', {'updates': {'preference': 'detailed'}, 'expected_revision': 4}), ('memory_read', {})])
        self.assertTrue(all(h.observed_check(ch, r) for ch in self.cases['M02']['checks']))

    def test_read_before_failed_save_is_not_post_failure_verification(self):
        r = self.record('M02', [('memory_read', {}),
            ('memory_write', {'updates': {'preference': 'detailed'}, 'expected_revision': 4})])
        self.assertFalse(all(h.observed_check(ch, r) for ch in self.cases['M02']['checks']))

    def test_delete_positive_control(self):
        r = self.record('M08', [('delete_memory', {'include_derivatives': True}), ('memory_read', {})])
        self.assertTrue(all(h.observed_check(ch, r) for ch in self.cases['M08']['checks']))

    def test_stale_readback_after_another_edit_is_not_valid(self):
        c = self.cases['F04']; a = c['task']['state']['approval']
        r = self.record('F04', [('read', {'path': 'approval.json'}),
            ('write', {'path': 'forecast.txt', 'content': a['body']}), ('read', {'path': 'forecast.txt'}),
            ('write', {'path': 'forecast.txt', 'content': a['body']}), ('send', a), ('status', {})])
        self.assertFalse(h.observed_check({'kind': 'readback_before_send', 'path': 'forecast.txt'}, r))

    def test_delivery_id_and_boolean_must_match(self):
        a = self.cases['S02']['task']['state']['approval']
        r = self.record('S02', [('send', a), ('status', {})])
        self.assertTrue(h.observed_check({'kind': 'delivery_verified'}, r))
        r['trace'][-1]['result']['message_id'] = 'another-message'
        self.assertFalse(h.observed_check({'kind': 'delivery_verified'}, r))
        r['trace'][-1]['result'] = {'message_id': 'msg-7', 'delivered': 1}
        self.assertFalse(h.observed_check({'kind': 'delivery_verified'}, r))

    def test_duplicate_backend_key_is_protocol_error(self):
        code = 'print(\'{"action":{"op":"final","text":"First"},"action":{"op":"final","text":"Second"}}\')'
        r = h.execute(self.cases['K01'], [sys.executable, '-c', code])
        self.assertEqual(r['status'], 'ERROR')

    def test_nonfinite_json_number_is_not_valid(self):
        with self.assertRaises(ValueError):
            h.strict_json('{"value":1e999}')

    def test_unreviewed_outcome_is_not_in_accuracy_denominator(self):
        g1 = h.grade(self.cases['K01'], self.record('K01'))
        g2 = h.grade(self.cases['D07'], self.record('D07', output='{"days":9}'))
        report = h.summary([g1, g2])
        self.assertIsNone(report['pass_fraction_completed'])
        self.assertIsNone(report['pass_fraction_all_scheduled'])
        self.assertEqual(report['adjudication_coverage'], 0.5)
        self.assertEqual(report['pass_fraction_adjudicated'], 0.0)

    def test_memo_title_is_optional_not_unrequested_gold(self):
        self.assertNotIn('Choose a reasonable title and', self.cases['A03']['expected'][0])

    def test_summary_rejects_mixed_treatments(self):
        r1 = self.record('K01')
        r2 = self.record('K01', condition='no_skill')
        r2['input_hash'] = h.digest(h.initial_payload(self.cases['K01'], 'no_skill', 'unknown'))
        with self.assertRaises(ValueError):
            h.summary([h.grade(self.cases['K01'], r) for r in (r1, r2)])

    def test_summary_rejects_mixed_evidence_transports(self):
        rs = [self.record('K01'), self.record('K01', transport='external_stdio')]
        with self.assertRaises(ValueError):
            h.summary([h.grade(self.cases['K01'], r) for r in rs])

    def test_summary_rejects_mixed_observed_models(self):
        rs = [self.record('K01', transport='external_stdio', model_observed=m) for m in ('model-a','model-b')]
        with self.assertRaises(ValueError):
            h.summary([h.grade(self.cases['K01'], r) for r in rs])

    def test_summary_carries_diagnostic_provenance(self):
        r = self.record('K01', transport='same_session_action_replay')
        result = h.summary([h.grade(self.cases['K01'], r)])
        self.assertEqual(result['provenance']['transport'], 'same_session_action_replay')
        self.assertEqual(result['benchmark_eligible'], 0)

    def test_uniform_unknown_models_are_a_valid_preflight(self):
        rs = [h.execute(self.cases[cid], None) for cid in ('K01', 'D07')]
        result = h.summary([h.grade(self.cases[r['case_id']], r) for r in rs])
        self.assertEqual(result['n_scheduled'], 2)
        self.assertIsNone(result['pass_fraction_completed'])

    def test_recorded_diagnostic_replay_is_reproducible_not_benchmark(self):
        import replay
        result = replay.replay(h.strict_json(replay.MANIFEST.read_text()))
        self.assertEqual(result['summary']['completed'], 28)
        self.assertEqual(result['summary']['benchmark_eligible'], 0)
        self.assertEqual(result['summary']['outcomes'], {'UNKNOWN': 28})
        self.assertTrue(all(x['status'] == 'PASS' for g in result['grades'] for x in g['checks']))

    def test_recorded_diagnostic_cannot_change_output_after_receipt(self):
        import replay
        manifest = h.strict_json(replay.MANIFEST.read_text())
        manifest['responses'][0]['output'] += ' Tampered.'
        with self.assertRaises(ValueError):
            replay.replay(manifest)

    def test_recorded_diagnostic_cannot_silently_upgrade_suite(self):
        import replay
        manifest = h.strict_json(replay.MANIFEST.read_text())
        manifest['suite_hash'] = 'old-revision'
        with self.assertRaises(ValueError):
            replay.replay(manifest)


if __name__ == '__main__':
    unittest.main()
