"""One bounded independent LINE02 review: four off-grid probes, no IVP/runtime.

Run from this directory. The raw CSV matrix is assembled independently of the
production loader; production outputs are never imported, modified or replayed.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import os
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "code"))
import native_line_owner as nlo

def serial(obj):
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, (np.floating, np.integer, np.bool_)): return obj.item()
    if isinstance(obj, dict): return {k: serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [serial(v) for v in obj]
    return obj

def digest(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

def back(M, X, s):
    return float(np.max(np.abs(M @ X - s) / (np.abs(M) @ np.abs(X) + np.abs(s) + np.finfo(float).tiny)))

def scaled(a, b):
    return float(np.max(np.abs(a-b)) / max(np.max(np.abs(a)), np.max(np.abs(b)), 1e-300))

def component(a,b):
    return float(np.max(np.abs(a-b) / np.maximum(np.abs(b),1e-30)))

start=time.monotonic()
owner=nlo.NativeLineOwner()
M=np.zeros((313,313)); source=np.zeros(313)
for row in csv.reader((ROOT / "inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv").open()):
    kind=row[0]
    if kind=="TRR": M[int(row[1]),int(row[2])]=float(row[3])
    elif kind=="TRV": M[int(row[1]),2+int(row[2])]=float(row[3])
    elif kind=="TVR": M[2+int(row[2]),int(row[1])]=float(row[3])
    elif kind=="TVV":
        band,i=int(row[1]),int(row[2]); j=i+(0,-1,1)[band]
        if 0 <= j < 311: M[2+i,2+j]=float(row[3])
    elif kind=="REAL": source[int(row[1])]=float(row[3])
    elif kind=="VIRTUAL": source[2+int(row[1])]=float(row[9])

records=[]
for case,rf,bf in [("P1_signed_boundary_off_solution",.37,-.0001),("P2_absorption_mixed_jvp",1.73,1.0273)]:
    r,b=rf*owner.r0,bf*owner.b0
    a=M.copy(); a[1,1]=a[1,1]-owner.r0+r
    s=source.copy(); s[1]=s[1]-owner.r0*owner.b0+r*b
    direct=np.linalg.solve(a,s)
    solved=owner.solution(r,b)
    arbitrary=solved.state*(1+.07*np.sin(np.arange(313)*.19))
    direction=np.maximum(np.abs(arbitrary),1e-30)*np.cos(np.arange(313)*.23)
    dr,db=.083*owner.r0,-.091*owner.b0
    analytic=owner.residual_jvp(arbitrary,direction,r,b,dr=dr,db=db)
    step=1e-30
    ac=M.astype(complex); sc=source.astype(complex)
    rc,bc=r+1j*step*dr,b+1j*step*db
    ac[1,1]+=rc-owner.r0; sc[1]+=rc*bc-owner.r0*owner.b0
    ref_jvp=np.imag(ac@(arbitrary+1j*step*direction)-sc)/step
    ref_sol=np.imag(np.linalg.solve(ac,sc))/step
    analytical_sol=owner.solution_jvp(solved,dr=dr,db=db)
    J=r*(solved.state[1]-b)
    ledger=nlo.event_ledger(J,owner.nH_m3)
    result={"case":case,"r_ratio":rf,"b_ratio":bf,"eta":solved.eta,
        "real_component_error":component(solved.real,direct[:2]),
        "virtual_component_error":component(solved.virtual,direct[2:]),
        "backward":back(a,solved.state,s),
        "arbitrary_state_residual_error":scaled(owner.residual(arbitrary,r,b),a@arbitrary-s),
        "residual_jvp_error":scaled(analytic,ref_jvp),
        "solution_jvp_error":scaled(analytical_sol,ref_sol),
        "line_J":J,"ledger":ledger,"ledger_check":nlo.ledger_invariants(ledger),
        "blue_total":1/math.expm1(nlo.E21_EV/owner.snapshot.TR_eV_rescaled)+b/(3*owner.snapshot.x1s),
        "state":solved.state,"reference":direct,
        "arbitrary_state":arbitrary,"direction":direction,
        "residual_jvp":analytic,"residual_jvp_reference":ref_jvp,
        "solution_jvp":analytical_sol,"solution_jvp_reference":ref_sol}
    result["passed"]=(result["real_component_error"]<=5e-10 and result["virtual_component_error"]<=5e-10
        and result["backward"]<=5e-12 and result["residual_jvp_error"]<=5e-9
        and result["solution_jvp_error"]<=5e-9 and result["ledger_check"]["passed"] and result["blue_total"]>0)
    records.append(result)

# One rotated finite-opacity case. Independent full-sphere rule, no use of the
# donor's principal-frame rule or its laboratory oracle.
tau=1.7
axis=np.array([2.,-1.,3.]); axis/=np.linalg.norm(axis)
cross=np.array([[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]])
rotation=np.eye(3)+math.sin(.43)*cross+(1-math.cos(.43))*(cross@cross)
S=rotation@np.diag([-.67,.21,.46])@rotation.T
event=owner.angular_event(tau,S,synthetic=True)
mu,wm=np.polynomial.legendre.leggauss(48)
phi=np.arange(96)*2*math.pi/96
rho=np.sqrt(1-mu[:,None]**2)
directions=np.stack((rho*np.cos(phi),rho*np.sin(phi),np.broadcast_to(mu[:,None],(48,96))),axis=-1).reshape(-1,3)
weights=np.broadcast_to(wm[:,None]/192,(48,96)).ravel()
q=1+np.einsum("ni,ij,nj->n",directions,S,directions)
integrand=q*(-np.expm1(-tau/q))
C=float(weights@integrand)
D=(directions.T*(weights*integrand))@directions-np.eye(3)*C/3
bound=owner.state_bound(event["rbase_s_inv"],owner.b0,tau,S)
finite=owner.solution(event["rstar_s_inv"],owner.b0)
base=np.array(bound["baseline_state"])
diff_state=float(np.max(np.abs(finite.state-base)))
finite_flux=finite.r_s_inv*(finite.state[1]-owner.b0)
diff_flux=abs(finite_flux-bound["baseline_flux_per_H_s"])
finite_tensor=nlo.ENERGY_J*owner.nH_m3*event["rbase_s_inv"]*(finite.state[1]-owner.b0)*event["D"]
thick_tensor=nlo.ENERGY_J*owner.nH_m3*bound["baseline_flux_per_H_s"]*2*S/15
diff_tensor=float(np.linalg.norm(finite_tensor-thick_tensor))
state_slack=64*nlo.EPS*max(np.max(np.abs(finite.state)),np.max(np.abs(base)))
flux_slack=64*nlo.EPS*event["rbase_s_inv"]*(abs(finite.state[1])+abs(owner.b0))
tensor_slack=nlo.ENERGY_J*owner.nH_m3*flux_slack*max(np.linalg.norm(event["D"]),np.linalg.norm(2*S/15),1.)
obs={"state_inf":diff_state,"flux_per_H_s":diff_flux,"tensor_J_m3_s":diff_tensor}
slack={"state_inf":float(state_slack),"flux_per_H_s":float(flux_slack),"tensor_J_m3_s":float(tensor_slack)}
angular_check=abs(C-event["C"])<5e-10 and np.linalg.norm(D-event["D"])<5e-10
records.append({"case":"P3_rotated_finite_bound","tau":tau,"shear":S,"event":event,
    "independent_rule":{"nodes":4608,"C":C,"D":D},
    "C_abs_error":abs(C-event["C"]),"D_fro_error":float(np.linalg.norm(D-event["D"])),
    "bound":bound,"finite_state":finite.state,"differences":obs,"numerical_slack":slack,
    "passed":bool(angular_check and all(obs[k]<=bound["bounds"][k]["value"]+slack[k] for k in obs))})

# One new underflow-depth control; no finite-depth quadrature or full solve.
tau=1100.; S=np.diag([-.5,.2,.3])
under=owner.state_bound(nlo.A_EFFECTIVE_S_INV/tau,owner.b0,tau,S)
records.append({"case":"P4_underflow_log_retention","tau":tau,"shear":S,"bound":under,
    "passed":under["delta"]["representation"]=="UNDERFLOW_USE_LOG" and under["delta"]["value"] is None
        and all(v["representation"]=="UNDERFLOW_USE_LOG" and v["value"] is None and math.isfinite(v["log"]) for v in under["bounds"].values())})

reuse=json.loads((ROOT/"provenance/IMPLEMENTATION_REUSE.json").read_text())
identities=[]
for item in reuse["unchanged_sources"]:
    actual=digest(ROOT/item["file"])
    identities.append({**actual,"expected_sha256":item["sha256"],"matches":actual["sha256"]==item["sha256"]})
raw={"schema":"LINE02_FRESH_REVIEW_PROBES_V1","started_utc":datetime.now(timezone.utc).isoformat(),
    "independence":"fresh non-constructor agent; manual CSV full matrix and independent laboratory angular quadrature",
    "scope":"four off-grid probes, no primary-case replay, no IVP, no native runtime, no history campaign",
    "counts":{"offgrid_cases":4,"direct313_real_solves":2,"direct313_complex_solves":2,
        "independent_angular_nodes":4608,"native_runtime":0,"IVP":0,"historical_replay":0},
    "thread_variables":{k:os.environ.get(k) for k in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]},
    "manual_raw_matrix_byte_equal":M.tobytes()==owner.M.tobytes(),
    "manual_raw_source_byte_equal":source.tobytes()==owner.s.tobytes(),
    "virtual_block_not_symmetric":not np.array_equal(M[2:,2:],M[2:,2:].T),
    "identities":identities,"reviewed_code":[digest(ROOT/"code/native_line_owner.py"),digest(ROOT/"code/run_line02.py")],
    "records":records,"operator_counters":dict(nlo.COUNTERS),
    "elapsed_s":time.monotonic()-start}
raw["passed"]=bool(raw["manual_raw_matrix_byte_equal"] and raw["manual_raw_source_byte_equal"] and all(r["passed"] for r in records) and all(i["matches"] for i in identities))
out=HERE/"PROBE_RAW.json"
if out.exists(): raise RuntimeError("immutable review probe output exists")
out.write_text(json.dumps(serial(raw),indent=2,allow_nan=False)+"\n")
print(json.dumps({"passed":raw["passed"],"cases":[{k:v for k,v in r.items() if k in {"case","passed","real_component_error","virtual_component_error","backward","residual_jvp_error","solution_jvp_error","C_abs_error","D_fro_error","differences","numerical_slack"}} for r in records],"elapsed_s":raw["elapsed_s"]},indent=2))
