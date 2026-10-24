"""October-2012 FULL hydrogen source, standalone primitive coordinates.

Value equations are shared by ordinary real and independent complex arithmetic.
The tangent path uses scalar.Dual only; no imported old package or native code.
"""
import math
import numpy as np
from scalar import Dual, exp, expm1, log, real, split

EI=13.598286071938324
E21=10.198714553953742
E31=12.087365397278509
E41=12.748393192442178
E32=1.8886508433247664
E42=2.5496786384884356
HPC=1.239841874331e-4
MH=.93878299831e9
SAHA=3.016103031869581e21
LYA=4.662899067555897e15
EV_J=1.602176634e-19
AXES=('xe','xHII','lnTR','lnTM','lnnH','lnH')


def parameters(baseline, delta=None, dual=False):
    """Additive xe/xHII; multiplicative positive primitives, no cosmology map."""
    if delta is None:
        delta=np.zeros(6)
    if dual:
        delta=[Dual(0.,np.eye(6)[i]) for i in range(6)]
    return [baseline[i]+delta[i] if i<2 else baseline[i]*exp(delta[i]) for i in range(6)]


def validate(theta):
    t=np.array([real(x) for x in theta])
    if not np.all(np.isfinite(t)) or not (t[0]>0 and 0<t[1]<1 and np.all(t[2:]>0)):
        raise ValueError('PRIMITIVE_DOMAIN')
    ratio=t[3]/t[2]
    if not (.004<t[2]<.4 and .1<ratio<1.):
        raise ValueError('SOURCE_TABLE_DOMAIN_OR_BOUNDARY')
    return t


def stencil(value,lo,hi,n):
    spacing=(hi-lo)/(n-1)
    coordinate=(real(value)-lo)/spacing
    raw=math.floor(coordinate)
    index=max(1,min(n-3,raw))
    # Only actual changes of the clamped stencil are branch surfaces.
    if 2<=round(coordinate)<=n-3 and abs(coordinate-round(coordinate))<=8*np.finfo(float).eps*max(1.,abs(coordinate)):
        raise ValueError('POLYNOMIAL_STENCIL_SURFACE')
    f=(value-lo)/spacing-index
    weights=[f*(f-1)*(2-f)/6,(1+f)*(1-f)*(2-f)/2,
             (1+f)*f*(2-f)/2,(1+f)*f*(f-1)/6]
    return index,weights


def dot4(values,weights):
    return values[0]*weights[0]+values[1]*weights[1]+values[2]*weights[2]+values[3]*weights[3]


def rates(theta,data):
    TR,TM=theta[2:4]
    it,wt=stencil(log(TR),math.log(.004),math.log(.4),100)
    im,wm=stencil(TM/TR,.1,1.,40)
    alpha=[];aeq=[]
    for l in range(2):
        temp=[dot4(data['log_alpha'][l,im-1+k,it-1:it+3],wt) for k in range(4)]
        alpha.append(exp(dot4(temp,wm)))
        aeq.append(exp(dot4(data['log_alpha'][l,39,it-1:it+3],wt)))
    factor=SAHA*TR*TR**.5*exp(-.25*EI/TR)
    beta=[aeq[0]*factor,aeq[1]*factor/3]
    R=exp(dot4(data['log_R'][it-1:it+3],wt))
    return alpha,[alpha[l]-aeq[l] for l in range(2)],aeq,beta,R,(it,im)


def escape(t,literal=False,allow_surface=False):
    """Native branch thresholds; stable same-function evaluation above 1e-6.

    Stable p sums k=1..10 (-1)^(k+1)t^k/(k+1)! for 1e-6<t<.03.
    Derivative follows the polynomial through Dual; complex uses plain complex
    operations on the identical expression. Small native p/A polynomials stay.
    """
    v=real(t)
    if not math.isfinite(v) or v<0:
        raise ValueError('OPTICAL_DEPTH_DOMAIN')
    if not allow_surface and (v==1e-6 or v==1e-30):
        raise ValueError('ESCAPE_BRANCH_SURFACE')
    if v<=1e-6:
        return t/2-t*t/6, t-t*t/2
    if literal:
        if isinstance(t,Dual) or np.iscomplexobj(t):
            raise ValueError('LITERAL_PARITY_REAL_ONLY')
        return 1-(1-math.exp(-t))/t,1-math.exp(-t)
    if v<.03:
        p=0.
        for k in range(1,11):
            p=p+((-1)**(k+1)/math.factorial(k+1))*t**k
    else:
        p=1+expm1(-t)/t
    return p,-expm1(-t)


