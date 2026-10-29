"""Export nine actual source-owned published line relationships and cycle design.

All rows derive from the pinned PR164 source JSON; no generated lab measurements.
"""
from pathlib import Path
import csv, importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cycles',ROOT/'src/correlated_cycles.py')
cycles=importlib.util.module_from_spec(spec);spec.loader.exec_module(cycles)

def write():
    a=cycles.read_source(ROOT/'input/LAB_INPUT_PR164_IMMUTABLE.json')
    values=cycles.measurements_mhz(a)
    rows=[]
    old=a['inherited_measurements']
    for i,rec in enumerate(old):
        units='Hz' if 'nominal_Hz' in rec else 'cm^-1'
        center=rec.get('nominal_Hz',rec.get('nominal_cm_minus1'))
        err=rec.get('uncertainty_Hz',rec.get('reported_plusminus_cm_minus1'))
        doi=rec['doi']
        rows.append({'row':i,'id':rec['id'],'upper_J':rec['upper_J'],'lower_J':rec['lower_J'],
                     'published_nominal':center,'published_unit':units,
                     'published_uncertainty_literal':err,'uncertainty_kind':'PUBLISHED_ORIGINAL_AS_TRANSCRIBED',
                     'frequency_MHz_derived':cycles.format_decimal(values[i]),'DOI':doi,
                     'measured_not_inferred':True})
    for j,rec in enumerate(a['line_parameters']):
        i=j+len(old)
        rows.append({'row':i,'id':'Sung2022_'+rec['R'],'upper_J':rec['upper_J'],'lower_J':rec['lower_J'],
                     'published_nominal':rec['nu0_cm_minus1'],'published_unit':'cm^-1',
                     'published_uncertainty_literal':rec['nu0_reported_fit_unc_cm_minus1'],
                     'uncertainty_kind':'MULTISPECTRAL_FIT_ONLY_EXCLUDES_SYSTEMATICS',
                     'frequency_MHz_derived':cycles.format_decimal(values[i]),
                     'DOI':a['primary_source']['doi'],'measured_not_inferred':True})
    out=ROOT/'evidence/MEASURED_NINE_ROWS.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    x=[cycles.F(rec['nu0_cm_minus1']) for rec in a['line_parameters']]
    B=cycles.two_parameter_sung_calibration(x)
    CM=cycles.matmul(cycles.C,B)
    observed=[cycles.dot(row,values) for row in cycles.C]
    out=ROOT/'evidence/CYCLE_CALIBRATION_RESPONSE.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['cycle','observed_nominal_MHz','source_common_offset_projection','source_common_scale_projection_cm_minus1','status'])
        w.writeheader()
        for j,rv in enumerate(observed):
            w.writerow({'cycle':j+1,'observed_nominal_MHz':cycles.format_decimal(rv),
                        'source_common_offset_projection':cycles.format_decimal(CM[j][0]),
                        'source_common_scale_projection_cm_minus1':cycles.format_decimal(CM[j][1]),
                        'status':'ACTUAL_NOMINAL_MEASURED_CYCLE_PLUS_HYPOTHETICAL_CALIBRATION_RESPONSE'})
    return len(rows)

if __name__=='__main__':print('measured rows',write())