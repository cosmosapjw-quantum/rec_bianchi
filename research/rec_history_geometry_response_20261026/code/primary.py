"""One frozen GEO01 run. Requires bounded runner and root RUN_READY."""
import csv,json,math,os,resource,sys,traceback
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from common import UNIT,save,load,source_snapshot,Counter
import geometry as geo
import decimal_oracle
EPS=np.finfo(float).eps
E21=10.198714553953742;E31=12.087365397278509;E41=12.748393192442178
LYA=4.662899067555897e15;EV_J=1.602176634e-19

def admission(out):
 c=load('PB_NATIVE_CHART.npz');history=load('history.npz',('eta','dlna','energy_eV'));K=load('KS_POINT.npz',('Khat',))['Khat'];ki=load('KS_INTERVAL.npz',('Klo','Khi'))
 meta={row[1]:float(row[2]) for row in csv.reader((UNIT/'inputs/target_native_snapshot.csv').open()) if row[0]=='META'}
 witness=json.loads((UNIT/'inputs/PB_QUERY_WITNESSES.json').read_text());r=c['safe_radius'];geo.margins(r)
 e=history['energy_eV'];et=np.r_[e,E21,E31];all_es=np.r_[e,E21,E31,E41]
 source=np.arange(1,314);source[139]=311;source[270]=312;source[310]=313;source[311]=140;source[312]=271
 if not np.array_equal(c['source'],source) or len(set(map(tuple,c['active_slots'])))!=626:raise ValueError('NATIVE_ROUTE_OR_ENDPOINT_IDENTITY')
 if meta['iz_local']!=5127 or meta['z']!=1099.9986525171403:raise ValueError('TARGET_OR_PREFIX_IDENTITY')
 if K.shape!=(314,313) or any(a.shape!=K.shape for a in ki.values()) or np.any(ki['Klo']>ki['Khi']) or not all(np.all(np.isfinite(a)) for a in (K,*ki.values())):raise ValueError('KS_ARRAY_DOMAIN')
 if not np.all((ki['Klo']<=K)&(K<=ki['Khi'])):raise ValueError('KS_MIDPOINT_OUTSIDE_INTERVAL')
 for j,row in enumerate(witness):
  if row['incoming_index']!=j or row['source_index']!=source[j] or float(F(row['slope_exact']))!=c['slope_hat'][j] or row['safe_radius']!=r[j]:raise ValueError('PB_WITNESS_IDENTITY')
 es=all_es[source];L=geo.energies(es,et);x=et/meta['TR_eV_rescaled'];g=c['slope_hat'];eta_t=-math.log1p(meta['z']);bridge=c['query']-(eta_t-L)
 h=min(1e-3,.25*float(np.min(r/(L+r))))
 if not math.isfinite(h) or h<=0:raise ValueError('INVALID_FROZEN_STEP')
 if not np.all(L*h/(1-h)<r):raise ValueError('ALL_DIRECTION_MARGIN_BOUND')
 W=np.exp(-x)
 np.savez(out/'SOURCE_BINDING.npz',source_index=source,target_energy_eV=et,source_energy_eV=es,Lambda=L,x_target=x,query_native=c['query'],query_geometric=eta_t-L,query_arithmetic_bridge=bridge,slope=g,safe_radius=r,stored_incoming=c['stored_incoming'],baseline_total_occupation=c['stored_incoming']+W,reference_W=W,active_slots=c['active_slots'],h=h,TR_eV=meta['TR_eV_rescaled'],eta_target=eta_t)
 save(out/'SOURCE_ADMISSION.json',dict(status='PASS',query_count=313,endpoint_slots=626,prefix=5127,source_is_target_energy_index=False,target_energy_order='Ebin[0:311],E21,E31',native_TR_eV=meta['TR_eV_rescaled'],native_H_sInv=meta['H_sInv'],native_z=meta['z'],min_safe_radius=float(r.min()),max_safe_radius=float(r.max()),h=h,Lambda_min=float(L.min()),Lambda_max=float(L.max()),maximum_query_arithmetic_bridge=float(abs(bridge).max()),baseline_stored_min=float(c['stored_incoming'].min()),baseline_total_min=float((c['stored_incoming']+W).min()),anchoring='q=q_native+Lambda-Delta; reference increment relative its own baseline',new_source_solve=False))
 return c,K,ki,meta,L,x,g,h

