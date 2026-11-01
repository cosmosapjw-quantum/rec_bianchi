#!/usr/bin/env python3
"""Finite and provenance-scoped tests of original F05 4-epoch material science."""
import hashlib,json,os,sys,tempfile,unittest
from pathlib import Path

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT))
import audit_energy
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class TestOriginalTrajectory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((UNIT/"results/SCIENCE_RESULT.json").read_text())
        cls.audit=json.loads((UNIT/"results/INDEPENDENT_AUDIT.json").read_text())

    def test_original_source_identity(self):
        d=self.data
        self.assertEqual(d["original_tar_sha256"],
            "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(d["source_REI_PR363_sha"],
            "abf83d4d883d5f311426b7f02cb001e70138ceb4")
        self.assertEqual(d["source_REC_parent_sha"],
            "b1f3dd6516539fc6b98a131528f42d8076b41fa3")
        self.assertEqual(d["physical_epochs"],[0,64,128,160])

    def test_exact_historical_replay_state(self):
        d=self.data
        self.assertEqual(d["replayed_128_state_sha256"],
            "bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6")
        self.assertEqual(d["replayed_160_state_sha256"],
            "74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")
        self.assertEqual(len(d["original_maps"]),2)
        for r in d["original_maps"]:
            self.assertEqual(r["computed_sha256"],r["historical_sha256"])
            self.assertEqual(r["three_source_maps_certified"],[True,True,True])
            self.assertTrue(r["all_14_ledgers_include_zero"])
            self.assertEqual(r["table_event_count"],0)
            self.assertLess(max(r["local_error_bounds"].values()),2e-4)
            self.assertLess(max(r["source_interval_widths"].values()),2e-3)

    def test_real_physical_energy_changes(self):
        for r in self.data["interval_physics"]:
            self.assertLess(r["delta_Ne"][1],0)
            self.assertLess(r["delta_B"][1],0)
            self.assertLess(r["delta_U"][1],0)
            self.assertEqual(sum(r["electron_sign_class"].values()),46080)

    def test_strict_chemical_thermal_separation(self):
        rows=self.audit["intervals"]
        for a,b in zip(rows,rows[1:]):
            self.assertGreater(b["source_secular_thermal_cooling_rate_erg_s"][0],
                               a["source_secular_thermal_cooling_rate_erg_s"][1])
            self.assertLess(b["source_secular_binding_discharge_rate_erg_s"][1],
                            a["source_secular_binding_discharge_rate_erg_s"][0])

    def test_full_184320_source_rows_identity(self):
        p=UNIT/"results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz"
        self.assertEqual(sha(p),self.data["csv_sha256"])
        self.assertEqual(self.audit["cell_rows_checked"],184320)
        self.assertEqual(self.audit["source_csv_sha256"],sha(p))

    def test_no_f05_canonical_promotion(self):
        d=self.data
        self.assertEqual(d["original_accepted_tick"],"160/131072")
        self.assertEqual(d["new_owner_accepted_ticks"],0)
        self.assertEqual(d["DAG_REI_canonical"],"28/88")
        self.assertEqual(d["DAG_REC_H5"],"0/313")
        self.assertEqual(d["f05_tick161"],"NOT_ACCEPTED")
        self.assertEqual(d["production"],"HOLD")

    def test_negative_source_checksum_failure(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)
            modified=dict(self.data)
            modified["csv_sha256"]="0"*64
            (dest/"SCIENCE_RESULT.json").write_text(json.dumps(modified)+"\n")
            os.symlink(UNIT/"results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz",
                       dest/"ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz")
            with self.assertRaisesRegex(AssertionError,"CSV_BYTE_IDENTITY"):
                audit_energy.audit(dest,dest/"unexpected.json")

if __name__=="__main__":unittest.main()
