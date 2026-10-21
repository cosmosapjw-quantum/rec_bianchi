#!/usr/bin/env python3
"""Verified saved-data reducer for the 125+1 HH/Li pilot; never runs a solver.

Only the standard library and NumPy are imported. Relative CLI paths resolve
against this research directory. Same input bytes produce the same reports.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = 193
XEND = math.log(7.)
REPRESENTATIVE = 's03_m03_r03'
CONTROL = 'control_s03_m03_r03_opacity_off'
BASELINE = 's00_m02_r02'
SIGNED = ('S_F_signed', 'P_m_F_signed', 'P_r_F_signed',
          'P_total_F_signed', 'P_gamma_F_signed', 'P_nu_F_signed')
NORMS = ('Sigma_F', 'Pi_m_F', 'Pi_r_F', 'Pi_total_F', 'Pi_gamma_F', 'Pi_nu_F')
GROUPS = {'n': (0,), 'H1': (1, 2), 'D': (3, 4), 'T': (5, 6),
          'He3': (7, 8, 9), 'He4': (10, 11, 12),
          'Li6': (13, 14, 15, 16), 'Li7': (17, 18, 19, 20)}
REQUIRED_GATES = {
    'full_interval_and_samples', 'initial_physical_axes', 'finite',
    'population_positivity', 'isotope_scaled_conservation',
    'baryon_conservation', 'nonnegative_electrons', 'number_monopoles',
    'monotone_optical_depth', 'einstein_constraint', 'tensor_sum',
    'finite_angular_positivity', 'trace_energy_small'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    raw = path.read_bytes()
    return json.loads(raw), sha(raw)


def relative_path(path):
    return str(path.resolve().relative_to(ROOT))


def path_arg(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def write_json(path, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False,
                       allow_nan=False, default=native) + '\n').encode()
    path.write_bytes(data)
    return {'bytes': len(data), 'sha256': sha(data)}


def write_csv(path, rows):
    require(bool(rows), 'refuse an empty CSV')
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode()
    path.write_bytes(data)
    return {'rows': len(rows), 'bytes': len(data), 'sha256': sha(data)}


def fractions(Y, initial_Y):
    """Fractions of each isotope's fixed initial inventory; never renormalize."""
    answer = np.full(Y.shape, np.nan)
    for indices in GROUPS.values():
        denominator = float(np.sum(initial_Y[list(indices)]))
        for index in indices:
            np.divide(Y[..., index], denominator, out=answer[..., index],
                      where=denominator > 0)
    return answer


def optional(value):
    return float(value) if np.isfinite(value) else None


def load_frozen(directory, expected_count):
    frozen, digest = read_json(directory / 'FROZEN.json')
    require(frozen['schema'] == 'HHELI_CASE_FREEZE_v1', 'unknown freeze schema')
    require(bool(frozen['files']), 'empty scientific source manifest')
    require(sha(canonical(frozen['files'])) == frozen['base_identity'], 'invalid base identity')
    for name, expected in frozen['files'].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), 'source path outside project')
        require(sha(path.read_bytes()) == expected, 'frozen source changed: ' + name)
    configs = frozen['configs']
    require(len(configs) == expected_count, 'unexpected frozen case count')
    ids = [config['case_id'] for config in configs]
    require(len(set(ids)) == expected_count, 'duplicate case identifiers')
    actual_dirs = {path.name for path in (directory / 'cases').iterdir() if path.is_dir()}
    require(actual_dirs == set(ids), 'case directory set differs from frozen contract')
    return frozen, digest


