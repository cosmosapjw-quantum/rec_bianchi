"""Bounded execution/storage contracts; no synthetic source is a physics oracle."""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sys
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from r3l_u6_cost import (PhaseLedger, HistoryNumpyProxy, instrument_verifier,
                          write_stored_history)
from run_r3l_u6_profiled import execute, step_count, bind_profile_source, EXTRA_FILES


def payload():
    # Signed zero, subnormals, distinct neighbors and both signs are preserved.
    bits = np.array([0, 1 << 63, 1, 0x3ff0000000000000,
                     0x3ff0000000000001, 0xbff0000000000000], dtype=np.uint64)
    return {"states_json": np.array(['{"iz":1}', '{"iz":2}']),
            "steps_json": np.array(['{"input_iz":1}']),
            "virtual_out": np.asfortranarray(bits.view(np.float64).reshape(2, 3)),
            "average_virtual": bits.view(np.float64).reshape(2, 3),
            "lyman_out": np.arange(9., dtype=np.float64).reshape(3, 3)}


def npy_members(path):
    with zipfile.ZipFile(path) as z:
        return {name: z.read(name) for name in z.namelist()}


class FakeClock:
    def __init__(self):
        self.value = dict(parent_cpu_s=0., children_cpu_s=0., wall_s=0.)
    def __call__(self):
        return self.value.copy()
    def advance(self, parent=0., child=0., wall=0.):
        self.value["parent_cpu_s"] += parent
        self.value["children_cpu_s"] += child
        self.value["wall_s"] += wall


@contextmanager
def ledger_file(folder, clock=None):
    with (Path(folder) / "phases.jsonl").open("x") as stream:
        yield PhaseLedger(stream, **({"clock": clock} if clock else {}))


def fake_verifier():
    identity = object()
    verifier = SimpleNamespace(CPU_CAP=60, WALL_CAP=180, np=np)
    for name in ("verify_source_closure", "load_frozen_checkpoint", "safe_extract_source",
                 "make_hmla_source", "CombinedOracle", "compare_native_stream",
                 "check_one_source", "causal_link_count", "_run",
                 "integrate_u6_rt_boundary"):
        setattr(verifier, name, lambda *a, **kw: identity)
    return verifier, identity


class LosslessStorageTests(unittest.TestCase):
    def test_stored_and_compressed_npy_members_identical(self):
        with tempfile.TemporaryDirectory() as d:
            arrays = payload()
            before = {k: v.tobytes() for k, v in arrays.items()}
            a, b = Path(d) / "stored.npz", Path(d) / "compressed.npz"
            write_stored_history(a, **arrays)
            np.savez_compressed(b, **arrays)
            self.assertEqual(npy_members(a), npy_members(b))
            with zipfile.ZipFile(a) as z:
                self.assertTrue(all(i.compress_type == zipfile.ZIP_STORED for i in z.infolist()))
            with np.load(a, allow_pickle=False) as restored:
                for key, value in arrays.items():
                    self.assertEqual(restored[key].dtype, value.dtype)
                    self.assertEqual(restored[key].shape, value.shape)
                    self.assertEqual(restored[key].tobytes(), value.tobytes())
            self.assertEqual(before, {k: v.tobytes() for k, v in arrays.items()})

    def test_reject_object_before_create(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.npz"
            a = payload(); a["states_json"] = np.array([{}], dtype=object)
            with self.assertRaisesRegex(ValueError, "OBJECT_DTYPE"):
                write_stored_history(p, **a)
            self.assertFalse(p.exists())

    def test_reject_missing_field(self):
        with tempfile.TemporaryDirectory() as d:
            a = payload(); a.pop("lyman_out")
            with self.assertRaisesRegex(ValueError, "HISTORY_FIELDS"):
                write_stored_history(Path(d) / "bad.npz", **a)

    def test_reject_extra_field(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "HISTORY_FIELDS"):
                write_stored_history(Path(d) / "bad.npz", extra=np.ones(1), **payload())

    def test_create_only_preserves_existing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "exists.npz"; p.write_bytes(b"preserve")
            with self.assertRaises(FileExistsError):
                write_stored_history(p, **payload())
            self.assertEqual(p.read_bytes(), b"preserve")

    def test_requires_exact_npz_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "NPZ_SUFFIX"):
                write_stored_history(Path(d) / "x", **payload())

    def test_proxy_scoped_and_modes(self):
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            original = np.savez_compressed
            for mode in ("compressed", "stored"):
                proxy = HistoryNumpyProxy(np, ledger, mode)
                self.assertIs(proxy.asarray, np.asarray)
                proxy.savez_compressed(Path(d) / (mode + ".npz"), **payload())
                self.assertIs(np.savez_compressed, original)
            self.assertEqual(npy_members(Path(d) / "stored.npz"),
                             npy_members(Path(d) / "compressed.npz"))
            self.assertEqual(ledger.summary()["phases"]["history_write"]["calls"], 2)

    def test_proxy_rejects_positional_payloads(self):
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            with self.assertRaisesRegex(ValueError, "NAMED_U6"):
                HistoryNumpyProxy(np, ledger, "stored").savez_compressed(Path(d) / "x.npz", np.zeros(2))


