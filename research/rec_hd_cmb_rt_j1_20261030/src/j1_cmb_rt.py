"""Source-pinned 2021 HD J=1->0 35Hz-gated thermal Gaussian CMB line transfer.

This is a stationary, conditional narrow-line single-pass slab and not a
self-consistent cosmological radiation-transport or 9-level production model.
Transcribed source inputs are pinned, not authenticated original laboratory bytes.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

# Single pinned copy of the previously validated PR167 numerical implementation.
from hd_cmb_balance import load_sources, twolevel, frequency_ledger, nu_gap, C, H, KB, T0

U_KG = 1.66053906660e-27  # unified atomic mass unit, CODATA 2018 derived (kg)
PI = math.pi
GRID_N = 321
GRID_LIMIT = 7.0
T_GRID = (50,100,200)
Z_GRID = (0,10,30,50)
DENSITIES = ('1','100','10000','1000000')
ORTHO = ('0','0.5','1')
COLUMNS_CM2 = ('1e14','1e16','1e18')
PHYSICAL_DAG = '0/313'
CANONICAL_DAG = '28/88'


def require(condition, message):
    if not condition: raise ValueError(message)


def load_pinned(directory):
    p=Path(directory)
    src,sung=load_sources(p/'LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json',p/'SUNG_HD_PR164_SOURCE.json')
    freq=frequency_ledger(src)
    require(freq[0]['frozen_35Hz_gate']=='PASS' and all(t['frozen_35Hz_gate']=='FAIL' for t in freq[1:]), '35Hz gate changed')
    require(src['molecular_weight_u']=='3.0','HD source molecular weight changed')
    require(src['radiative_lines'][0]['upper_J']==1 and src['radiative_lines'][0]['lower_J']==0,'J1 edge changed')
    require(src['radiative_lines'][0]['A_s1']=='5.442E-08','J1 A changed')
    require(sung['primary_source']['joint_covariance'] is None, 'Unacknowledged covariance')
    return src,sung


def line_state(src,Tgas:int,z:int,nH2:str,ortho:str):
    require(type(Tgas) is int and Tgas in T_GRID,'Not an original LAMDA temperature node')
    require(type(z) is int and z>=0, 'z must be nonnegative integer')
    require(float(nH2)>0,'Positive collider density required')
    require(0 <= float(ortho) <= 1,'Invalid H2 spin fraction')
    Tbg=float(T0)*(1+z)
    two=twolevel(src,Tgas,nH2,ortho,Tbg)
    p0,p1=float(two['p0']),float(two['p1'])
    g=3.0
    require(0<p1<1 and 0<p0<1 and (g*p0-p1)>0,'Population or inversion failure')
    c,h,k = float(C),float(H),float(KB)
    nu=float(nu_gap(src,1,0))
    A=float(src['radiative_lines'][0]['A_s1'])
    b_ms=math.sqrt(2*k*Tgas/(float(src['molecular_weight_u'])*U_KG))
    delta_nu=nu*b_ms/c
    nbar=1.0/math.expm1(h*nu/(k*Tbg))
    P=2*h*nu**3/c**2
    B=P*nbar
    S=P*p1/(g*p0-p1)
    net=float(two['net'])
    exact_emission=h*nu*A*(p1*(1+nbar)-g*p0*nbar)
    require(math.isclose(net,exact_emission,rel_tol=8e-12,abs_tol=2e-44), 'Net power did not match PR167 source')
    # 1cm^-2=1e4m^-2; Gaussian width is e-folding velocity, not 1-sigma.
    sigma_int=A*c*c/(8*PI*nu*nu)*(g*p0-p1)
    return dict(Tgas_K=Tgas,z=z,Tcmb_K=Tbg,nH2_cm3=nH2,ortho_fraction=ortho,
                p0=p0,p1=p1,nu0_Hz=nu,lambda0_m=c/nu,nu_obs_Hz=nu/(1+z),
                b_thermal_ms=b_ms,dnu_D_Hz=delta_nu,A_s1=A,nbar=nbar,
                B_rest=B,S_rest=S,ex_K=h*nu/(k*math.log(g*p0/p1)),
                sigma_int_m2_Hz=sigma_int,net_W_HD=net,source_gate='J1_PASS_35Hz',
                actual_source='LAMDA_2021_TRANSCRIPTION_PR161',
                model='FROZEN_SE_CMB_THIN_SLAB')


def gaussian_curve_growth_factor(tau0):
    """Exact convergent series of normalized ∫(1-exp(-tau0 exp(-x²)))dx.

    Value = 1 -tau0/(2 sqrt(2))+tau0²/(6 sqrt(3))-... for tau0 < 0.1.
    """
    require(0<=tau0<.1,'Thin slab criterion violated')
    s=0.0
    for k in range(1,14):
        s += (-1)**(k+1)*tau0**(k-1)/(math.factorial(k)*math.sqrt(k))
    return s


def spectrum(st,N_cm2,grid_n=GRID_N):
    require(grid_n>=161 and grid_n%2==1,'Spectrum sampling is odd >=161')
    N=float(N_cm2)*1e4
    require(N>0 and np.isfinite(N),'Invalid HD column')
    x=np.linspace(-GRID_LIMIT,GRID_LIMIT,grid_n,dtype=float)
    dnu=st['dnu_D_Hz']
    tau0=N*st['sigma_int_m2_Hz']/(math.sqrt(PI)*dnu)
    require(tau0<0.1,'Optical depth invalidates external-bath thin-slab assumption')
    tau=tau0*np.exp(-x*x)
    contrast_rest=(st['S_rest']-st['B_rest'])*(-np.expm1(-tau))
    contrast_obs=contrast_rest/(1+st['z'])**3
    freq_obs=(st['nu0_Hz']+x*dnu)/(1+st['z'])
    cmb_bg_obs=st['B_rest']/(1+st['z'])**3
    rest_I_int=float(np.trapezoid(contrast_rest,x*dnu))
    obs_I_int=float(np.trapezoid(contrast_obs,freq_obs))
    thin_exact=N*st['net_W_HD']/(4*PI)
    series_ratio=gaussian_curve_growth_factor(tau0)
    area_exact_theory=thin_exact*series_ratio
    require(math.isclose(rest_I_int,area_exact_theory,rel_tol=3e-10,abs_tol=3e-35), 'Gaussian integrated luminosity check')
    require(math.isclose(obs_I_int,rest_I_int/(1+st['z'])**4,rel_tol=5e-9,abs_tol=3e-35), 'Cosmological specific-intensity scaling')
    require(np.all(np.isfinite(contrast_obs)), 'nonfinite brightness')
    require(np.all(tau>=0),'negative tau')
    if st['net_W_HD'] != 0:
        require(math.copysign(1,rest_I_int)==math.copysign(1,st['net_W_HD']), 'net power/sky contrast sign mismatch')
    deltaI0=float(contrast_obs[grid_n//2]); nuobs=st['nu_obs_Hz']
    dTrj0=(float(C)**2/(2*float(KB)*nuobs**2))*deltaI0
    case={k:v for k,v in st.items() if k not in ('B_rest','S_rest','sigma_int_m2_Hz')}
    case.update(N_HD_cm_minus2=str(N_cm2),tau0=tau0,delta_T_RJ0_observed_K=dTrj0,
                center_deltaI_obs_W_m2_Hz_sr=deltaI0,
                net_integrated_contrast_rest_W_m2_sr=rest_I_int,
                net_integrated_contrast_observed_W_m2_sr=obs_I_int,
                thin_integral_rest_W_m2_sr=thin_exact,
                gaussian_saturation_factor=series_ratio,
                theoretical_integral_rest_W_m2_sr=area_exact_theory,
                redshift_energy_dimming='(1+z)^-4',
                optical_depth_admitted=tau0<0.1,
                measured_sky=False,source_covariance=None)
    return case, x, freq_obs, tau, contrast_obs


def build(src,output_dir:Path,grid_n=GRID_N):
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    cases=[]; spectra=[]
    for T in T_GRID:
        for z in Z_GRID:
            for den in DENSITIES:
                for f in ORTHO:
                    st=line_state(src,T,z,den,f)
                    for N in COLUMNS_CM2:
                        case,x,freq,tau,obs=spectrum(st,N,grid_n)
                        case['case_id']=f'J1_{T}_{z}_{den}_{f}_{N}'
                        cases.append(case)
                        for i in range(grid_n):
                            spectra.append(dict(case_id=case['case_id'],sample_i=i,x_doppler=float(x[i]),
                                  observed_frequency_GHz=float(freq[i])/1e9,tau=float(tau[i]),
                                  delta_I_observed_W_m_minus2_Hz_minus1_sr_minus1=float(obs[i]),
                                  source_gate='J1_PASS_35Hz',not_observed=True))
    require(len(cases)==432 and len(spectra)==432*grid_n,'wrong scientific atlas cardinality')
    def dump_csv(path,rows):
        with Path(path).open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    dump_csv(output_dir/'J1_CMB_RT_432_PHYSICAL_CASES.csv',cases)
    dump_csv(output_dir/'J1_CMB_RT_138672_SPECTRAL_SAMPLES.csv',spectra)
    summary=dict(schema='REC_HD_CMB_J1_CONDITIONAL_TRANSFER_V1',source_admission='PR161 LAMDA 2021 rendered-text transcription; raw original not acquired',
         n_cases=len(cases),n_spectral_samples=len(spectra), source_j1_gate='PASS',source_full9_gate='FAIL7/8',
         min_peak_tau=min(r['tau0'] for r in cases),max_peak_tau=max(r['tau0'] for r in cases),
         min_saturation_factor=min(r['gaussian_saturation_factor'] for r in cases),
         max_gaussian_area_relerror=max(abs(r['net_integrated_contrast_rest_W_m2_sr']-r['theoretical_integral_rest_W_m2_sr'])/max(abs(r['theoretical_integral_rest_W_m2_sr']),1e-50) for r in cases),
         T_grid=list(T_GRID),z_grid=list(Z_GRID),nH2_grid=list(DENSITIES),f_ortho_grid=list(ORTHO),N_HD_grid=list(COLUMNS_CM2),
         exact_population_model='PR167 TWO_LEVEL WITH CMB',line_profile='THERMAL_GAUSSIAN_ONLY, HD mass 3u, no pressure broadening',
         no_reconstructed_cdm_covariance=True, measured_external_sky=False, physical_model_claim='source-pinned J1 only, external radiation bath frozen',
         independent_2026_dataset='NEUFELD_V2_BINARY_NOT_ACQUIRED',canonical_DAG=CANONICAL_DAG,rec_physical_DAG=PHYSICAL_DAG,
         auto_next_node=False,production='HOLD')
    for k in ['50','100','200']:
        for z in [0,30,50]:
            match=next(v for v in cases if v['Tgas_K']==int(k) and v['z']==z and v['nH2_cm3']=='10000' and v['ortho_fraction']=='0.5' and v['N_HD_cm_minus2']=='1e18')
            summary[f'sample_T{k}_z{z}']={t:match[t] for t in ['nu_obs_Hz','tau0','delta_T_RJ0_observed_K','net_integrated_contrast_observed_W_m2_sr','gaussian_saturation_factor']}
    (output_dir/'RESULTS.json').write_text(json.dumps(summary,sort_keys=True,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--input',default=str(Path(__file__).resolve().parents[1]/'input'))
    a.add_argument('--out',default=str(Path(__file__).resolve().parents[1]/'results'))
    v=a.parse_args();src,_=load_pinned(v.input);print(json.dumps(build(src,Path(v.out)),indent=2))
