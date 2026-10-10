"""Two original HyRec histories, two epochs each; no rerun on failure."""
import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HELPER = ROOT / 'research/p02b_flrw_endpoint_20261010/run_endpoint.py'
spec = importlib.util.spec_from_file_location('frozen_endpoint_helpers', HELPER)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def contract():
    return json.loads((HERE / 'CONTRACT.json').read_text())


def validate_epochs(results, frozen, lane):
    if len(results) != 2:
        raise ValueError('EPOCH_COUNT_MISMATCH')
    checks = []
    for result, z in zip(results, frozen['epochs_z']):
        if result['grid']['DLNA'] != frozen[lane + '_DLNA']:
            raise ValueError('DLNA_MISMATCH')
        checks.append(base.validate_endpoint(result, dict(frozen, endpoint_z=z)))
    return checks


def compare(baseline, refined, frozen):
    return {str(z): base.compare_endpoints(a, b, frozen)
            for z, a, b in zip(frozen['epochs_z'], baseline, refined)}


def check_native(path, result, frozen, lane):
    count = 0
    with path.open() as stream:
        for count, row in enumerate(csv.DictReader(stream), 1):
            x, xe, tm = (float(row[k]) for k in ('ln_a', 'xe_per_H', 'Tm_K'))
            if not all(math.isfinite(v) for v in (x, xe, tm)) or not (
                    0 <= xe <= 1 + 2 * result['endpoint']['fHe'] and tm > 0):
                raise ValueError('NATIVE_ARRAY_DOMAIN')
            expected = result['grid']['ln_a_start'] + (count - 1) * frozen[lane + '_DLNA']
            if x != expected:
                raise ValueError('NATIVE_ARRAY_COORDINATE')
    if count != result['grid']['nz']:
        raise ValueError('NATIVE_ARRAY_LENGTH')
    return {'status': 'PASS', 'nodes': count, 'sha256': base.digest(path.read_bytes())}


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    frozen = contract()
    members = base.checked_members(ROOT / frozen['archive'], frozen)
    compiler = shutil.which('cc')
    if compiler is None:
        raise RuntimeError('COMPILER_UNAVAILABLE')
    _, compiler_receipt = base.record_command([compiler, '--version'], ROOT, output, 'compiler', timeout=30)
    manifest = {'archive_sha256': frozen['archive_sha256'], 'input_sha256': frozen['input_sha256'],
                'members': {k: base.digest(v) for k, v in members.items()},
                'local_files': {p.name: base.digest(p.read_bytes()) for p in
                                (HERE / 'epoch_driver.c', HERE / 'run_epochs.py', HERE / 'CONTRACT.json', HELPER)},
                'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'base_tree': subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=ROOT, text=True).strip(),
                'status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
                'compiler_sha256': base.digest(Path(compiler).read_bytes()), 'compiler_receipt': compiler_receipt,
                'harness': 'HARNESS_UNAVAILABLE'}
    (output / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    results, checks, receipts = {}, {}, {}
    science_runs = 0
    with tempfile.TemporaryDirectory(prefix='a-rec-epoch01-') as tmp:
        for lane in ('baseline', 'refined'):
            directory = Path(tmp) / lane
            directory.mkdir()
            for name, data in members.items():
                relative = Path(name).relative_to('HyRec')
                if lane == 'refined' and relative.name == 'hyrec_params.h':
                    data = base.refinement_header(data)
                target = directory / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            shutil.copyfile(HERE / 'epoch_driver.c', directory / 'epoch_driver.c')
            hashes = {p.name: base.digest(p.read_bytes()) for p in sorted(directory.iterdir()) if p.is_file()}
            (output / (lane + '.effective_sources.json')).write_text(json.dumps(hashes, indent=2) + '\n')
            command = [compiler, '-O2', 'hyrectools.c', 'helium.c', 'hydrogen.c', 'history.c', 'epoch_driver.c', '-lm', '-o', 'epochs']
            _, build = base.record_command(command, directory, output, lane + '.build')
            binary_hash = base.digest((directory / 'epochs').read_bytes())
            native = output / (lane + '.native_history.csv')
            science_runs += 1
            (output / 'SCIENCE_RUN_COUNT.json').write_text(json.dumps({'started': science_runs, 'limit': 2}) + '\n')
            stdout, receipt = base.record_command([str(directory / 'epochs'), str(native)], directory, output,
                                                  lane + '.run', stdin=members[frozen['input_member']], timeout=300)
            result = json.loads(stdout)
            (output / (lane + '.json')).write_text(json.dumps(result, indent=2) + '\n')
            results[lane] = result
            checks[lane] = {'epochs': validate_epochs(result, frozen, lane),
                            'native_history': check_native(native, result[0], frozen, lane)}
            receipts[lane] = {'binary_sha256': binary_hash, 'build': build, 'run': receipt}
    errors = compare(results['baseline'], results['refined'], frozen)
    validation = {'status': 'PASS_SCOPED', 'science_runs': science_runs, 'checks': checks,
                  'relative_differences': errors, 'limit': 1e-4, 'receipts': receipts,
                  'independent_review': 'PENDING', 'Bianchi_IC_adoption': 'HOLD',
                  'claim': 'One DLNA halving; no continuum/global error certificate'}
    (output / 'VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps({'status': 'PASS_SCOPED', 'relative_differences': errors}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('existing output refused')
    try:
        run(args.output.resolve())
    except Exception as exc:
        if args.output.exists():
            (args.output / 'FAILURE.json').write_text(json.dumps({'status': 'FAIL', 'error': repr(exc)}) + '\n')
        raise
