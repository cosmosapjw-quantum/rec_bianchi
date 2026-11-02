#!/usr/bin/env python3
"""Scientific source-free and negative controls for accepted F05 + V2 candidate.

The original historical owner may remain HOLD; these tests do not promote 161.
"""
import hashlib,json,math,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import audit_thomson_geometry as audit

class OriginalF05CollisionBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=json.loads((ROOT/"results/SCIENCE_RESULT.json").read_text())
        cls.a=json.loads((ROOT/"results/INDEPENDENT_AUDIT.json").read_text())

    def test_exact_original_source_provenance(self):
        d=self.s
        self.assertEqual(d["owner_rec_parent_head"],
            "832551b69801eea008daf2c8cf19881c28649075")
        self.assertEqual(d["source_rei_original_head"],
            "fab9429140038974a98f3ad3212036b0227e600e")
        self.assertEqual(d["source_rei_v2_head"],
            "a09ea7b999c90a692de07c74352f835707e65838")
        self.assertEqual(d["v2_npz_sha256"],
            "c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823")
        self.assertEqual(d["accepted_original_ticks"],[0,64,128,160])

    def test_source_original_frozen_volume_and_positive_H(self):
        s=self.s
        self.assertTrue(s["native_source_frozen_volume_over_microtick"])
        self.assertTrue(all(abs(z-5.95)<3e-13 for z in
                             s["native_source_frozen_z_interval"]))
        hlo,hhi=s["native_source_H_s_inv_interval"]
        self.assertTrue(0<hlo<=hhi)
        self.assertLess(s["native_source_max_W_volume_relative_discrepancy"],5e-13)

    def test_conditional_expansion_exact_factor(self):
        s=self.s
        dt=s["source_microtick_seconds"]
        hlo,hhi=s["native_source_H_s_inv_interval"]
        f0,f1=s["expansion_volume_inverse_factor_interval"]
        self.assertAlmostEqual(f0,math.exp(-3*hhi*dt),delta=3e-15)
        self.assertAlmostEqual(f1,math.exp(-3*hlo*dt),delta=3e-15)
        self.assertTrue(0<f0<=f1<1)
        # Exactly zero expansion must preserve original frozen-volume kernel.
        self.assertEqual(math.exp(-3*0*dt),1.0)

    def test_all_native_physical_cells_and_sign_reversal(self):
        self.assertEqual(self.s["cells"],46080)
        self.assertEqual(self.a["cells_checked"],46080)
        cats=self.s["physical_sign_classes"]
        self.assertEqual(cats["native_chemistry"],
          {"definite_increase":60,"definite_decrease":40350,"undetermined":5670})
        self.assertEqual(cats["with_expansion"],
          {"definite_increase":0,"definite_decrease":43194,"undetermined":2886})
        self.assertEqual(self.s["chem_increase_to_geometry_decrease_strict_cells"],60)
        self.assertEqual(self.a["strict_sign_reversals"],60)

    def test_three_volume_weighted_rate_intervals(self):
        d=self.s
        frozen=d["volume_weighted_Gamma160_s_inv"]
        chem=d["volume_weighted_Gamma161_frozen_s_inv"]
        expand=d["volume_weighted_Gamma161_expanded_s_inv"]
        self.assertTrue(all(0<a<=b for a,b in (frozen,chem,expand)))
        self.assertLess(chem[1],frozen[0])
        self.assertLess(expand[1],chem[0])
        self.assertLess(expand[1],frozen[0])

    def test_source_free_full_row_audit_and_sha(self):
        p=ROOT/"results/ORIGINAL_F05_V2_THOMSON_GEOMETRY_46080.csv.gz"
        self.assertEqual(audit.digest(p),self.s["source_csv_sha256"])
        self.assertEqual(self.a["data_sha256"],self.s["source_csv_sha256"])
        self.assertEqual(self.a["full_cell_physical_rate_and_geometry"],"PASS")
        self.assertEqual(self.a["additive_signed_collision_decomposition"],"PASS")

    def test_official_owner_and_observable_claims_remain_hold(self):
        s=self.s
        self.assertFalse(s["owner_accepted_tick161"])
        self.assertFalse(s["source_original_rei_modified"])
        self.assertFalse(s["source_original_26event_reintegrated"])
        self.assertEqual(s["REI_canonical_DAG"],"28/88")
        self.assertEqual(s["REC_H5_physical_DAG"],"0/313")
        self.assertEqual(s["production"],"HOLD")
        self.assertEqual(self.a["actual_Bianchi_null_ray_or_observed_CMB"],"NOT_COMPUTED")

    def test_negative_source_digest_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="rec197_badsha_") as tmp:
            folder=Path(tmp);altered=dict(self.s)
            altered["source_csv_sha256"]="0"*64
            (folder/"SCIENCE_RESULT.json").write_text(json.dumps(altered)+"\n")
            os.symlink(ROOT/"results/ORIGINAL_F05_V2_THOMSON_GEOMETRY_46080.csv.gz",
                       folder/"ORIGINAL_F05_V2_THOMSON_GEOMETRY_46080.csv.gz")
            with self.assertRaisesRegex(AssertionError,"SCIENTIFIC_SOURCE_CSV_HASH"):
                audit.audit(folder,folder/"SHOULD_NOT_EXIST.json")

if __name__=="__main__":
    unittest.main()
