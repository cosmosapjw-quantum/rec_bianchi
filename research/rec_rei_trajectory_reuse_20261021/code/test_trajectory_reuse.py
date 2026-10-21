"""Independent focused contract tests; no ODE and no completed-science replay."""
from __future__ import annotations
import hashlib
import itertools
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import warnings

import numpy as np

import reduce_trajectories as rt


def json_write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True) + "\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TrajectoryReuseIndependentTests(unittest.TestCase):
    def grid(self):
        return np.array(list(itertools.product([0., .25], [-1., 0., 1.],
                                               [-2., 0., 2.])))
    def additive(self, axes, epochs=5):
        t = np.linspace(0., 1., epochs)
        s, m, r = (axes[:, i, None] for i in range(3))
        return np.stack([
            s + m*(1-2*t) + r*(t-.25),
            2*m*(1+t) + r*.125*t,
            3*r*(1-t/2) - m*.0625*t,
        ], axis=-1)

    def test_additive_response_and_support_exact_reuse(self):
        axes = self.grid()
        values = self.additive(axes)
        pred, support = rt.reconstruct(axes, values)
        self.assertEqual(int(support.sum()), 10)
        np.testing.assert_allclose(pred, values, rtol=0., atol=2e-15)
        # Support rows must bypass cancellation in (large + small) - large.
        mixed = ~support
        adversarial = values.copy()
        for i, (_, m, r) in enumerate(axes):
            if m == r == 0:
                adversarial[i] = 2.**54
            elif support[i]:
                adversarial[i] = np.arange(15.).reshape(5, 3)/7
            else:
                adversarial[i] = -9
        p, got_support = rt.reconstruct(axes, adversarial)
        np.testing.assert_array_equal(got_support, support)
        np.testing.assert_array_equal(p[support], adversarial[support])
        self.assertTrue(mixed.any())

    def test_known_time_dependent_mixed_polynomial(self):
        axes = self.grid()
        additive = self.additive(axes)
        t = np.linspace(0., 1., additive.shape[1])
        _, m, r = (axes[:, j, None] for j in range(3))
        remainder = np.stack([m*r*(1+t), m*m*r*(2-t),
                              m*r*r*(.25+t*t)], axis=-1)
        actual = additive + remainder
        predicted, support = rt.reconstruct(axes, actual)
        np.testing.assert_allclose(predicted, additive, rtol=0., atol=2e-15)
        np.testing.assert_allclose(actual-predicted, remainder, rtol=0., atol=3e-15)
        np.testing.assert_array_equal(remainder[support], np.zeros_like(remainder[support]))

    def test_heldout_changes_cannot_change_predictions(self):
        axes = self.grid()
        actual = self.additive(axes)
        predicted, support = rt.reconstruct(axes, actual)
        changed = actual.copy()
        changed[~support] += np.arange(1, changed[~support].size+1).reshape(
            changed[~support].shape)*1e4
        other, new_support = rt.reconstruct(axes, changed)
        np.testing.assert_array_equal(other, predicted)
        np.testing.assert_array_equal(new_support, support)
        self.assertGreater(float(np.max(abs(changed[~support]-other[~support]))), 1.)

    def test_signed_shear_and_sum_before_norm(self):
        axes = np.array(list(itertools.product([0.], [-1., 0., 1.], [-1., 0., 1.])))
        t = np.array([0., .5, 1.])
        m, r = axes[:, 1, None], axes[:, 2, None]
        actual = np.stack([m*(1-2*t)+r*(2*t-.5),
                           m*np.ones_like(t), r*np.ones_like(t)], axis=-1)
        pred, _ = rt.reconstruct(axes, actual)
        np.testing.assert_allclose(pred, actual, rtol=0., atol=0.)
        wrong, _ = rt.reconstruct(axes, abs(actual))
        self.assertGreater(float(np.max(abs(abs(pred)-wrong))), 0.)
        i = list(map(tuple, axes)).index((0., 1., -1.))
        self.assertTrue(np.any(pred[i, :, 0] > 0) and np.any(pred[i, :, 0] < 0))
        np.testing.assert_array_equal(abs(pred[i, :, 1]+pred[i, :, 2]), np.zeros(3))
        np.testing.assert_array_equal(abs(pred[i, :, 1])+abs(pred[i, :, 2]), np.full(3, 2.))

    def test_malformed_grid_and_shape_fail_closed(self):
        axes = self.grid(); values = self.additive(axes)
        bad = [
            ("INVALID_SHAPE", axes[:, :2], values),
            ("INVALID_SHAPE", axes, values[:, :, 0]),
            ("DUPLICATE_COORDINATE", np.vstack([axes, axes[:1]]),
             np.concatenate([values, values[:1]], axis=0)),
            ("INCOMPLETE_CARTESIAN_GRID", axes[:-1], values[:-1]),
        ]
        nozero = axes.copy(); nozero[:, 1] += 3
        bad.append(("MISSING_ZERO_ANCHOR", nozero, values))
        for message, a, v in bad:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    rt.reconstruct(a, v)

    def test_real_finite_input_contract(self):
        axes = self.grid(); values = self.additive(axes)
        for where in ("axes", "values"):
            for nonfinite in (np.nan, np.inf, -np.inf):
                a, v = axes.copy(), values.copy()
                (a if where == "axes" else v).flat[0] = nonfinite
                with self.subTest(where=where, nonfinite=nonfinite):
                    with self.assertRaisesRegex(ValueError, "NONFINITE"):
                        rt.reconstruct(a, v)
        for where in ("axes", "values"):
            a, v = axes.astype(complex), values.astype(complex)
            (a if where == "axes" else v).flat[0] += 1j
            with self.subTest(complex=where), warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with self.assertRaisesRegex(ValueError, "REAL|COMPLEX"):
                    rt.reconstruct(a, v)

    def fixture(self, directory):
        root = Path(directory)
        (root/"vendor").mkdir()
        (root/"vendor"/"model.py").write_text("# manufactured metadata only\n")
        model_hash = digest(root/"vendor"/"model.py")
        base = root/"z2_extension"/"results"
        base.mkdir(parents=True)
        x = np.r_[np.linspace(0., math.log(21/5), 121),
                  np.linspace(math.log(21/5), math.log(7), 33)[1:]]
        a = np.exp(x)/21
        cases = []
        for i, (m, r) in enumerate(itertools.product((0., 1.), repeat=2)):
            cid = f"{i:064x}"
            config = dict(Sigma_F_i=0., P_m_i=m, P_r_i=r, Pi_F_signed_i=m+r,
                          guard=False, source_commit=rt.SOURCE_COMMIT,
                          source_sha256={"model.py": model_hash},
                          ellmax=8, radial_cells=24, angular_cells=12,
                          subcell_gauss_order=3, mass_fraction=.1, mass_over_Tref=30.,
                          ne_source=None, solver={"method": "DOP853"})
            case = dict(id=cid, config=config, prefix_raw_sha256="0"*64)
            cases.append(case)
            folder = base/"cases"/cid; folder.mkdir(parents=True)
            h = np.full(153, 1e-16)
            shear_ratio = (.01*m-.02*r)*x
            pm = m*np.exp(-x); pr = r*np.exp(-2*x)
            raw = dict(x=x, a=a, H=h, s=h*shear_ratio, raw_y=np.zeros((40, 153)),
                       P_m=pm, P_r=pr, P_total=pm+pr, Sigma_F=np.sqrt(6)*abs(shear_ratio),
                       Pi_matter_J_m3=pm*h*h/(np.sqrt(6)*rt.KAPPA_T),
                       Pi_gamma_J_m3=pr*h*h/(np.sqrt(6)*rt.KAPPA_T),
                       Pi_nu_J_m3=np.zeros(153),
                       elapsed_proper_s=x*(1+.2*m+.3*r))
            np.savez(folder/"raw.npz", **raw)
            json_write(folder/"INPUT.json", case)
            receipt = dict(id=cid, config=config, status="COMPLETED", exit=0,
                           checks={"manufactured_fixture": True},
                           raw_sha256=digest(folder/"raw.npz"),
                           raw_bytes=(folder/"raw.npz").stat().st_size)
            json_write(folder/"RESULT.json", receipt)
        json_write(base/"MANIFEST.json", {"cases": cases})
        return root, cases, digest(base/"MANIFEST.json")

    def replace_raw(self, root, cid, change):
        folder = root/"z2_extension/results/cases"/cid
        with np.load(folder/"raw.npz") as d:
            data = {k: d[k].copy() for k in d.files}
        change(data)
        np.savez(folder/"raw.npz", **data)
        receipt = json.loads((folder/"RESULT.json").read_text())
        receipt.update(raw_sha256=digest(folder/"raw.npz"),
                       raw_bytes=(folder/"raw.npz").stat().st_size)
        json_write(folder/"RESULT.json", receipt)

    def fixture_contract(self, manifest_hash):
        return mock.patch.multiple(rt, SIGMAS=(0.,), MATTER=(0., 1.),
                                   RADIATION=(0., 1.), MANIFEST_SHA256=manifest_hash)

    def test_common_redshift_not_common_proper_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            root, cases, mh = self.fixture(directory)
            with self.fixture_contract(mh):
                _, _, _, z, _, elapsed, _ = rt.load_snapshot(root)
                self.assertEqual(float(z[0]), 20.)
                self.assertAlmostEqual(float(z[-1]), 2., places=14)
                self.assertFalse(np.array_equal(elapsed[0], elapsed[-1]))
                self.replace_raw(root, cases[-1]["id"],
                                 lambda d: d["x"].__setitem__(10, d["x"][10]+1e-8))
                with self.assertRaisesRegex(ValueError, "UNALIGNED_REDSHIFT_GRID"):
                    rt.load_snapshot(root)

    def test_snapshot_rejects_bad_identity_and_nonfinite_clocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root, cases, mh = self.fixture(directory)
            with self.fixture_contract(mh):
                folder = root/"z2_extension/results/cases"/cases[0]["id"]
                with (folder/"raw.npz").open("ab") as f:
                    f.write(b"tampered")
                with self.assertRaisesRegex(ValueError, "RAW_IDENTITY_MISMATCH"):
                    rt.load_snapshot(root)
        for field, bad_value in (("H", np.inf), ("elapsed_proper_s", np.nan), ("a", np.nan),
                                 ("Pi_matter_J_m3", np.nan), ("Sigma_F", np.nan)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root, cases, mh = self.fixture(directory)
                with self.fixture_contract(mh):
                    self.replace_raw(root, cases[0]["id"],
                                     lambda d: d[field].__setitem__(10, bad_value))
                    with self.assertRaisesRegex(ValueError, "NONFINITE|INVALID_REAL_FINITE_FIELD"):
                        rt.load_snapshot(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
