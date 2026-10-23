from pathlib import Path
from decimal import Decimal, localcontext
import json,sys,math,hashlib,time
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'code'))
import native_line_owner as nlo

def ser(v):
 if isinstance(v,np.ndarray): return v.tolist()
 if isinstance(v,(np.floating,np.integer,np.bool_)): return v.item()
 if isinstance(v,dict): return {k:ser(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)): return [ser(x) for x in v]
 return v

def exact2(owner,r,b,dr=0.):
 with localcontext() as ctx:
  ctx.prec=80
  D=Decimal.from_float
  k=[[D(float(v)) for v in row] for row in owner.K]
  j=[D(float(v)) for v in owner.j]
  k[1][1]+=D(r)-D(owner.r0)
  j[1]+=D(r)*D(b)-D(owner.r0)*D(owner.b0)
  det=k[0][0]*k[1][1]-k[0][1]*k[1][0]
  xs=(k[1][1]*j[0]-k[0][1]*j[1])/det
  xp=(k[0][0]*j[1]-k[1][0]*j[0])/det
  drive=xp-D(b)
  forcing=-drive*D(dr)
  ds=-k[0][1]/det*forcing
  dp=k[0][0]/det*forcing
  return {'xs':str(xs),'xp':str(xp),'drive':str(drive),'flux':str(D(r)*drive),'dxr':[float(ds),float(dp)]}

def rel(a,b):return abs(a-b)/max(abs(a),abs(b),1e-300)

start=time.monotonic();o=nlo.NativeLineOwner();out=[]
# Fifth off-grid case: new depth/shear; direct 80-digit 2x2 solve supplies the
# small difference independently of the new rational implementation.
tau=1.1;S=np.diag([-.27,.08,.19]);ev=o.angular_event(tau,S,synthetic=True)
rb=ev['rbase_s_inv'];rf=ev['rstar_s_inv'];b=o.b0
base=o.solution(rb,b);finite=o.solution(rf,b)
hb=o.solved_line_rate(base);hf=o.solved_line_rate(finite)
refb=exact2(o,rb,b);reff=exact2(o,rf,b)
bound=o.state_bound(rb,b,tau,S,base_solution=base)
lim=bound['bounds']['flux_per_H_s']['value'];roundoff=64*nlo.EPS*(abs(hb)+abs(hf))
r={'case':'P5_stable_finite_flux_precision','tau':tau,'shear':S,'rbase':rb,'rfinite':rf,'b':b,'stable_base_flux':hb,'stable_finite_flux':hf,'rounded_base_flux':rb*(base.state[1]-b),'rounded_finite_flux':rf*(finite.state[1]-b),'base_reference80':refb,'finite_reference80':reff,'base_flux_relative_error':rel(hb,float(refb['flux'])),'finite_flux_relative_error':rel(hf,float(reff['flux'])),'flux_difference':abs(hf-hb),'analytic_bound':lim,'stable_arithmetic_allowance':roundoff,'departure_gross_allowance':64*nlo.EPS*rb*(abs(finite.state[1])+abs(b)),'bound':bound}
r['passed']=r['base_flux_relative_error']<5e-9 and r['finite_flux_relative_error']<5e-9 and r['flux_difference']<=lim+roundoff and lim>roundoff
out.append(r)
# Sixth off-grid case: high-r absorption r-only derivative, specifically the
# changed solved-state JVP forcing. This is not an old successful-case replay.
rval=2.37e8;b=1.031*o.b0;dr=.23*rval
sol=o.solution(rval,b);actual=o.solution_jvp(sol,dr=dr,db=0.)
reference=exact2(o,rval,b,dr)
dxr=np.array(reference['dxr']);ref=np.concatenate((dxr,-o.W@dxr))
err=float(np.max(np.abs(actual-ref))/max(np.max(np.abs(ref)),np.max(np.abs(actual)),1e-300))
out.append({'case':'P6_stable_high_r_jvp','r':rval,'b_ratio':1.031,'dr':dr,'reference80':reference,'analytical':actual,'reference':ref,'jvp_scaled_error':err,'stable_drive':o.solved_drive(sol),'rounded_drive':float(sol.state[1]-b),'passed':err<=5e-9})
raw={'schema':'LINE02_TARGETED_REPAIR_REVIEW_V1','scope':'Same independent pass, two new off-grid cases after stable-drive implementation change; original four raw cases preserved.','offgrid_cases_added':2,'offgrid_cases_total':6,'primary_case_replays':0,'IVP':0,'native_runtime':0,'direct313_solves':0,'decimal80_direct2x2_solves':3,'records':out,'operator_counters':dict(nlo.COUNTERS),'elapsed_s':time.monotonic()-start,'code_identities':[]}
for path in [ROOT/'code/native_line_owner.py',ROOT/'code/run_line02.py',HERE/'probe_stable_drive.py']:
 data=path.read_bytes();raw['code_identities'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
raw['passed']=all(q['passed'] for q in out)
p=HERE/'STABLE_DRIVE_PROBE_RAW.json'
if p.exists():raise RuntimeError('supplemental raw already exists')
p.write_text(json.dumps(ser(raw),indent=2,allow_nan=False)+'\n')
print(json.dumps({'passed':raw['passed'],'offgrid_total':6,'P5_base_relative_error':out[0]['base_flux_relative_error'],'P5_finite_relative_error':out[0]['finite_flux_relative_error'],'P5_difference':out[0]['flux_difference'],'P5_bound':out[0]['analytic_bound'],'P5_stable_allowance':out[0]['stable_arithmetic_allowance'],'P6_jvp_error':out[1]['jvp_scaled_error']},indent=2))