class ClockTests(unittest.TestCase):
    def test_bad_end_clock_does_not_replace_original_failure(self):
        c = FakeClock()
        with tempfile.TemporaryDirectory() as d, ledger_file(d, c) as ledger:
            original = RuntimeError("source failure")
            with self.assertRaises(RuntimeError) as caught:
                with ledger.measure("source"):
                    c.advance(parent=1, wall=1)
                    ledger.clock = lambda: dict(parent_cpu_s=-1., children_cpu_s=0., wall_s=0.)
                    raise original
            ledger.clock = c
            self.assertIs(caught.exception, original)
            self.assertEqual(ledger.stack, [])
            self.assertEqual(ledger.summary()["accounting_status"], "INVALID_PROFILING_ERROR")
            self.assertEqual(ledger.profiling_errors[0]["type"], "ValueError")

    def test_failed_end_event_does_not_replace_system_exit(self):
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            real_emit = ledger.emit
            def fail_end(row):
                if row["event"] == "end": raise OSError("journal unavailable")
                real_emit(row)
            original = SystemExit(2)
            with patch.object(ledger, "emit", fail_end), self.assertRaises(SystemExit) as caught:
                with ledger.measure("source"):
                    raise original
            self.assertIs(caught.exception, original)
            self.assertEqual(ledger.stack, [])
            self.assertEqual(ledger.profiling_errors[0]["type"], "OSError")

    def test_nested_exclusive_accounting(self):
        c = FakeClock()
        with tempfile.TemporaryDirectory() as d, ledger_file(d, c) as ledger:
            with ledger.measure("outer"):
                c.advance(1, 0, 2)
                with ledger.measure("inner"):
                    c.advance(3, 2, 5)
                c.advance(4, 1, 6)
            s = ledger.summary()
            self.assertEqual(s["phases"]["outer"]["inclusive"],
                             dict(parent_cpu_s=8., children_cpu_s=3., wall_s=13.))
            self.assertEqual(s["phases"]["outer"]["exclusive"],
                             dict(parent_cpu_s=5., children_cpu_s=1., wall_s=8.))
            self.assertEqual(s["process_tree_cpu_s"], 11.)
            self.assertTrue(all(v == 0 for v in s["unattributed"].values()))

    def test_exception_preserved_and_recorded(self):
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            failure = SystemExit(7)
            with self.assertRaises(SystemExit) as caught:
                with ledger.measure("failure"):
                    raise failure
            self.assertIs(caught.exception, failure)
            self.assertEqual(ledger.summary()["phases"]["failure"]["failed_calls"], 1)
            rows = [json.loads(s) for s in (Path(d) / "phases.jsonl").read_text().splitlines()]
            self.assertEqual(rows[-1]["failure"]["type"], "SystemExit")

    def test_repeated_hot_phase_aggregates_without_events(self):
        c = FakeClock()
        with tempfile.TemporaryDirectory() as d, ledger_file(d, c) as ledger:
            for _ in range(4):
                with ledger.measure("hot", durable=False):
                    c.advance(parent=2, wall=3)
            s = ledger.summary()
            self.assertEqual(s["phases"]["hot"]["calls"], 4)
            self.assertEqual(s["process_tree_cpu_s"], 8.)
            self.assertEqual((Path(d) / "phases.jsonl").read_text(), "")

    def test_running_phase_cannot_finalize(self):
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            with ledger.measure("open"):
                with self.assertRaisesRegex(RuntimeError, "STILL_RUNNING"):
                    ledger.summary()

    def test_wrapper_returns_exact_object(self):
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            value = object()
            self.assertIs(ledger.wrap("identity", lambda x: x)(value), value)


