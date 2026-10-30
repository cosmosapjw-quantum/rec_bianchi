"""Source-level adversarial tests for the two new 2026 high-J extrapolations.

One author's adversarial validation, not distinct-author blind peer review.
"""
from __future__ import annotations
import sys, unittest, tempfile, json, csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from compare_cmb_altex import compare
from source_frequency_audit import run as frequency_audit
from fits_source_grid import load_fits
from pr169_neufeld15_reference import parse_lamda
from hd_cmb15 import solve_cmb
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source/zenodo_v2'

class ScientificAdversarial(unittest.TestCase):
    def test_full_270_common_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=compare(SRC,Path(tmp))
            self.assertEqual(v['states'],270)
            self.assertEqual(v['line_pairs'],3780)
            self.assertEqual(v['source_original_changed_rate_rows'],54)
            self.assertFalse(v['cross_source_sign_disagreements'])
            self.assertGreater(v['largest_relative_delta_among_nonzero']['relative_alternate_minus_std'],.35)
            with open(Path(tmp)/'CMB15_STANDARD_VS_ALTEX_3780_LINE_PAIRS.csv') as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),3780)
            chosen=[r for r in rows if float(r['Tgas_K'])==4000 and float(r['nH2_cm3'])==1e6 and float(r['z'])==100]
            self.assertEqual(len(chosen),14)
            total=sum(float(r['alt_net_W_per_HD'])-float(r['std_net_W_per_HD']) for r in chosen)
            self.assertAlmostEqual(total,v['at_max_absolute']['alternate_minus_std_W_per_HD'],delta=1e-38)
            upper=sum(float(r['alt_net_W_per_HD'])-float(r['std_net_W_per_HD']) for r in chosen if int(r['J_upper'])>=9)
            self.assertGreater(upper/total,1)

    def test_full_17871_grid_byte_locked(self):
        a=load_fits(SRC/'hd_population_grids.fits',source_kind='standard')
        b=load_fits(SRC/'hd_population_grids_altex.fits',source_kind='alternate')
        self.assertEqual(len(a['temperatures_K'])*len(a['densities_cm3']),17871)
        self.assertEqual(a['nan_count'],18868)
        self.assertEqual(b['nan_count'],17736)
        self.assertEqual(a['populations'].shape,(161,111,15))
        self.assertEqual(b['populations'].shape,(161,111,15))

    def test_15level_equal_bath_source_rounding(self):
        with tempfile.TemporaryDirectory() as tmp:
            v=frequency_audit(SRC,Path(tmp)/'frequency.json')
            self.assertEqual(len(v['sources']),2)
            for item in v['sources']:
                self.assertEqual(len(item['frequency_line_differences']),14)
                self.assertEqual(len(item['equal_bath_cases']),16)
                self.assertGreater(item['max_absolute_source_frequency_mismatch_Hz'],40)
                self.assertLess(item['max_absolute_source_frequency_mismatch_Hz'],50)
                self.assertLess(item['max_absolute_relative_equilibrium_defect'],1e-10)

    def test_15level_source_geometry_unchanged(self):
        a=parse_lamda((SRC/'hd_lamda.dat').read_bytes(),verify=True)
        b=parse_lamda((SRC/'hd_lamda_altex.dat').read_bytes())
        self.assertEqual(a.rad,b.rad)
        self.assertEqual(a.levels,b.levels)
        self.assertEqual(len(a.rad),14)
        self.assertEqual(len(a.collision[2][1]),105)
        self.assertEqual(len(a.collision[3][1]),105)
        changed=[]
        for partner in (2,3):
            for (u,l),q in a.collision[partner][1].items():
                if q!=b.collision[partner][1][u,l]:changed.append((partner,u,l))
        self.assertEqual(len(changed),54)
        self.assertTrue(all(u>8 for _,u,l in changed))

if __name__=='__main__':unittest.main()
