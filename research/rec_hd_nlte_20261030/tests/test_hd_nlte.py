import json
import math
import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.linalg import norm
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import hd_nlte as m
S=m.read_source(ROOT/'data/LAMDA_HD_SOURCE_TRANSCRIPTION.json')

class SourceScientificChecks(unittest.TestCase):
    def test_exact_source_shape(self):
        self.assertEqual((len(S['levels']),len(S['radiative_lines'])),(9,8))
        self.assertEqual([len(S['collision_partner_'+x]['rates_cm3_s1']) for x in ('para_H2','ortho_H2')],[9,9])
    def test_no_private_raw_auth_promotion(self):
        self.assertFalse(S['exact_source_bytes_acquired'])
        self.assertEqual(S['historical_pinned_original']['bytes'],2289)
    def test_j1_35Hz_only(self):
        c=m.j1_source_gap_check(S)
        self.assertEqual(c['nuE_minus_nuP_Hz'],'-8.241016200')
        self.assertEqual(c['lines_2_to_8'],'FAIL_UNCHANGED')
    def test_collision_source_both_spins(self):
        for partner in ('para_H2','ortho_H2'):
            self.assertEqual(len(S['collision_partner_'+partner]['rates_cm3_s1']),9)
            self.assertEqual({(p['upper_J'],p['lower_J']) for p in S['collision_partner_'+partner]['rates_cm3_s1']},{(u,u-1) for u in range(1,9)}|{(2,0)})
    def test_source_tamper_fails_closed_even_optimized(self):
        import tempfile
        for mutate in ("remove_line", "fake_raw", "wrong_gate", "wrong_temperature", "wrong_collider"):
            source=json.loads((ROOT/'data/LAMDA_HD_SOURCE_TRANSCRIPTION.json').read_text())
            if mutate=="remove_line":source['radiative_lines'].pop()
            if mutate=="fake_raw":source['exact_source_bytes_acquired']=True
            if mutate=="wrong_gate":source['2011_source_gate_fail_J']=[]
            if mutate=="wrong_temperature":source['temperature_nodes_K']=[50,75,200]
            if mutate=="wrong_collider":source['collision_partner_ortho_H2']['rates_cm3_s1'][0]['lower_J']=1
            with tempfile.TemporaryDirectory() as d:
                f=Path(d)/'tamper.json';f.write_text(json.dumps(source))
                with self.assertRaises(ValueError): m.read_source(f)

    def test_all_positive_rates(self):
        for partner in ('para_H2','ortho_H2'):
            self.assertTrue(all(float(q)>0 for x in S['collision_partner_'+partner]['rates_cm3_s1'] for q in x['values']))
    def test_j1_equal_para_ortho_exact_source(self):
        self.assertEqual(S['collision_partner_para_H2']['rates_cm3_s1'][0]['values'],S['collision_partner_ortho_H2']['rates_cm3_s1'][0]['values'])
        for T in (50,100,200):
            self.assertEqual(m.mixed_q10(S,T,0),m.mixed_q10(S,T,1))
    def test_unphysical_temperature_fails(self):
        for T in (49,75,300):
            with self.assertRaises(ValueError):m.two_level(S,T,10,0.5)
    def test_invalid_density_and_fraction_fails(self):
        for n in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):m.two_level(S,50,n,0.5)
        for f in (-0.01,1.01,float('nan')):
            with self.assertRaises(ValueError):m.two_level(S,50,100,f)

