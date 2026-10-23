"""One bounded LINE01 production attempt; preserves raw rows on any failure.

Execution requires --execute. Compile/import are not scientific execution.
The parent must authorize execution after checkpoint A publication and backup.
"""
from __future__ import annotations

import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import argparse
from collections import Counter
import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import traceback

import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq
import line_source as model

ROOT = Path(__file__).resolve().parents[1]
EPS = np.finfo(float).eps
EXPECTED = {'source_rows': 36, 'local_map_rows': 27, 'direct_comparisons': 6,
            'finite_reference_roots': 2, 'plot_tracks': 3, 'plot_map_outputs': 243}
OBSERVED = Counter()
ACCEPTANCE = []


def clean(value):
    if isinstance(value, np.ndarray):
        return [clean(x) for x in value.tolist()]
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(x) for x in value]
    return value


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(clean(value), f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Evidence:
    def __init__(self, path):
        self.path = path
        self.handle = path.open('x', encoding='utf-8')
        self.rows = 0

    def append(self, row):
        self.handle.write(json.dumps(clean(row), ensure_ascii=False, allow_nan=False) + '\n')
        self.handle.flush()
        os.fsync(self.handle.fileno())
        self.rows += 1

    def close(self):
        self.handle.close()


def check(name, observed, limit, *, relation='<=', context=''):
    ok = bool(observed <= limit) if relation == '<=' else bool(observed == limit)
    ACCEPTANCE.append({'name': name, 'observed': clean(observed), 'limit': clean(limit),
                       'relation': relation, 'pass': ok, 'context': context})
    return ok


def source_rows(evidence):
    states, rows = [], []
    S = model.shear_fixtures()
    for driving in ('emission', 'LTE', 'absorption'):
        for depth in (0.1, 1.0, 100.0):
            for shear_name, tensor in S.items():
                states.append((f'effective_{driving}_t{depth:g}_{shear_name}',
                    model.state_at_depth('H_LYA_EFFECTIVE_2P', driving, depth, tensor),
                    driving, shear_name))
    native_metadata = None
    for shear_name, tensor in S.items():
        state, metadata = model.native_snapshot_state(tensor)
        native_metadata = metadata
        states.append((f'native_{shear_name}', state, 'saved_native_state', shear_name))
    for card in ('H_LYA_J1HALF', 'H_LYA_J3HALF'):
        for driving in ('emission', 'LTE', 'absorption'):
            states.append((f'{card}_{driving}_t1_triaxial',
                model.state_at_depth(card, driving, 1.0, S['triaxial']), driving, 'triaxial'))
    for identifier, state, driving, shear_name in states:
        result = model.exchange_source(state)
        result.update(id=identifier, driving=driving, shear_fixture=shear_name,
                      row_role='SOURCE_STATE')
        evidence.append(result)
        rows.append(result)
        OBSERVED['source_rows'] += 1
        scale = max(result['gross_escaped_down_m3_s'] + result['gross_escaped_up_m3_s'], 1e-300)
        energy_scale = state.card.energy_J * scale
        for key in ('atom_number_residual', 'photon_upper_residual'):
            check(key, abs(result[key]), 64 * EPS * scale, context=identifier)
        check('energy_ledger', abs(result['energy_residual']), 64 * EPS * energy_scale, context=identifier)
        check('pressure_trace', result['pressure_trace_residual_over_energy_gross'], 64 * EPS, context=identifier)
        check('pstf_trace', result['PSTF_trace_over_energy_gross'], 64 * EPS, context=identifier)
        check('gross_difference_conditioning', result['gross_difference_residual_over_micro'], 64 * EPS, context=identifier)
        check('nonnegative_gross_down', result['gross_escaped_down_m3_s'] >= 0, True, relation='==', context=identifier)
        check('nonnegative_gross_up', result['gross_escaped_up_m3_s'] >= 0, True, relation='==', context=identifier)
        check('zero_ionic_and_thermal', (result['ionic_yield'] == result['free_electron_yield'] == result['du_thermal_J_m3_s'] == 0), True, relation='==', context=identifier)
        if driving == 'LTE':
            check('LTE_absolute_over_gross', result['lte_residual_over_gross'], 64 * EPS, context=identifier)
        if driving in ('emission', 'absorption'):
            check('signed_driving', result['net_R_m3_s'] * (1 if driving == 'emission' else -1) > 0, True, relation='==', context=identifier)
    return states, rows, native_metadata


def high_precision_map(row):
    # Independent W0, at the frozen binary64 scalar coefficients supplied to the root.
    # No log-root values or endpoint values are used by this oracle.
    with mp.workdps(90):
        y0, d0, b = map(mp.mpf, (row['y0'], row['d0'], row['b']))
        N, eq, omega = map(mp.mpf, (row['N_m3'], row['x_eq'], row['omega']))
        if y0 == 0 or omega == 0:
            y1, packet, endpoint = y0, mp.mpf(0), mp.mpf(row['x0'])
        else:
            z0 = -b * y0 / d0
            y1 = -d0 / b * mp.lambertw(z0 * mp.exp(z0 - omega), 0)
            packet = -N * (y1 - y0)
            endpoint = eq + y1
        return {'precision_decimal_digits': 90, 'basis': 'frozen binary64 y0,d0,b,xeq,N,omega; independent principal LambertW',
            'x1_decimal': mp.nstr(endpoint, 85), 'packet_decimal': mp.nstr(packet, 85),
            'endpoint_absolute_error': float(abs(mp.mpf(row['x1']) - endpoint)),
            'packet_absolute_error': float(abs(mp.mpf(row['delta_n_gamma_m3']) - packet))}


def local_map_rows(evidence):
    tensor = model.shear_fixtures()['triaxial']
    inputs = []
    for f in (0.0, 0.1, 2.0):
        for driving in (('emission', 'LTE') if f == 0 else ('emission', 'LTE', 'absorption')):
            for omega in (1e-6, 0.5, 8.0):
                inputs.append((f'local_f{f:g}_{driving}_omega{omega:g}',
                    model.local_fixture(f_plus=f, driving=driving, omega=omega, S=tensor), driving))
    native, _ = model.native_snapshot_state(tensor)
    for omega in (0.1, 1.0, 5.0):
        inputs.append((f'local_native_omega{omega:g}', dict(card_id=native.card_id,
            population_scope=native.population_scope, N_m3=native.N, x0=native.x,
            H_s_inv=native.H_s_inv, f_plus=native.f_plus, S=native.S, omega=omega), 'saved_native_state'))
    rows = []
    for identifier, arguments, driving in inputs:
        row = model.thick_local_step(**arguments)
        row.update(id=identifier, driving=driving, row_role='LOCAL_THICK_MAP')
        oracle = high_precision_map(row)
        row['W0_oracle'] = oracle
        evidence.append(row)
        rows.append(row)
        OBSERVED['local_map_rows'] += 1
        endpoint_limit = 5e-11 * abs(row['y0']) + 64 * EPS * abs(row['x_eq'])
        packet_limit = 5e-13 * row['N_m3'] * abs(row['y0']) + 64 * EPS * abs(row['delta_n_gamma_m3'])
        check('W0_endpoint', oracle['endpoint_absolute_error'], endpoint_limit, context=identifier)
        check('W0_packet', oracle['packet_absolute_error'], packet_limit, context=identifier)
        check('log_root', abs(row['log_root_residual']), 5e-13 * (1 + row['omega'] + abs(row['z0'])), context=identifier)
        check('path_gate', row['path_depth_ratio'] >= model.THICK_THRESHOLD, True, relation='==', context=identifier)
        low, high = sorted((row['x0'], row['x_eq']))
        check('monotone_no_overshoot', low - 64 * EPS <= row['x1'] <= high + 64 * EPS, True, relation='==', context=identifier)
        check('map_population_domain', -64 * EPS <= row['x1'] < row['g'] / row['b'], True, relation='==', context=identifier)
        check('map_signed_packet', row['delta_n_gamma_m3'] * row['y0'] >= 0, True, relation='==', context=identifier)
        for key in ('atom_number_residual', 'photon_upper_residual', 'energy_residual'):
            check('map_' + key, abs(row[key]), 0.0, context=identifier)
        if driving == 'LTE':
            check('equilibrium_exact_branch', row['delta_n_gamma_m3'], 0.0, relation='==', context=identifier)
    return rows


def direct_comparisons(evidence, states, rows):
    Class, identity = model.load_exact_einstein_class()
    selected = ('effective_emission_t0.1_rotated', 'effective_absorption_t1_triaxial',
                'effective_LTE_t1_isotropic', 'effective_emission_t100_triaxial',
                'native_triaxial', 'H_LYA_J1HALF_emission_t1_triaxial')
    states_by_id = {item[0]: item[1] for item in states}
    results_by_id = {r['id']: r for r in rows}
    mu, wmu = np.polynomial.legendre.leggauss(128)
    phi = np.arange(256) * (2 * math.pi / 256)
    rho = np.sqrt(1 - mu[:, None] ** 2)
    n = np.stack((rho * np.cos(phi), rho * np.sin(phi),
                  np.broadcast_to(mu[:, None], (128, 256))), axis=-1).reshape(-1, 3)
    weights = np.broadcast_to(wmu[:, None] / (2 * 256), (128, 256)).ravel()
    for identifier in selected:
        state, primary = states_by_id[identifier], results_by_id[identifier]
        card = state.card
        q = 1 + np.einsum('ni,ij,nj->n', n, state.S, n)
        tau = primary['t'] / q
        absorbed = -np.expm1(-tau)
        beta = absorbed / tau
        Bref = float(weights @ beta)
        Qref = (n.T * (weights * beta)) @ n - Bref * np.eye(3) / 3.0
        fsource = state.n_u_m3 / primary['opacity_delta_m3']
        fbar = fsource + (state.f_plus - fsource) * beta
        nH = state.n_H_reference_m3 or state.N
        profile = 1.0 / card.frequency_Hz
        donor = Class(A_ul_s_inv=card.A_s_inv, profile_Hz_inv=profile,
            frequency_Hz=card.frequency_Hz, nH_m3=nH,
            upper_population=state.n_u_m3/nH, lower_population=state.n_l_m3/nH,
            upper_degeneracy=card.g, lower_degeneracy=1.0)
        phase_measure = 8 * math.pi * card.frequency_Hz**2 / model.C**3 / profile
        direct_direction = phase_measure * donor.directional_action(fbar)
        direct_R = float(weights @ direct_direction)
        direct_Qsource = (n.T * (weights * direct_direction)) @ n - direct_R * np.eye(3) / 3.0
        crossing_R = (8 * math.pi * state.H_s_inv / card.wavelength_m**3 *
                      (fsource-state.f_plus) * float(weights @ (q * absorbed)))
        gross_scale = max(card.A_s_inv * primary['gross_microscopic_density_m3'], 1e-300)
        r = {'id': identifier, 'row_role': 'SELECTED_DIRECT_EINSTEIN_AND_FULL_SPHERE',
             'nodes': len(weights), 'n_mu': 128, 'n_phi': 256, 'B_direct': Bref, 'Q_direct': Qref,
             'direct_Einstein_R_m3_s': direct_R, 'direct_crossing_R_m3_s': crossing_R,
             'source_R_m3_s': primary['net_R_m3_s'], 'gross_microscopic_rate_scale': gross_scale,
             'phase_space_residual_over_gross': abs(direct_R - primary['net_R_m3_s']) / gross_scale,
             'crossing_residual_over_gross': abs(crossing_R - primary['net_R_m3_s']) / gross_scale,
             'tensor_source_residual_over_gross': float(np.linalg.norm(direct_Qsource-primary['number_PSTF_m3_s'])) / gross_scale,
             'angular_B_relative': abs(Bref-primary['B']) / Bref,
             'angular_Q_F_over_B': float(np.linalg.norm(Qref-primary['Q'])) / Bref,
             'absolute_occupation_min': float(np.min(fbar)),
             'profile_Hz_inv': profile, 'donor_method': 'exact AST directional_action at profile-averaged occupation'}
        evidence.append(r)
        OBSERVED['direct_comparisons'] += 1
        OBSERVED['direct_full_sphere_nodes'] += len(weights)
        for key in ('phase_space_residual_over_gross', 'crossing_residual_over_gross', 'tensor_source_residual_over_gross'):
            check(key, r[key], 5e-13, context=identifier)
        for key in ('angular_B_relative', 'angular_Q_F_over_B'):
            check(key, r[key], 5e-10, context=identifier)
    return identity


def finite_references(evidence, local_rows):
    base = {r['id']: r for r in local_rows}
    # The normalized thick map depends on z0,omega only. Reuse the already
    # computed f=.1,omega=.5 map; isotropic reference has its own H for path=20.
    for driving in ('emission', 'absorption'):
        r = base[f'local_f0.1_{driving}_omega0.5']
        z0, d0, omega = r['z0'], r['d0'], r['omega']
        dmin = r['g'] - r['b'] * max(r['x0'], r['x_eq'])
        tau_factor = 20.0 * d0 / dmin
        counts = Counter()
        errors = []
        def integrand(v):
            counts['integrand_evaluations'] += 1
            shape = 1 + z0 * math.exp(v)
            return shape / (-math.expm1(-tau_factor * shape))
        def travel_residual(u):
            counts['travel_quadratures'] += 1
            value, error = quad(integrand, u, 0.0, epsabs=1e-13, epsrel=1e-13, limit=100)
            errors.append(error)
            return value - omega
        lower = -omega + min(z0, 0.0)
        u, report = brentq(travel_residual, lower, 0.0, xtol=1e-14, rtol=4*EPS,
                           maxiter=100, full_output=True)
        endpoint = r['x_eq'] + r['y0'] * math.exp(u)
        lo, hi = r['finite_endpoint_bracket_float']
        output = {'id': 'finite_isotropic_' + driving, 'row_role': 'FINITE_OPACITY_SEPARABLE_REFERENCE',
            'S': np.zeros((3, 3)), 'path_depth_ratio': 20.0, 'omega': omega,
            'reused_normalized_thick_row': r['id'],
            'reuse_reason': 'Same g,f,x0,omega and same path gate20; normalized flow/bracket independent of dimensional H and S',
            'u_finite': u, 'endpoint_finite': endpoint, 'thick_bracket': [lo, hi],
            'outside_bracket_slack': max(lo-endpoint, endpoint-hi, 0.0),
            'travel_integral_residual': travel_residual(u),
            'max_quad_error_estimate': max(errors), 'quad_error_is_not_rigorous_bound': True,
            'root_iterations': int(report.iterations), 'counts': dict(counts),
            'new_IVP_calls': 0}
        evidence.append(output)
        OBSERVED['finite_reference_roots'] += 1
        OBSERVED['finite_reference_integrand_evaluations'] += counts['integrand_evaluations']
        OBSERVED['finite_reference_travel_quadratures'] += counts['travel_quadratures']
        check('finite_reference_bracket', output['outside_bracket_slack'], 5e-13, context=output['id'])
        check('finite_reference_root_residual', abs(output['travel_integral_residual']), 5e-13, context=output['id'])


def rejection_checks(evidence, first_state):
    tensor = model.shear_fixtures()['triaxial']
    valid_map = model.local_fixture(f_plus=0.1, driving='emission', omega=0.5, S=tensor)
    trials = [
        ('whole_n2_card', lambda: model.source_card('H_LYA_WHOLE_N2_SHELL')),
        ('forged_coefficient', lambda: model.source_card(replace(model.CARDS['H_LYA_EFFECTIVE_2P'], A_s_inv=0.0))),
        ('wrong_population_scope', lambda: replace(first_state, population_scope='whole_n2')),
        ('native_duplicate_owner', lambda: replace(first_state, native_line_owner_active=True)),
        ('wrong_owner_mode', lambda: replace(first_state, owner_mode='add_to_canonical')),
        ('nonpositive_H', lambda: replace(first_state, H_s_inv=0.0)),
        ('nan_H', lambda: replace(first_state, H_s_inv=math.nan)),
        ('negative_population', lambda: replace(first_state, n_u_m3=-1.0)),
        ('population_inversion', lambda: replace(first_state, n_u_m3=4*first_state.n_l_m3)),
        ('negative_f_plus', lambda: replace(first_state, f_plus=-0.1)),
        ('nan_f_plus', lambda: replace(first_state, f_plus=math.nan)),
        ('anisotropic_f_plus', lambda: replace(first_state, f_plus=np.ones(3))),
        ('bad_S_shape', lambda: replace(first_state, S=np.zeros((2, 2)))),
        ('nonsymmetric_S', lambda: replace(first_state, S=np.array([[0,.1,0],[0,0,0],[0,0,0]]))),
        ('nontracefree_S', lambda: replace(first_state, S=np.eye(3))),
        ('contracting_direction', lambda: replace(first_state, S=np.diag([-1.1,.4,.7]))),
        ('insufficient_whole_path_gate', lambda: model.thick_local_step(**{**valid_map, 'H_s_inv': valid_map['H_s_inv']*2})),
        ('negative_omega', lambda: model.thick_local_step(**{**valid_map, 'omega': -1.0})),
    ]
    for name, operation in trials:
        try:
            operation()
        except ValueError as exc:
            rejected, reason = True, str(exc)
        else:
            rejected, reason = False, 'UNEXPECTED ACCEPTANCE'
        evidence.append({'id': name, 'row_role': 'INVALID_INPUT_REJECTION', 'rejected': rejected, 'reason': reason})
        check('input_rejection', rejected, True, relation='==', context=name)
        OBSERVED['invalid_input_checks'] += 1


def plot_tracks(evidence, results_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    S = model.shear_fixtures()['triaxial']
    native, _ = model.native_snapshot_state(S)
    tracks = [
        ('emission', model.local_fixture(f_plus=.1, driving='emission', omega=0, S=S),
         'Constructed emission; N=10⁹ m⁻³, f₊=0.1'),
        ('absorption', model.local_fixture(f_plus=.1, driving='absorption', omega=0, S=S),
         'Constructed absorption; N=10⁹ m⁻³, f₊=0.1'),
        ('native_saved_state', dict(card_id=native.card_id, population_scope=native.population_scope,
            N_m3=native.N, x0=native.x, H_s_inv=native.H_s_inv, f_plus=native.f_plus,
            S=native.S, omega=0), 'Saved HyRec z=1099.99865 state + supplied shear'),
    ]
    manifest = {'schema': 'line01.plot_manifest.v1', 'plots': [],
        'samples_per_track': 81, 'total_analytic_map_outputs': 243,
        'classification': 'new local fixed-input source model, not a cosmological trajectory',
        'raw_evidence': str(evidence.path.relative_to(ROOT)),
        'units': {'omega': 'dimensionless eta*proper_time', 'upper_fraction': 'dimensionless n_u/(n_l+n_u)',
                  'photon_packet': 'm^-3', 'energy_packet': 'J m^-3', 'PSTF_energy_packet': 'J m^-3'}}
    figure_dir = ROOT / 'figures'
    figure_dir.mkdir(exist_ok=True)
    for name, args, caption in tracks:
        rows = []
        for omega in np.linspace(0, 8, 81):
            row = model.thick_local_step(**{**args, 'omega': float(omega)})
            row.update(id=f'plot_{name}_{len(rows):03}', row_role='ANALYTIC_PLOT_SAMPLE', track=name)
            evidence.append(row)
            rows.append(row)
            OBSERVED['plot_map_outputs'] += 1
        csv_path = results_dir / f'plot_{name}.csv'
        fields = ['omega','proper_time_s','x0','x_eq','x1','delta_n_gamma_m3','delta_u_radiation_J_m3',
                  'delta_u_internal_J_m3','energy_PSTF_xx','energy_PSTF_yy','energy_PSTF_zz',
                  'energy_PSTF_F','bracket_width_float','log_delta','coarse_population_bound_log']
        with csv_path.open('x', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for r in rows:
                q = r['energy_PSTF_packet_J_m3']
                writer.writerow(dict(omega=r['omega'], proper_time_s=r['delta_t_s'],x0=r['x0'],x_eq=r['x_eq'],x1=r['x1'],
                    delta_n_gamma_m3=r['delta_n_gamma_m3'],delta_u_radiation_J_m3=r['delta_u_radiation_J_m3'],
                    delta_u_internal_J_m3=r['delta_u_internal_J_m3'],energy_PSTF_xx=q[0,0],energy_PSTF_yy=q[1,1],
                    energy_PSTF_zz=q[2,2],energy_PSTF_F=np.linalg.norm(q),bracket_width_float=r['bracket_width_float'],
                    log_delta=r['log_delta'],coarse_population_bound_log=r['coarse_population_error_upper_bound']['log_value']))
        x = [r['omega'] for r in rows]
        fig, ax = plt.subplots(2, 2, figsize=(10.5, 7.4))
        fig.suptitle('LINE01 — exact local thick relaxation\n' + caption, fontsize=14)
        a = ax[0,0]
        a.plot(x, [r['x1'] for r in rows], color='#0b6e75', lw=2, label='upper fraction x')
        a.axhline(rows[0]['x_eq'], color='#333333', lw=1, ls='--', label='equilibrium')
        a.set_ylabel('Upper-level fraction x'); a.set_title('(a) Population relaxation'); a.legend(fontsize=9)
        a = ax[0,1]
        a.plot(x, [r['delta_n_gamma_m3'] for r in rows], color='#8c3a88', lw=2)
        a.axhline(0, color='0.6', lw=.7)
        a.set_ylabel('Signed photon packet [m⁻³]'); a.set_title('(b) Effective escaping exchange')
        a = ax[1,0]
        a.plot(x, [r['delta_u_radiation_J_m3'] for r in rows], label='radiation', color='#d55e00', lw=2)
        a.plot(x, [r['delta_u_internal_J_m3'] for r in rows], label='atomic internal', color='#0072b2', lw=2)
        a.set_ylabel('Energy packet [J m⁻³]'); a.set_title('(c) Equal-opposite energy ledger'); a.legend(fontsize=9)
        a = ax[1,1]
        for j, (color, label) in enumerate((('#0072b2','xx'),('#d55e00','yy'),('#009e73','zz'))):
            a.plot(x, [r['energy_PSTF_packet_J_m3'][j,j] for r in rows], lw=2, label=label, color=color)
        a.set_ylabel('PSTF energy packet [J m⁻³]'); a.set_title('(d) Radiation tensor injection'); a.legend(fontsize=9)
        for a in ax.ravel():
            a.set_xlabel('Local dimensionless time ω = η Δt')
            a.grid(alpha=.2)
            a.ticklabel_format(axis='y', style='sci', scilimits=(-3,3), useOffset=False)
        last = rows[-1]
        text = (f"Fixed triaxial shear diag(−0.4, 0.1, 0.3); path τ/qmax={last['path_depth_ratio']:.5g}; "
                f"log δ={last['log_delta']:.5g}.\nAtomic/thermal separation: Δu_thermal=0 by this recoil-free bound–bound model. "
                'This is a detached source step, not a cosmological history.')
        fig.text(.02,.015,text,fontsize=8,va='bottom')
        fig.tight_layout(rect=(0,.075,1,.93))
        png, pdf = figure_dir/f'line01_{name}.png', figure_dir/f'line01_{name}.pdf'
        if png.exists() or pdf.exists():
            raise FileExistsError('Preserve previous figures; explicit targeted amendment required')
        fig.savefig(png,dpi=180)
        fig.savefig(pdf)
        plt.close(fig)
        manifest['plots'].append({'track':name,'sample_count':81,'caption':caption,
            'data_csv':str(csv_path.relative_to(ROOT)),'data_sha256':sha(csv_path),
            'png':str(png.relative_to(ROOT)),'png_sha256':sha(png), 'png_bytes':png.stat().st_size,
            'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf), 'pdf_bytes':pdf.stat().st_size,
            'path_depth_ratio':last['path_depth_ratio'],'log_delta':last['log_delta'],
            'delta_representation':last['delta_representation']})
        OBSERVED['plot_tracks'] += 1
    dump(figure_dir/'PLOT_MANIFEST.json',manifest)
    return manifest


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help='Only after parent RUN_AUTHORIZED')
    parser.add_argument('--attempt', default='attempt001')
    args = parser.parse_args()
    if not args.execute:
        parser.error('No science executed. Supply --execute only after checkpoint A authorization.')
    if args.attempt != 'attempt001':
        parser.error('Only frozen attempt001 is permitted; new attempts require an explicit amendment')
    folder = ROOT / 'results' / args.attempt
    folder.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    code_hashes = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'code').glob('*.py'))}
    dump(folder/'START.json', {'schema':'line01.production_start.v1','utc':datetime.now(timezone.utc).isoformat(),
        'expected_science_counts':EXPECTED,'contract_sha256':sha(ROOT/'FROZEN_CONTRACT.md'),
        'code_sha256':code_hashes,'old_campaign_reruns':0,'cosmological_IVP_calls':0,'native_runtime_calls':0,
        'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,
        'scipy':scipy.__version__,'mpmath':mp.__version__})
    handles = {key: Evidence(folder/(key+'.jsonl')) for key in ('sources','local_maps','direct_checks','finite_references','rejections','plot_samples')}
    exception = None
    try:
        states, sources, native = source_rows(handles['sources'])
        dump(folder/'NATIVE_STATE_RECONSTRUCTION.json',native)
        maps = local_map_rows(handles['local_maps'])
        donor = direct_comparisons(handles['direct_checks'],states,sources)
        dump(folder/'DONOR_AST_REUSE.json',donor)
        finite_references(handles['finite_references'],maps)
        rejection_checks(handles['rejections'],states[0][1])
        plot_tracks(handles['plot_samples'],folder)
        for key, expected in EXPECTED.items():
            check('fixed_count_'+key,OBSERVED[key],expected,relation='==')
        check('map_outputs_total',model.COUNTERS['local_map_outputs'],270,relation='==')
    except BaseException:
        exception = traceback.format_exc()
        with (folder/'FAILURE_TRACEBACK.txt').open('x') as f:
            f.write(exception)
    finally:
        for handle in handles.values():
            handle.close()
        failures = [row for row in ACCEPTANCE if not row['pass']]
        dump(folder/'ACCEPTANCE.json',{'checks':ACCEPTANCE,'passed':len(ACCEPTANCE)-len(failures),
            'failed':len(failures),'failures':failures})
        metrics = {'schema':'line01.production_result.v1','status':'FAIL' if exception or failures else 'PASS',
            'counts':dict(OBSERVED),'model_counters':dict(model.COUNTERS),
            'inherited_angular_counters_for_new_rows_only':dict(model.angular.COUNTERS),
            'raw_row_counts':{k:v.rows for k,v in handles.items()},
            'acceptance_passed':len(ACCEPTANCE)-len(failures),'acceptance_failed':len(failures),
            'exception':exception,'elapsed_wall_s':time.monotonic()-start,
            'old_campaign_reruns':0,'new_cosmological_IVP_calls':0,'new_local_IVP_calls':0,'native_runtime_calls':0,
            'Physical':'HOLD','REC_U5':['HOLD_9_FAIL','HOLD_8_FAIL'],'global_convergence':'NOT_RUN',
            'production':'NOT_APPROVED','REI_activation':False,
            'numeric_accuracy_is_not_atomic_data_accuracy':True,
            'finite_case_acceptance_is_not_global_convergence':True}
        dump(folder/'METRICS.json',metrics)
        files = [p for p in sorted(folder.rglob('*')) if p.is_file()]
        dump(folder/'RAW_MANIFEST.json',{'schema':'line01.immutable_attempt_manifest.v1',
            'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],
            'preserve_original_raw_on_any_targeted_fix':True})
    print(json.dumps({'status':metrics['status'],'counts':metrics['counts'],
                      'acceptance_failed':metrics['acceptance_failed'],
                      'elapsed_wall_s':metrics['elapsed_wall_s']},indent=2))
    return 0 if metrics['status']=='PASS' else 1


if __name__ == '__main__':
    raise SystemExit(run())
