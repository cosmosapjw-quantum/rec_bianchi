import json,numpy as np
from pathlib import Path
from scipy.integrate import quad
D=Path(__file__).resolve().parent
def run():
 # Two weak moments exact for affine projected density, jump inside cell.
 rng=np.random.default_rng(932);err=0.;linear=0.
 for _ in range(100):
  z=rng.uniform();a,b,c=rng.normal(size=3)
  f=lambda u:(a+b*u)+(c if u>=z else 0)
  m=np.array([quad(lambda t:t**k*f(t),0,1,points=[z],epsabs=1e-13)[0] for k in range(3)])
  L,R=4*m[0]-6*m[1],6*m[1]-2*m[0]
  err=max(err,abs((L+R)/2-m[0]),abs((L+2*R)/6-m[1]))
  v,w=rng.normal(size=2);exact=quad(lambda t:(v+(w-v)*t)*f(t),0,1,points=[z])[0];linear=max(linear,abs(exact-v*(m[0]-m[1])-w*m[1]))
 assert max(err,linear)<1e-13
 out=dict(affine_moment_abs=err,weighted_linear_abs=linear,scope='manufactured jump and exact endpoint transfer moment test')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