class InjectionTests(unittest.TestCase):
    def test_restores_all_bindings_on_success(self):
        v, sentinel = fake_verifier(); originals = vars(v).copy()
        owned = lambda *a, **k: sentinel
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            with instrument_verifier(v, owned, ledger, container="stored"):
                self.assertIs(v.integrate_u6_rt_boundary(object()), sentinel)
                self.assertIs(v.verify_source_closure(object()), sentinel)
                self.assertIs(v._run([], Path(d), Path(d) / "native_oracle_stdout.csv", Path(d) / "stderr"), sentinel)
            self.assertEqual(vars(v), originals)

    def test_restores_bindings_on_failure(self):
        v, _ = fake_verifier(); originals = vars(v).copy()
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            with self.assertRaisesRegex(RuntimeError, "first failure"):
                with instrument_verifier(v, lambda: None, ledger):
                    raise RuntimeError("first failure")
            self.assertEqual(vars(v), originals)

    def test_invalid_container_restores_partial_setup(self):
        v, _ = fake_verifier(); originals = vars(v).copy()
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            with self.assertRaisesRegex(ValueError, "HISTORY_CONTAINER"):
                with instrument_verifier(v, lambda: None, ledger, container="invalid"):
                    self.fail("must reject")
            self.assertEqual(vars(v), originals)

    def test_caps_cannot_drift(self):
        for key, bad in (("CPU_CAP", 61), ("WALL_CAP", 181)):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
                v, _ = fake_verifier(); setattr(v, key, bad); original = vars(v).copy()
                with self.assertRaisesRegex(ValueError, "RESOURCE_CAP_DRIFT"):
                    with instrument_verifier(v, lambda: None, ledger):
                        self.fail("must reject")
                self.assertEqual(vars(v), original)

    def test_callbacks_forward_exact_args_and_return(self):
        v, _ = fake_verifier(); source = object(); state = object(); seen = []
        def observer(*args):
            seen.append(args); return state
        def owner(cp, src, *, observer):
            self.assertIs(cp, state); self.assertIs(src, source)
            self.assertIs(observer(7, state, source), state)
            return source
        with tempfile.TemporaryDirectory() as d, ledger_file(d) as ledger:
            with instrument_verifier(v, owner, ledger):
                self.assertIs(v.integrate_u6_rt_boundary(state, source, observer=observer), source)
            self.assertEqual(seen, [(7, state, source)])
            s = ledger.summary()
            self.assertEqual(s["phases"]["callback_observer"]["calls"], 1)
            self.assertLessEqual(s["exclusive_sum"]["parent_cpu_s"], s["measured_interval"]["parent_cpu_s"] + 1.e-9)


