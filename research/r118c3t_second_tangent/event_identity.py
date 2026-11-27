"""Order-two distribution transport identities. Coefficients not derivatives."""
import numpy as np,json
from scipy.integrate import quad
from scipy.optimize import brentq
from pathlib import Path
D=Path(__file__).resolve().parent
def multiply(A,B,T,Tprime):return T@A-Tprime@B,T@B
def run():
 # f_lambda=(J+lambda*J1) H(t+lambda*a(t)+lambda²*b(t)-s).
 # Exact integral by moving root; analytic distribution action includes a'.
 s=.41;J=1.4;J1=.23;a=lambda t:.1+.07*t;b=lambda t:.03-.05*t
 w=lambda t:np.exp(-.7*t)*(1+t*t);wp=lambda t:np.exp(-.7*t)*(2*t-.7*(1+t*t))
 pred1=J*a(s)*w(s)+J1*quad(w,s,1)[0]
 pred2=J*b(s)*w(s)-.5*J*(2*a(s)*.07*w(s)+a(s)**2*wp(s))+J1*a(s)*w(s)
 def f(l):
  q=brentq(lambda t:t+l*a(t)+l*l*b(t)-s,0,1,xtol=1e-15);return (J+l*J1)*quad(w,q,1,epsabs=1e-13)[0]
 rows=[]
 for ep in [.02,.01,.005,.0025]:
  p,m=f(ep),f(-ep);z=f(0)
  rows.append(dict(eps=ep,first_relative=abs((p-m)/(2*ep)-pred1)/abs(pred1),second_relative=abs((p+m-2*z)/(2*ep*ep)-pred2)/abs(pred2)))
 assert rows[-1]['second_relative']<1e-5
 # Matrix-valued product with a delta derivative: check test-function identity.
 A=np.array([.2,-.3]);B=np.array([.04,.02]);T=np.array([[.7,.3],[.2,.8]]);P=np.array([[.1,-.2],[.3,.1]])
 C,E=multiply(A,B,T,P);g=np.array([.9,-.5]);gp=np.array([.2,.1])
 err=abs(g@C-gp@E-(g@T@A-(gp@T+g@P)@B));assert err<1e-15
 o=dict(rows=rows,matrix_weak_error=err,first=pred1,second=pred2,scope='manufactured smooth moving discontinuity and matrix delta derivative product; no full native event graph')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
