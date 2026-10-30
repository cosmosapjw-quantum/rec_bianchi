import csv
import math
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sixline_atlas import SOURCE, verify_inputs, original_spectroscopy, analyze, run, FLOORS
from pr169_neufeld15_reference import parse_lamda
from hd_cmb15 import solve_cmb

class SixLineAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pairs,cls.stats,cls.summary=analyze(ROOT)
        cls.st_model=parse_lamda((ROOT/'source/zenodo_v2/hd_lamda.dat').read_bytes(),verify=True)
        cls.alt_model=parse_lamda((ROOT/'source/zenodo_v2/hd_lamda_altex.dat').read_bytes())

    def test_original_pins(self):
        verify_inputs(ROOT)
        self.assertEqual(len(SOURCE),6)

    def test_nu_spectroscopy(self):
        original=original_spectroscopy(ROOT)
        self.assertEqual(len(original),14)
        self.assertTrue(22<299792458/original[4]['frequency_Hz']*1e6<24)
        self.assertTrue(12<299792458/original[9]['frequency_Hz']*1e6<13)
        self.assertTrue(all(x['upper']==x['lower']+1 for x in original))

    def test_original_rate_provenance(self):
        a=self.st_model;b=self.alt_model
        self.assertEqual(a.levels,b.levels)
        self.assertEqual(a.rad,b.rad)
        self.assertEqual(len(a.levels),15)
        changed=[(u,l) for cp in (2,3) for (u,l),v in a.collision[cp][1].items()
                    if v!=b.collision[cp][1][(u,l)]]
        self.assertEqual(len(changed),54)
        self.assertTrue(all(u>=9 for u,l in changed))

    def test_warm_grid_count(self):
        self.assertEqual(self.summary['warm_physical_source_conditions'],120)
        self.assertEqual(self.summary['original_full_source_states'],270)
        self.assertEqual(self.summary['original_full_line_pairs'],3780)
        self.assertEqual(len(self.pairs),1800)
        self.assertEqual(len(self.stats),15)

    def test_source_energy_ledger(self):
        self.assertLess(self.summary['max_parent_line_to_total_relative_residual'],3e-14)

    def test_strength_cut_counts(self):
        self.assertEqual(self.summary['floor_metrics']['0_permille']['count'],1800)
        self.assertEqual(self.summary['floor_metrics']['1_permille']['count'],1662)
        self.assertEqual(self.summary['floor_metrics']['10_permille']['count'],1512)
        self.assertEqual(self.summary['floor_metrics']['50_permille']['count'],1272)
        self.assertEqual(self.summary['floor_metrics']['100_permille']['count'],1198)

    def test_top_observable_ratio(self):
        peak=self.summary['floor_metrics']['10_permille']['case']
        self.assertEqual(peak['ratio_name'],'R(9)/R(7)')
        self.assertEqual(peak['Tgas_K'],1000)
        self.assertEqual(peak['nH2_cm3'],1e6)
        self.assertEqual(peak['z'],30)
        self.assertAlmostEqual(peak['relative_source_delta'],1.009805450961784,delta=2e-13)
        self.assertGreater(peak['min_four_line_power_over_sixline_peak'],0.02)

    def test_floor_sensitivity_disentanglement(self):
        peak=self.summary['floor_metrics']['50_permille']['case']
        self.assertEqual(peak['ratio_name'],'R(9)/R(7)')
        self.assertEqual(peak['Tgas_K'],2000)
        self.assertAlmostEqual(peak['relative_source_delta'],0.3884371871732777,delta=1e-13)
        self.assertGreater(peak['min_four_line_power_over_sixline_peak'],0.4)

    def test_all_source_line_ratios_finite_positive(self):
        self.assertTrue(all(x['standard_ratio']>0 and x['alternate_ratio']>0 for x in self.pairs))
        self.assertTrue(all(math.isfinite(x['log_source_delta']) for x in self.pairs))
        self.assertTrue(all(x['standard_num_W_per_HD']>0 and x['alternate_num_W_per_HD']>0 for x in self.pairs))

    def test_independent_log_ratio(self):
        for x in self.pairs[::137]:
            expdelta=math.log(x['alternate_num_W_per_HD'])-math.log(x['alternate_denom_W_per_HD'])-math.log(x['standard_num_W_per_HD'])+math.log(x['standard_denom_W_per_HD'])
            self.assertAlmostEqual(x['log_source_delta'],expdelta,delta=3e-14)

    def test_zero_redshift_warm_no_invalid_MIRI_claim(self):
        local=[x for x in self.pairs if x['z']==0 and x['qualifies_floor_1pct']]
        self.assertEqual(len(local),252)
        self.assertTrue(all(12<=x['rest_numerator_um']<=24 for x in local))
        shifted=[x for x in self.pairs if x['z']>=10]
        self.assertTrue(all(x['rest_numerator_um']*(1+x['z'])>100 for x in shifted))

    def test_warm_intermediate_density_peak(self):
        rows=self.summary['R9_over_R7_z0_1000K_density_sweep']
        self.assertEqual(len(rows),5)
        self.assertGreater(abs(rows[2]['relative_source_delta']),100*abs(rows[0]['relative_source_delta']))
        self.assertGreater(abs(rows[2]['relative_source_delta']),1000*abs(rows[-1]['relative_source_delta']))
        self.assertEqual(rows[2]['nH2_cm3'],1e6)

    def test_independent_fresh_15level_original_source_replay(self):
        # This genuinely solves original 15-level matrix equations, not the CSV transformation.
        for T,n,z in [(1000.,1e6,30.),(2000.,1e6,100.),(4000.,1e4,0.)]:
            row=next(x for x in self.pairs if x['Tgas_K']==T and x['nH2_cm3']==n and x['z']==z and x['ratio_name']=='R(9)/R(7)')
            a=solve_cmb(self.st_model,T,n,z)
            b=solve_cmb(self.alt_model,T,n,z)
            sa=a['line_power_records'][9]['net_W_per_HD']/a['line_power_records'][7]['net_W_per_HD']
            sb=b['line_power_records'][9]['net_W_per_HD']/b['line_power_records'][7]['net_W_per_HD']
            self.assertAlmostEqual(sa,row['standard_ratio'],delta=1e-12*max(abs(sa),1e-20))
            self.assertAlmostEqual(sb,row['alternate_ratio'],delta=1e-12*max(abs(sb),1e-20))
            for y in (a,b):
                self.assertAlmostEqual(y['sum_pop'],1.,delta=1e-12)
                self.assertGreaterEqual(min(y['populations_J0_to_J14']),0)

    def test_tamper_source_rejected_in_optimized_mode_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            for name in SOURCE:
                (root/name).parent.mkdir(parents=True,exist_ok=True)
                os.link(ROOT/name,root/name)
            bad=root/'input/CMB15_STANDARD_VS_ALTEX_270_STATES.csv'
            bad.unlink();bad.write_bytes((ROOT/'input/CMB15_STANDARD_VS_ALTEX_270_STATES.csv').read_bytes()+b' ')
            with self.assertRaises(ValueError): verify_inputs(root)

    def test_canonical_dag_locked(self):
        self.assertEqual(self.summary['canonical_DAG'],'28/88')
        self.assertEqual(self.summary['REC_physical_DAG'],'0/313')
        self.assertEqual(self.summary['original_35Hz'],'FAIL7/8')
        self.assertEqual(self.summary['production'],'HOLD')

if __name__=='__main__':unittest.main()
