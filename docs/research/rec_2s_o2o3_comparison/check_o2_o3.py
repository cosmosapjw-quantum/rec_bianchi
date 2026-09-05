#!/usr/bin/env python3
"""Research-only O2/O3 checks; calls parent APIs, creates no physical map.

No output files are changed unless --output-dir is supplied. Existing result
files are never overwritten. Run with -B to avoid modifying inherited caches.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

import mpmath as mp
import numpy as np
import sympy as sp

PARENT = "e65ae5c211db4e3375e73410a404f0b23da084d4"
PARENT_TREE = "e12a4ae4ed17859e4625f80fb0fa86e83a034036"
SOURCE = "src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py"
CONTRACT = "docs/research/original_hyrec_2s_input_trace/OWNER_REVIEW_CONTRACT.json"
ARCHIVE = "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
PINS = {
    SOURCE: "26ddc41e24fadf0bdd19f1924e1a429d602d9c19",
    CONTRACT: "e5d1d47199428f25ef05240f938d667f18616457",
    ARCHIVE: "e02869896ab3b826eb64d8233f2a1272366c1fc8",
    "scripts/c_harness/original_hyrec_two_photon_raman_harness.c":
        "a21176fada74481663b6296d4d3278f0b1005b39",
    "tests/trajectory/test_hyrec_two_photon_raman.py":
        "81cca71b42c08b32c194da3987ab0f41c6dff670",
}
MEMBERS = {
    "HyRec/two_photon_tables.dat":
        "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9",
    "HyRec/hydrogen.c":
        "421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b",
    "HyRec/hydrogen.h":
        "e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba",
}
EPS = np.finfo(float).eps
# Fixed before execution: elementary binary64 errors; no relative null test.
COEFFICIENT_BOUND = 64 * EPS
JVP_COMPONENT_BOUND = 128 * EPS
LITERAL_EXP_BOUND = 2e-13  # existing source-formula/C comparison tolerance
FD_FINE_ABS_BOUND = 1e-7   # centred h=2.5e-4, smooth manufactured rational path


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def symbolic_checks():
    a, u, g, fc, ft, nc = sp.symbols("a x_u x_g f_c f_t n_c")
    qc, qt = sp.symbols("q_c q_t", positive=True)
    pair = a * (u * (1 + fc) * (1 + ft) - g * fc * ft)
    native = a * (u * (1 + nc) - g * nc * ft)
    correction = a*u*(1+nc)*ft + a*(fc-nc)*(u*(1+ft)-g*ft)
    n = qc/(1-qc)
    lte = {u: g*qc*qt, fc: n, nc: n}
    checks = {}

    def zero(name, expression):
        result = sp.simplify(expression)
        require(result == 0, name + ": " + str(result))
        checks[name] = str(result)

    zero("paired_minus_native_decomposition", pair-native-correction)
    zero("C_minus_D_equals_a", a*(1+n)-a*n-a)
    zero("D_over_C_equals_qc", (a*n)/(a*(1+n))-qc)
    zero("paired_Planck_null", pair.subs(lte).subs(ft, qt/(1-qt)))
    zero("native_Wien_null", native.subs(lte).subs(ft, qt))
    zero("native_at_Planck_nonzero_formula",
         native.subs(lte).subs(ft, qt/(1-qt)) + a*g*n*qt**2/(1-qt))
    zero("paired_at_Wien_nonzero_formula", pair.subs(lte).subs(ft, qt)-a*g*n*qt**2)
    zero("vacuum_spontaneous_limit", pair.subs({fc: 0, ft: 0})-a*u)

    w, z, dw, dz, dg = sp.symbols("w_t z_b d_w_t d_z_b d_x_g")
    da, du, dfc = sp.symbols("d_a d_x_u d_f_c")
    inverse = w + z/g
    dft = dw + dz/g - z*dg/g**2
    zero("inverse_JVP", sp.diff(inverse,w)*dw+sp.diff(inverse,z)*dz
         +sp.diff(inverse,g)*dg-dft)
    dirs = {a: da, u: du, g: dg, fc: dfc, w: dw, z: dz}
    composed = pair.subs(ft, inverse)
    total = sum(sp.diff(composed, v)*d for v,d in dirs.items())
    chain = (sp.diff(pair,a)*da + sp.diff(pair,u)*du + sp.diff(pair,g)*dg
             +sp.diff(pair,fc)*dfc + sp.diff(pair,ft)*dft).subs(ft,inverse)
    zero("paired_composed_inverse_JVP", total-chain)

    C, D, dC, dD = sp.symbols("C D d_C d_D")
    native_inverse = C*u-D*(g*w+z)
    dn = dC*u+C*du-dD*(g*w+z)-D*(w*dg+g*dw+dz)
    zero("native_composed_inverse_JVP",
         sum(sp.diff(native_inverse,v)*d for v,d in
             {C:dC,D:dD,u:du,g:dg,w:dw,z:dz}.items())-dn)
    Cq, Dq = a/(1-qc), a*qc/(1-qc)
    departure = Cq*(u-g*qc*qt)-Dq*z
    native_total = Cq*u-Dq*(g*qt+z)
    zero("native_departure_cancellation", departure-native_total)
    dqc,dqt = sp.symbols("d_q_c d_q_t")
    zero("native_departure_cancellation_JVP",
         sum(sp.diff(departure-native_total,v)*d for v,d in
             {a:da,qc:dqc,qt:dqt,u:du,g:dg,z:dz}.items()))
    zero("reference_balance_derivative",
         sum(sp.diff(Dq*qt-Cq*qc*qt,v)*d for v,d in {a:da,qc:dqc,qt:dqt}.items()))

    T,E,k = sp.symbols("T E k_B", positive=True)
    occupation = 1/(sp.exp(E/(k*T))-1)
    reference = sp.exp(-E/(k*T))
    zero("blackbody_d_log_T", T*sp.diff(occupation,T)
         -E/(k*T)*occupation*(1+occupation))
    zero("Wien_d_log_T", T*sp.diff(reference,T)-E/(k*T)*reference)
    theta,fs,me,Tr = sp.symbols("Theta fsR meR T_phys", positive=True)
    thermal_coordinate = Tr/(fs**2*me)  # constant k_B/eV cancels in log derivative
    p,al,m = sp.symbols("d_log_T_phys d_log_fsR d_log_meR")
    zero("source_temperature_coordinate_chain",
         (sp.diff(thermal_coordinate,Tr)*Tr*p + sp.diff(thermal_coordinate,fs)*fs*al
          +sp.diff(thermal_coordinate,me)*me*m)/thermal_coordinate-(p-2*al-m))
    rate_scale = fs**8*me
    zero("rate_scale_chain", (sp.diff(rate_scale,fs)*fs*al
         +sp.diff(rate_scale,me)*me*m)/rate_scale-(8*al+m))

    R,Et,Ec = sp.symbols("R E_t E_c")
    zero("atomic_nuclei_number", -R+R)
    zero("two_photon_number_from_distinct_ledgers", R+R-2*R)
    zero("energy_with_both_photons", -(Et+Ec)*R+Et*R+Ec*R)
    zero("atom_plus_tracked_energy_equals_minus_bath", -(Et+Ec)*R+Et*R+Ec*R)
    return checks


def fraction_and_existing_api_checks(PhysicalBin):
    qc,qt,g,u,a = F(1,2),F(1,4),F(1,2),F(1,16),F(1)
    nc = qc/(1-qc)
    # Frequency metadata are manufactured, not hydrogen 2s frequencies or cells.
    kwargs = dict(process="two_photon", integrated_rate_s_inv=float(a),
                  transition_frequency_Hz=3e14, companion_frequency_Hz=1e14,
                  tracked_frequency_Hz=2e14, upper_population=float(u),
                  ground_population=float(g), upper_to_ground_degeneracy_ratio=1.0)
    source = PhysicalBin(**kwargs)
    cases=[]
    for name,ft,expected_native,expected_pair in [
        ("Planck",F(1,3),-F(1,24),F(0)),
        ("Wien",F(1,4),F(0),F(1,32)),
    ]:
        native = a*(u*(1+nc)-g*nc*ft)
        forward = a*u*(1+nc)*(1+ft)
        reverse = a*g*nc*ft
        paired = forward-reverse
        require((native,paired)==(expected_native,expected_pair), name)
        actual_forward,actual_reverse = source.paired_rates(
            companion_occupation=float(nc),tracked_occupation=float(ft))
        actual_net = source.net_action(float(nc),float(ft))
        require(abs(actual_forward-float(forward)) <= 8*EPS, name+" forward")
        require(abs(actual_reverse-float(reverse)) <= 8*EPS, name+" reverse")
        require(abs(actual_net-float(paired)) <= 8*EPS, name+" existing API")
        cases.append(dict(field=name,tracked_occupation=str(ft),native=str(native),
                          paired=str(paired),forward=str(forward),reverse=str(reverse),
                          existing_api_net=actual_net,existing_api_forward=actual_forward,
                          existing_api_reverse=actual_reverse))
    off_blackbody=[]
    for fc in [F(3,4),F(5,4)]:
        ft=F(1,3)
        rp=a*(u*(1+fc)*(1+ft)-g*fc*ft)
        rn=a*(u*(1+nc)-g*nc*ft)
        term1=a*u*(1+nc)*ft
        term2=a*(fc-nc)*(u*(1+ft)-g*ft)
        require(rp-rn==term1+term2,"off-blackbody correction")
        require(abs(source.net_action(float(fc),float(ft))-float(rp))<=8*EPS,
                "off-blackbody API")
        off_blackbody.append(dict(fc=str(fc),native=str(rn),paired=str(rp),
                                  high_stimulation=str(term1),companion_change=str(term2)))

    ledgers=[]
    for name,R in [("paired_Wien",F(1,32)),("native_Planck_proposed_ledger",-F(1,24))]:
        du_event,dg_event,dNt,dNc=-R,R,R,R
        atom_energy,tracked_energy,companion_energy=-3*R,2*R,R
        require(du_event+dg_event==0,"nuclei ledger")
        require(dNt==R and dNc==R and dNt+dNc==2*R,"distinct photon ledgers")
        require(atom_energy+tracked_energy+companion_energy==0,"energy ledger")
        require(atom_energy+tracked_energy!=0,"omitted companion energy detector")
        ledgers.append(dict(case=name,event_rate=str(R),d_x_u=str(du_event),d_x_g=str(dg_event),
                            tracked_count_rate=str(dNt),companion_count_rate=str(dNc),
                            total_photon_count_rate=str(dNt+dNc),atomic_energy_rate=str(atom_energy),
                            tracked_energy_rate=str(tracked_energy),companion_energy_rate=str(companion_energy),
                            energy_sum="0",energy_unit="E_star per H per second, E_star=h*(1e14 Hz)",
                            status="CONDITIONAL_STOICHIOMETRY_NOT_POPULATION_OR_DEPOSITION_EXECUTION"))

    # Nonzero signed distortion, reference direction and denominator direction.
    w,z,fc = F(1,4),F(1,24),F(3,4)
    da,du,dg,dfc,dz,dw = F(1,7),F(1,13),-F(1,11),F(1,17),F(1,19),F(1,23)
    ft=w+z/g
    dft=dw+dz/g-z*dg/g**2
    factor=u*(1+fc)*(1+ft)-g*fc*ft
    dfactor=(du*(1+fc)*(1+ft)-dg*fc*ft
             +(u*(1+ft)-g*ft)*dfc+(u*(1+fc)-g*fc)*dft)
    expected=da*factor+a*dfactor
    direction=dict(d_integrated_rate_s_inv=float(da),d_upper_population=float(du),
                   d_ground_population=float(dg),d_companion_occupation=float(dfc),
                   d_tracked_occupation=float(dft))
    actual=source.jvp(companion_occupation=float(fc),tracked_occupation=float(ft),**direction)
    require(abs(actual-float(expected))<=32*EPS,"inverse JVP existing API")
    reference_loss=a*(u*(1+fc)-g*fc)*dw
    denominator_loss=a*(u*(1+fc)-g*fc)*(-z*dg/g**2)
    require(reference_loss != 0 and denominator_loss != 0,"missing-term detectors")
    fd=[]
    for step in [1e-3,5e-4,2.5e-4]:
        actions=[]
        for sign in [1,-1]:
            h=sign*step
            shifted=replace(source,integrated_rate_s_inv=float(a)+h*float(da),
                            upper_population=float(u)+h*float(du),
                            ground_population=float(g)+h*float(dg))
            total=float(w)+h*float(dw)+(float(z)+h*float(dz))/shifted.ground_population
            actions.append(shifted.net_action(float(fc)+h*float(dfc),total))
        derivative=(actions[0]-actions[1])/(2*step)
        fd.append(dict(step=step,derivative=derivative,abs_error=abs(derivative-float(expected))))
    require(fd[-1]["abs_error"]<FD_FINE_ABS_BOUND,"inverse JVP centred difference")
    require(fd[-1]["abs_error"]<fd[0]["abs_error"],"inverse JVP convergence")
    inverse_result=dict(w_t=str(w),z_b=str(z),x_g=str(g),f_t=str(ft),
                        d_w_t=str(dw),d_z_b=str(dz),d_x_g=str(dg),d_f_t=str(dft),
                        d_a=str(da),d_x_u=str(du),d_f_c=str(dfc),
                        exact_JVP=str(expected),existing_JVP=actual,
                        omitted_reference_JVP_error=str(-reference_loss),
                        omitted_denominator_JVP_error=str(-denominator_loss),finite_differences=fd,
                        x_g_zero="UNDEFINED_INVERSE_NOT_EXTENDED",valid_domain="x_g>0, f_t>=0")

    # Fixed z,u,g,a with a prescribed blackbody companion: changing log T also
    # changes the Wien reference. The exact result is -17 log(2)/48.
    log2=sp.log(2)
    dfcT=2*log2
    dftT=log2/2
    expectedT=-17*log2/48
    exactT=a*((u*(1+F(1,3))-g*F(1,3))*dfcT+(u*2-g)*dftT)
    require(sp.simplify(exactT-expectedT)==0,"thermal chain exact")
    thermal=source.jvp(companion_occupation=1.0,tracked_occupation=1/3,
                       d_integrated_rate_s_inv=0.0,d_upper_population=0.0,
                       d_ground_population=0.0,d_companion_occupation=float(dfcT),
                       d_tracked_occupation=float(dftT))
    require(abs(thermal-float(expectedT))<=32*EPS,"thermal existing JVP")
    thermal_fd=[]
    for step in [1e-3,5e-4,2.5e-4]:
        actions=[]
        for sign in [1,-1]:
            inv_temperature=math.exp(-sign*step)
            fcb=1/math.expm1(math.log(2)*inv_temperature)
            wt=math.exp(-math.log(4)*inv_temperature)
            actions.append(source.net_action(fcb,wt+float(z/g)))
        derivative=(actions[0]-actions[1])/(2*step)
        thermal_fd.append(dict(step=step,derivative=derivative,
                               abs_error=abs(derivative-float(expectedT))))
    require(thermal_fd[-1]["abs_error"]<FD_FINE_ABS_BOUND,"thermal centred difference")
    require(thermal_fd[-1]["abs_error"]<thermal_fd[0]["abs_error"],"thermal convergence")
    # Following the equilibrium manifold is a third, explicitly different path:
    # LTE upper population and BOTH Planck occupations vary with temperature.
    duLTE=sp.Rational(3,16)*log2
    dftPlanck=sp.Rational(8,9)*log2
    tangent_exact=duLTE*2*sp.Rational(4,3)-dfcT/sp.Integer(12)-3*dftPlanck/8
    require(sp.simplify(tangent_exact)==0,"Planck manifold tangent")
    tangent_api=source.jvp(companion_occupation=1.0,tracked_occupation=1/3,
                          d_integrated_rate_s_inv=0,d_upper_population=float(duLTE),
                          d_ground_population=0,d_companion_occupation=float(dfcT),
                          d_tracked_occupation=float(dftPlanck))
    require(abs(tangent_api)<=32*EPS,"Planck manifold tangent API")
    return dict(manufactured_frequencies_Hz={k:v for k,v in kwargs.items() if "frequency" in k},
                manufactured_nulls=cases,off_blackbody=off_blackbody,number_energy_ledgers=ledgers,
                inverse_JVP=inverse_result,
                thermal_chain=dict(path="fixed signed z_b, populations, rate and reference energies",
                                   exact_JVP=str(expectedT),existing_JVP=thermal,
                                   omitted_companion_error=str(log2/6),
                                   omitted_reference_error=str(3*log2/16),
                                   finite_differences=thermal_fd),
                Planck_manifold_tangent=dict(exact="0",existing_JVP=tangent_api),
                physical_inputs_selected=False)


def coefficient_checks(table, Coupling, threshold):
    temperature,fs,mass=0.25882399309326415,1.013,0.987
    coupling=table.evaluate_canonical_coupling(radiation_temperature_eV=temperature,fsR=fs,meR=mass)
    require(isinstance(coupling,Coupling),"existing CanonicalTwoPhotonRamanCoupling")
    # A physical-temperature direction must first be converted to the source
    # temperature coordinate consumed by the existing canonical JVP.
    p,al,m=0.37,-0.11,0.23
    dtheta=p-2*al-m
    sigma=8*al+m
    actual_jvp=coupling.jvp(d_log_radiation_temperature=dtheta,d_log_fsR=al,d_log_meR=m).reshape(2,2,311)
    rows=[]
    max_coeff=max_literal=max_temp=max_jvp=0.0
    with mp.workdps(80):
        for b in range(140):
            ec=float(threshold-table.energy_eV[b])
            y=mp.mpf(ec)/mp.mpf(temperature)
            nc=1/mp.expm1(y)
            a=mp.mpf(fs)**8*mp.mpf(mass)*mp.mpf(float(table.A2s_s_inv[b]))
            C=a*(1+nc)
            D=a*nc
            thermal=a*y*nc*(1+nc)
            dc=mp.mpf(sigma)*C+mp.mpf(dtheta)*thermal
            dd=mp.mpf(sigma)*D+mp.mpf(dtheta)*thermal
            cvalue=float(coupling.real_to_virtual_s_inv[0,b])
            dvalue=float(coupling.virtual_to_real_s_inv[0,b])
            # Literal source-formula evaluation in Python, NOT original C.
            q=math.exp(-ec/temperature)
            literal=fs**8*mass*float(table.A2s_s_inv[b])/(1-q)
            coeff_error=max(float(abs(mp.mpf(cvalue)-C)/C),float(abs(mp.mpf(dvalue)-D)/D))
            literal_error=abs(literal-cvalue)/abs(cvalue)
            temp_error=max(float(abs(mp.mpf(float(coupling.d_real_to_virtual_d_log_temperature_s_inv[0,b]))-thermal)/thermal),
                           float(abs(mp.mpf(float(coupling.d_virtual_to_real_d_log_temperature_s_inv[0,b]))-thermal)/thermal))
            jvp_error=max(float(abs(mp.mpf(float(actual_jvp[0,0,b]))-dc)/(abs(sigma*C)+abs(dtheta*thermal))),
                          float(abs(mp.mpf(float(actual_jvp[1,0,b]))-dd)/(abs(sigma*D)+abs(dtheta*thermal))))
            require(coeff_error<=COEFFICIENT_BOUND,f"b={b} coefficients")
            require(literal_error<=LITERAL_EXP_BOUND,f"b={b} literal exp")
            require(temp_error<=JVP_COMPONENT_BOUND,f"b={b} temperature derivative")
            require(jvp_error<=JVP_COMPONENT_BOUND,f"b={b} transformed temperature JVP")
            max_coeff=max(max_coeff,coeff_error); max_literal=max(max_literal,literal_error)
            max_temp=max(max_temp,temp_error); max_jvp=max(max_jvp,jvp_error)
            rows.append(dict(b=b,source_line=b+1,energy_eV=float(table.energy_eV[b]),
                             normalized_A2s_s_inv=float(table.A2s_s_inv[b]),companion_eV=ec,
                             C_s_inv=cvalue,D_s_inv=dvalue,C_reference_80dps=mp.nstr(C,30),
                             D_reference_80dps=mp.nstr(D,30),dC_dlogTheta_s_inv=float(thermal),
                             dD_dlogTheta_s_inv=float(thermal),C_JVP=float(actual_jvp[0,0,b]),
                             D_JVP=float(actual_jvp[1,0,b]),coefficient_relative_error=coeff_error,
                             literal_exp_relative_error=literal_error,
                             temperature_derivative_relative_error=temp_error,JVP_component_scaled_error=jvp_error))
    require(np.array_equal(coupling.Tvr_offdiag_s_inv[0,:140],-coupling.real_to_virtual_s_inv[0,:140]),"Tvr signs")
    require(np.array_equal(coupling.Trv_offdiag_s_inv[0,:140],-coupling.virtual_to_real_s_inv[0,:140]),"Trv signs")
    metrics=dict(bins=140,diagnostic_inputs=dict(source_temperature_eV=temperature,fsR=fs,meR=mass),
                 direction=dict(d_log_T_phys=p,d_log_fsR=al,d_log_meR=m,
                                d_log_source_temperature=dtheta,d_log_rate_scale=sigma),
                 max_coefficient_relative_error=max_coeff,max_literal_exp_relative_error=max_literal,
                 max_temperature_derivative_relative_error=max_temp,
                 max_JVP_component_scaled_error=max_jvp,
                 subdomain_diagonal_increment_s_inv=float(np.sum(coupling.real_to_virtual_s_inv[0,:140])),
                 full_C_populateTS_executed=False,mpmath_precision_digits=80,
                 reference_note="Exact binary64 input values lifted to 80-digit arithmetic; not extra table precision.")
    return metrics,rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir",type=Path)
    args=parser.parse_args()
    repo=args.repo.resolve()
    require(git(repo,"rev-parse",PARENT+"^{tree}")==PARENT_TREE,"fixed parent tree")
    # Rooted files and parent objects are independently compared before import.
    for path,expected in PINS.items():
        require(git(repo,"rev-parse",PARENT+":"+path)==expected,path+" parent blob")
        require(blob((repo/path).read_bytes())==expected,path+" working bytes")
    owner=json.loads((repo/CONTRACT).read_text())
    require(all(x["status"]=="UNRESOLVED" for x in owner["required_owner_decisions"]),"O1-O6 remain unresolved")
    require(owner["deposition_inputs"]["B"] is None and owner["deposition_inputs"]["mu_m_inv3"] is None,"no B/mu")
    inherited=repo/CONTRACT
    verified_manifest=[]
    for line in (inherited.parent/"MANIFEST.sha256").read_text().splitlines():
        expected,name=line.split(maxsplit=1)
        name=name.strip().lstrip("*")
        require(hashlib.sha256((inherited.parent/name).read_bytes()).hexdigest()==expected,"PR65 "+name)
        verified_manifest.append(name)
    require(len(verified_manifest)==9,"PR65 payload count")
    archive_bytes=(repo/ARCHIVE).read_bytes()
    require(hashlib.sha256(archive_bytes).hexdigest()=="48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27","ZIP SHA256")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
        for member,expected in MEMBERS.items():
            require(hashlib.sha256(z.read(member)).hexdigest()==expected,member)
    sys.path.insert(0,str(repo/"src"))
    from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
        A2S_THRESHOLD_EV,CanonicalTwoPhotonRamanCoupling,
        OriginalHyRecTwoPhotonRamanTable,PhysicalTwoPhotonRamanBin,
    )
    table=OriginalHyRecTwoPhotonRamanTable.from_archive(repo/ARCHIVE)
    symbolic=symbolic_checks()
    manufactured=fraction_and_existing_api_checks(PhysicalTwoPhotonRamanBin)
    coefficients,rows=coefficient_checks(table,CanonicalTwoPhotonRamanCoupling,A2S_THRESHOLD_EV)
    result=dict(schema="rec-2s-o2o3-comparison-results/v1",status="CHECKS_PASSED_REVIEW_ONLY",
                parent_commit=PARENT,parent_tree=PARENT_TREE,source_blobs=PINS,
                original_member_sha256=MEMBERS,PR65_manifest_verified=verified_manifest,
                environment=dict(python=sys.version.split()[0],numpy=np.__version__,sympy=sp.__version__,
                                 mpmath=mp.__version__,platform=platform.platform()),
                thresholds=dict(coefficient_relative=COEFFICIENT_BOUND,
                                derivative_component_scaled=JVP_COMPONENT_BOUND,
                                literal_exp_relative=LITERAL_EXP_BOUND,FD_fine_absolute=FD_FINE_ABS_BOUND),
                symbolic_zero_residuals=symbolic,manufactured=manufactured,coefficients=coefficients,
                owner_obligations={x["id"]:x["status"] for x in owner["required_owner_decisions"]},
                not_executed=["full original C populateTS_2photon", "original HyRec history/trajectory",
                              "physical deposition or occupation-rate execution", "provider/physical admission"],
                C_coefficient_harness="Separate existing pytest, if run; see TARGETED_TEST.log and RUN_RECORD.json.",
                claim="NO_PASS_REC_PHYSICAL_SPLIT")
    encoded=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True,exist_ok=True)
        result_path=args.output_dir/"RESULTS.json"
        csv_path=args.output_dir/"COEFFICIENTS_2S.csv"
        require(not result_path.exists() and not csv_path.exists(),"refusing to overwrite results")
        with csv_path.open("x",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        with result_path.open("x") as f:
            f.write(encoded)
    print(encoded,end="")


if __name__=="__main__":
    main()
