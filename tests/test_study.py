import copy
import unittest
from study import generate, estimate, fit_historical_slopes

class StudyTests(unittest.TestCase):
    def test_assignment_balance_and_reproducibility(self):
        rows = generate(100, 19)
        self.assertEqual(rows, generate(100, 19))
        self.assertNotEqual(rows, generate(100, 20))
        for segment in (0, 1):
            for arm in (0, 1):
                self.assertEqual(sum(r['segment']==segment and r['assigned']==arm for r in rows),25)

    def test_known_effect_and_variance_by_hand(self):
        rows=[]
        for s in (0,1):
            for t in (0,1):
                for y in (1,3):
                    rows.append({'segment':s,'assigned':t,'pre_contribution':0,'outcome':y+4*t})
        result=estimate(rows)
        self.assertAlmostEqual(result['estimate'],4)
        self.assertAlmostEqual(result['se'],1) # .25*(2/2+2/2), summed over two strata

    def test_adjustment_recovers_exact_effect_when_all_noise_explained(self):
        rows=generate(100,123)
        for r in rows:
            r['outcome']=3*r['pre_contribution']+7*r['assigned']+20*r['segment']
        result=estimate(rows,{0:3,1:3})
        self.assertAlmostEqual(result['estimate'],7)
        self.assertAlmostEqual(result['se'],0)

    def test_oracle_columns_cannot_change_estimate(self):
        rows=generate(100,123)
        poisoned=copy.deepcopy(rows)
        for r in poisoned:
            r['truth_y0']=1e99;r['truth_effect']=-1e99
        self.assertEqual(estimate(rows),estimate(poisoned))

    def test_offset_and_scale_equivariance(self):
        rows=generate(100,111);original=estimate(rows)
        for r in rows: r['outcome']=2*r['outcome']+100
        result=estimate(rows)
        self.assertAlmostEqual(result['estimate'],2*original['estimate'])
        self.assertAlmostEqual(result['se'],2*original['se'])

    def test_historical_fit_uses_untreated_outcome(self):
        rows=generate(1000,7);a=fit_historical_slopes(rows)
        for r in rows:r['outcome']=1e20
        self.assertEqual(a,fit_historical_slopes(rows))

    def test_invalid_design_rejected(self):
        for n in [0,3,6,10]:
            with self.assertRaises(ValueError): generate(n,1)
        with self.assertRaises(ValueError):generate(100,1,'unknown')

if __name__=='__main__':unittest.main()
