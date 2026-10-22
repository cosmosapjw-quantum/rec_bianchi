"""Focused independent driver checks: AST extraction, no runtime import or ODE."""
import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import traceback
import types
import unittest
import numpy as np

DRIVER = Path(__file__).resolve().parents[2] / "code/run_compton.py"
REQUIRED = {"accepted_solver_nodes.npz", "trajectory.npz", "accepted_diagnostics.npz", "dense_513.npz", "dense_1025.npz"}
ADMISSION = ("finite", "temperature_domain", "population_positivity", "isotope_conservation", "baryon_conservation", "zero_n_T", "ne_nonnegative", "monotone_tau", "number_monopoles", "einstein_constraint", "tensor_sum", "finite_angular_positivity", "trace_energy_small", "source_energy", "transfer_ledger")
GATES = {f"{grid}:{gate}": True for grid in ("comparison_109", "accepted", "dense_513", "dense_1025") for gate in ADMISSION}
GATES.update({key: True for key in ("integrated_energy_1025", "initial_state_exact", "source_unchanged", "inputs_unchanged")})


def namespace(unit):
    """Compile actual helper bodies, omitting imports and all top-level calls."""
    tree = ast.parse(DRIVER.read_text(), filename=str(DRIVER))
    allowed = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            allowed.append(node)
        elif isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and t.id.isupper() and t.id not in {"UNIT", "REPO", "THERMAL", "OMITTED", "DONOR"} for t in node.targets):
            allowed.append(node)
    ns = dict(Path=Path, hashlib=hashlib, json=json, math=math, np=np, os=os, sys=sys,
              datetime=datetime, timezone=timezone, traceback=traceback,
              UNIT=unit, REPO=unit.parent, __name__="isolated_driver_helpers")
    exec(compile(ast.Module(body=allowed, type_ignores=[]), str(DRIVER), "exec"), ns)
    return ns


class DriverHelpers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="rec_compton_driver_helper_")
        self.unit = Path(self.tmp.name)
        self.ns = namespace(self.unit)

    def tearDown(self):
        self.tmp.cleanup()

    def receipt(self, outputs):
        return dict(status="COMPLETE", source_identity="synthetic-current-identity", gates=dict(GATES), outputs=outputs)

    def test_output_inventory_rejects_empty(self):
        with self.assertRaises(ValueError, msg="An empty outputs map cannot certify the five mandatory retained NPZ files"):
            self.ns["verify_outputs"](self.unit, self.receipt({}))

    def test_output_inventory_rejects_missing_dense(self):
        outputs = {}
        for name in REQUIRED - {"dense_1025.npz"}:
            p = self.unit / name
            p.write_bytes(b"synthetic retained bytes")
            outputs[name] = dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        with self.assertRaises(ValueError, msg="A receipt omitting dense_1025.npz must not be reused"):
            self.ns["verify_outputs"](self.unit, self.receipt(outputs))

    def test_refinement_requires_exact_initial_state(self):
        self.ns["SEEDS"], self.ns["BRANCHES"] = ("seed",), ("branch",)
        for refined in (False, True):
            folder = self.unit / self.ns["label_for"]("seed", "branch", refined)
            folder.mkdir()
            raw = np.zeros((3, 63))
            raw[0, 0] = float(refined)  # Clock only: absent from four refinement metrics.
            arrays = dict(x=np.arange(3.), isotope_scales=np.ones(21), raw_state=raw,
                          signed_observables=np.zeros((3, 6)), initial_state=raw[0].copy())
            outputs = {}
            for name in REQUIRED:
                p = folder / name
                np.savez(p, **arrays)
                outputs[name] = dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            (folder / "RESULT.json").write_text(json.dumps(self.receipt(outputs)))
        with self.assertRaises(ValueError, msg="Refinement comparison must reject different exact initial clock/state"):
            self.ns["refinement_pairs"](self.unit, "synthetic-current-identity")

    def test_campaign_deadline_checked_after_refinement(self):
        clock = types.SimpleNamespace(value=0.0)
        self.ns["time"] = types.SimpleNamespace(perf_counter=lambda: clock.value,
                                                process_time=lambda: 0.0, time=lambda: 1000 + clock.value)
        self.ns["source_identity"] = lambda: ("synthetic-current-identity", {})
        self.ns["require_preflight"] = lambda _: {"synthetic": True}
        self.ns["load_inputs"] = lambda: {}
        self.ns["input_manifest"] = lambda _: {}
        self.ns["environment"] = lambda: {"synthetic": True}
        self.ns["CASES"] = (("seed", "branch", False),)
        self.ns["CAMPAIGN_CAP_SECONDS"] = 1200.0
        def reused_case(*args):
            clock.value = 1199.0
            return dict(label="seed_branch_nominal", execution="complete_reused",
                        result=dict(label="seed_branch_nominal", status="COMPLETE", temperature_end_K=1000., wall_seconds=0.))
        def slow_refinement(*args):
            clock.value = 1201.0
            return dict(status="PASS", synthetic_only=True)
        self.ns["one_case"] = reused_case
        self.ns["refinement_pairs"] = slow_refinement
        (self.unit / "results").mkdir()
        with self.assertRaises(TimeoutError, msg="Final diagnostic work crossed 1200 s; COMPLETE must not be returned"):
            self.ns["run"](self.unit / "results/compton8", "all", False)

    def test_persistent_budget_includes_failed_and_unfinished(self):
        self.ns["time"] = types.SimpleNamespace(time=lambda: 1100.)
        root = self.unit / "execution"
        root.mkdir()
        for i, (started, finished) in enumerate(((1000., ("COMPLETE", 10.)), (1020., ("FAILED", 30.)), (1080., None)), 1):
            directory = root / f"attempt_{i:03d}"
            directory.mkdir()
            (directory / "STARTED.json").write_text(json.dumps(dict(started_epoch=started)))
            if finished:
                (directory / "FINISHED.json").write_text(json.dumps(dict(status=finished[0], wall_seconds=finished[1])))
        self.assertEqual(self.ns["execution_spent"](self.unit), 60.)

    def test_numeric_pair_retains_native63_and_grids(self):
        n, r = (self.ns["numerical_spec"](v) for v in (False, True))
        self.assertEqual(len(n["atol"]), 63)
        np.testing.assert_array_equal(r["atol"], np.array(n["atol"]) * .1)
        self.assertEqual(r["rtol"], .1 * n["rtol"])
        self.assertEqual((n["max_step"], r["max_step"]), (.025, .0125))
        self.assertEqual(n["dense_nodes"], [513, 1025])
        self.assertTrue(n["retain_accepted_nodes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
