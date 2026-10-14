import math,unittest
try:
    from .interval_reference import *
    from .interval_reference import _cubic_coeff, _eval_segment, _moments
except ImportError:
    from interval_reference import *
    from interval_reference import _cubic_coeff, _eval_segment, _moments

class IntervalContractTests(unittest.TestCase):
    def test_constant_cubic(self):
        coeff=_cubic_coeff(2.,2.,0.,0.,0.25)
        dt,db=_eval_segment(coeff,0.2,1e-9,0.25,0.)
        self.assertAlmostEqual(dt/(0.25e-9),2.,places=14)
        self.assertEqual(db,0.)
    def test_linear_cubic(self):
        h=.01;coeff=_cubic_coeff(2.,2.2,20.,20.,h)
        dt,_=_eval_segment(coeff,.3,.2,h,0.)
        self.assertAlmostEqual(dt/(h*.2),2+0.2*(.3+.2/2),places=13)
    def test_small_exponential_moment(self):
        for z in (0.,1e-14,1e-8,0.001,.004):
            m=_moments(z)
            self.assertAlmostEqual(m[0], -math.expm1(-z)/z if z else 1.,delta=2e-14)
    def test_endpoints(self):
        for q in (0.,.01,-.01):
            bg=PrescribedBackground(q)
            x=bg.interval(A_REF,A_END)
            self.assertTrue(x.delta_t_s>0)
            self.assertEqual(x.cells_crossed,1024)
    def test_short_near_origin_positive(self):
        p=PrescribedBackground(.01)
        a1=.04761905043465769;a2=.04761905047098814
        x=p.interval(a1,a2)
        self.assertTrue(x.delta_t_s>0)
        self.assertGreater(x.delta_t_s,6e6)
        self.assertLess(x.delta_t_s,7e6)
        self.assertLess(abs(x.delta_t_s-6446090.479173452)/6446090.479173452,1e-9)
    def test_signed_reflection(self):
        p=PrescribedBackground(.01);m=PrescribedBackground(-.01)
        for a1,a2 in [(A_REF,.048),(.053,.054),(.11,.111),(.198,.2)]:
            a=p.interval(a1,a2);b=m.interval(a1,a2)
            self.assertEqual(a.delta_t_s,b.delta_t_s)
            self.assertAlmostEqual(a.delta_b,-b.delta_b,delta=1e-14)
    def test_zero_anisotropy(self):
        b=PrescribedBackground(0.)
        for a1,a2 in [(.05,.06),(.06,.0600000001),(A_REF,A_END)]:
            self.assertEqual(b.interval(a1,a2).delta_b,0.)
    def test_monotone_selected_intervals(self):
        for q in (0.,.005,-.005,.01,-.01):
            b=PrescribedBackground(q,cells=2048)
            for j in range(20):
                a1=A_REF+(A_END-A_REF)*j/21
                a2=a1+2e-10
                self.assertGreater(b.interval(a1,a2).delta_t_s,0.)
    def test_no_extrapolation(self):
        b=PrescribedBackground(0.)
        for a1,a2 in [(A_REF-1e-5,.05),(.1,A_END+.01),(.1,.1),(.1,.09),(math.nan,.11)]:
            with self.assertRaises(ValueError):b.interval(a1,a2)
    def test_positive_integral_reflection(self):
        p=PrescribedBackground(.01)
        for j in range(10):
            left=A_REF*math.exp(p.l_end*j/10)
            right=A_REF*math.exp(p.l_end*(j+1)/10)
            a=p.interval(left,right)
            self.assertGreater(a.delta_t_s,0.)
            self.assertGreater(a.delta_b,0.)
    def test_error_bound_scale(self):
        self.assertLess(ideal_error(math.log(A_END/A_REF)/1024),3.080731e-10)
        self.assertLess(ideal_error(math.log(A_END/A_REF)/2048),1.921401e-11)
    def test_conditional_roundoff(self):
        e=conditional_clock_bound(1.92141e-11,0.,0.,312237)
        self.assertGreater(e,1.92141e-11)
        self.assertLess(e,5.39e-11)
    def test_evaluation_relative_error_composition(self):
        # Floating evaluation error relative to the interpolated positive integral.
        poly=1.0e-4; n=1
        # Deliberately large evaluation error makes the mixed term falsifiable.
        local=.1
        expected=poly+(1+poly)*local
        self.assertAlmostEqual(conditional_clock_bound(poly,0.,local,n),expected,places=15)
    def test_photon_isotropic_limit(self):
        for mu in (-1.,-.23,0.,.4,1.):
            x=photon_map(mu,0.,0.)
            self.assertAlmostEqual(x['energy_ratio'],1.)
            self.assertAlmostEqual(x['mu_final'],mu)
            self.assertAlmostEqual(x['solid_angle_jacobian'],1.)
    def test_photon_energy_lipschitz(self):
        for mu in (-1.,-.3,0.,.7,1.):
            x=photon_map(mu,0.,.01)
            self.assertLessEqual(abs(math.log(x['energy_ratio'])),.020000000001)
            self.assertLessEqual(abs(x['mu_final']-mu),2/math.sqrt(3)*.01+1e-14)
            self.assertLessEqual(abs(math.log(x['solid_angle_jacobian'])),.06+1e-14)
    def test_anisotropic_map_reflection_nontrivial(self):
        x=photon_map(.7,0.,.01)
        y=photon_map(.7,0.,-.01)
        self.assertNotEqual(x['energy_ratio'],y['energy_ratio'])
    def test_bad_ray(self):
        with self.assertRaises(ValueError):photon_map(1.01,0.,0.)
        with self.assertRaises(ValueError):photon_map(.5,math.inf,0.)

if __name__=='__main__':unittest.main()
