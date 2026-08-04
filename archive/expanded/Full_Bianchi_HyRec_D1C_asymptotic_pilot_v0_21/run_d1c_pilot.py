import csv, hashlib, itertools, json, math, shutil, time, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from scipy.constants import c,h,k,physical_constants
from scipy.special import wofz

ROOT=Path('/mnt/data')
BASE_DIR=ROOT/'Full_Bianchi_HyRec_D1B_domain_convergence_v0_20'
REG_DIR=ROOT/'Full_Bianchi_HyRec_D1_adaptive_wing_registry_v0_19'
OUT=ROOT/'Full_Bianchi_HyRec_D1C_asymptotic_pilot_v0_21'
OUT.mkdir(parents=True,exist_ok=True)

# -------------------------- inputs ----------------------------------
base=np.load(BASE_DIR/'D1B_conductance.npz',allow_pickle=True)
reg=np.load(REG_DIR/'adaptive_wing_registry.npz',allow_pickle=True)
S29=np.asarray(base['full29_conductance_high'],float)
Pi29=np.asarray(base['equilibrium_weight'],float)
base_edges=np.asarray(base['x_edges'],float)
directions=np.asarray(base['directions'],float)
ang_w=np.asarray(base['angular_weights'],float)
cache=pd.read_csv(BASE_DIR/'wing_orbit_cache.csv')
cells29=pd.read_csv(REG_DIR/'adaptive_frequency_cells.csv')
cal_path=Path('/tmp/hummer_uv_calibration.csv')
if not cal_path.exists():
    raise FileNotFoundError('Run /tmp/calibrate_uv.py first')
cal=pd.read_csv(cal_path)

# -------------------------- physics ---------------------------------
T=3000.0
lam=1215.6701e-10
nu_int=c/lam
M=physical_constants['atomic mass constant'][0]*1.00782503223
vD=math.sqrt(2*k*T/M)
dnu=nu_int*vD/c
A21=6.265e8
a=A21/(4*math.pi*dnu)
eps=h*nu_int/(M*c**2)
g=eps/(vD/c)
delta=dnu/nu_int
eta=h*dnu/(k*T)
eabs=2*eps/(1+math.sqrt(1-2*eps))
nu_abs=eabs*M*c**2/h

# Gauss caches
quad={n:leggauss(n) for n in [24,32,40,48,64,80]}

def H(a0,x): return np.real(wofz(np.asarray(x)+1j*a0))
def pi_density_x(x): return (1+delta*np.asarray(x))**2*np.exp(-eta*np.asarray(x))

# Generic Hummer II conductance integral in rotated (u,z) coordinates.
def hummer_generic(cell_o,cell_i,mu,nz=32,nu=32):
    ao,bo=cell_o; ai,bi=cell_i
    shift=g*(1-mu)
    A=ao+shift; B=bo+shift
    ss=math.sqrt((1-mu)/2); cc=math.sqrt((1+mu)/2)
    zmin=(A-bi)/(2*ss); zmax=(B-ai)/(2*ss)
    breaks=[zmin,zmax,(A-ai)/(2*ss),(B-bi)/(2*ss)]
    if zmin<0<zmax: breaks.append(0.0)
    breaks=sorted(set(round(max(zmin,min(zmax,x)),15) for x in breaks))
    zz,wz=quad[nz]; uu,wu=quad[nu]
    total=0.0
    for zl,zr in zip(breaks[:-1],breaks[1:]):
        if zr<=zl: continue
        zs=.5*(zl+zr)+.5*(zr-zl)*zz; zws=.5*(zr-zl)*wz
        for z,wzz in zip(zs,zws):
            umin=max((A-ss*z)/cc,(ai+ss*z)/cc)
            umax=min((B-ss*z)/cc,(bi+ss*z)/cc)
            if umax<=umin: continue
            us=.5*(umin+umax)+.5*(umax-umin)*uu; uws=.5*(umax-umin)*wu
            xo=cc*us+ss*z-shift; xi=cc*us-ss*z
            other=((1+delta*xo)/(1+delta*xi))*pi_density_x(xi)
            total += wzz*math.exp(-z*z)/math.pi*np.sum(uws*H(a/cc,us)*other)
    return float(total)