def guards(out):
 controls=[]
 def refuse(name,fn):
  try:fn()
  except ValueError as exc:controls.append({'name':name,'refused':True,'reason':str(exc)});return
  controls.append({'name':name,'refused':False});raise ValueError('GUARD_NOT_REFUSED:'+name)
 refuse('shear_shape',lambda:geo.shear([1,-1]));refuse('shear_nonfinite',lambda:geo.shear([1,float('nan'),-1]));refuse('shear_trace',lambda:geo.shear([1,0,0]))
 refuse('energy_zero',lambda:geo.energies([1.],[0.]));refuse('energy_ratio_nonpositive_log',lambda:geo.energies([1.],[1.]));refuse('energy_nonfinite',lambda:geo.energies([float('inf')],[1.]))
 refuse('zero_margin',lambda:geo.margins(np.zeros(313)));refuse('outside_margin',lambda:geo.margins(np.ones(313),np.ones(313)))
 refuse('direction_norm',lambda:geo.direction([1,1,0]));refuse('direction_nonfinite',lambda:geo.direction([float('nan'),0,1]))
 save(out/'NEW_GUARDS.json',{'status':'PASS','distinct_controls':len(controls),'controls':controls});return len(controls)

def analytic(L,x,g,out):
 ns,ww,exactw,squares=geo.rays();moments=geo.exact_rule();save(out/'EXACT_ANGULAR_MOMENTS.json',moments)
 np.savez(out/'ANGULAR_RULE.npz',directions=ns,weights=ww)
 results={};checks=[]
 for label,v in [('v1',np.array([1.,-.5,-.5])),('v2',np.array([1.,-1.,0.]))]:
  ds=[geo.derivatives(L,x,g,v,n) for n in ns]
  a={key:np.array([d[key] for d in ds]) for key in ('q1','q2','u1','u2','gross1','gross2','tangent')}
  hc=ds[0]['hc'];kc=ds[0]['kc'];B=L*hc;S2=float(v@v)
  m2=S2*(hc*(-4*L/15+2*L*L/5)+kc*(2*L*L/15));mean1=ww@a['u1'];mean2=ww@a['u2']
  Q=np.array([n[:,None]*n[None,:]-np.eye(3)/3 for n in ns]);quad=np.einsum('r,rij,rq->qij',ww,Q,a['u1']);qexpected=B[:,None,None]*(2/15)*np.diag(v)[None,:,:]
  mean1gross=ww@a['gross1'];mean2gross=ww@a['gross2']+S2*((abs(g)+x*np.exp(-x))*(4*L/15+2*L*L/5)+(x*x+x)*np.exp(-x)*(2*L*L/15))
  quadgross=np.einsum('r,rij,rq->qij',ww,abs(Q),a['gross1'])+abs(qexpected)
  tangentdot=np.einsum('ri,rqi->rq',ns,a['tangent']);tangentgross=np.einsum('ri,rqi->rq',abs(ns),abs(a['tangent']))
  metrics=dict(first_monopole=geo.normalized(mean1,mean1gross),second_monopole=geo.normalized(mean2-m2,mean2gross),quadrupole=geo.normalized(quad-qexpected,quadgross),source_direction_tangent=geo.normalized(tangentdot,tangentgross))
  passed=all(metrics[k]<=2048*EPS for k in ('first_monopole','second_monopole','quadrupole')) and metrics['source_direction_tangent']<=512*EPS
  checks.append(dict(shear=label,v=v,S2=S2,normalized_metrics=metrics,pass_all=passed))
  np.savez(out/f'ANALYTIC_{label}.npz',**a,B=B,mean_u1=mean1,mean_u2_rule=mean2,mean_u2_closed=m2,monopole_coefficient_per_S2=m2/S2,quadrupole=quad,quadrupole_closed=qexpected,source_direction_dot=tangentdot,source_direction_gross=tangentgross)
  results[label]=dict(mean2=m2,B=B,a=a,v=v)
  save(out/'ANALYTIC_CHECKS.json',checks)
  if not passed:raise ValueError('ANALYTIC_MOMENT_GATE:'+label)
 return results,ns,ww

