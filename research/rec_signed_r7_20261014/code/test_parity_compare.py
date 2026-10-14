import math, unittest
from parent_clock import NativeSeries
from parity_compare import parity, parity_error, compare_query, density_parity, validate_configs

class ParityTests(unittest.TestCase):
    def test_nonzero_odd(self):
        self.assertEqual(parity(10., 13., 11.), (2., 1.))
    def test_large_common_offset(self):
        self.assertEqual(parity(2.**40,2.**40+2.,2.**40-1.),(.5,1.5))
    def test_missing_baseline_error_does_not_block_odd(self):
        self.assertEqual(parity_error(None,2.,4.), {'even':None,'odd':3.})
    def test_unknown_signed_error(self):
        self.assertEqual(parity_error(1.,None,4.), {'even':None,'odd':None})
    def test_deterministic_error_propagation(self):
        self.assertEqual(parity_error(1.,2.,4.),{'even':4.,'odd':3.})
    def test_invalid_known_error_even_when_other_unknown(self):
        with self.assertRaises(ValueError):parity_error(None,-1.,2.)
    def test_invalid_state(self):
        with self.assertRaises(ValueError):parity(0.,math.nan,1.)
    def test_clock_change_cancels_in_odd(self):
        zero=NativeSeries([0,1,2],[0.,1.,2.],[0.,2.,4.],{'X':[0.,2.,4.]})
        plus=NativeSeries([0,1,2],[0.,1.,2.],[0.,1.,2.],{'X':[1.,3.,5.]})
        minus=NativeSeries([0,1,2],[0.,1.,2.],[0.,1.,2.],{'X':[-1.,1.,3.]})
        r=compare_query({'ZERO':zero,'SHEAR_PLUS':plus,'SHEAR_MINUS':minus},1.,1.,'X')
        self.assertEqual(r['even_L'],0.)
        self.assertEqual(r['odd_L'],1.)
        self.assertEqual(r['even_t'],1.)
        self.assertEqual(r['odd_t'],1.)
        self.assertTrue(r['signed_clock_equal_at_L'])
        self.assertEqual(r['odd_clock_residual'],0.)
    def test_unequal_clocks_do_not_receive_equal_clock_identity(self):
        zero=NativeSeries([0,1],[0.,1.],[0.,2.],{'X':[0.,2.]})
        plus=NativeSeries([0,1],[0.,1.],[0.,1.],{'X':[0.,2.]})
        minus=NativeSeries([0,1],[0.,1.],[0.,1.5],{'X':[0.,2.]})
        r=compare_query({'ZERO':zero,'SHEAR_PLUS':plus,'SHEAR_MINUS':minus},1.,1.,'X')
        self.assertFalse(r['signed_clock_equal_at_L'])
        self.assertIsNone(r['odd_clock_residual'])
        self.assertAlmostEqual(r['odd_t'],1/3)
    def test_original_gap_rejected(self):
        s=NativeSeries([0,2],[0.,2.],[0.,2.],{'X':[0.,2.]})
        with self.assertRaises(ValueError):s.at('L','X',1.)
    def test_extrapolation_rejected(self):
        s=NativeSeries([0,1],[0.,1.],[0.,1.],{'X':[0.,1.]})
        with self.assertRaises(ValueError):s.at('time_s','X',2.)
    def test_density_mixed_parity(self):
        nE,nO,xE,xO=2.,.5,3.,.25
        even,odd=density_parity(nE,nO,xE,xO)
        self.assertEqual(even,((nE+nO)*(xE+xO)+(nE-nO)*(xE-xO))/2)
        self.assertEqual(odd,((nE+nO)*(xE+xO)-(nE-nO)*(xE-xO))/2)
    def test_same_density_odd(self):
        self.assertEqual(density_parity(2.,0.,3.,.25),(6.,.5))
    def test_config_difference_scope(self):
        configs={n:{'q_ref':str(q),'T':'10','local_target':'1e-5'} for n,q in [('ZERO',0),('SHEAR_PLUS',.01),('SHEAR_MINUS',-.01)]}
        self.assertEqual(validate_configs(configs),.01)
        configs['SHEAR_MINUS']['T']='11'
        with self.assertRaises(ValueError):validate_configs(configs)
    def test_sign_binding_required(self):
        configs={n:{'q_ref':str(q)} for n,q in [('ZERO',0),('SHEAR_PLUS',.01),('SHEAR_MINUS',.02)]}
        with self.assertRaises(ValueError):validate_configs(configs)
    def test_odd_shift_nonidentifiability(self):
        q=.01;a1=.02;a3=-3.;lam=1.7
        self.assertAlmostEqual(q*a1+q**3*a3,q*(a1-q*q*lam)+q**3*(a3+lam),places=18)

if __name__=='__main__':unittest.main()