# Exact backscattering limit with rational u=a tan(theta).
def hummer_back(cell_o,cell_i,nv=80,nt=64):
    ao,bo=cell_o; ai,bi=cell_i
    A=ao+2*g; B=bo+2*g
    vmin=(A-bi)/2; vmax=(B-ai)/2
    breaks=[vmin,vmax,(A-ai)/2,(B-bi)/2]
    if vmin<0<vmax: breaks.append(0.0)
    breaks=sorted(set(round(max(vmin,min(vmax,x)),15) for x in breaks))
    zv,wv=quad[nv]; zt,wt=quad[nt]
    total=0.0
    for vl,vr in zip(breaks[:-1],breaks[1:]):
        if vr<=vl: continue
        vs=.5*(vl+vr)+.5*(vr-vl)*zv; vws=.5*(vr-vl)*wv
        for v,wvv in zip(vs,vws):
            umin=max(A-v,ai+v); umax=min(B-v,bi+v)
            if umax<=umin: continue
            thmin=math.atan(umin/a); thmax=math.atan(umax/a)
            th=.5*(thmin+thmax)+.5*(thmax-thmin)*zt; tw=.5*(thmax-thmin)*wt
            u=a*np.tan(th); xo=u+v-2*g; xi=u-v
            other=((1+delta*xo)/(1+delta*xi))*pi_density_x(xi)
            total += wvv*math.exp(-v*v)/(math.pi**1.5)*np.sum(tw*other)
    return float(total)

def hummer_pair(cell_a,cell_b,mu,high=False):
    if abs(mu+1)<1e-13:
        n1,n2=(80,64) if not high else (80,80)
        f=hummer_back(cell_a,cell_b,n1,n2)
        r=hummer_back(cell_b,cell_a,n1,n2)
    else:
        n=32 if not high else 40
        f=hummer_generic(cell_a,cell_b,mu,n,n)
        r=hummer_generic(cell_b,cell_a,mu,n,n)
    if f==0 and r==0: return 0.0,0.0
    rec=abs(f-r)/(abs(f)+abs(r)+1e-300)
    return .5*(f+r),rec

# --------------------- calibration model -----------------------------
merge=cache.merge(cal[['fi','fj','mu','log_hummer']],left_on=['frequency_i','frequency_j','mu'],right_on=['fi','fj','mu'],how='left').dropna()
# edge contribution weights by orbit
edge_a=reg['edge_a']; edge_b=reg['edge_b']; edge_oid=reg['edge_physics_orbit_id']
active=reg['recommended_active'].astype(bool); core_core=reg['edge_core_core'].astype(bool)
orbit_sq={}
for e in np.where(active & ~core_core)[0]:
    o=int(edge_oid[e]); ia=int(edge_a[e]); ib=int(edge_b[e])
    orbit_sq[o]=orbit_sq.get(o,0.0)+S29[ia,ib]**2
merge['weight']=[orbit_sq.get(int(o),0.0) for o in merge.physics_orbit_id]
xi=np.array([cells29.iloc[int(i)].x_center for i in merge.frequency_i],float)
xj=np.array([cells29.iloc[int(j)].x_center for j in merge.frequency_j],float)
muarr=merge.mu.values.astype(float)
mean=.5*(xi+xj); diff=.5*(xj-xi)
y=(merge.log_high-merge.log_hummer).values

def design(m,d,u):
    return np.column_stack([
        np.ones_like(m),m,m**2,m**3,m**4,m**5,d**2,d**4,u,u**2,u**3,
        m*u,m**2*u,d**2*u,m*d**2,m*u**2
    ])
feature_names=['1','m','m2','m3','m4','m5','d2','d4','u','u2','u3','mu','m2u','d2u','md2','mu2']
X=design(mean,diff,muarr)
wt=merge.weight.values; wt=wt/(wt.max()+1e-300); W=np.sqrt(wt+1e-30)
coef_full=np.linalg.lstsq(X*W[:,None],y*W,rcond=None)[0]
train=~((merge.frequency_i==0)|(merge.frequency_j==28))
Wt=np.sqrt(wt[train]+1e-30)
coef_hold=np.linalg.lstsq(X[train]*Wt[:,None],y[train]*Wt,rcond=None)[0]

