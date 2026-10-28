#!/usr/bin/env python3
"""Source-preserving printed-decimal compatibility audit for public LAMDA HD.

A certificate about printed numbers under nearest-rounding, NOT a molecular
spectroscopic fit, CDMS version-2 authenticity test, physical rate provider or
substitute for the original source-locked 35-Hz gate.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

C_M_PER_S = Decimal('299792458')
H_J_S = Decimal('6.62607015e-34')
K_B_J_K = Decimal('1.380649e-23')
NU_GHZ_TO_HZ = Decimal('1e9')
WAVENUMBER_CM_TO_M = Decimal(100)


def half_quantum(token: str) -> Decimal:
    """Max error of round-to-nearest for the exact printed decimal literal."""
    d = Decimal(token)
    if not d.is_finite():
        raise ValueError('nonfinite printed decimal')
    return Decimal('0.5') * (Decimal(10) ** d.as_tuple().exponent)


def audit(levels: list[dict], lines: list[dict]) -> dict:
    if len(levels) != 9 or len(lines) != 8:
        raise ValueError('HD printed fixture must have exactly nine J states and eight adjacent lines')
    if [int(x['J']) for x in levels] != list(range(9)):
        raise ValueError('J sequence is not 0..8')
    if [int(x['J_up']) for x in lines] != list(range(1, 9)):
        raise ValueError('line list must be J=1->0 through J=8->7')
    with localcontext() as ctx:
        ctx.prec = 60
        out=[]
        for j, line in enumerate(lines, start=1):
            wup, wlo = levels[j]['w_cm_minus_1'], levels[j-1]['w_cm_minus_1']
            fghz = line['nu_GHz']
            up,lo,nu = Decimal(wup),Decimal(wlo),Decimal(fghz)
            if not all(v.is_finite() for v in (up,lo,nu)):
                raise ValueError('nonfinite printed transition')
            if up <= lo or nu <= 0:
                raise ValueError('invalid positive adjacent HD rotational transition')
            delta = WAVENUMBER_CM_TO_M*C_M_PER_S*(up-lo) - NU_GHZ_TO_HZ*nu
            bound = WAVENUMBER_CM_TO_M*C_M_PER_S*(half_quantum(wup)+half_quantum(wlo)) + NU_GHZ_TO_HZ*half_quantum(fghz)
            if bound <= 0:
                raise ValueError('nonpositive precision allowance')
            excess = max(Decimal(0), abs(delta)-bound)
            status = 'PASS_PRINT_NEAREST_COMPATIBLE' if excess == 0 else 'FAIL_PRINT_NEAREST_ONLY'
            out.append({
                'j_up':j,'j_low':j-1, 'w_up_literal':wup,'w_low_literal':wlo,'nu_GHz_literal':fghz,
                'delta_Hz':str(delta),'absolute_delta_Hz':str(abs(delta)),
                'nearest_rounding_bound_Hz':str(bound), 'signed_interval_Hz':[str(delta-bound),str(delta+bound)],
                'minimum_nonrounding_excess_Hz':str(excess),
                'formal_source_affinity_intervals':{str(t):[str(H_J_S*(delta-bound)/(K_B_J_K*Decimal(t))),str(H_J_S*(delta+bound)/(K_B_J_K*Decimal(t)))] for t in (50,100,200)},
                'truncation_envelope_Hz':str(bound*2),
                'minimum_nontruncation_excess_Hz':str(max(Decimal(0),abs(delta)-2*bound)),
                'classification':status
            })
        return {'schema':'REC_HD_PRINTED_PRECISION_CERT_V1',
                'physical_admission':False,'original_cdms_v2_raw':'NOT_ACQUIRED',
                'assumption':'Each printed literal was separately rounded to nearest; units: w in cm^-1, nu in GHz; c exact SI',
                'rounding_only_fail_count':sum(r['classification'].startswith('FAIL') for r in out),
                'print_rows':out}


def parse_spcat_line(row: str) -> dict:
    """Conservative documented [F13.4,2F8.4,I2,F10.4,I3,I7,I4,12I2] header parser.

    Do not infer state mapping from QNs or use the line as a vetted v2 measurement.
    In a SPCAT catalog negative TAG indicates experimental lab value, not proof of
    provenance of an arbitrary LAMDA column.
    """
    if len(row) < 55: raise ValueError('short SPCAT catalog record')
    try:
        freq=Decimal(row[0:13].strip())
        uncertainty=Decimal(row[13:21].strip())
        dr=int(row[29:31].strip())
        elo=Decimal(row[31:41].strip())
        gup=int(row[41:44].strip())
        tag=int(row[44:51].strip())
        qnfmt=int(row[51:55].strip())
    except (ValueError,ArithmeticError) as err:
        raise ValueError('malformed fixed-width SPCAT header') from err
    if not all(v.is_finite() for v in (freq,uncertainty,elo)):
        raise ValueError('nonfinite SPCAT header')
    if abs(tag)!=3501 or freq <= 0 or uncertainty < 0 or gup <= 0:
        raise ValueError('unexpected species tag or invalid SPCAT header')
    return {'frequency_literal':str(freq),'uncertainty_literal':str(uncertainty),
            'frequency_unit':'MHz_assumed_requires_source_confirmation',
            'uncertainty_unit':'MHz_assumed_requires_source_confirmation',
            'dr':dr,'elo_cm_minus_1':str(elo),'gup':gup,'species_tag':abs(tag),
            'measured_tag':tag<0,'qnfmt':qnfmt,'raw_quantum_numbers':row[55:].rstrip(),
            'source_version':'UNVERIFIED','lamda_mapping':'NOT_ATTEMPTED'}


def verify_cdms_file(path:Path, expected_sha256:str|None):
    if not expected_sha256 or len(expected_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise ValueError('CDMS original raw SHA256 must be explicitly pinned before ingestion')
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual!=expected_sha256:
        raise ValueError(f'CDMS SHA256 MISMATCH: {actual}')
    records=[]
    for r in data.decode('ascii').splitlines():
        if r.strip(): records.append(parse_spcat_line(r))
    return {'sha256':actual,'bytes':len(data),'rows':records,
            'source_version':'HASH_LOCKED_ONLY_NOT_AUTHENTICATED_V2',
            'physical_admission':False}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture', type=Path, default=Path(__file__).with_name('public_print_transcription.json'))
    p.add_argument('--output', type=Path)
    p.add_argument('--cdms-cat', type=Path)
    p.add_argument('--expected-cdms-sha256')
    a=p.parse_args()
    src=json.loads(a.fixture.read_text(encoding='utf8'))
    if src.get('source_status')!='TRANSCRIBED_PUBLIC_PRINT_NOT_BYTE_LOCKED':
        raise ValueError('fixture source status must explicitly bar byte-identity claims')
    result=audit(src['levels'],src['radiative_lines'])
    result['source_identity']=src['source_status']
    result['reference_url']=src['reference_url']
    if a.cdms_cat:
        result['candidate_cdms_cat']=verify_cdms_file(a.cdms_cat,a.expected_cdms_sha256)
    elif a.expected_cdms_sha256:
        raise ValueError('CDMS hash given without original file')
    payload=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(payload,encoding='utf8')
    else: print(payload)

if __name__=='__main__': main()
