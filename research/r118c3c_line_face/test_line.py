import numpy as np
from line_face import LineOwner,L
def test_pair_and_qss():
 from labelled import Owner
 o=Owner(np.array([10.2,10.3]),np.array([2.,3.]),np.array([0]),np.array([1]),np.array([.2]))
 b=(0.,.25,1.,0.);n=np.array([1.,2.],dtype=L)
 q=LineOwner(o,b,1.,3.,2.,4.,n)
 assert abs(q.qss(n)-1.)<1e-14
 a,v=q.affine(0.,0.,False);x=np.r_[n,1.];dx=a@x+v
 assert abs(dx[2])<1e-14
 assert abs(dx[:3].sum()+dx[3]+dx[10]-dx[6]-dx[9])<1e-13
 e=o.e
 assert abs(dx[:2]@e+q.line_e*dx[2]+dx[4]+dx[5]+dx[8]+dx[11]+q.line_e*(dx[10]-dx[9])-dx[7])<1e-12
