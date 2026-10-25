"""PB01 single bounded actual-data pullback; zero source rebuild/solve/RHS."""
import argparse,json,math,os,resource,sys,traceback
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from common import UNIT,save,paths,verify,Counter
from chart import frac,upper,metric,gather,validate_shift,sparse_jvp,sparse_vjp,conditional_box,require_shapes
from composition import compose
import history_boundary as native
import interval as iv
EPS=np.finfo(float).eps

def load_npz(path,keys=None):
 with np.load(path,allow_pickle=False) as z:return {k:z[k].copy() for k in (z.files if keys is None else keys)}

def derivative_checks(c,K,op,directions,out,counter):
 rows=[];raw={};covectors=[(-1.)**np.arange(314),np.cos(np.arange(314)+1.)+.1*np.sin(2*np.arange(314)+1.)]
 for i,(dy,xi) in enumerate(directions):
  counter.charge('SPARSE_HISTORY_JVP_'+str(i))
  sparse=sparse_jvp(c,dy,xi);direct=counter.apply('EXPLICIT_P_ACTION_'+str(i),c['P'],dy)+c['ghat']*xi
  sj=counter.apply('K_SPARSE_JVP_'+str(i),K,sparse)
  dense=counter.apply('EXPLICIT_A_ACTION_'+str(i),op['A'],dy)+counter.apply('EXPLICIT_C_ACTION_'+str(i),op['C'],xi)
  counter.charge('REUSED_NATIVE_HISTORY_JVP_'+str(i))
  native_jvp=[]
  for j,st in enumerate(c['stencils']):
   dv=np.zeros(st['k']+2);dv[st['k']]=dy[2*j];dv[st['k']+1]=dy[2*j+1];native_jvp.append(native.interpolation_jvp(st,dv,xi[j]))
  nj=np.array(native_jvp)
  comparisons={'sparse_vs_explicit_history':metric(sparse,direct),'sparse_vs_native_JVP':metric(sparse,nj),'sparse_vs_explicit_outgoing':metric(sj,dense)}
  for key,m in comparisons.items():m['pass']=m['normalized_error']<=2e-12
  pairings=[]
  for widx,w in enumerate(covectors):
   v=counter.apply(f'K_TRANSPOSE_{i}_{widx}',K.T,w);counter.charge(f'SPARSE_COORDINATE_VJP_{i}_{widx}');ey,qy=sparse_vjp(c,v)
   exey=counter.apply(f'EXPLICIT_A_TRANSPOSE_{i}_{widx}',op['A'].T,w);exqy=counter.apply(f'EXPLICIT_C_TRANSPOSE_{i}_{widx}',op['C'].T,w)
   mv=metric(np.r_[ey,qy],np.r_[exey,exqy]);mv['pass']=mv['normalized_error']<=2e-12
   counter.charge(f'COORDINATE_PAIRING_{i}_{widx}');lt=w*sj;rt1=ey*dy;rt2=qy*xi;lhs=float(np.sum(lt));rhs=float(np.sum(rt1)+np.sum(rt2));gross=float(np.sum(np.abs(lt))+np.sum(np.abs(rt1))+np.sum(np.abs(rt2)));den=max(gross,1e-280)
   zero=bool(np.all(lt==0) and np.all(rt1==0) and np.all(rt2==0));okay=abs(lhs-rhs)/den<=2e-12 and (not zero or lhs==rhs==0.)
   row={'covector':widx+1,'lhs':lhs,'rhs':rhs,'absolute_error':abs(lhs-rhs),'denominator_sumabs_both_sides':den,'normalized_error':abs(lhs-rhs)/den,'exact_zero_terms':zero,'pass':okay,'VJP_explicit_comparison':mv};pairings.append(row)
   raw[f'd{i+1}_w{widx+1}_endpoint_vjp']=ey;raw[f'd{i+1}_w{widx+1}_query_vjp']=qy
  rows.append({'direction':i+1,'comparisons':comparisons,'pairings':pairings,'pass':all(x['pass'] for x in comparisons.values()) and all(x['pass'] and x['VJP_explicit_comparison']['pass'] for x in pairings)})
  save(out/f'DERIVATIVE_DIRECTION_{i+1}.json',rows[-1]);save(out/'DERIVATIVE_ADJOINT_CHECKS.json',rows)
  raw[f'd{i+1}_endpoint_direction']=dy;raw[f'd{i+1}_query_direction']=xi;raw[f'd{i+1}_history_jvp']=sparse;raw[f'd{i+1}_outgoing_jvp']=sj
 np.savez(out/'DERIVATIVE_ADJOINT_ARRAYS.npz',**raw)
 return rows

