import unittest,math
from r8_clock_budget import *

class ClockBudgetTests(unittest.TestCase):
    def test_hermite_partition_and_basis_weights(self):
        for k in range(101):
            u=k/100
            v,sl,rt,sr=hermite_basis(u)
            self.assertAlmostEqual(v+rt,1,places=14)
            self.assertGreaterEqual(v,-1e-15)
            self.assertGreaterEqual(rt,-1e-15)
            self.assertGreaterEqual(sl,-1e-15)
            self.assertLessEqual(sr,1e-15)
            self.assertLessEqual(sl-sr,0.25+1e-15)
    def test_relative_bound_below_component_gate(self):
        b=r8_frozen_budget()
        self.assertLess(b['theorem_only']['1024']['ideal_relative'],1e-9)
        self.assertLess(b['theorem_only']['2048']['ideal_relative'],1e-9)
    def test_positive_sum_global_arithmetic(self):
        b=r8_frozen_budget()
        self.assertAlmostEqual(b['gamma_n_minus_1'],3.466515963288771e-11,delta=1e-22)
        self.assertGreater(b['theorem_only']['1024']['conditional_global_relative'],b['theorem_only']['1024']['ideal_relative'])
    def test_rate_data_error_distinct_from_interp(self):
        h=.001
        x=rate_data_relative_error(h,1e-13,2e-13,5)
        self.assertGreater(x,ideal_hermite_relative_error(h))
    def test_near_origin_real_step_log_cancellation(self):
        a1=.04761905043465769;a2=.04761905047098814
        e=native_span_minus_stable_relative(a1,a2)
        self.assertAlmostEqual(e,-1.8189893480347052e-8,delta=2e-16)
        measured=-1.8190086434893404e-8
        self.assertLess(abs(measured-e),2e-13)
        self.assertGreater(abs(measured),1e-8)
    def test_invalid_intervals(self):
        for values in [(1,1,1),(2,1,1),(-1,2,1)]:
            with self.assertRaises(ValueError):native_span_minus_stable_relative(*values)
    def test_optical_split(self):
        n,F,xe=1.2,2.5,.2;dF=1e-3;dxe=-1e-4
        vals=optical_integrand_delta(n,F,xe,dF,dxe)
        actual=n*((F+dF)*(xe+dxe)-F*xe)
        self.assertAlmostEqual(sum(vals),actual,delta=3e-16)
    def test_baryon_density_matched_a(self):
        self.assertAlmostEqual(baryon_density_at_scale(100,1/21,1/5),100*(5/21)**3)
    def test_ideal_quartic_monotone_for_small_h(self):
        self.assertLess(ideal_hermite_relative_error(.001),ideal_hermite_relative_error(.002))
    def test_clock_zero_denominator_domain(self):
        with self.assertRaises(ValueError):rate_data_relative_error(.01,1e-16,1e-15,0)
    def test_nbound_positive(self):
        with self.assertRaises(ValueError):conditional_global_relative_error(.1,0)
    def test_negative_integrand_not_admitted(self):
        with self.assertRaises(ValueError):optical_integrand_delta(-1,1,1,0,0)

if __name__=='__main__':unittest.main()
