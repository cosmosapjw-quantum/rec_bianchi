import importlib.util
import math
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from neufeld15 import (Model,parse_lamda,m_matrix_positive_solve,solve,
                       SI_CONVERSION,SOURCE_CONVERSION,NEUFELD_2026_SHA256)

SAMPLE=b'''!MOLECULE
HD
!MOLECULAR WEIGHT
3.0
!NUMBER OF ENERGY LEVELS
2
!LEVEL + ENERGY + WEIGHT + J
1 0.000000000 1.0 0
2 89.227931612 3.0 1
!NUMBER OF RADIATIVE TRANSITIONS
1
!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)
1 2 1 5.4420380e-08 2674.986094 128.379085
!NUMBER OF COLL PARTNERS
2
!COLLISIONS BETWEEN
2 HD-pH2 rates
!NUMBER OF COLLISIONAL TRANSITIONS
1
!NUMBER OF TEMPERATURES
2
!TEMPERATURES
100.0 200.0
!TRANS + UP + LOW + RATES [cm3 s-1]
1 2 1 2.3030000e-11 3.4454000e-11
!COLLISIONS BETWEEN
3 HD-oH2 rates
!NUMBER OF COLLISIONAL TRANSITIONS
1
!NUMBER OF TEMPERATURES
2
!TEMPERATURES
100.0 200.0
!TRANS + UP + LOW + RATES [cm3 s-1]
1 2 1 2.3127000e-11 3.4535000e-11
'''
class TestHD(unittest.TestCase):
    def setUp(self): self.model=parse_lamda(SAMPLE)
    def test_source_structure(self):
        self.assertEqual(len(self.model.levels),2)
        self.assertEqual(len(self.model.rad),1)
        self.assertEqual(list(self.model.collision[2][1]),[(1,0)])
    def test_sha_lock_rejects_modified(self):
        with self.assertRaises(ValueError):parse_lamda(SAMPLE,verify=True)
    def test_j1_source_rates(self):
        self.assertAlmostEqual(self.model.collision[2][1][(1,0)][0],2.303e-11)
        self.assertAlmostEqual(self.model.collision[3][1][(1,0)][0],2.3127e-11)
    def test_100K_critical_density(self):
        q=(2.303e-11+3*2.3127e-11)/4
        self.assertAlmostEqual(5.442038e-8/q,2355.58017984872,places=8)
    def test_stationarity_and_normalization(self):
        for n in (100,10000,1e8):
            x=solve(self.model,100.,n)
            self.assertAlmostEqual(sum(x['populations']),1.,places=14)
            self.assertGreaterEqual(min(x['populations']),0.)
            self.assertLess(x['maximum_stationarity_residual_per_s'],1e-15)
    def test_limit_thermal_populations(self):
        x=solve(self.model,100.,1e15)['populations'][1]
        expected=3*math.exp(-SI_CONVERSION*89.227931612/100)
        expected=expected/(1+expected)
        self.assertAlmostEqual(x,expected,places=9)
    def test_j1_analytic_solution(self):
        n=1e4;q=(2.303e-11+3*2.3127e-11)/4
        D=n*q; U=3*D*math.exp(-SI_CONVERSION*89.227931612/100)
        expected=U/(U+D+5.442038e-8)
        x=solve(self.model,100.,n)
        self.assertAlmostEqual(x['populations'][1],expected,places=14)
        self.assertAlmostEqual(x['total_spontaneous_power_W_per_HD'],expected*5.442038e-8*6.62607015e-34*2.674986094e12,places=36)
    def test_no_source_temperature_interpolation(self):
        with self.assertRaises(ValueError):solve(self.model,150.,1e4)
    def test_no_negative_density(self):
        with self.assertRaises(ValueError):solve(self.model,100.,-1.)
    def test_no_negativity_after_m_matrix(self):
        # Two-state Markov generator with columns summing to zero
        p=m_matrix_positive_solve([[-0.001,0.002],[0.001,-0.002]])
        self.assertAlmostEqual(p[0],2/3,places=15)
        self.assertAlmostEqual(p[1],1/3,places=15)
    def test_source_and_si_conventions_distinct(self):
        self.assertNotEqual(SI_CONVERSION,SOURCE_CONVERSION)
    def test_collisional_detail_balance(self):
        T=200.;ratio=3*math.exp(-SI_CONVERSION*89.227931612/T)
        self.assertTrue(0<ratio<3)
if __name__=='__main__':unittest.main()