def check_recovery(result, frozen, payload):
    recovery = result.get('recovery')
    if not recovery:
        return None
    require(recovery['status'] == 'DATA_ONLY_RECOVERED', 'unknown recovery status')
    require(recovery['new_ODE_solves'] == 0 and recovery['byte_identical_npz'] is True,
            'recovery is not data-only')
    old_dir = ROOT / recovery['source_case']
    require(sha((old_dir / 'trajectory.npz').read_bytes()) == sha(payload), 'recovery bytes differ')
    old_freeze, old_hash = read_json(old_dir.parents[1] / 'FROZEN.json')
    require(sha(canonical(old_freeze['files'])) == old_freeze['base_identity'], 'old freeze identity')
    expected_old = sha(canonical({'base': old_freeze['base_identity'], 'config': result['config']}))
    require(result['execution_identity_sha256'] == expected_old == recovery['original_execution_identity'],
            'recovered execution identity mismatch')
    require(set(old_freeze['files']) == set(frozen['files']), 'recovery source set changed')
    changed = [key for key in frozen['files'] if old_freeze['files'][key] != frozen['files'][key]]
    require(changed == ['code/coupled.py'], 'recovery changed more than the output writer source')
    contract_path = ROOT / recovery['contract']
    contract, contract_hash = read_json(contract_path)
    require(contract['changed_AST_nodes'] == ['atomic_json']
            and contract['new_ODE_for_recovery'] == 0, 'unapproved recovery scope')
    require(contract['old_coupled_sha256'] == old_freeze['files']['code/coupled.py']
            and contract['new_coupled_sha256'] == frozen['files']['code/coupled.py'],
            'recovery contract source hashes')
    independent_path = ROOT / 'evidence/INDEPENDENT_RECOVERY_PRECHECK.json'
    independent, independent_hash = read_json(independent_path)
    require(independent['all_module_AST_except_atomic_json_equal'] is True
            and independent['old_coupled_sha256'] == contract['old_coupled_sha256']
            and independent['current_coupled_sha256'] == contract['new_coupled_sha256'],
            'recovery independent AST receipt mismatch')
    return {'status': 'VERIFIED_DATA_ONLY_RECOVERY', 'original_freeze_sha256': old_hash,
            'contract_sha256': contract_hash, 'independent_receipt_sha256': independent_hash,
            'execution_identity_sha256': expected_old,
            'solver_counters': 'UNKNOWN_REPORT_SERIALIZATION_FAILED', 'recovery_new_ODE': 0}


