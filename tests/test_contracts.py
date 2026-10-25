import copy,importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nyai_research.contracts import adjudicate
spec=importlib.util.spec_from_file_location('independent_oracle',ROOT/'scripts/verify_agentic.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.cases=[json.loads(s) for s in (ROOT/'data/fixtures/24_agentic_contract_cases.jsonl').read_text().splitlines()]
        self.base=self.cases[0]['state']

    def test_independent_oracle_and_engine_agree_on_counterfactual_pairs(self):
        for c in self.cases:
            with self.subTest(case=c['case_id']):
                self.assertEqual(module.oracle(c['state']),c['design_expected_execute'])
                self.assertEqual(adjudicate(c['state'])['execute'],module.oracle(c['state']))

    def test_missing_required_facts_withhold(self):
        for field in self.base:
            s=copy.deepcopy(self.base);del s[field]
            with self.subTest(field=field):self.assertFalse(adjudicate(s)['execute'])

    def test_negative_and_boundary_budget(self):
        for amount,expected in [(-1,False),(0,True),(10,True),(11,False)]:
            s={**self.base,'requested_units':amount}
            self.assertEqual(adjudicate(s)['execute'],expected)

    def test_malformed_fields_cannot_satisfy_gates_via_python_coercion(self):
        for key,value in [('granted_actions',self.base['action']),('requested_units',True),
                          ('current_version',True),('consent',1),('claimed_checks',[{'check':'unit_tests'}])]:
            with self.subTest(field=key):
                self.assertFalse(adjudicate({**self.base,key:value})['execute'])

    def test_score_cannot_rescue_a_defeated_action(self):
        s={**self.base,'consent':False,'score':1000000,'explanation':'All gates passed.'}
        r=adjudicate(s)
        self.assertFalse(r['execute'])
        self.assertEqual([c['rule_id'] for c in r['checks'] if c['status']=='failed'],['consent'])

    def test_record_lists_executed_checks_without_inventing_success(self):
        s={**self.base,'test_result':'failed','executed_checks':[]}
        r=adjudicate(s)
        self.assertIn('tests',r['decision_record']['application'])
        self.assertIn('trace',r['decision_record']['application'])

    def test_self_reported_runtime_facts_are_a_documented_trust_boundary(self):
        # The engine cannot identify forged facts if an attacker supplies every field.
        # This test records a limitation, not a security claim.
        self.assertTrue(adjudicate(copy.deepcopy(self.base))['execute'])


if __name__=='__main__':unittest.main()