def correction(xa,xb,mu,coef):
    m=.5*(xa+xb); d=.5*(xb-xa)
    return float(design(np.array([m]),np.array([d]),np.array([mu]))@coef)

# C_edge maps cached physics log to edge conductance after angular weights/phase.
# derive from exact overlap samples
mu_pairs={}
for muv in sorted(cache.mu.unique()):
    found=None
    for q in range(26):
        for r in range(26):
            if q!=r and abs(np.dot(directions[q],directions[r])-muv)<1e-12:
                found=(q,r);break
        if found:break
    mu_pairs[float(muv)]=found
cedge=[]
for _,row in cache.sample(min(800,len(cache)),random_state=7).iterrows():
    fi,fj,muv=int(row.frequency_i),int(row.frequency_j),float(row.mu)
    q,r=mu_pairs[muv]; sval=S29[fi*26+q,fj*26+r]
    if sval<=0: continue
    phase=.75*(1+muv*muv)
    cedge.append(float(row.log_high)+math.log(ang_w[q]*ang_w[r]*phase)-math.log(sval))
C_EDGE=float(np.mean(cedge))

# calibration metrics
pred_full=X@coef_full; pred_hold=X@coef_hold
cal_metrics={
    'full_weighted_log_rms':float(math.sqrt(np.sum(wt*(y-pred_full)**2)/np.sum(wt))),
    'holdout_outer_weighted_log_rms':float(math.sqrt(np.sum(wt[~train]*(y[~train]-pred_hold[~train])**2)/(np.sum(wt[~train])+1e-300))),
    'full_unweighted_log_std':float(np.std(y-pred_full)),
    'C_edge':C_EDGE,
}

# matrix overlap residual for full calibration
logH={int(r.physics_orbit_id):float(r.log_hummer) for _,r in merge.iterrows()}
pcorr={int(r.physics_orbit_id):float(v) for v,r in zip(pred_full,[r for _,r in merge.iterrows()])}
# safer mapping from dataframe order
pcorr={int(merge.iloc[i].physics_orbit_id):float(pred_full[i]) for i in range(len(merge))}
err=norm=0.0
for e in np.where(active & ~core_core)[0]:
    o=int(edge_oid[e])
    if o not in logH: continue
    ia=int(edge_a[e]); ib=int(edge_b[e]); qa=ia%26; qb=ib%26
    muv=float(np.dot(directions[qa],directions[qb])); phase=.75*(1+muv*muv)
    pred=math.exp(logH[o]+pcorr[o]-C_EDGE)*ang_w[qa]*ang_w[qb]*phase
    true=S29[ia,ib]; err+=(pred-true)**2; norm+=true**2
cal_metrics['overlap_matrix_relative_Frobenius']=float(math.sqrt(err/norm))

# --------------------- domain builders -------------------------------
base_new_edges={
    '10.25':base_edges,
    '12.75':np.concatenate(([-12.75],base_edges,[12.75])),
    '16.25':np.concatenate(([-16.25,-12.75],base_edges,[12.75,16.25])),
    '21.25':np.concatenate(([-21.25,-16.25,-12.75],base_edges,[12.75,16.25,21.25])),
}

# angular matrices grouped by mu
mu_mat=np.round(directions@directions.T,15)
unique_mu=sorted(set(mu_mat.ravel()))
# snap to cache mu classes plus 1
mu_classes=sorted(list(cache.mu.unique())+[1.0])
def snap_mu(x): return min(mu_classes,key=lambda z:abs(z-x))
mu_mat=np.vectorize(snap_mu)(mu_mat)
ang_factor=np.outer(ang_w,ang_w)*.75*(1+mu_mat**2)
np.fill_diagonal(ang_factor,0.0)  # same-ray cross-frequency disabled as in v0.20

