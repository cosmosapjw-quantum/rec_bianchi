"""Native-order stencils, exact anchored constants and sparse coordinate map."""
from fractions import Fraction as F
import math
import numpy as np
from common import save
import history_boundary as native
import interval as iv

def frac(x):return F(float(x))
def enclosure(x):
 v=float(x)
 if not math.isfinite(v):raise ValueError('RATIONAL_TO_FLOAT_OVERFLOW')
 f=frac(v)
 return (v,v) if f==x else ((v,float(np.nextafter(v,np.inf))) if f<x else (float(np.nextafter(v,-np.inf)),v))
def upper(x):return enclosure(x)[1]
def lower(x):return enclosure(x)[0]
def rational_array(values):
 pairs=[enclosure(x) for x in values];return np.array([x[0] for x in pairs]),np.array([x[1] for x in pairs])
def metric(a,b):
 a=np.asarray(a);b=np.asarray(b);err=float(np.max(np.abs(a-b)));scale=max(float(np.max(np.abs(a))),float(np.max(np.abs(b))),1e-280)
 return {'absolute_error':err,'scale':scale,'normalized_error':err/scale}

def require_shapes(source,prefix,history,q):
 if prefix!=5127:raise ValueError('WRONG_PREFIX_OWNER')
 if np.asarray(source).shape!=(313,) or not np.array_equal(np.sort(source),np.arange(1,314)):raise ValueError('WRONG_SOURCE_ROUTE')
 if history.shape[0]!=314 or history.shape[1]<prefix or np.asarray(q).shape!=(313,):raise ValueError('HISTORY_OR_QUERY_SHAPE')
 if not np.all(np.isfinite(history[:,:prefix])) or not np.all(np.isfinite(q)):raise ValueError('NONFINITE_HISTORY_OR_QUERY')

def gather(data,accepted,out):
 eta=data['eta'];h=float(data['dlna']);eta0=float(eta[0]);history=np.vstack((data['outgoing_virtual'],data['outgoing_lyman']));energy=data['energy_eV']
 source,targets,sources=native.native_links(energy);q=np.array([r['eta_emit'] for r in accepted['records']]);prefix=5127
 require_shapes(source,prefix,history,q)
 a=[];yl=[];yr=[];g=[];lo=[];hi=[];safe=[];stencils=[];witness=[];slots=[]
 for j,(r,s) in enumerate(zip(accepted['records'],source)):
  if r['incoming_index']!=j or r['source_index']!=s:raise ValueError('ACCEPTED_QUERY_OWNER_MISMATCH')
  expected=-math.log((1+1099.9986525171403)*float(sources[j])/float(targets[j]))
  if frac(expected)!=frac(q[j]):raise ValueError('QUERY_CLOCK_IDENTITY')
  st=native.interpolation(eta0,h,history[s],prefix,q[j])
  if st['thermal'] or st['k']!=r['cell']:raise ValueError('ACCEPTED_CELL_OR_PREFIX_MISMATCH')
  k=st['k'];aa=st['alpha'];left=float(history[s,k]);right=float(history[s,k+1]);gg=(frac(right)-frac(left))/frac(h)
  # Exact rational intersections of native chart, stored-knot, native-knot,
  # global retained-prefix limits. Values are represented constants.
  l=max(-frac(h)*frac(aa),frac(eta[k])-frac(q[j]),frac(eta0+h*k)-frac(q[j]),frac(eta0)-frac(q[j]))
  u=min(frac(h)*(1-frac(aa)),frac(eta[k+1])-frac(q[j]),frac(eta0+h*(k+1))-frac(q[j]),frac(eta0+h*(prefix-1))-frac(q[j]))
  if st['at_knot']:raise ValueError('ACTUAL_QUERY_IS_NONSMOOTH_RETURN_TO_ROOT')
  radius=min(-l,u)
  if not l<0<u or radius<=0:raise ValueError('NO_FIXED_CELL_INTERIOR')
  rad=lower(radius)
  if rad<=0:raise ValueError('UNREPRESENTABLE_INTERIOR_RADIUS')
  a.append(aa);yl.append(left);yr.append(right);g.append(gg);lo.append(l);hi.append(u);safe.append(rad);stencils.append(st);slots.extend([(int(s),k),(int(s),k+1)])
  row={'incoming_index':j,'source_index':int(s),'cell':k,'native_fraction':aa,'KS_saved_eta_fraction':r['weight'],'alpha_difference':aa-r['weight'],'native_base':st['value'],'KS_base':r['reconstructed'],'stored_base':r['stored'],'left_sample':left,'right_sample':right,'slope_exact':str(gg),'slope_enclosure':enclosure(gg),'stored_left_margin':r['left_margin'],'stored_right_margin':r['right_margin'],'strict_prefix_margin':r['upper_domain_margin'],'intersection_lower_exact':str(l),'intersection_upper_exact':str(u),'intersection_lower_enclosure':enclosure(l),'intersection_upper_enclosure':enclosure(u),'safe_radius':rad,'at_knot':st['at_knot']}
  save(out/'source_rows'/f'ROW_{j:03d}.json',row);witness.append(row)
 if len(set(slots))!=626:raise ValueError('ACTIVE_ENDPOINT_SUPPORT_NOT_DISJOINT')
 a=np.array(a);yl=np.array(yl);yr=np.array(yr);safe=np.array(safe);glo,ghi=rational_array(g);ghat=np.array([float(x) for x in g])
 P=np.zeros((313,626));P[np.arange(313),2*np.arange(313)]=1-a;P[np.arange(313),2*np.arange(313)+1]=a
 native_base=np.array([s['value'] for s in stencils]);stored=np.array([r['stored'] for r in accepted['records']]);ksbase=np.array([r['reconstructed'] for r in accepted['records']])
 checks={'native_reconstruction':metric(native_base,stored),'KS_reconstruction':metric(ksbase,stored),'source_permutation':True,'active_slot_count':626,'active_slots_distinct':True,'cells_equal_accepted':True,'all_inside_prefix':True,'base_fraction_comparison':'different binary64 operation order recorded; no identity assertion'}
 for key in ('native_reconstruction','KS_reconstruction'):
  if checks[key]['normalized_error']>5e-9:raise ValueError('BASE_RECONSTRUCTION_FAILED:'+key)
 save(out/'SOURCE_ADMISSION.json',checks);save(out/'QUERY_WITNESSES.json',witness)
 np.savez(out/'NATIVE_CHART_CONSTANTS.npz',source=source,query=q,alpha=a,left=yl,right=yr,slope_hat=ghat,slope_lo=glo,slope_hi=ghi,safe_radius=safe,intersection_lower_inner=np.array([upper(v) for v in lo]),intersection_upper_inner=np.array([lower(v) for v in hi]),P_hat=P,stored_incoming=stored,native_incoming=native_base,KS_incoming=ksbase,active_slots=np.asarray(slots))
 return dict(history=history,eta=eta,eta0=eta0,h=h,prefix=prefix,source=source,q=q,a=a,yl=yl,yr=yr,g=g,ghat=ghat,glo=glo,ghi=ghi,lower=lo,upper=hi,safe=safe,stencils=stencils,P=P,stored=stored,native_base=native_base,witness=witness,checks=checks)

