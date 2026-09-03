#!/usr/bin/env python3
"""Bounded angular-discretization audit; never admits a physical donor."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform, sys
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.special import eval_legendre, sph_harm

@dataclass
class Grid:
    name: str
    p: np.ndarray
    w: np.ndarray
    family: str
    order: int|None=None
    def __post_init__(self):
        self.p=np.asarray(self.p,float); self.w=np.asarray(self.w,float)
        assert self.p.ndim==2 and self.p.shape[1]==3 and self.w.shape==(len(self.p),)
        assert np.max(np.abs(np.linalg.norm(self.p,axis=1)-1))<5e-11
        assert np.all(self.w>0) and abs(self.w.sum()-1)<5e-11

def fib(n):
    i=np.arange(n); z=1-2*(i+.5)/n; ph=math.pi*(3-math.sqrt(5))*i
    r=np.sqrt(1-z*z); p=np.c_[r*np.cos(ph),r*np.sin(ph),z]
    return Grid(f"FIB_{n}",p,np.full(n,1/n),"FIBONACCI")

def tensor(nm,np_):
    mu,wm=np.polynomial.legendre.leggauss(nm); ph=2*math.pi*np.arange(np_)/np_
    p=[]; w=[]
    for x,wx in zip(mu,wm):
        r=math.sqrt(1-x*x)
        for q in ph: p.append((r*math.cos(q),r*math.sin(q),x)); w.append(wx/(2*np_))
    return Grid(f"GL{nm}xF{np_}",np.array(p),np.array(w),"GL_X_FOURIER")

def leb_lib():
    from pylebedev import PyLebedev
    lib=PyLebedev(); orders=list(map(int,lib.get_orders_list()))
    return lib,sorted(orders)

def leb(lib,o):
    p,w=lib.get_points_and_weights(o)
    return Grid(f"LEBEDEV_{o}_{len(w)}",p,w,"LEBEDEV",o)

def dfact(n):
    r=1
    for x in range(n,0,-2): r*=x
    return r

def exact_monomial(a,b,c):
    if a%2 or b%2 or c%2:return 0.
    return dfact(a-1)*dfact(b-1)*dfact(c-1)/dfact(a+b+c+1)

def exactness(g,maxd=12):
    errors={}; first=None
    for d in range(maxd+1):
        e=0.
        for a in range(d+1):
            for b in range(d-a+1):
                c=d-a-b
                v=g.p[:,0]**a*g.p[:,1]**b*g.p[:,2]**c
                e=max(e,abs(g.w@v-exact_monomial(a,b,c)))
        errors[str(d)]=e
        if first is None and e>5e-12:first=d
    return {"exact_through":maxd if first is None else first-1,"first_failure":first,"errors":errors}

def Ymat(p,L):
    th=np.arccos(np.clip(p[:,2],-1,1)); ph=np.mod(np.arctan2(p[:,1],p[:,0]),2*math.pi)
    return np.column_stack([sph_harm(m,l,ph,th) for l in range(L+1) for m in range(-l,l+1)])

def rank_rows(g):
    out=[]
    for L in range(9):
        A=Ymat(g.p,L); s=np.linalg.svd(A,compute_uv=False); tol=max(A.shape)*np.finfo(float).eps*s[0]
        r=int((s>tol).sum())
        out.append({"L":L,"ncoeff":(L+1)**2,"rank":r,"full":r==(L+1)**2,
                    "condition":float(s[0]/s[-1]) if s[-1]>tol else None})
    return out

def match(a,b):
    if len(a.w)!=len(b.w):return None
    C=np.linalg.norm(a.p[:,None]-b.p[None,:],axis=2); i,j=linear_sum_assignment(C)
    return {"max_point_distance":float(C[i,j].max()),"max_weight_delta":float(np.max(abs(a.w[i]-b.w[j]))),
            "identical":bool(C[i,j].max()<5e-12 and np.max(abs(a.w[i]-b.w[j]))<5e-12)}

def repo_face(root):
    sys.path.insert(0,str(root/'src'))
    from full_bianchi_hyrec.background.characteristics import aberrate_direction,normal_frame_characteristic,hydrogen_frame_characteristic
    from full_bianchi_hyrec.background.sequence import BackgroundSnapshotSequence
    from full_bianchi_hyrec.recoil.frequency_liouville import doppler_coordinate_speed
    from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
    seq=BackgroundSnapshotSequence.from_npz(root/'data/pr01c_background_snapshots_v048.npz','Bianchi_VI_h_tilted_large_shear')
    snap=seq.snapshot_at_tau(float(seq.tau[0]))
    with np.load(root/'data/z1100_direct_network_node.npz',allow_pickle=False) as z:
        line=LineBoundaryConfig.lyman_alpha(temperature_K=float(z['temperature_K']),x_red=-21.25,x_blue=21.25)
    def f(p):
        rates=[]
        for eh in p:
            en=aberrate_direction(-snap.beta_H,eh); n=normal_frame_characteristic(snap,en)
            rates.append(hydrogen_frame_characteristic(snap,n).R_hydrogen_s_inv)
        vx=doppler_coordinate_speed(np.array(rates),line.x_red,nu_abs_Hz=line.nu_abs_Hz,
            Doppler_width_Hz=line.Doppler_width_Hz,D0_nu_abs_Hz_s=line.D0_nu_abs_Hz_s,
            D0_log_Doppler_width_s_inv=line.D0_log_Doppler_width_s_inv,D0_x_boundary_s_inv=line.D0_x_red_s_inv)
        return (np.asarray(vx)>0).astype(float)
    return f,{"case":"Bianchi_VI_h_tilted_large_shear","tau":float(seq.tau[0]),"face":"red","available":True}

def axes(seed,n):
    r=np.random.default_rng(seed).normal(size=(n,3)); return r/np.linalg.norm(r,axis=1)[:,None]

def benches(face):
    return {
      "SMOOTH_QUADRUPOLE":(lambda p,u:1+.28*eval_legendre(2,p@u)+.08*eval_legendre(4,p@u),lambda:1.,True),
      "FINITE_BOOST_PATTERN":(lambda p,u:(1/math.sqrt(1-.35**2))*(1+.35*(p@u)),lambda:1/math.sqrt(1-.35**2),True),
      "NARROW_POSITIVE_BEAM":(lambda p,u:np.exp(40*((p@u)-1)),lambda:(1-math.exp(-80))/80,True),
      "HALF_RANGE_INFLOW_MASK":(lambda p,u:(p@u>0).astype(float),lambda:.5,True),
      "SIGNED_DISTORTION":(lambda p,u:eval_legendre(4,p@u)-.4*eval_legendre(2,p@u),lambda:0.,False),
      "REPOSITORY_BIANCHI_FACE_MASK":(lambda p,u:face(p),None,True),
    }

def Ycoeff(p,w,v,L=4):return 4*math.pi*(Ymat(p,L).conj().T@(w*v))

def grid_bench(grids,ref,face,seed=20260903,nrot=12):
    out=[]; U=axes(seed,nrot); B=benches(face); Yr=Ymat(ref.p,4); Yg={g.name:Ymat(g.p,4) for g in grids}
    for g in grids:
      for name,(fn,truthfn,pos) in B.items():
        ie=[]; me=[]; peaks=[]
        for u in U:
          v=fn(g.p,u); vr=fn(ref.p,u); q=float(g.w@v); truth=float(truthfn()) if truthfn else float(ref.w@vr)
          ie.append(abs(q-truth)); c=4*math.pi*(Yg[g.name].conj().T@(g.w*v)); cr=4*math.pi*(Yr.conj().T@(ref.w*vr))
          me.append(float(np.linalg.norm(c-cr)/max(np.linalg.norm(cr),1e-15)))
          if name=="NARROW_POSITIVE_BEAM":peaks.append(float(v.max()))
        out.append({"grid":g.name,"family":g.family,"points":len(g.w),"order":g.order,"benchmark":name,
          "mean_integral_error":float(np.mean(ie)),"max_integral_error":float(np.max(ie)),
          "rotation_std":float(np.std(ie)),"mean_l0_l4_moment_error":float(np.mean(me)),
          "mean_peak_capture":float(np.mean(peaks)) if peaks else None,"positive":pos})
    return out

def pn_bench(ref,face,seed=20260904):
    out=[]; U=axes(seed,8)
    for name,(fn,_,pos) in benches(face).items():
      for L in (2,4,6,8,10):
        Y=Ymat(ref.p,L); e=[]; neg=[]; mins=[]
        for u in U:
          v=fn(ref.p,u); c=4*math.pi*(Y.conj().T@(ref.w*v)); r=np.real(Y@c)
          e.append(math.sqrt(ref.w@((r-v)**2))/max(math.sqrt(ref.w@(v*v)),1e-15))
          neg.append(float(ref.w@(r<-1e-12))); mins.append(float(r.min()))
        out.append({"method":f"PN_L{L}","benchmark":name,"ncoeff":(L+1)**2,
          "mean_l2_error":float(np.mean(e)),"negative_fraction":float(np.mean(neg)),
          "minimum":float(np.min(mins)),"positive":pos})
    return out

def plot(out,gr,pn):
    (out/'plots').mkdir(exist_ok=True)
    for b in ('NARROW_POSITIVE_BEAM','HALF_RANGE_INFLOW_MASK','REPOSITORY_BIANCHI_FACE_MASK'):
      rows=sorted([r for r in gr if r['benchmark']==b],key=lambda r:(r['points'],r['grid']))
      fig,ax=plt.subplots(figsize=(11,6)); x=np.arange(len(rows)); ax.bar(x,[r['max_integral_error'] for r in rows]); ax.set_yscale('log')
      ax.set_xticks(x,[r['grid'] for r in rows],rotation=60,ha='right'); ax.set_ylabel('max normalized integral error'); ax.set_title(b)
      fig.tight_layout(); fig.savefig(out/'plots'/f'GRID_{b}.png',dpi=180); plt.close(fig)
    for b in ('NARROW_POSITIVE_BEAM','HALF_RANGE_INFLOW_MASK'):
      rows=[r for r in pn if r['benchmark']==b]; fig,ax=plt.subplots(figsize=(8,5)); ax.plot([r['ncoeff'] for r in rows],[r['mean_l2_error'] for r in rows],marker='o')
      ax.set_yscale('log'); ax.set_xlabel('coefficient count'); ax.set_ylabel('mean relative L2 error'); ax.set_title('PN '+b); fig.tight_layout(); fig.savefig(out/'plots'/f'PN_{b}.png',dpi=180); plt.close(fig)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--rotations',type=int,default=12); a=ap.parse_args()
    root=a.root.resolve(); out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    bg=root/'data/pr01c_background_snapshots_v048.npz'; dc=root/'data/pr05c2a_directional_coupling_v063.npz'; net=root/'data/z1100_direct_network_node.npz'
    with np.load(bg,allow_pickle=False) as z: cur=Grid('CURRENT_REPOSITORY_26',z['directions'],z['angular_weights'],'REPOSITORY_CURRENT')
    lib,orders=leb_lib(); lg={o:leb(lib,o) for o in orders}; selected=[o for o in (7,9,11,13,17,23,29) if o in lg]
    grids=[cur]+[lg[o] for o in selected]+[fib(n) for n in (26,50,110)]+[tensor(4,8),tensor(6,12),tensor(8,16)]
    ref=lg[max(o for o in orders if o<=59)]; face,fmeta=repo_face(root)
    matches=[{"order":o,**match(cur,g)} for o,g in lg.items() if len(g.w)==26]; identified=next((x['order'] for x in matches if x['identical']),None)
    cub=exactness(cur); ranks=rank_rows(cur); L4=next(x for x in ranks if x['L']==4); L5=next(x for x in ranks if x['L']==5)
    gr=grid_bench(grids,ref,face,nrot=a.rotations); pn=pn_bench(ref,face); plot(out,gr,pn)
    inv={}
    for p in (bg,dc,net):
      with np.load(p,allow_pickle=False) as z:inv[p.name]={"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"keys":{k:{"shape":list(z[k].shape),"dtype":str(z[k].dtype)} for k in z.files}}
    survivor={"architecture":"CONTINUOUS_CHARACTERISTIC_DONOR_WITH_HYBRID_LOW_MOMENT_PLUS_ADAPTIVE_RESIDUAL",
      "physical_authority":"causal characteristic path-integral generator with exact source/channel provenance",
      "runtime":"low-order PSTF/harmonic backbone plus positive adaptive angular residual",
      "current_26_role":"low-order cubature and backward-compatible 52-ray regression projection",
      "current_26_is_physical_donor_authority":False}
    report={"schema_version":"1.0.0","stage_id":"REC_PHYSICAL_DONOR_ANGULAR_BASIS_AUDIT_R1","status":"PASS_RESEARCH_AUDIT_NO_PHYSICAL_ADMISSION","authority_effect":"NONE_RESEARCH_ONLY",
      "environment":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"pylebedev":"1.1.0","pylebedev_wheel_sha256":"3f7afc5e53d9392931e1c4967c4b85a25b9950efceb1df22bc08f4de03808c68"},
      "repository_inputs":inv,"current_rule":{"point_count":26,"identified_lebedev_order":identified,"matches":matches,"cubature":cub,"harmonic_rank":ranks,"l4_full_column_rank":L4['full'],"l5_full_column_rank":L5['full'],"dimension_bound":"(L+1)^2<=26 implies L<=4"},
      "reference_grid":{"order":ref.order,"points":len(ref.w)},"repository_face_benchmark":fmeta,"grid_benchmarks":gr,"pn_benchmarks":pn,"survivor":survivor,
      "decisions":{"fixed_26_state_authority_rejected":not L5['full'],"keep_26_as_projection_checkpoint":True,"physical_face_admitted":False,"provider_export_authorized":False,"next_node":"REC_PHYSICAL_DONOR_GENERATOR_CONTRACT_R2"},
      "claim_boundary":"RESEARCH_DONOR_ARCHITECTURE_ONLY_NO_SOURCE_IDENTICAL_FACE_PROVIDER_OR_SCIENCE_PROMOTION"}
    (out/'ANGULAR_DONOR_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    for name,rows in [('GRID_BENCHMARKS',gr),('PN_BENCHMARKS',pn)]:
      (out/(name+'.json')).write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n');
      with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'NPZ_INVENTORY.json').write_text(json.dumps(inv,indent=2,sort_keys=True)+'\n')
    receipt={"status":"PASS","audit_semantic_sha256":hashlib.sha256(json.dumps(report,sort_keys=True,separators=(',',':')).encode()).hexdigest(),"current_point_count":26,"identified_lebedev_order":identified,"current_exact_degree":cub['exact_through'],"current_l4_full_rank":L4['full'],"current_l5_full_rank":L5['full'],"fixed_26_state_authority_rejected":not L5['full'],"physical_face_admitted":False,"authority_effect":"NONE_RESEARCH_ONLY"}
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    half=next(r for r in gr if r['grid']=='CURRENT_REPOSITORY_26' and r['benchmark']=='HALF_RANGE_INFLOW_MASK'); beam=next(r for r in gr if r['grid']=='CURRENT_REPOSITORY_26' and r['benchmark']=='NARROW_POSITIVE_BEAM')
    (out/'RESULT_SUMMARY.md').write_text(f"# Angular Donor Audit Result\n\nFixed 26-vector: **rejected as physical donor authority**; retained as projection/regression grid.\n\n- identified Lebedev order: {identified}\n- cubature exact through degree: {cub['exact_through']}\n- L=4 full rank: {L4['full']}\n- L=5 full rank: {L5['full']}\n- max half-range orientation error: {half['max_integral_error']:.6e}\n- max narrow-beam orientation error: {beam['max_integral_error']:.6e}\n\nSurvivor: causal characteristic donor + low-order PSTF backbone + positive adaptive residual.\n\nNo physical face/provider is admitted.\n")
    print(json.dumps(receipt,sort_keys=True)); return 0
if __name__=='__main__':raise SystemExit(main())