# Pi normalization from base
zg,wg=leggauss(40)
def cell_pi_raw(xl,xr):
    x=.5*(xl+xr)+.5*(xr-xl)*zg; nu=nu_abs+x*dnu
    return .5*(xr-xl)*np.sum(wg*nu**2*np.exp(-h*nu/(k*T)))
raw29=np.array([cell_pi_raw(base_edges[i],base_edges[i+1]) for i in range(29)])
pi_scale=float(np.mean([Pi29[i*26+q]/(ang_w[q]*raw29[i]) for i in range(29) for q in [0,6,18]]))

orbit_cache_new={}
max_recip=0.0; max_quad_rel=0.0

def build_domain(edges,coef,label):
    global max_recip,max_quad_rel
    nc=len(edges)-1; ns=nc*26
    centers=.5*(edges[:-1]+edges[1:])
    S=np.zeros((ns,ns),float)
    # embed old 29 block at offset
    off=(nc-29)//2
    old_idx=np.concatenate([np.arange((off+i)*26,(off+i+1)*26) for i in range(29)])
    S[np.ix_(old_idx,old_idx)]=S29
    cells=[(float(edges[i]),float(edges[i+1])) for i in range(nc)]
    oldset=set(range(off,off+29))
    # new frequency pair blocks
    for i in range(nc):
        for j in range(i,nc):
            if i in oldset and j in oldset: continue
            block=np.zeros((26,26),float)
            for muv in unique_mu:
                if abs(muv-1.0)<1e-12: continue
                key=(round(cells[i][0],8),round(cells[i][1],8),round(cells[j][0],8),round(cells[j][1],8),round(float(muv),12))
                if key not in orbit_cache_new:
                    val,rec=hummer_pair(cells[i],cells[j],float(muv),False)
                    valh,rech=hummer_pair(cells[i],cells[j],float(muv),True)
                    qrel=abs(valh-val)/(abs(valh)+1e-300)
                    orbit_cache_new[key]=(valh,max(rec,rech),qrel)
                val,rec,qrel=orbit_cache_new[key]
                max_recip=max(max_recip,rec); max_quad_rel=max(max_quad_rel,qrel)
                if val<=0: orb=0.0
                else:
                    corr=correction(centers[i],centers[j],float(muv),coef)
                    logedge=math.log(val)+corr-C_EDGE
                    orb=0.0 if logedge<-745 else math.exp(logedge)
                mask=np.isclose(mu_mat,muv,atol=1e-12)
                block[mask]=orb*ang_factor[mask]
            if i==j: np.fill_diagonal(block,0.0)
            ia=slice(i*26,(i+1)*26); jb=slice(j*26,(j+1)*26)
            S[ia,jb]=block
            if i!=j: S[jb,ia]=block.T
    raw=np.array([cell_pi_raw(edges[i],edges[i+1]) for i in range(nc)])
    Pi=np.concatenate([pi_scale*raw[i]*ang_w for i in range(nc)])
    return {'label':label,'edges':edges,'centers':centers,'S':S,'Pi':Pi,'offset':off}

models={'fullfit':coef_full,'holdout':coef_hold}
domains={}
t0=time.time()
for mname,coef in models.items():
    domains[mname]={}
    for dname,edges in base_new_edges.items():
        if dname=='10.25':
            domains[mname][dname]={'label':dname,'edges':edges,'centers':.5*(edges[:-1]+edges[1:]),'S':S29.copy(),'Pi':Pi29.copy(),'offset':0}
        else:
            print('building',mname,dname,flush=True)
            domains[mname][dname]=build_domain(edges,coef,dname)
print('build seconds',time.time()-t0,'new orbit evals',len(orbit_cache_new),flush=True)

# ------------------- action/moment diagnostics -----------------------
def state_arrays(dom):
    x=np.repeat(dom['centers'],26); n=np.tile(directions,(len(dom['centers']),1)); nu=nu_abs+x*dnu
    return x,n,nu

def taper_abs(x,inner=6.0,outer=9.0):
    ax=np.abs(x); t=np.ones_like(ax); t[ax>=outer]=0.0
    mask=(ax>inner)&(ax<outer); t[mask]=np.cos(.5*math.pi*(ax[mask]-inner)/(outer-inner))**2
    return t

