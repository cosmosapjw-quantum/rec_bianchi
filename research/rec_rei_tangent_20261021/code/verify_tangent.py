"""Independent finite-difference audit against the pinned original owner.

No IVP is solved here. The default run uses all 40 frozen cases, their five
stored epochs, three predetermined state directions, and fresh original
owner constructors for amplitude/initial-seed finite differences. Analytic
operator outputs never generate the finite-difference reference values.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import traceback
import unittest

import numpy as np

from owner_model import CanonicalFVSpecies, ROOT, cosmology, make_model, verify_source
from tangent_core import TangentOperator


EPS = np.finfo(np.float64).eps
FD_STEP = EPS ** .2
# A single-case development check exposed fourth-order truncation at late x:
# v=s/Href needs a smaller finite-difference step when H/Href has decreased.
# The 2e-8 acceptance limit is unchanged. The complete raw failed check and
# the same-point step-halving sequence remain in AUDITOR_DEVELOPMENT.json.
STATE_FD_STEP = FD_STEP / 8.
INITIAL_STEPS = np.array([2e-6, 2e-7, 2e-7])
TOLERANCES = {
    "rhs": 2e-13, "state_jvp": 2e-8, "amplitude_jvp": 2e-8,
    "observable_jvp": 2e-8, "observable_amplitude": 2e-8,
    "moment_rho_b_fd": 2e-8, "moment_pi_b_fd": 2e-8,
    "moment_pi_b_chain_rule": 2e-13, "rho_b_plus_six_owner_pi": 2e-13,
    "stored_observables": 2e-13, "owner_observables": 2e-13,
    "initial_state": 2e-13, "initial_seed_state_fd": 2e-9,
    "initial_seed_amplitude_fd": 2e-9, "initial_observable_identity": 2e-9,
    "initial_observable_fd": 2e-9,
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scaled_errors(actual, reference):
    a, b = np.asarray(actual, dtype=float), np.asarray(reference, dtype=float)
    if a.shape != b.shape or not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("AUDIT_SHAPE_OR_NONFINITE_COMPARISON")
    return np.abs(a - b) / np.maximum(1., np.abs(b))


def five_point(function, step=FD_STEP):
    # Central order-four derivative. Pair opposite values before summing.
    minus2, minus1 = function(-2. * step), function(-step)
    plus1, plus2 = function(step), function(2. * step)
    return (8. * (plus1 - minus1) - (plus2 - minus2)) / (12. * step)


def deterministic_directions(y):
    j = np.arange(1, 41, dtype=float)
    directions = np.column_stack((np.sin(.37*j), np.cos(.53*j),
                                  np.sin(.23*j)*np.cos(.71*j)))
    directions *= np.maximum(1., np.abs(y))[:, None]
    directions[3] = 0.  # The original owner rejects negative u at u=0.
    return directions


def original_observables(model, x, y):
    """SI fields and the original source's H, independent of analytic core."""
    fields = model.fields(float(x), y)
    h = float(fields['H'])
    kappa_t = 8. * math.pi * 6.67430e-11 / 299792458.**2
    factor = math.sqrt(6.) * kappa_t / h**2
    matter = factor * float(fields['Pi_matter_J_m3'])
    radiation = factor * (float(fields['Pi_gamma_J_m3'])
                          + float(fields['Pi_nu_J_m3']))
    return np.array([math.sqrt(6.) * float(fields['s']) / h,
                     matter, radiation, matter + radiation])


def original_with_amplitude(model, amplitude):
    """A fresh original species object: fixed radiation seed and fixed y."""
    _, temperature = cosmology()
    return CanonicalFVSpecies(model.source, temperature, model.ellmax,
        Sigma_ref=model.Sigma_ref, orientation=model.orientation,
        kappa_gamma=model.k_gamma, kappa_nu=model.k_nu, ne_source=None,
        mass_fraction=model.fm, massive_A=float(amplitude), mass_over_Tref=30.,
        radial_cells=24, angular_cells=12, subcell_gauss_order=3)


