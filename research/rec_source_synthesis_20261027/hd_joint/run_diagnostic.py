#!/usr/bin/env python3
"""One bounded actual-source diagnostic/control/reference/figure pass."""
import argparse
import csv
from dataclasses import asdict
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from joint_diagnostic import joint_thermal
from decimal_reference import decimal_reference
from targeted_controls import run_controls
from plot_saved import plot_saved

OWN = Path(__file__).resolve().parent
REPO = OWN.parents[2]
SOURCE_SHA = '0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
PARSER_SHA = 'ef10b34e1891755334083340b84ff1e298151df720c13f008b3762505813e275'
GATE_EVIDENCE_SHA = '6c0b2328688b9db4ee2ed61a057643e05ae40a449ad5514a74a19ca3cf11ea22'
CONTRACT_SHA = '7dd2e930cad8bf919a9dbbf90a0426f76ea00eaf6eabf16f3d677b8726d1364e'
TOLERANCE = 128 * sys.float_info.epsilon


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def load_pinned(path, expected_sha, expected_bytes=None):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha or (expected_bytes is not None and len(data) != expected_bytes):
        raise RuntimeError('IMMUTABLE_SOURCE_IDENTITY_MISMATCH: ' + str(path))
    return data


def relative_error(value, reference):
    with localcontext() as ctx:
        ctx.prec = 80
        expected = Decimal(reference)
        if expected == 0:
            return Decimal(0) if value == 0 else Decimal('Infinity')
        return abs((Decimal.from_float(value) - expected) / expected)


