import copy
import unittest
from workflow import baseline,validate_predictions,FACTS
from run_evaluation import structural_score

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.case={'id':'demo','text':'Where is A102?'}
        self.d=baseline(self.case)
    def test_valid_source(self): validate_predictions([self.d],[self.case])
    def test_unknown_reference_has_no_status(self):
        d=baseline({'id':'u','text':'Where is A999?'})
        self.assertEqual(d['evidence'],[])
        self.assertIn('not in the supplied snapshot',d['customer_reply'])
    def test_fabricated_quote_rejected(self):
        d=copy.deepcopy(self.d);d['evidence'][0]['quote']='Delivery tomorrow guaranteed'
        with self.assertRaises(RuntimeError):validate_predictions([d],[self.case])
    def test_unknown_source_rejected(self):
        d=copy.deepcopy(self.d);d['evidence'].append({'source_id':'LIVE','quote':'Carrier update'})
        with self.assertRaises(RuntimeError):validate_predictions([d],[self.case])
    def test_answer_needs_evidence(self):
        d=copy.deepcopy(self.d);d['answers'][0]['source_ids'].append('P4')
        with self.assertRaises(RuntimeError):validate_predictions([d],[self.case])
    def test_completed_action_rejected(self):
        d=copy.deepcopy(self.d);d['next_steps'][0]['status']='completed'
        with self.assertRaises(RuntimeError):validate_predictions([d],[self.case])
    def test_manager_is_named(self):
        d=copy.deepcopy(self.d);d['needs_manager']=True
        with self.assertRaises(RuntimeError):validate_predictions([d],[self.case])
    def test_response_ids_must_match(self):
        with self.assertRaises(RuntimeError):validate_predictions([self.d,self.d],[self.case])
    def test_partial_answer_is_not_complete(self):
        expected={'issues':['return','delivery'],'sources':['P1','P3'],'manager':False}
        self.assertFalse(structural_score(self.d,expected)['pass'])
if __name__=='__main__':unittest.main()
