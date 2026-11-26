import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
rng=np.random.default_rng(26);A=np.array([[1.2,.1,.2],[0.,.8,.12],[0.,0.,1./.96]])
mu,w=leggauss(64);p=2*np.pi*np.arange(128)/128;M,P=np.meshgrid(mu,p,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(P),np.sqrt(1-M*M)*np.sin(P),M],axis=-1).reshape(-1,3);w=np.repeat(w/256,128)
v=n@A.T;norm=np.linalg.norm(v,axis=1);nn=v/norm[:,None];ww=w*abs(np.linalg.det(A))/norm**3
out=dict(area=float(ww.sum()),first=np.sum(ww[:,None]*nn,axis=0).tolist(),second=np.einsum('n,ni,nj->ij',ww,nn,nn).tolist())
assert abs(ww.sum()-1)<1e-12 and np.max(abs(np.array(out['second'])-np.eye(3)/3))<1e-12
(D/'JACOBIAN.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
