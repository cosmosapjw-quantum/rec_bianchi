import itertools
import math
import unittest
from axis_reuse import build_table, axis_support, predict, plan_cases, tensor_diagnostics, exact_residual

class AxisReuseTests(unittest.TestCase):
    def grid(self, coupling=0.0):
        return [{'s':s,'m':m,'r':r,'y':2*s+3*m+4*r+coupling*m*r}
                for s,m,r in itertools.product((-1.,0.,1.),repeat=3)]
    def test_additive_withheld(self):
        t=build_table(self.grid(),('s','m','r'),('y',)); a=axis_support(t)
        self.assertEqual(len(a),15)
        for k,row in t.items(): self.assertEqual(predict(a,k,'y'),row['y'])
    def test_mixed_not_hidden(self):
        t=build_table(self.grid(7),('s','m','r'),('y',)); a=axis_support(t)
        for (s,m,r), row in t.items():
            self.assertEqual(row['y']-predict(a,(s,m,r),'y'),7*m*r)
    def test_no_heldout_training_leak(self):
        t=build_table(self.grid(),('s','m','r'),('y',)); a=axis_support(t)
        before=predict(a,(1.,1.,1.),'y'); t[(1.,1.,1.)]['y']=1.e20
        self.assertEqual(predict(a,(1.,1.,1.),'y'),before)
    def test_duplicate(self):
        rows=self.grid(); rows.append(dict(rows[0]))
        with self.assertRaises(ValueError): build_table(rows,('s','m','r'),('y',))
    def test_missing_grid_cell(self):
        with self.assertRaises(ValueError): build_table(self.grid()[:-1],('s','m','r'),('y',))
    def test_nonfinite(self):
        rows=self.grid(); rows[0]['y']=float('nan')
        with self.assertRaises(ValueError): build_table(rows,('s','m','r'),('y',))
    def test_no_zero_anchor(self):
        rows=[x for x in self.grid() if x['m']!=0]
        with self.assertRaises(ValueError): build_table(rows,('s','m','r'),('y',))
    def test_missing_prediction_key(self):
        a=axis_support(build_table(self.grid(),('s','m','r'),('y',)))
        with self.assertRaises(KeyError): predict(a,(2.,1.,1.),'y')
    def test_cancellation_norm(self):
        x=tensor_diagnostics(2.,3.,-3.,5.,7.)
        self.assertEqual(x['Pi_total_half'],0.0)
        self.assertGreater(x['component_norm_sum'],0)
        self.assertEqual(x['work_m']+x['work_r'],0.0)
    def test_tensor_units_and_frobenius(self):
        x=tensor_diagnostics(2.,3.,6.,5.,7.)
        self.assertAlmostEqual(x['Pi_m_half'],7*3/(math.sqrt(3)*25))
        self.assertEqual(x['work_m'],12.)
        self.assertAlmostEqual(x['Pi_m_frobenius']/x['Pi_m_half'],math.sqrt(2))
    def test_plan_has_no_duplicate(self):
        rows=[{'s':s,'m':m,'r':r,'y':0.0} for s,m,r in
              itertools.product(range(-4,5),repeat=3)]
        p=plan_cases(build_table(rows,('s','m','r'),('y',)))
        self.assertEqual((len(p['support']),len(p['sentinels']),len(p['remaining'])),(153,90,486))
        self.assertEqual(len(set(map(tuple,p['support']+p['sentinels']+p['remaining']))),729)
    def test_exact_saved_float_residual(self):
        self.assertEqual(exact_residual(8.,5.,4.,1.),0.)
        self.assertEqual(exact_residual(9.,5.,4.,1.),1.)

if __name__=='__main__': unittest.main(verbosity=2)
