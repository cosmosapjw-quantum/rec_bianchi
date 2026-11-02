#!/usr/bin/env python3
"""Source-scoped actual-original F08 S0 photon visibility physical/negative tests."""
import hashlib,json,math,os,sys,tempfile,unittest
from pathlib import Path
UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT))
import compute_visibility as calc
import audit_native_visibility as independent

class OriginalF08SourceVisibility(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((UNIT/"results/SCIENCE_RESULT.json").read_text())
  cls.a=json.loads((UNIT/"results/INDEPENDENT_AUDIT.json").read_text())
 def test_original_photon_gas_source_identity(self):
  s=self.s
  self.assertEqual(s["original_rei_F08_S0_pair_sha256"],
    "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8")
  self.assertEqual(s["native_source_trajectory_sha256"],
    "75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843")
  self.assertEqual(s["native_source_q128_sha256"],
    "a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92")
  self.assertEqual(s["bass_original_native_donor_head"],
    "b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6")
 def test_exact_source_physics_and_4_models(self):
  s=self.s
  self.assertEqual(s["native_source_dt_s"],625000000.0)
  self.assertEqual(s["source_horizon_T_s"],1e11)
  self.assertEqual(s["original_source_H_per_s"]["S0_BI"],
                   [1.01e-14,9.9e-15,1e-14])
  self.assertEqual(s["original_source_H_per_s"]["S0_FLRW"],
                   [1e-14,1e-14,1e-14])
  self.assertEqual(len(s["model_results"]),4)
  self.assertEqual(s["physical_gas_trajectory_rows_from_donor"],640)
 def test_positive_thomson_depth_and_visibility_mass(self):
  for m,v in self.s["model_results"].items():
   tau=v["total_Thomson_tau_t0_to_T"]
   P=v["total_scattering_probability"]
   self.assertTrue(2.0e-7<tau<2.1e-7)
   self.assertAlmostEqual(P,-math.expm1(-tau),delta=1e-20)
   self.assertAlmostEqual(P,v["source_temporal_visibility_probability_sum"],
                          delta=2e-20)
 def test_angular_redshift_effect_and_zero_shear_limit(self):
  for model in ("CHARACTERISTIC","ORIGINAL_HAT"):
   for f in (.25,.5,.75):
    q=":fraction="+str(f)
    bi=self.s["ray_angular_redshift_opacity_spread"]["S0_BI_"+model+q]
    fl=self.s["ray_angular_redshift_opacity_spread"]["S0_FLRW_"+model+q]
    self.assertTrue(.0180<bi["relative_tau_spread"]<.0183)
    self.assertLess(fl["relative_tau_spread"],5e-11)
  vec=(.4,.3,math.sqrt(.75))
  H=(1e-14,)*3
  self.assertAlmostEqual(calc.source_redshift(vec,H,0.,1e11),
                         math.expm1(1e-3),delta=4e-15)
 def test_source_native_exact_partial_integral_limits(self):
  a,b=calc.exact_moments(0.)
  self.assertEqual((a,b),(1.,.5))
  self.assertEqual(calc.integrate_segment(0,0,0,625000000.,1,1,1e-4,3e-14),0.)
  # For zero expansion and linear source electron fraction, exact trapezoid
  # is obtained from the source integral formula without time quadrature.
  got=calc.integrate_segment(0,6.25e8,0,6.25e8,1,2,1e-4,0.)
  expect=calc.RATE*1e-4*6.25e8*1.5
  self.assertAlmostEqual(got/expect,1.0,delta=3e-15)
 def test_full_128_ray_4_geometry_source_free_evidence(self):
  s=self.s
  self.assertEqual(s["time_visibility_rows"],644)
  self.assertEqual(s["ray_visibility_rows"],1536)
  self.assertEqual(self.a["physical_scalar_checks"],2180)
  self.assertEqual(self.a["native_gas_thomson_time_integral"],
                   "SOURCE_AFFINE_PHYSICAL_MODEL_PASS")
  self.assertEqual(self.a["source_FLRW_zero_shear_direction"],"PASS")
 def test_owner_no_false_CMB_F05_or_acceptance(self):
  s=self.s
  self.assertFalse(s["F05_original_26event_source_used"])
  self.assertEqual(s["F08_original_full_interval_owner_status"],"HOLD")
  self.assertEqual(s["REI_canonical_DAG"],"28/88")
  self.assertEqual(s["REC_H5_physical_DAG"],"0/313")
  self.assertEqual(s["production"],"HOLD")
  self.assertFalse(s["new_accepted_REI_owner_nodes"])
  self.assertEqual(s["source_nonnegligible_Klein_Nishina_or_thermal_corrections"],
                   "NOT_APPLIED_LEADING_THOMSON_ONLY")
 def test_bad_original_source_hash_fails_closed(self):
  with tempfile.TemporaryDirectory(prefix="rec198_mutation_") as x:
   root=Path(x)
   src=root/"source_inputs"
   src.mkdir()
   authority=json.loads((UNIT/"source_inputs/SOURCE_AUTHORITY.json").read_text())
   authority["bass_donor_trajectory_sha256"]="0"*64
   (src/"SOURCE_AUTHORITY.json").write_text(json.dumps(authority)+"\n")
   os.symlink(UNIT/"source_inputs/F08_ORIGINAL_NATIVE_GAS_640.csv.gz",
              src/"F08_ORIGINAL_NATIVE_GAS_640.csv.gz")
   os.symlink(UNIT/"source_inputs/F08_ORIGINAL_SOURCE_Q128.csv",
              src/"F08_ORIGINAL_SOURCE_Q128.csv")
   with self.assertRaisesRegex(AssertionError,"DONOR_SOURCE_AUTHORITY"):
    independent.read_source(src)
 def test_full_new_physics_source_conditional_reproduction(self):
  # Different platform libm may change the last binary64 bit in exponentials.
  # Check science semantics rather than demanding archive byte identity.
  with tempfile.TemporaryDirectory(prefix="rec198_reproduce_") as folder:
   target=Path(folder)/"regen"
   regenerated=calc.run(UNIT,target)
   self.assertEqual(regenerated["time_visibility_rows"],644)
   self.assertEqual(regenerated["ray_visibility_rows"],1536)
   for key,model in self.s["model_results"].items():
    fresh=regenerated["model_results"][key]
    self.assertTrue(math.isclose(
        fresh["total_Thomson_tau_t0_to_T"],model["total_Thomson_tau_t0_to_T"],
        rel_tol=5e-13))
   audit_result=independent.audit(UNIT,target,Path(folder)/"fresh_audit.json")
   self.assertEqual(audit_result["ray_rows_verified"],1536)

if __name__=="__main__":
 unittest.main()