def q_states(dom):
    x,n,nu=state_arrays(dom); nz=n[:,2]; tap=taper_abs(x)
    return {
      'BE_equilibrium':np.ones_like(x),
      'smooth_L8':1+.05*np.cos(x/8),
      'smooth_L2':1+.05*np.cos(x/2),
      'narrow_core':1+.10*np.exp(-.5*(x/.4)**2),
      'angular_dipole':1+.08*nz,
      'angular_quadrupole':1+.03*(3*nz*nz-1),
      'red_blue_crossing':1+.04*x*nz,
      'tapered_L8':1+.05*np.cos(x/8)*tap,
      'tapered_red_blue':1+.04*x*nz*tap,
      'compact_gaussian':1+.10*np.exp(-.5*(x/2)**2),
      'wing_localized':1+.10*np.exp(-.5*((np.abs(x)-9)/.7)**2),
    }

def action(S,q):
    return S@q-S.sum(axis=1)*q

def entropy(S,q):
    # -1/2 sum_ab S_ab(qa-qb)^2
    d=q[:,None]-q[None,:]
    return -.5*float(np.sum(S*d*d))

def fourforce(A,dom):
    x,n,nu=state_arrays(dom); ratio=nu/nu_int
    p=np.column_stack([ratio,ratio[:,None]*n])
    return p.T@A

def moments(dom):
    S=dom['S'];Pi=dom['Pi'];x,n,nu=state_arrays(dom)
    K=S/Pi[None,:]; gam=K.sum(axis=0); out={'opacity':gam}
    dxm=x[:,None]-x[None,:]
    for r in range(1,5): out[f'M{r}']=np.sum(K*dxm**r,axis=0)/(gam+1e-300)
    return out

sequence=['10.25','12.75','16.25','21.25']
action_rows=[]; model_rows=[]; moment_rows=[]; boundary_rows=[]
# fullfit nested domain convergence
for small,large in zip(sequence[:-1],sequence[1:]):
    ds=domains['fullfit'][small]; dl=domains['fullfit'][large]
    offset=(len(dl['centers'])-len(ds['centers']))//2
    idx=np.concatenate([np.arange((offset+i)*26,(offset+i+1)*26) for i in range(len(ds['centers']))])
    qs=q_states(ds); ql=q_states(dl)
    ms=moments(ds); ml=moments(dl)
    for name in qs:
        As=action(ds['S'],qs[name]); Al=action(dl['S'],ql[name]); Ali=Al[idx]
        den=np.linalg.norm(Ali)+1e-300
        Qs=fourforce(As,ds); Ql=fourforce(Al,dl)
        action_rows.append({
          'small_domain':small,'large_domain':large,'state':name,
          'small_action_norm':float(np.linalg.norm(As)),
          'large_restricted_action_norm':float(np.linalg.norm(Ali)),
          'domain_relative':float(np.linalg.norm(Ali-As)/den),
          'small_entropy':entropy(ds['S'],qs[name]),'large_entropy':entropy(dl['S'],ql[name]),
          'small_number_residual':float(abs(As.sum())),'large_number_residual':float(abs(Al.sum())),
          'fourforce_relative':float(np.linalg.norm(Ql-Qs)/(np.linalg.norm(Ql)+1e-300)),
        })
        # boundary identity: cross contribution on inner + action on outer
        outer=np.setdiff1d(np.arange(len(Al)),idx)
        cross=dl['S'][np.ix_(idx,outer)]@ql[name][outer]-dl['S'][np.ix_(idx,outer)].sum(axis=1)*ql[name][idx]
        boundary_rows.append({
          'small_domain':small,'large_domain':large,'state':name,
          'inner_cross_sum':float(cross.sum()),'outer_action_sum':float(Al[outer].sum()),
          'boundary_number_identity_residual':float(cross.sum()+Al[outer].sum())
        })
    # moments common states
    for key in ['opacity','M1','M2','M3','M4']:
        a1=ms[key];a2=ml[key][idx];diffv=a2-a1
        moment_rows.append({
          'small_domain':small,'large_domain':large,'quantity':key,
          'max_abs':float(np.max(np.abs(diffv))),
          'max_rel':float(np.max(np.abs(diffv)/(np.abs(a2)+1e-14))),
          'rms_rel':float(np.linalg.norm(diffv)/(np.linalg.norm(a2)+1e-300))
        })
