#!/usr/bin/env python3
import csv,gzip,hashlib,json,time,sys
from pathlib import Path
import numpy as np
from thomson_l4 import weights_l4,quadrupole,operators
from thomson_tetrad import tetrad_grid,physical_weights,project_q_mass
BASE=Path(__file__).parent
SRC=BASE/'rec199/source_inputs'
Q_SHA='a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92'
ANGLE_SHA='70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,m):
 if not c:raise ValueError(m)
def main():
 t=time.perf_counter();cpu=time.process_time()
 qfile=SRC/'F08_ORIGINAL_SOURCE_Q128.csv';angfile=SRC/'ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz'
 scenario_file=SRC/'science_scenario_v1.json';scenario_sha='c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1'
 require(sha(scenario_file)==scenario_sha,'original scenario hash')
 scenario=json.loads(scenario_file.read_text())
 require(scenario['initial_state']['photon_angular_distribution'].startswith('ISOTROPIC_CONTINUUM_MEASURE'),'source continuum interpretation')
 require(sha(qfile)==Q_SHA and sha(angfile)==ANGLE_SHA,'source hash')
 q=np.loadtxt(qfile,delimiter=',',skiprows=1)[:,1:];z=q[:,2];w4=weights_l4(q)
 w2=(1+(4/63)*(z*z-21/64))/128
 A=np.stack([z**k for k in (0,2,4,6)])
 w6=np.ones(128)/128+A.T@np.linalg.solve(A@A.T,np.array([1,1/3,1/5,1/7])-A@np.ones(128)/128)
 X=np.column_stack((np.ones(128),q,q[:,0]**2-q[:,2]**2,q[:,1]**2-q[:,2]**2,q[:,0]*q[:,1],q[:,0]*q[:,2],q[:,1]*q[:,2]))
 original=list(csv.DictReader(gzip.open(angfile,'rt')))
 require(len(original)==81920,'native rows');records=[];failures=[];summaries={};angles=[]
 maxledger=0.;maxpsd=0.
 for k in range(640):
  s=original[k*128:(k+1)*128];b,mode,step=s[0]['branch'],s[0]['model'],int(s[0]['step'])
  require(all(r['branch']==b and r['model']==mode and int(r['step'])==step and int(r['ray'])==j for j,r in enumerate(s)),'source stage indexing')
  p=float(s[0]['thomson_probability_one_source_tick'])
  H=np.array(scenario['background']['pairs']['BIANCHI_I' if b=='S0_BI' else 'FLRW']['H_per_s'])
  directions,J=tetrad_grid(q,H,step*6.25e8)
  pw4=physical_weights(q,directions,J,4);pw6=physical_weights(q,directions,J,6)
  K,Q,U=operators(directions,pw4)
  X=np.column_stack((np.ones(128),directions,directions[:,0]**2-directions[:,2]**2,directions[:,1]**2-directions[:,2]**2,directions[:,0]*directions[:,1],directions[:,0]*directions[:,2],directions[:,1]*directions[:,2]))
  arrays=[]
  for channel in ('photons_per_H','energy_eV_per_H'):
   n=np.array([float(r['original_'+channel]) for r in s]);I=128*n/J
   require(np.min(n)>0,'native positive photons')
   v=np.linalg.lstsq(X,I/I.mean()-1,rcond=None)[0];a,bb,c,d,e=v[4:]
   qls=2*np.array([[a,c/2,d/2],[c/2,bb,e/2],[d/2,e/2,-a-bb]])/(15*(1+v[0]))
   qs={2:quadrupole(q,w2,n),4:quadrupole(directions,pw4,I/128),6:quadrupole(directions,pw6,I/128)}
   row={'branch':b,'model':mode,'step':step,'channel':channel}
   for degree,mat in qs.items():
    norm=float(np.linalg.norm(mat));diff=float(np.linalg.norm(mat-qls))
    row[f'q{degree}_norm']=norm;row[f'q{degree}_fit_abs_diff']=diff
    row[f'q{degree}_fit_rel_diff']=diff/norm if norm>1e-12 else None
   d46=float(np.linalg.norm(qs[4]-qs[6]));row['q4_q6_abs_diff']=d46
   row['q4_q6_rel_diff']=d46/row['q4_norm'] if row['q4_norm']>1e-12 else None
   m=project_q_mass(n,J,pw4,'q_midpoint_continuum');inc=p*(K@m);dN=inc-p*m;qn=p*(Q@m);un=p*(U@m)
   maxledger=max(maxledger,abs(float(dN.sum()))/(p*n.sum()))
   maxpsd=max(maxpsd,float(np.max(np.hypot(qn,un)-inc))/(p*n.sum()))
   row['max_polarization_fraction_scattered_in']=float(np.max(np.hypot(qn,un)/inc))
   row['total_expected_scatter']=float(p*n.sum())
   row['total_elastic_delta']=float(dN.sum())
   for i in range(3):
    for j in range(i,3):row[f'q4_{i}{j}']=float(qs[4][i,j])
   records.append(row)
   if b=='S0_BI' and row['q4_norm']>1e-12 and row['q4_fit_rel_diff']>=.03:failures.append(row)
   key=f'{b}_{mode}_{channel}';ss=summaries.setdefault(key,{'max_l4_vs_fit_relative':0.,'max_l4_vs_l6_relative':0.,'peak_polarization_scattered_in':0.,'expected_scattering_sum':0.})
   ss['max_l4_vs_fit_relative']=max(ss['max_l4_vs_fit_relative'],row['q4_fit_rel_diff'] or 0)
   ss['max_l4_vs_l6_relative']=max(ss['max_l4_vs_l6_relative'],row['q4_q6_rel_diff'] or 0)
   ss['peak_polarization_scattered_in']=max(ss['peak_polarization_scattered_in'],row['max_polarization_fraction_scattered_in'])
   ss['expected_scattering_sum']+=row['total_expected_scatter']
   if b=='S0_BI' and mode=='ORIGINAL_HAT' and step==142 and channel=='photons_per_H':witness=row.copy()
   arrays.append((m,inc,dN,qn,un))
  for j in range(128):
   r={'branch':b,'model':mode,'step':step,'ray':j}
   for label,arr in zip(('N','E_eV'),arrays):
    for name,vals in zip(('projected','in','delta','Q','U'),arr):r[label+'_'+name]=float(vals[j])
   angles.append(r)
 out=BASE/'results_tetrad';out.mkdir(exist_ok=True)
 def csvout(path,data):
  with path.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 csvout(out/'native_l4_moments.csv',records)
 import io
 with (out/'native_l4_stokes.csv.gz').open('wb') as raw:
  with gzip.GzipFile(fileobj=raw,filename='',mode='wb',mtime=0) as gz:
   with io.TextIOWrapper(gz,encoding='ascii',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(angles[0]),lineterminator='\n');wr.writeheader();wr.writerows(angles)
 res={'schema':'REC_NATIVE_TETRAD_L4_REPAIR_V2','source_measure':'q_midpoint_continuum_intensity_estimator','source_q_semantics':'KILLING_LABEL_NOT_INSTANTANEOUS_TETRAD','solid_angle_conversion':'I_n=128*N_q/J; J=det(A)/|Aq|^3; n=Aq/|Aq|','original_scenario_sha256':scenario_sha,'source_commit':'c10e97ab3178c423cc7699684b33e1730d26437a','source_q_sha256':Q_SHA,'source_angles_sha256':ANGLE_SHA,'native_stages':640,'native_source_rows':81920,'derived_stokes_rows':len(angles),'native_IVP_reexecutions':0,'historical_REC199_gate':'FAIL_PRESERVED_AND_Q_FRAME_PHYSICAL_ERROR_IDENTIFIED','new_l4_same_3pct_gate':'PASS_SCOPED' if not failures else 'FAIL','failures':failures,'witness_original_hat_tick142':witness,'model_summaries':summaries,'max_elastic_ledger_relative':maxledger,'max_stokes_psd_violation_scaled':maxpsd,'final_stage_weights_minmax':[float(pw4.min()),float(pw4.max())],'degree4_l2_field_exactness':'DERIVED_AND_TESTED_IN_PHYSICAL_TETRAD','q2_comparator':'HISTORICAL_WRONG_FRAME_DIAGNOSTIC_NOT_SAME_PHYSICAL_TARGET','continuum_angular_convergence':'UNRESOLVED','owner_abundance_DAG_delta':0,'outputs_sha256':{p.name:sha(p) for p in out.iterdir() if p.suffix in ('.csv','.gz')},'elapsed_wall_s':time.perf_counter()-t,'cpu_s':time.process_time()-cpu,'python':sys.version}
 (out/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
if __name__=='__main__':main()
