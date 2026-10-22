#!/usr/bin/env python3
"""Bounded, zero-IVP Compton budgets from eight immutable REC histories."""
from pathlib import Path
import argparse
import ctypes
import csv
import hashlib
import json
import platform
import subprocess
import time
import numpy as np
from scipy.integrate import simpson

KB, C, HP = 1.380649e-23, 299792458., 6.62607015e-34
ME, ST, EV = 9.1093837139e-31, 6.6524587051e-29, 1.602176634e-19
AR = 8*np.pi**5*KB**4/(15*HP**3*C**3)
ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, default=None,
                        help='Optional flat staging directory; otherwise use the pinned repo inputs')
    parser.add_argument('--output', type=Path, default=ROOT/'results')
    args=parser.parse_args()
    start=time.monotonic(); cpu=time.process_time()
    args.output.mkdir(parents=True,exist_ok=True)
    libpath=args.output/'libcompton_budget.so'
    cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',
         str(ROOT/'code/compton_budget.c'),'-lm','-o',str(libpath)]
    compilation=subprocess.run(cmd,capture_output=True,text=True,check=True)
    dll=ctypes.CDLL(str(libpath))
    vector=np.ctypeslib.ndpointer(dtype=np.float64,ndim=1,flags='C_CONTIGUOUS')
    dll.compton_terms.argtypes=[ctypes.c_size_t]+[vector]*7
    dll.compton_terms.restype=ctypes.c_int
    dll.compton_frozen_step.argtypes=[ctypes.c_double]*4
    dll.compton_frozen_step.restype=ctypes.c_double

    def evaluate(t,tg,ne,nb,eta):
        aa=[np.ascontiguousarray(v,dtype=np.float64) for v in (t,tg,ne,nb,eta)]
        q,g=np.empty(len(aa[0])),np.empty(len(aa[0]))
        status=dll.compton_terms(len(q),*aa,q,g)
        if status: raise ValueError(f'C input/kernel failure: {status}')
        return q,g

    # Discriminating independent checks, not a historical campaign replay.
    q,g=evaluate([20.,30.,40.,100.],[30.]*4,[1.,1.,1.,0.],[2.]*4,[1.5]*4)
    assert q[0]>0 and q[1]==0 and q[2]<0 and q[3]==0 and g[3]==0
    t0,tg,gg,d1,d2=10000.,20.,2e-16,2e15,3e15
    split=dll.compton_frozen_step(dll.compton_frozen_step(t0,tg,gg,d1),tg,gg,d2)
    one=dll.compton_frozen_step(t0,tg,gg,d1+d2)
    semigroup=abs(split-one)/one
    assert semigroup < 3e-14 and tg < one < t0
    assert np.isnan(dll.compton_frozen_step(t0,tg,-1.,1.))
    try: evaluate([1.],[1.],[-1.],[1.],[1.])
    except ValueError: pass
    else: raise AssertionError('negative ne accepted')

    rows=[]; histories=[]; inputlocks=[]; c_error=0.; capacity_error=0.
    frozen=json.loads((ROOT/'SOURCE_INPUTS.json').read_text())['files']
    for item in frozen:
        staged=args.inputs or (ROOT/'inputs')
        p=staged/item['file']
        receipt_path=p.with_suffix('.RESULT.json')
        if not p.exists() and args.inputs is None:
            candidates=[parent/item['source_path'] for parent in ROOT.parents]
            p=next((v for v in candidates if v.is_file()),p)
            receipt_path=p.with_name('RESULT.json')
        case=item['file'].removesuffix('.npz')
        receipt=json.loads(receipt_path.read_text())
        raw=p.read_bytes()
        assert digest(raw)==item['sha256'] and len(raw)==item['bytes']
        assert receipt['status']=='COMPLETE'
        assert digest(raw)==receipt['trajectory_sha256']
        assert len(raw)==receipt['trajectory_bytes']
        data=np.load(p,allow_pickle=False)
        x,z,T=data['x'],data['z'],data['T_K']
        assert len(x)==109 and np.all(np.diff(x)>0)
        dd=dict(zip(data['diagnostic_names'],data['diagnostics'].T))
        H,nb,ne,eta=[dd[k] for k in ('H_s','nb_m3','ne_m3','gas_particles_per_baryon')]
        assert np.all(H>0) and np.all(np.isfinite(H))
        Tg=2.7255*(1+z)
        q,gamma=evaluate(T,Tg,ne,nb,eta)
        # Independent form: temperature-relaxation coefficient then heat capacity.
        reference_g=(8*ST/(3*ME*C))*(AR*Tg**4)*(ne/nb)/eta
        reference_q=(1.5*KB*nb*eta)*reference_g*(Tg-T)
        c_error=max(c_error,float(np.max(np.abs(q/reference_q-1))))
        capacity_error=max(capacity_error,float(np.max(np.abs(gamma/reference_g-1))))
        assert np.all(q<0) # factual property of these eight current histories
        ef=q/(nb*H)/EV
        damp=gamma/H
        heat=dd['photo_primary_W_m3']
        adiabatic=3*H*nb*eta*KB*T
        v=dict(case=case,samples=len(x),z_start=float(z[0]),z_end=float(z[-1]),
               rr_closure=receipt['rr_closure'],refined=receipt['refined'],
               compton_energy_eV_per_baryon=float(simpson(ef,x=x)),
               compton_trapezoid_eV_per_baryon=float(np.trapezoid(ef,x)),
               compton_coarse_simpson_eV_per_baryon=float(simpson(ef[::2],x=x[::2])),
               damping_depth=float(simpson(damp,x=x)),
               max_Gamma_over_H=float(max(damp)),
               max_abs_Qc_over_photo=float(max(abs(q)/heat)),
               max_abs_Qc_over_adiabatic=float(max(abs(q)/adiabatic)),
               min_T_K=float(min(T)),max_T_K=float(max(T)),
               max_Tgamma_K=float(max(Tg)))
        v['saved_grid_sensitivity_eV']=abs(v['compton_energy_eV_per_baryon']-v['compton_coarse_simpson_eV_per_baryon'])
        rows.append(v)
        histories.extend(dict(case=case,x=float(a),z=float(b),T_K=float(c),Tgamma_K=float(d),
                              Qc_W_m3=float(e),Gamma_per_s=float(f),energy_eV_per_baryon_per_x=float(j),
                              Gamma_over_H=float(k)) for a,b,c,d,e,f,j,k in zip(x,z,T,Tg,q,gamma,ef,damp))
        inputlocks.append(dict(file=item['file'],bytes=len(raw),sha256=digest(raw),
                               git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                               source_commit='892aad5c3e9fb0b2abd021154b62a42c39277125',
                               source_path=item['source_path']))
    assert len(rows)==8 and len(histories)==872
    assert c_error<3e-14 and capacity_error<3e-14
    for name,rr in [('budgets.csv',rows),('history.csv',histories)]:
        with (args.output/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rr[0]));writer.writeheader();writer.writerows(rr)
    result=dict(status='PASS_SCOPED_SAVED_HISTORY_REFERENCE_FIELD',new_ODEs=0,cases=rows,
                source_field='Reference blackbody: Tgamma=2.7255*(1+z) K; donor anisotropic spectral energy not reconstructed',
                interpretation='Fixed-history omitted energy/damping budget; no prediction of coupled temperature change',
                checks=dict(input_count=8,source_npz_sha256='PASS',semigroup_relative=semigroup,
                            C_vs_independent_Python_relative=c_error,heatcapacity_relative=capacity_error,
                            signs_equilibrium_zero_density='PASS',invalid_input_rejection='PASS'),
                constants_SI=dict(kB=KB,c=C,h=HP,me=ME,sigmaT=ST,aR=AR,eV_J=EV),
                compile_command=cmd,compiler_stdout=compilation.stdout,compiler_stderr=compilation.stderr,
                environment=dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform()),
                wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time()-cpu,
                holds=dict(physical='HOLD',production='NOT_APPROVED',global_convergence='NOT_RUN',REI_activation=False),
                input_lock=inputlocks)
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','new_ODEs','checks','wall_seconds','process_cpu_seconds')}))
    print(json.dumps(rows,indent=2))

if __name__=='__main__': main()
