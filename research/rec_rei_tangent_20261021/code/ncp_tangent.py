"""Create-only pending-case runner for the three new interior tangent IVPs.

Default invocation only plans.  --execute admits a bounded spawn batch using
observed CPU/RAM and live cooperative leases, with one numerical thread per
nice worker.  Completed pilots and peer leases are never edited or retried.
"""
from __future__ import annotations

import os
THREAD_KEYS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
               'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
for _key in THREAD_KEYS:
    os.environ[_key] = '1'

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import re
import socket
import sys
import tempfile
import time
import traceback
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
GIB = 1024**3
RUN_SCHEMA = 'rec_bianchi.tangent_run.v1'
RESULT_SCHEMA = 'rec_bianchi.tangent_result.v1'
LEASE_SCHEMA = 'rec_bianchi.cooperative_lease.v1'


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _create_json(path, value):
    """Publish a complete JSON file atomically; never replace a prior file."""
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.write-',
                                     delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
            os.link(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def load_contract():
    manifest_path = ROOT / 'inputs/NCP_TANGENT_CASES.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema') != 'rec.tangent.pending_manifest.v1':
        raise ValueError('UNRECOGNIZED_INPUT_NAMESPACE')
    if manifest.get('case_memory_bytes') != GIB//2:
        raise ValueError('UNSUPPORTED_PER_CASE_MEMORY_RESERVATION')
    seen = set()
    for case in manifest['cases']:
        if (not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', case['id']) or case['id'] in seen
                or len(case['axes']) != 3
                or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in case['axes'])):
            raise ValueError('INVALID_OR_DUPLICATE_CASE')
        seen.add(case['id'])
    for name in ('rtol', 'atol', 'per_case_seconds', 'controller_seconds'):
        if not math.isfinite(manifest[name]) or manifest[name] <= 0:
            raise ValueError('INVALID_FINITE_EXECUTION_BUDGET:' + name)
    source = json.loads((ROOT / 'provenance/SOURCE_MANIFEST.json').read_text())
    source_hashes = {'vendor/' + name: digest for name, digest in source['files'].items()}
    for path, expected in source_hashes.items():
        if _sha(ROOT / path) != expected:
            raise ValueError('PINNED_SOURCE_CHANGED:' + path)
    names = ('ncp_tangent.py', 'resources.py', 'augmented.py', 'tangent_core.py', 'owner_model.py')
    hashes = {**source_hashes, **{'code/' + n: _sha(ROOT / 'code' / n) for n in names}}
    identity = {'schema': RUN_SCHEMA, 'source_commit': source['source_commit'],
                'input_sha256': _sha(manifest_path), 'file_sha256': hashes}
    identity['sha256'] = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return manifest, identity


def initialise_output(output, identity):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    marker = output / 'RUN_MANIFEST.json'
    if not marker.exists():
        if any(output.iterdir()):
            raise ValueError('NONEMPTY_OUTPUT_WITHOUT_TANGENT_NAMESPACE')
        try:
            _create_json(marker, identity)
        except FileExistsError:
            pass
    if json.loads(marker.read_text()) != identity:
        raise ValueError('OUTPUT_IDENTITY_MISMATCH_USE_A_FRESH_OUTPUT_DIRECTORY')
    return output


def case_status(directory, case, identity):
    directory = Path(directory)
    result = directory / 'RESULT.json'
    if result.exists():
        receipt = json.loads(result.read_text())
        if (receipt.get('schema') != RESULT_SCHEMA or receipt.get('status') != 'COMPLETE'
                or receipt.get('identity_sha256') != identity['sha256']
                or receipt.get('case') != case
                or _sha(directory / 'tangent.npz') != receipt.get('npz_sha256')):
            raise ValueError('COMPLETED_CASE_IDENTITY_OR_PAYLOAD_MISMATCH:' + case['id'])
        return 'complete_reused'
    for name, status in (('FAILED.json', 'preserved_failed'),
                         ('ATTEMPT.json', 'preserved_attempt'), ('.claim', 'preserved_claim')):
        if (directory / name).exists():
            return status
    if directory.exists() and any(directory.iterdir()):
        raise ValueError('UNRECOGNIZED_CASE_NAMESPACE:' + case['id'])
    return 'pending'


def scheduler_admission(sample, othercpu, othermem, requested, pending):
    """Return worker slots; othermem is bytes, including explicit reservations."""
    if othercpu < 0 or othermem < 0 or not math.isfinite(othermem):
        raise ValueError('INVALID_PEER_RESERVATION')
    total = sample['memory_total_bytes']
    reserve = 16*GIB if total >= 120*GIB else max(GIB, .1*total)
    memory_slots = math.floor((sample['memory_available_bytes']-reserve-othermem)/(.5*GIB))
    cpu_slots = sample['effective_cpus'] - 1 - othercpu
    return max(0, min(int(sample['slots']), int(cpu_slots), int(memory_slots),
                      int(requested), int(pending), 63))


