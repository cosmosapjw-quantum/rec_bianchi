"""Exploratory Neufeld2026 HD 15-level line-shape fits to Francis2025 arXiv v1 printed observations.

NONAUTHORITATIVE: covariance is a declared sensitivity family, not an acquired MIRI
joint covariance or a recovered Francis/Neufeld likelihood. No source-owner mutation.
Upper limits and 0.00 rounded measurement errors are retained but excluded from
Gaussian profile. Keep all real constants and provenance attached to outputs.
"""
from __future__ import annotations
import csv,hashlib,json,math,os,sys,argparse
from pathlib import Path
import numpy as np
from hd_line_transfer import read_models
from hd_cmb15 import solve_cmb

SOURCE_PDF='https://arxiv.org/pdf/2501.02085v1'
SOURCE_VERSION='Francis2025_arxiv_2501.02085v1_TABLE_E1_E2_transcription_NOT_FINAL_ZENODO'
FLUX_UNIT='1e-15 erg cm^-2 s^-1 (observed, not dereddened)'
EPS=0.06 # Neufeld 2026 adds 6% flux error in quadrature
T_EXACT=(100.,200.,300.,400.,600.,1000.,2000.,3000.,4000.)
PRESSURE_LOG_K_CM3=tuple(float(np.log10(x)) for x in np.geomspace(1e7,1e10,19))
DENSITY_CM3=tuple(float(x) for x in np.geomspace(1e2,1e8,19))
SOURCE_NAMES=('std','alternate')


def read_flux(root:Path):
    records=[]
    for sp, transitions in [('H2',tuple('S(%d)'%i for i in range(1,9))),
                            ('HD',tuple('R(%d)'%i for i in range(4,10)))]:
        file=root/'source'/('francis25_table_E1_H2.txt' if sp=='H2' else 'francis25_table_E2_HD.txt')
        observed=set()
        for row in file.read_text(encoding='utf8').splitlines():
            if not row.strip() or row.startswith('#'): continue
            src,ap,vals=row.split('|')
            k=(src,int(ap))
            if k in observed: raise ValueError('Duplicate position '+str(k))
            observed.add(k)
            cells=vals.strip().split()
            if len(cells)!=len(transitions):raise ValueError(f'Bad {sp} row {k}: {len(cells)}')
            for line,cell in zip(transitions,cells):
                if cell.startswith('<'):
                    v=float(cell[1:]);sigma=None
                    status='upper_limit_3sigma'
                else:
                    v,sigma=map(float,cell.split('/'))
                    status='detected_rounded_error_zero' if sigma==0 else 'detected_positive_printed_error'
                if v<=0 or (sigma is not None and sigma<0):raise ValueError('Nonphysical reported flux/error')
                records.append(dict(source=src,aperture=int(ap),species=sp,line=line,status=status,
                    value_printed=v,sigma_printed=sigma,units=FLUX_UNIT,
                    source_version=SOURCE_VERSION))
        if len(observed)!=26:raise ValueError(f'Expected 26 positions for {sp}')
    return records


def row_summary(records):
    from collections import Counter
    counts=Counter(r['status'] for r in records)
    apertures={(r['source'],r['aperture']) for r in records}
    if not (len(records)==364 and len(apertures)==26 and counts['upper_limit_3sigma']==73
            and counts['detected_rounded_error_zero']==8 and counts['detected_positive_printed_error']==283):
        raise ValueError('Printed-table census differs from transcribed source')
    return counts


def covariance(f,sigma,rho:float,eps:float=EPS):
    """C=D+e²[(1-rho)diag(F²)+rho F F^T], a *sensitivity*, not measured C."""
    f=np.asarray(f,float);sigma=np.asarray(sigma,float)
    if f.ndim!=1 or f.shape!=sigma.shape or np.any(f<=0) or np.any(sigma<=0):
        raise ValueError('Covariance needs positive detected printed errors')
    if not 0<=rho<=1:raise ValueError('Assumed correlation rho must be in [0,1]')
    C=np.diag(sigma*sigma+(1-rho)*(eps*f)**2)+rho*eps**2*np.outer(f,f)
    np.linalg.cholesky(C)
    return C


