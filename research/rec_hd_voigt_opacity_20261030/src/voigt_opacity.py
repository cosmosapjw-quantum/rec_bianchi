"""HD measured-source conditional absorption line-profile atlas.

Science boundary: 296 K, H2-only pressure, Gaussian Maxwell Doppler + Lorentz
pressure broadening (Voigt). This is NOT Sung's experimentally fitted Rautian
profile. S is HITRAN-natural-abundance weighted per reference molecule; the
column is N_ref in the SAME convention, not an independently inferred HD column.
"""
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import voigt_profile

C_MS = 299792458.0  # SI defined constant
KB_JK = 1.380649e-23  # SI defined constant
U_KG = 1.66053906660e-27  # CODATA 2018 rounded atomic-mass constant
HD_MASS_U_APPROX = 3.021927 # pure isotopologue, source-reported nominal, no mass-uncertainty claim
M_HD_KG = U_KG * HD_MASS_U_APPROX
TEMP_K = 296.0
H2_ATM = (0.01,0.1,0.5)
N_REFERENCE_CM2 = (1e22,1e23,1e24)


def input_data(path:Path) -> dict:
    d=json.loads(Path(path).read_text())
    if d.get('schema')!='REC_HD_SUNG_2022_MULTISPECTRAL_LAB_MEASURED_V1': raise ValueError('source schema')
    if d['primary_source']['doi']!='10.1016/j.jqsrt.2022.108412': raise ValueError('source DOI')
    if d['temperature_K']!='296' or len(d['line_parameters'])!=4: raise ValueError('source domain')
    # Physics must remain source/nominal, no silent A or S conversion
    hard=[(1,'89.22792','5.561E-28','0.0120','0.00017'),
          (2,'177.84141','2.402E-27','0.0114','0.00141'),
          (3,'265.24055','2.886E-27','0.0104','0.00106'),
          (4,'350.85401','1.522E-27','0.0097','-0.00108')]
    for row, (j,nu,S,gamma,delta) in zip(d['line_parameters'],hard):
        if (row['upper_J'],row['nu0_cm_minus1'],row['S_296_cm_per_molecule'],
                row['H2_gamma0_cm_minus1_per_atm'],row['H2_delta0_cm_minus1_per_atm']) != (j,nu,S,gamma,delta):
            raise ValueError('source measured literal mismatch')
    return d


def sigma_doppler(nu_cm1:float, T:float=TEMP_K, m_kg:float=M_HD_KG) -> float:
    if not (nu_cm1>0 and T>0 and m_kg>0):raise ValueError('positive nu/T/m required')
    return nu_cm1*math.sqrt(KB_JK*T/(m_kg*C_MS*C_MS))


def source_params(row:dict,p_atm:float) -> dict:
    if p_atm<=0:raise ValueError('positive H2 pressure required')
    nu=float(row['nu0_cm_minus1']); s=float(row['S_296_cm_per_molecule'])
    gamma=float(row['H2_gamma0_cm_minus1_per_atm'])*p_atm
    delta=float(row['H2_delta0_cm_minus1_per_atm'])*p_atm
    return {'j':row['upper_J'],'nu0_cm1':nu,'S_cm_per_molecule':s,
            'p_atm':p_atm,'center_cm1':nu+delta,'shift_cm1':delta,
            'gamma_cm1':gamma,'sigma_d_cm1':sigma_doppler(nu),
            'gaussian_fwhm_cm1':2*math.sqrt(2*math.log(2))*sigma_doppler(nu),
            'lorentz_fwhm_cm1':2*gamma}


def phi(offset_cm1, sigma_cm1, gamma_cm1):
    """Normalized Voigt in wavenumber: unit cm, integral d(cm^-1)=1."""
    if not (sigma_cm1>0 and gamma_cm1>=0):raise ValueError('width domain')
    return voigt_profile(offset_cm1,sigma_cm1,gamma_cm1)


