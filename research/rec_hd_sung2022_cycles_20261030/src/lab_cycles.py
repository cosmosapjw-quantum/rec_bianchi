"""Source-bounded HD laboratory cycle constraints and 296 K H2-pressure conditional observables.

No inverse spectroscopic fit, no catalog update, no statistical significance or owner switch.
Pure Python stdlib, decimal exact source-literal arithmetic and integer incidence ranks.
"""
from __future__ import annotations
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
import argparse, csv, json

getcontext().prec = 75
D = Decimal
C = D(299792458)
H = D('6.62607015e-34')
CM_TO_HZ = C * 100
ONE_MHZ = D(10)**6
DOI_SUNG = '10.1016/j.jqsrt.2022.108412'
DOI_1984 = '10.1139/p84-213'
DOI_2022_20 = '10.1140/epjd/s10053-022-00552-x'
DOI_2022_31 = '10.1103/PhysRevA.105.062823'
EDGE = [(2,0),(3,1),(4,3),(6,5),(7,6),(1,0),(2,1),(3,2),(4,3)]
CYCLES = [[1,0,0,0,0,-1,-1,0,0],
          [0,1,0,0,0,0,-1,-1,0],
          [0,0,1,0,0,0,0,0,-1]]

def load_and_validate(path:Path):
    a=json.loads(Path(path).read_text(encoding='utf8'))
    if a.get('schema')!='REC_HD_SUNG_2022_MULTISPECTRAL_LAB_MEASURED_V1':
        raise ValueError('input schema change')
    if a['primary_source']['doi']!=DOI_SUNG or a['primary_source']['joint_covariance'] is not None:
        raise ValueError('source provenance/covariance changed')
    if a['protection']['original_35Hz']!='FAIL7/8' or a['protection']['production']!='HOLD':
        raise ValueError('immutable protection changed')
    if a['protection']['CDMS_2011_v2_original_raw']!='NOT_ACQUIRED':
        raise ValueError('raw CDMS acquisition must be independently proved')
    line=a['line_parameters']; old=a['inherited_measurements']
    if len(line)!=4 or len(old)!=5:
        raise ValueError('source rows count mismatch')
    for j,item in enumerate(line):
        if (item['upper_J'],item['lower_J'],item['R']) != (j+1,j,f'R({j})'):
            raise ValueError('line assignment mismatch')
        for k in ['nu0_cm_minus1','nu0_reported_fit_unc_cm_minus1','S_296_cm_per_molecule',
                  'H2_gamma0_cm_minus1_per_atm','historical_A_s_minus1']:
            if D(item[k])<=0:
                raise ValueError(f'non-positive {k} at J={j+1}')
    for item,doi in zip(old,[DOI_2022_20,DOI_2022_31,DOI_1984,DOI_1984,DOI_1984]):
        if item['doi']!=doi:
            raise ValueError('historical primary DOI not source locked')
    if [(q['upper_J'],q['lower_J']) for q in old+line]!=EDGE:
        raise ValueError('incidence edge mapping has changed')
    return a

def incidence():
    mat=[]
    for u,l in EDGE:
        row=[0]*9;row[u]=1;row[l]=-1;mat.append(row)
    return mat

def rank_exact(matrix):
    a=[[Fraction(x) for x in row] for row in matrix]
    rows=len(a);cols=len(a[0]);pivot=0
    for j in range(cols):
        i=next((i for i in range(pivot,rows) if a[i][j]!=0),None)
        if i is None: continue
        a[pivot],a[i]=a[i],a[pivot]
        t=a[pivot][j];a[pivot]=[x/t for x in a[pivot]]
        for k in range(rows):
            if k!=pivot and a[k][j]!=0:
                s=a[k][j];a[k]=[x-s*y for x,y in zip(a[k],a[pivot])]
        pivot+=1
        if pivot==rows:break
    return pivot

def groups():
    g={i:set() for i in range(9)}
    for u,l in EDGE:g[u].add(l);g[l].add(u)
    left=set(g);component=[]
    while left:
        root=min(left);stack=[root];seen=set()
        while stack:
            p=stack.pop()
            if p in seen:continue
            seen.add(p);stack.extend(g[p]-seen)
        left-=seen;component.append(sorted(seen))
    return component

def observations(a):
    old=a['inherited_measurements']; line=a['line_parameters']
    vals=[D(q['nominal_Hz']) if 'nominal_Hz' in q else D(q['nominal_cm_minus1'])*CM_TO_HZ for q in old]
    vals.extend(D(q['nu0_cm_minus1'])*CM_TO_HZ for q in line)
    return vals