def _start_tick(pid):
    try:
        return int(Path(f'/proc/{pid}/stat').read_text().rpartition(')')[2].split()[19])
    except (OSError, IndexError, ValueError):
        return None


@contextmanager
def resource_lease(args, sampler, pending):
    directory = Path(args.lease_dir)
    directory.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    own = directory / ('rec_tangent_' + token + '.json')
    host, pid = socket.gethostname(), os.getpid()
    time.sleep(.15)
    try:
        with (directory / '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            cpu, mem, live, unknown = args.reserved_cpus, args.reserved_memory_gib*GIB, 0, 0
            for path in directory.glob('*.json'):
                try:
                    peer = json.loads(path.read_text())
                    recognized = (isinstance(peer, dict) and peer.get('schema') == LEASE_SCHEMA and peer.get('host') == host
                                  and isinstance(peer.get('pid'), int)
                                  and isinstance(peer.get('proc_start_tick'), int)
                                  and isinstance(peer.get('slots'), int) and peer['slots'] >= 0
                                  and isinstance(peer.get('memory_bytes'), (int, float))
                                  and math.isfinite(peer['memory_bytes']) and peer['memory_bytes'] >= 0)
                    if recognized and _start_tick(peer['pid']) == peer['proc_start_tick']:
                        cpu += peer['slots']; mem += peer['memory_bytes']; live += 1
                    elif not recognized:
                        unknown += 1
                except (OSError, ValueError, TypeError):
                    unknown += 1
            sample = sampler.sample(args.profile, args.max_workers)
            slots = scheduler_admission(sample, cpu, mem, args.max_workers, pending)
            observation = {'sample': sample, 'live_peer_leases': live, 'unknown_peer_records': unknown,
                           'reserved_cpus_including_peers': cpu, 'reserved_memory_bytes_including_peers': mem}
            if slots:
                tick = _start_tick(pid)
                if tick is None:
                    raise RuntimeError('OWN_PROCESS_IDENTITY_UNAVAILABLE')
                _create_json(own, {'schema': LEASE_SCHEMA, 'token': token, 'host': host, 'pid': pid,
                                  'proc_start_tick': tick, 'slots': slots, 'memory_bytes': slots*.5*GIB,
                                  'created_utc': _utc(), 'owner': 'REC_REI_TANGENT_INTERIOR3'})
        yield slots, observation
    finally:
        try:
            if own.exists() and json.loads(own.read_text()).get('token') == token:
                own.unlink()  # Only this invocation's unique lease; peers are never deleted.
        except (OSError, ValueError, AttributeError):
            pass


def run_worker(job):
    directory = Path(job['directory'])
    status = case_status(directory, job['case'], job['identity'])
    if status != 'pending':
        return {'case_id': job['case']['id'], 'status': status, 'task_exit_code': None}
    directory.mkdir(parents=True, exist_ok=True)
    try:
        (directory / '.claim').mkdir()
    except FileExistsError:
        return {'case_id': job['case']['id'], 'status': 'preserved_claim', 'task_exit_code': None}
    started, cpu_start = time.monotonic(), time.process_time()
    os.nice(max(0, 10-os.getpriority(os.PRIO_PROCESS, 0)))
    base = {'schema': RESULT_SCHEMA, 'case': job['case'], 'identity_sha256': job['identity']['sha256'],
            'job_token': job.get('job_token', uuid.uuid4().hex),
            'source_code_identity': job['identity'], 'started_utc': _utc(),
            'pid': os.getpid(), 'host': socket.gethostname(), 'proc_start_tick': _start_tick(os.getpid()),
            'nice': os.getpriority(os.PRIO_PROCESS, 0), 'numerical_threads': {k: os.environ[k] for k in THREAD_KEYS},
            'admission': job['admission'], 'process_exit_code': None, 'exit_kind': 'worker_callable_return'}
    _create_json(directory / 'ATTEMPT.json', {**base, 'status': 'RUNNING'})
    try:
        for path, digest in job['identity']['file_sha256'].items():
            if _sha(ROOT / path) != digest:
                raise ValueError('CODE_CHANGED_BEFORE_EXECUTION:' + path)
        from augmented import integrate_case
        import numpy as np
        arrays, integration = integrate_case(job['case']['axes'], rtol=job['rtol'], atol=job['atol'],
                                             case_seconds=job['per_case_seconds'])
        with tempfile.NamedTemporaryFile(dir=directory, prefix='.npz-', delete=False) as stream:
            temporary = Path(stream.name)
            try:
                np.savez_compressed(stream, **arrays)
                stream.flush(); os.fsync(stream.fileno())
                os.link(temporary, directory / 'tangent.npz')
            finally:
                temporary.unlink(missing_ok=True)
        base.update(integration=integration, npz_sha256=_sha(directory / 'tangent.npz'))
        for path, digest in job['identity']['file_sha256'].items():
            if _sha(ROOT / path) != digest:
                raise ValueError('CODE_CHANGED_DURING_EXECUTION:' + path)
        if integration.get('status') != 'COMPLETED':
            raise RuntimeError('AUGMENTED_VALIDATION_FAILED')
        receipt = {**base, 'status': 'COMPLETE', 'task_exit_code': 0, 'finished_utc': _utc(),
                   'wall_seconds': time.monotonic()-started, 'cpu_seconds': time.process_time()-cpu_start}
        _create_json(directory / 'RESULT.json', receipt)
    except Exception as exc:
        receipt = {**base, 'status': 'FAILED', 'task_exit_code': 1, 'finished_utc': _utc(),
                   'wall_seconds': time.monotonic()-started, 'cpu_seconds': time.process_time()-cpu_start,
                   'error_type': type(exc).__name__, 'error': str(exc), 'traceback': traceback.format_exc()}
        _create_json(directory / 'FAILED.json', receipt)
    return {'case_id': job['case']['id'], 'status': receipt['status'], 'task_exit_code': receipt['task_exit_code']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--max-workers', type=int, default=63)
    parser.add_argument('--profile', choices=('sandbox', 'ncp'), default='ncp')
    parser.add_argument('--lease-dir', default='/tmp/bianchi_resource_leases')
    parser.add_argument('--reserved-cpus', type=int, default=0)
    parser.add_argument('--reserved-memory-gib', type=float, default=0.)
    args = parser.parse_args(argv)
    if (args.max_workers < 1 or args.reserved_cpus < 0 or args.reserved_memory_gib < 0
            or not math.isfinite(args.reserved_memory_gib)):
        parser.error('worker count must be positive; reservations must be finite and nonnegative')
    manifest, identity = load_contract()
    output = initialise_output(args.output, identity)
    states = {c['id']: case_status(output / c['id'], c, identity) for c in manifest['cases']}
    pending = [c for c in manifest['cases'] if states[c['id']] == 'pending']
    summary = {'schema': 'rec_bianchi.tangent_dispatch.v1', 'identity_sha256': identity['sha256'],
               'execute': args.execute, 'case_states': states, 'batches': [], 'new_jobs': 0,
               'new_jobs_semantics': 'worker_callable_submissions; actual IVPs are in per-case receipts'}
    if not args.execute or not pending:
        summary['status'] = 'PLAN_ONLY' if pending else 'NO_PENDING_WORK'
        print(json.dumps(summary, sort_keys=True)); return 0
    from resources import Sampler
    sampler, begin = Sampler(), time.monotonic()
    while pending:
        if time.monotonic()-begin+manifest['per_case_seconds'] > manifest['controller_seconds']:
            summary['status'] = 'DEFERRED_CONTROLLER_BUDGET'; break
        with resource_lease(args, sampler, len(pending)) as (slots, observation):
            if not slots:
                summary['status'] = 'DEFERRED_RESOURCES'; break
            batch, pending = pending[:slots], pending[slots:]
            summary['batches'].append({'cases': [c['id'] for c in batch], 'resources': observation})
            with ProcessPoolExecutor(max_workers=slots, mp_context=multiprocessing.get_context('spawn')) as pool:
                tokens = {c['id']: uuid.uuid4().hex for c in batch}
                futures = {pool.submit(run_worker, {'case': c, 'job_token': tokens[c['id']], 'directory': str(output/c['id']),
                           'identity': identity, 'admission': observation, **{k: manifest[k] for k in
                           ('rtol', 'atol', 'per_case_seconds')}}): c for c in batch}
                summary['new_jobs'] += len(futures)
                for future in as_completed(futures):
                    case = futures[future]
                    try:
                        result = future.result()
                        states[case['id']] = result['status']
                    except Exception as exc:
                        states[case['id']] = 'WORKER_FAILURE_PRESERVED'
                        failure = {'case': case, 'finished_utc': _utc(),
                                   'error_type': type(exc).__name__, 'error': str(exc),
                                   'task_exit_code': None, 'process_exit_code': None, 'exit_kind': 'pool_exception'}
                        summary.setdefault('worker_failures', []).append(failure)
                        directory = output/case['id']
                        try:
                            attempt = json.loads((directory/'ATTEMPT.json').read_text())
                            if attempt.get('job_token') == tokens[case['id']]:
                                _create_json(directory/'FAILED.json', {**attempt, **failure, 'status': 'WORKER_FAILURE'})
                        except (OSError, ValueError, AttributeError):
                            pass
    summary.setdefault('status', 'DISPATCH_FINISHED')
    _create_json(output/('DISPATCH_' + uuid.uuid4().hex + '.json'), summary)
    print(json.dumps(summary, sort_keys=True))
    return 1 if any('FAIL' in state for state in states.values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
