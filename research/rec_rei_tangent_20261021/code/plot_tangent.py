"""Plot measured tangent diagnostics, or future completed augmented IVPs.

Default input: the frozen 200-state verifier and the three-node tiny wiring
run. With --ncp-output, actual COMPLETE runner receipts with a nested COMPLETED
integration and hash-bound tangent.npz are plotted. This script never imports
a solver, constructs a model or runs an IVP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import ScalarFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = '3b85dedce84d37b3e165da00685a8a984950aafe'
COLORS = ['#1b6a91', '#c15a21', '#378153', '#8b4e91']
OBSERVABLES = [r'$S_F$', r'$P_{m,F}$', r'$P_{r,F}$', r'$P_{m,F}+P_{r,F}$']
SEEDS = [r'$S_{F,i}$', r'$P_{m,F,i}$', r'$P_{r,F,i}$']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_npz(path):
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key].copy() for key in data.files}


def require_shape(data, key, shape):
    array = data[key]
    if array.shape != shape or np.iscomplexobj(array) or not np.isfinite(array).all():
        raise ValueError('INVALID_PLOT_ARRAY:' + key)


def configure():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 10.5,
        'axes.titlesize': 12, 'axes.labelsize': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.axisbelow': True, 'grid.alpha': .22,
        'savefig.dpi': 180, 'pdf.fonttype': 42, 'ps.fonttype': 42,
    })


def redshift_axis(axis):
    axis.set_xlim(20.5, 1.5)
    axis.set_xticks([20, 15, 10, 5, 2])
    axis.set_xlabel('Mean redshift  z')
    axis.grid(True, which='major')


def save_pair(fig, output, stem):
    files = []
    for extension in ('png', 'pdf'):
        path = output / (stem + '.' + extension)
        if path.exists():
            raise FileExistsError('Plot output already exists: ' + str(path))
        metadata = {'Creator': 'plot_tangent.py'} if extension == 'pdf' else None
        fig.savefig(path, bbox_inches='tight', facecolor='white', metadata=metadata)
        files.append({'file': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)})
    plt.close(fig)
    return files


def representative_cases(axes):
    requested = [(0., .0003, -.0003), (0., -.0003, .0003),
                 (.003, -.0003, -.001), (.1, .0003, .001)]
    selected = []
    for target in requested:
        matches = np.flatnonzero(np.all(axes == np.array(target), axis=1))
        if len(matches) != 1:
            raise ValueError('REPRESENTATIVE_CASE_NOT_UNIQUE:' + str(target))
        selected.append(int(matches[0]))
    return selected


def plot_local_partials(data, output):
    fig, panels = plt.subplots(1, 3, figsize=(15.2, 4.9))
    selected = representative_cases(data['axes'])
    quantities = [-data['moment_pi_b'], data['rhs_amplitude'][:, 2],
                  data['observable_amplitude'][:, 1]]
    titles = ['Restoring packet-stress slope', 'Direct matter-amplitude forcing',
              'Normalized matter-stress response']
    labels = [r'$-\partial_b\widehat p_m$  (fixed $x,A$)',
              r'$\partial_A F_v$  (fixed $x,y$)',
              r'$\partial_A P_{m,F}$  (fixed $x,y$)']
    for panel, values, title, label in zip(panels, quantities, titles, labels):
        if np.any(values <= 0):
            raise ValueError('EXPECTED_POSITIVE_LOCAL_DIAGNOSTIC_CHANGED')
        for case in range(40):
            mask = data['case_index'] == case
            panel.plot(data['z'][mask], values[mask], color='#b8c0c7', alpha=.55,
                       linewidth=.7, marker='.', markersize=3, zorder=1)
        for color, case in zip(COLORS, selected):
            mask = data['case_index'] == case
            panel.plot(data['z'][mask], values[mask], color=color, linewidth=1.45,
                       marker='o', markersize=4.2, fillstyle='none', zorder=3)
        panel.set_yscale('log')
        panel.set_title(title)
        panel.set_ylabel(label)
        redshift_axis(panel)
    legend_labels = []
    for case in selected:
        s, m, r = data['axes'][case]
        legend_labels.append(r'$(S_i,10^4P_{m,i},10^4P_{r,i})=$'
                             + f'({s:g}, {1e4*m:+g}, {1e4*r:+g})')
    handles = [plt.Line2D([], [], color=color, marker='o', fillstyle='none',
                         linewidth=1.45, markersize=4.2) for color in COLORS]
    handles.append(plt.Line2D([], [], color='#b8c0c7', linewidth=1.2))
    legend_labels.append('All 40 saved cases')
    fig.legend(handles, legend_labels, loc='lower center', bbox_to_anchor=(.5, -.055),
               ncol=3, frameon=False, fontsize=9.2)
    fig.suptitle('Local partial derivatives on existing z = 20 to 2 states',
                 fontsize=15, y=1.02)
    fig.text(.5, .96, '40 cases × 5 stored epochs | finite L8, 24×12 Gauss3 | no new trajectory solve',
             ha='center', fontsize=10.5)
    fig.text(.5, -.105,
             r'$\widehat p_m=p_m/\rho_{m,\mathrm{ref}}$,  $v=s/H_{\mathrm{ref}}$,  $F_v=dv/dx$,  '
             r'$x=\ln(a/a_{\mathrm{ref}})$.  Lines only connect stored samples.',
             ha='center', fontsize=9.6)
    fig.text(.5, -.15, 'These are fixed-state partial derivatives; full initial-seed trajectory responses require the augmented IVP.',
             ha='center', fontsize=9.6)
    fig.subplots_adjust(left=.065, right=.985, top=.86, bottom=.16, wspace=.36)
    files = save_pair(fig, output, '01_local_partials_on_saved_states')
    return files, {'representative_case_indices': selected,
                   'representative_case_ids': [str(data['case_ids'][i]) for i in selected],
                   'local_pi_b_range': [float(data['moment_pi_b'].min()), float(data['moment_pi_b'].max())],
                   'interpretation': 'Fixed-x/A packet slope and fixed-x/y amplitude partials at stored states; not integrated sensitivity.'}


def epoch_max(data, values):
    epochs = np.unique(data['stored_index'])
    redshifts, maxima = [], []
    for epoch in epochs:
        mask = data['stored_index'] == epoch
        z = data['z'][mask]
        if not np.allclose(z, z[0], rtol=0., atol=1e-12):
            raise ValueError('MIXED_REDSHIFT_AT_STORED_EPOCH')
        redshifts.append(float(z[0]))
        maxima.append(float(np.max(values[mask])))
    return np.asarray(redshifts), np.asarray(maxima)


def plot_validation(data, receipt, tiny, tiny_receipt, output):
    fig, panels = plt.subplots(1, 3, figsize=(15.5, 6.5),
                               gridspec_kw={'width_ratios': [1.1, 1., 1.15]})
    first, second, third = panels
    fields = [('state_jvp_scaled_error', 'State JVP'),
              ('amplitude_jvp_scaled_error', 'Direct A forcing'),
              ('observable_jvp_scaled_error', 'Observable JVP'),
              ('observable_amplitude_scaled_error', 'Observable direct A')]
    for color, (key, label) in zip(COLORS, fields):
        z, error = epoch_max(data, data[key])
        first.plot(z, error, color=color, marker='o', markersize=4, label=label)
    limit = receipt['metrics']['state_jvp']['tolerance']
    first.axhline(limit, color='#303030', linestyle='--', linewidth=1.2,
                  label=f'Frozen limit {limit:.0e}')
    first.set_yscale('log')
    first.set_ylim(2e-17, 1e-7)
    first.set_ylabel(r'Max. $|D_{\rm analytic}-D_{\rm FD}|/\max(1,|D_{\rm FD}|)$')
    first.set_title('Original-owner finite differences')
    first.legend(loc='upper left', bbox_to_anchor=(0., -.23),
                 ncol=2, fontsize=8.3, frameon=False, borderaxespad=0.,
                 handlelength=1.8, columnspacing=1.1)
    redshift_axis(first)
    ratios = data['duality_limit_fraction']
    positive = ratios > 0.
    repeated_z = np.repeat(data['z'][:, None], ratios.shape[1], axis=1)
    second.scatter(repeated_z[positive], ratios[positive], s=8, color=COLORS[0],
                   alpha=.3, label='Finite direction/cotangent checks')
    z, maximum = epoch_max(data, ratios)
    second.plot(z, maximum, color='#202c35', marker='o', linewidth=1.5,
                label='Maximum at each epoch')
    second.axhline(1., color='#303030', linestyle='--', linewidth=1.2,
                   label='Frozen limit')
    second.set_yscale('log')
    min_positive = float(np.min(ratios[positive]))
    second.set_ylim(min_positive*.65, 2.)
    second.set_ylabel('JVP/VJP duality residual / allowed roundoff')
    second.set_title('Independent transpose-action check')
    second.text(.03, .04, f'{int(np.size(ratios)-np.count_nonzero(positive))} exact zeros omitted on log scale',
                transform=second.transAxes, fontsize=8.4)
    second.legend(loc='upper left', bbox_to_anchor=(0., -.23),
                  fontsize=8.3, frameon=False, borderaxespad=0.)
    redshift_axis(second)
    response = tiny['observable_tangent_signed'][:, :3, :]
    delta = response[-1] - response[0]
    scale = float(np.max(np.abs(delta)))
    image = third.imshow(delta, cmap='RdBu_r', norm=TwoSlopeNorm(vmin=-scale, vcenter=0., vmax=scale),
                         aspect='equal')
    third.set_xticks(range(3), SEEDS)
    third.set_yticks(range(3), OBSERVABLES[:3])
    third.set_xlabel('Initial signed seed')
    third.set_ylabel('Signed observable')
    for row in range(3):
        for col in range(3):
            text_color = 'white' if abs(delta[row, col]) > .58*scale else '#14202a'
            third.text(col, row, f'{delta[row,col]:+.2e}', ha='center', va='center',
                        fontsize=9, color=text_color)
    third.set_title(r'Tiny IVP: $\Delta R=R(x_f)-R(0)$' + '\n'
                    + f'z: {tiny["z"][0]:.0f} → {tiny["z"][-1]:.6f}', fontsize=11)
    colorbar = fig.colorbar(image, ax=third, fraction=.046, pad=.04)
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((-2, 2))
    colorbar.formatter = formatter
    colorbar.update_ticks()
    colorbar.set_label(r'$\Delta R$', fontsize=10)
    fig.suptitle('Finite-set validation and short-interval response wiring', fontsize=15, y=.985)
    fig.text(.5, .925, 'FD: 200 stored states × 3 directions | JVP/VJP uses the stated 512-epsilon bound',
             ha='center', fontsize=10.4)
    fig.text(.5, .09,
             r'$R_{ij}=\partial O_i/\partial\theta_j$ (unscaled).  Synthetic seed '
             + '(0.002, 0.00007, −0.0002); x ∈ [0, 0.0001], three output nodes.',
             ha='center', fontsize=9.5)
    fig.text(.5, .035, 'The tiny run checks the implementation connection. These finite diagnostics do not certify long-window or continuum error.',
             ha='center', fontsize=9.5)
    fig.subplots_adjust(left=.065, right=.965, top=.84, bottom=.36, wspace=.42)
    files = save_pair(fig, output, '02_finite_set_validation_and_tiny_response')
    return files, {'tiny_x_interval': tiny_receipt['x_interval'],
                   'tiny_z_interval': [float(tiny['z'][0]), float(tiny['z'][-1])],
                   'tiny_response_delta': delta.tolist(),
                   'max_duality_limit_fraction': float(ratios.max()),
                   'new_ODE_by_plotter': 0, 'input_tiny_ODE_solves': tiny_receipt['new_ODE_solves']}


def default_plots(output):
    paths = {
        'verification': ROOT / 'results/verification_v1/VERIFICATION.json',
        'diagnostics': ROOT / 'results/verification_v1/VERIFICATION_DIAGNOSTICS.npz',
        'tiny_receipt': ROOT / 'results/wiring_v1/TINY_WIRING.json',
        'tiny_data': ROOT / 'results/wiring_v1/TINY_WIRING.npz',
    }
    receipt = json.loads(paths['verification'].read_text())
    tiny_receipt = json.loads(paths['tiny_receipt'].read_text())
    if receipt['status'] != 'PASS_SCOPED' or not all(receipt['gates'].values()):
        raise ValueError('VERIFICATION_NOT_PASSED')
    if tiny_receipt['status'] != 'PASS_SCOPED_WIRING' or not all(tiny_receipt['checks'].values()):
        raise ValueError('TINY_WIRING_NOT_PASSED')
    if receipt['source_commit'] != SOURCE or tiny_receipt['source_commit'] != SOURCE:
        raise ValueError('PLOT_SOURCE_IDENTITY_MISMATCH')
    if sha256(paths['diagnostics']) != receipt['diagnostics']['sha256']:
        raise ValueError('VERIFICATION_ARRAY_HASH_MISMATCH')
    data, tiny = load_npz(paths['diagnostics']), load_npz(paths['tiny_data'])
    for key, shape in (('axes', (40, 3)), ('z', (200,)), ('rhs_amplitude', (200, 40)),
                       ('observable_amplitude', (200, 4)), ('moment_pi_b', (200,)),
                       ('duality_limit_fraction', (200, 3))):
        require_shape(data, key, shape)
    require_shape(tiny, 'observable_tangent_signed', (3, 4, 3))
    require_shape(tiny, 'x', (3,))
    require_shape(tiny, 'z', (3,))
    files1, summary1 = plot_local_partials(data, output)
    files2, summary2 = plot_validation(data, receipt, tiny, tiny_receipt, output)
    return files1 + files2, {'local_partials': summary1, 'validation': summary2}, paths


def completed_case_plots(ncp_output, output):
    files, records, input_paths = [], [], {}
    manifest_path = ncp_output / 'RUN_MANIFEST.json'
    identity = json.loads(manifest_path.read_text())
    if identity.get('schema') != 'rec_bianchi.tangent_run.v1' or identity.get('source_commit') != SOURCE:
        raise ValueError('UNKNOWN_TANGENT_RUN_MANIFEST')
    payload = {key: value for key, value in identity.items() if key != 'sha256'}
    identity_digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    if identity.get('sha256') != identity_digest:
        raise ValueError('RUN_MANIFEST_IDENTITY_HASH_MISMATCH')
    input_paths['RUN_MANIFEST.json'] = manifest_path
    seen_cases = set()
    for receipt_path in sorted(ncp_output.rglob('RESULT.json')):
        wrapper = json.loads(receipt_path.read_text())
        if wrapper.get('status') != 'COMPLETE':
            continue
        if (wrapper.get('schema') != 'rec_bianchi.tangent_result.v1'
                or wrapper.get('identity_sha256') != identity_digest
                or wrapper.get('source_code_identity') != identity
                or wrapper.get('task_exit_code') != 0):
            raise ValueError('COMPLETED_CASE_RUN_IDENTITY_MISMATCH:' + str(receipt_path))
        case = wrapper['case']
        case_key = str(case['id'])
        if case_key != receipt_path.parent.name or case_key in seen_cases:
            raise ValueError('DUPLICATE_OR_MISPLACED_COMPLETED_CASE:' + case_key)
        seen_cases.add(case_key)
        receipt = wrapper['integration']
        if receipt.get('status') != 'COMPLETED':
            raise ValueError('RUNNER_AND_INTEGRATION_STATUS_MISMATCH')
        if receipt.get('schema') != 'rec.tangent.execution.v1' or receipt.get('source_commit') != SOURCE:
            raise ValueError('UNKNOWN_COMPLETED_CASE_SCHEMA:' + str(receipt_path))
        if not receipt.get('checks') or not all(receipt['checks'].values()):
            raise ValueError('COMPLETED_CASE_HAS_FAILED_CHECK:' + str(receipt_path))
        raw_path = receipt_path.parent / 'tangent.npz'
        raw_digest = sha256(raw_path)
        declared_digest = wrapper.get('npz_sha256')
        if declared_digest != raw_digest:
            raise ValueError('COMPLETED_CASE_RAW_HASH_MISMATCH:' + str(raw_path))
        data = load_npz(raw_path)
        count = int(receipt['epochs'])
        join = math.log(21./5.)
        expected_grid = np.r_[np.linspace(0., join, 121),
                              np.linspace(join, math.log(7.), 33)[1:]]
        x_interval = np.asarray(receipt.get('x_interval', []), dtype=float)
        z_interval = np.asarray(receipt.get('redshift_interval', []), dtype=float)
        if (count != 153 or x_interval.shape != (2,) or z_interval.shape != (2,)
                or not np.allclose(x_interval, [0., math.log(7.)], rtol=0., atol=2e-14)
                or not np.allclose(z_interval, [20., 2.], rtol=0., atol=2e-14)):
            raise ValueError('COMPLETED_CASE_FULL_WINDOW_CONTRACT_MISMATCH')
        for key, shape in (('axes', (3,)), ('x', (count,)), ('z', (count,)),
                           ('observables_signed', (count, 4)),
                           ('observable_tangent_signed', (count, 4, 3))):
            require_shape(data, key, shape)
        if not (np.array_equal(data['axes'], receipt['axes'])
                and np.array_equal(data['axes'], case['axes'])):
            raise ValueError('COMPLETED_CASE_SEED_MISMATCH')
        if not np.allclose(data['x'], expected_grid, rtol=0., atol=2e-14):
            raise ValueError('COMPLETED_CASE_FULL_GRID_CONTRACT_MISMATCH')
        if not (np.all(np.diff(data['x']) > 0) and np.all(np.diff(data['z']) < 0)):
            raise ValueError('COMPLETED_CASE_TIME_ORDER_INVALID')
        if not np.allclose(data['z'], 21.*np.exp(-data['x'])-1., rtol=0., atol=5e-13):
            raise ValueError('COMPLETED_CASE_REDSHIFT_MAPPING_INVALID')
        obs, tangent = data['observables_signed'], data['observable_tangent_signed']
        if not (np.array_equal(obs[:, 3], obs[:, 1]+obs[:, 2])
                and np.array_equal(tangent[:, 3], tangent[:, 1]+tangent[:, 2])):
            raise ValueError('COMPLETED_CASE_SIGNED_SUM_INVALID')
        fig, panels = plt.subplots(2, 2, figsize=(12.5, 8.))
        panels = panels.ravel()
        for component, (color, name) in enumerate(zip(COLORS, OBSERVABLES)):
            panels[0].plot(data['z'], obs[:, component], color=color, label=name)
            for seed in range(3):
                panels[seed+1].plot(data['z'], tangent[:, component, seed], color=color, label=name)
        panels[0].set_title('Signed observables')
        panels[0].set_ylabel('Dimensionless signed value')
        for seed in range(3):
            panels[seed+1].set_title('Response to ' + SEEDS[seed])
            panels[seed+1].set_ylabel(r'$\partial O / \partial\theta_' + str(seed+1) + r'$ (unscaled)')
        for axis in panels:
            axis.axhline(0., color='#888888', linewidth=.7)
            axis.set_xlim(float(data['z'][0]), float(data['z'][-1]))
            axis.set_xlabel('Mean redshift  z')
            axis.grid(True)
        panels[0].legend(ncol=2, frameon=False, fontsize=9)
        axes = ', '.join(f'{a:g}' for a in data['axes'])
        fig.suptitle('Completed augmented-IVP histories | initial signed seeds = (' + axes + ')', fontsize=13)
        fig.text(.5, .01, 'Matter and radiation remain signed; total is formed by adding components. Local solver tolerances do not give a global error certificate.',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=(0., .035, 1., .95))
        safe_key = ''.join(c if c.isalnum() or c in '_-' else '_' for c in case_key)
        stem = 'ncp_response_' + safe_key
        files.extend(save_pair(fig, output, stem))
        input_paths[case_key + '/RESULT.json'] = receipt_path
        input_paths[case_key + '/tangent.npz'] = raw_path
        records.append({'case': case_key, 'axes': data['axes'].tolist(), 'epochs': count,
                        'raw_sha256': raw_digest, 'run_identity_sha256': identity_digest,
                        'receipt_raw_hash_verified': True})
    if not records:
        raise ValueError('NO_COMPLETED_TANGENT_CASES_TO_PLOT')
    return files, {'completed_cases': records}, input_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'figures')
    parser.add_argument('--ncp-output', type=Path,
                        help='Read actual COMPLETE RESULT.json + hash-bound tangent.npz cases; no local fixture plots.')
    parser.add_argument('--record', type=Path,
                        help='Create-only plot receipt (default: evidence/PLOT_BUILD.json, or output/PLOT_BUILD.json with --ncp-output).')
    args = parser.parse_args()
    output = args.output.resolve()
    record_path = args.record or (output / 'PLOT_BUILD.json' if args.ncp_output
                                  else ROOT / 'evidence/PLOT_BUILD.json')
    if record_path.exists():
        raise FileExistsError('Plot receipt already exists: ' + str(record_path))
    output.mkdir(parents=True, exist_ok=True)
    configure()
    if args.ncp_output:
        files, summary, inputs = completed_case_plots(args.ncp_output.resolve(), output)
    else:
        files, summary, inputs = default_plots(output)
    record = {
        'schema': 'rec.tangent.plot_build.v1', 'status': 'BUILT_PENDING_VISUAL_REVIEW',
        'mode': 'completed_augmented_cases' if args.ncp_output else 'saved_state_and_tiny_wiring',
        'files': files, 'summary': summary,
        'inputs': {name: {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)}
                   for name, path in inputs.items()},
        'code_sha256': sha256(__file__),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
        'new_ODE_by_plotter': 0, 'new_NCP_by_plotter': 0, 'benchmarks': 0,
        'physical': 'HOLD', 'global_convergence': 'NOT_RUN', 'production': 'NOT_APPROVED',
    }
    record_path.parent.mkdir(parents=True, exist_ok=True)
    with record_path.open('x') as stream:
        json.dump(record, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': record['status'], 'figures': len(files)//2,
                      'receipt': str(record_path), 'mode': record['mode']}))


if __name__ == '__main__':
    main()
