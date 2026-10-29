import json
import sys
from pathlib import Path
from fractions import Fraction
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import recoil
RAW=(ROOT/'data'/'PR156_SELECTED_FREQUENCIES.json').read_bytes()

class RecoilTests(unittest.TestCase):
 def test_exact_constants(self):
  self.assertEqual(recoil.H,Fraction('6.62607015e-34'))
  self.assertEqual(recoil.C,Fraction(299792458))
  self.assertEqual(recoil.U,Fraction('1.66053906660e-27'))
 def test_source_replay(self):self.assertEqual(len(recoil.load_transcript(RAW)['rows']),8)
 def test_source_bad_fingerprint(self):
  d=json.loads(RAW);d['source_blob_sha']='0'*40
  with self.assertRaises(recoil.SourceIdentityError):recoil.load_transcript(json.dumps(d).encode())
 def test_source_mutated_J2(self):
  d=json.loads(RAW);d['rows'][1]['nu_P_Hz']='5331561951500/1'
  with self.assertRaises(recoil.SourceIdentityError):recoil.load_transcript(json.dumps(d).encode())
 def test_source_mutated_delta(self):
  d=json.loads(RAW);d['rows'][0]['nu_E_minus_nu_P_Hz']='0/1'
  with self.assertRaises(recoil.SourceIdentityError):recoil.load_transcript(json.dumps(d).encode())
 def test_bad_len(self):
  d=json.loads(RAW);d['rows'].pop()
  with self.assertRaises(recoil.SourceIdentityError):recoil.load_transcript(json.dumps(d).encode())
 def test_bad_ids(self):
  d=json.loads(RAW);d['rows'][2]['upper']=9
  with self.assertRaises(recoil.SourceIdentityError):recoil.load_transcript(json.dumps(d).encode())
 def test_exact_mass_shell_emission(self):
  M=recoil.REFERENCE_MASS; dE=recoil.H*Fraction(15000000000000)
  Ml=M-dE/(recoil.C**2)
  gamma=recoil.emission_photon_energy(dE,M)
  self.assertEqual((M*recoil.C**2-gamma)**2, (Ml*recoil.C**2)**2+gamma**2)
 def test_exact_mass_shell_absorption(self):
  Ml=recoil.REFERENCE_MASS;dE=recoil.H*Fraction(15000000000000);Mu=Ml+dE/recoil.C**2
  gamma=recoil.absorption_photon_energy(dE,Ml)
  self.assertEqual((Ml*recoil.C**2+gamma)**2,(Mu*recoil.C**2)**2+gamma**2)
 def test_three_sector_energy_closure(self):
  M=recoil.REFERENCE_MASS;nu=Fraction(10**13);dE=recoil.H*nu
  photon=recoil.emission_photon_energy(dE,M)
  kinetic=dE-photon
  self.assertEqual(-dE+photon+kinetic,Fraction(0))
  self.assertEqual(kinetic/dE,recoil.recoil_shift_hz(nu,M)/nu)
 def test_recoil_sign(self):
  dE=recoil.H*Fraction(10**13)
  self.assertLess(recoil.emission_photon_energy(dE,recoil.REFERENCE_MASS),dE)
  self.assertGreater(recoil.absorption_photon_energy(dE,recoil.REFERENCE_MASS),dE)
 def test_mass_scaling(self):
  nu=Fraction(10**13)
  self.assertEqual(recoil.recoil_shift_hz(nu,2*recoil.U),Fraction(3,2)*recoil.recoil_shift_hz(nu,3*recoil.U))
 def test_minimum_mass_bound(self):
  nu=Fraction(10**13)
  self.assertGreaterEqual(recoil.recoil_shift_hz(nu,2*recoil.U),recoil.recoil_shift_hz(nu,3*recoil.U))
 def test_seven_legacy_source_fail(self):
  x=recoil.compute(RAW)
  self.assertEqual(x['count_original_35_Hz_fail'],7)
  self.assertEqual([r['J_upper'] for r in x['rows'] if r['original_35_Hz_pass']],[1])
 def test_recoil_large_mismatch(self):
  x=recoil.compute(RAW)
  self.assertEqual(x['count_J2_to_J8_defect_exceeds_2u_recoil'],7)
  self.assertTrue(all(Fraction(r['nu_E_minus_nu_P_Hz_exact'])!=0 for r in x['rows']))
 def test_sign_obstruction(self):
  x=recoil.compute(RAW)
  self.assertEqual([r['J_upper'] for r in x['rows'] if not r['emission_sign_compatible']],[1,2,4,6])
 def test_strong_J8_bound(self):
  x=recoil.compute(RAW)
  self.assertGreater(Fraction(x['rows'][-1]['min_abs_residual_after_recoil_2u_Hz']),Fraction(6000))
 def test_recoil_lower_not_physical_uncertainty(self):
  x=recoil.compute(RAW)
  self.assertEqual(x['production'],'HOLD')
  self.assertIn('NOT original',x['source_authenticity'])
 def test_domain_invalid(self):
  for gap,m in [(Fraction(0),recoil.REFERENCE_MASS),(-recoil.H,recoil.REFERENCE_MASS),(recoil.H,-recoil.U),(recoil.C**2*recoil.U,recoil.U)]:
   with self.assertRaises(recoil.DomainError):recoil.emission_photon_energy(gap,m)
 def test_mass_required_positive(self):
  v=Fraction(8*10**12); d=Fraction(5000)
  self.assertEqual(recoil.mass_required_for_shift(v,-d),recoil.mass_required_for_shift(v,d))
 def test_compact_reference_source(self):
  x=recoil.compute(RAW)
  self.assertEqual(x['selected_source_blob'],recoil.PUBLIC_RESULT_BLOB)
  self.assertEqual(x['canonical_DAG'],'28/88')
  self.assertEqual(x['REC_physical_DAG'],'0/313')

if __name__=='__main__': unittest.main()
