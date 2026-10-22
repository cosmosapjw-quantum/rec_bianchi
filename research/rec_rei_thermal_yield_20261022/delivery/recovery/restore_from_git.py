"""Restore only missing/mismatched THERM01 payloads from the immutable Git pin.

This performs no scientific execution. Every received byte string is admitted
only after its original byte length and Git SHA (and SHA256 where available) match.
"""
import concurrent.futures
import hashlib
import json
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/scratch/a6dfe82cc85f')
TARGET = ROOT / 'repos/rec_bianchi/research/rec_rei_thermal_yield_20261022'
COMMIT = 'd562d03415e37488cd4b5444488c77555260e0fb'
BASE = f'https://raw.githubusercontent.com/cosmosapjw-quantum/rec_bianchi/{COMMIT}/research/rec_rei_thermal_yield_20261022/'
ROWS = json.loads((ROOT / 'recovery/EXPECTED_STAGE_C_PAYLOADS.json').read_text())


def matches(data, row):
    git_sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return (len(data) == row['bytes'] and git_sha == row['git_sha']
            and ('sha256' not in row or hashlib.sha256(data).hexdigest() == row['sha256']))


def restore(row):
    rel = PurePosixPath(row['path'])
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('Unsafe expected path')
    path = TARGET.joinpath(*rel.parts)
    if path.exists() and matches(path.read_bytes(), row):
        return {'path': str(rel), 'status': 'REUSED_EXACT', 'bytes': row['bytes']}
    request = urllib.request.Request(BASE + str(rel), headers={'User-Agent': 'THERM01-exact-payload-recovery'})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    byte_repair = None
    if not matches(data, row) and rel.suffix == '.csv' and b'\r' not in data:
        candidate = data.replace(b'\n', b'\r\n')
        if matches(candidate, row):
            data = candidate
            byte_repair = 'LF_TO_ORIGINAL_CRLF_VERIFIED_BY_ORIGINAL_SHA'
    if not matches(data, row):
        raise ValueError('Remote bytes disagree with pinned payload identity: ' + str(rel))
    if path.exists():
        conflict = ROOT / 'recovery/replaced_staging_text' / rel
        conflict.parent.mkdir(parents=True, exist_ok=True)
        conflict.write_bytes(path.read_bytes())
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.restore_tmp')
    temp.write_bytes(data)
    temp.replace(path)
    return {'path': str(rel), 'status': 'RESTORED_EXACT', 'bytes': len(data), 'byte_repair': byte_repair}


if __name__ == '__main__':
    results, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(restore, row): row for row in ROWS}
        for future in concurrent.futures.as_completed(futures):
            row = futures[future]
            try:
                results.append(future.result())
            except Exception as error:
                errors.append({'path': row['path'], 'type': type(error).__name__, 'error': str(error)})
    report = {'commit': COMMIT, 'expected_files': len(ROWS),
              'exact_files': len(results), 'restored_files': sum(r['status'] == 'RESTORED_EXACT' for r in results),
              'reused_files': sum(r['status'] == 'REUSED_EXACT' for r in results),
              'science_IVPs_executed': 0, 'status': 'PASS' if not errors else 'PARTIAL',
              'errors': errors, 'files': sorted(results, key=lambda r: r['path'])}
    (ROOT / 'recovery/GIT_PAYLOAD_RECOVERY.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}))
    raise SystemExit(bool(errors))
