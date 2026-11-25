"""REC_BIANCHI standalone HMLA state -> calibrated scalar live line.
No upstream recombination executable or history, no BASS. Local frozen bath,
separate dynamic outer reservoirs, no population/thermal writeback.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,math
from pathlib import Path
import numpy as np
from scipy.constants import h,k,c
from numpy.polynomial.legendre import leggauss
from .trajectory.standalone import independent_history
from .recoil.calibrated_source import Bath,compile_isotropic

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def line(x):return ' '.join(format(float(v),'.17g') for v in np.ravel(x))+'\n'
def prepare(data,sub,order=24):
    """Finite quadrature hat volumes, local thermal activity functions,
    and positive reciprocal source graph. Node identity is parent-owned."""
    bounds=data['bounds'];nu=float(data['nu0']);dnu=float(data['dnu']);T=float(data['T_m_K'])
    z0=float(data['z0']);p=sub+1;n=35*p;x=np.linspace(bounds[:,0],bounds[:,1],p,axis=1)
    hats=[[] for _ in range(n)];zr=[[] for _ in range(n)];xx=[[] for _ in range(n)]
    u,w=leggauss(order);u=(1+u)/2;w=w/2
    for i in range(35):
        for j in range(sub):
            l,r=x[i,j:j+2];q=l+(r-l)*u
            weight=8*np.pi*dnu/c**3*(r-l)*w*(nu+dnu*q)**2
            z=np.exp(-h*dnu*q/(k*T))
            for v,hh in [(j,1-u),(j+1,u)]:
                idx=i*p+v;hats[idx].extend(weight*hh);zr[idx].extend(z);xx[idx].extend(q)
    g=np.array([sum(w) for w in hats]);w=[np.asarray(a)/b for a,b in zip(hats,g)]
    zr=[np.asarray(v) for v in zr];xx=[np.asarray(v) for v in xx]
    K=np.zeros((n,n))
    for (i,j),Q in zip(data['pairs'],data[f'Q{sub}']):
        I=slice(i*p,(i+1)*p);J=slice(j*p,(j+1)*p)
        K[I,J]=Q
        if i!=j:K[J,I]=Q.T
    np.fill_diagonal(K,0.)
    assert np.array_equal(K,K.T) and np.min(K)>=0
    return dict(x=x.ravel(),g=g,w=w,z=zr,xx=xx,K=K,T=T,n1s=float(data['n_1s_m3']),nu=nu,dnu=dnu,sub=sub,z0=z0)

def export_graph(q,path):
    with Path(path).open('x') as f:
        f.write(f"rec_calibrated_line_v1\n{len(q['x'])} {q['sub']} {q['nu']:.17g} {q['dnu']:.17g} {q['T']:.17g} {q['n1s']:.17g}\n")
        for x,g,w,z in zip(q['x'],q['g'],q['w'],q['z']):
            f.write(f'{x:.17g} {g:.17g} {len(w)}\n');f.write(line(w));f.write(line(z))
        f.write(line(q['K']))

def initial(q,kind,Tr=None):
    T=q['T'];nu=q['nu'];dnu=q['dnu'];f=[]
    for x,w,z in zip(q['xx'],q['w'],q['z']):
        if kind=='zero':v=np.zeros_like(x)
        elif kind in ('thermal','high_eq','narrow','pulse'):
            a={'thermal':q['z0'],'high_eq':.3,'narrow':.3,'pulse':q['z0']}[kind]
            if kind=='narrow':a=a*(1+.25*np.exp(-.5*((x-1.2)/.22)**2))
            if kind=='pulse':a=a*(1+.15*np.tanh(x/3))
            v=a*z/(1-a*z)
        else:
            t={'hot':T*1.001,'cold':T*.999,'radiation':Tr}.get(kind)
            if t is None or t<=0:raise ValueError('bad radiation initial state')
            v=1/np.expm1(h*(nu+dnu*x)/(k*t))
        f.append(w@v)
    return np.array(f)

def export_case(path,q,f,dt,steps,*,drift=None):
    with Path(path).open('x') as out:
        out.write(f'rec_live_line_case_v1\n{dt:.17g} {steps}\n');out.write(line(f))
        if drift is None:out.write('0\n')
        else:
            ext,extent,dz1,dz2=drift
            edges=np.r_[np.linspace(-extent,-21.25,ext+1),np.linspace(21.25,extent,ext+1)]
            centers=np.r_[(edges[:ext]+edges[1:ext+1])/2,(edges[ext+1:-1]+edges[ext+2:])/2]
            outside=1/np.expm1(h*(q['nu']+q['dnu']*centers)/(k*q['T']))
            out.write(f'1\n{ext} {extent:.17g} {dz1:.17g} {dz2:.17g}\n');out.write(line(outside))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rates',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--z',type=float,default=3000/2.7255-1);p.add_argument('--subcells',type=int,choices=[1,2,4,8],default=4)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--duration',type=float,default=1.);p.add_argument('--steps',type=int,default=4)
    p.add_argument('--initial',choices=['radiation','thermal','hot','cold','narrow','pulse','high_eq','zero'],default='radiation')
    p.add_argument('--exterior',action='store_true')
    a=p.parse_args();a.out.mkdir(exist_ok=False,parents=True)
    hist=independent_history(a.rates,z_end=a.z,points=301,rtol=1e-10,atol=1e-12)
    (a.out/'HISTORY.json').write_text(json.dumps(hist,indent=2,allow_nan=False)+'\n');state=hist['states'][-1]
    bath=Bath(state['T_m_K'],state['n_1s_m3']);d=compile_isotropic(bath,(a.subcells,),a.workers)
    np.savez_compressed(a.out/'SOURCE.npz',**d)
    q=prepare(d,a.subcells);export_graph(q,a.out/'GRAPH.txt')
    f=initial(q,a.initial,state['T_r_K']);dz=-state['H_s']*a.duration
    export_case(a.out/'CASE.txt',q,f,a.duration,a.steps,drift=(8,80.,dz,dz) if a.exterior else None)
    cmd=[str(a.binary.resolve()),str((a.out/'GRAPH.txt').resolve()),str((a.out/'CASE.txt').resolve()),str((a.out/'line').resolve())]
    subprocess.run(cmd,check=True)
    receipt=dict(scope='independent_HMLA_H_neutral_He_then_frozen_scalar_line_tracer',state=state,command=cmd,external_hyrec_runtime=False,external_history=False,rate_hashes=hist['rate_hashes'],hashes={str(f.relative_to(a.out)):sha(f) for f in a.out.rglob('*') if f.is_file()},binary_sha256=sha(a.binary))
    (a.out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
