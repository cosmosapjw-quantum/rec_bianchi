"""Independent 80-digit equations: bisection and fixed-step central differences.

No import of production adapter/vendor. Binary input values promoted exactly.
"""
import mpmath as mp
mp.mp.dps=80
M=mp.mpf

def vec(x):return [M(v) for v in x]
def norm(x):return mp.sqrt(sum(v*v for v in x))
def direction(x):
    z=norm(x);return [v/z for v in x]
def cross(n,b,lam,eta_t=0):
    n=direction(vec(n));a=[1+x for x in vec(b)];lam=M(lam)
    if lam==0:d=M(0)
    elif all(x==1 for x in a):d=lam
    elif sum(x!=0 for x in n)==1:d=lam/a[next(i for i,x in enumerate(n) if x)]
    else:
        low=lam/max(a);high=lam/min(a)
        for _ in range(300):
            mid=(low+high)/2
            logs=[mp.log(abs(x))+aa*mid for x,aa in zip(n,a) if x];shift=max(logs)
            value=shift+mp.log(sum(mp.exp(2*(x-shift)) for x in logs))/2
            if value>lam:high=mid
            else:low=mid
        d=(low+high)/2
    logs=[mp.log(abs(x))+aa*d if x else mp.ninf for x,aa in zip(n,a)];shift=max(logs)
    z=mp.sqrt(sum(mp.exp(2*(x-shift)) for x in logs));ns=[mp.sign(x)*mp.exp(y-shift)/z for x,y in zip(n,logs)]
    return {'delta':d,'ns':ns,'eta_s':M(eta_t)-d,'qt':sum(aa*x*x for aa,x in zip(a,n))}

def offset(xt,lam,delta):
    xt=M(xt);logxs=mp.log(xt)+M(lam)-M(delta) if xt else mp.ninf
    # Above x=1e10 all occupations are far below any declared floor.
    xs=mp.exp(logxs) if logxs<mp.log(M('1e10')) else mp.inf
    ws=mp.exp(-xs);wt=mp.exp(-xt)
    return {'offset':ws-wt,'ws':ws,'wt':wt,'xs':xs,'xws':xs*ws if xs!=mp.inf else M(0)}

def perturb(c,t):
    return direction([M(n)+t*M(v) for n,v in zip(c['n'],c['dn'])]),[M(b)+t*M(v) for b,v in zip(c['b'],c['db'])],M(c['lam'])+t*M(c['dlam']),M(c['eta_t'])+t*M(c['deta_t'])

def cross_difference(c):
    step=M(c['fd_step']);ends=[]
    for t in [-step,step]:
        n,b,l,e=perturb(c,t);ends.append(cross(n,b,l,e))
    return {'ddelta':(ends[1]['delta']-ends[0]['delta'])/(2*step),'deta_s':(ends[1]['eta_s']-ends[0]['eta_s'])/(2*step),'dns':[(x-y)/(2*step) for x,y in zip(ends[1]['ns'],ends[0]['ns'])],'dqt':(ends[1]['qt']-ends[0]['qt'])/(2*step)}

def field(coeff,n):
    return coeff[0]+sum(coeff[1+i]*n[i] for i in range(3))+sum(coeff[4+i]*n[i]**2 for i in range(3))+2*(coeff[7]*n[0]*n[1]+coeff[8]*n[0]*n[2]+coeff[9]*n[1]*n[2])

def composite(c,t=M(0)):
    n,b,l,e=perturb(c,t);r=cross(n,b,l,e);xt=M(c['xt'])*mp.exp(t*M(c['dlnxt']));w=offset(xt,l,r['delta'])
    coeff=[M(v)+M(s)*r['eta_s']+t*M(dv) for v,s,dv in zip(c['coefficient_base'],c['coefficient_slopes'],c['coefficient_data_tangent'])]
    f=field(coeff,r['ns']);din=f+w['offset'];xr=M(c['xr_p'])+t*M(c['dxr_p']);x1=M(c['x1s'])+t*M(c['dx1s']);tau=M(c['tau'])+t*M(c['dtau']);T=mp.exp(-tau/r['qt']);A=1-T;source=xr/(3*x1);out=T*din+A*source
    rate=M('1.3988697202667691e22')*M(c['H_t'])*r['qt']*(source-din)*A
    return {'din':din,'outgoing':out,'field':f,'absolute_in':f+w['ws'],'rate':rate,'energy':M('10.198714553953742')*M('1.602176634e-19')*rate,'offset':w['offset'],'eta_s':r['eta_s']}

def composite_difference(c):
    s=M(c['fd_step']);a=composite(c,-s);b=composite(c,s)
    return {k:(b[k]-a[k])/(2*s) for k in a}
