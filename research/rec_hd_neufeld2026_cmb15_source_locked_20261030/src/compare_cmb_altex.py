"""Source-authentic standard vs alternative high-J extrapolation, under a CMB bath.

Scope: independent exploratory Neufeld (2026) 15-level HD model, two original
source tables, no CDMS 2011 owner default/35 Hz replacement. All rates at
exactly the author's tabulated temperatures, OPR=3, optically thin escape.
"""
from __future__ import annotations
from pathlib import Path
import argparse, csv, hashlib, json, math
from pr169_neufeld15_reference import parse_lamda
from hd_cmb15 import solve_cmb, TCMB0_K

SOURCE_T_GRID=(100.,200.,300.,400.,600.,1000.,2000.,3000.,4000.)
SOURCE_D_GRID=(100.,1e4,1e6,1e8,1e10)
REDSHIFTS=(0.,10.,30.,50.,73.,100.)

STANDARD='f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb'
ALTERNATE='66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac'


def compare(data_dir:Path, output:Path):
    data_dir=Path(data_dir); output=Path(output); output.mkdir(parents=True,exist_ok=True)
    src_a=(data_dir/'hd_lamda.dat').read_bytes(); src_b=(data_dir/'hd_lamda_altex.dat').read_bytes()
    if hashlib.sha256(src_a).hexdigest()!=STANDARD or hashlib.sha256(src_b).hexdigest()!=ALTERNATE:
        raise ValueError('Original Neufeld2026 .dat checksum mismatch')
    a=parse_lamda(src_a, verify=True); b=parse_lamda(src_b)
    if a.levels!=b.levels or a.rad!=b.rad or set(a.collision)!=set(b.collision):
        raise ValueError('Cannot compare when level energies or Einstein lines changed')
    changed=[]
    for collider in (2,3):
        temps_a,ra=a.collision[collider];temps_b,rb=b.collision[collider]
        if temps_a!=temps_b or set(ra)!=set(rb):raise ValueError('Temperature/collision edge source mismatch')
        for (u,l),row in ra.items():
            if row!=rb[u,l]:changed.append((collider,u,l))
    if len(changed)!=54 or any(u<=8 for _,u,_ in changed):
        raise ValueError('Unexpected rate-change scope; expected 54 high-J extrapolations')
    cases=[]; line_rows=[]; max_stationarity=0; min_pop=1.; upper_rel_error=None
    for T in SOURCE_T_GRID:
        for n in SOURCE_D_GRID:
            for z in REDSHIFTS:
                r1=solve_cmb(a,T,n,z); r2=solve_cmb(b,T,n,z)
                power1=r1['net_cooling_W_per_HD']; power2=r2['net_cooling_W_per_HD']
                # Near zero crossing, relative error is ill-conditioned: retain absolute delta
                # and only admit a relative ratio if both source powers are well separated
                # from cancellation. This is NOT a threshold for scientific acceptance.
                delta=power2-power1
                relative=(delta/power1 if abs(power1)>=1e-35 else None)
                pa=r1['populations_J0_to_J14'];pb=r2['populations_J0_to_J14']
                for r in (r1,r2):
                    if abs(r['sum_pop']-1)>2e-12 or any(x<0 for x in r['populations_J0_to_J14']):
                        raise ArithmeticError('Unphysical 15-level steady-state population')
                    max_stationarity=max(max_stationarity,r['max_stationary_residual_s_inverse'])
                    min_pop=min(min_pop,*r['populations_J0_to_J14'])
                cell={'Tgas_K':T,'nH2_cm3':n,'z':z,'Tbg_K':TCMB0_K*(1+z),
                     'std_net_cooling_W_per_HD':power1,'alternate_net_cooling_W_per_HD':power2,
                     'alternate_minus_std_W_per_HD':delta,'relative_alternate_minus_std':relative,
                     'std_J0':pa[0],'alt_J0':pb[0], 'std_J9':pa[9], 'alt_J9':pb[9],
                     'max_abs_population_difference':max(abs(x-y) for x,y in zip(pa,pb)),
                     'sign_std':0 if power1==0 else math.copysign(1,power1),
                     'sign_alt':0 if power2==0 else math.copysign(1,power2)}
                cases.append(cell)
                for i,(one,two) in enumerate(zip(r1['line_power_records'],r2['line_power_records'])):
                    if one['J_upper']!=two['J_upper'] or one['nu_Hz']!=two['nu_Hz']:
                        raise ValueError('Line identity changed unexpectedly')
                    line_rows.append({'Tgas_K':T,'nH2_cm3':n,'z':z,
                                      'J_upper':one['J_upper'],'J_lower':one['J_lower'],
                                      'frequency_Hz':one['nu_Hz'],
                                      'std_net_W_per_HD':one['net_W_per_HD'],
                                      'alt_net_W_per_HD':two['net_W_per_HD'],
                                      'std_spontaneous_W_per_HD':one['spontaneous_W_per_HD'],
                                      'alt_spontaneous_W_per_HD':two['spontaneous_W_per_HD']})
    if len(cases)!=270 or len(line_rows)!=3780:
        raise AssertionError("Source 270/3780 grid wrong")
    for name,rows in [('CMB15_STANDARD_VS_ALTEX_270_STATES.csv',cases),
                      ('CMB15_STANDARD_VS_ALTEX_3780_LINE_PAIRS.csv',line_rows)]:
        with (output/name).open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    rel=[x for x in cases if x['relative_alternate_minus_std'] is not None]
    maxcase=max(cases,key=lambda r:abs(r['alternate_minus_std_W_per_HD']))
    relative_case=max(rel,key=lambda r:abs(r['relative_alternate_minus_std']))
    different_sign=[x for x in cases if x['sign_std']!=x['sign_alt']]
    # Physical magnitude and sign are more informative than a relative ratio near
    # a zero crossing; detailed records preserve all conditions.
    summary={'scope':'NEUFELD2026_ORIGINAL_STANDARD_VS_ALTERNATE_EXTRAPOLATION_WITH_ISOTROPIC_CMB',
        'sha_standard_dat':STANDARD,'sha_alternate_dat':ALTERNATE,
        'source_original_changed_rate_rows':len(changed),'rates_changed_only_above_J8':True,
        'states':len(cases),'line_pairs':len(line_rows),
        'max_stationarity_residual_s_inverse':max_stationarity,'minimum_population':min_pop,
        'max_absolute_cooling_delta_W_per_HD':maxcase['alternate_minus_std_W_per_HD'],
        'at_max_absolute':maxcase,
        'largest_relative_delta_among_nonzero':relative_case,
        'cross_source_sign_disagreements':different_sign,
        'canonical_DAG':'28/88','REC_physical_DAG':'0/313','original_35Hz':'FAIL7/8',
        'production':'HOLD','independent_reviewer':'NOT_RUN'}
    (output/'CMB15_EXTRAPOLATION_COMPARISON_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    p=ap.parse_args();print(json.dumps(compare(p.source,p.output),indent=2))
