"""Source-authentic 15-level HD non-LTE, CMB-background line transfer atlas.

All 14 rotational lines: formal transfer through a homogeneous slab with fixed
optically-thin-source statistical equilibrium populations. Finite-tau values are
transfer diagnostics, NOT self-consistent trapped-radiation predictions.
No observations, fitted likelihood, or CDMS-2011 owner/source switch.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np
from numpy.polynomial.hermite import hermgauss
from pr169_neufeld15_reference import C,H,K_B,parse_lamda
from hd_cmb15 import solve_cmb,planck_number

SOURCE_SHA={
 'hd_lamda.dat':'f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb',
 'hd_lamda_altex.dat':'66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac',
 'hd_population_grids.fits':'0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1',
 'hd_population_grids_altex.fits':'1fc3588b32e1423a5c56c68df43ee0385f38f62424615971857b403bf02d45de',
}
TEMPS=(100.,400.,1000.,4000.) # exact input-table temperatures
DENSITIES_CM3=(1e2,1e4,1e6,1e8)
REDSHIFTS=(0.,10.,30.,50.,100.)
MICROTURB_KMS=(0.,3.) # prescribed Doppler b parameter, not measured velocity
COLUMNS_CM2=(1e14,1e16,1e18,1e20)
AMU_KG=1.66053906660e-27
HD_MASS_KG=3.0*AMU_KG # original LAMDA source header 3.0 amu (approx mass)
TCMB0=2.72548
SQRT_PI=math.sqrt(math.pi)
_HERM_X,_HERM_W=hermgauss(96)


def check_sources(root):
    for name,expected in SOURCE_SHA.items():
        path=Path(root)/'source/zenodo_v2'/name
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected:raise ValueError(f'SOURCE_BYTE_GATE_FAILED {name}: {actual}')


def doppler_width_Hz(nu_hz,T_K,vturb_kms):
    if not (nu_hz>0 and T_K>0 and vturb_kms>=0):raise ValueError('nonphysical Doppler inputs')
    b_ms=math.hypot(math.sqrt(2*K_B*T_K/HD_MASS_KG),vturb_kms*1000.)
    return nu_hz*b_ms/C, b_ms


def beta_gauss(tau):
    """Exact frequency-integrated formal-slab / thin intensity ratio.

    Gaussian line profile and constant populations, 96-node Gauss-Hermite.
    Negative tau is allowed for weak, unsaturated population inversion.
    """
    if not math.isfinite(tau) or tau < -60:raise ValueError('invalid tau or unmodelled large maser gain')
    if tau==0:return 1.
    y=tau*np.exp(-_HERM_X**2)
    f=np.ones_like(y)
    m=np.abs(y)>1.e-12
    f[m]=-np.expm1(-y[m])/y[m]
    f[~m]=1.-0.5*y[~m]+y[~m]**2/6.
    return float(np.dot(_HERM_W,f)/SQRT_PI)


def tau_zero_and_source(pop,model,radiative_row,Tgas_K,vturb_kms,z):
    up,low,A,nu=radiative_row
    gu=model.levels[up][2];gl=model.levels[low][2]
    fu=float(pop[up]);fl=float(pop[low]); balance=(gu/gl)*fl-fu
    delta_nu,b=doppler_width_Hz(nu,Tgas_K,vturb_kms)
    phi0=1./(SQRT_PI*delta_nu)
    tau0_per_cm2=1.e4*(C*C/(8.*math.pi*nu*nu))*A*balance*phi0
    nbar=planck_number(nu,TCMB0*(1+z))
    net_W_per_HD=H*nu*A*(fu*(1+nbar)-(gu/gl)*fl*nbar)
    thin_intensity_per_cm2=1.e4*net_W_per_HD/(4*math.pi) # W m^-2 sr^-1 / (cm^-2)
    I_bg=2.*H*nu**3/(C*C)*nbar
    S=2.*H*nu**3/(C*C)*fu/balance if balance!=0 else None
    return {'tau0_per_Ncm2':tau0_per_cm2,'net_W_per_HD':net_W_per_HD,
            'thin_excess_intensity_per_Ncm2':thin_intensity_per_cm2,
            'source_function_W_m2_sr_Hz':S,'I_CMB_W_m2_sr_Hz':I_bg,
            'Doppler_width_Hz':delta_nu,'b_Doppler_km_s':b/1000.,
            'population_balance':balance,'wavelength_rest_um':C/nu*1e6}


def read_models(root):
    check_sources(root)
    base=Path(root)/'source/zenodo_v2'
    std=parse_lamda((base/'hd_lamda.dat').read_bytes(),verify=True)
    alt=parse_lamda((base/'hd_lamda_altex.dat').read_bytes())
    if len(std.levels)!=15 or len(std.rad)!=14 or len(alt.rad)!=14:raise ValueError('model levels/lines mismatch')
    if [r[3] for r in std.rad]!=[r[3] for r in alt.rad]:raise ValueError('source switched radiative frequencies')
    return {'std':std,'alternate':alt}


def make_rows(root):
    models=read_models(root)
    states=[];rows=[]
    for model_name,model in models.items():
      for T in TEMPS:
       for n in DENSITIES_CM3:
        for z in REDSHIFTS:
         state=solve_cmb(model,T,n,z)
         p=state['populations_J0_to_J14']
         if min(p)<0 or abs(sum(p)-1)>1e-11:raise ArithmeticError('stationary population invalid')
         states.append({'source':model_name,'Tgas_K':T,'nH2_cm3':n,'z':z,
                        'T_CMB_K':state['Tbg_K'],'net_cooling_W_per_HD':state['net_cooling_W_per_HD'],
                        'max_stationarity_residual_s_inverse':state['max_stationary_residual_s_inverse'],
                        'min_population':min(p)})
         power={int(x['J_upper']):x['net_W_per_HD'] for x in state['line_power_records']}
         for item in model.rad:
          u,l,A,nu=item
          if not (model.levels[u][0]==model.levels[l][0]+1):raise ValueError('non-adjacent radiative line')
          J=int(model.levels[u][0]);R=f'R({J-1})'
          for vturb in MICROTURB_KMS:
           pcoeff=tau_zero_and_source(p,model,item,T,vturb,z)
           expected_power=power[J]
           # Separate equivalent arithmetic groupings can cancel nearly equal
           # spontaneous/stimulated/absorptive terms; bound roundoff against
           # the sum of physical *term* magnitudes, not against tiny net power.
           raw_line=next(x for x in state['line_power_records'] if int(x['J_upper'])==J)
           term_scale=sum(abs(raw_line[k]) for k in
                          ('spontaneous_W_per_HD','stimulated_W_per_HD','absorbed_W_per_HD'))
           if abs(pcoeff['net_W_per_HD']-expected_power)>5e-15*term_scale:
               raise ArithmeticError('CMB radiation ledger mismatch')
           tau_unit=pcoeff['tau0_per_Ncm2']
           # Negative tau is preserved as weak, small-signal population inversion.
           for col in COLUMNS_CM2:
            tau0=tau_unit*col
            beta=beta_gauss(tau0)
            thin=col*pcoeff['thin_excess_intensity_per_Ncm2']
            formal=thin*beta
            # Tolman (1+z)^-4 intensity mapping is conditional on FLRW redshift.
            d={'source':model_name,'Tgas_K':T,'nH2_cm3':n,'z':z,'T_CMB_K':state['Tbg_K'],
              'upper_J':J,'line_name':R,'frequency_Hz':nu,'wavelength_rest_um':pcoeff['wavelength_rest_um'],
              'A_s_inverse':A,'microturb_km_s':vturb,'b_Doppler_km_s':pcoeff['b_Doppler_km_s'],
              'N_HD_cm2':col,'tau0':tau0,'N_HD_abs_tau0_0p1_cm2':.1/abs(tau_unit) if tau_unit!=0 else None,
              'I_CMB_W_m2_sr_Hz':pcoeff['I_CMB_W_m2_sr_Hz'],
              'net_radiative_power_W_per_HD':pcoeff['net_W_per_HD'],
              'I_excess_thin_rest_W_m2_sr':thin,'formal_slab_beta':beta,
              'I_excess_formal_rest_W_m2_sr':formal,
              'I_excess_formal_observer_FLRW_W_m2_sr':formal/(1.+z)**4,
              'sign_class':('emission' if formal>0 else 'absorption' if formal<0 else 'zero'),
              'population_inverted':tau0<0,
              'fixed_populations_validity':('thin_abs_tau_lt_0p1' if abs(tau0)<.1 else
                 'formal_only_saturation_unmodelled' if tau0<0 else 'formal_only_trapping_unmodelled')}
            rows.append(d)
    return states,rows


def save(root):
    states,rows=make_rows(root)
    out=Path(root)/'evidence';out.mkdir(parents=True,exist_ok=True)
    def csvwrite(name,rs):
      with (out/name).open('w',encoding='utf8',newline='') as f:
       writer=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');writer.writeheader();writer.writerows(rs)
    csvwrite('FULLLINE_15LEVEL_STATES.csv',states)
    csvwrite('FULLLINE_SLAB_TRANSFER_ATLAS.csv',rows)
    tau=np.array([r['tau0'] for r in rows]);signs={k:sum(r['sign_class']==k for r in rows) for k in ('emission','absorption','zero')}
    perJ=[]
    for j in range(1,15):
      rs=[r for r in rows if r['upper_J']==j]
      perJ.append({'upper_J':j,'line':f'R({j-1})','mean_tau0':float(np.mean([r['tau0'] for r in rs])),
                   'max_tau0':float(max(r['tau0'] for r in rs)),
                   'thin_count_abs_tau_lt_0p1':sum(abs(r['tau0'])<.1 for r in rs),
                   'absorption_count':sum(r['sign_class']=='absorption' for r in rs),
                   'wavelength_rest_um':rs[0]['wavelength_rest_um']})
    csvwrite('FULLLINE_PER_TRANSITION_SUMMARY.csv',perJ)
    summary={'unit':'REC_HD_NEUFELD2026_CMB15_FULLLINE_TRANSFER_20261030',
     'science_class':'SOURCE_LOCKED_NONLTE_PHYSICAL_MODEL_NOT_OBSERVED_SKY',
     'source_sha256':SOURCE_SHA,
     'model_assumptions':{'populations':'15-level optically-thin stationary CMB-coupled','OPR':3,'mass_amu':3.,
       'profile':'Gaussian thermal b plus quadratic microturb b','radiation':'CMB T0=2.72548 K; no dust/continuum/line overlap',
       'transfer':'uniform prescribed-population formal slab; self-consistent radiative trapping NOT solved',
       'frequency':'Original Neufeld2026 source radiative frequencies, not CDMS2011 owner replacement',
       'Tolman':'FLRW conditional (1+z)^-4 for frequency-integrated surface brightness'},
     'grid':{'Tgas_K':list(TEMPS),'nH2_cm3':list(DENSITIES_CM3),'redshift':list(REDSHIFTS),
       'microturb_km_s':list(MICROTURB_KMS),'N_HD_cm2':list(COLUMNS_CM2)},
     'stationary_model_states':len(states),'line_transfer_rows':len(rows),
     'counts_sign':signs,'thin_abs_tau_lt_0p1_rows':int(np.sum(np.abs(tau)<.1)),
     'formal_only_abs_tau_ge_0p1_rows':int(np.sum(np.abs(tau)>=.1)),
     'population_inverted_rows':int(np.sum(tau<0)),'min_tau0':float(np.min(tau)),'max_tau0':float(np.max(tau)),
     'per_line':perJ,'physical_DAG':'0/313','canonical_DAG':'28/88',
     'original_CDMS2011_35Hz':'FAIL7/8','R6_C9_distinct_author':'NOT_RUN',
     'production':'HOLD','merge':False,'parent_PR':173,'parent_HEAD':'90d883c77b3823322f2ecdb09888442b9a620a97'}
    (out/'FULLLINE_SCIENCE_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    return summary,rows

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'))
 s,r=save(p.parse_args().root)
 print(json.dumps({k:s[k] for k in ('stationary_model_states','line_transfer_rows','counts_sign','thin_abs_tau_lt_0p1_rows','population_inverted_rows','min_tau0','max_tau0')},indent=2))
