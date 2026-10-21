"""Small operational audit with synthetic workers; no scientific IVP is run.

Temporary fake results never enter the scientific output directories. This
checks the actual create-only runner, resume paths and cooperative lease logic.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import types
from unittest.mock import patch

import numpy as np
import ncp_tangent as runner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError('Create-only audit receipt already exists')
    checks = {}

    def check(name, value):
        checks[name] = bool(value)
        if not value:
            raise AssertionError(name)

    def rejects(name, action, text):
        try:
            action()
        except ValueError as exc:
            check(name, text in str(exc))
        else:
            check(name, False)

    manifest, identity = runner.load_contract()
    check('three_new_interior_cases', len(manifest['cases']) == 3)
    check('identity_has_ten_actual_source_and_code_hashes', len(identity['file_sha256']) == 10)
    sample = {'effective_cpus': 64, 'memory_total_bytes': 128*runner.GIB,
              'memory_available_bytes': 90*runner.GIB, 'slots': 63}
    admit = runner.scheduler_admission
    check('idle_capacity_admits_only_three_pending', admit(sample, 0, 0, 63, 3) == 3)
    check('busy_cpu_still_allows_one_nice_worker', admit({**sample, 'slots': 1}, 12, 4*runner.GIB, 63, 3) == 1)
    check('fully_reserved_cpu_defers', admit(sample, 63, 0, 63, 3) == 0)
    check('memory_reservation_is_in_bytes', admit({**sample, 'memory_available_bytes': 20*runner.GIB}, 0, 4*runner.GIB, 63, 3) == 0)
    check('requested_limit_respected', admit(sample, 0, 0, 2, 3) == 2)

    calls = {'synthetic_integrations': 0, 'sampler': 0}

    def forbidden_sampler():
        calls['sampler'] += 1
        raise AssertionError('Plan or no-pending path must not sample resources')

    def synthetic_success(*args, **kwargs):
        calls['synthetic_integrations'] += 1
        return {'SYNTHETIC_OPERATIONAL_FIXTURE': np.arange(3)}, {
            'status': 'COMPLETED', 'synthetic_operational_fixture': True,
            'new_augmented_IVP': 0}

    def synthetic_failure(*args, **kwargs):
        calls['synthetic_integrations'] += 1
        raise RuntimeError('SYNTHETIC_EXPECTED_WORKER_FAILURE')

    fake_augmented = types.ModuleType('augmented')
    fake_augmented.integrate_case = synthetic_success
    fake_resources = types.ModuleType('resources')
    fake_resources.Sampler = forbidden_sampler
    with tempfile.TemporaryDirectory(prefix='rec-tangent-operational-') as scratch:
        scratch = Path(scratch)
        run = scratch / 'synthetic_run'
        with patch.dict(sys.modules, {'augmented': fake_augmented, 'resources': fake_resources}):
            printed = io.StringIO()
            with redirect_stdout(printed):
                code = runner.main(['--output', str(run)])
            plan = json.loads(printed.getvalue())
            check('plan_only_submits_zero_and_imports_no_sampler', code == 0 and plan['status'] == 'PLAN_ONLY'
                  and plan['new_jobs'] == 0 and calls['sampler'] == 0)
            marker = (run/'RUN_MANIFEST.json').read_bytes()
            rejects('changed_identity_rejected_without_overwrite',
                    lambda: runner.initialise_output(run, {**identity, 'sha256': 'changed'}),
                    'OUTPUT_IDENTITY_MISMATCH')
            check('marker_unchanged', marker == (run/'RUN_MANIFEST.json').read_bytes())
            cases = manifest['cases']

            def job(case):
                return {'case': case, 'directory': str(run/case['id']), 'identity': identity,
                        'admission': {'SYNTHETIC_OPERATIONAL_FIXTURE': True},
                        **{k: manifest[k] for k in ('rtol', 'atol', 'per_case_seconds')}}

            first = runner.run_worker(job(cases[0]))
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (run/cases[0]['id']).iterdir() if p.is_file()}
            repeated = runner.run_worker(job(cases[0]))
            after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (run/cases[0]['id']).iterdir() if p.is_file()}
            check('complete_reuse_no_second_worker_or_overwrite', first['status'] == 'COMPLETE'
                  and repeated['status'] == 'complete_reused' and before == after
                  and calls['synthetic_integrations'] == 1)
            fake_augmented.integrate_case = synthetic_failure
            failed = runner.run_worker(job(cases[1]))
            failure_bytes = (run/cases[1]['id']/'FAILED.json').read_bytes()
            repeated_failure = runner.run_worker(job(cases[1]))
            check('failure_preserved_without_retry', failed['status'] == 'FAILED'
                  and repeated_failure['status'] == 'preserved_failed'
                  and failure_bytes == (run/cases[1]['id']/'FAILED.json').read_bytes()
                  and calls['synthetic_integrations'] == 2)
            (run/cases[2]['id']/'.claim').mkdir(parents=True)
            check('existing_claim_never_resubmitted', runner.run_worker(job(cases[2]))['status'] == 'preserved_claim')
            printed = io.StringIO()
            with redirect_stdout(printed):
                code = runner.main(['--output', str(run), '--execute'])
            no_work = json.loads(printed.getvalue())
            check('no_pending_execute_skips_sampler_and_new_jobs', code == 0
                  and no_work['status'] == 'NO_PENDING_WORK' and no_work['new_jobs'] == 0
                  and calls['sampler'] == 0 and calls['synthetic_integrations'] == 2)
            npz = run/cases[0]['id']/'tangent.npz'
            npz.write_bytes(npz.read_bytes()+b'EXPECTED_HASH_MISMATCH')
            rejects('payload_corruption_rejected', lambda: runner.case_status(run/cases[0]['id'], cases[0], identity),
                    'COMPLETED_CASE_IDENTITY_OR_PAYLOAD_MISMATCH')
            unknown = scratch/'unknown'
            unknown.mkdir()
            (unknown/'peer.txt').write_text('preserve')
            rejects('unknown_output_rejected', lambda: runner.initialise_output(unknown, identity),
                    'NONEMPTY_OUTPUT_WITHOUT_TANGENT_NAMESPACE')
            check('unknown_peer_file_untouched', (unknown/'peer.txt').read_text() == 'preserve')

        leases = scratch/'leases'
        leases.mkdir()
        peer = {'schema': runner.LEASE_SCHEMA, 'host': socket.gethostname(),
                'pid': runner.os.getpid(), 'proc_start_tick': 12345,
                'slots': 61, 'memory_bytes': 10*runner.GIB, 'token': 'synthetic_peer'}
        (leases/'live_peer.json').write_text(json.dumps(peer))
        (leases/'unknown.json').write_text('{not-json')
        originals = {p.name: p.read_bytes() for p in leases.iterdir()}
        lease_args = types.SimpleNamespace(lease_dir=str(leases), reserved_cpus=1,
                                           reserved_memory_gib=0., profile='ncp', max_workers=63)
        sampler = types.SimpleNamespace(sample=lambda *args: sample)
        # The managed sandbox virtualizes getpid separately from mounted /proc.
        # Use an explicit synthetic PID-start provider for this operational fixture.
        with patch.object(runner, '_start_tick', lambda pid: 12345 if pid == runner.os.getpid() else None), \
                runner.resource_lease(lease_args, sampler, 3) as (slots, observation):
            own = list(leases.glob('rec_tangent_*.json'))
            check('live_peer_lease_and_explicit_reservation_both_honored', slots == 1
                  and observation['live_peer_leases'] == 1
                  and observation['reserved_cpus_including_peers'] == 62
                  and observation['unknown_peer_records'] == 1)
            check('only_one_owned_lease_created', len(own) == 1)
        check('owned_lease_removed_and_peer_bytes_preserved', not list(leases.glob('rec_tangent_*.json'))
              and all((leases/name).read_bytes() == value for name, value in originals.items()))

    receipt = {'schema': 'rec.tangent.operational_audit.v1', 'status': 'PASS_SCOPED',
               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'checks': checks, 'check_count': len(checks),
               'audited_code_sha256': runner._sha(runner.ROOT/'code/ncp_tangent.py'),
               'audit_code_sha256': runner._sha(__file__), 'run_identity': identity,
               'synthetic_stub_invocations': calls['synthetic_integrations'],
               'actual_scientific_ODE': 0, 'actual_NCP_jobs': 0, 'benchmarks': 0,
               'resource_observations': 'Synthetic CPU/RAM samples, synthetic PID-start provider and temporary local lease records only; no live NCP allocation observed.',
               'limits': ['No speedup or scaling measurement.', 'No hard-kill timeout experiment.',
                          'No assertion that plan-only or NO_PENDING_WORK means all cases completed.',
                          'No scientific arrays produced by the stub are retained.']}
    output.parent.mkdir(parents=True, exist_ok=True)
    runner._create_json(output, receipt)
    print(json.dumps({'status': receipt['status'], 'checks': len(checks), 'scientific_ODE': 0,
                      'NCP': 0, 'output': str(output)}, sort_keys=True))


if __name__ == '__main__':
    main()