def profile_nonnegative_basis(flux,sigma,basis,*,rho=0.):
    """Profile nonnegative amplitudes for n_models x n_components x n_lines.

    Returned chi^2 is a GLS quadratic *conditional diagnostic*.  F (observed)
    in calibration term is a plug-in; no model-dependent logdet or proper joint
    posterior evidence is claimed. Bounds constrain amplitudes >= 0.
    """
    f=np.asarray(flux,float);s=np.asarray(sigma,float);q=np.asarray(basis,float)
    if not (q.ndim==3 and q.shape[2]==len(f) and q.shape[1] in (1,2)):
        raise ValueError('Wrong basis shape')
    if not np.all(np.isfinite(q)) or np.any(q<0) or np.any(np.max(q,axis=2)<=0):
        raise ValueError('Invalid emissivity')
    C=covariance(f,s,rho)
    L=np.linalg.cholesky(C)
    y=np.linalg.solve(L,f)
    # Normalize each component for conditioning, leaving amplitudes free.
    scale=np.max(q,axis=2)
    Q=q/scale[:,:,None]
    # whiten across last axis
    wq=np.linalg.solve(L,Q.reshape(-1,len(f)).T).T.reshape(Q.shape)
    dots=np.einsum('nki,i->nk',wq,y)
    norms=np.einsum('nki,nki->nk',wq,wq)
    coeff=np.maximum(dots/norms,0)
    yy=np.dot(y,y)
    boundary=yy-2*coeff*dots+coeff*coeff*norms
    if q.shape[1]==1:
        scores=boundary[:,0]
        mix=coeff/scale
    else:
        a=np.einsum('ni,ni->n',wq[:,0],wq[:,0]); b=np.einsum('ni,ni->n',wq[:,1],wq[:,1]);c=np.einsum('ni,ni->n',wq[:,0],wq[:,1])
        v=dots[:,0];w=dots[:,1]
        det=a*b-c*c
        good=(det > 1e-12*a*b)
        xx=np.zeros_like(a);zz=np.zeros_like(a)
        xx[good]=(v[good]*b[good]-w[good]*c[good])/det[good]
        zz[good]=(w[good]*a[good]-v[good]*c[good])/det[good]
        interior=good&(xx>=0)&(zz>=0)
        # NNLS cone in two dimensions: one of interior or boundary faces.
        score2=np.full_like(a,np.inf)
        score2[interior]=yy-v[interior]*xx[interior]-w[interior]*zz[interior]
        choose=np.argmin(np.stack([boundary[:,0],boundary[:,1],score2],axis=1),axis=1)
        scores=np.where(choose==0,boundary[:,0],np.where(choose==1,boundary[:,1],score2))
        mix=np.zeros_like(coeff)
        mix[choose==0,0]=coeff[choose==0,0]/scale[choose==0,0]
        mix[choose==1,1]=coeff[choose==1,1]/scale[choose==1,1]
        mix[choose==2,0]=xx[choose==2]/scale[choose==2,0]
        mix[choose==2,1]=zz[choose==2]/scale[choose==2,1]
    scores=np.maximum(scores,0.)
    return scores,mix


