"""One bounded C9 audit of saved results; no production module is imported."""
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
started = time.monotonic()
start_utc = datetime.now(timezone.utc).isoformat()
resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
resource.setrlimit(resource.RLIMIT_AS, (2147483648, 2147483648))
signal.alarm(60)


def read(path):
    return json.loads(Path(path).read_text())


def rat(value):
    return F(value['exact'])


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def display_check(value):
    if isinstance(value, dict):
        if set(value) == {'exact', 'display'}:
            need(float(F(value['exact'])) == value['display'], 'EXACT_DISPLAY_MISMATCH')
        else:
            for item in value.values():
                display_check(item)
    elif isinstance(value, list):
        for item in value:
            display_check(item)


preexec = {
    'scope': 'Saved raw identity, binding, sign, envelope and two delicate HD value checks only.',
    'start_utc': start_utc,
    'command': [sys.executable, str(Path(__file__).resolve())],
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'cpu_limit_s': 20, 'wall_limit_s': 60, 'address_space_limit_bytes': 2147483648,
    'thread_environment': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')},
    'production_modules_imported': False, 'primary_rerun': False,
    'new_ivp': False, 'native_execution': False,
    'requested_reviewer_identity': 'Astra independent code reviewer reused after capacity rejection',
    'observed_runtime_identity': 'UNKNOWN_NOT_EXPOSED'
}
(OUT/'PREEXEC.json').write_text(json.dumps(preexec, indent=2)+'\n')
result = {'status': 'ERROR', 'preexec': 'PREEXEC.json'}
try:
    hd = read(ROOT/'hd_joint/raw/primary001/DIAGNOSTICS.json')
    hd_pre = read(ROOT/'hd_joint/raw/primary001/PREEXEC.json')
    history_dir = ROOT/'history_remainder/results/primary001'
    summary = read(history_dir/'summary.json')
    retimings = read(history_dir/'retimings.json')
    chords = read(history_dir/'chords.json')
    bindings = read(history_dir/'bindings.json')
    skips = read(history_dir/'skips.json')
    clocks = read(history_dir/'clock_differences.json')
    context = read(ROOT.parent/'program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json')
    freeze = read(ROOT/'history_remainder/freeze.json')
    checked_paths = set()
    for item in hd_pre['inputs_and_code'] + freeze['identities']:
        path = Path(item['path'])
        data = path.read_bytes()
        need(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'CURRENT_FROZEN_IDENTITY_MISMATCH:'+str(path))
        checked_paths.add(str(path))
    for receipt_name in ['primary001.receipt.json', 'plot001.receipt.json']:
        receipt = read(ROOT/'history_remainder/evidence'/receipt_name)
        need(receipt['exit_code'] == 0 and receipt['status'] == 'PASS', 'HISTORY_RECEIPT_STATUS')
        for item in receipt['output_identities']:
            path = ROOT/'history_remainder'/item['path']
            data = path.read_bytes()
            need(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'SAVED_RESULT_IDENTITY_MISMATCH:'+str(path))
    for value in [summary, retimings, chords, bindings, clocks]:
        display_check(value)
    t0, h = rat(summary['grid']['eta0']), rat(summary['grid']['dlna'])
    end = rat(summary['grid']['final_excluded_endpoint'])
    need(end == t0 + 5126*h, 'GRID_ENDPOINT_IDENTITY')
    for j, (binding, witness) in enumerate(zip(bindings, context['queries'])):
        q = F(float.fromhex(witness['query_hex']))
        k = (q-t0)//h
        need(k == witness['cell'] == binding['cell'], 'SOURCE_CELL_BINDING')
        need(binding['incoming_index'] == j and binding['source_index'] == witness['source_index'], 'SOURCE_ORDER_BINDING')
        yl, yr = F(float.fromhex(witness['sample_left_hex'])), F(float.fromhex(witness['sample_right_hex']))
        alpha = (q-(t0+k*h))/h
        native = yl + alpha*(yr-yl)
        need(native == rat(binding['native_real_value']), 'NATIVE_REAL_VALUE_BINDING')
        nominal = F(float.fromhex(witness['nominal_incoming_hex']))
        need(abs(nominal-native) == rat(binding['native_real_anchor_radius']), 'NATIVE_ANCHOR_BINDING')
        need(rat(binding['preserved_stored_geometric_anchor_radius']) == F(witness['anchor_representation_radius_exact']), 'PRESERVED_GEOMETRIC_ANCHOR')
    for row in retimings:
        q, target, step = rat(row['query']), rat(row['target']), rat(row['step'])
        need(t0 <= q < end and t0 <= target < end and step == target-q, 'RETIMING_DOMAIN_OR_STEP')
        signed = F(0)
        bound = F(0)
        for k, weight, jump in row['jump_terms']:
            knot = t0+k*h
            need(min(q,target) < knot < max(q,target), 'START_OR_TARGET_ATOM_INCLUDED')
            w = target-knot if step > 0 else knot-target
            need(w == rat(weight) and w > 0, 'SIGNED_DIRECTION_WEIGHT')
            signed += w*rat(jump)
            bound += w*abs(rat(jump))
        need(signed == rat(row['direct']) == rat(row['signed']), 'SAVED_RETIMING_EQUALITY')
        need(bound == rat(row['bound']) and abs(signed) <= bound, 'SAVED_RETIMING_ENVELOPE')
        if row['case'].startswith('within'):
            need(signed == 0 and not row['jump_terms'], 'WITHIN_CELL_ZERO')
    for row in chords:
        a, x, b = rat(row['a']), rat(row['query']), rat(row['b'])
        need(t0 <= a < x < b < end, 'CHORD_CAUSAL_DOMAIN')
        signed = F(0)
        bound = F(0)
        for k, kernel, jump in row['jump_terms']:
            knot = t0+k*h
            need(a < knot < b, 'CHORD_ATOM_DOMAIN')
            g = (knot-a)*(b-x)/(b-a) if knot <= x else (x-a)*(b-knot)/(b-a)
            need(g == rat(kernel) and g >= 0, 'CHORD_KERNEL')
            signed -= g*rat(jump)
            bound += g*abs(rat(jump))
        need(signed == rat(row['direct']) == rat(row['signed']), 'SAVED_CHORD_EQUALITY')
        need(bound == rat(row['bound']) and abs(signed) <= bound, 'SAVED_CHORD_ENVELOPE')
        if row['right_fallback']:
            need(b == (x+end)/2, 'CAUSAL_FALLBACK_MIDPOINT')
    need(len(retimings)==1240 and len(chords)==len(bindings)==313 and len(clocks)==5127, 'ROW_COUNTS')
    need([s['incoming_index'] for s in skips] == list(range(134,145))+[311], 'ACTUAL_SKIP_WITNESSES')
    need(all(s['status']=='SKIP_CAUSAL_PREFIX' and s['case']=='cross_right' for s in skips), 'SKIP_CLASSIFICATION')
    need(summary['physical_epsilon'] is None and summary['physical_bound_coverage']=='0/313', 'PHYSICAL_BOUND_PROMOTION')
    hd_rows = hd['rows']
    need(len(hd_rows)==24 and {(r['line_id'],r['temperature_K']) for r in hd_rows}=={(i,t) for i in range(1,9) for t in (50,100,200)}, 'HD_CASE_SET')
    tol = Decimal.from_float(128*sys.float_info.epsilon)
    max_errors = {}
    with localcontext() as ctx:
        ctx.prec = 100
        for key in ('paired_flux_imbalance_I','source_planck_deviation_D','source_planck_ratio'):
            errors = [abs((Decimal.from_float(r[key])-Decimal(r['decimal_reference'][key]))/Decimal(r['decimal_reference'][key])) for r in hd_rows]
            need(max(errors) <= tol, 'HD_REFERENCE_TOLERANCE:'+key)
            max_errors[key] = str(max(errors))
        for row in hd_rows:
            need(row['paired_flux_imbalance_I']*row['source_planck_deviation_D'] < 0, 'HD_SIGN_LINK')
            gap = F(row['signed_frequency_gap_Hz_exact']['numerator'])/F(row['signed_frequency_gap_Hz_exact']['denominator'])
            need(abs(gap)==F(row['old_absolute_frequency_gap_Hz']), 'ORIGINAL_GATE_GAP_LINK')
            need(row['old_35_Hz_gate_passed']==(abs(gap)<=35), 'ORIGINAL_GATE_THRESHOLD')
        delicate = [min(hd_rows,key=lambda r:abs(r['source_planck_deviation_D'])), max(hd_rows,key=lambda r:Decimal(r['relative_errors']['source_planck_deviation_D']))]
        delicate_checks = []
        for row in delicate:
            h_si,c,kb = Decimal('6.62607015e-34'), Decimal('299792458'), Decimal('1.380649e-23')
            e = Decimal(row['upper_energy_cm_inverse_literal'])-Decimal(row['lower_energy_cm_inverse_literal'])
            temp = Decimal(row['temperature_K'])
            A = (h_si*c*100*e/(kb*temp)).exp()
            B = (h_si*Decimal('1e9')*Decimal(row['frequency_GHz_literal'])/(kb*temp)).exp()
            up = 1/(B-1)
            down = (1+up)/A
            independent = {'paired_flux_imbalance_I':(up-down)/(up+down),'source_planck_deviation_D':(B-A)/(A-1)}
            errors = {k:abs((Decimal.from_float(row[k])-v)/v) for k,v in independent.items()}
            reference_errors = {k:abs((Decimal(row['decimal_reference'][k])-v)/v) for k,v in independent.items()}
            need(max(errors.values()) <= tol and max(reference_errors.values()) <= tol, 'DELICATE_100_DIGIT_CHECK')
            delicate_checks.append({'line_id':row['line_id'],'temperature_K':row['temperature_K'],'D':row['source_planck_deviation_D'],'production_relative_errors':{k:str(v) for k,v in errors.items()},'saved_80_digit_reference_relative_errors':{k:str(v) for k,v in reference_errors.items()}})
    need(hd['physical_source_gate']=='FAIL_ORIGINAL_35_HZ_7_OF_8' and hd['production_approved'] is False, 'HD_SOURCE_PROMOTION')
    need(sum(not g['passed'] for g in hd['line_source_gates'])==7, 'HD_GATE_FAILURE_COUNT')
    need(hd['physical_epsilon'] is None and hd['physical_bound_coverage']=='0/313' and not hd['collider_mixing'] and not hd['temperature_extrapolation'], 'HD_SCOPE')
    result.update(status='PASS', checked_current_frozen_paths=len(checked_paths),
                  exact_serialized_retimings=len(retimings), exact_serialized_chords=len(chords),
                  native_real_binding_reconstructions=len(bindings), serialized_clock_records=len(clocks),
                  retiming_counts=dict(Counter(r['case'] for r in retimings)), right_crossing_skips=len(skips),
                  nonzero_crossing_remainders=sum(r['case'].startswith('cross') and rat(r['direct'])!=0 for r in retimings),
                  chord_cases_with_strict_cancellation=sum(abs(rat(r['direct']))<rat(r['bound']) for r in chords),
                  HD_actual_cases=len(hd_rows),HD_max_recomputed_relative_errors=max_errors,
                  HD_delicate_100_digit_checks=delicate_checks, primary_rerun=False,
                  production_modules_imported=False, frozen_source_and_code_current=True,
                  saved_history_output_identities_current=True)
except Exception as exc:
    result['error'] = repr(exc)
finally:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result.update(start_utc=start_utc,end_utc=datetime.now(timezone.utc).isoformat(),
                  process_cpu_s=usage.ru_utime+usage.ru_stime,
                  wall_after_import_s=time.monotonic()-started,peak_rss_KiB=usage.ru_maxrss,
                  unmeasured_receipt_serialization_tail='UNKNOWN_NOT_ZERO',
                  input_parsing_and_hashing_included_in_process_cpu=True)
    (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
signal.alarm(0)
raise SystemExit(0 if result['status']=='PASS' else 1)