def equivalent_width(params:dict,N_ref_cm2:float):
    if N_ref_cm2<=0:raise ValueError('positive column')
    s=params['S_cm_per_molecule'];sig=params['sigma_d_cm1'];g=params['gamma_cm1']
    peak_tau=N_ref_cm2*s*float(phi(0,sig,g))
    span=100*max(sig,g)
    # Integrate separately over sides to sample narrow line core and wide wings.
    def width_integrand(x):
        tau=N_ref_cm2*s*float(phi(x,sig,g))
        return -math.expm1(-tau)
    p_kwargs={'epsabs':5e-13,'epsrel':1e-10,'limit':200}
    W=2*quad(width_integrand,0,span,**p_kwargs)[0]
    area=2*quad(lambda x:float(phi(x,sig,g)),0,span,**p_kwargs)[0]
    # A mathematically valid upper bound for the full equivalent width under exact numerical integration:
    # missing W_tail<=N_ref S (1-area), up to quadrature error, never statistical bound.
    upper=W+N_ref_cm2*s*max(0.0,1-area)
    return {'peak_tau':peak_tau,'transmission_at_center':math.exp(-peak_tau),
            'window_halfwidth_cm1':span,'profile_captured_area':area,
            'equivalent_width_window_cm1':W,'equivalent_width_upper_cm1':upper,
            'integrated_tau_exact_cm1':N_ref_cm2*s}


def atlas(input_path:Path, out:Path):
    d=input_data(input_path);out.mkdir(exist_ok=True,parents=True)
    cases,profile_rows=[],[]
    for row in d['line_parameters']:
        for p in H2_ATM:
            pars=source_params(row,p)
            window=max(15*pars['gamma_cm1'],25*pars['sigma_d_cm1'])
            # all molecular/atomic constants and source units are fixed, no implied collider environment
            xpts=np.linspace(-window,window,201)
            q=phi(xpts,pars['sigma_d_cm1'],pars['gamma_cm1'])
            for N in N_REFERENCE_CM2:
                e=equivalent_width(pars,N)
                case={**pars,'T_K':TEMP_K,'N_ref_cm_minus2':N,**e,
                      'profile_assumption':'VOIGT_APPROX_NOT_EXPERIMENTAL_RAUTIAN',
                      'HITRAN_abundance_reference':'S_AND_NREF_SAME_NATURAL_ABUNDANCE_CONVENTION',
                      'not_a_new_observation':True}
                cases.append(case)
                tau=N*pars['S_cm_per_molecule']*q
                for x,v,t in zip(xpts,q,tau):
                    profile_rows.append({'J_upper':pars['j'],'p_H2_atm':p,'N_ref_cm_minus2':N,
                        'T_K':TEMP_K,'wavenumber_cm_minus1':pars['center_cm1']+float(x),
                        'offset_cm_minus1':float(x),'phi_cm':float(v),
                        'tau':float(t),'transmission':float(np.exp(-t))})
    def csv_save(path, rows):
        with open(path,'w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    csv_save(out/'SPECTRAL_CASES_36.csv',cases)
    csv_save(out/'VOIGT_PROFILE_ATLAS_7236.csv',profile_rows)
    result={'schema':'REC_HD_VOIGT_296K_CONDITIONAL_ATLAS_V1',
            'input_path':'data/LAB_INPUT_PARENT_PR164.json','T_K':TEMP_K,'p_H2_atm':list(H2_ATM),
            'Nref_cm_minus2':list(N_REFERENCE_CM2),'case_count':len(cases),
            'profile_count':len(profile_rows),'source_S_convention':'HITRAN_ABUNDANCE_WEIGHTED_REFERENCE_MOLECULE',
            'source_primary_doi':d['primary_source']['doi'],
            'assumptions':['Maxwell-Doppler 296 K','single H2 pressure broadening','Voigt profile, not Rautian',
                           'pure absorption slab without emission, scattering, stimulated source function or instrument convolution',
                           'Nref and S use same HITRAN natural abundance convention'],
            'uncertainty_status':{'joint_covariance':None,'model_systematic':None,'statistical_significance':None},
            'science_status':'CONDITIONAL_SOURCE_BOUND_OPACITY_NOT_OBSERVED_SPECTRUM',
            'protection':d['protection'],
            'example':{'J_upper':cases[0]['j'],'p_atm':cases[0]['p_atm'],'N_ref_cm_minus2':cases[0]['N_ref_cm_minus2'],
                       'peak_tau':cases[0]['peak_tau'],'equivalent_width_window_cm1':cases[0]['equivalent_width_window_cm1']}}
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default=str(Path(__file__).resolve().parents[1]/'data'/'LAB_INPUT_PARENT_PR164.json'))
    ap.add_argument('--out',default=str(Path(__file__).resolve().parents[1]/'evidence'))
    args=ap.parse_args()
    print(json.dumps(atlas(Path(args.input),Path(args.out)),indent=2))
