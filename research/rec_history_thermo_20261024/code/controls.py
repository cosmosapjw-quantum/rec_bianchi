"""New bounded exact manufactured systems, escape probes, refusal controls."""
from fractions import Fraction as Q
from itertools import permutations
import math
import numpy as np
import mpmath as mp
from scalar import Dual
from source import escape,validate,stencil


def determinant_and_derivative(A,Ak):
    """Fraction Leibniz polynomial and its derivative, dimension <=3."""
    n=len(A);value=Q(0);derivative=Q(0)
    for p in permutations(range(n)):
        inversions=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        sign=(-1)**inversions
        factors=[Q(A[i][p[i]]) for i in range(n)]
        value+=sign*math.prod(factors)
        for i in range(n):
            derivative+=sign*Q(Ak[i][p[i]])*math.prod(factors[j] for j in range(n) if j!=i)
    return value,derivative


def exact_cramer(M,Mk,s,sk):
    """Independent rational derivative, no implicit tangent RHS formula."""
    denominator,d_denominator=determinant_and_derivative(M,Mk)
    X=[];DX=[]
    for column in range(len(s)):
        A=[row.copy() for row in M];Ak=[row.copy() for row in Mk]
        for i in range(len(s)):
            A[i][column]=s[i];Ak[i][column]=sk[i]
        numerator,d_numerator=determinant_and_derivative(A,Ak)
        X.append(numerator/denominator)
        DX.append((d_numerator*denominator-numerator*d_denominator)/denominator**2)
    return X,DX


def run():
    records=[]
    cases=[([[3]],[[2]],[5],[7]),
           ([[4,1],[-2,3]],[[1,-2],[3,0]],[2,-1],[1,4]),
           ([[5,1,0],[-1,4,2],[1,0,3]],[[0,2,1],[1,-1,0],[2,0,1]],[1,3,-2],[2,-1,4])]
    toy_rhs=0
    for k,(M,Mk,s,sk) in enumerate(cases):
        X,DX=exact_cramer(M,Mk,s,sk)
        A=np.array(M,dtype=float);B=np.array(Mk,dtype=float)
        x=np.linalg.solve(A,np.array(s,dtype=float));toy_rhs+=1
        dx=np.linalg.solve(A,np.array(sk)-B@x);toy_rhs+=1
        ref=np.array([float(v) for v in DX]);err=float(np.max(np.abs(dx-ref)))
        gross=np.abs(A)@np.abs(dx)+np.abs(B)@np.abs(x)+np.abs(sk)
        residual=A@dx+B@x-np.array(sk)
        diagnostic=float(np.max(np.abs(residual)/np.maximum(gross,1e-280)))
        scale=max(float(np.max(np.abs(ref))),1e-280)
        records.append({'case':k,'dimension':len(X),'M_parameter_derivative':Mk,
                        'exact_X':[str(v) for v in X],'exact_dX':[str(v) for v in DX],
                        'reference_method':'Fraction Cramer determinants differentiated as rational functions; no implicit RHS reference',
                        'absolute_derivative_error':err,'normalized_derivative_error':err/scale,
                        'backward_residual':diagnostic,'pass':err/scale<=512*np.finfo(float).eps})
    mp.mp.dps=60
    depths=[0.,1e-32,1e-12,1e-8,1e-6*(1-1e-8),1e-6*(1+1e-8),1e-5,.001,.029,.03,.1,1.,10.,100.]
    probes=[]
    for t in depths:
        z=mp.mpf(t)
        if t<=1e-6:
            pv=z/2-z*z/6;av=z-z*z/2;pd=mp.mpf('.5')-z/3;ad=1-z
        else:
            pv=1+mp.expm1(-z)/z;av=-mp.expm1(-z)
            pd=(1-(1+z)*mp.exp(-z))/(z*z);ad=mp.exp(-z)
        p,A=escape(Dual(t,np.eye(6)[0]),allow_surface=True)
        pe=abs(p.v-float(pv));ae=abs(A.v-float(av))
        pde=abs(p.d[0]-float(pd));ade=abs(A.d[0]-float(ad))
        # A binary64 arithmetic check, not a physical/transcendental enclosure.
        tol=1024*np.finfo(float).eps
        ok=max(pe/max(abs(float(pv)),1e-280),ae/max(abs(float(av)),1e-280),
               pde/max(abs(float(pd)),1e-280),ade/max(abs(float(ad)),1e-280))<=tol
        probes.append({'tau':t,'p':p.v,'A':A.v,'p_prime':p.d[0],'A_prime':A.d[0],
                       'p_60digit':str(pv),'A_60digit':str(av),'p_prime_60digit':str(pd),
                       'A_prime_60digit':str(ad),'p_value_absolute_error':pe,'A_value_absolute_error':ae,
                       'p_prime_absolute_error':pde,'A_prime_absolute_error':ade,'pass':ok,
                       'p_series_remainder_bound':t**11/math.factorial(12) if 1e-6<t<.03 else None,
                       'p_derivative_remainder_bound':11*t**10/math.factorial(12) if 1e-6<t<.03 else None})
    refusals=[]
    base=[.2,.2,.25,.24,200.,5e-14]
    bad=[]
    for i in range(6):
        for v in [float('nan'),float('inf')]:
            x=base.copy();x[i]=v;bad.append(('nonfinite_'+str(i),lambda x=x:validate(x)))
    for i in [2,3,4,5]:
        x=base.copy();x[i]=0.;bad.append(('nonpositive_'+str(i),lambda x=x:validate(x)))
    for name,x in [('xe_zero',[0.,.2,.25,.24,200,5e-14]),('xH_zero',[.2,0.,.25,.24,200,5e-14]),
                   ('xH_one',[.2,1.,.25,.24,200,5e-14]),('TR_outside',[.2,.2,.5,.24,200,5e-14]),
                   ('ratio_outside',[.2,.2,.25,.01,200,5e-14]),('ratio_boundary',[.2,.2,.25,.25,200,5e-14])]:
        bad.append((name,lambda x=x:validate(x)))
    bad.extend([('escape_switch',lambda:escape(1e-6)),('transparent_switch',lambda:escape(1e-30)),
                ('negative_depth',lambda:escape(-1)),('nonfinite_depth',lambda:escape(float('nan'))),
                ('stencil_surface',lambda:stencil(.1+10*(.9/39),.1,1.,40))])
    for name,fn in bad:
        try:
            fn();refusals.append({'name':name,'refused':False})
        except (ValueError,FloatingPointError) as e:
            refusals.append({'name':name,'refused':True,'reason':str(e)})
    return {'manufactured':records,'small_RHS_including_exact_rational':toy_rhs,
            'escape_probes':probes,'escape_probe_count':len(probes),'refusal_controls':refusals,
            'pass':all(x['pass'] for x in records+probes) and all(x['refused'] for x in refusals)}