def collider_fingerprint(dataset):
    return hashlib.sha256(json.dumps([asdict(c) for c in dataset.colliders], sort_keys=True, default=str).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data_bytes = load_pinned(args.source, SOURCE_SHA, 2289)
    parser_path = REPO / 'research/program_expansion_20261025/hd_adapter/lamda_hd.py'
    load_pinned(parser_path, PARSER_SHA)
    load_pinned(OWN.parent / 'CODING_CONTRACT.md', CONTRACT_SHA)
    gate_path = REPO / 'research/program_expansion_20261025/hd_adapter/raw/source_diagnostic/diagnostics.json'
    historical = json.loads(load_pinned(gate_path, GATE_EVIDENCE_SHA))
    original_gaps = {g['line_id']: g for g in historical['frequency_gap_Hz']}
    spec = importlib.util.spec_from_file_location('hd_joint_pinned_literal_parser', parser_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    data = module.parse_hd(data_bytes)
    before_colliders = collider_fingerprint(data)
    rows, line_gates = [], []
    for line in data.radiative_lines:
        upper, lower = data.level(line.upper), data.level(line.lower)
        values = (upper.energy_cm_inverse.literal, lower.energy_cm_inverse.literal, line.frequency_GHz.literal)
        for t in (50, 100, 200):
            out = joint_thermal(*values, t)
            ref = decimal_reference(*values, t)
            gap = out['signed_frequency_gap_Hz_exact']
            gap_fraction = Fraction(int(gap['numerator']), int(gap['denominator']))
            old_gap_exact = Fraction(original_gaps[line.id]['absolute_gap_Hz'])
            if abs(gap_fraction) != old_gap_exact:
                raise RuntimeError('IMMUTABLE_OLD_SOURCE_GATE_LINK_MISMATCH')
            errors = {key: relative_error(out[key], ref[key]) for key in ('paired_flux_imbalance_I', 'source_planck_deviation_D', 'source_planck_ratio')}
            passed = all(error <= Decimal.from_float(TOLERANCE) for error in errors.values())
            if out['analytic_zero']:
                passed = passed and out['paired_flux_imbalance_I'] == 0 and out['source_planck_deviation_D'] == 0 and out['source_planck_ratio'] == 1
            rows.append({'line_id': line.id, 'upper_level_id': line.upper, 'lower_level_id': line.lower,
                         'upper_J': upper.J, 'lower_J': lower.J, 'temperature_K': t,
                         'upper_energy_cm_inverse_literal': values[0], 'lower_energy_cm_inverse_literal': values[1],
                         'frequency_GHz_literal': values[2], 'source_line_number': line.source_line,
                         'upper_source_line_number': upper.source_line, 'lower_source_line_number': lower.source_line,
                         'signed_frequency_gap_Hz': float(gap_fraction), 'old_absolute_frequency_gap_Hz': str(old_gap_exact),
                         'old_35_Hz_gate_passed': old_gap_exact <= 35,
                         'old_gate_classification': 'PASS_CATALOG_ROUNDING_GATE' if old_gap_exact <= 35 else 'SOURCE_DISCREPANCY_UNQUALIFIED',
                         **out, 'decimal_reference': ref,
                         'relative_errors': {k: str(v) for k, v in errors.items()}, 'numerical_reference_passed': passed})
        line_gates.append({'line_id': line.id, 'upper_J': upper.J, 'lower_J': lower.J,
                           'absolute_gap_Hz': original_gaps[line.id]['absolute_gap_Hz'], 'gate_Hz': 35,
                           'passed': Fraction(original_gaps[line.id]['absolute_gap_Hz']) <= 35})
    controls = run_controls()
    controls.extend([
        {'name': 'collider_blocks_unchanged', 'passed': before_colliders == collider_fingerprint(data), 'details': {'before_sha256': before_colliders, 'after_sha256': collider_fingerprint(data), 'collider_ids': [c.id for c in data.colliders], 'temperature_nodes_K': [[str(t.value) for t in c.temperature_nodes_K] for c in data.colliders], 'rate_values': sum(len(p.downward_cm3_per_s) for c in data.colliders for p in c.downward_pairs)}},
        {'name': 'source_byte_roundtrip_unchanged', 'passed': data.source_roundtrip() == data_bytes, 'details': 'Original parser used only for literal ingestion. No collider interpolation or qualified production consumer called.'},
        {'name': 'original_35_Hz_gate_preserved', 'passed': sum(not r['passed'] for r in line_gates) == 7 and len(line_gates) == 8, 'details': 'Seven failing lines remain unqualified; diagnostics provide no source-gate promotion.'},
    ])
    all_passed = len(rows) == 24 and all(row['numerical_reference_passed'] for row in rows) and all(row['passed'] for row in controls)
    result = {'schema': 'REC_HD_JOINT_THERMAL_DIAGNOSTIC_V1', 'status': 'PASS_SCOPED_NUMERICAL_DIAGNOSTIC' if all_passed else 'FAIL_SCOPED_NUMERICAL_DIAGNOSTIC',
              'claim': 'Fixed-column paired flux and source/Planck compatibility diagnostics; no empirical uncertainty or production qualification.',
              'source': {'path': str(args.source), 'url': 'https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat', 'bytes': 2289, 'sha256': SOURCE_SHA, 'parser_path': parser_path.relative_to(REPO).as_posix(), 'parser_sha256': PARSER_SHA, 'old_source_gate_evidence_path': gate_path.relative_to(REPO).as_posix(), 'old_source_gate_evidence_sha256': GATE_EVIDENCE_SHA},
              'units': {'energy_wavenumber': 'cm^-1', 'frequency': 'GHz; exact conversion to Hz', 'temperature': 'K', 'delta_I_D_ratio': 'dimensionless'},
              'formulas': {'delta': 'h_SI*(100*c*(Etilde_u-Etilde_l)-10^9*nu_GHz)/(k_B*T), exact rational source arithmetic', 'I': 'tanh(delta/2)', 'D': 'expm1(-delta)/(-expm1(-x_E))', 'ratio': '1+D'},
              'reference': '80-digit Decimal independent positive b/(1-b), r/(1-b) fluxes and original exponential source ratio',
              'relative_error_tolerance': TOLERANCE, 'rows': rows, 'line_source_gates': line_gates, 'controls': controls,
              'physical_source_gate': 'FAIL_ORIGINAL_35_HZ_7_OF_8', 'production_approved': False,
              'collider_mixing': False, 'temperature_extrapolation': False, 'new_IVPs': 0, 'historical_suites_executed': 0,
              'physical_epsilon': None, 'physical_bound_coverage': '0/313'}
    save(args.output / 'DIAGNOSTICS.json', result)
    fields = ['line_id', 'upper_level_id', 'lower_level_id', 'temperature_K', 'upper_energy_cm_inverse_literal', 'lower_energy_cm_inverse_literal', 'frequency_GHz_literal', 'signed_frequency_gap_Hz', 'old_35_Hz_gate_passed', 'delta', 'paired_flux_imbalance_I', 'source_planck_deviation_D', 'source_planck_ratio', 'numerical_reference_passed']
    with (args.output / 'DIAGNOSTICS.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields + ['delta_numerator', 'delta_denominator', 'I_relative_error', 'D_relative_error', 'ratio_relative_error'])
        writer.writeheader()
        for row in rows:
            writer.writerow({**{key: row[key] for key in fields}, 'delta_numerator': row['delta_exact']['numerator'], 'delta_denominator': row['delta_exact']['denominator'], 'I_relative_error': row['relative_errors']['paired_flux_imbalance_I'], 'D_relative_error': row['relative_errors']['source_planck_deviation_D'], 'ratio_relative_error': row['relative_errors']['source_planck_ratio']})
    save(args.output / 'TARGETED_CONTROLS.json', {'controls': controls, 'all_passed': all(row['passed'] for row in controls)})
    summary = {'status': result['status'], 'actual_cases': len(rows), 'controls': len(controls), 'controls_passed': sum(row['passed'] for row in controls), 'old_gate_failing_lines': sum(not row['passed'] for row in line_gates), 'max_absolute_I': max(abs(r['paired_flux_imbalance_I']) for r in rows), 'max_absolute_D': max(abs(r['source_planck_deviation_D']) for r in rows), 'max_relative_error_I': str(max(Decimal(r['relative_errors']['paired_flux_imbalance_I']) for r in rows)), 'max_relative_error_D': str(max(Decimal(r['relative_errors']['source_planck_deviation_D']) for r in rows)), 'max_relative_error_ratio': str(max(Decimal(r['relative_errors']['source_planck_ratio']) for r in rows)), 'figure_PNG': 'joint_thermal_diagnostics.png', 'figure_PDF': 'joint_thermal_diagnostics.pdf', 'production_approved': False}
    save(args.output / 'SUMMARY.json', summary)
    (args.output / 'SUMMARY.md').write_text('# HD joint thermal diagnostic\n\n' + json.dumps(summary, indent=2) + '\n\nI and D describe fixed-column thermal compatibility. They do not estimate physical source uncertainty. Seven original 35 Hz failures remain unqualified.\n')
    for control in controls:
        print(json.dumps({'targeted_control': control['name'], 'passed': control['passed']}))
    plot_saved(args.output / 'DIAGNOSTICS.json', args.output)
    print(json.dumps(summary))
    return 0 if all_passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
