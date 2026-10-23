"""One independent six-case review; no production/historical campaign rerun."""
from pathlib import Path
import hashlib, json, math, sys, traceback
import numpy as np
import mpmath as mp

HERE=Path(__file__).resolve().parent
UNIT=HERE.parents[1]
sys.path.insert(0,str(UNIT/'code'))
import line_source as m

def clean(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,(np.floating,np.integer,np.bool_)):return v.item()
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [clean(x) for x in v]
    return v

out=HERE/'PROBES_RAW.json'
assert not out.exists(),'Independent original evidence is immutable'
rows=[]
mp.mp.dps=90
eps=np.finfo(float).eps

def map_case(label,card_id,N,f,x0,S,path,omega):
    card=m.CARDS[card_id]
    qmax=1+float(np.linalg.eigvalsh(S)[-1])
    eq=card.g*f/(1+(card.g+1)*f)
    dmin=card.g-(card.g+1)*max(x0,eq)
    H=card.A_s_inv*card.wavelength_m**3*N*dmin/(8*math.pi*qmax*path)
    args=dict(card_id=card_id,population_scope=card.population_scope,N_m3=N,
              x0=x0,H_s_inv=H,f_plus=f,S=S,omega=omega)
    actual=m.thick_local_step(**args)
    # Form all equilibrium/root coefficients independently from input scalars.
    g,F=mp.mpf(card.g),1+(mp.mpf(card.g)+1)*mp.mpf(f)
    b=g+1;eqm=g*mp.mpf(f)/F;d0=g/F;y=mp.mpf(x0)-eqm
    z=-b*y/d0
    y1=-d0/b*mp.lambertw(z*mp.exp(z-mp.mpf(omega)),0)
    x1=eqm+y1; packet=-mp.mpf(N)*(y1-y)
    endpoint_error=float(abs(mp.mpf(actual['x1'])-x1))
    packet_error=float(abs(mp.mpf(actual['delta_n_gamma_m3'])-packet))
    endpoint_limit=5e-11*float(abs(y))+64*eps*float(abs(eqm))
    packet_limit=5e-13*N*float(abs(y))+64*eps*abs(actual['delta_n_gamma_m3'])
    checks={'endpoint':endpoint_error<=endpoint_limit,'packet':packet_error<=packet_limit,
       'monotone':min(x0,float(eqm))-64*eps<=actual['x1']<=max(x0,float(eqm))+64*eps,
       'packet_sign':actual['delta_n_gamma_m3']*float(y)>=0,
       'root_residual':abs(actual['log_root_residual'])<=5e-13*(1+omega+abs(actual['z0']))}
    rows.append({'id':label,'kind':'OFFGRID_LOCAL_MAP','inputs':args,'actual':actual,
       'oracle':'90 digit principal LambertW; coefficients rebuilt from original input scalars',
       'endpoint_mp':mp.nstr(x1,85),'packet_mp':mp.nstr(packet,85),
       'endpoint_error':endpoint_error,'endpoint_limit':endpoint_limit,
       'packet_error':packet_error,'packet_limit':packet_limit,
       'packet_relative_error':float(abs((mp.mpf(actual['delta_n_gamma_m3'])-packet)/packet)),
       'checks':checks,'pass':all(checks.values())})