# surrogate model spread at each domain and state
for dname in sequence[1:]:
    dfull=domains['fullfit'][dname]; dhold=domains['holdout'][dname]
    qf=q_states(dfull)
    for name,q in qf.items():
        Af=action(dfull['S'],q); Ah=action(dhold['S'],q)
        model_rows.append({'domain':dname,'state':name,'relative_action_spread':float(np.linalg.norm(Af-Ah)/(np.linalg.norm(Af)+1e-300))})

# summarize matrices, generators and conservation fullfit
matrix_meta={}
npz_payload={}
for dname in sequence:
    d=domains['fullfit'][dname];S=d['S'];Pi=d['Pi'];K=S/Pi[None,:];G=K.copy();np.fill_diagonal(G,0);np.fill_diagonal(G,-G.sum(axis=0))
    matrix_meta[dname]={
      'cells':len(d['centers']),'states':len(Pi),'conductance_symmetry':float(np.max(np.abs(S-S.T))),
      'left_null':float(np.max(np.abs(np.ones(len(Pi))@G))),
      'right_null':float(np.max(np.abs(G@Pi))),
      'min_conductance':float(S[S>0].min()) if np.any(S>0) else 0.0,
    }
    npz_payload[f'edges_{dname}']=d['edges'];npz_payload[f'centers_{dname}']=d['centers'];npz_payload[f'Pi_{dname}']=Pi;npz_payload[f'S_{dname}']=S
np.savez_compressed(OUT/'nested_wing_conductance.npz',classification=np.asarray('D1C_CALIBRATED_HUMMER_ASYMPTOTIC_PILOT'),directions=directions,angular_weights=ang_w,**npz_payload)

# write CSVs
def write_csv(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0].keys()));wr.writeheader();wr.writerows(rows)
write_csv('nested_domain_actions.csv',action_rows)
write_csv('surrogate_model_spread.csv',model_rows)
write_csv('nested_moment_convergence.csv',moment_rows)
write_csv('boundary_flux_ledger.csv',boundary_rows)
# calibration coefficients
coeff_data={'features':feature_names,'fullfit':coef_full.tolist(),'outer_holdout':coef_hold.tolist(),'metrics':cal_metrics,'C_edge':C_EDGE}
(OUT/'calibration_coefficients.json').write_text(json.dumps(coeff_data,indent=2),encoding='utf-8')
shutil.copy(cal_path,OUT/'overlap_hummer_calibration.csv')

# decisions
df_actions=pd.DataFrame(action_rows);df_models=pd.DataFrame(model_rows)
compact_states=['narrow_core','tapered_L8','tapered_red_blue','compact_gaussian','angular_dipole','angular_quadrupole']
decisions=[]
for small,large in zip(sequence[:-1],sequence[1:]):
    sub=df_actions[(df_actions.small_domain==small)&(df_actions.large_domain==large)&(df_actions.state.isin(compact_states))]
    maxerr=float(sub.domain_relative.max());state=str(sub.loc[sub.domain_relative.idxmax(),'state'])
    mod=float(df_models[(df_models.domain==large)&(df_models.state.isin(compact_states))].relative_action_spread.max()) if large!='10.25' else 0
    decisions.append({'small':small,'large':large,'max_compact_domain_error':maxerr,'worst_compact_state':state,'max_surrogate_spread':mod,'robust_gate':('FAIL' if maxerr>1e-4+mod else 'CONDITIONAL')})

