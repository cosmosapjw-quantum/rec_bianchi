"""Source-locked non-LTE HD emission vs Francis (2025) final Appendix F.

Conditional *independent-error scenario*, not a reconstructed MIRI covariance,
Neufeld posterior, elemental D/H inference or a physical-DAG admission.
Source rate files and parent solver are unchanged from PR175 SHA dbe708e6.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.optimize import brentq,minimize
from scipy.special import log_ndtr
from jwst_conditional_fit import make_basis

FLUX_UNIT='10^-15 erg cm^-2 s^-1 (observed, not dereddened)'
PARENT_HEAD='dbe708e6c6bc9d52625321678809d7d816ecf029'
FRANCIS_MD5='652ec146b75c860c20628e5bd906d8ad'
# Six predeclared source-exact candidate thermal pairs; subset of the 36 parent pairs.
SELECTED_T_PAIRS=((100.,1000.),(200.,2000.),(300.,3000.),(400.,4000.),
                  (600.,2000.),(600.,3000.))
SCENARIOS=(0.,.06)


def get_positions(input_file):
    with Path(input_file).open(newline='',encoding='utf8') as fh:
        records=list(csv.DictReader(fh))
    if len(records)!=364:raise ValueError('Francis final F1/F2 cell count mismatch')
    if Counter(x['species'] for x in records)!=Counter({'H2':208,'HD':156}):
        raise ValueError('species count mismatch')
    status=Counter((x['species'],x['status']) for x in records)
    want={('H2','detected_positive_printed_error'):207,('H2','upper_limit'):1,
          ('HD','detected_positive_printed_error'):76,('HD','upper_limit'):72,
          ('HD','detected_rounded_error_zero'):8}
    if dict(status)!=want:raise ValueError(f'Unexpected census {status}')
    bypos=defaultdict(list)
    for x in records:
        v=float(x['value_printed'])
        if not math.isfinite(v) or v<=0:raise ValueError('Nonpositive printed flux/limit')
        if x['species']!='HD':continue
        idx=int(x['line'][2:-1])-4
        if not 0<=idx<6:raise ValueError('Not R(4..9)')
        sigma=float(x['sigma_printed']) if x['sigma_printed'] else None
        if x['status']=='detected_positive_printed_error' and not (sigma is not None and sigma>0):
            raise ValueError('Detected flux needs positive printed error')
        if x['status']=='detected_rounded_error_zero' and sigma!=0:raise ValueError('Rounded zero convention')
        bypos[(x['source'],int(x['aperture']))].append((idx,x['status'],v,sigma))
    if len(bypos)!=26 or any(len(x)!=6 for x in bypos.values()):
        raise ValueError('26 positions each with six HD lines required')
    return bypos,status


def observed_data(rows,epsilon):
    """Fixed-error declared scenario. 3-sigma printed limit => sigma=L/3.
    Rounded-zero error is *not* assigned sigma. It remains excluded.
    Error calibration eps*F is a plug-in scenario, not generative calibration.
    """
    det=[x for x in rows if x[1]=='detected_positive_printed_error']
    lim=[x for x in rows if x[1]=='upper_limit']
    return (np.array([x[0] for x in det],int),
            np.array([x[2] for x in det],float),
            np.array([math.hypot(x[3],epsilon*x[2]) for x in det],float),
            np.array([x[0] for x in lim],int),
            np.array([x[2] for x in lim],float))


def score_and_grad(x,q,dat):
    """Censored Gaussian -2log conditional L, omit parameter-constant terms.
    q[k,i] normalized flux template; x nonnegative flux amplitudes.
    """
    idet,y,s,ilim,L=dat
    mu=np.asarray(x)@q
    z=(y-mu[idet])/s
    val=float(np.dot(z,z))
    g=np.zeros(len(x),float)
    if len(idet):g+=2*q[:,idet]@((mu[idet]-y)/s**2)
    if len(ilim):
        u=(L-mu[ilim])/(L/3.)
        lp=log_ndtr(u)
        val-=2*float(np.sum(lp))
        # inverse Mills ratio, log-stable even for strongly excluded models
        log_phi=-0.5*u*u-0.5*math.log(2*math.pi)
        lam=np.exp(np.minimum(log_phi-lp,700))
        g+=2*q[:,ilim]@(lam/(L/3.))
    if not np.isfinite(val) or not np.all(np.isfinite(g)):
        raise ArithmeticError('Non-finite censored likelihood/derivative')
    return val,g


def profile(q,dat):
    """1- or 2-temperature convex nonnegative profile with an explicit KKT check."""
    q=np.asarray(q,float)
    if q.shape[1]!=6 or q.shape[0] not in (1,2) or np.any(q<0) or not np.all(np.isfinite(q)):
        raise ValueError('bad emissivity basis')
    scale=np.max(q,axis=1)
    if np.any(scale<=0):raise ValueError('zero source emission')
    q=q/scale[:,None]  # fitted x now in observed flux units, not columns
    idet,y,s,ilim,L=dat
    if len(idet)==0:
        x=np.zeros(q.shape[0]);return float(score_and_grad(x,q,dat)[0]),x,True
    # Convex 1D boundary profiles, then a 2D interior candidate.
    def one_at(k):
        qq=q[[k],:]
        def fn(a):return score_and_grad(np.array([a]),qq,dat)
        g0=fn(0.)[1][0]
        if g0>=0:return 0.,fn(0.)[0]
        hi=max(float(y.max()),float(L.max()) if len(L) else 0.,.01)
        for _ in range(60):
            if fn(hi)[1][0]>=0:break
            hi*=2
        else:raise ArithmeticError('No finite 1D profile bracket')
        x=float(brentq(lambda a:fn(a)[1][0],0,hi,xtol=1e-10))
        return x,fn(x)[0]
    profiles=[one_at(k) for k in range(q.shape[0])]
    if q.shape[0]==1:
        x=np.array([profiles[0][0]]);return profiles[0][1],x,True
    k=min(range(2),key=lambda i:profiles[i][1])
    init=np.zeros(2);init[k]=profiles[k][0]
    def fn(x):
        v,g=score_and_grad(x,q,dat);return v,g
    opt=minimize(fn,init,jac=True,method='L-BFGS-B',bounds=[(0.,None)]*2,
                 options={'maxiter':200,'ftol':1e-12,'gtol':1e-9,'maxls':30})
    candidates=[(float(opt.fun),np.asarray(opt.x,float)),
                (profiles[0][1],np.array([profiles[0][0],0.])),
                (profiles[1][1],np.array([0.,profiles[1][0]])),
                (score_and_grad(np.zeros(2),q,dat)[0],np.zeros(2))]
    value,x=min(candidates,key=lambda z:z[0])
    value,g=score_and_grad(x,q,dat)
    # KKT: grad=0 if x>0, grad>=0 at x=0; normalized by natural objective scale.
    kkt=np.where(x>1e-8,np.abs(g),np.maximum(-g,0.))
    good=bool(np.max(kkt)<=2e-4*max(1.,value))
    if not good:
        opt2=minimize(fn,x,jac=True,method='SLSQP',bounds=[(0.,None)]*2,
                      options={'maxiter':500,'ftol':1e-12})
        if opt2.fun<value:
            x=np.maximum(opt2.x,0.);value,g=score_and_grad(x,q,dat)
            kkt=np.where(x>1e-8,np.abs(g),np.maximum(-g,0.))
            good=bool(np.max(kkt)<=2e-4*max(1.,value))
    return float(value),x,good


def compute(root,render=True):
    root=Path(root);out=root/'outputs';out.mkdir(exist_ok=True,parents=True)
    bypos,census=get_positions(root/'inputs/francis_zenodo_v1_final_F1_F2_364.csv')
    # Parent source-locked emitter generator reused without modification.
    singles,skeys,doubles,dkeys,maxres=make_basis(root)
    selected=[i for i,k in enumerate(dkeys) if (k['warm_temperature_K'],k['hot_temperature_K']) in SELECTED_T_PAIRS]
    doubles=doubles[selected];dkeys=[dkeys[i] for i in selected]
    if not (len(singles)==342 and len(doubles)==228 and len(bypos)==26):raise ValueError('grid mismatch')
    if maxres>1e-12:raise ArithmeticError('stationarity error')
    rows=[];best=[];nfail=0
    for position,obs in sorted(bypos.items()):
        for eps in SCENARIOS:
            data=observed_data(obs,eps)
            counts=Counter(x[1] for x in obs)
            for tag,arr,keys in [('singleT',singles,skeys),('twoT_isobaric_subset6',doubles,dkeys)]:
                bestval=float('inf');bestitem=None
                for q,k in zip(arr,keys):
                    dev,amp,converged=profile(q,data)
                    if not converged:nfail+=1
                    row={'source':position[0],'aperture':position[1],
                         'epsilon_calibration_independent_assumed':eps,
                         'model':tag,'collision_source':k['source'],
                         'warm_T_K':k.get('warm_temperature_K',k.get('gas_temperature_K')),
                         'hot_T_K':k.get('hot_temperature_K',''),
                         'log10_p_over_kB_K_cm3':k['log10_p_over_kB_K_cm3'],
                         'n_detected_positive_error_HD':counts['detected_positive_printed_error'],
                         'n_upper_limit_HD':counts['upper_limit'],
                         'n_rounded_zero_sigma_excluded_HD':counts['detected_rounded_error_zero'],
                         'conditional_deviance':dev,'amplitudes_normalized_flux_units':';'.join(f'{v:.14g}' for v in amp),
                         'algorithm_kkt_ok':int(converged)}
                    rows.append(row)
                    if dev<bestval:bestval=dev;bestitem=row
                best.append(bestitem)
    if nfail:raise ArithmeticError(f'{nfail} grid profiles failed KKT; do not publish PASS')
    def save_csv(name,rs):
        with (out/name).open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
    save_csv('HD_CENSORED_29640_PROFILES.csv',rows)
    save_csv('HD_CENSORED_104_BEST.csv',best)
    for_summ=defaultdict(dict)
    for b in best:for_summ[(b['source'],b['aperture'],b['epsilon_calibration_independent_assumed'])][b['model']]=b
    pairs=[]
    for (s,a,eps),vv in sorted(for_summ.items()):
        x=vv['singleT'];y=vv['twoT_isobaric_subset6']
        pairs.append(dict(source=s,aperture=a,epsilon_assumed=eps,
             n_detected_HD=x['n_detected_positive_error_HD'],n_limits_HD=x['n_upper_limit_HD'],
             n_rounded_zero_HD=x['n_rounded_zero_sigma_excluded_HD'],
             singleT_deviance=x['conditional_deviance'],twoT_deviance=y['conditional_deviance'],
             delta_deviance_single_minus_two=x['conditional_deviance']-y['conditional_deviance'],
             single_best_source=x['collision_source'],two_best_source=y['collision_source'],
             two_warm_K=y['warm_T_K'],two_hot_K=y['hot_T_K'],
             two_log10_p_over_kB=y['log10_p_over_kB_K_cm3'],
             selection_note='NO_DETECTION_UNIDENTIFIABLE' if x['n_detected_positive_error_HD']==0 else 'DESCRIPTIVE_ONLY'))
    save_csv('HD_APERTURE_52_MODEL_CONTRASTS.csv',pairs)
    # One-sided exact *pointwise printed-limit envelope* in flux amplitude units for no-detection positions.
    # No coverage/probability claim is attached to this deterministic inequality.
    bounds=[]
    for (s,a),obs in sorted(bypos.items()):
        if any(r[1]=='detected_positive_printed_error' for r in obs):continue
        limit=np.array([r[2] for r in sorted(obs)])
        for q,k in zip(singles,skeys):
            raw=q[0]/max(q[0]);A=float(np.min(limit/raw))
            bounds.append({'source':s,'aperture':a,'collision_source':k['source'],
               'T_K':k['gas_temperature_K'],'log10_p_over_kB':k['log10_p_over_kB_K_cm3'],
               'max_normalized_amplitude_from_printed_R4_R9_limits':A})
    save_csv('HD_NO_DETECTION_EXACT_FLUX_ENVELOPES.csv',bounds)
    result={'unit':'REC_HD_FRANCIS_CENSORED_FLUX_20261031','science':'EXPLORATORY_CONDITIONAL_INDEPENDENT_ERROR_CENSORED_HD_ONLY',
      'source_zenodo_francis':14592550,'source_zenodo_neufeld':21165907,
      'parent_pr':175,'parent_head':PARENT_HEAD,'input_sha256':hashlib.sha256((root/'inputs/francis_zenodo_v1_final_F1_F2_364.csv').read_bytes()).hexdigest(),
      'pdf_md5_verified_previously':FRANCIS_MD5,'n_positions':26,'n_HD_detections_positive':76,
      'n_HD_limits':72,'n_HD_rounded_zero_error_excluded':8,'n_H2_detections_unused':207,
      'n_H2_limits_unused':1,'source_states_single':342,'source_states_two_full_parent':1368,
      'source_states_two_scoped':228,'temperatures_two_scoped':[list(x) for x in SELECTED_T_PAIRS],
      'profiles_evaluated':len(rows),'best_rows':len(best),'contrast_rows':len(pairs),
      'all_non_detect_positions':len(bounds)//342,'no_detection_bound_rows':len(bounds),
      'kkt_nonpassed':nfail,'max_state_residual_s_inv':maxres,
      'caveat':'Diagonal scenario only; 3sigma limit sigma=L/3 conditional; assumed independent 0 or 6pct calibration on observed positive flux. No empirical cross-line covariance, no H2 likelihood, no extinction, no zero-error resolution, no formal significance.',
      'canonical_DAG':'28/88','REC_physical_DAG':'0/313','R_C_existing':'18/20','R6_C9_distinct_author':'NOT_RUN','original_35Hz':'FAIL7/8','production':'HOLD','merge':False}
    (out/'SUMMARY.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
    if render:
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(10,5))
        rr=[r for r in pairs if r['epsilon_assumed']==.06]
        idx=np.arange(len(rr));xx=np.array([r['delta_deviance_single_minus_two'] for r in rr])
        ax.bar(idx,xx)
        ax.set_xticks(idx,[f"{r['source']} {r['aperture']}" for r in rr],rotation=75,ha='right',fontsize=7)
        ax.set_ylabel('Best conditional deviance (1T - 2T), not significance')
        ax.set_title('26 JWST apertures | conditional HD non-LTE censored likelihood, assumed independent 6%')
        ax.axhline(0,linewidth=1)
        fig.tight_layout();fig.savefig(root/'figures/HD_26_APERTURE_CONDITIONAL_CONTRAST.png',dpi=160);plt.close(fig)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'))
    print(json.dumps(compute(p.parse_args().root),sort_keys=True))
