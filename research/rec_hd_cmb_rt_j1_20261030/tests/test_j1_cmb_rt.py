"""Regression and physical science tests for the J1 CMB spectral transfer atlas."""
import csv
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from j1_cmb_rt import (load_pinned, line_state, spectrum, gaussian_curve_growth_factor,
                       T_GRID, Z_GRID, DENSITIES, ORTHO, COLUMNS_CM2, GRID_N)
from hd_cmb_balance import C, KB, T0, frequency_ledger, twolevel

class J1TransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src,cls.sung = load_pinned(ROOT/'input')
        cls.state = line_state(cls.src,50,30,'10000','0.5')

    def test_01_source_identity(self):
        self.assertEqual(self.src['exact_source_bytes_acquired'],False)
        self.assertEqual(self.src['temperature_nodes_K'],[50,100,200])
        self.assertEqual(self.src['2011_source_gate_pass_J'],[1])

    def test_02_protected_gate(self):
        self.assertEqual([v['frozen_35Hz_gate'] for v in frequency_ledger(self.src)],['PASS']+['FAIL']*7)

    def test_03_no_maser_source_inversion(self):
        for T in T_GRID:
            for z in Z_GRID:
                s=line_state(self.src,T,z,'1','0.5')
                self.assertGreater(3*s['p0']-s['p1'],0)

    def test_04_j1_collisional_ortho_independence(self):
        a=line_state(self.src,100,30,'10000','0')
        b=line_state(self.src,100,30,'10000','1')
        self.assertAlmostEqual(a['p1'],b['p1'],places=13)
        self.assertAlmostEqual(a['net_W_HD'],b['net_W_HD'],places=35)

    def test_05_sign_cooling_or_heating(self):
        a=line_state(self.src,50,0,'10000','0.5')
        b=line_state(self.src,50,30,'10000','0.5')
        ca,*_=spectrum(a,'1e18')
        cb,*_=spectrum(b,'1e18')
        self.assertGreater(ca['delta_T_RJ0_observed_K'],0)
        self.assertLess(cb['delta_T_RJ0_observed_K'],0)

    def test_06_tau_nonnegative(self):
        r,x,f,tau,y = spectrum(self.state,'1e18')
        self.assertGreaterEqual(float(tau.min()),0)
        self.assertLess(float(tau.max()),0.1)
        self.assertEqual(len(y),GRID_N)

    def test_07_thin_limit_area_identity(self):
        r,*_=spectrum(self.state,'1e14')
        ratio=r['net_integrated_contrast_rest_W_m2_sr']/r['thin_integral_rest_W_m2_sr']
        self.assertAlmostEqual(ratio,r['gaussian_saturation_factor'],delta=1e-10)
        self.assertGreater(ratio,.99999)

    def test_08_gaussian_curve_growth_bounds(self):
        for t in (0,1e-5,0.01,.099):
            v=gaussian_curve_growth_factor(t)
            self.assertLessEqual(v,1)
            self.assertGreaterEqual(v,1-t/(2*math.sqrt(2)))

    def test_09_rest_observer_fourth_power(self):
        r,*_=spectrum(self.state,'1e18')
        self.assertAlmostEqual(r['net_integrated_contrast_rest_W_m2_sr']/(1+self.state['z'])**4,
                               r['net_integrated_contrast_observed_W_m2_sr'],delta=1e-19)

    def test_10_frequency_and_wavelength_units(self):
        s=self.state
        self.assertAlmostEqual(s['nu_obs_Hz'],s['nu0_Hz']/(1+s['z']),places=4)
        self.assertAlmostEqual(s['lambda0_m'],float(C)/s['nu0_Hz'],places=14)
        self.assertGreater(s['b_thermal_ms'],0)

    def test_11_column_monotonicity(self):
        low,*_=spectrum(self.state,'1e14')
        high,*_=spectrum(self.state,'1e16')
        self.assertAlmostEqual(high['tau0']/low['tau0'],100,places=10)
        self.assertLessEqual(abs(high['delta_T_RJ0_observed_K'])/abs(low['delta_T_RJ0_observed_K']),100)

    def test_12_at_very_high_column_reject(self):
        with self.assertRaisesRegex(ValueError,'Optical depth'):
            spectrum(self.state,'1e21')

    def test_13_out_of_source_temperature_reject(self):
        with self.assertRaisesRegex(ValueError,'LAMDA temperature node'):
            line_state(self.src,135,10,'100','0.5')

    def test_14_zero_density_no_unjustified_admission(self):
        with self.assertRaisesRegex(ValueError,'Positive collider density'):
            line_state(self.src,100,10,'0','0.5')

    def test_15_wrong_spin_fraction_reject(self):
        with self.assertRaisesRegex(ValueError,'spin fraction'):
            line_state(self.src,100,10,'1000','1.2')

    def test_16_data_rows_and_scoped_status(self):
        with (ROOT/'results/RESULTS.json').open() as f: s=json.load(f)
        self.assertEqual(s['n_cases'],432)
        self.assertEqual(s['n_spectral_samples'],432*321)
        self.assertEqual(s['source_full9_gate'],'FAIL7/8')
        self.assertEqual(s['canonical_DAG'],'28/88')
        self.assertEqual(s['rec_physical_DAG'],'0/313')
        self.assertEqual(s['production'],'HOLD')
        self.assertFalse(s['auto_next_node'])

    def test_17_data_csv_exact_record_count(self):
        with (ROOT/'results/J1_CMB_RT_432_PHYSICAL_CASES.csv').open() as f:
            self.assertEqual(sum(1 for _ in csv.DictReader(f)),432)
        with (ROOT/'results/J1_CMB_RT_138672_SPECTRAL_SAMPLES.csv').open() as f:
            self.assertEqual(sum(1 for _ in csv.DictReader(f)),138672)

    def test_18_no_source_covariance_fabricated(self):
        case,*_=spectrum(self.state,'1e18')
        self.assertIsNone(case['source_covariance'])
        self.assertIs(case['measured_sky'],False)

    def test_19_source_tamper_rejected_optimized_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in ['LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json','SUNG_HD_PR164_SOURCE.json']:
                (p/name).write_bytes((ROOT/'input'/name).read_bytes())
            path=p/'LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json'
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'digest mismatch'):
                load_pinned(p)

    def test_20_j1_radiative_net_vs_pr167(self):
        for T,z in [(50,0),(50,30),(100,50),(200,50)]:
            s=line_state(self.src,T,z,'10000','0.5')
            r=twolevel(self.src,T,'10000','0.5',float(T0)*(1+z))
            self.assertAlmostEqual(s['net_W_HD']/float(r['net']),1,places=11)

if __name__=='__main__':unittest.main()