class TwoLevelScientificChecks(unittest.TestCase):
    def test_exact_stationary_balance(self):
        for T in (50,100,200):
            for n in (0,1,100,10000,1000000,1e10):
                x=m.two_level(S,T,n,0.5)
                c10=n*x['q10_cm3_s'];c01=n*x['q01_cm3_s']
                self.assertAlmostEqual(math.fsum(((1-x['population_J1'])*c01,-x['population_J1']*c10)),x['A10_s']*x['population_J1'],delta=32*sys.float_info.epsilon*max(c01,c10,x['A10_s']*x['population_J1'])+1e-26)
    def test_analytic_density_half_saturation(self):
        for T in (50,100,200):
            first=m.two_level(S,T,0,0)
            x=m.two_level(S,T,first['n_half_cooling_cm3'],0.5)
            self.assertAlmostEqual(x['cool_photon_W_per_HD']/x['high_density_limit_photon_W_per_HD'],0.5,places=12)
    def test_low_and_high_density(self):
        for T in (50,100,200):
            self.assertEqual(m.two_level(S,T,0,0)['cool_photon_W_per_HD'],0)
            hi=m.two_level(S,T,1e13,1)
            self.assertAlmostEqual(hi['population_J1']/hi['pJ1_LTE'],1,delta=1e-8)
    def test_source_separate_photon_and_internal(self):
        for T in (50,100,200):
            x=m.two_level(S,T,1e4,0.5)
            self.assertAlmostEqual(x['collisional_energy_exchange_W_per_HD'],x['cool_gap_energy_W_per_HD'],delta=1e-11*abs(x['cool_gap_energy_W_per_HD']))
            self.assertGreater(x['cool_photon_W_per_HD']-x['cool_gap_energy_W_per_HD'],0)
            self.assertLess(abs(x['source_frequency_consistency_defect_W_per_HD']/x['cool_photon_W_per_HD']),4e-12)
    def test_ortho_fraction_analytic_no_effect_j1(self):
        for T in (50,100,200):
            for n in (1,100,1e4,1e8):
                a=m.two_level(S,T,n,0);b=m.two_level(S,T,n,0.5);c=m.two_level(S,T,n,1)
                self.assertEqual(a['cool_photon_W_per_HD'],b['cool_photon_W_per_HD'])
                self.assertEqual(b['cool_photon_W_per_HD'],c['cool_photon_W_per_HD'])
    def test_critical_density_monotonic_temperature(self):
        ns=[m.two_level(S,T,0,0)['n_half_cooling_cm3'] for T in (50,100,200)]
        self.assertTrue(ns[0]>ns[1]>ns[2]>0)

class NineLevelConditionalDiagnostics(unittest.TestCase):
    def test_exact_column_sum_zero_and_offdiag_nonnegative(self):
        for T in (50,100,200):
            for f in (0,0.5,1):
                Q=m.full_generator(S,T,1e4,f)
                self.assertLess(max(abs(Q.sum(axis=0))),1e-17)
                self.assertTrue(np.all(Q-np.diag(np.diag(Q))>=0))
    def test_stationary_normalized(self):
        for T in (50,100,200):
            for n in (0,100,1e4,1e6,1e10):
                for f in (0,1):
                    x=m.full_nlte(S,T,n,f)
                    self.assertTrue(x['valid_numerical_solution'])
                    self.assertLess(x['sum_error'],1e-12)
                    self.assertGreater(min(x['populations']),-2e-15)
                    self.assertEqual(len(x['lines']),8)
    def test_zero_collider_ground_state(self):
        for T in (50,100,200):
            x=m.full_nlte(S,T,0,0.5)
            self.assertEqual(x['populations'][0],1.0)
            self.assertLess(max(abs(v) for v in x['populations'][1:]),1e-15)
            self.assertEqual(x['total_printed_power_W_per_HD'],0.)
    def test_large_density_LTE(self):
        for T in (50,100,200):
            p=np.array(m.full_nlte(S,T,1e10,0.5)['populations']); q=np.array(m.lte(S,T))
            self.assertLess(np.linalg.norm(p-q,ord=1),3e-5)
    def test_high_J_spin_sensitivity(self):
        at0=m.full_nlte(S,200,100,0);at1=m.full_nlte(S,200,100,1)
        self.assertGreater(abs(at1['total_printed_power_W_per_HD']/at0['total_printed_power_W_per_HD']-1),1e-3)
    def test_no_ninelevel_as_physical_authority(self):
        x=m.full_nlte(S,100,100,0.5)
        self.assertIn('FAIL7_OF8',x['source_policy'])
    def test_frozen_2022_constraints(self):
        self.assertEqual([x['frequency_kHz'] for x in S['laboratory_2022_constraints']],['8006533168','13283245098'])

if __name__=='__main__':unittest.main()