"""Bounded independent finite checks for REC-HISTORY-01.

Written separately from history_boundary.py. Numerical execution is explicit;
this file never imports or runs LINE02's preparation, runner or campaign.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time
import traceback

import mpmath as mp
import numpy as np
from scipy.linalg import solve
import history_boundary as hb
from native_oracle_build import build_oracle

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent / "rec_line_native_owner_20261023"
EPS = np.finfo(float).eps
E21 = 10.198714553953742
E31 = 12.087365397278509
E41 = 12.748393192442178
LYA_FACT = 4.662899067555897e15
EV_J = 1.602176634e-19
CONTRACT_SHA = "dc0e109608edddf458489066be4a1bae83bd2d89134535f2a0303c4c5efbcf35"
CSV_SHA = "3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7"
COUNTS = Counter()


def clean(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.integer, np.floating, np.bool_)):
        return x.item()
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    return x


def write_json(path, data):
    Path(path).write_text(json.dumps(clean(data), indent=2, allow_nan=False) + "\n")


class Evidence:
    def __init__(self, output):
        self.output = output
        self.checks = []
        self.rows = []
        self.arrays = {}
        self.handle = (output / "checks.jsonl").open("x")
        self.raw_handle = (output / "raw_cases.jsonl").open("x")

    def check(self, name, condition, **facts):
        row = {"id": name, "result": "pass_scoped" if bool(condition) else "fail", **clean(facts)}
        self.checks.append(row)
        self.handle.write(json.dumps(row, allow_nan=False) + "\n")
        self.handle.flush()

    def row(self, **facts):
        row = clean(facts)
        self.rows.append(row)
        self.raw_handle.write(json.dumps(row, allow_nan=False) + "\n")
        self.raw_handle.flush()

    def parity(self, name, actual, expected, scale, tolerance, **facts):
        a, b, gross = np.asarray(actual), np.asarray(expected), np.asarray(scale)
        error = np.abs(a - b)
        denom = np.maximum(np.abs(gross), 1e-300)
        ratio = error / denom
        maximum = float(np.max(ratio))
        self.check(name, np.all(np.isfinite(a)) and np.all(error <= tolerance * denom),
                   maximum_scaled_error=maximum, tolerance=tolerance,
                   max_absolute_error=float(np.max(error)), **facts)
        return maximum


def read_snapshot(path):
    """Independent direct CSV field assembly; no production parser imported."""
    meta, virtual = {}, np.zeros((311, 13))
    trr, trv, tvr, tvv = np.zeros((2,2)), np.zeros((2,311)), np.zeros((2,311)), np.zeros((3,311))
    real = np.zeros((2,5))
    seen = set()
    for row in csv.reader(path.read_text().splitlines()):
        if not row:
            continue
        if row[0] == "META":
            meta[row[1]] = float(row[2])
        elif row[0] == "REAL":
            real[int(row[1])] = list(map(float,row[2:]))
        elif row[0] == "VIRTUAL":
            j = int(row[1])
            if j in seen:
                raise ValueError("duplicate snapshot virtual row")
            seen.add(j)
            virtual[j] = list(map(float,row[2:]))
        elif row[0] in {"TRR","TRV","TVR","TVV"}:
            target = {"TRR":trr,"TRV":trv,"TVR":tvr,"TVV":tvv}[row[0]]
            target[int(row[1]),int(row[2])] = float(row[3])
    if len(seen) != 311:
        raise ValueError("incomplete immutable virtual snapshot")
    matrix = np.zeros((313,313))
    matrix[:2,:2] = trr
    matrix[:2,2:] = trv
    matrix[2:,:2] = tvr.T
    for j in range(311):
        matrix[2+j,2+j] = tvv[0,j]
        if j > 0:
            matrix[2+j,1+j] = tvv[1,j]
        if j < 310:
            matrix[2+j,3+j] = tvv[2,j]
    return {"meta":meta,"virtual":virtual,"M":matrix,"source":np.r_[real[:,1],virtual[:,7]],
            "tvr":tvr,"tvv":tvv,"energies":virtual[:,0],"dtau":virtual[:,5],
            "u0":np.r_[virtual[:,1],meta["Dfplus_Lya"],meta["Dfplus_Lyb"]]}


def local_controls(ev, frozen):
    native_tau = ((6.2649e8+2*6.2648e8)/3) / frozen.r0
    base = 2.0**-40
    for tau in (0.,1e-10,.3,2.,30.,native_tau):
        for q in (.6,1.,1.4):
            for drive, source in (("emission",2*base),("absorption",-.5*base),("equilibrium",base)):
                COUNTS["local_ray_controls"] += 1
                din, x1s, xr = base, .5, 1.5*source
                got = hb.boundary(din,xr,x1s,tau,q,reference_occupation=4*base)
                mm = list(map(mp.mpf,(din,xr,x1s,tau,q)))
                dm,xm,gm,tm,qm = mm
                sm = xm/(3*gm)
                am = -mp.expm1(-tm/qm)
                delta_ref = (sm-dm)*am
                outgoing_ref = dm+delta_ref
                gross = float(abs(dm)+abs(sm)+abs(delta_ref))
                scaled = ev.parity(f"ray{COUNTS['local_ray_controls']}:outgoing",got["outgoing"],
                                   float(outgoing_ref),gross,128*EPS)
                ev.parity(f"ray{COUNTS['local_ray_controls']}:stable_jump",got["delta"],
                          float(delta_ref),float(abs(sm-dm)*am),128*EPS)
                ev.parity(f"ray{COUNTS['local_ray_controls']}:transmission",got["transmission"],
                          float(mp.exp(-tm/qm)),1.,128*EPS)
                ev.check(f"ray{COUNTS['local_ray_controls']}:log_transmission",
                         math.isfinite(got["log_transmission"]) and got["log_transmission"] == -tau/q)
                # Supply the same absolute-occupation reference to the ledger.
                led = hb.line_ledger(din,xr,x1s,tau,frozen.nH,frozen.H,q,
                                     reference_occupation=4*base)
                rate_ref = mp.mpf(3e6)*mp.mpf(LYA_FACT)*mp.mpf(frozen.H)*qm*delta_ref
                scale_rate = float(abs(mp.mpf(3e6)*mp.mpf(LYA_FACT)*mp.mpf(frozen.H)*qm)*
                                   (abs(sm)+abs(dm))*am)
                ev.parity(f"ray{COUNTS['local_ray_controls']}:phase_flux",led["R"],float(rate_ref),
                          scale_rate,128*EPS)
                ev.parity(f"ray{COUNTS['local_ray_controls']}:energy",led["radiation_J_m3_s"],
                          E21*EV_J*led["R"],2*abs(E21*EV_J*led["R"]),128*EPS)
                ev.parity(f"ray{COUNTS['local_ray_controls']}:energy_closure",
                          led["radiation_J_m3_s"]+led["atomic_internal_J_m3_s"],0.,
                          abs(led["radiation_J_m3_s"])+abs(led["atomic_internal_J_m3_s"]),128*EPS)
                if tau == 0 or drive == "equilibrium":
                    ev.check(f"ray{COUNTS['local_ray_controls']}:exact_zero",got["delta"] == 0. and led["R"] == 0.)
                ev.row(group="local",tau=tau,q=q,drive=drive,din=din,source=source,
                       outgoing=got["outgoing"],delta=got["delta"],transmission=got["transmission"],
                       absorbed_fraction=got["absorbed_fraction"],log_transmission=got["log_transmission"],
                       oracle_outgoing=str(outgoing_ref),oracle_delta=str(delta_ref),
                       R=led["R"],scaled_outgoing_error=scaled)


def scalar_controls(ev, oracle):
    eta0,h,iz = -8.,.125,6
    values = np.array([2e-9,-3e-9,1e-9,4e-9,-2e-9,5e-9,1e30])
    queries = [(0,-8.),(1,-7.8),(2,-8.5),(6,-8.01),(6,-8.),(6,-7.875),
               (6,-7.75),(6,-7.625),(6,-7.5),(6,np.nextafter(-7.375,-np.inf)),
               (6,-7.99),(6,-7.94),(6,-7.88),(6,-7.86),(6,-7.81),
               (6,-7.73),(6,-7.67),(6,-7.59),(6,-7.48),(6,-7.41)]
    for i,(count,query) in enumerate(queries):
        COUNTS["scalar_interpolation_controls"] += 1
        got = hb.interpolation(eta0,h,values,count,query)
        expected = oracle.interpolate(eta0,h,values,count,query)
        if count < 2 or query < eta0:
            scale = 0.
        else:
            coord = (query-eta0)/h
            k = math.floor(coord)
            alpha = coord-k
            scale = abs((1-alpha)*values[k])+abs(alpha*values[k+1])
        ratio = ev.parity(f"interp{i}:source_C",got["value"],expected,scale,64*EPS)
        if not got["thermal"]:
            ev.check(f"interp{i}:known_prefix",0<=got["k"] and got["k"]+1<count)
        ev.row(group="interpolation",eta0=eta0,h=h,iz=count,query=query,
               C_value=expected,python_value=got["value"],scaled_error=ratio,stencil=got)


def mapping_control(ev, oracle, frozen):
    COUNTS["native_mapping_comparisons"] += 1
    iz = 4096
    eta0,h = -8.,oracle.h
    eta_face = eta0+h*(iz-1.25)
    times = h*np.arange(iz+1)
    amplitudes = 1e-13*(1+np.arange(314)/314.)
    amplitudes[::3] *= -.25
    history = amplitudes[:,None]*(1+.03*times[None,:]+.2*times[None,:]**2)
    history[:,-1] = 1e30  # unknown current column; must never enter interpolation.
    zstart,z = math.expm1(-eta0),math.expm1(-eta_face)
    actual_eta0,actual_eta_face = -math.log(1.+zstart),-math.log(1.+z)
    got = hb.incoming_history(actual_eta0,h,history,iz,actual_eta_face,frozen.energies,z_face=z)
    expected = oracle.mapping(history,iz,zstart,z,frozen.energies)
    src,target,energy = hb.native_links(frozen.energies)
    # Independent owner table from the three literal native loops.
    indices = np.r_[np.arange(1,312),140,271].astype(int)
    indices[139],indices[270],indices[310] = 311,312,313
    targets = np.r_[frozen.energies,E21,E31]
    all_e = np.r_[frozen.energies,E21,E31,E41]
    ev.check("native313:owner_indices",np.array_equal(src,indices))
    ev.check("native313:target_energies",np.array_equal(target,targets))
    ev.check("native313:source_energies",np.array_equal(energy,all_e[indices]))
    gross = np.zeros(313)
    query_difference = np.zeros(313)
    for j,stencil in enumerate(got["stencils"]):
        if not stencil["thermal"]:
            k,a = stencil["k"],stencil["alpha"]
            gross[j] = abs((1-a)*history[indices[j],k])+abs(a*history[indices[j],k+1])
        native_query = -math.log((1+z)*all_e[indices[j]]/targets[j])
        algebraic_query = actual_eta_face-math.log(all_e[indices[j]]/targets[j])
        query_difference[j] = algebraic_query-native_query
    ev.parity("native313:all_C_values",got["incoming"],expected,gross,64*EPS,
              manufactured_history=True,max_equivalent_query_difference=float(np.max(abs(query_difference))))
    ev.check("native313:all_prefixes",all(s["thermal"] or s["k"]+1<iz for s in got["stencils"]))
    ev.arrays.update(mapping_history=history,mapping_C=expected,mapping_python=got["incoming"],
                     mapping_gross=gross,mapping_query_difference=query_difference,
                     mapping_owner_indices=indices,mapping_target_energies=targets,
                     mapping_source_energies=all_e[indices])
    ev.row(group="mapping",channels=313,iz=iz,eta0=actual_eta0,eta_face=actual_eta_face,h=h,
           max_query_difference=float(np.max(abs(query_difference))),manufactured=True)
    return got,history,indices,actual_eta0,actual_eta_face,h,iz


def derivatives(ev, mapping):
    base = np.array([2e-12,9e-12,.75,.3,1.4])
    scales = np.array([1e-12,2e-12,.03,.07,.08])
    directions = [np.eye(5)[j]*scales for j in range(5)] + [scales*np.array([1,-1,1,-1,1])]
    for j,direction in enumerate(directions):
        COUNTS["derivative_directions"] += 1
        def mapped(t):
            din,xr,x1s,tau,q = [mp.mpf(float(base[k]))+t*mp.mpf(float(direction[k])) for k in range(5)]
            return din+(xr/(3*x1s)-din)*(-mp.expm1(-tau/q))
        ref = mp.diff(mapped,mp.mpf(0))
        got = hb.boundary_jvp(*base,*direction)
        # Derivative scale from independently differentiated individual factors,
        # retaining physical units rather than summing unlike input components.
        din,xr,x1s,tau,q = map(mp.mpf,base)
        dd,dx,dg,dt,dq = map(mp.mpf,direction)
        trans,absorb = mp.exp(-tau/q),-mp.expm1(-tau/q)
        source = xr/(3*x1s)
        gross = float(abs(trans*dd)+abs(absorb*dx/(3*x1s))+abs(absorb*source*dg/x1s)+
                      abs((source-din)*trans*dt/q)+abs((source-din)*trans*tau*dq/q**2))
        ev.parity(f"boundary_jvp{j}:mp80",got,float(ref),gross,5e-9)
        ev.row(group="derivative",kind="local_boundary",direction=j,value=got,oracle=str(ref),gross=gross)
    values = np.array([2e-9,-3e-9,1e-9,4e-9,-2e-9,5e-9])
    result = hb.interpolation(-8.,.125,values,6,-7.81)
    for j in range(3):
        COUNTS["derivative_directions"] += 1
        tangent = 1e-10*np.cos((np.arange(6)+1)*(j+1))
        deta = (.004,-.003,.002)[j]
        q = (mp.mpf(-7.81)-mp.mpf(-8.))/mp.mpf(.125)
        k = int(mp.floor(q)); alpha=q-k
        ref = (1-alpha)*mp.mpf(tangent[k])+alpha*mp.mpf(tangent[k+1]) + \
              (mp.mpf(values[k+1])-mp.mpf(values[k]))*mp.mpf(deta)/mp.mpf(.125)
        gross = float(abs((1-alpha)*mp.mpf(tangent[k]))+abs(alpha*mp.mpf(tangent[k+1]))+
                      abs((mp.mpf(values[k+1])-mp.mpf(values[k]))*mp.mpf(deta)/mp.mpf(.125)))
        got = hb.interpolation_jvp(result,tangent,deta)
        ev.parity(f"interpolation_jvp{j}:mp80",got,float(ref),gross,5e-9)
        ev.row(group="derivative",kind="scalar_history",direction=j,value=got,oracle=str(ref),gross=gross)
    result,history,indices,eta0,eta_face,h,iz = mapping
    for j in range(3):
        COUNTS["derivative_directions"] += 1
        tangent = np.zeros_like(history)
        row_scale = (1e-15*np.cos((np.arange(314)+.7)*(j+1)))[:,None]
        tangent[:,:iz] = row_scale*(1+.02*np.arange(iz)[None,:]*h)
        tangent[:,iz] = -1e30
        deta = (1e-4,-2e-4,3e-4)[j]
        got = hb.incoming_history_jvp(result,tangent,deta)
        expected,gross = np.zeros(313),np.zeros(313)
        # Independent exact fixed-cell differential; no production JVP helper.
        for m,st in enumerate(result["stencils"]):
            if st["thermal"]:
                continue
            k,a = st["k"],mp.mpf(st["alpha"])
            y0,y1 = map(mp.mpf,history[indices[m],k:k+2])
            d0,d1 = map(mp.mpf,tangent[indices[m],k:k+2])
            terms = [(1-a)*d0,a*d1,(y1-y0)*mp.mpf(deta)/mp.mpf(h)]
            expected[m] = float(sum(terms)); gross[m] = float(sum(abs(x) for x in terms))
        ev.parity(f"incoming_history_jvp{j}:mp80",got,expected,gross,5e-9)
        ev.arrays[f"history_jvp{j}"] = np.vstack((got,expected,gross))


def dense_solve(matrix, rhs):
    columns = 1 if np.ndim(rhs) == 1 else np.shape(rhs)[1]
    if COUNTS["dense_rhs_solves"]+columns > 8:
        raise RuntimeError("frozen dense RHS allocation exhausted")
    COUNTS["dense_rhs_solves"] += columns
    return solve(matrix,rhs,assume_a="gen",check_finite=True)


def frozen_directions(ev, oracle, frozen, snap, saved):
    matrix, source = snap["M"],snap["source"]
    ev.parity("frozen:Mstar_native",frozen.Mstar(),matrix,np.abs(matrix),64*EPS)
    ev.parity("frozen:saved_matrix",saved["M"],matrix,np.abs(matrix),64*EPS)
    ev.parity("frozen:u0",frozen.u0,snap["u0"],np.abs(snap["u0"]),64*EPS)
    ev.parity("frozen:saved_X0",frozen.X0,saved["X0"],np.abs(saved["X0"]),64*EPS)
    x1s = snap["meta"]["x1s"]
    r0 = LYA_FACT*snap["meta"]["H_sInv"]/(snap["meta"]["nH_cm3"]*x1s)
    channels = np.arange(313,dtype=float)
    patterns = [np.ones(313),np.cos((channels+.25)*.37),np.sin((channels+.7)*.23)]
    for j,pattern in enumerate(patterns):
        COUNTS["frozen_history_rhs_directions"] += 1
        tau = 2. if j == 2 else None
        system_matrix, system_source = matrix.copy(), source.copy()
        absorption = 1. if tau is None else float(-mp.expm1(-mp.mpf(tau)))
        rate_delta = r0*(absorption-1.)
        system_matrix[1,1] += rate_delta
        system_source[1] += rate_delta*3*x1s*snap["u0"][311]
        baseline = saved["X0"] if tau is None else dense_solve(system_matrix,system_source)
        du = .005*np.maximum(np.abs(snap["u0"]),1e-30)*pattern
        literal_rhs = oracle.rhs(r0,x1s,snap["dtau"],snap["tvv"][0],du)
        literal_rhs[1] *= absorption
        actual_rhs = frozen.source_increment(du,tau)
        ev.parity(f"frozen{j}:Mstar",frozen.Mstar(tau),system_matrix,np.abs(system_matrix),64*EPS)
        ev.parity(f"frozen{j}:source_row_C",actual_rhs,literal_rhs,np.abs(literal_rhs),128*EPS)
        ev.parity(f"frozen{j}:baseline_source",frozen.source_at(snap["u0"],tau),system_source,
                  np.abs(source)+np.abs(system_source),128*EPS)
        ev.parity(f"frozen{j}:perturbed_source",frozen.source_at(snap["u0"]+du,tau),
                  system_source+literal_rhs,np.abs(system_source)+np.abs(literal_rhs),128*EPS)
        delta = dense_solve(system_matrix,literal_rhs)
        plus = dense_solve(system_matrix,system_source+literal_rhs)
        gross = np.abs(system_matrix) @ np.abs(delta)+np.abs(literal_rhs)
        ev.parity(f"frozen{j}:backward",frozen.Mstar(tau) @ delta,actual_rhs,gross,5e-12)
        ev.parity(f"frozen{j}:actual_resolved_state",baseline+delta,plus,
                  np.abs(baseline)+np.abs(delta)+np.abs(plus),5e-9)
        u_plus = snap["u0"]+du
        c_out = oracle.outgoing(plus,u_plus,x1s,frozen.TR,snap["dtau"],snap["tvr"],snap["tvv"])
        if tau is not None:
            dm,xm,gm,am=map(mp.mpf,(u_plus[311],plus[1],x1s,absorption))
            c_out[311]=float(dm+(xm/(3*gm)-dm)*am)
        py_out = frozen.outgoing(plus,u_plus,tau)
        ev.parity(f"frozen{j}:actual_outgoing_C",py_out,c_out,np.abs(c_out)+np.abs(py_out),128*EPS)
        c_tangent = oracle.outgoing(delta,du,x1s,frozen.TR,snap["dtau"],snap["tvr"],snap["tvv"])
        if tau is not None:
            dm,xm,gm,am=map(mp.mpf,(du[311],delta[1],x1s,absorption))
            c_tangent[311]=float((1-am)*dm+am*xm/(3*gm))
        py_tangent = frozen.outgoing_jvp(delta,du,tau)
        ev.parity(f"frozen{j}:all_channel_outgoing_JVP_C",py_tangent,c_tangent,
                  np.abs(c_tangent)+np.abs(py_tangent),5e-9)
        ev.arrays[f"frozen_direction{j}"] = du
        ev.arrays[f"frozen_rhs{j}"] = np.vstack((actual_rhs,literal_rhs))
        ev.arrays[f"frozen_states{j}"] = np.vstack((delta,plus))
        ev.arrays[f"frozen_outgoing{j}"] = np.vstack((py_out,c_out,py_tangent,c_tangent))
        ev.row(group="frozen_history",direction=j,tau="native_thick" if tau is None else tau,
               nonzero_incoming_channels=int(np.count_nonzero(du)),
               dense_rhs_solves=2 if tau is None else 3,max_state_change=float(np.max(abs(delta))))
    # A positive comparison vector supplies a conditional all-channel error
    # envelope for this one frozen Z-matrix. It is not a physical-history bound.
    witness = dense_solve(matrix,np.ones(313))
    mv = matrix @ witness
    # Conditional IEEE binary64 dot-product enclosure, including a separate
    # error allocation for the computed sum of absolute products. EPS here is
    # twice the unit roundoff; 2*n+4 deliberately overcounts a multiply/add dot.
    # The small absolute term also covers gradual-underflow/flush-to-zero loss.
    # nextafter makes the final divisions, products and subtraction outward.
    n = matrix.shape[1]
    operations = 2*n+4
    gamma = np.nextafter((operations*EPS)/(1-operations*EPS),np.inf)
    underflow_reserve = operations*np.finfo(float).tiny
    sumabs_fl = np.abs(matrix) @ np.abs(witness)
    sumabs_numerator = np.nextafter(sumabs_fl+underflow_reserve,np.inf)
    sumabs_denominator = np.nextafter(1-gamma,-np.inf)
    sumabs_upper = np.nextafter(sumabs_numerator/sumabs_denominator,np.inf)
    rounding_reserve = np.nextafter(gamma*sumabs_upper,np.inf)
    rounding_reserve = np.nextafter(rounding_reserve+underflow_reserve,np.inf)
    lower = np.nextafter(mv-rounding_reserve,-np.inf)
    z_matrix = np.all(matrix-np.diag(np.diag(matrix)) <= 0)
    certificate = (z_matrix and np.all(np.isfinite(sumabs_upper))
                   and np.all(witness>0) and np.all(lower>0))
    ev.check("frozen:positive_comparison_witness",certificate,
             Z_matrix=z_matrix,min_witness=float(witness.min()),min_Mv_lower=float(lower.min()),
             gamma_operations=operations,gamma_upper=gamma,
             dot_product_assumptions="binary64 multiply/add or FMA, at most 2*n+4 rounding steps; no overflow",
             sumabs_rounding_included=True,underflow_absolute_reserve=underflow_reserve)
    if certificate:
        for j in range(2):
            bound_rhs = np.abs(ev.arrays[f"frozen_rhs{j}"][1])
            scaled_rhs_upper = np.nextafter(bound_rhs/lower,np.inf)
            envelope = np.nextafter(witness*np.max(scaled_rhs_upper),np.inf)
            delta = ev.arrays[f"frozen_states{j}"][0]
            ev.check(f"frozen{j}:conditional_input_envelope",np.all(abs(delta)<=envelope*(1+128*EPS)),
                     max_ratio=float(np.max(abs(delta)/np.maximum(envelope,1e-300))),
                     input_domain="represented binary64 M and explicit manufactured B*du; physical history uncalibrated")
        ev.arrays["positive_comparison_witness"] = witness
        ev.arrays["positive_comparison_Mv_lower"] = lower


def interpolation_bounds(ev):
    mp.mp.dps = 80
    families = {"exp":lambda x:mp.exp(mp.mpf("0.7")*x),
                "cos":lambda x:2+mp.cos(mp.mpf("1.3")*x)}
    for name,func in families.items():
        for h in (.25,.125,.0625):
            for alpha in (0.,.125,.25,.375,.5,.625,.75,.875):
                COUNTS["analytic_history_queries"] += 1
                y0m,y1m = func(mp.mpf(0)),func(mp.mpf(h))
                y0,y1 = float(y0m),float(y1m)
                err0,err1 = float(abs(mp.mpf(y0)-y0m)),float(abs(mp.mpf(y1)-y1m))
                eta = h*alpha
                expected = func(mp.mpf(eta))
                got = hb.interpolation(0.,h,[y0,y1],2,eta)
                curvature = float(mp.mpf("0.49")*mp.exp(mp.mpf("0.7")*mp.mpf(h))) if name=="exp" else 1.69
                envelope = hb.interpolation_envelope(h,alpha,curvature,err0,err1)
                arithmetic = 64*EPS*(abs((1-alpha)*y0)+abs(alpha*y1))
                actual_error = float(abs(mp.mpf(got["value"])-expected))
                ev.check(f"envelope:{name}:{h}:{alpha}",actual_error<=envelope+arithmetic,
                         actual_error=actual_error,envelope=envelope,arithmetic_allocation=arithmetic,
                         curvature_bound=curvature,manufactured_domain=True)
                direct_envelope = curvature*h*h*alpha*(1-alpha)/2+(1-alpha)*err0+alpha*err1
                ev.parity(f"envelope_formula:{name}:{h}:{alpha}",envelope,direct_envelope,
                          direct_envelope,64*EPS)
                ev.row(group="analytic_history",family=name,h=h,alpha=alpha,error=actual_error,
                       envelope=envelope,arithmetic=arithmetic,curvature=curvature,
                       source_value=str(expected),interpolated=got["value"],manufactured=True)


def invalid_and_mutations(ev, frozen):
    tests = [
      ("negative_tau",lambda:hb.boundary(0.,0.,1.,-.1)),
      ("zero_q",lambda:hb.boundary(0.,0.,1.,1.,0.)),
      ("zero_x1s",lambda:hb.boundary(0.,0.,0.,1.)),
      ("nan_incoming",lambda:hb.boundary(float("nan"),0.,1.,1.)),
      ("negative_total_incoming",lambda:hb.boundary(-2.,0.,1.,1.,reference_occupation=1.)),
      ("negative_total_source",lambda:hb.boundary(0.,-6.,1.,1.,reference_occupation=1.)),
      ("zero_spacing",lambda:hb.interpolation(0.,0.,[0.,1.],2,.1)),
      ("negative_spacing",lambda:hb.interpolation(0.,-1.,[0.,1.],2,.1)),
      ("exact_latest",lambda:hb.interpolation(0.,1.,[0.,1.,2.],3,2.)),
      ("future_query",lambda:hb.interpolation(0.,1.,[0.,1.,2.],3,2.1)),
      ("missing_known_prefix",lambda:hb.interpolation(0.,1.,[0.],3,.5)),
      ("nonfinite_query",lambda:hb.interpolation(0.,1.,[0.,1.],2,float("nan"))),
      ("negative_curvature",lambda:hb.interpolation_envelope(1.,.5,-1.)),
      ("alpha_outside_cell",lambda:hb.interpolation_envelope(1.,1.1,1.)),
      ("duplicate_owner",lambda:hb.line_ledger(0.,1e-12,.7,2.,250.,5e-14,owner=["event","boundary"])),
      ("unknown_owner",lambda:hb.line_ledger(0.,1e-12,.7,2.,250.,5e-14,owner="both")),
      ("wrong_history_shape",lambda:hb.incoming_history(0.,1.,np.zeros((313,3)),3,.5,frozen.energies)),
      ("bad_source_energy",lambda:hb.native_links(-np.ones(311))),
      ("nonsmooth_query_knot",lambda:hb.interpolation_jvp(hb.interpolation(0.,1.,[0.,1.,3.],3,1.),[0.,0.,0.],1.)),
      ("optical_ratio_overflow",lambda:hb.boundary(0.,0.,1.,1e308,1e-308)),
    ]
    for name,call in tests:
        COUNTS["invalid_owner_cases"] += 1
        try:
            call()
        except (ValueError,TypeError,IndexError,OverflowError) as exc:
            ev.check("invalid:"+name,True,exception=type(exc).__name__,message=str(exc))
        else:
            ev.check("invalid:"+name,False,exception=None)
    # Four explicit corrupted alternatives, evaluated on already bounded inputs.
    din,xr,x1s,tau,q = 1e-12,6e-12,.5,.3,1.4
    valid = hb.boundary(din,xr,x1s,tau,q)
    sign_mutant = din+(xr/(3*x1s)-din)*(-math.expm1(+tau/q))
    ev.check("mutation:transfer_sign",abs(sign_mutant-valid["outgoing"])>1e-3*abs(valid["outgoing"]))
    led = hb.line_ledger(din,xr,x1s,tau,250.,5e-14,q)
    wrong_normalization = LYA_FACT*5e-14*q*valid["delta"]
    ev.check("mutation:missing_3e6_normalization",abs(wrong_normalization-led["R"])>.9*abs(led["R"]))
    try:
        hb.interpolation(0.,1.,[0.,1.,1e30],2,1.)
    except ValueError:
        blocked = True
    else:
        blocked = False
    ev.check("mutation:inclusive_future_read",blocked,mutant_would_read_current_column=True)
    duplicate = 2*led["radiation_J_m3_s"]+led["atomic_internal_J_m3_s"]
    ev.check("mutation:duplicate_source",abs(duplicate)>128*EPS*(2*abs(led["radiation_J_m3_s"])+abs(led["atomic_internal_J_m3_s"])))
    COUNTS["deliberate_mutations"] += 4


def figures(ev):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.alpha":.25})
    rows = [r for r in ev.rows if r["group"]=="local"]
    fig,axes = plt.subplots(1,2,figsize=(11,4.3),layout="constrained")
    for q in (.6,1.,1.4):
        subset = [r for r in rows if r["q"]==q and r["drive"]=="emission"]
        axes[0].plot([r["tau"] for r in subset],[r["absorbed_fraction"] for r in subset],"o-",label=f"q = {q:g}")
    axes[0].set(xscale="symlog",xlabel=r"Optical depth $\tau$ (selected samples)",ylabel=r"Transferred fraction $1-e^{-\tau/q}$",ylim=(-.03,1.05))
    axes[0].set_xscale("symlog",linthresh=1e-10)
    axes[0].legend()
    axes[1].scatter([r["tau"] for r in rows],[r["scaled_outgoing_error"]/EPS for r in rows],s=24,alpha=.6)
    axes[1].set_xscale("symlog",linthresh=1e-10)
    axes[1].set(xlabel=r"Optical depth $\tau$",ylabel=r"Outgoing error / (gross scale $\times\epsilon_{64}$)")
    axes[1].axhline(128.,color="tab:red",linestyle="--",label="Frozen arithmetic limit: 128")
    axes[1].legend()
    fig.suptitle("Local finite boundary: 54 controls; exact 80-digit reference")
    fig.savefig(ev.output/"history_boundary_controls.png",dpi=160)
    plt.close(fig)
    data = [r for r in ev.rows if r["group"]=="analytic_history"]
    fig,axes = plt.subplots(1,2,figsize=(11,4.3),layout="constrained")
    colors={"exp":"tab:blue","cos":"tab:orange"}
    for family in ("exp","cos"):
        hs=sorted({r["h"] for r in data})
        err=[max(r["error"] for r in data if r["family"]==family and r["h"]==h) for h in hs]
        bnd=[max(r["envelope"] for r in data if r["family"]==family and r["h"]==h) for h in hs]
        axes[0].loglog(hs,err,"o-",color=colors[family],label=f"{family}: measured")
        axes[0].loglog(hs,bnd,"s--",color=colors[family],label=f"{family}: curvature bound")
        rr=[r for r in data if r["family"]==family and r["alpha"]>0]
        axes[1].scatter([r["alpha"] for r in rr],[r["error"]/(r["envelope"]+r["arithmetic"]) for r in rr],color=colors[family],label=family,s=25,alpha=.6)
    axes[0].set(xlabel=r"Grid spacing $h$",ylabel="Maximum absolute interpolation error")
    axes[0].legend(fontsize=8)
    axes[1].set(xlabel=r"Cell fraction $\alpha$",ylabel="Error / (conditional bound + arithmetic)",ylim=(-.03,1.08))
    axes[1].axhline(1,color="black",linestyle="--")
    axes[1].legend()
    fig.suptitle("Manufactured histories: conditional interpolation bound; physical calibration remains open")
    fig.savefig(ev.output/"history_interpolation_bounds.png",dpi=160)
    plt.close(fig)
    COUNTS["figures_from_saved_rows"] += 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    start_wall=time.perf_counter()
    start_self=resource.getrusage(resource.RUSAGE_SELF)
    start_child=resource.getrusage(resource.RUSAGE_CHILDREN)
    ev=Evidence(out)
    fatal=None
    mp.mp.dps=80
    try:
        if hashlib.sha256((ROOT/"FROZEN_CONTRACT.md").read_bytes()).hexdigest()!=CONTRACT_SHA:
            raise ValueError("pre-code frozen contract identity changed")
        csv_path=PARENT/"inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv"
        if hashlib.sha256(csv_path.read_bytes()).hexdigest()!=CSV_SHA:
            raise ValueError("immutable native input changed")
        prepared=PARENT/"results/attempt001/PREPARED_BLOCKS.npz"
        snap=read_snapshot(csv_path)
        with np.load(prepared,allow_pickle=False) as bundle:
            saved={key:bundle[key] for key in ("M","source","X0")}
        frozen=hb.load_frozen(csv_path,prepared)
        oracle=build_oracle(out)
        local_controls(ev,frozen)
        scalar_controls(ev,oracle)
        mapping=mapping_control(ev,oracle,frozen)
        derivatives(ev,mapping)
        frozen_directions(ev,oracle,frozen,snap,saved)
        interpolation_bounds(ev)
        invalid_and_mutations(ev,frozen)
        np.savez_compressed(out/"raw_arrays.npz",**ev.arrays)
        figures(ev)
    except Exception as exc:
        fatal={"exception":type(exc).__name__,"message":str(exc)}
        (out/"exception.log").write_text(traceback.format_exc())
        if ev.arrays:
            np.savez_compressed(out/"partial_raw_arrays.npz",**ev.arrays)
    end_self=resource.getrusage(resource.RUSAGE_SELF)
    end_child=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_self=end_self.ru_utime+end_self.ru_stime-start_self.ru_utime-start_self.ru_stime
    cpu_children=end_child.ru_utime+end_child.ru_stime-start_child.ru_utime-start_child.ru_stime
    wall=time.perf_counter()-start_wall
    peak_rss_kib=max(end_self.ru_maxrss,end_child.ru_maxrss)
    ev.check("resource:one_process_allocation",cpu_self+cpu_children<=60 and wall<=180 and peak_rss_kib<=1024*1024,
             cpu_seconds=cpu_self+cpu_children,wall_seconds=wall,peak_rss_KiB=peak_rss_kib,
             note="controller accumulates this attempt with any later repair/review")
    maxima={"local_ray_controls":54,"scalar_interpolation_controls":20,"native_mapping_comparisons":1,
            "derivative_directions":12,"frozen_history_rhs_directions":3,"dense_rhs_solves":8,
            "analytic_history_queries":48,"invalid_owner_cases":20,"deliberate_mutations":4,"figures_from_saved_rows":2}
    ev.check("resource:finite_case_caps",all(COUNTS[k]<=v for k,v in maxima.items()),counts=dict(COUNTS),caps=maxima)
    failures=[row for row in ev.checks if row["result"]=="fail"]
    status="PASS_SCOPED" if fatal is None and not failures else "FAILED_PRESERVED"
    identity={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [ROOT/"FROZEN_CONTRACT.md",ROOT/"PREEXEC_ADDENDUM.md",ROOT/"vendor/hyrec_params.h",
                        ROOT/"code/history_boundary.py",Path(__file__),ROOT/"code/native_oracle_build.py"] if p.exists()}
    summary={"unit":"REC-HISTORY-01","status":status,"fatal":fatal,"counts":dict(COUNTS),
             "checks":len(ev.checks),"checks_pass":len(ev.checks)-len(failures),"checks_fail":len(failures),
             "failed_ids":[r["id"] for r in failures],"cpu_self_seconds":cpu_self,
             "cpu_children_seconds":cpu_children,"cpu_total_seconds":cpu_self+cpu_children,
             "wall_seconds":wall,"peak_rss_KiB":peak_rss_kib,"threads":1,"mpmath_digits":80,
             "source_and_code_sha256":identity,"old_LINE02_reruns":0,"new_IVP":0,
             "native_recombination_runtime":0,"actual_history_calibration":"INPUT_DEPENDENT_UNCALIBRATED"}
    write_json(out/"SUMMARY.json",summary)
    ev.handle.close();ev.raw_handle.close()
    print(json.dumps(clean(summary),indent=2))
    return 0 if status=="PASS_SCOPED" else 1


if __name__=="__main__":
    sys.exit(main())