def finite_case(c,K,Kint,op,dy_req,xi_req,direction,t,out,counter,U):
 tag=f'd{direction}_t{t:g}';requestedL=dy_req[::2]*t;requestedR=dy_req[1::2]*t;requestedXi=xi_req*t
 newL=c['yl']+requestedL;newR=c['yr']+requestedR;qprime=c['q']+requestedXi
 n=313;delta=[];tangent=[];rem=[];bridge=[];dyF=[];xiF=[];ea=[];nativeprime=[];nativealphaprime=[];exact_records=[]
 # Requested and actually rounded input coordinates are retained before case work.
 np.savez(out/f'CASE_{tag}_INPUTS.npz',requested_left=requestedL,requested_right=requestedR,requested_query=requestedXi,new_left=newL,new_right=newR,new_query=qprime,base_left=c['yl'],base_right=c['yr'],base_query=c['q'])
 for j in range(n):
  dl=frac(newL[j])-frac(c['yl'][j]);dr=frac(newR[j])-frac(c['yr'][j]);x=frac(qprime[j])-frac(c['q'][j]);validate_shift(c,j,qprime[j],x)
  y=c['history'][c['source'][j],:c['prefix']].copy();k=c['stencils'][j]['k'];y[k]=newL[j];y[k+1]=newR[j]
  native_new=native.interpolation(c['eta0'],c['h'],y,c['prefix'],qprime[j]);a=frac(c['a'][j]);h=frac(c['h']);l=frac(c['yl'][j]);r=frac(c['yr'][j])
  d=(1-a-x/h)*(l+dl)+(a+x/h)*(r+dr)-((1-a)*l+a*r)
  lin=(1-a)*dl+a*dr+c['g'][j]*x;rr=x/h*(dr-dl);aa=frac(native_new['alpha'])-a-x/h;br=aa*(frac(newR[j])-frac(newL[j]))
  native_exact=(1-frac(native_new['alpha']))*frac(newL[j])+frac(native_new['alpha'])*frac(newR[j])-((1-a)*l+a*r)
  if d!=lin+rr or native_exact!=d+br:raise AssertionError('EXACT_ANCHORED_REMAINDER_OR_BRIDGE_IDENTITY')
  delta.append(d);tangent.append(lin);rem.append(rr);bridge.append(br);dyF.extend((dl,dr));xiF.append(x);ea.append(aa);nativeprime.append(native_new['value']);nativealphaprime.append(native_new['alpha'])
  exact_records.append({'row':j,'actual_dy_left':str(dl),'actual_dy_right':str(dr),'actual_query_shift':str(x),'delta_alpha_exact':str(aa),'chart_delta_exact':str(d),'tangent_exact':str(lin),'mixed_remainder_exact':str(rr),'native_fraction_bridge_exact':str(br)})
 save(out/f'CASE_{tag}_EXACT.json',{'status':'EXACT_RATIONAL_IDENTITIES_PASS','records':exact_records})
 df=np.array(list(map(float,delta)));tf=np.array(list(map(float,tangent)));rf=np.array(list(map(float,rem)));bf=np.array(list(map(float,bridge)));actualdy=np.array(list(map(float,dyF)));actualxi=np.array(list(map(float,xiF)));nativeprime=np.array(nativeprime);native_delta=nativeprime-c['native_base']
 # The bridge-corrected interpolation residual uses the frozen base incoming scale.
 bridge_residual=native_delta-(df+bf);bridge_error=float(np.max(np.abs(bridge_residual)));normscale=max(U,float(np.max(np.abs(df))),float(np.max(np.abs(native_delta))),1e-280)
 chartout=counter.apply('CHART_FORWARD_'+tag,K,df);nativeout=counter.apply('NATIVE_BRIDGE_FORWARD_'+tag,K,native_delta);tangentout=counter.apply('TANGENT_FORWARD_'+tag,K,tf);remainderout=counter.apply('REMAINDER_FORWARD_'+tag,K,rf);bridgeout=counter.apply('ARITHMETIC_BRIDGE_FORWARD_'+tag,K,bf)
 observed=nativeout-tangentout-bridgeout
 floorin=512*EPS*(np.abs(nativeprime)+np.abs(c['native_base'])+np.abs(tf)+np.abs(rf)+np.abs(bf)+U)
 floorout=counter.apply('ARITHMETIC_FLOOR_DIAGNOSTIC_'+tag,np.abs(K),floorin)+512*EPS*(np.abs(nativeout)+np.abs(tangentout)+np.abs(bridgeout))
 floor=float(np.max(floorout));rema=float(np.max(np.abs(observed)));nonfloor=rema>100*floor
 # Supplied numerical radii enclose exact actual differences, never physical errors.
 eL=np.array([upper(abs(dyF[2*j])) for j in range(n)]);eR=np.array([upper(abs(dyF[2*j+1])) for j in range(n)]);tau=np.array([upper(abs(x)) for x in xiF])
 counter.interval('FINITE_BOX_'+tag);box=conditional_box(Kint,c,eL,eR,tau)
 chart_contained=bool(np.all(np.abs(chartout)<=box['bound']));native_contained=bool(np.all(np.abs(nativeout)<=box['bound']))
 eventfinite=counter.apply('EVENT_CHART_FORWARD_'+tag,op['events'],df,event=True);eventtangent=counter.apply('EVENT_TANGENT_'+tag,op['events'],tf,event=True);eventrem=counter.apply('EVENT_REMAINDER_'+tag,op['events'],rf,event=True)
 eventdirect=counter.apply('EVENT_ENDPOINT_ACTION_'+tag,op['event_endpoint'],actualdy,event=True)+counter.apply('EVENT_QUERY_ACTION_'+tag,op['event_query'],actualxi,event=True)
 eventmetric={key:metric(eventtangent[i],eventdirect[i]) for i,key in enumerate(('F','proper','number','radiation','atomic'))}
 # Atomic/radiation diagnostic actions use shared event arrays; retain signed zero.
 event_sign=bool(eventfinite[4]==-eventfinite[3] and eventtangent[4]==-eventtangent[3] and eventrem[4]==-eventrem[3])
 save(out/f'CASE_{tag}_BOX.json',box)
 np.savez(out/f'CASE_{tag}_OUTPUTS.npz',actual_endpoint_increment=actualdy,actual_query_shift=actualxi,actual_native_alpha=np.array(nativealphaprime),delta_alpha=np.array(list(map(float,ea))),chart_delta=df,tangent=tf,mixed_remainder=rf,arithmetic_bridge=bf,native_interpolation=nativeprime,native_delta=native_delta,bridge_corrected_residual=bridge_residual,connected_incoming=c['stored']+df,chart_outgoing_increment=chartout,native_outgoing_increment=nativeout,outgoing_tangent=tangentout,outgoing_remainder=remainderout,outgoing_bridge=bridgeout,observed_taylor_remainder=observed,arithmetic_floor=floorout,event_finite=eventfinite,event_tangent=eventtangent,event_remainder=eventrem,event_explicit_tangent=eventdirect)
 row={'direction':direction,'t':t,'exact_fraction_identity':'PASS','bridge_corrected_absolute_error':bridge_error,'bridge_normalization':normscale,'bridge_corrected_normalized_error':bridge_error/normscale,'bridge_pass':bridge_error/normscale<=5e-12,'outgoing_remainder_norm':rema,'arithmetic_floor':floor,'above100_floor':nonfloor,'max_exact_chart_remainder':float(max(map(abs,rem))),'chart_finite_box_contained':chart_contained,'native_numerical_probe_box_contained':native_contained,'event_explicit_tangent':eventmetric,'event_sign_pair':event_sign,'physical_epsilon':None,'physical_bound':None}
 row['pass']=row['bridge_pass'] and chart_contained and native_contained and event_sign and all(m['normalized_error']<=2e-12 for m in eventmetric.values())
 save(out/f'CASE_{tag}_SUMMARY.json',row);return row

