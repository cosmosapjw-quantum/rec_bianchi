"""Archive handling tests with labelled synthetic bytes; production pins fixed."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from extract_r3l_reviewed_u5 import extract_checkpoint


class RecoveryTests(unittest.TestCase):
    def test_receipt_error_does_not_mask_checkpoint_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p, raw, cp = self.make_raw(d)
            real_write = Path.write_text
            def fail_receipt(path, *a, **kw):
                if path.name == "RECOVERY_RECEIPT.json": raise OSError("receipt unavailable")
                return real_write(path, *a, **kw)
            with patch.object(Path, "write_text", fail_receipt), self.assertRaisesRegex(ValueError, "CHECKPOINT_SHA") as caught:
                extract_checkpoint(p, Path(d) / "out", expected_raw_sha=raw, expected_checkpoint_sha="0" * 64)
            self.assertIn("Secondary recovery receipt failure", caught.exception.__notes__[0])

    def make_raw(self, root, *, name="run/python_u5_thermal.npz", data=b"synthetic-fixture", link=False, duplicate=False):
        path = Path(root) / "raw.tar.gz"
        with tarfile.open(path, "w:gz") as t:
            m = tarfile.TarInfo(name)
            if link:
                m.type = tarfile.SYMTYPE; m.linkname = "elsewhere"; t.addfile(m)
            else:
                m.size = len(data); t.addfile(m, io.BytesIO(data))
                if duplicate: t.addfile(m, io.BytesIO(data))
        return path, hashlib.sha256(path.read_bytes()).hexdigest(), hashlib.sha256(data).hexdigest()

    def run_fixture(self, root, **kwargs):
        p, raw, cp = self.make_raw(root, **kwargs)
        return extract_checkpoint(p, Path(root) / "out", expected_raw_sha=raw, expected_checkpoint_sha=cp)

    def test_capsule_member_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_fixture(d)
            self.assertEqual(r["status"], "PASS_CHECKPOINT_CAPSULE_ONLY")
            with zipfile.ZipFile(Path(d) / "out" / r["capsule"]) as z:
                self.assertEqual(set(z.namelist()), {"python_u5_thermal.npz", "MANIFEST.json"})
                self.assertEqual(z.read("python_u5_thermal.npz"), b"synthetic-fixture")
            self.assertEqual(r["new_integrations"], 0)

    def test_raw_hash_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as d:
            p, raw, cp = self.make_raw(d)
            with self.assertRaisesRegex(ValueError, "RAW_SHA"):
                extract_checkpoint(p, Path(d) / "out", expected_raw_sha="0" * 64, expected_checkpoint_sha=cp)
            self.assertFalse((Path(d) / "out").exists())

    def test_checkpoint_hash_failure_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p, raw, cp = self.make_raw(d)
            with self.assertRaisesRegex(ValueError, "CHECKPOINT_SHA"):
                extract_checkpoint(p, Path(d) / "out", expected_raw_sha=raw, expected_checkpoint_sha="0" * 64)
            r = json.loads((Path(d) / "out/RECOVERY_RECEIPT.json").read_text())
            self.assertEqual(r["status"], "FAIL")
            self.assertIsNotNone(r["first_failure"])

    def test_unsafe_parent_path(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "UNSAFE"):
                self.run_fixture(d, name="../python_u5_thermal.npz")

    def test_absolute_path(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "UNSAFE"):
                self.run_fixture(d, name="/python_u5_thermal.npz")

    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "NOT_REGULAR"):
                self.run_fixture(d, link=True)

    def test_duplicate_members_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "NOT_UNIQUE"):
                self.run_fixture(d, duplicate=True)

    def test_missing_member_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "NOT_UNIQUE"):
                self.run_fixture(d, name="other.txt")

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p, raw, cp = self.make_raw(d)
            out = Path(d) / "out"; out.mkdir(); (out / "keep").write_text("unchanged")
            with self.assertRaises(FileExistsError):
                extract_checkpoint(p, out, expected_raw_sha=raw, expected_checkpoint_sha=cp)
            self.assertEqual((out / "keep").read_text(), "unchanged")

    def test_size_guard_before_extraction(self):
        with tempfile.TemporaryDirectory() as d:
            p, raw, cp = self.make_raw(d)
            with self.assertRaisesRegex(ValueError, "TRANSFER_SIZE"):
                extract_checkpoint(p, Path(d) / "out", expected_raw_sha=raw, expected_checkpoint_sha=cp, transfer_limit=65536)
            self.assertFalse((Path(d) / "out/python_u5_thermal.npz").exists())


if __name__ == "__main__":
    unittest.main()
