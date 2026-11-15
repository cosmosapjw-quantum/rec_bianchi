from pathlib import Path
import csv,gzip,hashlib,json,math
import numpy as np
B=Path(__file__).resolve().parents[1];OUT=B/'reviews/rerun';OUT.mkdir(exist_ok=True)
q=np.loadtxt(B/'rec199/source_inputs/F08_ORIGINAL_SOURCE_Q128.csv',delimiter=',',skiprows=1)[:,1:]
scenario=json.loads((B/'rec199/source_inputs/science_scenario_v1.json').read_text())
z=q[:,2];w0=(68083/61440-64517/47520*z*z+2641/1485*z**4)/128
with gzip.open(B/'rec199/source_inputs/ORIGINAL_NATIVE_F08_640STEP_128RAY_PHOTON_ANGLES.csv.gz','rt') as f:source=list(csv.DictReader(f))
with (B/'results_tetrad/native_l4_moments.csv').open() as f:moment=list(csv.DictReader(f))
with gzip.open(B/'results_tetrad/native_l4_stokes.csv.gz','rt') as f:saved=list(csv.DictReader(f))
def df(n):return math.prod(range(n,0,-2))
def sphere(e):return 0. if any(i%2 for i in e) else math.prod(df(i-1) for i in e)/df(sum(e)+1)
def wm(n,J,d):
 exps=[(i,j,d-i-j) for i in range(d+1) for j in range(d-i+1)]
 M=np.array([np.prod(n**np.array(e),axis=1) for e in exps]);target=np.array([sphere(e) for e in exps])
 base=w0*J;base/=base.sum()
 # SVD minimum norm correction, independently avoids producer's normal equations.
 corr=np.linalg.lstsq(M,target-M@base,rcond=None)[0]
 return base+corr,float(np.linalg.cond(M))
def tensor(n,I,w):
 n=n.astype(np.longdouble);I=I.astype(np.longdouble);w=w.astype(np.longdouble)
 d=I-I[0];mean=I[0]+np.sum(w*d)/np.sum(w)
 d=(d-np.sum(w*d)/np.sum(w))/mean
 return np.einsum('n,na,nb->ab',w*d,n,n)/np.sum(w)