def independent_pi_b(momentum, x, b):
    """Unexpanded packet chain rule, distinct from core's signed polynomial."""
    r = math.exp(-float(x))
    transverse = (r*momentum._q)**2 * math.exp(2.*b) * (1.-momentum._mu2)
    longitudinal = (r*momentum._q)**2 * math.exp(-4.*b) * momentum._mu2
    energy = np.sqrt(momentum.mass**2 + transverse + longitudinal)
    energy_b = (transverse - 2.*longitudinal) / energy
    stress_numerator = longitudinal - .5*transverse
    stress_numerator_b = -4.*longitudinal - transverse
    weight = r**3 * momentum._numbers / momentum.reference_energy_norm
    return float(np.sum(weight * (stress_numerator_b / (3.*energy)
                                  - stress_numerator*energy_b / (3.*energy**2))))


class Audit:
    def __init__(self):
        self.metrics = {name: {"maximum_scaled_error": 0., "maximum_abs_error": 0.,
                              "tolerance": tolerance, "comparisons": 0,
                              "worst_context": None}
                        for name, tolerance in TOLERANCES.items()}
        self.counts = {"original_rhs_evaluations": 0, "original_field_evaluations": 0,
                       "base_models": 0, "amplitude_perturbed_models": 0,
                       "initial_seed_perturbed_models": 0}

    def compare(self, name, actual, reference, context):
        error = scaled_errors(actual, reference)
        entry = self.metrics[name]
        maximum = float(np.max(error))
        absolute = float(np.max(np.abs(np.asarray(actual) - np.asarray(reference))))
        entry['comparisons'] += int(error.size)
        entry['maximum_abs_error'] = max(entry['maximum_abs_error'], absolute)
        if entry['worst_context'] is None or maximum > entry['maximum_scaled_error']:
            entry['maximum_scaled_error'] = maximum
            entry['worst_context'] = context
        return maximum

    def rhs(self, model, x, y):
        self.counts['original_rhs_evaluations'] += 1
        return model.rhs(float(x), y)

    def observables(self, model, x, y):
        self.counts['original_field_evaluations'] += 1
        return original_observables(model, x, y)


def load_fixture():
    manifest_path = ROOT / 'inputs/FIXTURE_MANIFEST.json'
    path = ROOT / 'inputs/STORED_STATE_FIXTURE.npz'
    manifest = json.loads(manifest_path.read_text())
    if sha256(path) != manifest['fixture_sha256'] or path.stat().st_size != manifest['fixture_bytes']:
        raise ValueError('FROZEN_FIXTURE_BYTE_IDENTITY_MISMATCH')
    with np.load(path, allow_pickle=False) as packet:
        fixture = {key: packet[key].copy() for key in packet.files}
    expected_shapes = {'axes': (40, 3), 'y': (40, 5, 40), 'x': (40, 5),
                       'observables': (40, 5, 4), 'epochs': (5,), 'case_ids': (40,)}
    for name, shape in expected_shapes.items():
        if fixture[name].shape != shape:
            raise ValueError('FROZEN_FIXTURE_SHAPE_MISMATCH:' + name)
        if name != 'case_ids' and (np.iscomplexobj(fixture[name])
                                   or not np.isfinite(fixture[name]).all()):
            raise ValueError('FROZEN_FIXTURE_NONFINITE:' + name)
    np.testing.assert_array_equal(fixture['epochs'], manifest['epochs'])
    np.testing.assert_array_equal(fixture['axes'], [case['axes'] for case in manifest['cases']])
    np.testing.assert_array_equal(fixture['case_ids'], [case['case_id'] for case in manifest['cases']])
    return fixture, manifest


