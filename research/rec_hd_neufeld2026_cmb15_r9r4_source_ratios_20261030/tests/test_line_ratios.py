"""Physical post-hoc assertions independent from original author processing."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
import csv

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from compute_line_ratios import compute
SRC=ROOT/'input'

class TestR9R4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.summary=compute(SRC/'CMB15_STANDARD_VS_ALTEX_3780_LINE_PAIRS.csv',SRC/'CMB15_STANDARD_VS_ALTEX_270_STATES.csv')
    def test_16_cases(self): self.assertEqual(len(self.rows),16)
    def test_positive_outputs(self):
        self.assertTrue(all(min(r['std_R4_W_per_HD'],r['std_R9_W_per_HD'],r['alt_R4_W_per_HD'],r['alt_R9_W_per_HD'])>0 for r in self.rows))
    def test_ledger_reconstruction(self): self.assertLess(self.summary['maximum_paired_total_energy_ledger_relative_error'],3e-14)
    def test_known_original_highJ_extrap_ratio(self):
        r=next(r for r in self.rows if r['Tgas_K']==1000 and r['nH2_cm3']==1e6)
        self.assertAlmostEqual(r['std_R9_over_R4'],0.026217341199782862,places=13)
        self.assertAlmostEqual(r['alt_R9_over_R4'],0.05261014998283047,places=13)
    def test_original_full_generator_replay_at_maximum(self):
        sys.path.insert(0,str(ROOT/'src'))
        from hd_cmb15 import solve_cmb
        from pr169_neufeld15_reference import parse_lamda
        root=ROOT/'source'
        a=parse_lamda((root/'hd_lamda.dat').read_bytes(),verify=True)
        original_alt=(root/'hd_lamda_altex.dat').read_bytes()
        self.assertEqual(hashlib.sha256(original_alt).hexdigest(),
            '66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac')
        b=parse_lamda(original_alt)
        src=solve_cmb(a,1000.,1e6,0.)['line_power_records']
        alt=solve_cmb(b,1000.,1e6,0.)['line_power_records']
        ar={x['J_upper']:x['net_W_per_HD'] for x in src}
        br={x['J_upper']:x['net_W_per_HD'] for x in alt}
        ratio=ar[10]/ar[5]
        alternate=br[10]/br[5]
        r=next(x for x in self.rows if x['Tgas_K']==1000 and x['nH2_cm3']==1e6)
        self.assertLess(abs(r['std_R9_over_R4']-ratio),1e-14)
        self.assertLess(abs(r['alt_R9_over_R4']-alternate),1e-14)
    def test_tight_scope(self):
        self.assertTrue(all(r['Tgas_K']>=1000 and r['nH2_cm3']>=1e4 and r['z']==0 for r in self.rows))
    def test_source_sha_refusal(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            bad=Path(d)/'bad.csv'
            f=SRC/'CMB15_STANDARD_VS_ALTEX_3780_LINE_PAIRS.csv'
            bad.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaises(ValueError):compute(bad,SRC/'CMB15_STANDARD_VS_ALTEX_270_STATES.csv')

if __name__=='__main__':unittest.main()
