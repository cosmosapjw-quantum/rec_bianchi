"""Adversarial source-byte, NaN-mask, parity and high-J scope tests."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from fits_source_grid import load_fits
from compare_original_fits import run
from pr169_neufeld15_reference import parse_lamda
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'source/zenodo_v2'
class TestOriginalFITS(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.standard=load_fits(DATA/'hd_population_grids.fits',source_kind='standard')
  cls.alternate=load_fits(DATA/'hd_population_grids_altex.fits',source_kind='alternate')
 def test_original_md5_and_sha(self):
  expected={'hd_population_grids.fits':('3fffb1591b0f96b254210ed54599667a','0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1'),
  'hd_population_grids_altex.fits':('012ff8819227cd9888f92a7aedafb3f2','1fc3588b32e1423a5c56c68df43ee0385f38f62424615971857b403bf02d45de')}
  for n,(md5,sha) in expected.items():
   b=(DATA/n).read_bytes();self.assertEqual(len(b),2174400);self.assertEqual(hashlib.md5(b).hexdigest(),md5);self.assertEqual(hashlib.sha256(b).hexdigest(),sha)
 def test_full_grid_dims(self):
  for d in (self.standard,self.alternate):
   self.assertEqual(d['populations'].shape,(161,111,15));self.assertEqual(d['HDU_count'],6)
   self.assertEqual(len(d['temperatures_K']),161);self.assertEqual(len(d['densities_cm3']),111)
 def test_true_nan_preserved(self):
  self.assertEqual(self.standard['nan_count'],18868);self.assertEqual(self.alternate['nan_count'],17736)
  self.assertEqual(self.standard['nan_count'],self.standard['metadata_nan_count'])
  self.assertTrue(np.isnan(self.standard['populations']).any())
  self.assertTrue(np.isnan(self.standard['populations'][0,30,8]))
 def test_no_fake_population_from_missing(self):
  for d in (self.standard,self.alternate):
   x=d['populations'];nan=d['logpop'];self.assertTrue(np.array_equal(np.isnan(x),np.isnan(nan)))
   self.assertTrue(np.isfinite(x[~np.isnan(x)]).all())
   self.assertGreaterEqual(np.nanmin(x),0)
 def test_normalized_finite_mass(self):
  for d in (self.standard,self.alternate):
   self.assertLess(float(np.max(abs(d['known_mass']-1))),6e-11)
 def test_source_5_ref_population(self):
  r=self.standard
  self.assertAlmostEqual(float(r['populations'][0,30,0]),0.5842582018478376,places=13)
  self.assertAlmostEqual(float(r['densities_cm3'][30]),10000.,places=7)
 def test_lowJ_collision_rate_original_unchanged(self):
  a=parse_lamda((DATA/'hd_lamda.dat').read_bytes(),verify=True)
  b=parse_lamda((DATA/'hd_lamda_altex.dat').read_bytes())
  changed=[]
  for partner in (2,3):
   for edge,q in a.collision[partner][1].items():
    if q!=b.collision[partner][1][edge]:changed.append((partner,edge))
  self.assertEqual(len(changed),54)
  self.assertTrue(all(edge[0]>8 for partner,edge in changed))
 def test_both_finite_count(self):
  full=(~np.isnan(self.standard['populations']).any(axis=2))&(~np.isnan(self.alternate['populations']).any(axis=2))
  self.assertEqual(int(full.sum()),13532)
 def test_matched_source_line_frequency(self):
  a=parse_lamda((DATA/'hd_lamda.dat').read_bytes(),verify=True)
  b=parse_lamda((DATA/'hd_lamda_altex.dat').read_bytes())
  self.assertEqual(a.rad,b.rad)
 def test_model_predicted_cooling_contrast(self):
  with tempfile.TemporaryDirectory() as tmp:
   j=run(DATA,Path(tmp));self.assertEqual(j['grid']['full15_both_finite_cells'],13532)
   self.assertAlmostEqual(j['cooling_full15']['max_abs_fraction_change'],0.3569998546164981,places=12)
 def test_corrupted_source_refused(self):
  raw=bytearray((DATA/'hd_population_grids.fits').read_bytes());raw[-64]^=1
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'wrong.fits';p.write_bytes(raw)
   with self.assertRaises(ValueError):load_fits(p,source_kind='standard')
if __name__=='__main__':unittest.main()
