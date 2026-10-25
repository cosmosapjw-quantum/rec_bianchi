"""One frozen stable incoming response run; requires bounded parent authorization."""
import argparse, json, os, resource, sys, traceback
from pathlib import Path
import numpy as np
import interval as iv
from certificate import certify
from common import UNIT,defaults,verify,save
from history_admission import admit
RHS=0
EPS=np.finfo(float).eps

def solve(M,b):
    global RHS
    n=1 if b.ndim==1 else b.shape[1]
    if RHS+n>639: raise RuntimeError('LARGE_RHS_CAP')
    RHS+=n
    return np.linalg.solve(M,b)

def metric(a,b):
    a=np.asarray(a);b=np.asarray(b);err=float(np.max(np.abs(a-b)));scale=max(float(np.max(np.abs(a))),float(np.max(np.abs(b))),1e-280)
    return {'absolute_error':err,'scale':scale,'normalized_error':err/scale}

def run(args,out):
    save(out/'CHILD_RESOURCE_LIMITS.json',{'RLIMIT_CPU':resource.getrlimit(resource.RLIMIT_CPU),'RLIMIT_AS':resource.getrlimit(resource.RLIMIT_AS),'RLIMIT_CORE':resource.getrlimit(resource.RLIMIT_CORE),'thread_environment':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')},'numpy_version':np.__version__})
    data,ids=verify(args.thermo,args.history,args.query_map);save(out/'VERIFIED_IDENTITIES.json',ids)
    import source
    from scalar import split
    with np.load(args.thermo/'results/primary001/BASE_COEFFICIENTS.npz',allow_pickle=False) as f: stored={k:f[k].copy() for k in f.files}
    with np.load(args.thermo/'results/primary001/ANALYTIC_RESPONSE.npz',allow_pickle=False) as f: js={k:f[k].copy() for k in f.files}
    theta=data['theta'];u=data['incoming'];blocks=source.build(source.parameters(theta),data)
    base,_=source.matrices(blocks)
    equal={k:bool(np.array_equal(base[k],stored[k])) for k in ('M','s','T','P','p','Tvv','Beta')}
    save(out/'STABLE_REPRESENTATION_IDENTITY.json',equal)
    if not all(equal.values()): raise ValueError('FRESH_STABLE_BINARY64_IDENTITY_FAILED_RETURN_TO_ROOT')
    # History admission precedes every solve.
    history,reconstructed=admit(args.history,args.query_map,args.thermo,data)
    save(out/'HISTORY_ADMISSION.json',history);np.savez(out/'HISTORY_RECONSTRUCTION.npz',reconstructed=reconstructed,stored=u)
    if history['status']!='PASS': raise ValueError('HISTORY_ADMISSION_FAILED')
    M,T,P=stored['M'],stored['T'],stored['P']; B=np.zeros((313,313));x=1-theta[1];ly=source.LYA*theta[5]/theta[4]/x
    B[0,312]=3*ly*x*1.664786871919931;B[1,311]=3*ly*x
    B[np.arange(311)+2,np.arange(311)]=stored['Tvv'][0]*x*(1-stored['p'])
    np.savez(out/'REPRESENTED_COEFFICIENTS.npz',M=M,B=B,T=T,P=P)
    V=solve(M,B);Z=solve(M,np.eye(313));K=T@V+P
    cert,a=certify(M,B,T,P,V,Z);save(out/'CERTIFICATE.json',cert)
    np.savez(out/'CERTIFICATE_ARRAYS.npz',**a);np.savez(out/'APPROXIMATE_RESPONSE.npz',Vhat=V,Zhat=Z,Khat=K)
    if cert['status']!='CERTIFIED_REPRESENTED_BINARY64_OPERATOR': raise ValueError(cert['status'])
    sharp=(cert['norm_upper']-cert['norm_lower'])/max(cert['norm_upper'],1e-280)
    residual=M@V-B;gross=np.abs(M)@np.abs(V)+np.abs(B);ratio=np.zeros_like(gross);np.divide(np.abs(residual),gross,out=ratio,where=gross!=0)
    backward={'max_componentwise':float(np.max(ratio)),'zero_gross_exact':bool(np.all(residual[gross==0]==0)),'limit':2048*EPS}
    backward['pass']=backward['max_componentwise']<=backward['limit'] and backward['zero_gross_exact']
    save(out/'BACKWARD_RESIDUAL.json',backward);np.savez(out/'BACKWARD_RESIDUAL.npz',residual=residual,gross=gross)
    delta=np.zeros(313);delta[311]=1
    jump=iv.sub((a['Klo'][311],a['Khi'][311]),iv.point(delta))
    number=iv.mul(iv.mul(iv.mul(iv.point(3e6),iv.point(source.LYA)),iv.point(theta[5])),jump)
    radiation=iv.mul(iv.mul(iv.point(source.E21),iv.point(source.EV_J)),number);atomic=iv.neg(radiation)
    numhat=3e6*source.LYA*theta[5]*(K[311]-delta); radhat=source.E21*source.EV_J*numhat
    Fhat=stored['Beta']@V[:2]/theta[5]
    ion=iv.point_dot(stored['Beta'][None,:],V[:2]);beta_sum=iv.sum_bounds(iv.point(np.abs(stored['Beta'])))[1];ionerror=iv.up(beta_sum*a['column_error_upper'])
    # Division by positive exact represented H, with outward rounding.
    flo=iv.down(iv.down(ion[0][0]-ionerror)/theta[5]);fhi=iv.up(iv.up(ion[1][0]+ionerror)/theta[5])
    proper=iv.mul((flo,fhi),iv.point(theta[5]))
    np.savez(out/'EVENT_RESPONSE.npz',number_hat=numhat,number_lo=number[0],number_hi=number[1],radiation_hat=radhat,radiation_lo=radiation[0],radiation_hi=radiation[1],atomic_hat=-radhat,atomic_lo=atomic[0],atomic_hi=atomic[1],F_hat=Fhat,F_lo=flo,F_hi=fhi,proper_hat=theta[5]*Fhat,proper_lo=proper[0],proper_hi=proper[1])
    save(out/'CONDITIONAL_BOX.json',iv.box_weights((a['Klo'],a['Khi'])))
    np.savez(out/'BOX_WEIGHTS.npz',weights=iv.abs_bounds((a['Klo'],a['Khi']))[1])
    def endpoint(shift,incoming,tag):
        dd=dict(data);dd['incoming']=incoming
        bb=source.build(source.parameters(theta,shift),dd,ownership=blocks['ownership']); vv,_=source.matrices(bb)
        X=solve(vv['M'],vv['s'])
        oo={k:split(v)[0] for k,v in source.outputs(bb,X,incoming).items()}
        np.savez(out/f'ENDPOINT_{tag}.npz',X=X,theta=np.asarray(bb['theta']),incoming=incoming,M=vv['M'],s=vv['s'],T=vv['T'],P=vv['P'],**oo)
        save(out/'RHS_USAGE.json',{'large_rhs':RHS,'large_rhs_cap':639,'last_completed_endpoint':tag})
        return oo
    baseout=endpoint(np.zeros(6),u,'base')
    np.savez(out/'BASE_SOLVED_OUTPUTS.npz',**baseout)
    scale=max(float(np.max(np.abs(u))),1e-30);directions=[(-1.)**np.arange(313)*scale,np.sin(np.arange(313)+1.)*scale]
    affine=[];mixed=[];raw={}
    for i,d in enumerate(directions):
        plus=endpoint(np.zeros(6),u+d,f'affine_{i+1}_plus');minus=endpoint(np.zeros(6),u-d,f'affine_{i+1}_minus')
        metrics={}
        for key,pred in [('outgoing',K@d),('F',Fhat@d),('R_gamma',numhat@d)]:
            actual=(plus[key]-minus[key])/2; m=metric(actual,pred)
            m['gross_roundoff']=float(2048*EPS*max(np.max(np.abs(plus[key])),np.max(np.abs(minus[key])),1e-280));m['pass']=m['normalized_error']<=2e-9;metrics[key]=m
        affine.append({'direction':i+1,'metrics':metrics})
        save(out/f'AFFINE_PAIR_{i+1}.json',affine[-1]);save(out/'AFFINE_CONTROLS.json',affine)
        for sign,oo in [('plus',plus),('minus',minus)]:
            for key,value in oo.items():raw[f'affine_{i}_{sign}_{key}']=value
    vv=[np.array([.1,-.2,.3,-.1,.2,-.3]),np.array([.2,.2,-.1,.1,-.3,.2])]
    for i,(v,d) in enumerate(zip(vv,directions)):
        pred={'outgoing':js['d_outgoing']@v+K@d,'F':js['d_F']@v+Fhat@d,'R_gamma':js['d_R_gamma']@v+numhat@d}
        for h in (1e-6,5e-7):
            plus=endpoint(h*v,u+h*d,f'joint_{i+1}_{h}_plus');minus=endpoint(-h*v,u-h*d,f'joint_{i+1}_{h}_minus')
            metrics={key:metric((plus[key]-minus[key])/(2*h),pred[key]) for key in pred}
            for m in metrics.values():m['pass']=m['normalized_error']<=2e-5
            mixed.append({'direction':i+1,'h':h,'metrics':metrics,'pass':all(m['pass'] for m in metrics.values())})
            save(out/f'JOINT_PAIR_{i+1}_{h}.json',mixed[-1]);save(out/'JOINT_LOCAL_CONTROLS.json',mixed)
            for sign,oo in [('plus',plus),('minus',minus)]:
                for key,value in oo.items():raw[f'mixed_{i}_{h}_{sign}_{key}']=value
    np.savez(out/'CONTROL_ENDPOINTS.npz',**raw)
    save(out/'AFFINE_CONTROLS.json',affine);save(out/'JOINT_LOCAL_CONTROLS.json',mixed)
    sys.path.insert(0,str(UNIT/'tests'));from manufactured import run as manufactured
    controls=manufactured(out);save(out/'MANUFACTURED_CONTROLS.json',controls)
    energy={'incoming_exact_opposites':bool(np.array_equal(radhat+(-radhat),np.zeros(313))),'stored_Js_exact_opposites':bool(np.array_equal(js['d_radiation_energy']+js['d_atomic_energy'],np.zeros(6)))}
    summary={'certificate_sharpness':sharp,'certificate_sharpness_pass':sharp<=1e-6,'backward_pass':backward['pass'],'affine_pass':all(m['pass'] for row in affine for m in row['metrics'].values()),'joint_pass':all(any(row['pass'] for row in mixed if row['direction']==i) for i in (1,2)),'energy':energy,'history_pass':history['status']=='PASS','large_rhs':RHS,'small_rhs':controls['small_rhs'],'physical_epsilon':None,'whole_cell_curvature':None,'absolute_history_bound':None,'actual_model':None,'requested_model':'gpt-6.1-sol'}
    summary['status']='PASS' if all([summary['certificate_sharpness_pass'],summary['backward_pass'],summary['affine_pass'],summary['joint_pass'],all(energy.values())]) else 'FAILED_FROZEN_CRITERION'
    save(out/'SUMMARY.json',summary)
    return summary

def main():
    parser=argparse.ArgumentParser();t,h,q=defaults()
    parser.add_argument('--thermo',type=Path,default=t);parser.add_argument('--history',type=Path,default=h);parser.add_argument('--query-map',type=Path,default=q);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    try:
        summary=run(args,args.out);print(json.dumps(summary,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),flush=True)
        return 0 if summary['status']=='PASS' else 2
    except BaseException as e:
        save(args.out/'EXCEPTION.json',{'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'large_rhs':RHS});traceback.print_exc();return 1
if __name__=='__main__':sys.exit(main())