def finite(c,L,x,g,h,ns,ww,out,counter):
 v=np.array([1.,-.5,-.5]);means=[];allraw=[];summaries=[];baseline=c['stored_incoming'];W=np.exp(-x)
 # Explicit baseline branch guarantees exact stored incoming, without a subtraction.
 zero=np.array([geo.increment(float(gg),float(xx),0.) for gg,xx in zip(g,x)])
 if not np.array_equal(baseline+zero,baseline):raise ValueError('EXACT_ANCHORED_BASELINE')
 for p in (h,-h,h/2,-h/2):
  delta=np.full((313,14),np.nan);du=np.full_like(delta,np.nan);iterations=np.full_like(delta,-1,dtype=int);residual=np.full_like(delta,np.nan)
  for j in range(313):
   for ray,n in enumerate(ns):
    counter.root()
    try:
     d,it,res=geo.root(float(L[j]),float(p),v,n*n)
     delta[j,ray]=d;iterations[j,ray]=it;residual[j,ray]=res
     if not c['intersection_lower_inner'][j]<d<c['intersection_upper_inner'][j] or abs(d)>=c['safe_radius'][j]:raise ValueError('SAMPLED_FIXED_CELL_CONTAINMENT')
     bound=L[j]*abs(p)/(1-abs(p))
     if abs(d)>bound*(1+16*EPS):raise ValueError('SAMPLED_UNIFORM_SHIFT_BOUND')
     du[j,ray]=geo.increment(float(g[j]),float(x[j]),d)
    except BaseException:
     np.savez(out/'FINITE_FAILED_COMPLETED_PREFIX.npz',lambda_value=p,query=j,ray=ray,delta_query=delta,incoming_increment=du,iterations=iterations,residual_normalized=residual)
     raise
  mean=du@ww;means.append(mean);allraw.append(du)
  total=baseline[:,None]+W[:,None]+du;anchored=baseline[:,None]+du
  np.savez(out/f'FINITE_{len(means)}.npz',lambda_value=p,delta_query=delta,incoming_increment=du,mean_increment=mean,total_occupation=total,anchored_departure=anchored,iterations=iterations,residual_normalized=residual)
  row=dict(step=float(p),root_count=313*14,max_iterations=int(iterations.max()),max_root_normalized_residual=float(residual.max()),root_tolerance=256*EPS,min_total_occupation=float(total.min()),negative_total_count=int(np.count_nonzero(total<0)),min_anchored_departure=float(anchored.min()),negative_anchored_departure_count=int(np.count_nonzero(anchored<0)),max_shift_fraction_of_margin=float(np.max(abs(delta)/c['safe_radius'][:,None])),positive_directional_rates=bool(np.all(1+p*v>0)))
  summaries.append(row);save(out/'FINITE_SUMMARY.json',summaries);counter.persist('FINITE_STEP_'+str(p))
  if row['negative_total_count'] or np.any(baseline+W<0):raise ValueError('SAMPLED_TOTAL_OCCUPATION_DOMAIN_FINDING')
 means=np.array(means);du=np.array(allraw)
 np.savez(out/'FINITE_DIAGNOSTICS.npz',steps=np.array([h,-h,h/2,-h/2]),mean_increments=means,mean_first_h=(means[0]-means[1])/(2*h),mean_second_h=(means[0]+means[1])/(h*h),mean_first_half=(means[2]-means[3])/h,mean_second_half=(means[2]+means[3])/((h/2)**2),directional_first_h=(du[0]-du[1])/(2*h),directional_second_h=(du[0]+du[1])/(h*h),directional_first_half=(du[2]-du[3])/h,directional_second_half=(du[2]+du[3])/((h/2)**2))
 return means

def outward(x):
 a=float(x);b=F(a)
 if b==x:return [a,a]
 return [a,float(np.nextafter(a,np.inf))] if b<x else [float(np.nextafter(a,-np.inf)),a]