def compute(a):
    d=incidence(); obs=observations(a)
    if rank_exact(d)!=6 or rank_exact(CYCLES)!=3:
        raise ValueError('unexpected graph rank')
    for row in CYCLES:
        test=[sum(row[i]*d[i][j] for i in range(9)) for j in range(9)]
        if any(test):raise ValueError('cycle identity not exact')
    residuals=[sum(D(CYCLES[i][j])*obs[j] for j in range(9)) for i in range(3)]
    # Exact minimax in the source integer/decimal Hz domain, avoiding division
    # by c followed by inverse conversion (which otherwise inserts decimal tails).
    d0_hz,d1_hz=residuals[:2]
    correction_hz=(max(D(0),d0_hz,d1_hz)-min(D(0),d0_hz,d1_hz))/2
    common_hz=(max(D(0),d0_hz,d1_hz)+min(D(0),d0_hz,d1_hz))/2
    line_corrections_hz=[d0_hz-common_hz,common_hz,d1_hz-common_hz]
    if max(abs(t) for t in line_corrections_hz)!=correction_hz:
        raise ValueError('minimal correction witness invalid')
    if line_corrections_hz[0]+line_corrections_hz[1]!=d0_hz or line_corrections_hz[1]+line_corrections_hz[2]!=d1_hz:
        raise ValueError('minimal correction does not satisfy source constraints')
    names=['C20_Cozijn_minus_Sung_R0_R1','C31_Cozijn_minus_Sung_R1_R2','C43_Essenwanger_minus_Sung_R3']
    cycles=[{'id':n,'difference_Hz':str(z),'difference_MHz':str(z/ONE_MHZ),'difference_cm_minus1':str(z/CM_TO_HZ),'statistical_sigma':None} for n,z in zip(names,residuals)]
    line_data=[]; pressure=[]
    for q in a['line_parameters']:
        u=q['upper_J'];w=D(q['nu0_cm_minus1']);gamma=D(q['H2_gamma0_cm_minus1_per_atm']);shift=D(q['H2_delta0_cm_minus1_per_atm']);A=D(q['historical_A_s_minus1'])
        freq=w*CM_TO_HZ
        line_data.append({'upper_J':u,'lower_J':u-1,'frequency_Hz':str(freq),'frequency_cm_minus1':str(w),'fitted_position_error_cm_minus1':q['nu0_reported_fit_unc_cm_minus1'],'fit_error_not_total':True,
          'h2_gamma_cm_minus1_atm_minus1':str(gamma),'h2_delta_cm_minus1_atm_minus1':str(shift),
          'S_296_cm_per_molecule':q['S_296_cm_per_molecule'], 'historic_2021_A_s_minus1':str(A),
          'photon_energy_J':str(H*freq),'photon_wavelength_m':str(C/freq),'conditional_spontaneous_power_per_upper_HD_W':str(A*H*freq)})
        for p in [D('0.1'),D('0.5'),D('1')]:
            pressure.append({'upper_J':u,'lower_J':u-1,'T_K':'296','H2_partial_pressure_atm':str(p),'conditional_center_cm_minus1':str(w+shift*p),
             'pressure_center_shift_MHz':str(shift*p*CM_TO_HZ/ONE_MHZ),'H2_lorentz_HWHM_cm_minus1':str(gamma*p),
             'H2_lorentz_FWHM_cm_minus1':str(2*gamma*p),'applies_only_as_linear_296K_H2_pressure_model':True})
    return {
      'schema':'REC_HD_SUNG2022_CYCLE_ATLAS_V1','authority':'PRIMARY_SUNG_TABLE4_WITH_HISTORICAL_SOURCE_LOCKS',
      'new_direct_lab_line_positions':4,'inherited_direct_measurement_edges':5,'measured_equations':9,
      'number_of_levels':9,'independent_rank':6,'nullity':3,'cycle_space_dim':3,'components':groups(),
      'cycles':cycles,'minimum_max_abs_lowJ_frequency_correction_MHz':str(correction_hz/ONE_MHZ),
      'minimum_max_abs_lowJ_correction_cm_minus1':str(correction_hz/CM_TO_HZ),
      'nominal_minimax_correction_witness_MHz':[str(t/ONE_MHZ) for t in line_corrections_hz],
      'calibration_reference_only_MHz':str(D(a['primary_source']['calibration_better_than_cm_minus_1'])*CM_TO_HZ/ONE_MHZ),
      'minimal_correction_is_not_a_statistical_significance':True,
      'source_fit_joint_covariance':None,'source_experiment_joint_covariance':None,
      'line_atlas':line_data,'pressure_conditional_rows':pressure,
      'canonical_DAG':'28/88','REC_physical_DAG':'0/313','REC_EXP_SPECTRAL':'PARTIAL_4_NEW_SUNG_EXPERIMENT_LINES',
      'original_35Hz':'FAIL7/8','H5_epsilon':None,'H6':'OPEN','H7':'OPEN','production':'HOLD',
      'independent_different_author_R6_C9':'NOT_RUN','auto_next_node':False
    }

def save_outputs(result,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    files=[('SUNG4_SOURCE_PHYSICAL.csv',result['line_atlas']),('H2_PRESSURE_296K_CONDITIONAL.csv',result['pressure_conditional_rows']),('EXPERIMENTAL_CYCLES.csv',result['cycles'])]
    for name,rows in files:
        with (out/name).open('w',newline='',encoding='utf8') as h:
            writer=csv.DictWriter(h,fieldnames=list(rows[0].keys()));writer.writeheader();writer.writerows(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(Path(__file__).resolve().parents[1]/'data/LAB_INPUT.json'));p.add_argument('--output',default=str(Path(__file__).resolve().parents[1]/'evidence'))
    a=p.parse_args();save_outputs(compute(load_and_validate(Path(a.input))),Path(a.output))
