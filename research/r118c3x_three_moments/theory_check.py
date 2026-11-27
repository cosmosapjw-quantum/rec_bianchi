import numpy as np,json
from numpy.polynomial.legendre import leggauss,legvander
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 z,w=leggauss(16);v=legvander(z,6);u=(z+1)/2;w/=2;T=np.stack([u**k for k in range(3)])@(w[:,None]*v)
 want=np.array([[1,0,0],[.5,1/6,0],[1/3,1/6,1/30]])
 assert np.max(abs(T[:,:3]-want))<1e-14 and np.max(abs(T[:,3:]))<1e-14
 # Negative quadratic with nonnegative quartic extension (a sharp endpoint).
 a=np.array([.15,.22,.09,.05,.04]);m=T[:,:5]@a
 realizable=m[0]*m[2]>=m[1]**2 and m[2]<=m[1]<=m[0]
 out=dict(moment_matrix=T.tolist(),orthogonality_abs=float(np.max(abs(T[:,3:]))),example_realizable=bool(realizable),scope='shifted Legendre moment identity and necessary realizability inequality')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
