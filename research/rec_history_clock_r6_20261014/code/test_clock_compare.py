import math
import unittest
from clock_compare import NativeSeries, exact_clock_split, common_grid, uncertainty_bound, linear_interpolation_bound, paired_ready

class ClockTests(unittest.TestCase):
    def test_native_affine_and_no_extrapolation(self):
        s=NativeSeries([0,1,2],[0.,1.,2.],[0.,2.,4.],{'X':[1.,4.,7.]})
        self.assertEqual(s.at('L','X',.5).value,2.5)
        self.assertEqual(s.at('time_s','X',1.).value,2.5)
        with self.assertRaises(ValueError):s.at('L','X',3.)
    def test_sparse_gap_rejected(self):
        s=NativeSeries([0,3],[0.,3.],[0.,6.],{'X':[1.,10.]})
        self.assertEqual(s.at('L','X',3.).value,10.)
        with self.assertRaises(ValueError):s.at('L','X',1.)
    def test_monotonic_clock_required(self):
        with self.assertRaises(ValueError):NativeSeries([0,1],[0.,1.],[0.,0.],{'X':[1.,2.]})
    def test_finite_values_required(self):
        with self.assertRaises(ValueError):NativeSeries([0,1],[0.,1.],[0.,1.],{'X':[1.,float('nan')]})
    def test_exact_clock_split_and_sign_change(self):
        r=NativeSeries([0,1,2],[0.,1.,2.],[0.,2.,4.],{'X':[0.,2.,4.]})
        c=NativeSeries([0,1,2],[0.,1.,2.],[0.,1.,2.],{'X':[0.,1.5,3.]})
        q=exact_clock_split(r,c,1.,'X')
        self.assertEqual(q['same_L'],-.5)
        self.assertEqual(q['same_time'],.5)
        self.assertEqual(q['clock_transport'],1.)
        self.assertEqual(q['identity_residual'],0.)
    def test_clock_split_checks_missing_baseline_support(self):
        r=NativeSeries([0,1],[0.,1.],[0.,1.],{'X':[0.,1.]})
        c=NativeSeries([0,1],[0.,1.],[0.,2.],{'X':[0.,2.]})
        with self.assertRaises(ValueError):exact_clock_split(r,c,1.,'X')
    def test_partial_grid_not_rescaled(self):
        g, omitted=common_grid(math.log(.08873654701704167))
        self.assertEqual([j for j,L in g],list(range(434)))
        self.assertEqual(omitted,list(range(434,1001)))
        self.assertLess(g[-1][1],math.log(.08873654701704167))
    def test_unknown_uncertainty_stays_unknown(self):
        self.assertIsNone(uncertainty_bound(None,0.,0.,0.,1.,1.))
    def test_inverse_clock_error_bound(self):
        self.assertEqual(uncertainty_bound(.1,.2,.3,.4,2.,4.),1.7)
        with self.assertRaises(ValueError):uncertainty_bound(0.,0.,0.,0.,0.,1.)
    def test_interpolation_bound(self):
        self.assertEqual(linear_interpolation_bound(0.,1.,.5,2.,0.,0.),.25)
        self.assertEqual(linear_interpolation_bound(0.,1.,0.,2.,.1,.2),.1)
        self.assertIsNone(linear_interpolation_bound(0.,1.,.5,None,0.,0.))
    def test_no_fabricated_five_case_admission(self):
        self.assertFalse(paired_ready({'ZERO','SHEAR_PLUS'}))
        self.assertTrue(paired_ready({'ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'}))
    def test_gap_at_exact_sample_is_permitted(self):
        s=NativeSeries([4,100],[1.,2.],[3.,4.],{'X':[5.,6.]})
        self.assertEqual(s.at('L','X',1.).left_id,4)
        self.assertEqual(s.at('L','X',2.).right_id,100)

if __name__=='__main__':unittest.main()