def diffusion(TM,data):
    e=data['energy'];a=data['rates'][0]
    up=[0.]*311;dn=[0.]*311
    DE2=E21*E21*2*TM/MH
    up[100]=DE2/(e[101]-e[100])**2*a[100]
    for b in range(101,139):
        dn[b]=exp((e[b]-e[b-1])/TM)*up[b-1]
        up[b]=(DE2*a[b]-(e[b]-e[b-1])**2*dn[b])/(e[b+1]-e[b])**2
    b=139
    dn[b]=exp((e[b]-e[b-1])/TM)*up[b-1]
    up[b]=(DE2*a[b]-(e[b]-e[b-1])**2*dn[b])/(E21-e[b])**2
    ld=exp((E21-e[b])/TM)/3*up[b]
    dn[179]=DE2/(e[179]-e[178])**2*a[179]
    for b in range(178,140,-1):
        up[b]=exp((e[b]-e[b+1])/TM)*dn[b+1]
        dn[b]=(DE2*a[b]-(e[b+1]-e[b])**2*up[b])/(e[b]-e[b-1])**2
    b=140
    up[b]=exp((e[b]-e[b+1])/TM)*dn[b+1]
    dn[b]=(DE2*a[b]-(e[b+1]-e[b])**2*up[b])/(e[b]-E21)**2
    lu=exp((E21-e[b])/TM)/3*dn[b]
    # Source has no clipping. Negative recurrences are preserved, not repaired.
    return up,dn,lu,ld


def build(theta,data,literal=False,ownership=None):
    validate(theta)
    xe,xH,TR,TM,nH,H=theta;x=1-xH
    alpha,da,aeq,beta,R,indices=rates(theta,data)
    e=data['energy'];u=data['incoming'];a=data['rates']
    vr=[[0.]*311 for _ in range(2)];rv=[[0.]*311 for _ in range(2)]
    ly=LYA*H/nH/x
    rr=[[beta[0]+3*R+3*ly*(1.664786871919931*exp(-E32/TR)+1.953125*exp(-E42/TR)),-R],
        [-3*R,beta[1]+R+ly]]
    saha=SAHA*TR*TR**.5*exp(-EI/TR)/nH
    dxe2=xe*xH-saha*x
    sr=[nH*(saha*x*da[0]+alpha[0]*dxe2)+3*ly*x*1.664786871919931*u[312],
        nH*(saha*x*da[1]+alpha[1]*dxe2)+3*ly*x*u[311]]
    for b in range(311):
        # fabs(exp(delta/TR)-1) uses the energy-fixed sign for complex/dual.
        inv=[]
        for threshold in (E21,E31,E41):
            delta=e[b]-threshold
            if delta==0:
                raise ValueError('ENERGY_TRANSITION_SURFACE')
            inv.append(1/((1 if delta>0 else -1)*(exp(delta/TR)-1)))
        vr[0][b]=-a[1,b]*inv[0]
        vr[1][b]=-exp(-E32/TR)/3*a[2,b]*inv[1]-exp(-E42/TR)/3*a[3,b]*inv[2]
        db=exp((e[b]-E21)/TR)
        rv[0][b]=vr[0][b]*db;rv[1][b]=vr[1][b]*3*db
        rr[0][0]=rr[0][0]-vr[0][b]
        rr[1][1]=rr[1][1]-vr[1][b]
    up,dn,lu,ld=diffusion(TM,data)
    rr[1][1]=rr[1][1]+ld+lu
    vv=[[0.]*311 for _ in range(3)];tau=[];pi=[];atten=[];gamma=[]
    for b in range(311):
        g=-(rv[0][b]+rv[1][b])+up[b]+dn[b]
        t=g*x*(HPC/e[b])**3*nH/8/math.pi/H
        p,A=escape(t,literal)
        gamma.append(g);tau.append(t);pi.append(p);atten.append(A)
        scale=x*(HPC/e[b])**3*nH/8/math.pi/H
        vv[0][b]=g/p if real(t)>0 else 2/scale
        if 100<b<=139 or 140<b<180:
            vv[1][b]=-up[b-1]
        if 100<=b<139 or 140<=b<179:
            vv[2][b]=-dn[b+1]
    vr[1][139]=vr[1][139]-ld;rv[1][139]=rv[1][139]-up[139]
    vr[1][140]=vr[1][140]-lu;rv[1][140]=rv[1][140]-dn[140]
    sv=[vv[0][b]*x*u[b]*(1-pi[b]) for b in range(311)]
    signature=(indices,tuple(real(t)<=1e-6 for t in tau),tuple(real(t)>1e-30 for t in tau),
               tuple(real(t)<.03 for t in tau))
    if ownership is not None and signature!=ownership:
        raise ValueError('BRANCH_OR_STENCIL_CROSSING')
    return {'Trr':rr,'Trv':rv,'Tvr':vr,'Tvv':vv,'sr':sr,'sv':sv,'tau':tau,
            'p':pi,'A':atten,'gamma':gamma,'Alpha':alpha,'DAlpha':da,'Alpha_eq':aeq,
            'Beta':beta,'R2p2s':R,'Aup':up,'Adn':dn,'A2p_up':lu,'A2p_dn':ld,
            'theta':theta,'ownership':signature}


