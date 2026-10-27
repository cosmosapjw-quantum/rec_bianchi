import os,json,time,resource,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
u=Path('/tmp/rec_history_resume_20261026/rec_bianchi/research/rec_history_geometry_response_20261026')
r=u/'results/primary001'
inputs={}
def read(name):
 p=r/name;inputs[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 with np.load(p,allow_pickle=False) as a:return {k:a[k].copy() for k in a.files}
def readjson(name):
 p=r/name;inputs[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};return json.loads(p.read_text())
def extrema(a):
 a=np.asarray(a);imin=int(np.argmin(a));imax=int(np.argmax(a))
 return {'shape':list(a.shape),'minimum':float(a.flat[imin]),'minimum_index':list(np.unravel_index(imin,a.shape)),'maximum':float(a.flat[imax]),'maximum_index':list(np.unravel_index(imax,a.shape)),'zero_count':int(np.count_nonzero(a==0)),'negative_count':int(np.count_nonzero(a<0)),'positive_count':int(np.count_nonzero(a>0))}
def rel(actual,expected):
 d=np.asarray(expected);a=np.asarray(actual);mask=d!=0;indices=np.argwhere(mask);v=np.abs((a[mask]-d[mask])/d[mask]);k=int(np.argmax(v)) if v.size else None
 return {'scope':'DIAGNOSTIC_ONLY_NOT_GATE; absolute relative error against stored analytic values; zero denominators excluded','denominator_nonzero_count':int(mask.sum()),'zero_denominator_count':int((~mask).sum()),'max_relative_error':float(v[k]) if k is not None else None,'max_index':indices[k].tolist() if k is not None else None,'median_relative_error':float(np.median(v)) if v.size else None,'max_absolute_error':float(np.max(abs(a-d)))}
a=read('ANALYTIC_v1.npz');a2=read('ANALYTIC_v2.npz');b=read('SOURCE_BINDING.npz');c=read('SCALAR_COMPOSITION.npz');d=read('FINITE_DIAGNOSTICS.npz');inter=readjson('EXACT_INTERVAL_ACTION.json');comp=readjson('SCALAR_COMPOSITION.json')
arrays={'B':a['B'],'Q11_prime_v1':a['quadrupole_closed'][:,0,0],'mean_u2_per_S2_v1':a['monopole_coefficient_per_S2'],'mean_u2_per_S2_v2':a2['monopole_coefficient_per_S2'],'mean_u2_v1':a['mean_u2_closed'],'outgoing_mean_second':c['outgoing_mean_second']}
lo=list(map(F,inter['lower_exact']));hi=list(map(F,inter['upper_exact']));width=[h-l for l,h in zip(lo,hi)];inside=[l<=F(float(v))<=h for l,v,h in zip(lo,c['outgoing_mean_second'],hi)]
wmin=min(range(len(width)),key=lambda i:width[i]);wmax=max(range(len(width)),key=lambda i:width[i])
idx=[0,37,139,140,270,289,310,311,312]
samples=[]
for j in idx:
 samples.append({'incoming_index':j,'source_index':int(b['source_index'][j]),'target_energy_eV':float(b['target_energy_eV'][j]),'source_energy_eV':float(b['source_energy_eV'][j]),'stored_incoming':float(b['stored_incoming'][j]),'baseline_total_occupation':float(b['baseline_total_occupation'][j]),**{k:float(v[j]) for k,v in arrays.items()},'interval_lower_outward':float(c['interval_lo'][j]),'interval_upper_outward':float(c['interval_hi'][j]),'interval_width_exact':str(width[j]),'interval_width_float':float(width[j]),'outgoing_point_inside_exact_represented_K_enclosure':inside[j]})
samples.append({'outgoing_index':313,'outgoing_mean_second':float(c['outgoing_mean_second'][313]),'incoming_index':None,'interval_lower_outward':float(c['interval_lo'][313]),'interval_upper_outward':float(c['interval_hi'][313]),'interval_width_exact':str(width[313]),'interval_width_float':float(width[313]),'outgoing_point_inside_exact_represented_K_enclosure':inside[313]})
h=float(b['h']);of=c['finite_outgoing_mean_increments'];out_h=(of[0]+of[1])/(h*h);out_half=(of[2]+of[3])/((h/2)**2)
diag={}
for step in ('h','half'):
 diag['mean_second_'+step]=rel(d['mean_second_'+step],a['mean_u2_closed'])
 diag['directional_first_'+step]=rel(d['directional_first_'+step],a['u1'].T)
 diag['directional_second_'+step]=rel(d['directional_second_'+step],a['u2'].T)
 diag['mean_first_'+step]={'scope':'DIAGNOSTIC_ONLY_NOT_GATE; theoretical analytic mean first derivative is zero, relative error undefined','maximum_absolute_value':float(abs(d['mean_first_'+step]).max()),'maximum_index':int(np.argmax(abs(d['mean_first_'+step])))}
diag['outgoing_second_h']=rel(out_h,c['outgoing_mean_second']);diag['outgoing_second_half']=rel(out_half,c['outgoing_mean_second'])
res={'status':'SAVED_RESULTS_READBACK_COMPLETE','scope':'Mechanical saved-result arithmetic only. No new source, root, operator, interval action, or scientific acceptance gate. Interval width subtraction and point containment use exact saved Fraction endpoints; no libm evaluation validity is asserted.','source_directory':'results/primary001','saved_input_identities':inputs,'extrema':{k:extrema(v) for k,v in arrays.items()},'samples':samples,'interval_summary':{'scope':inter['scope'],'point_count':len(inside),'inside_exact_count':sum(inside),'outside_exact_indices':[i for i,v in enumerate(inside) if not v],'inside_exact_by_outgoing_index':inside,'minimum_width_index':wmin,'minimum_width_exact':str(width[wmin]),'minimum_width_float':float(width[wmin]),'maximum_width_index':wmax,'maximum_width_exact':str(width[wmax]),'maximum_width_float':float(width[wmax]),'width_float_extrema':extrema(np.array([float(w) for w in width]))},'finite_diagnostics':diag,'scalar_composition_saved':comp,'new_actions':{'roots':0,'decimal_roots':0,'operator_actions':0,'interval_actions':0,'source_actions':0}}
p=u/'results/SAVED_VALUES.json'
with p.open('x') as f:json.dump(res,f,indent=2,sort_keys=True,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x);f.write('\n')
print(json.dumps({'status':res['status'],'output':str(p),'point_inside_count':sum(inside),'point_outside_indices':res['interval_summary']['outside_exact_indices'],'output_bytes':p.stat().st_size,'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