def domain_controls(c,Kint,out,counter):
 refused=[]
 def no(name,fn):
  try:fn()
  except ValueError:refused.append(name)
  else:raise AssertionError('EXPECTED_REFUSAL:'+name)
 bad=c['source'].copy();bad[0]=bad[1]
 no('wrong_source',lambda:require_shapes(bad,c['prefix'],c['history'],c['q']))
 no('wrong_prefix',lambda:require_shapes(c['source'],5126,c['history'],c['q']))
 no('wrong_shape',lambda:require_shapes(c['source'],c['prefix'],c['history'][:313],c['q']))
 no('nonfinite_tangent',lambda:sparse_jvp(c,np.full(626,np.nan),np.zeros(313)))
 no('cell_crossing',lambda:validate_shift(c,0,float(c['q'][0]+2*c['safe'][0]+c['h']),frac(2*c['safe'][0]+c['h'])))
 no('strict_prefix_endpoint',lambda:native.interpolation(c['eta0'],c['h'],c['history'][c['source'][0]],c['prefix'],c['eta0']+c['h']*(c['prefix']-1)))
 zero=np.zeros(313)
 no('negative_box_radius',lambda:conditional_box(Kint,c,-np.ones(313),zero,zero))
 no('nonfinite_box_radius',lambda:conditional_box(Kint,c,np.full(313,np.inf),zero,zero))
 no('box_crosses_cell',lambda:conditional_box(Kint,c,zero,zero,np.ones(313)))
 save(out/'ACTUAL_DOMAIN_REFUSALS.json',{'status':'PASS','refused':refused,'physical_fields':conditional_box(Kint,c)})
 return refused

