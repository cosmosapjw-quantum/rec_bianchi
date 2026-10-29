"""Lab-anchored HD ground-rotational combination observables, no production source promotion.

Only primary 2022 measured combination differences and pinned PR156 source results.
Do not reuse as LAMDA/CDMS raw catalog or as an energy source in REC/REI.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import csv, hashlib, json, math

ROOT = Path(__file__).resolve().parents[1]
H = Decimal('6.62607015e-34')  # exact SI h
C = Decimal('299792458')       # exact SI c
K_B = Decimal('1.380649e-23') # exact SI k_B
T_GRID = (Decimal('50'), Decimal('100'), Decimal('200'))
PINNED_A = ('5.442E-08','5.159E-07','1.828E-06','4.365E-06','8.405E-06','1.410E-05','2.150E-05','3.051E-05')
PINNED_NU_P = (2674986094000,5331561951400,7951728180800,10518307081200,13015353487100,15428565614100,17745695903500,19956961867900)
PINNED_NU_E = ('13374930469958794919/5000000','1332890250930289919/250000','19879323162796857291/2500000','52591535167862954543/5000000','13015354732561910729/1000000','38571409466318598107/2500000','22182121643381812819/1250000','49892404686912474057/2500000')
EXPECTED_SOURCE_BLOB = '5a99c9e31604347cf756abb4ab3ea1a134238e0d'
EXPECTED_LAMDA_SHA256 = '0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
EXPECTED_LAB = ((2,0,'8006533168','26','10.1140/epjd/s10053-022-00552-x'),(3,1,'13283245098','30','10.1103/PhysRevA.105.062823'))


def read_verified_inputs(root=ROOT):
    lab_bytes=(root/'data/LAB_ANCHORS.json').read_bytes()
    src_bytes=(root/'data/PR156_SOURCE_TRANSCRIPTION.json').read_bytes()
    lab=json.loads(lab_bytes)
    src=json.loads(src_bytes)
    if src['git_blob'] != EXPECTED_SOURCE_BLOB or src['underlying_lamda_source_sha256']!=EXPECTED_LAMDA_SHA256 or src['underlying_lamda_source_bytes'] != 2289:
        raise ValueError('source identity metadata mismatch')
    rows=src['rows']
    if len(rows)!=8 or tuple(x['J_upper'] for x in rows)!=tuple(range(1,9)):
        raise ValueError('eight one-step radiative lines in frozen order required')
    if tuple(x['nu_P_Hz'] for x in rows)!=tuple(f'{x}/1' for x in PINNED_NU_P) or tuple(x['A_s_inv'] for x in rows)!=PINNED_A or tuple(x['nu_E_Hz'] for x in rows)!=PINNED_NU_E:
        raise ValueError('source photon or A literal differs from pinned PR156 transcription')
    levels=[]
    for x in rows:
        nu_e=Fraction(x['nu_E_Hz'])
        nu_p=Fraction(x['nu_P_Hz'])
        if nu_e<=0 or nu_p<=0 or Decimal(x['A_s_inv'])<=0:
            raise ValueError('nonpositive frequency or Einstein A')
        levels.append((nu_e,nu_p,Decimal(x['A_s_inv'])))
    if len(lab['measurements'])!=2:
        raise ValueError('two primary combination differences required')
    for i,x in enumerate(lab['measurements']):
        j,k,center,unc,doi=EXPECTED_LAB[i]
        if (x['upper_J'],x['lower_J'],x['nominal_kHz'],x['reported_uncertainty_kHz'],x['source_DOI']) != (j,k,center,unc,doi):
            raise ValueError('experimental value, uncertainty, quantum label or primary source changed')
    if tuple((x['upper_J'],x['lower_J']) for x in lab['measurements']) != ((2,0),(3,1)):
        raise ValueError('incorrect lab transition labels')
    return levels,lab,src,{'lab_sha256':hashlib.sha256(lab_bytes).hexdigest(),'transcription_sha256':hashlib.sha256(src_bytes).hexdigest()}


def exact_reconciliation(root=ROOT):
    src,lab,transcription,hashes=read_verified_inputs(root)
    def f(j): return src[j-1][1]
    def e(j): return src[j-1][0]
    y=Fraction(int(lab['measurements'][0]['nominal_kHz'])*1000)
    z=Fraction(int(lab['measurements'][1]['nominal_kHz'])*1000)
    sy=int(lab['measurements'][0]['reported_uncertainty_kHz'])*1000
    sz=int(lab['measurements'][1]['reported_uncertainty_kHz'])*1000
    # Each combination prediction uses precisely its two consecutive radiative transitions.
    combinations=[(2,0,y,sy,f(1)+f(2),e(1)+e(2)),(3,1,z,sz,f(2)+f(3),e(2)+e(3))]
    results=[]
    for ju,jl,meas,meas_std,pred,term in combinations:
        results.append({
            'upper_J':ju,'lower_J':jl,'v':0,
            'experiment_Hz':str(meas.numerator),'reported_uncertainty_Hz':meas_std,
            'source_photon_combo_Hz':str(pred.numerator),
            'source_level_energy_combo_Hz':str(Decimal(term.numerator)/Decimal(term.denominator)),
            'experiment_minus_source_photon_combo_Hz':str((meas-pred).numerator),
            'experiment_minus_source_level_combo_Hz':str(Decimal(meas.numerator)/Decimal(meas.denominator)-Decimal(term.numerator)/Decimal(term.denominator)),
            'source_internal_energy_minus_photon_combo_Hz':str(Decimal((term-pred).numerator)/Decimal((term-pred).denominator)),
            'experiment_source_difference_kind':'LAB_2022_MINUS_SOURCE_2011V2_BASED_2021_TRANSCRIPTION_NOT_MODEL_ERROR_SIGNIFICANCE',
            'published_sigma_is_not_total_model_uncertainty':True
        })
    # Rank two; the 2x3 measurement matrix has kernel (1,-1,1).
    x=f(1)
    candidates=(x,y-x,z-y+x)
    assert candidates[0]+candidates[1]==y and candidates[1]+candidates[2]==z
    assert sum(abs(e(j)-f(j))>35 for j in range(1,9))==7
    # No experimental Doppler/gas dynamics, line profile, density or source fit inserted.
    return {
        'schema':'REC_HD_LAB_COMBINATION_PHYSICAL_DATA_V1',
        'sources':{'experiment':'PRIMARY_2022_TWO_COMBINATION_MEASUREMENTS','original_LAMDA':'NOT_REACQUIRED','CDMS_2011_V2_RAW':'NOT_ACQUIRED','prior_source_result_blob':EXPECTED_SOURCE_BLOB,**hashes},
        'measured_combinations':results,
        'rank':2,'null_vector_of_two_by_three_line_incidence':[1,-1,1],
        'conditionally_anchored_individual_lines_Hz':{'anchor_J1_0_from_pinned_2011_source_nominal':str(x.numerator),'derived_J2_1':str(candidates[1].numerator),'derived_J3_2':str(candidates[2].numerator)},
        'individual_line_candidates_are_conditional_on_2011_1_0_nominal':True,
        'experimental_uncertainty_covariance_and_2011_anchor_uncertainty':'NOT_ACQUIRED',
        'original_35Hz_gate':{'failed':7,'total':8,'status':'FAIL_UNCHANGED'},
        'physical_source_choice':'HOLD', 'production':'HOLD',
        'canonical_DAG':'28/88 (+0)', 'REC_physical_DAG':'0/313 (+0)'
    }


def photon_power_and_thermo(root=ROOT):
    src,lab,_,hashes=read_verified_inputs(root)
    rows=[]
    with localcontext() as ctx:
        ctx.prec=80
        for j,(_,nu,A) in enumerate(src,1):
            f=Decimal(nu.numerator)/Decimal(nu.denominator)
            energy=H*f
            o={'upper_J':j,'lower_J':j-1,'A_s_inv':str(A),'printed_photon_frequency_Hz':str(f),
               'photon_energy_J':str(energy),'wavelength_m':str(C/f),'spontaneous_lifetime_s':str(1/A),
               'photon_power_per_one_excited_molecule_W':str(A*energy),'E_photon_over_k_K':str(energy/K_B)}
            for T in T_GRID:
                x=energy/(K_B*T)
                o['blackbody_occupation_at_'+str(T)+'K']=str(Decimal(1)/(x.exp()-1))
            rows.append(o)
        y=Decimal(lab['measurements'][0]['nominal_kHz'])*1000
        z=Decimal(lab['measurements'][1]['nominal_kHz'])*1000
        experimental_thermo=[]
        for temp in T_GRID:
            experimental_thermo.append({'T_K':str(temp),
              'LTE_nJ2_over_nJ0_from_measured_E2-E0':str(Decimal(5)*(-H*y/(K_B*temp)).exp()),
              'LTE_nJ3_over_nJ1_from_measured_E3-E1':str((Decimal(7)/Decimal(3))*(-H*z/(K_B*temp)).exp()),
              'interpretation':'CONDITIONAL_LTE_POPULATION_RATIO_FROM_REAL_LAB_ENERGY_NOT_MEASURED_COSMIC_POPULATION'})
    return {'schema':'REC_HD_SOURCE_2021_PHOTON_AND_REAL_2022_LTE_OBSERVABLES_V1','original_raw_missing':True,
            'radiative_lines':rows,'measured_based_LTE_ratios':experimental_thermo,
            'A_uncertainty':None,'energy_frequencies':'PRINTED_PHOTON_CONSUMER_ONLY',
            'source_identity':hashes,'production':'HOLD'}


def write_outputs(root=ROOT):
    rows=exact_reconciliation(root)
    phys=photon_power_and_thermo(root)
    evidence=root/'evidence';evidence.mkdir(parents=True,exist_ok=True)
    (evidence/'MEASUREMENT_RECONCILIATION.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    (evidence/'PHOTON_PHYSICAL_TABLE.json').write_text(json.dumps(phys,indent=2,ensure_ascii=False)+'\n')
    with (evidence/'PHOTON_PHYSICAL_TABLE.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(phys['radiative_lines'][0]));writer.writeheader();writer.writerows(phys['radiative_lines'])
    return rows,phys

if __name__=='__main__':
    out,phy=write_outputs()
    print('experimental minus frozen source combination Hz', [(x['upper_J'],x['experiment_minus_source_photon_combo_Hz']) for x in out['measured_combinations']]);print('original 35Hz gate',out['original_35Hz_gate']);print('radiative lines',len(phy['radiative_lines']),'LTE temperatures',len(phy['measured_based_LTE_ratios']))
