"""Independent full-exponential Decimal80 crossing and finite derivatives.
This uses Delta bisection in the original law, never the binary64 shifted root
or the binary64 stable incoming increment implementation.
"""
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from common import save

def represented(x):
 a,b=float(x).as_integer_ratio();return D(a)/D(b)
def rational(x):return D(x.numerator)/D(x.denominator)
def run(L,x,g,h,out,counter):
 raw=[];checks=[];v=(D(1),D(-1)/2,D(-1)/2)
 weights=[(F(1),F(0),F(0)),(F(0),F(1),F(0)),(F(1,3),)*3,(F(1,14),F(4,14),F(9,14))]
 with localcontext() as ctx:
  ctx.prec=80
  for j in (0,139,140,270,311,312):
   l,xx,gg,hh=map(represented,(L[j],x[j],g[j],h));W=(-xx).exp();hc=gg-xx*W;kc=(xx*xx-xx)*W
   for ray,wf in enumerate(weights):
    w=tuple(map(rational,wf));A=sum(a*b for a,b in zip(w,v));C=sum(a*b*b for a,b in zip(w,v));aa=sum(a*abs(b) for a,b in zip(w,v))
    q1=l*A;q2=-2*l*A*A+2*l*l*(C-A*A);u1=hc*q1;u2=hc*q2+kc*l*l*A*A
    gross1=(abs(gg)+xx*W)*l*aa
    gross2=(abs(gg)+xx*W)*(2*l*aa*aa+2*l*l*(C+aa*aa))+(xx*xx+xx)*W*l*l*aa*aa
    values={}
    for divisor in (1,2):
     step=hh/D(divisor)
     for sign in (-1,1):
      p=sign*step;counter.root(decimal=True);t=abs(p);lo=l/(1+2*t);hi=l/(1-2*t)
      # Strict oracle-only bracket avoids endpoint roundoff; it is not a chart-domain enlargement.
      def residual(delta):return delta+sum(a*(2*p*b*delta).exp() for a,b in zip(w,v)).ln()/2-l
      flo,fhi=residual(lo),residual(hi)
      if flo>0 or fhi<0:raise ValueError('DECIMAL_BRACKET')
      for _ in range(160):
       mid=(lo+hi)/2
       if residual(mid)>0:hi=mid
       else:lo=mid
      Delta=(lo+hi)/2;dq=l-Delta
      # Full exp evaluated independently; baseline history cancels in differences.
      value=gg*dq+(-xx*dq.exp()).exp();values[(divisor,sign)]=value
      raw.append(dict(query=j,ray=ray,weights=[str(a) for a in wf],step_divisor=divisor,sign=sign,Lambda=str(l),x=str(xx),g=str(gg),lambda_value=str(p),Delta=str(Delta),delta_query=str(dq),full_reference_plus_history_increment=str(value),crossing_residual=str(residual(Delta)),bisection_iterations=160))
     fd1=(values[(divisor,1)]-values[(divisor,-1)])/(2*step)
     fd2=(values[(divisor,1)]+values[(divisor,-1)]-2*W)/(step*step)
     def metric(a,b,scale):
      if scale==0:
       if a!=b:raise ValueError('DECIMAL_ZERO_GROSS_NONZERO_ERROR')
       return D(0)
      return abs(a-b)/scale
     e1=metric(fd1,u1,gross1);e2=metric(fd2,u2,gross2)
     checks.append(dict(query=j,ray=ray,step_divisor=divisor,analytic_first=str(u1),analytic_second=str(u2),finite_first=str(fd1),finite_second=str(fd2),first_gross=str(gross1),second_gross=str(gross2),first_normalized_error=str(e1),second_normalized_error=str(e2),pass_first=e1<=D('2e-7'),pass_second=e2<=D('2e-7')))
    save(out/'DECIMAL_ROOTS.json',raw);save(out/'DECIMAL_CHECKS.json',checks);counter.persist('DECIMAL_QUERY_'+str(j)+'_RAY_'+str(ray))
    if not all(row['pass_first'] and row['pass_second'] for row in checks[-2:]):raise ValueError('DECIMAL_FINITE_ORACLE_FAILED')
 summary=dict(status='PASS',precision=80,bisection_iterations_per_root=160,scalar_roots=counter.decimal_roots,configurations=24,derivative_checks=48,max_first_normalized_error=max(float(r['first_normalized_error']) for r in checks),max_second_normalized_error=max(float(r['second_normalized_error']) for r in checks),tolerance=2e-7,scope='represented parameters; finite h and h/2 numerical evidence; no global remainder bound')
 save(out/'DECIMAL_SUMMARY.json',summary);return summary
