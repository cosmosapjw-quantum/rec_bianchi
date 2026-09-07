"""Research-only completion of the PR79 invariant/JVP checks; not a provider.

This file was authored in the main conversation. Execution is not implied by
its presence. The original seven PR79 tests and their tolerances are unchanged.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
import math
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL = ROOT / "docs/research/rec_multi_bin_affinity_20260907"
sys.path.insert(0, str(ORIGINAL))
import numpy as np
import mpmath as mp
import sympy as sp
import study as m
import test_study as original_checks
from run_study import Result, csvwrite, dump

TOL = 4096 * np.finfo(float).eps
OBS: dict = {}
JVP_ROWS: list[dict] = []
# Count ordering: (xu, xg, beta0*f0, ..., beta4*f4).
L_INTEGER = [
    [1, 1, 0, 0, 0, 0, 0],
    [2, 0, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0, 0, -1],
    [0, 0, 0, 1, 0, -1, 0],
]
L = np.array(L_INTEGER, dtype=float)


def scaled(a, b) -> float:
    aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if aa.shape != bb.shape or not np.isfinite(aa).all() or not np.isfinite(bb).all():
        raise ValueError("comparison needs finite, equally shaped arrays")
    return float(np.max(np.abs(aa - bb) / (1 + np.abs(bb))))


def family(kappa=1., p=-.5, q=-.125, total=9/16):
    """Positive stationary family, not a new physical spectrum or an update."""
    if not (math.isfinite(total) and total > 0 and kappa > max(abs(p), abs(q))):
        raise ValueError("stationary-family positive interior required")
    chi = np.array([kappa+p, kappa+q, kappa, kappa-q, kappa-p])
    f = 1 / np.expm1(chi)
    rho = math.exp(-2*kappa)
    xg = total / (1+rho)
    xu = rho*xg
    z = np.r_[np.log(f), xu, xg, 1., 8., 4.]
    # Coordinate derivatives with respect to (kappa,p,q,total).
    dchi = np.array([[1,1,1,1,1], [1,0,0,0,-1], [0,1,0,-1,0], [0,0,0,0,0]], dtype=float)
    tangents = np.zeros((4, 10))
    tangents[:, :5] = -(1+f)[None, :] * dchi
    tangents[0, 5:7] = [-2*xu*xg/total, 2*xu*xg/total]
    tangents[3, 5:7] = [xu/total, xg/total]
    return z, tangents


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables, _ = m.load_tables()

    def close(self, a, b):
        self.assertLessEqual(scaled(a, b), TOL)

    def test_01_full_left_kernel_and_energy_dependence(self):
        exact_L = sp.Matrix(L_INTEGER)
        self.assertEqual(exact_L.rank(), 4)
        eps = Q(float(m.U[0]))
        energy = [Q(1), Q(0), *[Q(float(u)) for u in m.U]]
        combination = [Q(1,2)*L_INTEGER[1][i] + (eps-Q(1,2))*L_INTEGER[2][i]
                       - Q(1,4)*L_INTEGER[3][i] for i in range(7)]
        self.assertEqual(energy, combination)
        rows = []
        for table in self.tables:
            columns = []
            for uf in table['ut']:
                u = Q(float(uf))
                bt = original_checks.exact_weights(u)
                bc = original_checks.exact_weights(1-u)
                v = [Q(-1), Q(1), *[a+b for a,b in zip(bt,bc)]]
                columns.append(v)
                for row in L_INTEGER:
                    self.assertEqual(sum(Q(a)*b for a,b in zip(row,v)), 0)
            # The four exact left vectors prove rank <=3. A nonzero minor of
            # three actual table columns proves rank >=3 independently of an
            # arbitrary singular-value threshold.
            _, pivots = original_checks.exact_rank(table)
            self.assertEqual(len(pivots), 3)
            witness = sp.Matrix([[sp.Rational(x.numerator,x.denominator)
                                  for x in columns[b]] for b in pivots]).T
            self.assertEqual(witness.rank(), 3)
            vf = np.vstack([-np.ones(table['n']), np.ones(table['n']), table['D']])
            self.close(L @ vf, np.zeros((4, table['n'])))
            rows.append({'table':table['label'], 'exact_left_rank':4,
                         'exact_stoichiometric_rank':3, 'witness_bin_indices':pivots,
                         'floating_left_residual':float(np.max(np.abs(L@vf))),
                         'qualification':'exact rational stencil and rounded API stencil are distinguished'})
        OBS['complete_invariants'] = {'rows':L_INTEGER, 'tables':rows,
            'energy_combination':'energy = L1/2 + (2^-30-1/2)*L2 - L3/4'}

    def test_02_actual_count_source_and_density_direction(self):
        rows = []
        z = m.state(eta=-.125, even=.125)
        dz = m.directions()[-1]
        beta = m.MU/z[8]
        for table in self.tables:
            for kind in ('chi', 'log_control'):
                r = m.compose(table, z, dz, kind)
                field = np.r_[-r['S'], r['S'], beta*r['C']]
                derivative = np.r_[-r['dS'], r['dS'], beta*(r['dC']-r['C']*dz[8]/z[8])]
                self.close(L@field, np.zeros(4))
                self.close(L@derivative, np.zeros(4))
                # A diagnostic omission, not a mutation of production code.
                wrong = np.r_[-r['dS'], r['dS'], beta*r['dC']]
                missing_term_residual = float(np.max(np.abs(L@wrong)))
                self.assertGreater(missing_term_residual, 1e-6)
                rows.append({'table':table['label'], 'read':kind,
                             'field_residual':float(np.max(np.abs(L@field))),
                             'jvp_residual':float(np.max(np.abs(L@derivative))),
                             'omit_beta_density_derivative_residual':missing_term_residual})
        OBS['count_density_chain'] = rows

    def test_03_stationary_manifold_and_four_right_null_vectors(self):
        z, dzs = family()
        beta = m.MU/z[8]
        f = np.exp(z[:5])
        tangent_counts = np.column_stack([np.r_[dz[5:7], beta*f*dz[:5]] for dz in dzs])
        self.assertEqual(np.linalg.matrix_rank(tangent_counts), 4)
        rows = []
        for table in self.tables:
            r = m.compose(table,z)
            activity = math.fsum(r['F']+r['R'])
            self.assertLessEqual(float(np.max(np.abs(r['gamma'])/(r['F']+r['R']))), TOL)
            cols = []
            for j in range(7):
                dz = np.zeros(10)
                if j < 2:
                    dz[5+j] = 1.
                else:
                    dz[j-2] = 1/(beta[j-2]*f[j-2])
                a = m.compose(table,z,dz)
                cols.append(np.r_[-a['dS'],a['dS'],beta*a['dC']])
            J = np.column_stack(cols)
            metric = np.r_[1/z[5],1/z[6],1/(beta*f*(1+f))]
            right_null = L.T/metric[:,None]
            self.close(J@right_null, np.zeros((7,4)))
            self.close(J@tangent_counts, np.zeros((7,4)))
            tangent_residuals = []
            for dz in dzs:
                a = m.compose(table,z,dz)
                e = float(np.max(np.abs(a['dgamma'])))
                self.assertLessEqual(e, TOL*(1+activity))
                tangent_residuals.append(e)
            rows.append({'table':table['label'], 'positive_chi':[.5,.875,1.,1.125,1.5],
                         'net_rate':r['S'], 'activity':activity,
                         'right_null_residual':float(np.max(np.abs(J@right_null))),
                         'stationary_tangent_residuals':tangent_residuals,
                         'count_jacobian':J.tolist()})
        OBS['stationary_manifold'] = rows

    def test_04_missing_photon_axes_against_independent_primal(self):
        z, _ = family()
        z[:5] = -np.log(np.expm1(np.array([.5,.8,1.1,1.4,2.1])))
        # PR79 uses y1 and a mixed direction. This adds y0,y2,y3,y4 at one
        # explicitly non-equilibrium state, for both tables and both reads.
        for table in self.tables:
            for kind in ('chi','log_control'):
                for axis in (0,2,3,4):
                    dz = np.zeros(10); dz[axis] = 1.
                    a = m.compose(table,z,dz,kind)
                    p80,j80 = m.independent(table,z,dz,kind,80,32)
                    p120,j120 = m.independent(table,z,dz,kind,120,32)
                    _,fine = m.independent(table,z,dz,kind,120,36)
                    with mp.workdps(120):
                        ep = max(abs(x-y)/(1+abs(y)) for x,y in zip(p80+j80,p120+j120))
                        eh = max(abs(x-y)/(1+abs(y)) for x,y in zip(j120,fine))
                        self.assertLess(ep, mp.mpf('1e-60'))
                        self.assertLess(eh, mp.mpf('1e-16'))
                    self.close(a['value'],p120)
                    self.close(a['jvp'],fine)
                    JVP_ROWS.append({'table':table['label'],'read':kind,'photon_axis':axis,
                                     'scaled_primal_error':scaled(a['value'],p120),
                                     'scaled_jvp_error':scaled(a['jvp'],fine),
                                     'precision_80_120':mp.nstr(ep,25),
                                     'central_step_refinement':mp.nstr(eh,25)})
        self.assertEqual(len(JVP_ROWS),16)
        OBS['additional_jvp'] = {'comparisons':len(JVP_ROWS),
            'max_scaled_jvp_error':max(x['scaled_jvp_error'] for x in JVP_ROWS),
            'normalization':'normalized', 'state_role':'manufactured non-equilibrium',
            'reference':'original independent nonlinear primal; not a second derivative implementation'}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    with (out/'unittest.log').open('w', encoding='utf-8') as log:
        result = unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    good = result.wasSuccessful() and result.testsRun == 4 and not result.skipped
    rc = 0 if good else 1
    report = {'classification':'PASS_BOUNDED_NULLSPACE_SUPPLEMENT' if good else 'FAIL_NULLSPACE_SUPPLEMENT',
              'claim':'NO_PASS_REC_PHYSICAL_SPLIT', 'physical_source_authenticated':False,
              'provider_admitted':False, 'tests':{'run':result.testsRun,
              'failures':len(result.failures),'errors':len(result.errors),
              'skips':len(result.skipped),'per_id':result.per_id},
              'observations':OBS,'exit_code':rc,'visual_audit':'NOT_PERFORMED'}
    dump(out/'RESULT.json',report)
    csvwrite(out/'ADDITIONAL_JVP.csv',JVP_ROWS)
    print(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
    print((out/'unittest.log').read_text(encoding='utf-8'))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
