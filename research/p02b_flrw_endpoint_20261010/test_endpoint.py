"""Focused input, mapping, and saved-endpoint checks; never start a history run."""
import json
import unittest

import run_endpoint as subject


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.contract = subject.load_contract()

    def test_original_archive_and_input_identity(self):
        members = subject.checked_members(subject.ROOT / self.contract["archive"], self.contract)
        self.assertEqual(subject.digest(members["HyRec/input.dat"]), self.contract["input_sha256"])

    def test_archive_mismatch_fails_before_materialization(self):
        wrong = dict(self.contract, archive_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "IMMUTABLE_ARCHIVE_SHA_MISMATCH"):
            subject.checked_members(subject.ROOT / wrong["archive"], wrong)

    def test_refinement_changes_only_dlna(self):
        members = subject.checked_members(subject.ROOT / self.contract["archive"], self.contract)
        original = members["HyRec/hyrec_params.h"]
        changed = subject.refinement_header(original)
        self.assertEqual(changed.replace(b"#define DLNA          4.245e-5", b"#define DLNA          8.49e-5"), original)
        with self.assertRaisesRegex(ValueError, "REFINEMENT_HEADER_CONTEXT_MISMATCH"):
            subject.refinement_header(changed)

    def saved(self, lane="baseline"):
        return json.loads((subject.HERE / "evidence" / (lane + ".json")).read_text())

    def test_saved_endpoint_mapping_cubic_and_refinement(self):
        baseline, refined = self.saved(), self.saved("refined")
        for endpoint in (baseline, refined):
            subject.validate_endpoint(endpoint, self.contract)
        differences = subject.compare_endpoints(baseline, refined, self.contract)
        self.assertLessEqual(max(differences.values()), 1e-4)

    def test_unresolved_helium_cannot_be_silently_relabelled(self):
        endpoint = self.saved()
        endpoint["endpoint"]["xHeII"] = 0.01
        with self.assertRaisesRegex(ValueError, "MAPPING_MISMATCH:xHeII"):
            subject.validate_endpoint(endpoint, self.contract)

    def test_mutated_export_is_rejected(self):
        endpoint = self.saved()
        endpoint["endpoint"]["Tm_K"] *= 1.001
        with self.assertRaisesRegex(ValueError, "CUBIC_EXPORT_MISMATCH:Tm_K"):
            subject.validate_endpoint(endpoint, self.contract)

    def test_refinement_failure_is_not_promoted(self):
        baseline, refined = self.saved(), self.saved("refined")
        refined["endpoint"]["xe_per_H"] *= 1.01
        with self.assertRaisesRegex(ValueError, "ENDPOINT_REFINEMENT_FAILED"):
            subject.compare_endpoints(baseline, refined, self.contract)


if __name__ == "__main__":
    unittest.main()