ledger={
 'classification':'D1C_CALIBRATED_HUMMER_ASYMPTOTIC_NESTED_WING_PILOT',
 'stage':'C2d2C2-D1C-A',
 'source':'v0.20 exact core+initial wing; new outer cells use Hummer-II recoil/phase-space kernel calibrated to v0.20 COM-KHW wing cache',
 'domains':{k:{'xmax':float(max(abs(v[0]),abs(v[-1]))),'cells':len(v)-1,'states':(len(v)-1)*26} for k,v in base_new_edges.items()},
 'calibration':cal_metrics,
 'quadrature':{'generic':'rotated (u,z), GL32 main/GL40 audit','backscatter':'rational u=a tan(theta), v80 theta64/80'},
 'new_orbit_evaluations':len(orbit_cache_new),'max_pair_reciprocity':max_recip,'max_low_high_orbit_relative':max_quad_rel,
 'matrix_invariants':matrix_meta,
 'nested_decisions':decisions,
 'limitations':[
   'This is an asymptotic outer-wing pilot, not the full COM-KHW event-integrated D1C production kernel.',
   'The calibrated correction has 3.75e-5 overlap matrix error and about 7.35e-5 weighted outer holdout log RMS.',
   'Cells beyond |x|=10.25 are extrapolated from a low-order COM/KHW correction fitted on v0.20.',
   'The v0.20 block is embedded unchanged.'
 ],
 'next_stage':{'name':'D1C-B_exact_outer_orbits_or_boundary_closure','tasks':[
   'If nested errors remain above the surrogate spread, extend exact COM-KHW orbit integration to the required outer boundary.',
   'If errors fall to the surrogate floor, replace the calibrated model by exact outer-orbit evaluation before declaring convergence.',
   'Keep wing-localized states in a separate boundary-interface lane coupled to Liouville and true emission/absorption.'
 ]}
}
(OUT/'D1C_ledger.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')

formalism='''# D1C calibrated far-wing pilot\n\nThe new outer-wing conductance uses the observer-frame Hummer-II kernel\nwith recoil shift and the photon phase-space detailed-balance factor.\nFor -1<mu<1, define\n\nX=x_o+g(1-mu),  Y=x_i,\nX=c u+s z,       Y=c u-s z,\n\nc=sqrt((1+mu)/2), s=sqrt((1-mu)/2).\n\nThe Jacobian cancels the prefactor:\n\nr_II dX dY = exp(-z^2) H(a/c,u) du dz / pi.\n\nAt mu=-1 the exact finite limit is integrated with u=a tan(theta).\nA low-order log-correction in mean detuning, frequency separation and mu\nis fitted to the immutable v0.20 wing cache.  The full-fit and an\nouter-cell holdout fit define the surrogate uncertainty band.\n\nExisting |x|<=10.25 conductance entries are never replaced.\n'''
(OUT/'ASYMPTOTIC_FORMALISM.md').write_text(formalism,encoding='utf-8')
readme=f'''# Full Bianchi-HyRec D1C asymptotic pilot v0.21\n\nThis artifact extends the immutable v0.20 conductance to nested symmetric\ndomains |x|=12.75,16.25,21.25 with a calibrated Hummer-II far-wing lane.\n\nIt is intentionally classified as a pilot: the overlap matrix error of the\ncalibration is {cal_metrics['overlap_matrix_relative_Frobenius']:.6e}, and the\nouter holdout uncertainty is recorded separately.\n\nSee D1C_ledger.json and nested_domain_actions.csv for the domain decision.\n'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
# reproducibility: copy this script
shutil.copy('/tmp/run_d1c_pilot.py',OUT/'run_d1c_pilot.py')
# manifest and zip
manifest=[]
for p in sorted(OUT.iterdir()):
    if p.name=='MANIFEST_SHA256.txt':continue
    manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
(OUT/'MANIFEST_SHA256.txt').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
zip_path=ROOT/'Full_Bianchi_HyRec_D1C_asymptotic_pilot_v0_21.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(OUT.iterdir()): zf.write(p,arcname=f'{OUT.name}/{p.name}')
print(json.dumps({'zip':str(zip_path),'calibration':cal_metrics,'decisions':decisions,'max_recip':max_recip,'max_quad_rel':max_quad_rel,'seconds':time.time()-t0},indent=2))