def compose(K,ki,m2,means,meta,out,counter):
 o2=counter.apply(K,m2,'ANALYTIC_SECOND_MEAN');of=np.array([counter.apply(K,row,'FINITE_MEAN_'+str(i)) for i,row in enumerate(means)])
 factor=3e6*LYA*meta['H_sInv'];number=factor*(o2[311]-m2[311]);rad=E21*EV_J*number;atomic=-rad
 # Elementwise coefficient identity check uses the saved KS event row; no action.
 event=load('KS_EVENT_RESPONSE.npz',('number_hat',))['number_hat'];inc=np.zeros(313);inc[311]=1
 expected=factor*(K[311]-inc)
 if not np.array_equal(event,expected):raise ValueError('SAME_SOURCE_EVENT_COEFFICIENT_IDENTITY')
 counter.interval_action();vf=[F(float(a)) for a in m2];lower=[];upper=[];flo=[];fhi=[]
 for rowlo,rowhi in zip(ki['Klo'],ki['Khi']):
  lo=sum((F(float(a if v>=0 else b))*v for a,b,v in zip(rowlo,rowhi,vf)),F(0))
  hi=sum((F(float(b if v>=0 else a))*v for a,b,v in zip(rowlo,rowhi,vf)),F(0))
  lower.append(str(lo));upper.append(str(hi));flo.append(outward(lo)[0]);fhi.append(outward(hi)[1])
 save(out/'EXACT_INTERVAL_ACTION.json',dict(scope='Exact Fraction action on represented binary64 analytic mean_u_second only; excludes coefficient/libm/physical uncertainty',lower_exact=lower,upper_exact=upper,lower_outward=flo,upper_outward=fhi))
 np.savez(out/'SCALAR_COMPOSITION.npz',incoming_mean_second=m2,outgoing_mean_second=o2,finite_outgoing_mean_increments=of,interval_lo=np.array(flo),interval_hi=np.array(fhi),number_second=number,radiation_energy_second=rad,atomic_energy_second=atomic)
 row=dict(status='PASS',operator_actions=counter.matvecs,exact_interval_actions=counter.interval,number_second=float(number),radiation_energy_second=float(rad),atomic_energy_second=float(atomic),radiation_atomic_exact_negative=bool(atomic==-rad),direct_incoming_subtraction=True,event_coefficient_identity='EXACT_BINARY64_SAVED_ROW',number_units='m^-3 s^-1 per lambda^2',energy_units='J m^-3 s^-1 per lambda^2',outgoing_units='occupation per lambda^2',physical_epsilon=None,physical_outgoing_bound=None)
 save(out/'SCALAR_COMPOSITION.json',row);return row

def run(out,counter):
 before=source_snapshot();save(out/'SOURCE_SNAPSHOT_BEFORE.json',before)
 save(out/'CHILD_LIMITS.json',dict(cpu=resource.getrlimit(resource.RLIMIT_CPU),address_space=resource.getrlimit(resource.RLIMIT_AS),thread_environment={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')},numpy_version=np.__version__,observed_runtime_model=None))
 c,K,ki,meta,L,x,g,h=admission(out);guardcount=guards(out);analyticdata,ns,ww=analytic(L,x,g,out);means=finite(c,L,x,g,h,ns,ww,out,counter)
 oracle=decimal_oracle.run(L,x,g,h,out,counter);composition=compose(K,ki,analyticdata['v1']['mean2'],means,meta,out,counter)
 after=source_snapshot();save(out/'SOURCE_SNAPSHOT_AFTER.json',after)
 if after!=before:raise ValueError('SOURCE_CHANGED_DURING_RUN')
 counter.persist('COMPLETE')
 save(out/'SUMMARY.json',dict(status='PASS_CONTROLLED_PROPAGATION_PARTIAL',source_identity_pass=True,guard_controls=guardcount,exact_sphere_monomials=35,analytic_shears=2,ordinary_roots=counter.roots,decimal_roots=counter.decimal_roots,operator_actions=counter.matvecs,interval_actions=counter.interval,h=h,decimal=oracle,composition=composition,new_RHS=0,solves=0,IVP=0,global_convergence='NOT_RUN',physical_state='HOLD',parent_REC_HISTORY='PARTIAL',H5_physical_epsilon=None,H6_physical_trace='OPEN',H7_total_coupled='OPEN',production='NOT_APPROVED',runtime_model_observed=None))

if __name__=='__main__':
 out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);counter=Counter(out)
 try:run(out,counter)
 except BaseException as exc:
  counter.persist('FAILED_COMPLETED_PREFIX_PRESERVED');save(out/'FAILURE.json',dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),scientific_outcome='FAILED_OR_INCOMPLETE_FROZEN_CRITERION',preserved_completed_prefix=True));raise
