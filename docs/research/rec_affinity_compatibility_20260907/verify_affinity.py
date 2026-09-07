"""Bounded entropy discriminator through unchanged PR77 component calls."""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal as D, localcontext
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'rec_fixed_map_single_field_jvp_20260907'
sys.path.insert(0, str(PARENT))
from composite_probe import compose

PINS = {
    'docs/research/rec_fixed_map_single_field_jvp_20260907/composite_probe.py':
        '7b604e79d514a89b8181e6533ecf27e8a4836337',
    'src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py':
        '26ddc41e24fadf0bdd19f1924e1a429d602d9c19',
    'src/full_bianchi_hyrec/trajectory/com_source_deposition.py':
        'a3662cf399f14b7148d880266825be12baf934a0',
}
ETAS = (-1/4, -1/8, -1/16, 0., 1/16, 1/4)
TOL = 4096 * np.finfo(float).eps
OBSERVATIONS = {}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def state(eta):
    ratio = math.exp(eta) / 8
    ground = (9/16) / (1 + ratio)
    return np.array([0., -math.log(15), ground*ratio, ground, 1., 8., 4.])


def decimal_reference(z, kind, precision):
    """Independent primal; no NumPy or original API in the reference path."""
    with localcontext() as ctx:
        ctx.prec = precision
        y0, y1, xu, xg, a, n, H = [D.from_float(float(v)) for v in z]
        f0, f1 = y0.exp(), y1.exp()
        c0, c1 = (1 + 1/f0).ln(), (1 + 1/f1).ln()
        if kind == 'chi':
            ct, cc = (2*c0+c1)/3, c0
            ft, fc = 1/(ct.exp()-1), 1/(cc.exp()-1)
        elif kind == 'log_control':
            ft, fc = ((y0+y1)/2).exp(), f0
            ct, cc = (1 + 1/ft).ln(), (1 + 1/fc).ln()
        else:
            raise ValueError(kind)
        forward = a*xu*(1+fc)*(1+ft)
        reverse = a*xg*fc*ft
        gamma = forward-reverse
        ar = (xu/xg).ln() + ct + cc
        asc = (xu/xg).ln() + (5*c0+c1)/3
        return {
            'gamma': gamma, 'affinity_read': ar, 'affinity_scatter': asc,
            'entropy_rate': gamma*asc, 'pair_entropy_rate': gamma*ar,
            'C0': n*D(5)/6*gamma, 'C1': n/12*gamma,
        }


def observe(eta, kind):
    z = state(eta)
    r = compose(z, np.zeros(7), kind)
    chi = np.logaddexp(0., -z[:2])
    asc = math.log(z[2]/z[3]) + (5*chi[0]+chi[1])/3
    ar = math.log(z[2]/z[3]) + float(np.sum(r['query_chi']))
    beta = np.array([2., 4.])/z[5]
    # Direct contraction of the discrete entropy gradient with actual API flow.
    sdot = r['gamma']*math.log(z[2]/z[3]) + float((beta*chi)@r['C'])
    return z, r, {
        'eta': eta, 'read_kind': kind, 'gamma': r['gamma'],
        'affinity_read': ar, 'affinity_scatter': asc, 'entropy_rate': sdot,
        'pair_entropy_rate': r['gamma']*ar, 'C0': r['C'][0], 'C1': r['C'][1],
        'number_residual': float(np.array([2., 4.])@r['C']-2*z[5]*r['gamma']),
        'energy_residual_E0': float(np.array([2., 16.])@r['C']-3*z[5]*r['gamma']),
    }


def entropy_count(w, beta):
    xu, xg, p0, p1 = w
    result = -xu*xu.ln()-xg*xg.ln()
    for p, b in zip((p0, p1), beta):
        f = p/b
        result += b*((1+f)*(1+f).ln()-f*f.ln())
    return result