class LauncherTests(unittest.TestCase):
    def test_malformed_receipt_keeps_original_failure(self):
        with tempfile.TemporaryDirectory() as d:
            v, _ = fake_verifier(); ev = Path(d) / "run"; original = SystemExit(2)
            before = sys.argv[:]
            def main():
                ev.mkdir(); (ev / "verification.json").write_text("{incomplete")
                raise original
            v.main = main; bindings = vars(v).copy()
            with self.assertRaises(SystemExit) as caught:
                execute(v, lambda: None, checkpoint="x", evidence=ev, steps=3,
                        binding={}, allocation_id="test", container="stored")
            self.assertIs(caught.exception, original)
            self.assertEqual(sys.argv, before); self.assertEqual(vars(v), bindings)
            self.assertEqual((ev / "verification.json").read_text(), "{incomplete")
            report = json.loads((Path(d) / "run.r3l_profile.json").read_text())
            self.assertEqual(report["closeout_errors"][0]["type"], "JSONDecodeError")
            self.assertEqual(report["verification"]["read_status"], "UNREADABLE_PRESERVED")

    def test_profile_write_failure_keeps_original_failure(self):
        with tempfile.TemporaryDirectory() as d:
            v, _ = fake_verifier(); original = SystemExit(2); real_open = Path.open
            def main(): raise original
            def guarded_open(path, *args, **kwargs):
                if path.name.endswith(".r3l_profile.json"): raise OSError("profile write unavailable")
                return real_open(path, *args, **kwargs)
            v.main = main; bindings = vars(v).copy(); before = sys.argv[:]
            with patch.object(Path, "open", guarded_open), self.assertRaises(SystemExit) as caught:
                execute(v, lambda: None, checkpoint="x", evidence=Path(d) / "run", steps=3,
                        binding={}, allocation_id="test", container="stored")
            self.assertIs(caught.exception, original)
            self.assertEqual(vars(v), bindings); self.assertEqual(sys.argv, before)
            rows = [json.loads(s) for s in (Path(d) / "run.r3l_phases.jsonl").read_text().splitlines()]
            self.assertEqual(rows[-1]["closeout_errors"][0]["stage"], "profile_save")

    def test_successful_verifier_with_profile_error_still_fails_profile(self):
        with tempfile.TemporaryDirectory() as d:
            v, _ = fake_verifier(); ev = Path(d) / "run"
            def main():
                ev.mkdir(); (ev / "verification.json").write_text("{incomplete")
            v.main = main
            with self.assertRaises(json.JSONDecodeError):
                execute(v, lambda: None, checkpoint="x", evidence=ev, steps=3,
                        binding={}, allocation_id="test", container="stored")

    def setup_git(self, root, include_adapters):
        from run_r3j_u6_owned import EXTRA_FILES as inherited
        for name in set(inherited) | set(EXTRA_FILES):
            p = Path(root) / name; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("synthetic source-binding fixture\n")
        def git(*args):
            return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                  text=True, check=True).stdout.strip()
        git("init", "-q")
        git("add", "--", *(list(inherited) + (list(EXTRA_FILES) if include_adapters else [])))
        git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        return git("rev-parse", "HEAD")

    def test_committed_profile_sources_are_bound(self):
        with tempfile.TemporaryDirectory() as d:
            head = self.setup_git(d, True)
            binding = bind_profile_source(d, head)
            self.assertEqual(binding["commit"], head)
            self.assertTrue(set(EXTRA_FILES) <= set(binding["additional_source_sha256"]))

    def test_untracked_profile_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            head = self.setup_git(d, False)
            with self.assertRaises(subprocess.CalledProcessError):
                bind_profile_source(d, head)

    def test_wrong_source_commit_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_git(d, True)
            with self.assertRaisesRegex(ValueError, "SOURCE_COMMIT_MISMATCH"):
                bind_profile_source(d, "0" * 40)

    def test_step_modes(self):
        self.assertEqual(step_count("smoke", 128), 3)
        self.assertEqual(step_count("pilot", 16), 16)
        self.assertEqual(step_count("full", 128), 5210)

    def test_invalid_steps_and_mode(self):
        for bad in (True, 0, -1, 129, 1.5, "3"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                step_count("pilot", bad)
        with self.assertRaises(ValueError):
            step_count("other", 3)

    def test_create_only_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            ev = Path(d) / "existing"; ev.mkdir()
            v, _ = fake_verifier()
            with self.assertRaises(FileExistsError):
                execute(v, lambda: None, checkpoint="x", evidence=ev, steps=3,
                        binding={}, allocation_id="test", container="stored")

    def test_failed_verifier_preserves_exception_argv_and_summary(self):
        with tempfile.TemporaryDirectory() as d:
            v, _ = fake_verifier(); saved = vars(v).copy(); before = sys.argv[:]
            def fail():
                self.assertEqual(sys.argv[-1], "3")
                raise SystemExit(2)
            v.main = fail; saved["main"] = fail
            with self.assertRaises(SystemExit) as caught:
                execute(v, lambda: None, checkpoint="x", evidence=Path(d) / "run", steps=3,
                        binding={"commit": "test"}, allocation_id="test", container="stored")
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(sys.argv, before); self.assertEqual(vars(v), saved)
            r = json.loads((Path(d) / "run.r3l_profile.json").read_text())
            self.assertEqual(r["execution_status"], "failed")
            self.assertEqual(r["run_error"]["type"], "SystemExit")
            self.assertEqual(r["scientific_status"], "READ_ORIGINAL_VERIFICATION_RECEIPT")

    def test_returned_receipt_is_linked_without_promoting_science(self):
        with tempfile.TemporaryDirectory() as d:
            v, _ = fake_verifier(); ev = Path(d) / "run"
            def main():
                ev.mkdir()
                v.np.savez_compressed(ev / "python_u6_rt.npz", **payload())
                (ev / "verification.json").write_text(json.dumps({"status": "SMOKE_ONLY",
                    "python_result": {"steps": 3}, "same_h_parity": {"status": "PASS_PENDING_REVIEW"}}))
            v.main = main
            r = execute(v, lambda: None, checkpoint="x", evidence=ev, steps=3,
                        binding={}, allocation_id="test", container="stored")
            self.assertEqual(r["verification"]["status"], "SMOKE_ONLY")
            self.assertEqual(r["verification"]["same_h_status"], "PASS_PENDING_REVIEW")
            self.assertEqual(r["full_run_budget_admission"], "NOT_ESTABLISHED_BY_PROFILING")


if __name__ == "__main__":
    unittest.main()
