"""Independent input-contract regressions for the actual analyzer run body.

AST extraction avoids importing a runtime model or solver. The inputs below
are synthetic, self-consistent file fixtures; no scientific trajectory is
modified or recomputed. All temporary files are owned by this review.
"""
import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
import sys
sys.dont_write_bytecode = True
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import time
import types
import unittest

import numpy as np
from scipy.integrate import simpson

REVIEW = Path(__file__).resolve().parent
UNIT = REVIEW.parents[1]
ANALYZER = UNIT / "code/analyze_compton.py"
DRIVER = UNIT / "code/run_compton.py"
RID = "synthetic-current-runtime"


def extract_functions(path, names, namespace):
    tree = ast.parse(path.read_text(), filename=str(path))
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_value(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def save_json(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, default=json_value, allow_nan=False)


def save_npz(path, **arrays):
    with Path(path).open("xb") as f:
        np.savez(f, **arrays)


class AnalyzerBindingChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="binding_fixture_", dir=REVIEW)
        self.unit = Path(self.temporary.name)
        self.source = self.unit / "results/compton8"
        self.source.mkdir(parents=True)
        (self.source / "execution").mkdir()
        self.seed, self.branch, self.refined = "s03_m03_r03", "actual_hot", False
        self.ns = dict(np=np, simpson=simpson, Path=Path, json=json, hashlib=hashlib, csv=csv,
                       datetime=datetime, timezone=timezone, time=time, sys=sys,
                       UNIT=self.unit, REPO=self.unit, THERMAL=self.unit / "old",
                       CASES=((self.seed, self.branch, self.refined),), SEEDS=(),
                       BRANCHES=("actual_hot", "planck_reference"), SIGNED_NAMES=tuple("abcdef"),
                       EV_J=1., KB_J_K=1., MEC2_J=1., SIGMA_T_C_M3_S=1.,
                       digest=digest, save_json=save_json, save_npz=save_npz,
                       analyze_collision_case=lambda *_: {"synthetic_fixture": True})
        extract_functions(DRIVER, {"canonical", "label_for", "numerical_spec", "input_manifest"}, self.ns)
        extract_functions(ANALYZER, {"run", "read_npz", "diag_map", "no_ode"}, self.ns)
        tree = ast.parse(ANALYZER.read_text())
        energy_node = next(n for n in tree.body if isinstance(n, ast.Assign)
                           and any(isinstance(t, ast.Name) and t.id == "ENERGY_FIELDS" for t in n.targets))
        exec(compile(ast.Module(body=[energy_node], type_ignores=[]), str(ANALYZER), "exec"), self.ns)
        self.label = self.ns["label_for"](self.seed, self.branch, self.refined)
        self.folder = self.source / self.label
        self.folder.mkdir()
        x = np.array([.9, 1.2, 1.9])
        raw = np.zeros((3, 63))
        raw[:, 40:61] = 1/21
        raw[:, 61] = [.1, .2, .3]
        raw[:, 62] = np.log(1000.)
        names = [field for _, field, _ in self.ns["ENERGY_FIELDS"]]
        names += ["work_J_per_baryon_per_x", "ne_m3", "nb_m3", "H_s", "U_gamma_actual_J_m3",
                  "U_planck_reference_J_m3", "T_planck_reference_K", "elapsed_Myr"]
        values = {name: np.ones(3) for name in names}
        values.update(compton_actual_hot_W_m3=np.full(3, -4000.),
                      compton_planck_reference_W_m3=np.full(3, -3996.))
        self.arrays = dict(x=x, z=21*np.exp(-x)-1, raw_state=raw, initial_state=raw[0].copy(),
                           isotope_scales=np.ones(21), initial_Y=raw[0, 40:61].copy(),
                           T_K=np.full(3, 1000.), signed_observables=np.zeros((3, 6)),
                           compton_branch=np.array(self.branch), source_index=np.array(84),
                           diagnostics=np.column_stack([values[n] for n in names]), diagnostic_names=np.array(names))
        self.inputs = {self.seed: dict(config={"Sigma_F":0., "matter_A":0., "radiation_A":0.},
                         donor={"sha256":"synthetic-donor"},
                         cases={r: dict(arrays=self.arrays,
                                        identity={"label":self.seed+("_refined" if r else "_nominal"),
                                                  "sha256":"synthetic-old"}) for r in (False, True)})}
        spec = dict(seed=self.seed, branch=self.branch, refined=False, rr_closure="mao2017",
                    config=self.inputs[self.seed]["config"], numeric=self.ns["numerical_spec"](False),
                    input=self.ns["input_manifest"](self.inputs)[self.seed],
                    initial_state_sha256=hashlib.sha256(raw[0].tobytes()).hexdigest(), source_identity=RID)
        self.receipt = dict(label=self.label, status="COMPLETE", source_identity=RID, source_files={},
                            case_identity=hashlib.sha256(self.ns["canonical"](spec)).hexdigest(), specification=spec,
                            gates={"synthetic_admitted":True}, outputs={},
                            energy_integrals={"dense_1025":dict(residual_scaled=0., max_backreaction_ratio=0., backreaction_ratio_integral=0.)},
                            energy_grid_delta_scaled=0., admission={"synthetic":dict(metrics={"max_trace_energy_fraction":0.})},
                            wall_seconds=0., own_cpu_seconds=0., integration_wall_seconds=0.,
                            diagnostics_and_persistence_wall_seconds=0., nfev=0, njev=0, nlu=0, accepted_nodes=3)
        for name in ("trajectory.npz", "dense_1025.npz", "dense_513.npz", "accepted_solver_nodes.npz", "accepted_diagnostics.npz"):
            self.write_array(name, self.arrays)
        self.correct_refinement = dict(source_identity=RID, status="PASS", pairs={},
                                       scope="synthetic exact matching refinement receipt")
        self.write_json(self.source / "CAMPAIGN_LOCK.json", dict(source_identity=RID))
        self.write_json(self.source / "REFINEMENT.json", self.correct_refinement)
        self.write_json(self.folder / "RESULT.json", self.receipt)
        def verify_outputs(folder, receipt):
            for name, row in receipt["outputs"].items():
                path = folder / name
                if digest(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
                    raise ValueError("fixture output integrity changed")
        self.ns["verify_outputs"] = verify_outputs
        self.ns["source_identity"] = lambda _: ("synthetic-analysis-id", {"code/analyze_compton.py":digest(ANALYZER)})
        self.ns["runner"] = types.SimpleNamespace(source_identity=lambda:(RID, {}), load_inputs=lambda:self.inputs,
                            refinement_pairs=lambda *_:self.correct_refinement,
                            **{name:self.ns[name] for name in ("canonical", "numerical_spec", "input_manifest", "label_for")})

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, path, value):
        path.write_text(json.dumps(value, default=json_value, allow_nan=False))

    def write_array(self, name, arrays):
        path = self.folder / name
        np.savez(path, **arrays)
        self.receipt["outputs"][name] = dict(bytes=path.stat().st_size, sha256=digest(path))

    def run_analysis(self):
        self.write_json(self.folder / "RESULT.json", self.receipt)
        return self.ns["run"](self.source, self.unit / "analysis")

    def test_stale_refinement_identity_rejected(self):
        stale = dict(self.correct_refinement, source_identity="different-runtime")
        self.write_json(self.source / "REFINEMENT.json", stale)
        with self.assertRaises(ValueError, msg="PASS refinement must be bound to current cases and runtime"):
            self.run_analysis()

    def test_case_label_mismatch_rejected(self):
        self.receipt["label"] = "s04_m04_r04_planck_reference_refined"
        with self.assertRaises(ValueError, msg="The receipt label must match the folder's expected CASES entry"):
            self.run_analysis()

    def test_case_branch_specification_mismatch_rejected(self):
        self.receipt["specification"]["branch"] = "planck_reference"
        self.receipt["case_identity"] = hashlib.sha256(self.ns["canonical"](self.receipt["specification"])).hexdigest()
        with self.assertRaises(ValueError, msg="A self-consistent receipt for another branch must not be relabeled"):
            self.run_analysis()

    def test_case_tolerance_specification_mismatch_rejected(self):
        self.receipt["specification"]["refined"] = True
        self.receipt["specification"]["numeric"] = self.ns["numerical_spec"](True)
        self.receipt["case_identity"] = hashlib.sha256(self.ns["canonical"](self.receipt["specification"])).hexdigest()
        with self.assertRaises(ValueError, msg="A self-consistent refined case must not be reported as nominal"):
            self.run_analysis()

    def test_unbound_case_identity_rejected(self):
        self.receipt["case_identity"] = "incorrect-case-identity"
        with self.assertRaises(ValueError, msg="The case hash must match the expected current configuration"):
            self.run_analysis()

    def test_saved_branch_mismatch_rejected(self):
        wrong = dict(self.arrays, compton_branch=np.array("planck_reference"))
        self.write_array("trajectory.npz", wrong)
        with self.assertRaises(ValueError, msg="Saved arrays must carry the selected branch, even when their bytes match the receipt"):
            self.run_analysis()


if __name__ == "__main__":
    unittest.main(verbosity=2)
