#!/usr/bin/env python3
"""Source-owned z=20 local (non-IVP) Thomson/REI directional pilot.

Runs against the original Git-tracked REC boundary JSON. No native REI state
injection, time evolution, integrated tau, or physically adopted donor.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

SOURCE_BLOB = '89cdfc766e2e613760d84274812f2b4432373354'
NATIVE_STDOUT_SHA = '6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400'
RECIPIENT_SHA = '07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696'
C, SIGMA_T = 299792458., 6.6524587321e-29
QS = (-.01,-.005,0.,.005,.01)


def load(path):
    raw = Path(path).read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob != SOURCE_BLOB:
        raise ValueError('refuse non-original or changed source Git blob')
    d = json.loads(raw)
    if (d.get('schema') != 'rec.rei.primordial_reference_boundary.v1' or
        d.get('source_sha256') != NATIVE_STDOUT_SHA or
        d.get('rei_scenario_sha256') != RECIPIENT_SHA or
        d.get('decision') != 'REI_REFERENCE_COUNTERFACTUAL_NOT_ADOPTED' or
        d.get('zbar') != 20.0 or
        d.get('reference_clock') != 'mean FLRW redshift zbar=a^-1-1; NOT observed-direction redshift'):
        raise ValueError('source/domain/clock/decision drift')
    return d


def direction(q, mu):
    d = math.hypot(1.,q)+q*(3*mu*mu-1)
    if not (0 <= mu <= 1 and d > 0):
        raise ValueError('nonmonotone redshift or invalid angle')
    return 1/d


def moments(q):
    if q == 0.: return 1.,0.
    A, B = math.hypot(1.,q)-q,3*q
    if B > 0:
        I0=math.atan(math.sqrt(B/A))/math.sqrt(A*B)
    else:
        I0=math.atanh(math.sqrt(-B/A))/math.sqrt(-A*B)
    I2=(1-A*I0)/B
    return I0, 2.5*(3*I2-I0)


def writecsv(path, data):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)


def generate(root, output):
    root=Path(root)
    d=load(root/'research/rec_r3c_rei_bridge_20261015/REI_CONDITIONAL_BOUNDARY.json')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    Hf=d['normalization_mismatch']['H_s_inv']
    nh=d['normalization_mismatch']['nH_REI_m3']
    branches=(('REI_APPROXIMATE_LOCKED',d['published_rei_approximate_initial']),
              ('HYREC_Q0_DONOR_NOT_ADOPTED',d['hyrec_full_conditional_projection']))
    rows=[];summaries=[]
    for name,b in branches:
        ne=b['electron_density_m3']; gam=C*SIGMA_T*ne
        if abs(ne/nh-b['electron_fraction_per_H']) > 1e-14:
            raise ValueError('REI hydrogen-normalization/charge mismatch')
        if not math.isclose(gam,b['thomson_scattering_rate_s_inv'],rel_tol=2e-13):
            raise ValueError('Thomson source rate mismatch')
        if not math.isclose(gam/Hf,b['thomson_optical_depth_rate_per_ln_a'],rel_tol=2e-13):
            raise ValueError('source mean-a derivative mismatch')
        for q in QS:
            H=Hf*math.hypot(1,q)
            M,Q=moments(q)
            for j in range(21):
                mu=j/20
                Hdir=Hf/direction(q,mu)
                rows.append(dict(branch=name,zbar=20,q_ref=q,mu=mu,
                    x_e_per_H=b['electron_fraction_per_H'],Tgas_K=b['temperature_K'],
                    n_e_m_inv3=ne,gamma_s_inv=gam,H_flrw_s_inv=Hf,
                    H_bianchi_s_inv=H,H_direction_s_inv=Hdir,
                    dtaudln_a_mean=gam/H,dtaudln_1plusz_direction=gam/Hdir,
                    u_th_J_m_inv3=b['thermal_energy_J_m3']))
            summaries.append(dict(branch=name,zbar=20,q_ref=q,
                monopole_factor=M,P2_factor=Q,
                monopole_dtaudln_1plusz_direction=gam/Hf*M,
                P2_dtaudln_1plusz_direction=gam/Hf*Q,
                dtaudln_a_mean=gam/H))
    writecsv(output/'directional_z20_210rows.csv',rows)
    writecsv(output/'angular_moments_z20_10rows.csv',summaries)
    status=dict(schema='rec.rei.thomson.local_pilot.v1',source_blob=SOURCE_BLOB,
      recipient_sha256=RECIPIENT_SHA,native_stdout_sha256=NATIVE_STDOUT_SHA,
      exact_source_git_blob_loaded=True,source_recipient_semantic_parity=True,
      consumer_symbol='rei_bianchi/src/rei_bianchi/monolithic_model_b2a.py::electron_density',
      consumer_git_blob='3d806e1c1d3bb523bb3c339d1a141f67d7f10069',
      accepted_native_REI_input=False,receiver_execution='NOT_RUN',
      new_IVP=False,integrated_tau=False,tilt=False,production='HOLD',
      directional_rows=len(rows),angular_moment_rows=len(summaries),
      canonical_REI='28/88',physical_REC_H5='0/313')
    (output/'SCIENCE_STATUS.json').write_text(json.dumps(status,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return status


if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--repo-root',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    v=a.parse_args()
    print(json.dumps(generate(v.repo_root,v.out),indent=2))
