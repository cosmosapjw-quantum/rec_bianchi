#!/usr/bin/env python3
"""Read-only fixed-observed-redshift tau first variation on exact REI #319 epochs.
No native REI IVP, no physically admitted anisotropic H/He history.
Full finite-geodesic independent control and tests live in source-inclusive archive.
"""
import argparse, csv, hashlib, json, math
from pathlib import Path
from scipy.integrate import quad

EXPECTED="aaf60834dcc095025ad6261515fa5535d5b30894"
C=299792458.; SIGMA_T=6.6524587321e-29
H0=67.4e3/3.0856775814913673e22
OM,OR=.315,9.27e-5
FHE=.245/(4*(1-.245))
QS=(-.01,-.005,0.,.005,.01)

def Hf(z):
    return H0*math.sqrt(OM*(1+z)**3+OR*(1+z)**4+(1-OM-OR))

def K(z,zlo):
    return Hf(20)/21**3*quad(lambda zz:(1+zz)**2/Hf(zz),zlo,z,epsrel=1e-12)[0]

def run(source,output):
    b=Path(source).read_bytes()
    sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()
    if sha!=EXPECTED:raise ValueError("Git source SHA mismatch")
    rows=list(csv.DictReader(b.decode('utf8').splitlines()))
    if len(rows)!=11:raise ValueError("source epoch count mismatch")
    src=[{k:float(v) for k,v in row.items()} for row in rows]
    zlo=src[-1]["actual_output_z"];out=Path(output);out.mkdir(parents=True,exist_ok=True)
    derived=[];moments=[]
    for row in src:
        z=row["actual_output_z"]
        ne=row["ne_cm3"]*1e6
        nH=row["nH_cm3"]*1e6
        xe=row["x_HII"]+FHE*(row["x_HeII"]+2*row["x_HeIII"])
        if not math.isclose(ne,nH*xe,rel_tol=5e-11):
            raise ValueError("source electron inventory mismatch")
        tau=row["tau_from_zlo"]
        A=C*SIGMA_T*ne/Hf(z)*K(z,zlo)
        for q in QS:
            moments.append(dict(source_z=z,q_ref=q,original_tau=tau,
                K=K(z,zlo),a2_first_order=-2*q*A))
            for j in range(21):
                mu=j/20
                derived.append(dict(source_z=z,mu_observer=mu,q_ref=q,
                    original_tau=tau,tau_first_order=tau+q*A*(1-3*mu*mu)))
    def write(name,rows):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write("REI319_FIXEDZ_DIRECTIONAL_1155.csv",derived)
    write("REI319_FIXEDZ_P2_55.csv",moments)
    report={"status":"SOURCE_CONDITIONAL_FIRST_VARIATION_ONLY",
            "source_git_blob":EXPECTED,"source_rows":11,"derived_rows":len(derived),
            "moment_rows":len(moments),"REI_canonical":"28/88",
            "REC_H5_physical":"0/313","F05_F08_newly_admitted":0,
            "native_REI_receiver":"NOT_RUN","production":"HOLD"}
    (out/"SCOPED_VERDICT.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out",required=True)
    v=a.parse_args()
    print(json.dumps(run(v.source,v.out),indent=2))
