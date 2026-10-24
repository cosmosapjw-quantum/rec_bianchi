"""Root-authorized saved-data diagnostic reclassification; no source/solve import.

Reads original saved residuals/scales/direction; reconstructs only the frozen
ones/alternating/sin/cos vectors. No matrix product, native action, solve,
exact dot, toy, coefficient or certificate recomputation occurs.
"""
import os
for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def identity(paths):
    return [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def reclassify(name, residual, gross, direction=None):
    residual = np.array(residual, dtype=float); gross = np.array(gross, dtype=float)
    if not np.all(np.isfinite(residual)) or not np.all(np.isfinite(gross)):
        raise ValueError('SAVED_NONFINITE')
    repaired = gross.copy()
    if direction is not None:
        if residual.shape != (314,) or direction.shape != (313,):
            raise ValueError('SAVED_DIAGNOSTIC_SHAPE')
        repaired[:311] += 2*np.abs(direction[:311])
    factor = 512*np.finfo(float).eps
    old_allowed = factor*gross; new_allowed = factor*repaired
    original_flags = residual <= old_allowed; repaired_flags = residual <= new_allowed
    affected = np.flatnonzero(~original_flags | ~repaired_flags)
    return {'name': name, 'checks': int(residual.size),
            'original_pass': bool(np.all(original_flags)), 'repaired_pass': bool(np.all(repaired_flags)),
            'original_failed_count': int(np.count_nonzero(~original_flags)),
            'repaired_failed_count': int(np.count_nonzero(~repaired_flags)),
            'criterion': 'absolute residual <=512eps64*gross; no additive floor',
            'scale_change': 'old+2abs(u) virtual rows0:311; line rows unchanged' if direction is not None else 'unchanged source diagnostic',
            'affected_rows_only': [{'row': int(i), 'absolute_residual': float(residual[i]),
                'original_gross': float(gross[i]), 'repaired_gross': float(repaired[i]),
                'original_allowed': float(old_allowed[i]), 'repaired_allowed': float(new_allowed[i]),
                'original_pass': bool(original_flags[i]), 'repaired_pass': bool(repaired_flags[i])} for i in affected]}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--input', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args(); source = ROOT/args.input; out = ROOT/args.output; out.mkdir(parents=True, exist_ok=False)
    primary_paths = sorted(p for p in source.iterdir() if p.is_file())
    code_paths = sorted((ROOT/'code').glob('*.py'))
    input_paths = sorted(p for folder in ['inputs', 'vendor'] for p in (ROOT/folder).rglob('*') if p.is_file())
    before = {'primary_outputs': identity(primary_paths), 'code': identity(code_paths), 'inputs_vendor': identity(input_paths)}
    write(out/'IDENTITIES_BEFORE.json', before)
    parity = json.loads((source/'NATIVE_ACTION_PARITY.json').read_text())
    witness = json.loads((source/'EXTREMIZER_WITNESS.json').read_text())
    index = np.arange(313, dtype=float)
    directions = [np.ones(313), (-1.)**index, np.sin(index+1.), np.cos((index+1.)/7.)]
    records = []
    for row in parity['records']:
        direction = directions[row['direction']] if row['operation'] == 'outgoing' else None
        record = reclassify(f"parity_direction{row['direction']}_{row['operation']}", row['absolute_difference'], row['gross_scale'], direction)
        if record['original_pass'] != row['pass']:
            raise ValueError('SAVED_ORIGINAL_FLAG_MISMATCH')
        records.append(record)
    record = reclassify('all314_witness', witness['all_channel_absolute_difference'], witness['all_channel_gross_scale'], np.array(witness['direction'], dtype=float))
    if record['original_pass'] != witness['all_314_channel_pass']:
        raise ValueError('SAVED_WITNESS_FLAG_MISMATCH')
    records.append(record)
    after = {'primary_outputs': identity(primary_paths), 'code': identity(code_paths), 'inputs_vendor': identity(input_paths)}
    write(out/'IDENTITIES_AFTER.json', after)
    unchanged = before == after
    passed = all(row['repaired_pass'] for row in records) and unchanged
    report = {'schema': 'REC_HISTORY_RESPONSE_SAVED_DIAGNOSTIC_REPAIR_V1',
              'status': 'PASS_SAVED_DIAGNOSTICS' if passed else 'FINDING_RETURN_TO_ASTRA',
              'root_decision': 'evidence/ROOT_DIAGNOSTIC_REPAIR_DECISION.json',
              'original_primary_status_preserved': 'FINDING_RETURN_TO_ASTRA; exit2',
              'checks': records, 'diagnostic_groups': len(records),
              'componentwise_comparison_count': sum(row['checks'] for row in records),
              'identity_before_after_equal': unchanged, 'original_primary_outputs_unchanged': before['primary_outputs'] == after['primary_outputs'],
              'code_unchanged_during_probe': before['code'] == after['code'],
              'additional_dense_rhs_columns': 0, 'coefficient_or_certificate_recomputation': 0,
              'native_action_calls': 0, 'exact_dot_or_toy_reruns': 0,
              'new_IVP': 0, 'native_runtime': 0, 'old_campaign_replay': 0, 'physical_epsilon': None,
              'runtime': {'python': sys.version, 'numpy': np.__version__}}
    write(out/'SUMMARY.json', report); print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if passed else 2


if __name__ == '__main__':
    sys.exit(main())
