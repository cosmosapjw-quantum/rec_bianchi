#!/usr/bin/env python3
"""Independent physics/scientific claim tests for original source event snapshot data."""
import hashlib,importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
import numpy as np

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT))
import audit_source_events as audit
import replay_source_events as replayer
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class OriginalSourceEventPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((UNIT/"results/SCIENCE_RESULT.json").read_text())
        cls.audit=json.loads((UNIT/"results/INDEPENDENT_AUDIT.json").read_text())
    def test_original_owner_identity(self):
        d=self.data
        self.assertEqual(d["source_original_tar_sha256"],replayer.TAR_SHA)
        self.assertEqual(d["source_original_kernel_sha256"],replayer.KERNEL_SHA)
        self.assertEqual(d["source_REI_owner_head"],replayer.REI_OWNER)
        self.assertEqual(d["source_REC_parent_head"],replayer.REC_PARENT)
    def test_original_alllane_historical_acceptance_only(self):
        d=self.data
        self.assertEqual(d["original_shape_audit_lanes"],3)
        self.assertEqual(d["newly_replayed_audit_lanes"],2)
        self.assertEqual(d["original_source_physical_realizations"],1)
        for lane in d["source_lane_results"].values():
            self.assertTrue(lane["original_source_acceptance"])
            self.assertEqual(set(lane["source_state_numeric_shas"]),{"128","160"})
            self.assertEqual(len(lane["original_events"]),4)
        self.assertEqual(d["cross_lane_event_fields"],"EXACT_NUMERIC_PAYLOAD_EQUAL")
    def test_frozen_owner_gate_and_DAG(self):
        d=self.data
        self.assertEqual(d["official_original_tick"],"160/131072")
        self.assertEqual(d["original_tick161"],"NOT_ACCEPTED")
        self.assertEqual(d["rei_canonical_DAG"],"28/88")
        self.assertEqual(d["rei_working_DAG"],"33/88")
        self.assertEqual(d["rec_h5_physical_DAG"],"0/313")
        self.assertEqual(d["production"],"HOLD")
        self.assertFalse(d["new_authoritative_owner_accepted_tick"])
    def test_184320_actual_original_event_rows(self):
        d=self.data
        self.assertEqual(d["physical_source_event_rows"],184320)
        p=UNIT/"results/ORIGINAL_F05_NATIVE_SOURCE_EVENTS_184320.csv.gz"
        self.assertEqual(sha(p),d["source_event_bytes_sha256"])
        self.assertEqual(self.audit["original_source_rows"],184320)
        self.assertEqual(self.audit["source_csv_sha256"],sha(p))
    def test_event_all_rows_and_thermal_ledger(self):
        a=self.audit
        self.assertEqual(a["source_cell_OTS_LEDGER"],"ALL_ROWS_ZERO_ENCLOSURE_PASS")
        self.assertEqual(a["source_cell_primary_OTS_single_count"],"ALL_ROWS_PASS")
        self.assertEqual(a["source_cell_thermal_product_identity"],"ALL_FINAL_ROWS_PASS")
        self.assertEqual(a["source_global_sums"],"ALL_EVENT_FIELDS_PASS")
        self.assertEqual(len(a["events"]),4)
    def test_original_charge_and_binding_stoichiometry(self):
        from types import SimpleNamespace
        lo=np.zeros((replayer.N,5,5),dtype=float)
        hi=lo.copy()
        lo[0,1,0]=2.5
        hi[0,1,0]=2.5
        event=SimpleNamespace(lo=lo,hi=hi)
        n=replayer.weighted_source(event,replayer.CHARGE)
        b=replayer.weighted_source(event,replayer.CHI*replayer.EV_ERG)
        h=replayer.weighted_source(event,replayer.HNUC)
        self.assertEqual(n[0][0],2.5)
        self.assertAlmostEqual(b[0][0],2.5*13.598434599702*replayer.EV_ERG)
        self.assertEqual(h[0][0],0)
    def test_no_double_count_and_BASS_HE_150_overlap(self):
        # BASS_HE #150 evaluated one source-conserving component-box
        # interior point on the same original tick160 26-event source.
        d=self.data["source_lane_results"][replayer.RECOMB]["original_events"]
        last=d[-1]
        self.assertEqual(last["interval_ticks"],[128,160])
        self.assertEqual(last["source_event_sample"],"final")
        self.assertLess(last["dot_B_lo_erg_s"],-7.694841173062561e39)
        self.assertGreater(last["dot_B_hi_erg_s"],-7.690602824089983e39)
        # Original thermal root evolves the total gas U; composition work
        # is a DECOMPOSITION, never a second source term added to it.
        self.assertIn("original_total_U_rhs_lo_erg_s",last)
        self.assertIn("temperature_only_U_term_lo_erg_s",last)
        self.assertIn("composition_U_work_lo_erg_s",last)
    def test_negative_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            d=dict(self.data)
            d["source_event_bytes_sha256"]="0"*64
            (root/"SCIENCE_RESULT.json").write_text(json.dumps(d)+"\n")
            os.symlink(UNIT/"results/ORIGINAL_F05_NATIVE_SOURCE_EVENTS_184320.csv.gz",
                       root/"ORIGINAL_F05_NATIVE_SOURCE_EVENTS_184320.csv.gz")
            with self.assertRaisesRegex(AssertionError,"SOURCE_DATA_SHA"):
                audit.audit(root,root/"audit.json")
if __name__=="__main__":unittest.main()