class Checks(unittest.TestCase):
    def test_01_api_reference_and_conservation(self):
        rows = []
        for eta in ETAS:
            for kind in ('chi', 'log_control'):
                z, r, row = observe(eta, kind)
                lo = decimal_reference(z, kind, 80)
                hi = decimal_reference(z, kind, 120)
                with localcontext() as ctx:
                    ctx.prec = 120
                    gap = max(abs(lo[k]-hi[k])/(1+abs(hi[k])) for k in hi)
                self.assertLess(gap, D('1e-70'))
                err = max(abs(row[k]-float(hi[k]))/(1+abs(float(hi[k]))) for k in hi)
                self.assertLessEqual(err, TOL)
                self.assertLessEqual(abs(row['number_residual']), TOL*(1+abs(2*z[5]*r['gamma'])))
                self.assertLessEqual(abs(row['energy_residual_E0']), TOL*(1+abs(3*z[5]*r['gamma'])))
                self.assertLessEqual(abs(z[2]+z[3]-9/16), TOL)
                row.update(reference_gap_80_120=str(gap), scaled_api_error=err,
                           reference_entropy_rate_120=str(hi['entropy_rate']))
                rows.append(row)
        OBSERVATIONS['cases'] = rows

    def test_02_negative_entropy_interval(self):
        with localcontext() as ctx:
            ctx.prec = 120
            eta0 = (D(4)/(1+D(15).sqrt())).ln()
            self.assertLess(eta0, D('-0.125'))
            self.assertLess(D('-0.125'), 0)
        _, _, good = observe(-1/8, 'chi')
        _, _, bad = observe(-1/8, 'log_control')
        self.assertGreater(good['entropy_rate'], 1e-5)
        self.assertLess(bad['entropy_rate'], -1e-5)
        self.assertGreater(bad['pair_entropy_rate'], 0)
        self.assertGreater(bad['gamma'], 0)
        OBSERVATIONS['counterexample'] = {
            'exact_interval': 'log(4/(1+sqrt(15))) < eta < 0',
            'eta0_decimal_120': str(eta0), 'chi': good, 'log_control': bad,
        }

    def test_03_independent_entropy_directional_difference(self):
        records = []
        for kind in ('chi', 'log_control'):
            z, r, row = observe(-1/8, kind)
            with localcontext() as ctx:
                ctx.prec = 100
                # Exact decimal interpretation of the binary64 state and API flow.
                beta = (D(1)/4, D(1)/2)
                f = [D.from_float(float(y)).exp() for y in z[:2]]
                w = [D.from_float(float(z[2])), D.from_float(float(z[3])),
                     beta[0]*f[0], beta[1]*f[1]]
                g = D.from_float(float(r['gamma']))
                v = [-g, g, beta[0]*D.from_float(float(r['C'][0])),
                     beta[1]*D.from_float(float(r['C'][1]))]
                gradient = [-w[0].ln()-1, -w[1].ln()-1,
                            (1+1/f[0]).ln(), (1+1/f[1]).ln()]
                target = sum(a*b for a, b in zip(gradient, v))
                errors = []
                estimates = []
                for exponent in (8, 12, 16):
                    h = D(2)**(-exponent)
                    plus = [a+h*b for a, b in zip(w, v)]
                    minus = [a-h*b for a, b in zip(w, v)]
                    self.assertTrue(all(x > 0 for x in plus+minus))
                    fd = (entropy_count(plus, beta)-entropy_count(minus, beta))/(2*h)
                    estimates.append(str(fd)); errors.append(abs(fd-target))
                self.assertLess(errors[1], errors[0]/100)
                self.assertLess(errors[2], errors[1]/100)
                self.assertLess(errors[2], D('1e-11'))
                self.assertLessEqual(abs(float(target)-row['entropy_rate']), TOL)
                self.assertEqual(target > 0, kind == 'chi')
                records.append({'read_kind': kind, 'entropy_gradient_flow': str(target),
                                'steps_s': ['2^-8', '2^-12', '2^-16'],
                                'central_estimates': estimates,
                                'absolute_errors': [str(x) for x in errors]})
        OBSERVATIONS['entropy_directional_difference'] = records


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ids = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.ids.append({'id': test.id(), 'outcome': 'PASS'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.ids.append({'id': test.id(), 'outcome': 'FAIL'})

    def addError(self, test, err):
        super().addError(test, err)
        self.ids.append({'id': test.id(), 'outcome': 'ERROR'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    result = {'classification': 'NOT_COMPLETED', 'physical_source_authenticated': False,
              'provider_admitted': False, 'claim': 'NO_PASS_REC_PHYSICAL_SPLIT',
              'original_bass_replayed': False, 'pr77_tests_replayed': False}
    rc = 2
    try:
        result.update(source_commit=git('rev-parse', 'HEAD'), source_tree=git('rev-parse', 'HEAD^{tree}'),
                      source_parent=git('rev-parse', 'HEAD^'), initial_status=git('status', '--porcelain'),
                      command=[sys.executable, *sys.argv], python=sys.version, numpy=np.__version__)
        result['source_blobs'] = {p: blob(ROOT/p) for p in PINS}
        result['script_blob'] = blob(Path(__file__))
        if result['initial_status'] or result['source_blobs'] != PINS:
            raise RuntimeError('Dirty checkout or changed inherited source')
        with (out/'tests.log').open('w') as stream:
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
            run = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
        result['tests'] = {'run': run.testsRun, 'failures': len(run.failures), 'errors': len(run.errors),
                           'skips': len(run.skipped), 'per_id': run.ids}
        result['observations'] = OBSERVATIONS
        result['final_status'] = git('status', '--porcelain')
        result['source_unchanged'] = all(blob(ROOT/p) == sha for p, sha in PINS.items())
        success = (run.wasSuccessful() and run.testsRun == 3 and not run.skipped
                   and not result['final_status'] and result['source_unchanged'])
        rc = 0 if success else 1
        result['classification'] = 'PASS_BOUNDED_AFFINITY_DISCRIMINATOR' if success else 'FAIL_AFFINITY_DISCRIMINATOR'
        if OBSERVATIONS.get('cases'):
            with (out/'CASES.csv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(OBSERVATIONS['cases'][0]), lineterminator='\n')
                writer.writeheader(); writer.writerows(OBSERVATIONS['cases'])
    except Exception:
        result['classification'] = 'SETUP_OR_EXECUTION_FAILED'
        result['traceback'] = traceback.format_exc()
    result.update(exit_code=rc, elapsed_seconds=time.monotonic()-started)
    (out/'RESULT.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2, allow_nan=False))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
