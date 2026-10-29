"""Conservative source-text HD printed-energy crosswalk. No fit, sigma or source switch."""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path

getcontext().prec = 65
C = Decimal(299792458)             # SI exact, m/s
HZ_PER_CM1 = C * Decimal(100)       # 1/cm -> Hz
ROUNDING_HALF = Decimal('0.0000005')  # 2011 .egy printed to 6 dp in cm^-1
EXPECTED_LAMDA_PIN = '0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
LAB = ((2,0,Decimal('8006533168000'),Decimal('26000'), '10.1140/epjd/s10053-022-00552-x'),
       (3,1,Decimal('13283245098000'),Decimal('30000'), '10.1103/PhysRevA.105.062823'))


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def value(v):
    return format(v, 'f')


def calculate(cdms, lamda):
    def require(condition,message):
        if not condition: raise ValueError(message)
    require(cdms['schema'] == 'REC_HD_CDMS2011V2_PRINTED_EGY_TRANSCRIPTION_V1','Unexpected CDMS transcription schema')
    require(cdms['raw_file_obtained'] is False,'Source kind changed; no raw source acquired')
    require(lamda['exact_source_bytes_acquired'] is False,'Incompatible parent authority expectation')
    require(lamda['historical_pinned_original']['sha256'] == EXPECTED_LAMDA_PIN,'Wrong historical LAMDA pin')
    require(len(cdms['levels']) == len(lamda['levels']) == 9,'Nine level rows required')
    require(len(lamda['radiative_lines']) == 8,'Eight radiative lines required')
    E = [Decimal(r['E_cm1']) for r in cdms['levels']]
    EL = [Decimal(r['E_cm1']) for r in lamda['levels']]
    P = [Decimal(r['nu_GHz'])*Decimal('1000000000') for r in lamda['radiative_lines']]
    A = [Decimal(r['A_s1']) for r in lamda['radiative_lines']]
    require([x['J'] for x in cdms['levels']] == list(range(9)),'Incorrect J ordering')
    require(all(r['v'] == 0 and Decimal(r['g']) == 2*r['J']+1 for r in cdms['levels']),'Incorrect v/g')
    require(all(lamda['radiative_lines'][i]['upper_J'] == i+1 for i in range(8)),'Incorrect radiative order')
    require(all(A[i] > 0 and P[i] > 0 for i in range(8)),'Nonpositive physical source value')
    Eprefix = [Decimal(0)]
    for p in P:
        Eprefix.append(Eprefix[-1]+p/HZ_PER_CM1)
    offsets = [Eprefix[j]-E[j] for j in range(9)]
    all_pass = all(abs(r) <= ROUNDING_HALF for r in offsets)
    require(all_pass,'Printed-photon spectrum is NOT globally compatible with 2011 .egy print cells')
    # Joint rather than only separate line checks, with exactly one fixed J=0 anchor.
    rows=[]
    for j in range(1,9):
        nu_egy = (E[j]-E[j-1])*HZ_PER_CM1
        nu_lamda_level = (EL[j]-EL[j-1])*HZ_PER_CM1
        rows.append({
            'J_upper':j,'J_lower':j-1,
            'cdms2011_v2_printed_E_upper_cm1':value(E[j]),
            'cdms2011_v2_printed_E_lower_cm1':value(E[j-1]),
            'cdms2011_v2_printed_gap_Hz':value(nu_egy),
            'lamda2021_printed_photon_Hz':value(P[j-1]),
            'lamda2021_term_gap_Hz':value(nu_lamda_level),
            'egy_gap_minus_photon_Hz':value(nu_egy-P[j-1]),
            'lamda_term_gap_minus_photon_Hz':value(nu_lamda_level-P[j-1]),
            'photon_cumulative_level_minus_egy_cm1':value(offsets[j]),
            'egy_energy_printing_halfwidth_cm1':value(ROUNDING_HALF),
            'joint_print_cell_compatible':abs(offsets[j])<=ROUNDING_HALF,
            'einstein_A_source_s_minus_1':value(A[j-1])
        })
    combos=[]
    for u,l,y,sigma,doi in LAB:
        older_egy_gap = (E[u]-E[l])*HZ_PER_CM1
        source_p_gap = sum(P[l:u],Decimal(0))
        combos.append({
            'level':f'v0_J{u}_minus_J{l}',
            'measurement_Hz':value(y),
            'published_meas_uncertainty_Hz':value(sigma),
            'doi':doi,
            '2011_egy_printed_combination_Hz':value(older_egy_gap),
            '2021_lamda_photon_combination_Hz':value(source_p_gap),
            'measured_minus_egy_print_Hz':value(y-older_egy_gap),
            'measured_minus_photon_Hz':value(y-source_p_gap),
            'fit_covariance_status':'NOT_ACQUIRED',
            'catalog_vs_lab_sigma_significance':None,
            'max_printed_egy_combination_roundoff_Hz':value(HZ_PER_CM1*Decimal('0.000001'))
        })
    maxoffset=max(abs(z) for z in offsets)
    return {'schema':'REC_HD_CDMS2011V2_PRINTED_ENERGY_CROSSWALK_V1',
            'claim':'2011 v2 .egy displayed ground-state level energies and inherited 2021 source photon frequencies admit ONE global 9-level vector within 6-decimal print cells; NOT a fitted spectrum or byte provenance',
            'line_count':8, 'level_count':9,
            'joint_print_cell_pass_count':sum(abs(z)<=ROUNDING_HALF for z in offsets[1:]),
            'joint_print_cell_total':8,
            'maximum_abs_cumulative_offset_cm1':value(maxoffset),
            'minimum_print_cell_slack_cm1':value(ROUNDING_HALF-maxoffset),
            'level0_fixed_cm1':'0',
            'frequency_to_wavenumber_exact_hz_per_cm1':value(HZ_PER_CM1),
            'source_kind':'OFFICIAL_CDMS_V2_RENDERED_EGY_TEXT_AND_PARENT_LAMDA_TRANSCRIPTION_NOT_RAW',
            'source_2011_v2_raw':'NOT_ACQUIRED',
            'fit_joint_covariance':None,
            'native_production':'HOLD',
            'old_35Hz_gate':'FAIL7/8_UNCHANGED',
            'central_dag':'28/88_UNCHANGED',
            'rec_physical_dag':'0/313_UNCHANGED',
            'source_lines':rows,
            'measured_combinations':combos}


def generate(cdms_path,lamda_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=calculate(load_json(cdms_path),load_json(lamda_path))
    (out/'CROSSWALK.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for path,records in ((out/'LINE_CROSSWALK.csv',data['source_lines']),
                         (out/'LAB_COMBINATION_CROSSWALK.csv',data['measured_combinations'])):
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    print(json.dumps({k:v for k,v in data.items() if k not in ('source_lines','measured_combinations')},indent=2))
    return data


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--cdms',default=str(Path(__file__).resolve().parents[1]/'source/CDMS2011_V2_EGY_V0_TRANSCRIPTION.json'))
    root=Path(__file__).resolve().parents[1]
    bundled=root/'reference/pr161/data/LAMDA_HD_SOURCE_TRANSCRIPTION.json'
    ancestor=root.parent/'rec_hd_nlte_20261030/data/LAMDA_HD_SOURCE_TRANSCRIPTION.json'
    p.add_argument('--lamda',default=str(bundled if bundled.is_file() else ancestor))
    p.add_argument('--output',default=str(Path(__file__).resolve().parents[1]/'evidence'))
    a=p.parse_args();generate(a.cdms,a.lamda,a.output)
