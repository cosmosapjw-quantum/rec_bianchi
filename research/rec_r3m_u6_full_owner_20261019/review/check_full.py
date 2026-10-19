import sys, json, math, hashlib, zipfile
import sys as _s; _s.path.insert(0,"/home/cosmosapjw/.local/lib/python3.12/site-packages")
import numpy as np
R="/home/cosmosapjw/rec_theory_runs/REC_R3M_U6_PILOT_20261019"
CK=R+"/checkout"; EV=R+"/evidence_full_001/full5210_stored"; PI=R+"/evidence_001/pilot128_stored"
sys.path.insert(0, CK+"/src"); sys.path.insert(1, "/home/cosmosapjw/.local/lib/python3.12/site-packages")
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u6_rt_boundary import START_IZ, RT_IZ, PREFIX_COLUMNS
LINE_EV=(10.198714553953742,12.087365397278509,12.748393192442178)  # verify_r3i_h2_u5_thermal.py:40
KB_EV_K=8.617343e-5  # :41
c=HyRec2012Cosmology()
table=OriginalHyRecTwoPhotonRamanTable.from_archive(CK+"/archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
E=np.asarray(table.energy_eV,dtype=float); assert E.shape==(311,)
out={}
z=np.load(EV+"/python_u6_rt.npz",allow_pickle=False)
V=z["virtual_out"];A=z["average_virtual"];L=z["lyman_out"]
states=[json.loads(s) for s in z["states_json"]]; steps=[json.loads(s) for s in z["steps_json"]]
n=len(steps); out["n_steps"]=n; out["n_states"]=len(states)
out["shapes"]=[V.shape,A.shape,L.shape,str(V.dtype)]
out["npz_finite"]=bool(np.isfinite(V).all() and np.isfinite(A[:,PREFIX_COLUMNS:]).all() and np.isfinite(L).all())
out["avg_prefix_finite_frac"]=float(np.isfinite(A[:,:PREFIX_COLUMNS]).mean())
# parse CSV
tags={k:[] for k in ("V","A","L","PV","PL","STEP")}; seq=[]; other={}
with open(EV+"/native_oracle_stdout.csv") as f:
    for line in f:
        t,_,rest=line.rstrip("\n").partition(",")
        if t in ("V","A","L"):
            tags[t].append(rest); seq.append(t)
        elif t in ("PV","PL"): tags[t].append(rest)
        elif t=="STEP": tags[t].append(rest); seq.append("S")
        else: other.setdefault(t,[]).append(rest)
out["counts"]={k:len(v) for k,v in tags.items()}|{k:len(v) for k,v in other.items()}
out["END"]=other["END"]
# sequence check: per step S then 311V 311A 3L
exp=("S"+"V"*311+"A"*311+"L"*3)*n
out["sequence_ok"]=("".join(seq)==exp)
def arr(rows,k):
    a=[r.split(",") for r in rows]
    ib=np.array([[int(x[0]),int(x[1])] for x in a]); v=np.array([float(x[2]) for x in a])
    return ib,v
z_in=np.array([s["z"] for s in states[:n]])
tr=KB_EV_K*c.T0_K*(1.+z_in)
res={}
for t,P,EN,nb in (("V",V,E,311),("A",A,E,311),("L",L,np.array(LINE_EV),3)):
    ib,cv=arr(tags[t],t)
    ei=np.repeat(np.arange(n),nb); eb=np.tile(np.arange(nb),n)
    order_ok=bool((ib[:,0]==ei).all() and (ib[:,1]==eb).all())
    py=P[eb,PREFIX_COLUMNS+ei]
    fbb=np.array([1./math.expm1(float(EN[b])/float(tr[i])) for i,b in zip(ei,eb)])
    tol=1e-7*np.maximum(np.abs(py),np.abs(cv))+1e-10*fbb
    ratio=np.abs(py-cv)/tol
    k=int(np.argmax(ratio))
    res[t]={"rows":len(cv),"order_ok":order_ok,"finite":bool(np.isfinite(cv).all() and np.isfinite(py).all() and np.isfinite(ratio).all()),
            "max_ratio":float(ratio.max()),"argmax_step_bin":[int(ei[k]),int(eb[k])],"n_gt1":int((ratio>1).sum()),
            "n_gt_0.1":int((ratio>0.1).sum()),"max_absrel_diff":float(np.max(np.abs(py-cv)/np.maximum(np.abs(cv),1e-300)))}
out["spectral"]=res
# prefix PV/PL
pres={}
for t,P,EN,nb in (("PV",V,E,311),("PL",L,np.array(LINE_EV),3)):
    ib,cv=arr(tags[t],t)
    ec=np.repeat(np.arange(PREFIX_COLUMNS),nb); eb=np.tile(np.arange(nb),PREFIX_COLUMNS)
    order_ok=bool((ib[:,0]==ec).all() and (ib[:,1]==eb).all())
    zc=np.array([c.redshift(RT_IZ+j) for j in range(PREFIX_COLUMNS)])
    trc=KB_EV_K*c.T0_K*(1.+zc)
    py=P[eb,ec]
    fbb=1./np.expm1(EN[eb]/trc[ec])
    ratio=np.abs(py-cv)/(1e-7*np.maximum(np.abs(py),np.abs(cv))+1e-10*fbb)
    pres[t]={"rows":len(cv),"order_ok":order_ok,"max_ratio":float(ratio.max()),"n_gt1":int((ratio>1).sum()),"bitexact_frac":float((py==cv).mean())}
out["prefix"]=pres
# STEP rows
mx={"xe":0.,"Tm_K":0.,"xHII":0.,"xHeII":0.,"z":0.,"xH1s":0.,"hrhs":0.,"trhs":0.}
iz_ok=True; flags_ok=True; inz=True
for i,r in enumerate(tags["STEP"]):
    x=r.split(",")
    if int(x[0])!=i or int(x[1])!=START_IZ+i+1: iz_ok=False
    s=states[i+1]; st=steps[i]
    if s["iz"]!=START_IZ+i+1 or st["input_iz"]!=START_IZ+i or st["photon_col"]!=PREFIX_COLUMNS+i or not st["coupled"] or int(x[9])!=1 or bool(int(x[10]))!=s["post_saha"]: flags_ok=False
    nat=dict(z=float(x[2]),xH1s=float(x[3]),xHII=float(x[4]),xHeII=float(x[5]),xe=float(x[6]),Tm_K=float(x[7]))
    mx["xe"]=max(mx["xe"],abs(s["xe"]-nat["xe"])/max(abs(nat["xe"]),1e-8))
    mx["Tm_K"]=max(mx["Tm_K"],abs(s["Tm_K"]-nat["Tm_K"])/max(abs(nat["Tm_K"]),1.))
    mx["xHII"]=max(mx["xHII"],abs(s["xHII"]-nat["xHII"])/max(abs(nat["xHII"]),1e-8))
    mx["xHeII"]=max(mx["xHeII"],abs(s["xHeII"]-nat["xHeII"]))
    mx["z"]=max(mx["z"],abs(s["z"]-nat["z"])); mx["xH1s"]=max(mx["xH1s"],abs(s["xH1s"]-nat["xH1s"])/max(abs(nat["xH1s"]),1e-8))
    mx["hrhs"]=max(mx["hrhs"],abs(st["hydrogen_rhs"]-float(x[8]))/max(1.,abs(float(x[8]))))
    mx["trhs"]=max(mx["trhs"],abs(st["thermal_rhs"]-float(x[11]))/max(1.,abs(float(x[11]))))
    if not all(map(math.isfinite,nat.values())): inz=False
out["step"]={"maxima":mx,"iz_ok":iz_ok,"flags_ok":flags_ok,"finite":inz,"last_state_iz":states[-1]["iz"],
    "schur_max":max(s["schur_residual"] for s in steps),"branches":sorted({s["branch"] for s in steps})}
b=other["BASE"][0].split(","); out["base_vs_state0"]={"iz":(int(b[0]),states[0]["iz"]),"xe_rel":abs(float(b[5])-states[0]["xe"])/states[0]["xe"],"Tm_rel":abs(float(b[6])-states[0]["Tm_K"])/states[0]["Tm_K"]}
# Task 3 pilot prefix
p=np.load(PI+"/python_u6_rt.npz",allow_pickle=False)
K=PREFIX_COLUMNS+128
pc={}
for k in ("virtual_out","average_virtual","lyman_out"):
    a=z[k]; q=p[k]
    pc[k]={"pilot_shape":q.shape,"bytes_equal":bool(np.ascontiguousarray(a[:,:K]).tobytes()==np.ascontiguousarray(q).tobytes()) if q.shape[1]==K else "SHAPE"}
pc["states_prefix_equal"]=bool(list(p["states_json"])==list(z["states_json"][:len(p["states_json"])])); pc["n_pilot_states"]=len(p["states_json"])
pc["steps_prefix_equal"]=bool(list(p["steps_json"])==list(z["steps_json"][:len(p["steps_json"])]))
out["pilot_prefix"]=pc
pb={}
for k,nb,key in (("virtual",311,"virtual_out"),("average",311,"average_virtual"),("lyman",3,"lyman_out")):
    d=np.fromfile(EV+f"/python_partial_{k}_f64le.bin",dtype="<f8")
    ok=d.size==n*nb
    pb[k]={"size_ok":ok,"equal_npz_cols":bool(ok and np.ascontiguousarray(z[key][:,PREFIX_COLUMNS:PREFIX_COLUMNS+n].T).astype("<f8").tobytes()==d.tobytes())}
out["partial_bins"]=pb
print(json.dumps(out,indent=1,default=str))
