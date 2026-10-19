"""Runner resource regressions; no primordial integration is performed."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_r3o_h4_start as runner


class H4ResourceTests(unittest.TestCase):
    def test_fast_child_preserves_success_and_command_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)/"fast"
            command = [sys.executable, "-B", "-c", "print('complete')"]
            result = runner.Budget(2., 2.).run(command, ROOT, prefix)
            self.assertEqual(result["returncode"], 0)
            self.assertTrue(result["process_group_owned"])
            self.assertIsNone(result["failure"])
            self.assertEqual(json.loads(prefix.with_suffix(".json").read_text()), result)
            self.assertEqual(prefix.with_suffix(".stdout").read_text(), "complete\n")

    @unittest.skipUnless(sys.platform == "linux", "process tree probe uses Linux /proc")
    def test_timeout_stops_descendant_and_preserves_failed_receipt(self):
        child_pid = None
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)/"timeout"
            command = [sys.executable, "-B", "-c",
                       "import subprocess,sys,time; "
                       "p=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(20)']); "
                       "print(p.pid,flush=True); time.sleep(20)"]
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    runner.Budget(2., .6).run(command, ROOT, prefix)
                child_pid = int(prefix.with_suffix(".stdout").read_text().strip())
                record = json.loads(prefix.with_suffix(".json").read_text())
                self.assertEqual(record["returncode"], -signal.SIGKILL)
                self.assertEqual(record["failure"]["type"], "TimeoutExpired")
                self.assertTrue(record["process_group_owned"])
                state = None
                for _ in range(50):
                    try:
                        state = Path(f"/proc/{child_pid}/stat").read_text().rsplit(") ", 1)[1].split()[0]
                    except FileNotFoundError:
                        state = None
                    if state in (None, "Z", "X"):
                        break
                    time.sleep(.005)
                self.assertIn(state, (None, "Z", "X"), "descendant still runs after timeout")
            finally:
                # A failed regression must not leave the synthetic child alive.
                if child_pid is not None:
                    try:
                        os.kill(child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_real_main_admission_includes_final_artifact_hash_work(self):
        # Execute main/finally, replacing only scientific work, I/O and clocks.
        # The accounting jump happens in the last required artifact hash.
        for overrun in (None, "cpu", "wall"):
            with self.subTest(overrun=overrun):
                cpu = [0.]; wall = [0.]; zip_calls = [0]; snapshots = []
                ev = MagicMock(name="memory_evidence")
                ev.resolve.return_value = ev
                artifact = MagicMock(name="controlled_artifact")
                artifact.name = "controlled.data"
                artifact.is_file.return_value = True
                artifact.stat.return_value = SimpleNamespace(st_size=1)
                ev.iterdir.return_value = (artifact,)
                args = SimpleNamespace(evidence_dir=ev, mode="helium", steps=8,
                                       cpu_seconds=1, wall_seconds=2)
                helium = SimpleNamespace(**{k: np.zeros(1) for k in (
                    "iz", "z", "xe", "xHII", "xHeI", "xHeII", "xHeIII", "Tm_K",
                    "helium_rhs_dln_a", "stage", "update_method", "post_saha")})

                def controlled_sha(path):
                    if path == runner.ZIP:
                        zip_calls[0] += 1
                    if path is artifact:
                        self.assertGreaterEqual(zip_calls[0], 2)
                        cpu[0] = 1.25 if overrun == "cpu" else .25
                        wall[0] = 2.25 if overrun == "wall" else .25
                    return runner.h4.PINNED_ZIP_SHA256

                with contextlib.ExitStack() as stack:
                    changes = [
                        (runner, "H4_SOURCE_FILES", ()), (runner, "DEPENDENCIES", ()),
                        (runner, "sha", controlled_sha),
                        (runner, "json_new", lambda p, value: snapshots.append(copy.deepcopy(value))),
                        (runner.argparse.ArgumentParser, "parse_args", lambda _: args),
                        (runner.Budget, "cpu", staticmethod(lambda: cpu[0])),
                        (runner.Budget, "run", lambda *a, **kw: {"returncode": 0}),
                        (runner.time, "monotonic", lambda: wall[0]),
                        (runner.os, "sched_getaffinity", lambda _: set()),
                        (runner.resource, "setrlimit", lambda *a: None),
                        (runner.signal, "signal", lambda *a: None),
                        (runner.signal, "alarm", lambda *a: None),
                        (runner, "prepare_source", lambda *a: (Path("/controlled/source"),
                                                              {"modified_member_sha256": {}})),
                        (runner.subprocess, "run", lambda *a, **kw: SimpleNamespace(stdout="controlled compiler\n")),
                        (runner, "parse_native", lambda *a: {"memories": {-1: np.zeros((2, 2))}}),
                        (runner.h4, "integrate_helium_stages", lambda *a, **kw: helium),
                        (runner.h4, "source_native_derivative_seeds", lambda *a: np.zeros((2, 2))),
                        (runner, "save_npz_new", lambda *a: "controlled_no_file"),
                        (runner, "compare_helium", lambda *a: {"status": "CONTROL_ONLY"}),
                    ]
                    for target, name, value in changes:
                        stack.enter_context(patch.object(target, name, value))
                    with contextlib.redirect_stdout(io.StringIO()):
                        code = runner.main()
                report = snapshots[-1]
                self.assertIn("controlled.data", report["artifacts"])
                self.assertEqual(report["resources"]["cpu_s_including_children"], cpu[0])
                self.assertEqual(report["resources"]["wall_s"], wall[0])
                if overrun is None:
                    self.assertEqual(code, 0)
                    self.assertEqual(report["status"], "PASS_SAME_H_HELIUM")
                else:
                    self.assertNotEqual(code, 0)
                    self.assertEqual(report["status"], "FAIL_RESOURCE_LIMIT")
                    self.assertIn("CPU" if overrun == "cpu" else "WALL",
                                  report["resource_failure"]["message"])


if __name__ == "__main__":
    unittest.main()