def make_basis(root:Path):
    """Match the frozen predecessor's grids exactly; don't silently extend a gate.

    Single-T: 19 original-scope H2 density values [1e2,1e8] cm^-3 for
    each original T knot. Two-T: 19 p/kB values [1e7,1e10] K cm^-3,
    n(T)=(p/kB)/T, exact original T knots, source std + alternate.
    """
    models=read_models(root) # strict 4-source SHA-256 identity, no switch
    singles=[];skeys=[];pairs=[];pkeys=[];resid=[]
    for srcname in SOURCE_NAMES:
        model=models[srcname]
        for T in T_EXACT:
            for n in DENSITY_CM3:
                st=solve_cmb(model,T,n,0.,f_ortho=.75)
                P={r['J_upper']-1:r['net_W_per_HD'] for r in st['line_power_records']}
                arr=np.array([P[J] for J in range(4,10)],float)
                if not np.all(arr>0):raise ValueError('Non-positive R4..R9 HD net power')
                singles.append(arr[None,:]);skeys.append(dict(source=srcname,gas_temperature_K=T,
                                      log10_p_over_kB_K_cm3=float(np.log10(n*T)),gas_density_cm3=n))
                resid.append(st['max_stationary_residual_s_inverse'])
        for logp in PRESSURE_LOG_K_CM3:
            p=10**logp
            emiss={}
            for T in T_EXACT:
                n=p/T
                st=solve_cmb(model,T,n,0.,f_ortho=.75)
                P={r['J_upper']-1:r['net_W_per_HD'] for r in st['line_power_records']}
                arr=np.array([P[J] for J in range(4,10)],float)
                if not np.all(arr>0):raise ValueError('Non-positive R4..R9 HD net power')
                emiss[T]=arr
                resid.append(st['max_stationary_residual_s_inverse'])
            for i,T1 in enumerate(T_EXACT):
                for T2 in T_EXACT[i+1:]:
                    pairs.append(np.stack([emiss[T1],emiss[T2]]))
                    pkeys.append(dict(source=srcname,warm_temperature_K=T1,hot_temperature_K=T2,log10_p_over_kB_K_cm3=logp,
                                      warm_density_cm3=p/T1,hot_density_cm3=p/T2))
    if len(singles)!=342 or len(pairs)!=1368:
        raise ValueError('Basis count mismatch')
    return np.stack(singles),skeys,np.stack(pairs),pkeys,max(resid)