def validate_shift(c,j,qprime,xi_exact):
 if not c['lower'][j]<xi_exact<c['upper'][j]:raise ValueError('QUERY_SHIFT_OUTSIDE_FIXED_STENCIL')
 st=native.interpolation(c['eta0'],c['h'],c['history'][c['source'][j]],c['prefix'],qprime)
 if st['k']!=c['stencils'][j]['k'] or st['thermal']:raise ValueError('QUERY_CELL_CROSSING')
 return st

def sparse_jvp(c,dy,xi):
 if np.shape(dy)!=(626,) or np.shape(xi)!=(313,) or not np.all(np.isfinite(dy)) or not np.all(np.isfinite(xi)):raise ValueError('TANGENT_SHAPE_OR_NONFINITE')
 return (1-c['a'])*dy[::2]+c['a']*dy[1::2]+c['ghat']*xi

def sparse_vjp(c,v):
 out=np.zeros(626);out[::2]=(1-c['a'])*v;out[1::2]=c['a']*v
 return out,c['ghat']*v

def conditional_box(Kinterval,c,eL=None,eR=None,tau=None):
 if eL is None or eR is None or tau is None:return {'status':'INPUT_DEPENDENT_UNCALIBRATED','physical_bound':None,'physical_epsilon':None}
 n=len(c['a'])
 for a in (eL,eR,tau):
  if np.shape(a)!=(n,) or not np.all(np.isfinite(a)) or np.any(np.asarray(a)<0):raise ValueError('INVALID_CONDITIONAL_RADII')
 for j,t in enumerate(tau):
  if frac(t)>=min(-c['lower'][j],c['upper'][j]):raise ValueError('BOX_CROSSES_FIXED_CELL')
 a=iv.point(c['a']);one_minus=iv.sub(iv.point(np.ones(n)),a);h=iv.point(c['h'])
 abs_g=iv.abs_bounds((c['glo'],c['ghi']));ta=iv.point(np.asarray(tau));el=iv.point(np.asarray(eL));er=iv.point(np.asarray(eR))
 first=iv.add(iv.mul(one_minus,el),iv.mul(a,er));linear=iv.add(first,iv.mul(abs_g,ta))
 ratio=(iv.down(np.asarray(tau)/c['h']),iv.up(np.asarray(tau)/c['h']))
 remainder=iv.mul(ratio,iv.add(el,er));b=iv.add(linear,remainder)
 W=iv.abs_bounds(Kinterval)[1];product=iv.point_dot(W,b[1][:,None]);bound=np.maximum(0,product[1][:,0])
 return {'status':'CONDITIONAL_NUMERICAL_BOX_ONLY','physical_bound':None,'physical_epsilon':None,'bound':bound,'incoming_bound':b[1],'linear_bound':linear[1],'mixed_bound':remainder[1]}
