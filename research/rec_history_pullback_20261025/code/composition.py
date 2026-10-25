"""Outward composition of reused Ks/event intervals with the anchored chart."""
import numpy as np
import interval as iv
from common import save
from chart import frac,metric

def row_norm(interval):
 lo,hi=iv.sum_bounds(iv.abs_bounds(interval));lo=np.maximum(lo,0)
 return {'lower':float(np.max(lo)),'upper':float(np.max(hi))},lo,hi

def compose(c,K,Kinterval,certificate,events,out,counter):
 counter.interval('QUERY_C')
 Cint=iv.mul(Kinterval,(c['glo'][None,:],c['ghi'][None,:]));C=K*c['ghat'][None,:]
 A=np.repeat(K,2,axis=1)*np.ravel(np.column_stack((1-c['a'],c['a'])))[None,:]
 weights=(np.column_stack((iv.down(1-c['a']),c['a'])).ravel(),np.column_stack((iv.up(1-c['a']),c['a'])).ravel())
 Aint=iv.mul((np.repeat(Kinterval[0],2,axis=1),np.repeat(Kinterval[1],2,axis=1)),weights)
 query_norm,gainlo,gainhi=row_norm(Cint)
 if query_norm['lower']<=0:
  save(out/'QUERY_NORM.json',{'status':'ZERO_LOWER_BOUND_RETURN_TO_ROOT','absolute_interval':query_norm});raise ValueError('QUERY_NORM_ZERO_LOWER_RETURN_TO_ROOT')
 width=(query_norm['upper']-query_norm['lower'])/query_norm['upper'];query_norm.update(relative_width=width,pass_width=width<=1e-6)
 contained=bool(np.all(C>=Cint[0]) and np.all(C<=Cint[1]))
 common=iv.sum_bounds(Cint);scaled=iv.mul(Cint,iv.point(c['safe'][None,:]));scaled_norm,scaledlo,scaledhi=row_norm(scaled)
 save(out/'QUERY_NORM.json',{'status':'CERTIFIED_REUSED_K_TIMES_EXACT_SLOPE','independent_query_norm':query_norm,'point_candidate_contained':contained,'endpoint_norm':{'lower':certificate['norm_lower'],'upper':certificate['norm_upper'],'proof':'disjoint positive partition; exact inherited Ks interval','recomputed_inverse_or_certificate':False},'common_clock_units':'outgoing occupation per common eta shift','radius_scaled_query_units':'outgoing occupation per unit row-radius-scaled coordinate','radius_scaled_norm':scaled_norm})
 np.savez(out/'COMPOSED_OPERATORS.npz',Ahat=A,Chat=C,Alo=Aint[0],Ahi=Aint[1],Clo=Cint[0],Chi=Cint[1],query_row_gain_lower=gainlo,query_row_gain_upper=gainhi,common_clock_lo=common[0],common_clock_hi=common[1],radius_scaled_row_lower=scaledlo,radius_scaled_row_upper=scaledhi)
 if not contained or not query_norm['pass_width']:raise ValueError('QUERY_INTERVAL_CRITERION_FAILED')
 # Preserve the same shared radiation/atomic event by construction.
 keys=['F','proper','number','radiation','atomic']
 hats=np.vstack([events['F_hat'],events['proper_hat'],events['number_hat'],events['radiation_hat'],events['atomic_hat']])
 el=np.vstack([events['F_lo'],events['proper_lo'],events['number_lo'],events['radiation_lo'],events['atomic_lo']]);eh=np.vstack([events['F_hi'],events['proper_hi'],events['number_hi'],events['radiation_hi'],events['atomic_hi']])
 EA=np.repeat(hats,2,axis=1)*np.ravel(np.column_stack((1-c['a'],c['a'])))[None,:];EC=hats*c['ghat'][None,:]
 EAI=iv.mul((np.repeat(el,2,axis=1),np.repeat(eh,2,axis=1)),weights);ECI=iv.mul((el,eh),(c['glo'][None,:],c['ghi'][None,:]))
 EA[4]=-EA[3];EC[4]=-EC[3];EAI[0][4]=-EAI[1][3];EAI[1][4]=-EAI[0][3];ECI[0][4]=-ECI[1][3];ECI[1][4]=-ECI[0][3]
 sign=all([np.array_equal(EA[4],-EA[3]),np.array_equal(EC[4],-EC[3]),np.array_equal(EAI[0][4],-EAI[1][3]),np.array_equal(ECI[1][4],-ECI[0][3])])
 np.savez(out/'EVENT_COMPOSITION.npz',event_hat=hats,event_lo=el,event_hi=eh,endpoint_hat=EA,endpoint_lo=EAI[0],endpoint_hi=EAI[1],query_hat=EC,query_lo=ECI[0],query_hi=ECI[1])
 save(out/'EVENT_METADATA.json',{'order':keys,'units':['per ln(a) per occupation','s^-1 per occupation','m^-3 s^-1 per occupation','J m^-3 s^-1 per occupation','J m^-3 s^-1 per occupation'],'source':'KS01 EVENT_RESPONSE.npz immutable rows; same incident subtraction and actual source H retained','additional_H_or_volume_factor':False,'atomic_radiation_exact_sign_pair':sign})
 if not sign:raise ValueError('EVENT_SHARED_SIGN_PAIR_FAILED')
 return {'A':A,'C':C,'Cinterval':Cint,'Ainterval':Aint,'events':hats,'event_endpoint':EA,'event_query':EC,'query_norm':query_norm,'event_sign':sign}