failure=None
try:
    map_case('g1_near_inversion','H_LYA_J1HALF',2e8,.03,.49,np.diag([-.7,.2,.5]),25,.07)
    map_case('g2_high_occupation_absorption','H_LYA_J3HALF',4e8,3,.02,np.diag([-.12,-.18,.3]),20.3,1.73)
    map_case('g3_tiny_packet_slow_ray','H_LYA_EFFECTIVE_2P',7e8,.001,.4,np.diag([-.98,.17,.81]),25,1e-12)
    card=m.CARDS['H_LYA_J3HALF'];N=9e8;f=.37;x=.6;t=.73;S=np.diag([.4,.4,-.8])
    nl=N*(1-x);nu=N*x;H=card.A_s_inv*card.wavelength_m**3*(card.g*nl-nu)/(8*math.pi*t)
    state=m.LineState(card.id,card.population_scope,nl,nu,H,f,S,'INDEPENDENT_OFFGRID_LRS')
    actual=m.exchange_source(state)
    tm=mp.mpf(card.A_s_inv)*mp.mpf(card.wavelength_m)**3*(mp.mpf(card.g)*mp.mpf(nl)-mp.mpf(nu))/(8*mp.pi*mp.mpf(H))
    def beta(mu):
        q=1+mp.mpf(.4)*(1-mu*mu)+mp.mpf(-.8)*mu*mu
        tau=tm/q
        return -mp.expm1(-tau)/tau
    B=mp.quad(beta,[-1,0,1])/2
    Qzz=mp.quad(lambda mu:(mu*mu-mp.mpf(1)/3)*beta(mu),[-1,0,1])/2
    D=mp.mpf(nu)*(1+mp.mpf(f))-mp.mpf(card.g)*mp.mpf(nl)*mp.mpf(f)
    R=mp.mpf(card.A_s_inv)*B*D
    Qref=np.diag([-float(Qzz)/2,-float(Qzz)/2,float(Qzz)])
    errors={'B_relative':float(abs((mp.mpf(actual['B'])-B)/B)),
        'Q_frobenius_over_B':float(np.linalg.norm(actual['Q']-Qref))/float(B),
        'R_relative':float(abs((mp.mpf(actual['net_R_m3_s'])-R)/R))}
    rows.append({'id':'g2_LRS_source','kind':'OFFGRID_SOURCE','inputs':dict(N=N,f=f,x=x,t=t,S=S),
        'actual':actual,'oracle':'Independent 90 digit one-dimensional LRS integrals; no ANGULAR donor oracle reused',
        'B_mp':mp.nstr(B,85),'Qzz_mp':mp.nstr(Qzz,85),'R_mp':mp.nstr(R,85),
        'errors':errors,'limit':5e-10,'pass':max(errors.values())<=5e-10})
    for label,native,initial_depth,f in [('duplicate_map_owner',True,100,.2),('absorption_initial_gate_trap',False,40,.7)]:
        card=m.CARDS['H_LYA_EFFECTIVE_2P'];N=1e9;x0=0.;S=np.diag([-.2,.03,.17]);qmax=1.17
        H=card.A_s_inv*card.wavelength_m**3*N*card.g/(8*math.pi*qmax*initial_depth)
        eq=card.g*f/(1+(card.g+1)*f)
        path=initial_depth*(card.g-(card.g+1)*eq)/card.g
        args=dict(card_id=card.id,population_scope=card.population_scope,N_m3=N,x0=x0,H_s_inv=H,
            f_plus=f,S=S,omega=.2,native_line_owner_active=native)
        try:
            m.thick_local_step(**args)
        except ValueError as exc:
            rejected=True;reason=str(exc)
        else:
            rejected=False;reason='unexpected acceptance'
        rows.append({'id':label,'kind':'OFFGRID_REJECTION','inputs':args,
            'initial_depth_ratio':initial_depth,'whole_path_depth_ratio':path,
            'rejected':rejected,'reason':reason,'pass':rejected})
except BaseException:
    failure=traceback.format_exc()
finally:
    report={'schema':'LINE01_SINGLE_INDEPENDENT_REVIEW_PROBES_V1','cases':rows,
        'case_count':len(rows),'case_budget':6,'exception':failure,
        'status':'PASS' if not failure and len(rows)==6 and all(r['pass'] for r in rows) else 'FAIL',
        'production_rows_rerun':0,'old_campaign_rerun':0,'new_IVPs':0,
        'model_counters':dict(m.COUNTERS),'angular_counters':dict(m.angular.COUNTERS),
        'reviewed_code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (UNIT/'code').glob('*.py')}}
    out.write_text(json.dumps(clean(report),indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'],'case_count':len(rows),'exception':failure,
                     'failed':[r['id'] for r in rows if not r['pass']]}))