def run(out):
 counter=Counter(out)
 save(out/'CHILD_RESOURCE_LIMITS.json',{'RLIMIT_CPU':resource.getrlimit(resource.RLIMIT_CPU),'RLIMIT_AS':resource.getrlimit(resource.RLIMIT_AS),'RLIMIT_CORE':resource.getrlimit(resource.RLIMIT_CORE),'thread_environment':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS')},'numpy_version':np.__version__})
 before=verify();save(out/'INPUT_IDENTITIES_BEFORE.json',before);p=paths()
 history=load_npz(p['history'],('eta','dlna','energy_eV','outgoing_virtual','outgoing_lyman'));accepted=json.loads(p['accepted_queries'].read_text());c=gather(history,accepted,out)
 K=load_npz(p['point_K'],('Khat',))['Khat'];ki=load_npz(p['K_intervals'],('Klo','Khi'));Kint=(ki['Klo'],ki['Khi']);certificate=json.loads(p['K_certificate'].read_text());events=load_npz(p['event_rows'])
 if K.shape!=(314,313) or ki['Klo'].shape!=K.shape or ki['Khi'].shape!=K.shape:raise ValueError('K_SHAPE')
 iv.valid(Kint);iv.finite(K)
 op=compose(c,K,Kint,certificate,events,out,counter)
 U=max(float(np.max(np.abs(c['stored']))),float(np.max(np.abs(c['native_base']))),1e-280);e=.01*U;j=np.arange(313)
 directions=[(np.ravel(np.column_stack((np.full(313,e),np.full(313,-e)))),.2*c['safe']),(np.ravel(np.column_stack((e*np.cos(j+1.),e*np.sin(2*j+1.)))),.2*c['safe']*np.cos(j+1.))]
 save(out/'FROZEN_PROBE_SCALES.json',{'U':U,'endpoint_e':e,'t':[1.,.5,.25,.125],'physical_radii':False,'formula':'contract directions; safe intersection radius; numerical controls only'})
 dchecks=derivative_checks(c,K,op,directions,out,counter);cases=[]
 for i,(dy,xi) in enumerate(directions):
  for t in (1.,.5,.25,.125):
   cases.append(finite_case(c,K,Kint,op,dy,xi,i+1,t,out,counter,U));save(out/'FINITE_CASES.json',cases)
 orders=[]
 for direction in (1,2):
  rows=[r for r in cases if r['direction']==direction]
  for a,b in zip(rows,rows[1:]):
   above=a['above100_floor'] and b['above100_floor'];order=math.log2(a['outgoing_remainder_norm']/b['outgoing_remainder_norm']) if above else None
   orders.append({'direction':direction,'from_t':a['t'],'to_t':b['t'],'above100_floor':above,'order':order,'pass':None if not above else 1.9<=order<=2.1,'interpretation':'fixed local Taylor control; not global convergence'})
 save(out/'TAYLOR_ORDERS.json',orders)
 sys.path.insert(0,str(UNIT/'tests'));from exact_controls import run as exact_run
 toys=exact_run(out,counter);domain_controls(c,Kint,out,counter)
 after=verify();save(out/'INPUT_IDENTITIES_AFTER.json',after)
 summary={'status':'PENDING_CRITERIA','identity_pass':before==after,'source_route_permutation':True,'active_endpoint_slots':626,'derivative_adjoint_pass':all(r['pass'] for r in dchecks),'finite_bridge_box_event_pass':all(r['pass'] for r in cases),'query_interval_pass':op['query_norm']['pass_width'],'endpoint_norm_interval':[certificate['norm_lower'],certificate['norm_upper']],'query_norm_interval':[op['query_norm']['lower'],op['query_norm']['upper']],'query_norm_relative_width':op['query_norm']['relative_width'],'exact_toy_controls':toys['status'],'taylor_nonfloor_ratios':{str(d):sum(r['above100_floor'] for r in orders if r['direction']==d) for d in (1,2)},'taylor_nonfloor_orders_pass':all(r['pass'] for r in orders if r['above100_floor']),'event_sign_pair':op['event_sign'],'operator_actions':counter.operator_actions,'event_actions':counter.event_actions,'interval_passes':counter.interval_passes,'new_RHS':0,'solves':0,'inverses':0,'source_coefficients_rebuilt':False,'physical_epsilon':None,'physical_outgoing_bound':None,'requested_model':'gpt-6.1-sol','observed_model':None}
 summary['status']='PASS' if all([summary['identity_pass'],summary['derivative_adjoint_pass'],summary['finite_bridge_box_event_pass'],summary['query_interval_pass'],summary['taylor_nonfloor_orders_pass'],max(summary['taylor_nonfloor_ratios'].values())>=2,summary['event_sign_pair'],toys['status']=='PASS']) else 'FAILED_FROZEN_CRITERION'
 counter.persist('COMPLETE');save(out/'SUMMARY.json',summary);return summary

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 try:
  summary=run(a.out);print(json.dumps(summary,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)));return 0 if summary['status']=='PASS' else 2
 except BaseException as e:
  save(a.out/'EXCEPTION.json',{'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'raw_partial_preserved':True});traceback.print_exc();return 1
if __name__=='__main__':sys.exit(main())