def verify_case(audit, fixture, index):
    axes = fixture['axes'][index]
    case_id = str(fixture['case_ids'][index])
    model, seed = make_model(*axes)
    audit.counts['base_models'] += 1
    operator = TangentOperator(model)
    y0 = model.initial_state()
    audit.compare('initial_state', y0, fixture['y'][index, 0], {'case_id': case_id})
    # Original constructors are shared only across this case's five x values.
    offsets = (-2., -1., 1., 2.)
    amplitude_models = {offset: original_with_amplitude(model, seed.amplitude + offset*FD_STEP)
                        for offset in offsets}
    audit.counts['amplitude_perturbed_models'] += len(amplitude_models)
    rows = []
    for epoch_index, (x, y) in enumerate(zip(fixture['x'][index], fixture['y'][index])):
        context = {'case_id': case_id, 'stored_index': int(fixture['epochs'][epoch_index])}
        prepared = operator.prepare(float(x), y)
        audit.compare('rhs', prepared.rhs, audit.rhs(model, x, y), context)
        audit.compare('owner_observables', prepared.observables_signed,
                      audit.observables(model, x, y), context)
        audit.compare('stored_observables', prepared.observables_signed,
                      fixture['observables'][index, epoch_index], context)
        directions = deterministic_directions(y)
        actions = prepared.jvp(directions)
        observable_actions = prepared.observable_jvp(directions)
        jvp_errors, observable_errors = [], []
        for col in range(3):
            direction = directions[:, col]
            reference = five_point(lambda h: audit.rhs(model, x, y + h*direction), STATE_FD_STEP)
            obs_reference = five_point(lambda h: audit.observables(model, x, y + h*direction), STATE_FD_STEP)
            c = dict(context, direction=col)
            jvp_errors.append(audit.compare('state_jvp', actions[:, col], reference, c))
            observable_errors.append(audit.compare('observable_jvp', observable_actions[:, col], obs_reference, c))
        amp_rhs = {offset: audit.rhs(amplitude_models[offset], x, y) for offset in offsets}
        amp_obs = {offset: audit.observables(amplitude_models[offset], x, y) for offset in offsets}
        fd_amp = (8.*(amp_rhs[1.] - amp_rhs[-1.]) - (amp_rhs[2.] - amp_rhs[-2.])) / (12.*FD_STEP)
        fd_amp_obs = (8.*(amp_obs[1.] - amp_obs[-1.]) - (amp_obs[2.] - amp_obs[-2.])) / (12.*FD_STEP)
        direct = prepared.jvp(np.zeros(40), 1.)
        obs_direct = prepared.observable_jvp(np.zeros(40), 1.)
        amp_error = audit.compare('amplitude_jvp', direct, fd_amp, context)
        amp_obs_error = audit.compare('observable_amplitude', obs_direct, fd_amp_obs, context)
        cotangent = np.cos(.19 * np.arange(1, 41, dtype=float))
        grad, grad_a = prepared.vjp(cotangent)
        da = np.array([.7, -.2, 1.1])
        combined = prepared.jvp(directions, da)
        left = cotangent @ combined
        right_state, right_a = grad @ directions, grad_a * da
        dual_residual = np.abs(left - (right_state + right_a))
        dual_scale = 512.*EPS*(1. + np.abs(left) + np.abs(right_state) + np.abs(right_a))
        dual_ratio = dual_residual / dual_scale
        moment = model.momentum.moments(float(x), float(y[1]))
        b = float(y[1])
        rho_b_fd = five_point(lambda h: np.asarray(model.momentum.moments(float(x), b+h).rho))
        pi_b_fd = five_point(lambda h: np.asarray(model.momentum.moments(float(x), b+h).pi_s))
        md = prepared.moment_data
        rho_error = audit.compare('moment_rho_b_fd', md['rho_b'], rho_b_fd, context)
        pi_error = audit.compare('moment_pi_b_fd', md['pi_b'], pi_b_fd, context)
        audit.compare('moment_pi_b_chain_rule', md['pi_b'], independent_pi_b(model.momentum, x, b), context)
        audit.compare('rho_b_plus_six_owner_pi', md['rho_b'], -6.*moment.pi_s, context)
        rows.append({
            'case_index': index, 'stored_index': context['stored_index'], 'x': float(x),
            'z': float(21.*math.exp(-float(x)) - 1.), 'observables': prepared.observables_signed,
            'moment_pi_b': md['pi_b'], 'moment_rho_b': md['rho_b'], 'moment_pi_A': md['pi_A'],
            'rhs_amplitude': direct, 'observable_amplitude': obs_direct,
            'state_jvp_scaled_error': jvp_errors, 'observable_jvp_scaled_error': observable_errors,
            'amplitude_jvp_scaled_error': amp_error, 'observable_amplitude_scaled_error': amp_obs_error,
            'duality_residual': dual_residual, 'duality_limit_fraction': dual_ratio,
            'moment_rho_b_scaled_error': rho_error, 'moment_pi_b_scaled_error': pi_error,
        })
    p0 = operator.prepare(0., y0)
    initial_action = p0.observable_jvp(seed.initial_tangents, seed.amplitude_gradient)[:3]
    audit.compare('initial_observable_identity', initial_action, np.eye(3), {'case_id': case_id})
    for col, step in enumerate(INITIAL_STEPS):
        delta = np.zeros(3)
        delta[col] = step
        plus, _ = make_model(*(axes + delta))
        minus, _ = make_model(*(axes - delta))
        audit.counts['initial_seed_perturbed_models'] += 2
        plus_y, minus_y = plus.initial_state(), minus.initial_state()
        context = {'case_id': case_id, 'seed_column': col}
        audit.compare('initial_seed_state_fd', seed.initial_tangents[:, col],
                      (plus_y - minus_y) / (2.*step), context)
        audit.compare('initial_seed_amplitude_fd', seed.amplitude_gradient[col],
                      (plus.momentum.amplitude - minus.momentum.amplitude) / (2.*step), context)
        obs_fd = (audit.observables(plus, 0., plus_y)[:3]
                  - audit.observables(minus, 0., minus_y)[:3]) / (2.*step)
        audit.compare('initial_observable_fd', initial_action[:, col], obs_fd, context)
    return rows