def matrices(blocks):
    """Return M,s,T,P and analytic coefficient tangents from scalar blocks."""
    vals={};der={}
    for key,value in blocks.items():
        if key!='ownership':
            vals[key],der[key]=split(value)
    dtype=vals['Trr'].dtype
    M=np.zeros((313,313),dtype=dtype);dM=np.zeros((313,313,6))
    M[:2,:2]=vals['Trr'];dM[:2,:2]=der['Trr']
    M[:2,2:]=vals['Trv'];dM[:2,2:]=der['Trv']
    M[2:,:2]=vals['Tvr'].T;dM[2:,:2]=der['Tvr'].transpose(1,0,2)
    for b in range(311):
        M[b+2,b+2]=vals['Tvv'][0,b];dM[b+2,b+2]=der['Tvv'][0,b]
        if b>0:
            M[b+2,b+1]=vals['Tvv'][1,b];dM[b+2,b+1]=der['Tvv'][1,b]
        if b<310:
            M[b+2,b+3]=vals['Tvv'][2,b];dM[b+2,b+3]=der['Tvv'][2,b]
    s=np.r_[vals['sr'],vals['sv']];ds=np.concatenate((der['sr'],der['sv']))
    T=np.zeros((314,313),dtype=dtype);dT=np.zeros((314,313,6))
    P=np.zeros((314,313),dtype=dtype);dP=np.zeros((314,313,6))
    x=1-blocks['theta'][1]
    def put(array,darray,i,j,z):
        v,d=split(z);array[i,j]=v;darray[i,j]=d
    for b in range(311):
        if real(blocks['tau'][b])<=1e-30:
            P[b,b]=1
            continue
        den=x*blocks['p'][b]*blocks['Tvv'][0][b]
        factor=blocks['A'][b]/den
        for l in range(2):
            put(T,dT,b,l,-blocks['Tvr'][l][b]*factor)
        if b>0:
            put(T,dT,b,b+1,-blocks['Tvv'][1][b]*factor)
        if b<310:
            put(T,dT,b,b+3,-blocks['Tvv'][2][b]*factor)
        put(P,dP,b,b,1-blocks['A'][b])
    put(T,dT,311,1,1/(3*x))
    put(T,dT,312,0,exp(-E32/blocks['theta'][2])/x)
    put(T,dT,313,0,exp(-E42/blocks['theta'][2])/x)
    vals.update(M=M,s=s,T=T,P=P)
    der.update(M=dM,s=ds,T=dT,P=dP)
    return vals,der


def outputs(blocks,X,incoming):
    """Literal native outgoing evaluation; X may carry the implicit tangent."""
    x=1-blocks['theta'][1];TR=blocks['theta'][2];H=blocks['theta'][5]
    o=[]
    for b in range(311):
        if real(blocks['tau'][b])<=1e-30:
            o.append(incoming[b]);continue
        numerator=-(X[0]*blocks['Tvr'][0][b]+X[1]*blocks['Tvr'][1][b])
        if b>0:
            numerator=numerator-X[b+1]*blocks['Tvv'][1][b]
        if b<310:
            numerator=numerator-X[b+3]*blocks['Tvv'][2][b]
        eq=numerator/(x*blocks['p'][b]*blocks['Tvv'][0][b])
        o.append(incoming[b]+(eq-incoming[b])*blocks['A'][b])
    o.extend([X[1]/(3*x),X[0]/x*exp(-E32/TR),X[0]/x*exp(-E42/TR)])
    xe,xH,_,_,nH,_=blocks['theta']
    saha=SAHA*TR*TR**.5*exp(-EI/TR)/nH
    terms=[nH*(saha*x*blocks['DAlpha'][l]+blocks['Alpha'][l]*(xe*xH-saha*x))-X[l]*blocks['Beta'][l] for l in range(2)]
    F=-(terms[0]+terms[1])/H
    number=3e6*LYA*H*(o[311]-incoming[311])
    radiation=E21*EV_J*number
    return {'outgoing':o,'F':F,'proper_ionization':H*F,'R_gamma':number,
            'radiation_energy':radiation,'atomic_energy':-radiation}
