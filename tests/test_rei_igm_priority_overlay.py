"""Bounded regression: refuse fabricated research-progress or dependency claims."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("overlay_guard", ROOT / "scripts" / "verify_rei_igm_priority_overlay.py")
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
BASE = json.loads((ROOT / "docs" / "REI_IGM_PRIORITY_OVERLAY_20261101.json").read_text(encoding="utf-8"))


class OverlayContractTests(unittest.TestCase):
    def test_valid_snapshot_passes(self):
        self.assertEqual(GUARD.validate(BASE), [])

    def test_canonical_promotion_rejected(self):
        x = copy.deepcopy(BASE)
        x["interpretation"]["newly_admitted_central_nodes"] = 1
        self.assertTrue(GUARD.validate(x))

    def test_original_35hz_and_no_merge_persist(self):
        x = copy.deepcopy(BASE)
        x["preserved_controls"]["original_35hz"] = "PASS8/8"
        x["preserved_controls"]["no_merge"] = False
        self.assertGreaterEqual(len(GUARD.validate(x)), 2)

    def test_hd_not_universal_precondition(self):
        x = copy.deepcopy(BASE)
        target = next(n for n in x["nodes"] if n["id"] == "REI_F08_PAIRED_S0_HISTORY")
        target["requires"].append("REC_HD_SPECTROSCOPY_AUX")
        self.assertTrue(any("HD incorrectly" in e for e in GUARD.validate(x)))

    def test_no_invented_rec_blocker_on_first_s0_interval(self):
        x = copy.deepcopy(BASE)
        target = next(n for n in x["nodes"] if n["id"] == "REI_FIRST_COUPLED_INTERVAL")
        target["requires"].append("REC_REI_HISTORY_CONSUMER_BINDING")
        self.assertTrue(any("manufactured" in e for e in GUARD.validate(x)))

    def test_cycles_rejected(self):
        x = copy.deepcopy(BASE)
        target = next(n for n in x["nodes"] if n["id"] == "REI_FIRST_COUPLED_INTERVAL")
        target["requires"].append("REI_F08_PAIRED_S0_HISTORY")
        self.assertTrue(any("cycle" in e for e in GUARD.validate(x)))

    def test_missing_source_identity_rejected(self):
        x = copy.deepcopy(BASE)
        x["observed_sources"]["rei_program_source_commit"] = ""
        self.assertTrue(any("missing immutable identity" in e for e in GUARD.validate(x)))

    def test_only_selected_next_with_auto_next_false(self):
        x = copy.deepcopy(BASE)
        x["next_candidate_only"] = "REC_HD_SPECTROSCOPY_AUX"
        x["preserved_controls"]["auto_next_node"] = True
        self.assertGreaterEqual(len(GUARD.validate(x)), 2)


if __name__ == "__main__":
    unittest.main()