def load_case(directory, frozen, config, reference):
    case_id = config['case_id']
    folder = directory / 'cases' / case_id
    result, result_hash = read_json(folder / 'RESULT.json')
    complete, complete_hash = read_json(folder / 'COMPLETE.json')
    identity = sha(canonical({'base': frozen['base_identity'], 'config': config}))
    require(result['schema'] == 'rec.rei.hheli.coupled62.v1', 'result schema: ' + case_id)
    require(result['status'] == 'COMPLETE', 'case incomplete: ' + case_id)
    require(result['config'] == config, 'result/frozen configuration mismatch: ' + case_id)
    require(result['scientific_identity_sha256'] == complete['identity'] == identity, 'case identity mismatch')
    require(complete['result_sha256'] == result_hash, 'result digest mismatch')
    require(complete['outputs'] == result['outputs'], 'completion output manifest mismatch')
    require(set(result['outputs']) == {'trajectory.npz'}, 'unexpected output set')
    gates = result['gates']
    require(REQUIRED_GATES <= set(gates) and all(value is True for value in gates.values()),
            'missing/false/nonboolean gate: ' + case_id)
    require(config['samples'] == SAMPLES and config.get('x_end', XEND) == XEND,
            'case does not request193fullnodes')
    payload = (folder / 'trajectory.npz').read_bytes()
    entry = result['outputs']['trajectory.npz']
    require(len(payload) == entry['bytes'] and sha(payload) == entry['sha256'], 'NPZ hash/size mismatch')
    with np.load(io.BytesIO(payload), allow_pickle=False) as saved:
        data = {key: saved[key] for key in saved.files}
    shapes = {'x': (SAMPLES,), 'z': (SAMPLES,), 'raw_state': (SAMPLES, 62),
              'Y': (SAMPLES, 21), 'scaled_populations': (SAMPLES, 21),
              'signed_observables': (SAMPLES, 6), 'observables_norm': (SAMPLES, 6),
              'species_names': (21,), 'A': (21,), 'q': (21,),
              'isotope_scales': (21,), 'initial_Y': (21,)}
    for key, shape in shapes.items():
        require(data[key].shape == shape, 'bad array shape ' + case_id + ':' + key)
    for key, array in data.items():
        if array.dtype.kind in 'biufc':
            require(array.dtype.kind != 'c' and np.isfinite(array).all(), 'nonfinite/complex saved data')
    x, z = data['x'], data['z']
    require(np.array_equal(x, np.linspace(0., XEND, SAMPLES)), 'not the full frozen193nodegrid')
    require(np.all(np.diff(x) > 0) and np.all(np.diff(z) < 0)
            and abs(z[0] - 20) < 1e-13 and abs(z[-1] - 2) < 1e-13
            and np.max(abs(z - (21 * np.exp(-x) - 1))) < 1e-13, 'invalid redshift grid')
    require(result['samples'] == SAMPLES and result['x_end'] == XEND
            and abs(result['z_end'] - 2) < 1e-13, 'result interval differs')
    require(data['species_names'].tolist() == reference['names'], 'species registry changed')
    for key, source in (('A', 'A'), ('q', 'q'), ('isotope_scales', 'scales'), ('initial_Y', 'initial_Y')):
        require(np.array_equal(data[key], np.asarray(reference[source])), 'metadata differs: ' + key)
    diag_names = data['diagnostic_names'].tolist()
    require(len(diag_names) == len(set(diag_names)) and data['diagnostics'].shape == (SAMPLES, len(diag_names)),
            'invalid diagnostic matrix')
    diag = {name: data['diagnostics'][:, i] for i, name in enumerate(diag_names)}
    obs = data['signed_observables']
    require(np.array_equal(data['observables_norm'], np.abs(obs)), 'norm must follow signed sum')
    require(np.max(abs(obs[:, 3] - obs[:, 1] - obs[:, 2])) < 2e-16
            and np.max(abs(obs[:, 2] - obs[:, 4] - obs[:, 5])) < 2e-16, 'stress component sum')
    require(np.array_equal(np.asarray(result['initial_signed_observables']), obs[0])
            and np.array_equal(np.asarray(result['final_signed_observables']), obs[-1]),
            'result endpoint mismatch')
    require(np.array_equal(data['raw_state'][:, 40:61], data['scaled_populations'])
            and np.array_equal(data['Y'], data['scaled_populations'] * data['isotope_scales']),
            'abundance scaling mismatch')
    require(np.array_equal(data['raw_state'][:, 61], diag['tau_T']), 'tau diagnostic mismatch')
    target = np.array([config['Sigma_F'], config['P_m_initial_target'], config['P_r_initial_target']])
    initial_error = float(np.max(abs(obs[0, :3] - target)))
    baryon_error = float(np.max(abs(data['Y'] @ data['A'] - 1)))
    min_scaled = float(np.min(data['scaled_populations']))
    isotope_errors = {}
    for name, indices in GROUPS.items():
        nominal = float(data['initial_Y'][list(indices)].sum())
        isotope_errors[name] = float(np.max(abs(data['Y'][:, indices].sum(axis=1) - nominal))
                                      / data['isotope_scales'][indices[0]])
    ne_expected = diag['nb_m3'] * (data['Y'] @ data['q'])
    ne_difference = float(np.max(abs(ne_expected - diag['ne_m3'])))
    require(initial_error < 2e-12 and baryon_error < 2e-8 and min_scaled >= -2e-8
            and max(isotope_errors.values()) < 2e-7, 'saved population/axis gate failed')
    require(np.all(diag['ne_m3'] >= 0) and np.allclose(ne_expected, diag['ne_m3'], rtol=3e-15, atol=1e-14),
            'saved neutrality mismatch')
    require(np.max(abs(data['raw_state'][:, [13, 31]] - 1)) < 2e-9
            and np.min(np.diff(diag['tau_T'])) >= -2e-10, 'number/tau saved-data gate failed')
    angular_names = [name for name in diag if name.startswith('min_') and 'angular_weight' in name]
    require(len(angular_names) == 4 and min(float(diag[k].min()) for k in angular_names) > -2e-7,
            'saved finite-angle positivity gate failed')
    require(float(diag['trace_energy_fraction'].max()) < 1e-5, 'saved trace-energy gate failed')
    recovery = check_recovery(result, frozen, payload)
    receipt = {'case_id': case_id, 'scientific_identity_sha256': identity,
               'result_sha256': result_hash, 'complete_sha256': complete_hash,
               'npz_sha256': entry['sha256'], 'npz_bytes': entry['bytes'],
               'recovery': recovery}
    metrics = {'initial_axis_error': initial_error, 'baryon_error': baryon_error,
               'min_scaled_population': min_scaled, 'isotope_scaled_errors': isotope_errors,
               'neutrality_max_abs_m3': ne_difference,
               'tensor_sum_max_abs': float(np.max(abs(obs[:, 3] - obs[:, 1] - obs[:, 2]))),
               'radiation_sum_max_abs': float(np.max(abs(obs[:, 2] - obs[:, 4] - obs[:, 5])))}
    return {'id': case_id, 'config': config, 'result': result, 'data': data,
            'diag': diag, 'fractions': fractions(data['Y'], data['initial_Y']),
            'receipt': receipt, 'metrics': metrics}


def extrema(values, ids, x, z, indices):
    lo = np.unravel_index(int(np.argmin(values)), values.shape)
    hi = np.unravel_index(int(np.argmax(values)), values.shape)
    def point(pair):
        c, j = pair
        return {'value': float(values[c, j]), 'case_id': ids[c],
                'sample_index': int(indices[j]), 'x': float(x[j]), 'z': float(z[j])}
    return {'min': point(lo), 'max': point(hi)}