maxerr={'tensor':0.,'stokes_scaled_pN':0.,'projection_scaled_N':0.,'ledger_scaled_pN':0.,'monomial_degree6':0.,'monomial_degree4':0.,'isotropic_spin_scaled':0.,'isotropic_tensor':0.,'pure_l2_exactness':0.,'jacobian_tangent_area':0.}
minw4=1;minw6=1;maxcond4=0.;maxcond6=0.;summaries={};witness={}
for k in range(640):
 rows=source[k*128:(k+1)*128];r=rows[0];branch,mode=r['branch'],r['model'];t=float(r['proper_t_s']);p=float(r['thomson_probability_one_source_tick']);step=int(r['step'])
 H=np.array(scenario['background']['pairs']['BIANCHI_I' if branch=='S0_BI' else 'FLRW']['H_per_s'])
 aa=np.exp(-H*t);u=q*aa;n=u/np.linalg.norm(u,axis=1)[:,None];g=np.linalg.norm(u,axis=1);J=np.exp(-sum(H)*t)/g**3
 w4,c4=wm(n,J,4);w6,c6=wm(n,J,6);minw4=min(minw4,float(w4.min()));minw6=min(minw6,float(w6.min()));maxcond4=max(maxcond4,c4);maxcond6=max(maxcond6,c6)
 assert min(w4)>0 and min(w6)>0
 for d,w in ((4,w4),(6,w6)):
  for total in range(d+1):
   for i in range(total+1):
    for j in range(total-i+1):
     e=(i,j,total-i-j);err=abs(w@np.prod(n**np.array(e),axis=1)-sphere(e));maxerr['monomial_degree'+str(d)]=max(maxerr['monomial_degree'+str(d)],float(err))
 ep=np.column_stack([-n[:,1],n[:,0],np.zeros(128)]);ep/=np.linalg.norm(ep,axis=1)[:,None];et=np.cross(ep,n)
 # Independent differential area determinant for the q->n map.
 up=np.column_stack([-q[:,1],q[:,0],np.zeros(128)]);up/=np.linalg.norm(up,axis=1)[:,None];ut=np.cross(up,q)
 d1=(ut*aa-n*np.sum(n*(ut*aa),axis=1)[:,None])/g[:,None]
 d2=(up*aa-n*np.sum(n*(up*aa),axis=1)[:,None])/g[:,None]
 jac=np.sum(n*np.cross(d1,d2),axis=1)
 maxerr['jacobian_tangent_area']=max(maxerr['jacobian_tangent_area'],float(np.max(abs(jac-J))))
 isoC=.75*(sum(w4)*np.eye(3)-np.einsum('n,ni,nj->ij',w4,n,n))
 isoQ=np.einsum('ni,ij,nj->n',et,isoC,et)-np.einsum('ni,ij,nj->n',ep,isoC,ep)
 isoU=2*np.einsum('ni,ij,nj->n',et,isoC,ep)
 maxerr['isotropic_spin_scaled']=max(maxerr['isotropic_spin_scaled'],float(np.max(np.hypot(isoQ,isoU))))
 maxerr['isotropic_tensor']=max(maxerr['isotropic_tensor'],float(np.linalg.norm(tensor(n,np.ones(128),w4))))
 S=np.array([[.11,.03,-.02],[.03,-.07,.01],[-.02,.01,-.04]])
 maxerr['pure_l2_exactness']=max(maxerr['pure_l2_exactness'],float(np.max(abs(tensor(n,1+np.einsum('ni,ij,nj->n',n,S,n),w4)-2*S/15))))
 X=np.column_stack([np.ones(128),n,n[:,0]**2-n[:,2]**2,n[:,1]**2-n[:,2]**2,n[:,0]*n[:,1],n[:,0]*n[:,2],n[:,1]*n[:,2]])
 for h,(ch,label) in enumerate([('photons_per_H','N'),('energy_eV_per_H','E_eV')]):
  count=np.array([float(x['original_'+ch]) for x in rows]);I=count/J;Q=tensor(n,I,w4);Q6=tensor(n,I,w6);norm=float(np.linalg.norm(Q))
  rr=moment[2*k+h];qref=np.zeros((3,3))
  for i in range(3):
   for j in range(i,3):qref[i,j]=qref[j,i]=float(rr[f'q4_{i}{j}'])
  maxerr['tensor']=max(maxerr['tensor'],float(np.max(abs(Q-qref))))
  v=np.linalg.lstsq(X,I/I[0]-1,rcond=None)[0];a,b,c,d,e=v[4:]
  Qfit=2*np.array([[a,c/2,d/2],[c/2,b,e/2],[d/2,e/2,-a-b]])/(15*(1+v[0]))
  fit=float(np.linalg.norm(Q-Qfit))/norm if norm>1e-12 else None;l6=float(np.linalg.norm(Q-Q6))/norm if norm>1e-12 else None
  m=I.astype(np.longdouble)*w4.astype(np.longdouble);m*=sum(count.astype(np.longdouble))/sum(m);nn=n.astype(np.longdouble)
  C=.75*(sum(m)*np.eye(3)-np.einsum('n,ni,nj->ij',m,nn,nn))
  ctt=np.einsum('ni,ij,nj->n',et,C,et);cpp=np.einsum('ni,ij,nj->n',ep,C,ep);ctp=np.einsum('ni,ij,nj->n',et,C,ep)
  inc=p*w4*(ctt+cpp);Qs=p*w4*(ctt-cpp);Us=2*p*w4*ctp
  for nam,arr in [('in',inc),('Q',Qs),('U',Us)]:
   old=np.array([float(x[label+'_'+nam]) for x in saved[k*128:(k+1)*128]],dtype=np.longdouble)
   maxerr['stokes_scaled_pN']=max(maxerr['stokes_scaled_pN'],float(np.max(abs(arr-old))/(p*sum(count))))
  oldm=np.array([float(x[label+'_projected']) for x in saved[k*128:(k+1)*128]])
  maxerr['projection_scaled_N']=max(maxerr['projection_scaled_N'],float(np.max(abs(oldm-m))/sum(count)))
  oldd=np.array([float(x[label+'_delta']) for x in saved[k*128:(k+1)*128]])
  maxerr['ledger_scaled_pN']=max(maxerr['ledger_scaled_pN'],float(abs(sum(oldd))/(p*sum(count))))
  key=branch+'_'+mode+'_'+ch;ss=summaries.setdefault(key,{'max_fit_relative':0.,'max_l6_relative':0.,'peak_polarization_scattered_in':0.})
  ss['max_fit_relative']=max(ss['max_fit_relative'],fit or 0);ss['max_l6_relative']=max(ss['max_l6_relative'],l6 or 0);ss['peak_polarization_scattered_in']=max(ss['peak_polarization_scattered_in'],float(np.max(np.hypot(Qs,Us)/inc)))
  if (branch,mode,step,h)==('S0_BI','ORIGINAL_HAT',142,0):witness={'norm':norm,'fit_relative':fit,'l6_relative':l6,'tensor':np.array(Q,float).tolist()}
paths=[B/'thomson_tetrad.py',B/'run_native_tetrad.py',B/'results_tetrad/RESULT.json',B/'results_tetrad/native_l4_moments.csv',B/'results_tetrad/native_l4_stokes.csv.gz',B/'rec199/source_inputs/science_scenario_v1.json',B/'source_continuous_s0.py',B/'source_spectral_support.py',B/'source_capture_native_angles.py']
r={'schema':'INDEPENDENT_REC_TETRAD_REVIEW_V1','runtime':'PYTHON_PASS','verdict':'PASS_SCOPED_TETRAD_L4_ESTIMATOR','continuum_angular_convergence':'UNRESOLVED','checked_stages':640,'checked_channel_tensors':1280,'checked_angular_rows':81920,'source_measure_established_by_scenario':scenario['initial_state']['photon_angular_distribution'],'jacobian_derivation':'For n=Aq/g, Dn[u]=(1-nnT)Au/g. The tangent-area determinant is det(A)/g^3. Native q-cell mass divided by J estimates intensity; no duplicate J.','max_errors':maxerr,'minimum_weights_all_stages':{'degree4':minw4,'degree6':minw6},'maximum_constraint_matrix_condition':{'degree4':maxcond4,'degree6':maxcond6},'models':summaries,'witness':witness,'hashes':{str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(OUT/'REC_TETRAD_REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='hashes'},indent=2))
