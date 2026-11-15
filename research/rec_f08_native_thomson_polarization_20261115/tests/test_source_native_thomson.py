#!/usr/bin/env python3
"""Bounded source-free original F08 photon Thomson science and adverse controls."""
import hashlib,json,math,os,sys,tempfile,unittest
from pathlib import Path
import numpy as np
UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT))
import compute_native_scatter as physics
import audit_thomson_stokes as auditor
import angular_quadrupole_systematics as harmonic

class OriginalF08NativeThomsonTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=json.loads((UNIT/"results/SCIENCE_RESULT.json").read_text())
  cls.a=json.loads((UNIT/"results/INDEPENDENT_AUDIT.json").read_text())
  cls.s=json.loads((UNIT/"results/SYSTEMATIC_RESULT.json").read_text())
  cls.native=json.loads((UNIT/"source_inputs/NATIVE_CAPTURE_RESULT.json").read_text())

 def test_original_native_640_source_byte_identity(self):
  self.assertEqual(self.native["original_native_runs"],640)
  self.assertEqual(self.native["true_native_source_photon_stage_rows"],81920)
  self.assertEqual(self.native["source_native_640_output_sha256"],physics.NATIVE_BASS_SHA)
  self.assertEqual(self.d["source_original_81920_angle_capture_sha256"],physics.ANGULAR_CAPTURE_SHA)
  self.assertEqual(self.d["source_original_REI_F08_pair_sha256"],
                  "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8")
  self.assertEqual(physics.sha(UNIT/"source_inputs/ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz"),
                  physics.ANGULAR_CAPTURE_SHA)

 def test_real_f08_photons_and_stokes_81920_rows(self):
  self.assertEqual(self.d["source_native_actual_Rust_stages"],640)
  self.assertEqual(self.d["source_physics_actual_angular_rows"],81920)
  self.assertEqual(self.a["source_stage_count"],640)
  self.assertEqual(self.a["total_ray_checks"],81920)
  self.assertEqual(self.d["source_ang_stokes_csv_sha256"],
       physics.sha(UNIT/"results/NATIVE_F08_THOMSON_81920_ANGULAR_STOKES_SOURCE.csv.gz"))
  self.assertEqual(self.d["source_stage_budget_csv_sha256"],
       physics.sha(UNIT/"results/NATIVE_F08_THOMSON_640_PHYSICAL_STAGE_BUDGET.csv.gz"))
  self.assertEqual(self.a["scattering_csv_sha256"],self.d["source_ang_stokes_csv_sha256"])

 def test_quadrupole_exact_positive_conserving_thomson(self):
  q=physics.source_q(UNIT)
  w,P,Q,U,raw,moment=physics.kernel(q)
  self.assertTrue(np.all(w>0) and np.all(P>0))
  self.assertLess(np.max(np.abs(moment-np.eye(3)/3)),4e-15)
  self.assertLess(np.max(abs(P.sum(axis=0)-1)),4e-15)
  self.assertLess(np.max(abs(P@w-w)),4e-15)
  self.assertLess(np.max(np.hypot(Q@w,U@w)),4e-15)
  self.assertTrue(.005<raw<.006)

 def test_native_bianchi_source_generates_pol_not_flrw_fake(self):
  for model,s in self.d["model_results"].items():
   frac=s["source_peak_polarization_fraction_scattered_in"]
   if model.startswith("S0_BI"):
    self.assertGreater(frac,1e-7)
    self.assertLess(frac,1e-6)
   else:
    self.assertLess(frac,3e-15)
   self.assertGreater(s["source_expected_scattering_events_per_H_sum"],9e-9)
   self.assertLess(s["source_expected_scattering_events_per_H_sum"],1e-8)
   self.assertLess(s["source_Thomson_sums_conserve_to"],2e-24)

 def test_coherency_referee_source_f64_parity(self):
  self.assertLess(self.a["max_relative_to_scattered_intensity_IQU_discrepancy"],2e-13)
  self.assertLess(self.a["max_flrw_source_polarization_fraction"],2e-15)
  self.assertEqual(self.a["original_Rust_feedback_from_Thomson"],"NOT_RUN")
  self.assertEqual(self.a["true_polarized_Boltzmann_trajectory"],"NOT_RUN")

 def test_predeclared_l2_three_percent_did_fail(self):
  # Preserve the actual negative numerical evidence rather than
  # silently relaxing the research criterion to a larger tolerance.
  self.assertEqual(self.s["predeclared_three_percent_method_gate"],"FAIL")
  fails=self.s["method_gate_failed_observations"]
  self.assertEqual(len(fails),1)
  self.assertEqual(fails[0]["source_model"],"S0_BI_ORIGINAL_HAT")
  self.assertEqual(fails[0]["step"],142)
  self.assertEqual(fails[0]["observable"],"number")
  self.assertAlmostEqual(fails[0]["relative_method_difference"],.04152277708926094,delta=1e-12)
  self.assertLess(fails[0]["absolute_method_difference"],2e-10)
  self.assertEqual(self.s["source_native_stage_count"],640)

 def test_bi_characteristic_representation_difference_and_flrw_zero(self):
  s=self.s["models"]
  self.assertTrue(.011<s["S0_BI_CHARACTERISTIC"]["max_number_relative_angular_method_difference"]<.013)
  self.assertGreater(s["S0_BI_ORIGINAL_HAT"]["max_number_relative_angular_method_difference"],.03)
  self.assertTrue(s["S0_FLRW_CHARACTERISTIC"]["at_step160_number_weighted_quadrupole"]<1e-14)
  self.assertTrue(s["S0_FLRW_ORIGINAL_HAT"]["at_step160_number_weighted_quadrupole"]<1e-14)

 def test_untouched_rei_source_and_DAG(self):
  self.assertFalse(self.d["source_original_F05_26event_gas_used"])
  self.assertFalse(self.d["original_Rust_native_source_modified"])
  self.assertFalse(self.d["original_Rust_native_gas_updated_with_Thomson_scattering"])
  self.assertTrue(self.d["original_single_scatter_first_order_source_only"])
  self.assertEqual(self.d["production"],"HOLD")
  self.assertEqual(self.d["original_REI_F08_paired_runtime_owner"],"HOLD")
  self.assertEqual(self.d["REI_canonical_DAG"],"28/88")
  self.assertEqual(self.d["REC_H5_physical_DAG"],"0/313")

 def test_independent_physics_audit_from_frozen_original_sources(self):
  with tempfile.TemporaryDirectory(prefix="rec199_cold_audit_") as scratch:
   dest=Path(scratch)/"audit.json"
   audited=auditor.audit(UNIT,UNIT/"results",dest)
   self.assertEqual(audited["total_ray_checks"],81920)
   self.assertEqual(audited["source_stage_count"],640)
   self.assertEqual(audited["original_REI_F08_paired_runtime"],"HOLD")

 def test_negative_original_ray_hash_tamper_fails_closed(self):
  q=UNIT/"source_inputs/F08_ORIGINAL_SOURCE_Q128.csv"
  with tempfile.TemporaryDirectory(prefix="rec199_bad_source_") as scratch:
   target=Path(scratch)/"source_inputs"
   target.mkdir()
   content=q.read_text()
   # Keep parsing valid but change the original ray coordinate SHA.
   (target/"F08_ORIGINAL_SOURCE_Q128.csv").write_text(content.replace("0.000", "0.001",1)
          if "0.000" in content else content+" ")
   with self.assertRaisesRegex(AssertionError,"ORIGINAL_RAY_SHA"):
    physics.source_q(target.parent)

if __name__=="__main__":
 unittest.main()