def run_contract_tests():
    import test_tangent_contract
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_tangent_contract)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {'tests_run': result.testsRun, 'failures': len(result.failures),
            'errors': len(result.errors), 'successful': result.wasSuccessful(),
            'log': stream.getvalue()}


def run_verification(case_indices=None, include_unit_tests=True):
    verify_source()
    fixture, manifest = load_fixture()
    indices = list(range(40)) if case_indices is None else list(case_indices)
    if not indices or any(type(i) is not int or not 0 <= i < 40 for i in indices):
        raise ValueError('INVALID_AUDIT_CASE_SUBSET')
    audit = Audit()
    rows = []
    for index in indices:
        rows.extend(verify_case(audit, fixture, index))
    for entry in audit.metrics.values():
        entry['pass'] = entry['maximum_scaled_error'] <= entry['tolerance']
    arrays = {key: np.asarray([row[key] for row in rows]) for key in rows[0]}
    arrays['axes'] = fixture['axes'][indices]
    arrays['case_ids'] = fixture['case_ids'][indices]
    max_duality_ratio = float(np.max(arrays['duality_limit_fraction']))
    pi_b_max = float(np.max(arrays['moment_pi_b']))
    tests = run_contract_tests() if include_unit_tests else {'status': 'NOT_RUN_DEVELOPMENT_SUBSET'}
    gates = {name: entry['pass'] for name, entry in audit.metrics.items()}
    gates['duality'] = max_duality_ratio <= 1.
    gates['nonpositive_pi_b'] = pi_b_max <= 0.
    if include_unit_tests:
        gates['contract_tests'] = bool(tests['successful'] and tests['tests_run'] == 8)
    summary = {
        'schema': 'rec.tangent.independent_verification.v1',
        'status': 'PASS_SCOPED' if all(gates.values()) else 'FAIL_SCOPED',
        'scope': 'Finite stored states and original-owner finite differences; no IVP or global error certification.',
        'case_count': len(indices), 'state_count': len(rows), 'state_directions_per_point': 3,
        'initial_seed_columns_per_case': 3, 'case_indices': indices,
        'state_fd': {'formula': 'central five-point, fourth order', 'step': STATE_FD_STEP,
                     'directions': 'sin(.37*j),cos(.53*j),sin(.23*j)*cos(.71*j); max(1,abs(y)) row scale; du=0'},
        'amplitude_fd': {'formula': 'central five-point at fixed y and radiation seed', 'step': FD_STEP,
                         'reference': 'fresh original CanonicalFVSpecies objects at A+h,A-h,A+2h,A-2h'},
        'initial_fd': {'formula': 'central two-point original initial state/field values',
                       'steps': INITIAL_STEPS.tolist(), 'zero_shear': 'signed smooth extension'},
        'scaled_error_definition': 'max_i |actual-reference|/max(1,|reference_i|)',
        'duality': {'max_limit_fraction': max_duality_ratio,
                    'max_abs_residual': float(np.max(arrays['duality_residual'])),
                    'limit': '512*eps64*(1+|lambda dot JVP|+|VJP_y dot direction|+|VJP_A*dA|)'},
        'moment_sign': {'max_pi_b': pi_b_max, 'min_pi_b': float(np.min(arrays['moment_pi_b']))},
        'metrics': audit.metrics, 'gates': gates, 'unit_tests': tests,
        'execution_counts': dict(audit.counts, new_ODE_integrations=0, NCP=0, benchmarks=0),
        'execution_counts_scope': 'Counters cover the fixture audit; eight bounded contract tests are recorded separately.',
        'fixture_sha256': manifest['fixture_sha256'],
        'fixture_manifest_sha256': sha256(ROOT / 'inputs/FIXTURE_MANIFEST.json'),
        'source_commit': manifest['parent_source'],
        'code_sha256': {name: sha256(ROOT / 'code' / name)
                        for name in ('owner_model.py', 'tangent_core.py', 'verify_tangent.py',
                                     'test_tangent_contract.py')},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'historical_failure_note': manifest['data_only_recovery_note'],
        'global_convergence': 'NOT_RUN', 'physical': 'HOLD', 'production': 'NOT_APPROVED',
    }
    return summary, arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result_path = args.output / 'VERIFICATION.json'
    arrays_path = args.output / 'VERIFICATION_DIAGNOSTICS.npz'
    failure_path = args.output / 'VERIFICATION_EXCEPTION.json'
    if any(path.exists() for path in (result_path, arrays_path, failure_path)):
        raise FileExistsError('Verification outputs are create-only; choose a fresh --output directory.')
    try:
        summary, arrays = run_verification()
        with arrays_path.open('xb') as stream:
            np.savez_compressed(stream, **arrays)
        summary['diagnostics'] = {'file': arrays_path.name, 'bytes': arrays_path.stat().st_size,
                                  'sha256': sha256(arrays_path)}
        with result_path.open('x') as stream:
            json.dump(summary, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write('\n')
        print(json.dumps({'status': summary['status'], 'cases': summary['case_count'],
                          'states': summary['state_count'], 'gates': summary['gates']}, sort_keys=True))
        return 0 if summary['status'] == 'PASS_SCOPED' else 1
    except Exception as exc:
        with failure_path.open('x') as stream:
            json.dump({'status': 'EXCEPTION', 'type': type(exc).__name__, 'message': str(exc),
                       'traceback': traceback.format_exc(), 'new_ODE_integrations': 0},
                      stream, indent=2, allow_nan=False)
            stream.write('\n')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