def compute(root:Path, plot=True):
    root=Path(root)
    out=root/'outputs';out.mkdir(exist_ok=True,parents=True)
    data=read_flux(root)
    counts=row_summary(data)
    with (out/'francis2025_arxiv_v1_line_flux_364.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    basis_single,skeys,basis_double,dkeys,maxres=make_basis(root)
    if maxres>1e-12:raise ArithmeticError('Invalid 15-state stationarity residual')
    pos=sorted({(r['source'],r['aperture']) for r in data})
    fits=[];best_rows=[]
    grid_file=(out/'conditional_hd_54720_grid_scores.csv').open('w',newline='',encoding='utf8')
    grid_fields=['source','aperture','model','rho_calibration_assumed','n_usable_HD','collision_source','warm_T_K','hot_T_K',
                 'log10_p_over_kB_K_cm3','conditional_profile_chi2']
    gw=csv.DictWriter(grid_file,fieldnames=grid_fields)
    gw.writeheader()
    for p in pos:
        obs=[r for r in data if (r['source'],r['aperture'])==p and r['species']=='HD'
             and r['status']=='detected_positive_printed_error']
        ndet=len(obs)
        if ndet<3:
            best_rows.append(dict(source=p[0],aperture=p[1],n_usable_HD=ndet,reason='LT_3_POSITIVE_ERROR_DETECTIONS',mode='EXCLUDED'))
            continue
        inds=np.array([int(r['line'][2:-1])-4 for r in obs]);flux=np.array([r['value_printed'] for r in obs]);sig=np.array([r['sigma_printed'] for r in obs])
        for rho in (0.,1.):
            for tag,basis,keys in [('singleT',basis_single,skeys),('twoT_isobaric',basis_double,dkeys)]:
                score,mix=profile_nonnegative_basis(flux,sig,basis[:,:,inds],rho=rho)
                for k, val in zip(keys,score):
                    gw.writerow(dict(source=p[0],aperture=p[1],model=tag,rho_calibration_assumed=rho,n_usable_HD=ndet,
                         collision_source=k['source'],warm_T_K=k.get('warm_temperature_K',k.get('gas_temperature_K')),
                         hot_T_K=k.get('hot_temperature_K',''),log10_p_over_kB_K_cm3=k['log10_p_over_kB_K_cm3'],
                         conditional_profile_chi2=float(val)))
                j=int(np.argmin(score));pval=keys[j]
                pred=np.einsum('k,ki->i',mix[j],basis[j][:,inds])
                row=dict(source=p[0],aperture=p[1],model=tag,assumed_calibration_rho=rho,n_usable_HD=ndet,
                         number_grid_models=len(keys),min_chi2_conditional=float(score[j]),
                         fitted_params=json.dumps(pval,sort_keys=True),
                         best_component_amplitude_model_units=json.dumps([float(x) for x in mix[j]]),
                         observed_HD_lines=';'.join(x['line'] for x in obs),
                         best_model_flux_printed_units=';'.join(f'{x:.10g}' for x in pred))
                best_rows.append(row)
                if p==('HH 211',7):
                    fits.append(dict(**row,flux=flux.tolist(),sigma=sig.tolist(),pred=pred.tolist(),
                                     model_mixture_weights=mix[j].tolist(),source_identity=pval.get('source')))
    grid_file.close()
    # all rows may have different keys due excluded marker
    with (out/'hd_shape_best_profile_by_position.csv').open('w',newline='',encoding='utf8') as f:
        fields=['source','aperture','model','assumed_calibration_rho','n_usable_HD','number_grid_models','min_chi2_conditional','fitted_params',
                'best_component_amplitude_model_units','observed_HD_lines','best_model_flux_printed_units','reason','mode']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(best_rows)
    with (out/'hh211_ap7_conditional_profiles.json').open('w',encoding='utf8') as f:
        f.write(json.dumps(fits,indent=2,sort_keys=True)+'\n')
    summary=dict(input_source=SOURCE_VERSION,source_pdf=SOURCE_PDF,flux_units=FLUX_UNIT,
        rows=len(data),apertures=len(pos),detections_positive_printed_sigma=counts['detected_positive_printed_error'],
        detections_rounded_0_sigma=counts['detected_rounded_error_zero'],upper_limits_3sigma=counts['upper_limit_3sigma'],
        nonlte_original_source_models=len(basis_single),two_temperature_isobaric_models=len(basis_double),
        temperatures_K=list(T_EXACT),log10_pressure_grid=list(PRESSURE_LOG_K_CM3),
        single_temperature_density_grid_cm3=list(DENSITY_CM3),
        full_joint_covariance='NOT_ACQUIRED',gaussian_likelihood='NOT_RECONSTRUCTED',
        score_definition='conditional GLS quadratic with observed flux fixed-covariance plug-in; profiles nonnegative common amplitudes',
        rho_values=[0.,1.],source_variant='std primary; alternate source sensitivity only',
        source_owner_switch=False,original_35hz='FAIL7/8',canonical_dag='28/88',rec_physical_dag='0/313',scoped_rc='18/20',
        production='HOLD',merge=False,auto_next_node=False,max_stationarity_residual_s_inverse=maxres,
        compared_positions=sum('model' in x for x in best_rows)//4,excluded_positions=len(pos)-sum('model' in x for x in best_rows)//4,
        all_conditional_best_rows=len([x for x in best_rows if 'model' in x]),
        exhaustive_grid_scores=sum(x['number_grid_models'] for x in best_rows if x.get('number_grid_models')),
        caution='Printed arXiv v1 only; final Francis Zenodo appendix unverified. No dust/extinction, joint MIRI covariance, upper-limit likelihood, or H2 joint non-LTE fit.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf8')
    if plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(8,4.5))
        obs=next(t for t in fits if t['model']=='twoT_isobaric' and t['assumed_calibration_rho']==0.)
        j=np.arange(len(obs['flux']))
        ax.errorbar(j,obs['flux'],yerr=obs['sigma'],marker='o',linestyle='none',label='HH 211 aperture 7 measured (printed errors)')
        for rho in (0.,1.):
            tt=next(t for t in fits if t['model']=='twoT_isobaric' and t['assumed_calibration_rho']==rho)
            ax.plot(j,tt['pred'],marker='x',label=f'two-T conditional, assumed rho={rho:g}')
        ax.set_xticks(j,[f'HD R({i})' for i in range(4,10)])
        ax.set_ylabel(r'Line flux ($10^{-15}$ erg cm$^{-2}$ s$^{-1}$)')
        ax.set_title('Francis et al. arXiv v1 printed lines; no empirical joint covariance')
        ax.legend(fontsize=8);fig.tight_layout()
        fig.savefig(root/'figures'/'HH211_aperture7_conditional_models.png',dpi=160)
        plt.close(fig)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.')
    args=parser.parse_args()
    summary=compute(Path(args.root))
    print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