def profile_comparison(on, off, x, z, absolute_floor=1e-12):
    on, off = np.asarray(on), np.asarray(off)
    difference = on - off
    k = int(np.argmax(np.abs(difference)))
    scale = float(max(np.max(np.abs(on)), np.max(np.abs(off))))
    floor = max(absolute_floor, 1e-4 * scale)
    mask = (np.abs(on) > floor) & (np.abs(off) > floor)
    relative = np.full(on.shape, np.nan)
    relative[mask] = difference[mask] / np.maximum(abs(on[mask]), abs(off[mask]))
    result = {'max_absolute_difference': float(abs(difference[k])),
              'max_abs_at': {'sample_index': k, 'x': float(x[k]), 'z': float(z[k]),
                             'on': float(on[k]), 'off': float(off[k]), 'on_minus_off': float(difference[k])},
              'endpoint': {'on': float(on[-1]), 'off': float(off[-1]),
                           'on_minus_off': float(difference[-1]), 'absolute_difference': float(abs(difference[-1]))},
              'normalized_difference': {'definition': '(on-off)/max(abs(on),abs(off))',
                  'absolute_denominator_floor': floor, 'profile_scale': scale,
                  'rule': 'Both absolute values must exceed max(absolute_floor,1e-4*profile_scale).',
                  'included_samples': int(mask.sum()), 'excluded_samples': int((~mask).sum()),
                  'max_abs': None, 'max_abs_at': None, 'endpoint': optional(relative[-1])}}
    if mask.any():
        j = int(np.nanargmax(abs(relative)))
        result['normalized_difference']['max_abs'] = float(abs(relative[j]))
        result['normalized_difference']['max_abs_at'] = {'sample_index': j, 'z': float(z[j]),
                                                        'signed_value': float(relative[j])}
    return result


def control_comparison(on, off, source_info):
    ignored = {'opacity', 'case_id'}
    require({k: v for k, v in on['config'].items() if k not in ignored}
            == {k: v for k, v in off['config'].items() if k not in ignored}, 'unpaired scientific configurations')
    require(on['config']['opacity'] is True and off['config']['opacity'] is False, 'wrong control toggle')
    x, z = on['data']['x'], on['data']['z']
    require(np.array_equal(x, off['data']['x']) and np.array_equal(z, off['data']['z']), 'control grid mismatch')
    require(np.array_equal(on['data']['raw_state'][0], off['data']['raw_state'][0]), 'control IC differs')
    output = {'schema': 'rec.hheli.control_comparison.v1', 'status': 'PASS_SAVED_DATA_COMPARISON',
        'difference_direction': 'opacity_on minus opacity_off', 'on_case': on['id'], 'off_case': off['id'],
        'same_scientific_config_except': ['opacity', 'case_id'], 'same_initial_state': True,
        'source_identity': source_info, 'samples': SAMPLES, 'x_range': [0., XEND], 'z_range': [20., float(z[-1])],
        'signed_observables': {}, 'norm_observables': {}, 'diagnostics': {}, 'chemistry': [],
        'scope': {'control': 'Distinct prospective finite model with photon Thomson collision switched off.',
            'charge_fraction': 'Y_i divided by its fixed initial isotope inventory; no diagnostic renormalization; n/T zero-inventory fractions are null.',
            'tau_off': 'Potential electron-column Thomson depth from this trajectory, integrated from z20; not applied collision depth.',
            'applied_photon_collision_amplitude_off': 0.0,
            'gamma_T_per_H_off': 'Electron-derived diagnostic remains nonzero; applied operator is zero.',
            'indirect_feedback': 'Neutrino, chemistry and geometry trajectories may change indirectly. Instantaneous gamma-only wiring does not imply identical full neutrino histories.',
            'convergence_certification': 'NOT_RUN', 'physical': 'HOLD', 'production': 'NOT_APPROVED',
            'benchmark': 0, 'reducer_new_ODE': 0}}
    for j, (signed, norm) in enumerate(zip(SIGNED, NORMS)):
        output['signed_observables'][signed] = profile_comparison(on['data']['signed_observables'][:, j],
            off['data']['signed_observables'][:, j], x, z)
        output['norm_observables'][norm] = profile_comparison(on['data']['observables_norm'][:, j],
            off['data']['observables_norm'][:, j], x, z)
    for key in ('ne_m3', 'H', 'tau_T', 'gamma_T_per_H', 'trace_energy_fraction', 'T_K', 'uv_scale'):
        floor = 1e-30 if key == 'H' else 1e-14 if key == 'trace_energy_fraction' else 1e-12
        output['diagnostics'][key] = profile_comparison(on['diag'][key], off['diag'][key], x, z, floor)
    for j, species in enumerate(on['data']['species_names']):
        item = {'species': str(species),
                'Y_per_baryon': profile_comparison(on['data']['Y'][:, j], off['data']['Y'][:, j], x, z, 1e-30),
                'charge_fraction': None}
        if np.isfinite(on['fractions'][:, j]).all() and np.isfinite(off['fractions'][:, j]).all():
            item['charge_fraction'] = profile_comparison(on['fractions'][:, j], off['fractions'][:, j], x, z, 1e-12)
        else:
            item['charge_fraction_status'] = 'UNDEFINED_ZERO_ISOTOPE_INVENTORY; Y remains recorded'
        output['chemistry'].append(item)
    output['max_absolute_charge_fraction_difference'] = float(np.nanmax(abs(on['fractions'] - off['fractions'])))
    output['max_absolute_Y_per_baryon_difference'] = float(np.max(abs(on['data']['Y'] - off['data']['Y'])))
    return output


