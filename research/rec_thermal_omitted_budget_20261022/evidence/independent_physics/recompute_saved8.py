"""Independent algebraic evaluator on immutable NPZ, no new ODE.

Does not import any new omitted-budget implementation. Used only to review
the implemented calculation after its output exists.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from scipy.constants import sigma as SB
from scipy.integrate import simpson

UNIT=Path(__file__).resolve().parents[2]
ROOT=UNIT.parents[1]
INTAKE=Path(__file__).resolve().parent
DONOR=ROOT/"research/rec_rei_hheli_sandbox_20261021"
sys.path.insert(0,str(DONOR/"code"))
from atomic_network import AtomicNetwork
from coupled import thermal_uv

atomic=AtomicNetwork()
c=299792458.;kb=1.380649e-23;ev=1.602176634e-19
st=6.6524587051e-29;me=9.1093837139e-31;h=6.62607015e-34
aR=8*np.pi**5*kb**4/(15*h**3*c**3)
energies=atomic.photon_energy_eV*ev
uv_U0=float(atomic.photon_flux_bins_base@energies)/c
uv_M0=float(atomic.photon_flux_bins_base@(energies**2))/c
summaries=[]
saved={}
names=["CMB_hot","Planck_reference","UV_hot","UV_recoil","UV_net",
       "CI_kinetic","CI_binding","CE_kinetic","base_total_kinetic",
       "base_total_gas","old_primary","old_RR_loss","old_DR_loss"]
for path in sorted((ROOT/"research/rec_thermal_moments_20261022/results/thermal8").glob("*/trajectory.npz")):
    case=path.parent.name
    with np.load(path) as f:
        x=f["x"];T=f["T_K"];Y=f["Y"];raw=f["raw_state"]
        d={str(k):f["diagnostics"][:,i] for i,k in enumerate(f["diagnostic_names"])}
        H=d["H_s"];nb=d["nb_m3"];ne=nb*(Y@atomic.q)
        eta=Y@(1+atomic.q);a=np.exp(x)/21
        uv=np.array([thermal_uv(float(xx))[1] for xx in x])
        Ucmb=4*SB/c*2.7255**4*raw[:,4]/a**4
        coeffs={}
        for key,threshold,A,p,b,d1,f1 in [
            ("HI",157807.,21.11,-1.089,.354,.874,1.101),
            ("HeI",285335.,32.38,-1.146,.416,.987,1.056),
            ("HeII",631515.,19.95,-1.089,.553,.735,1.275),
        ]:
            ll=2*threshold/T
            coeffs["CI_"+key]=1e-6*A*T**(-1.5)*np.exp(-ll/2)*ll**p/(1+(ll/b)**d1)**f1
        coeffs["CE_HI"]=1e-13*7.5e-19*np.exp(-.75*157807/T)/(1+np.sqrt(T/1e5))
        coeffs["CE_HeII"]=1e-13*5.54e-17*T**(-.397)*np.exp(-.75*631515/T)/(1+np.sqrt(T/1e5))
        src=np.zeros_like(Y);particle=np.zeros_like(T);bind=np.zeros_like(T)
        for i,j,key in [(1,2,"HI"),(3,4,"HI"),(5,6,"HI"),
                        (7,8,"HeI"),(8,9,"HeII"),(10,11,"HeI"),(11,12,"HeII")]:
            r=ne*Y[:,i]*coeffs["CI_"+key]
            src[:,i]-=r;src[:,j]+=r
            particle+=r
            bind+=nb*r*(atomic.ionization_energy_J[j]-atomic.ionization_energy_J[i])
        ce=-ne*nb*((Y[:,1]+Y[:,3]+Y[:,5])*coeffs["CE_HI"]+
                  (Y[:,8]+Y[:,11])*coeffs["CE_HeII"])
        hot=-4*st*c*ne*kb*T*Ucmb/(me*c*c)
        trad=2.7255/a
        planck=4*st*c*ne*kb*aR*trad**4*(trad-T)/(me*c*c)
        uv_hot=-4*st*c*ne*kb*T*(uv*uv_U0)/(me*c*c)
        uv_recoil=st*c*ne*(uv*uv_M0)/(me*c*c)
        uv_net=uv_hot+uv_recoil
        kinetic=hot+uv_net-bind+ce
        gas=hot+uv_net+ce
        powers=np.column_stack([hot,planck,uv_hot,uv_recoil,uv_net,-bind,bind,ce,
                                kinetic,gas,d["photo_primary_W_m3"],
                                -d["rr_cooling_W_m3"],-d["dr_cooling_W_m3"]])
        eperx=powers/(nb*H)[:,None]/ev
        forcing=2*kinetic/(3*kb*T*nb*H*eta)-particle/(H*eta)
        force_particle=-particle/(H*eta)
        ci_force=-2*bind/(3*kb*T*nb*H*eta)+force_particle
        trap=np.trapezoid(eperx,x=x,axis=0)
        supported_ci=(T[:-1]>=1e4)&(T[1:]>=1e4)&(T[:-1]<=1e9)&(T[1:]<=1e9)
        supported_ce=(T[:-1]>=5e3)&(T[1:]>=5e3)&(T[:-1]<=5e5)&(T[1:]<=5e5)
        cell=np.diff(x)[:,None]*(eperx[:-1]+eperx[1:])/2
        records=dict(case_id=case,
                     input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     energy_eV_per_baryon_109_trapezoid=dict(zip(names,map(float,trap))),
                     energy_eV_per_baryon_109_Simpson=dict(zip(names,map(float,simpson(eperx,x=x,axis=0)))),
                     energy_eV_per_baryon_55_trapezoid=dict(zip(names,map(float,np.trapezoid(eperx[::2],x=x[::2],axis=0)))),
                     forcing_109_trapezoid=float(np.trapezoid(forcing,x=x)),
                     CI_particle_forcing_109_trapezoid=float(np.trapezoid(force_particle,x=x)),
                     CI_total_forcing_109_trapezoid=float(np.trapezoid(ci_force,x=x)),
                     CI_continuation_and_boundary_eV_per_baryon=float(cell[~supported_ci,5].sum()),
                     CE_continuation_and_boundary_eV_per_baryon=float(cell[~supported_ce,7].sum()),
                     CI_event_count_per_baryon=float(np.trapezoid(particle/H,x=x)),
                     work_eV_per_baryon=float(np.trapezoid(3*kb*T*eta/ev,x=x)),
                     ne_reconstruction_max_relative=float(np.max(np.abs(ne-d["ne_m3"])/np.maximum(ne,1e-300))),
                     eta_reconstruction_max_relative=float(np.max(np.abs(eta-d["gas_particles_per_baryon"])/eta)))
        summaries.append(records)
        saved[case+"__powers"]=powers;saved[case+"__forcing"]=forcing
        saved[case+"__dYdt"]=src;saved[case+"__particle_source"]=particle
        saved[case+"__x"]=x;saved[case+"__coefficients"]=np.column_stack(list(coeffs.values()))

out=dict(schema="rec.omitted.physics_independent_precompute.v1",
         method="Direct HG97 expressions and Compton moments; no new module imports; immutable109 states only.",
         arrays_columns=names,coefficient_columns=list(coeffs),no_ode=True,cases=summaries)
(INTAKE/"INDEPENDENT_FIXED_PATH.json").write_text(json.dumps(out,indent=2)+"\n")
np.savez_compressed(INTAKE/"independent_fixed_path.npz",**saved)
print(json.dumps(out,indent=2))
