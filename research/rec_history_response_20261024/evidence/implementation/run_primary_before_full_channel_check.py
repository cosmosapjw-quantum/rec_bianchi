"""One finite primary; root authorizes execution after S1 publication and ACK."""
import os
for _key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
    os.environ[_key] = '1'
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
import interval as iv
from source_response import ROOT, load, coefficients, certify, query_records, event_coefficients
from checks import controls, parity, probes


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def csvwrite(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def verify_inputs():
    manifest = json.loads((ROOT/'inputs/INPUT_IDENTITIES.json').read_text())
    for row in manifest['files']:
        p = ROOT/row['path']; b = p.read_bytes()
        if len(b) != row['bytes'] or hashlib.sha256(b).hexdigest() != row['sha256']:
            raise ValueError('INPUT_BYTES_CHANGED:'+row['path'])
    return manifest


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', default='results/primary001'); args = p.parse_args()
    out = ROOT/args.output; out.mkdir(parents=True, exist_ok=False)
    write(out/'INPUT_VERIFICATION.json', verify_inputs())
    report = {'schema': 'REC_HISTORY_RESPONSE_PRIMARY_V1', 'status': 'STARTED',
              'dense_algebraic_rhs_columns': 0, 'new_IVP': 0, 'native_runtime': 0,
              'old_campaign_replay': 0, 'epsilon_physical': None,
              'interpretation': 'represented frozen binary64 operator; no physical epsilon'}
    products = {}; arrays = {}; phase = 'load_coefficients'; started = time.monotonic()
    try:
        f = load(); M, B, T, P, owners = coefficients(f)
        arrays.update(M=M, B=B, T=T, P=P)
        np.savez(out/'COEFFICIENTS.npz', **arrays)
        write(out/'ROW_SOURCE_OWNERS.json', owners)
        phase = 'combined_solve'
        report['dense_algebraic_rhs_columns'] = 626
        combined = np.linalg.solve(M, np.concatenate((B, np.eye(313)), axis=1))
        V, Z = combined[:, :313], combined[:, 313:]
        Khat = T@V+P; iv.finite(V, Z, Khat)
        arrays.update(Vhat=V, Z=Z, Khat=Khat)
        phase = 'interval_certificate'
        summary, cert = certify(M, B, T, P, V, Z, products)
        report['certificate'] = summary; arrays.update(cert)
        if not summary['status'].startswith('CERTIFIED'):
            raise iv.CertificateFailure(summary['status'])
        phase = 'exact_checks'
        exact = {name: probes(*entry) for name, entry in products.items()}
        write(out/'EXACT_DOT_PROBES.json', exact)
        report['exact_dot_probes_per_product'] = {k: len(v) for k, v in exact.items()}
        report['exact_dot_probes_pass'] = all(x['pass'] for v in exact.values() for x in v)
        validation = controls(); write(out/'CONTROLS_AND_EXACT_TOYS.json', validation)
        report['controls_pass'] = validation['pass']
        comparison = parity(f, B, T, P); write(out/'NATIVE_ACTION_PARITY.json', comparison)
        report['native_action_parity_pass'] = comparison['pass']
        phase = 'extremizer_witness'
        selected = int(np.argmax(np.sum(np.abs(Khat), axis=1)))
        sign = np.where(Khat[selected] < 0, -1., 1.)
        # One additional independent RHS; total dense solve columns 627 maximum.
        report['dense_algebraic_rhs_columns'] += 1
        witness_rhs = f.source_increment(sign)
        xw = np.linalg.solve(M, witness_rhs)
        witness = f.outgoing(xw, sign)
        predicted = Khat@sign
        rowlo, rowhi = iv.sum_bounds(iv.mul((cert['Klo'][selected], cert['Khi'][selected]), iv.point(sign)))
        witness_check = {'selected_row': selected, 'direction': sign.tolist(),
                         'source_rhs': witness_rhs.tolist(), 'population_response': xw.tolist(),
                         'native_response': witness.tolist(), 'predicted_response': predicted.tolist(),
                         'selected_response_lower': float(rowlo), 'selected_response_upper': float(rowhi),
                         'row_gain_lower': float(cert['row_gain_lower'][selected]),
                         'row_gain_upper': float(cert['row_gain_upper'][selected]),
                         'selected_response_inside_certificate': bool(rowlo <= witness[selected] <= rowhi),
                         'absolute_response_below_gain_upper': bool(abs(witness[selected]) <= cert['row_gain_upper'][selected]),
                         'absolute_response_above_gain_lower': bool(abs(witness[selected]) >= cert['row_gain_lower'][selected]),
                         'sign_uncertain_coefficient_count': int(np.count_nonzero((cert['Klo'][selected] < 0) & (cert['Khi'][selected] > 0))),
                         'note': 'single-RHS floating solve/native map diagnostic; interval theorem is independent'}
        write(out/'EXTREMIZER_WITNESS.json', witness_check)
        arrays.update(witness_direction=sign, witness_response=witness)
        phase = 'export'
        event = event_coefficients(f, Khat, cert['Klo'], cert['Khi']); arrays.update(event)
        queries = query_records(f)
        for j, q in enumerate(queries):
            for key, value in event.items():
                q[key] = float(value[j])
            q['selected_output_row'] = selected
            q['selected_output_abs_lower'] = float(iv.abs_bounds((cert['Klo'][selected], cert['Khi'][selected]))[0][j])
            q['selected_output_abs_upper'] = float(iv.abs_bounds((cert['Klo'][selected], cert['Khi'][selected]))[1][j])
        csvwrite(out/'QUERY_RESPONSE_COEFFICIENTS.csv', queries)
        gains = [{'outgoing_index': i, 'gain_lower': float(cert['row_gain_lower'][i]),
                  'gain_upper': float(cert['row_gain_upper'][i]), 'unit': 'occupation_per_unit_incoming_box'} for i in range(314)]
        csvwrite(out/'OUTGOING_ROW_GAINS.csv', gains)
        top = np.argsort(-np.abs(Khat[selected]), kind='stable')
        csvwrite(out/'TOP_CONTRIBUTORS.csv', [{'rank': rank+1, 'incoming_index': int(j),
                 'selected_output_coefficient': float(Khat[selected, j]), 'number_coefficient': float(event['number_hat'][j])}
                 for rank, j in enumerate(top)])
        report.update(selected_output_row=selected, box=iv.box_weights((cert['Klo'], cert['Khi'])),
                      paired_event={'number_units': 'm^-3 s^-1 per occupation', 'energy_units': 'J m^-3 s^-1 per occupation',
                                    'same_event_atomic_plus_radiation_exact': 0, 'extra_photon_source': 0},
                      witness_pass=witness_check['selected_response_inside_certificate'] and witness_check['absolute_response_below_gain_upper'] and witness_check['absolute_response_above_gain_lower'])
        report['status'] = 'PASS_SCOPED' if all(report[k] for k in ['exact_dot_probes_pass', 'controls_pass', 'native_action_parity_pass', 'witness_pass']) else 'FINDING_RETURN_TO_ASTRA'
    except Exception as exc:
        report.update(status='FAILURE_RETURN_TO_ASTRA', failed_phase=phase, exception=repr(exc))
    finally:
        # Preserve all coefficients, candidate inverse and intervals reached before a failure.
        np.savez(out/'RAW_RESPONSE.npz', **arrays)
        report['wall_in_child_seconds'] = time.monotonic()-started
        write(out/'SUMMARY.json', report)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report['status'] == 'PASS_SCOPED' else 2


if __name__ == '__main__':
    sys.exit(main())