def run_observations(directory):
    observations = []
    for path in sorted(directory.glob('RUN_*.json')):
        value, digest = read_json(path)
        counts = {}
        for entry in value.get('records', []):
            counts[entry['status']] = counts.get(entry['status'], 0) + 1
        observations.append({'path': relative_path(path), 'sha256': digest,
            'wall_seconds': value.get('wall_seconds'), 'record_status_counts': counts,
            'workers': value.get('resources', {}).get('workers'),
            'host_claim': value.get('resources', {}).get('host_claim'),
            'unsubmitted': value.get('unsubmitted')})
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='results/pilot_v2')
    parser.add_argument('--control', default='results/control')
    parser.add_argument('--output', default='results')
    args = parser.parse_args()
    source, control_dir, output_dir = map(path_arg, (args.input, args.control, args.output))
    main_frozen, main_frozen_hash = load_frozen(source, 125)
    control_frozen, control_frozen_hash = load_frozen(control_dir, 1)
    reference, reference_hash = read_json(ROOT / 'data/atomic_reference_rates.json')
    configs = sorted(main_frozen['configs'], key=lambda config: config['case_id'])
    case_ids = [config['case_id'] for config in configs]
    campaign, _ = read_json(ROOT / 'data/CAMPAIGN.json')
    expected = {tuple((s, m, r)) for s in campaign['physical_axes']['Sigma_F']
                for m in campaign['physical_axes']['P_m'] for r in campaign['physical_axes']['P_r']}
    actual = {(c['Sigma_F'], c['P_m_initial_target'], c['P_r_initial_target']) for c in configs}
    require(actual == expected and len(expected) == 125, 'not the frozen125-axis product')
    cases = [load_case(source, main_frozen, config, reference) for config in configs]
    off = load_case(control_dir, control_frozen, control_frozen['configs'][0], reference)
    by_id = {case['id']: case for case in cases}
    require(off['id'] == CONTROL and REPRESENTATIVE in by_id and BASELINE in by_id, 'missing named cases')
    representative, baseline = by_id[REPRESENTATIVE], by_id[BASELINE]
    x, z = cases[0]['data']['x'], cases[0]['data']['z']
    for case in cases + [off]:
        require(np.array_equal(case['data']['x'], x) and np.array_equal(case['data']['z'], z), 'noncommon nodes')
        require(case['data']['diagnostic_names'].tolist() == cases[0]['data']['diagnostic_names'].tolist(),
                'noncommon diagnostic schema')
    excluded_manifests = {'data/CAMPAIGN.json', 'data/CONTROL_CAMPAIGN.json'}
    mf = {k: v for k, v in main_frozen['files'].items() if k not in excluded_manifests}
    cf = {k: v for k, v in control_frozen['files'].items() if k not in excluded_manifests}
    require(mf == cf, 'control and main scientific source bytes differ')
    source_info = {'main_base_identity': main_frozen['base_identity'],
        'control_base_identity': control_frozen['base_identity'],
        'main_frozen_sha256': main_frozen_hash, 'control_frozen_sha256': control_frozen_hash,
        'on_receipt': representative['receipt'], 'off_receipt': off['receipt'],
        'all_common_scientific_source_bytes_equal': True}
    control_result = control_comparison(representative, off, source_info)
    signed = np.stack([case['data']['signed_observables'] for case in cases])
    norms = np.abs(signed)
    all_fractions = np.stack([case['fractions'] for case in cases])
    all_Y = np.stack([case['data']['Y'] for case in cases])
    summaries, time_ranges = {}, {'x': x.tolist(), 'z': z.tolist(), 'signed': {}, 'norm': {}}
    for kind, values, labels in (('signed', signed, SIGNED), ('norm', norms, NORMS)):
        summaries[kind] = {}
        for j, label in enumerate(labels):
            matrix = values[:, :, j]
            summaries[kind][label] = {
                'initial': extrema(matrix[:, :1], case_ids, x[:1], z[:1], [0]),
                'endpoint': extrema(matrix[:, -1:], case_ids, x[-1:], z[-1:], [SAMPLES - 1]),
                'all_saved_nodes': extrema(matrix, case_ids, x, z, np.arange(SAMPLES))}
            time_ranges[kind][label] = {'min': matrix.min(axis=0).tolist(), 'max': matrix.max(axis=0).tolist(),
                'min_case_id': [case_ids[k] for k in np.argmin(matrix, axis=0)],
                'max_case_id': [case_ids[k] for k in np.argmax(matrix, axis=0)]}
    gate_names = sorted(set().union(*(case['result']['gates'] for case in cases)))
    gate_counts = {name: sum(case['result']['gates'].get(name) is True for case in cases) for name in gate_names}
    recovered = [case for case in cases if case['receipt']['recovery'] is not None]
    require(len(recovered) == 1 and recovered[0]['id'] == BASELINE, 'unexpected recovery accounting')
    known_wall = [case['result']['wall_seconds'] for case in cases if case['result'].get('wall_seconds') is not None]
    known_nfev = [case['result']['nfev'] for case in cases if case['result'].get('nfev') is not None]
    diagnostic_ranges = {}
    for key in cases[0]['diag']:
        matrix = np.stack([case['diag'][key] for case in cases])
        diagnostic_ranges[key] = {
            'initial': extrema(matrix[:, :1], case_ids, x[:1], z[:1], [0]),
            'endpoint': extrema(matrix[:, -1:], case_ids, x[-1:], z[-1:], [SAMPLES - 1]),
            'all_saved_nodes': extrema(matrix, case_ids, x, z, np.arange(SAMPLES))}
    cancellations = []
    for i, case in enumerate(cases):
        pm, pr = signed[i, :, 1], signed[i, :, 2]
        denominator = abs(pm) + abs(pr)
        mask = (pm * pr < 0) & (denominator > 1e-10)
        if mask.any():
            ratio = np.full(SAMPLES, np.inf)
            ratio[mask] = abs(pm[mask] + pr[mask]) / denominator[mask]
            j = int(np.argmin(ratio))
            cancellations.append({'case_id': case['id'], 'sample_index': j, 'z': float(z[j]),
                'P_m_signed': float(pm[j]), 'P_r_signed': float(pr[j]),
                'total_norm': float(abs(pm[j] + pr[j])), 'sum_component_norms': float(denominator[j]),
                'cancellation_ratio': float(ratio[j]), 'initial_axes': [case['config'][k] for k in
                    ('Sigma_F', 'P_m_initial_target', 'P_r_initial_target')]})
    cancellations.sort(key=lambda row: (row['cancellation_ratio'], row['case_id']))
    snapshots = []
    for target_z in (20., 10., 8., 6., 4., 2.):
        j = int(np.argmin(abs(z - target_z)))
        snapshots.append({'requested_z': target_z, 'saved_z': float(z[j]), 'sample_index': j,
            'sampling': 'nearest stored redshift; no interpolation',
            'signed': dict(zip(SIGNED, representative['data']['signed_observables'][j].tolist())),
            'norm': dict(zip(NORMS, representative['data']['observables_norm'][j].tolist())),
            'diagnostics': {key: float(value[j]) for key, value in representative['diag'].items()},
            'species': [{'name': name, 'Y_per_baryon': float(representative['data']['Y'][j, k]),
                         'charge_fraction': optional(representative['fractions'][j, k])}
                        for k, name in enumerate(reference['names'])]})
    species_ranges = []
    for j, name in enumerate(reference['names']):
        active = np.isfinite(all_fractions[:, -1, j]).all()
        species_ranges.append({'name': name, 'A': reference['A'][j], 'q': reference['q'][j],
            'Y_endpoint': extrema(all_Y[:, -1:, j], case_ids, x[-1:], z[-1:], [SAMPLES - 1]),
            'charge_fraction_endpoint': extrema(all_fractions[:, -1:, j], case_ids, x[-1:], z[-1:],
                [SAMPLES - 1]) if active else None,
            'fraction_status': 'DEFINED' if active else 'UNDEFINED_ZERO_ISOTOPE_INVENTORY'})
    endpoints, species_endpoints = [], []
    for i, case in enumerate(cases):
        row = {'case_id': case['id'], 'scientific_identity_sha256': case['receipt']['scientific_identity_sha256'],
               'Sigma_F_target': case['config']['Sigma_F'], 'P_m_F_target': case['config']['P_m_initial_target'],
               'P_r_F_target': case['config']['P_r_initial_target'], 'matter_A': case['config']['matter_A'],
               'radiation_A': case['config']['radiation_A'], 'z_endpoint': float(z[-1])}
        row.update({label + '_initial': float(signed[i, 0, j]) for j, label in enumerate(SIGNED)})
        row.update({label + '_endpoint': float(signed[i, -1, j]) for j, label in enumerate(SIGNED)})
        row.update({label + '_endpoint': float(norms[i, -1, j]) for j, label in enumerate(NORMS)})
        row.update({key + '_endpoint': float(value[-1]) for key, value in case['diag'].items()})
        row.update(wall_seconds=case['result'].get('wall_seconds'), nfev=case['result'].get('nfev'),
                   data_only_recovered=case['receipt']['recovery'] is not None)
        endpoints.append(row)
        for j, name in enumerate(reference['names']):
            species_endpoints.append({'case_id': case['id'], 'species': name,
                'A': reference['A'][j], 'q': reference['q'][j], 'z': float(z[-1]),
                'Y_per_baryon': float(all_Y[i, -1, j]), 'charge_fraction': optional(all_fractions[i, -1, j]),
                'fraction_status': 'DEFINED' if np.isfinite(all_fractions[i, -1, j]) else 'UNDEFINED_ZERO_INVENTORY'})
    evolution = []
    for j in range(SAMPLES):
        row = {'case_id': REPRESENTATIVE, 'sample_index': j, 'x': float(x[j]), 'z': float(z[j])}
        row.update(zip(SIGNED, representative['data']['signed_observables'][j].tolist()))
        row.update(zip(NORMS, representative['data']['observables_norm'][j].tolist()))
        row.update({key: float(value[j]) for key, value in representative['diag'].items()})
        for k, name in enumerate(reference['names']):
            row['Y_' + name] = float(representative['data']['Y'][j, k])
            row['fraction_' + name] = optional(representative['fractions'][j, k])
        evolution.append(row)
    baseline_max = {label: float(np.max(abs(baseline['data']['signed_observables'][:, j])))
                    for j, label in enumerate(SIGNED)}
    baseline_sources, _ = read_json(ROOT / 'provenance/BASELINE_SOURCES.json')
    atomic_sources, _ = read_json(ROOT / 'provenance/atomic_sources.json')
    summary = {'schema': 'rec.hheli.pilot_summary.v1', 'status': 'PASS_VERIFIED_SAVED_125_PLUS_1',
        'reducer': {'path': relative_path(Path(__file__)), 'sha256': sha(Path(__file__).read_bytes()),
                    'scientific_modules_imported': [], 'solver_calls': 0, 'new_ODE': 0, 'benchmark': 0},
        'verification': {'main_complete': 125, 'control_complete': 1, 'nonempty_required_gate_count': len(REQUIRED_GATES),
            'main_gate_pass_counts': gate_counts, 'control_gates': off['result']['gates'],
            'frozen_file_hashes_checked': True, 'completion_result_npz_hashes_checked': True,
            'common_full193nodes': True, 'cartesian125axes_verified': True,
            'max_initial_axis_error': max(case['metrics']['initial_axis_error'] for case in cases),
            'max_baryon_error': max(case['metrics']['baryon_error'] for case in cases),
            'max_isotope_scaled_error': max(max(case['metrics']['isotope_scaled_errors'].values()) for case in cases),
            'min_scaled_population': min(case['metrics']['min_scaled_population'] for case in cases),
            'max_neutrality_saved_difference_m3': max(case['metrics']['neutrality_max_abs_m3'] for case in cases),
            'max_tensor_sum_saved_difference': max(case['metrics']['tensor_sum_max_abs'] for case in cases),
            'einstein_constraint': 'All original receipt gates true; not recomputed from a new scientific model call.'},
        'source_identity': {'main_directory': relative_path(source), 'control_directory': relative_path(control_dir),
            'main_base_identity': main_frozen['base_identity'], 'control_base_identity': control_frozen['base_identity'],
            'main_frozen_sha256': main_frozen_hash, 'control_frozen_sha256': control_frozen_hash,
            'frozen_scientific_files': main_frozen['files'], 'atomic_reference_sha256': reference_hash,
            'baseline_source_records': baseline_sources['files'],
            'atomic_reused_source_records': atomic_sources['reused_files'],
            'case_receipts': [case['receipt'] for case in cases], 'control_receipt': off['receipt']},
        'execution_accounting': {'unique_main_IVPs': 125, 'first_main_IVP_output_only_recovered': 1,
            'remaining_main_fresh_IVPs': 124, 'distinct_opacity_off_control_IVPs': 1, 'unique_total_IVPs': 126,
            'new_ODE_for_output_recovery': 0, 'old_campaign_reruns': 0, 'benchmark_runs': 0,
            'first_IVP_actual_solver_counts_and_wall_seconds': None,
            'first_IVP_missing_count_reason': 'Report serialization failed after trajectory write; no inferred replacement counts.',
            'main_case_wall_seconds_observed': {'known_cases': len(known_wall), 'unknown_cases': 125-len(known_wall),
                'min': min(known_wall), 'max': max(known_wall), 'sum_known': math.fsum(known_wall)},
            'main_known_nfev': {'known_cases': len(known_nfev), 'sum': sum(known_nfev)},
            'control_wall_seconds_observed': off['result']['wall_seconds'],
            'main_run_receipts': run_observations(source), 'control_run_receipts': run_observations(control_dir),
            'performance_interpretation': 'Observed execution timing only; no measured speedup, scaling benchmark or missing-time estimate.'},
        'grid': {'samples': SAMPLES, 'x_range': [0., XEND], 'z_range': [20., float(z[-1])],
                 'x_binary64_sha256': sha(x.tobytes()), 'z_binary64_sha256': sha(z.tobytes())},
        'observable_ranges': summaries, 'per_saved_time_ranges': time_ranges, 'diagnostic_ranges': diagnostic_ranges,
        'isotropic_baseline': {'case_id': BASELINE, 'max_abs_signed_observables': baseline_max,
            'maximum_over_all_six': max(baseline_max.values()),
            'interpretation': 'Observed numerical residual of the zero-anisotropy seed; not a detected physical anisotropy or universal error bound.'},
        'cancellation': {'definition': 'abs(Pm+Pr)/(abs(Pm)+abs(Pr)), opposite signed components only',
            'minimum_sum_component_norms': 1e-10, 'distinct_case_examples': cancellations[:8],
            'eligible_cases': len(cancellations), 'scope': 'Saved-node examples; no zero-location interpolation or continuous-time certification.'},
        'representative': {'case_id': REPRESENTATIVE, 'config': representative['config'],
            'snapshots': snapshots, 'full_evolution_csv': 'REPRESENTATIVE_EVOLUTION.csv'},
        'species_endpoint_ranges': species_ranges,
        'control_key_results': {'comparison_file': 'CONTROL_COMPARISON.json',
            'signed_max_abs_differences': {label: control_result['signed_observables'][label]['max_absolute_difference'] for label in SIGNED},
            'signed_endpoint_on_minus_off': {label: control_result['signed_observables'][label]['endpoint']['on_minus_off'] for label in SIGNED},
            'max_ne_difference_m3': control_result['diagnostics']['ne_m3']['max_absolute_difference'],
            'max_charge_fraction_difference': control_result['max_absolute_charge_fraction_difference'],
            'tau_off_is_potential_column': True, 'applied_collision_off': 0.},
        'scope': {'physical': 'HOLD', 'global_convergence': 'NOT_RUN', 'production': 'NOT_APPROVED',
            'REC_U5': 'HOLD_9_FAIL/HOLD_8_FAIL', 'REI_activation': False,
            'model': 'Conditional prescribedT/UV, finite photo/RR/DR, single-photoelectron yield, test-fluid gas.',
            'species': 'Explicit21states; n/T zero inventory, no all-nuclear-isotopes or completeEoR claim.',
            'charge_fraction': 'Y_i divided by its fixed initial isotope inventory; no diagnostic renormalization; n/T zero-inventory fractions are null.',
            'trace_energy': 'Instantaneous omitted-energy ratio; no accumulated-error certificate.',
            'finite_angular_gate': 'Saved193times and129angles; no continuous-time/angle positivity theorem.',
            'time_optical_depth': 'Elapsed time and tau accumulate from z20, not from the Big Bang or z0.'}}
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    outputs['ENDPOINTS.csv'] = write_csv(output_dir / 'ENDPOINTS.csv', endpoints)
    outputs['SPECIES_ENDPOINTS.csv'] = write_csv(output_dir / 'SPECIES_ENDPOINTS.csv', species_endpoints)
    outputs['REPRESENTATIVE_EVOLUTION.csv'] = write_csv(output_dir / 'REPRESENTATIVE_EVOLUTION.csv', evolution)
    outputs['CONTROL_COMPARISON.json'] = write_json(output_dir / 'CONTROL_COMPARISON.json', control_result)
    summary['artifacts'] = outputs
    write_json(output_dir / 'SUMMARY.json', summary)
    print(json.dumps({'status': summary['status'], 'main_cases': len(cases), 'control_cases': 1,
        'samples_per_case': SAMPLES, 'aggregate_gates': gate_counts,
        'max_trace_energy_fraction': diagnostic_ranges['trace_energy_fraction']['all_saved_nodes']['max']['value'],
        'max_baryon_error': summary['verification']['max_baryon_error'],
        'baseline_max_abs': summary['isotropic_baseline']['maximum_over_all_six'],
        'strongest_saved_cancellation': cancellations[0] if cancellations else None,
        'control_max_abs': summary['control_key_results']['signed_max_abs_differences'],
        'max_ne_difference_m3': summary['control_key_results']['max_ne_difference_m3'],
        'max_charge_fraction_difference': summary['control_key_results']['max_charge_fraction_difference'],
        'summary': str(output_dir / 'SUMMARY.json')}, default=native))


if __name__ == '__main__':
    main()
