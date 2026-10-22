"""Finite THERM02 adapter checks only: no ODE and no old source-table suite.

Expectations use retained scalar Mao algebra, independent SI/cgs Compton
formulae, analytic/continuous radiation integrals and finite differences.
These checks do not certify independent cooling accuracy or a trajectory.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
import scipy
from scipy.integrate import quad

from coupled_thermal import (
    ROOT, KB, EV_J, C_LIGHT, M_E, H_PLANCK, A_RAD, K_COMPTON, THOMSON,
    CoupledThermalAtomic, CoupledThermalSystem, compton_coefficients,
    frozen_subflow, lift34, restrict63, verify_reused_files,
)
import thermal as donor

sys.path.insert(0, str(ROOT / "vendor/pr121/code"))
from thermal_sources import mao_factor
from recombination_moments import RecombinationMoments


BASE_CONFIG = dict(Sigma_F=.15, matter_A=.6, radiation_A=.15,
                   Emax_eV=60., uv_multiplier=1., T0_K=1000.,
                   rr_closure="mao2017", cmb_branch="planck_reference")


def relative(a, b, floor=1e-300):
    aa, bb = np.asarray(a), np.asarray(b)
    return float(np.max(np.abs(aa-bb)/np.maximum(np.maximum(np.abs(aa), np.abs(bb)), floor)))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def physical_state(system, index):
    """Three declared synthetic physical points, not evolved trajectories."""
    states = (
        (0., 550., [.92, .08], [.88, .10, .02], [.55, .30, .10, .05], 1.),
        (.85, 8100., [.65, .35], [.45, .35, .20], [.25, .35, .25, .15], 1.025),
        (1.5, 31000., [.2, .8], [.15, .35, .50], [.10, .25, .30, .35], .98),
    )
    x, T, hydrogen, helium, lithium, photon_factor = states[index]
    y = system.expand(system.y0).copy()
    scaled = y[40:61]
    for name, group in system.atomic.isotope_groups.items():
        if name in ("n", "T"):
            scaled[list(group)] = 0.
        else:
            scaled[list(group)] = (hydrogen if name in ("H1", "D") else
                                    helium if name.startswith("He") else lithium)
    y[4] *= photon_factor
    y[1] += .005*index
    Y = scaled*system.scale
    eta = float((1+system.atomic.q) @ Y)
    y[62] = 1.5*eta*T
    require(np.array_equal(lift34(restrict63(y)), y), "fixture outside compact invariant")
    require(abs(system.atomic.A @ Y-1) < 3e-15, "fixture baryon inventory")
    return x, y


def check_source_identity():
    manifest = verify_reused_files()
    lock = json.loads((ROOT/"vendor/pr121/provenance/MAO_SOURCE_LOCK.json").read_text())
    for row in lock["files"]:
        b = (ROOT/"vendor/pr121"/row["path"]).read_bytes()
        require(len(b) == row["bytes"] and hashlib.sha256(b).hexdigest() == row["sha256"],
                "source lock disagreement")
    selected = ROOT/"vendor/pr121"/lock["selected_file"]
    require(hashlib.sha256(selected.read_bytes()).hexdigest() == lock["selected_sha256"],
            "selected six-row identity")
    require(len(manifest["files"]) == 70, "frozen reused file count")
    return dict(retained_files_verified=70, selected_rows=6,
                old_114_point_source_suite="NOT_RUN; retained result reused",
                number_coefficient_source="unchanged THERM01/REI PR220 donor")


def check_mao_vectorization():
    a = CoupledThermalAtomic()
    max_f = max_df = max_map = 0.
    # Four new adapter probes, not the 114 published-table points.
    temperatures = (317., 1733., 13791., 280123.)
    rows = json.loads((ROOT/"vendor/pr121/data/mao2017_selected.json").read_text())["rows"]
    scalar_rows = {(r["initial_Z"], r["initial_q"]): r for r in rows}
    for T in temperatures:
        f, df = a.mao_factors_six(T)
        scalar = np.array([mao_factor(T, r["a0_b0_c0_a1_b1_a2_b2"]) for r in rows])
        max_f = max(max_f, relative(f, scalar[:, 0]))
        max_df = max(max_df, relative(df, scalar[:, 1], 1e-12))
        rates = a.rates(T, .37)
        rr, _dr = a.moments(T, rates)
        for j, ion in enumerate(a.recombination_indices):
            key = (int(a.Z[ion]), int(a.q[ion]))
            source = scalar_rows[key]
            require(key[1] == key[0]-source["recombined_s"]+1, "initial charge mapping")
            expected = KB*T*rates["rr_m3_s"][ion]*mao_factor(T, source["a0_b0_c0_a1_b1_a2_b2"])[0]
            max_map = max(max_map, relative(rr[ion], expected))
            require(a.mao_keys[a.mao_map[j]] == key, "13-isotope map mismatch")
    require(max(max_f, max_df, max_map) < 3e-14, "six-vector/scalar Mao adapter")
    require(a.rates.__func__ is donor.AtomicNetwork.rates, "number-rate owner changed")
    return dict(temperatures_K=list(temperatures), six_factor_max_relative=max_f,
                six_derivative_max_relative=max_df, isotope_moment_max_relative=max_map,
                six_to_13_map=a.mao_map.tolist(), recombination_channels=13,
                number_rate_method_identity=True)


def check_compton_units_and_limits():
    # Independent constants in cgs, including the retained donor sigma_T.
    sigma_cm2, c_cgs, me_g, kb_erg = 6.6524587051e-25, 2.99792458e10, 9.1093837139e-28, 1.380649e-16
    sigma_si = sigma_cm2*1e-4
    fixture = dict(ne=730., nb=900., eta=1.3, temperature=9300.,
                   w=1.5*1.3*9300., H=1.3e-16, U_gamma=7.1e-9,
                   scale_factor=.052, U_uv=2.3e-17, M_uv=8.2e-35)
    hot = compton_coefficients("actual_hot", **fixture)
    q_si = -4*sigma_si*fixture["ne"]*fixture["U_gamma"]*KB*fixture["temperature"]/(M_E*C_LIGHT)
    q_cgs = (-4*sigma_cm2*c_cgs*(fixture["ne"]*1e-6)*kb_erg*fixture["temperature"]
             *(fixture["U_gamma"]*10)/(me_g*c_cgs*c_cgs))*.1
    quv_cgs = (sigma_cm2*c_cgs*(fixture["ne"]*1e-6)/(me_g*c_cgs*c_cgs)*
               (fixture["M_uv"]*1e8-4*kb_erg*fixture["temperature"]*(fixture["U_uv"]*10)))*.1
    err = max(relative(hot["Q_C"], q_si), relative(hot["Q_C"], q_cgs),
              relative(hot["Q_UV"], quv_cgs))
    require(err < 8e-15, "Compton SI/cgs or c conversion")
    require(relative(THOMSON, sigma_si*C_LIGHT) < 8e-15, "THOMSON must be sigma*c")
    derivative_T = 2*hot["w_source"]/(3*fixture["eta"])
    direct_T = 2*(q_si+quv_cgs)/(3*fixture["nb"]*fixture["eta"]*KB*fixture["H"])
    require(relative(derivative_T, direct_T) < 8e-15, "3eta/2 heat-capacity factor")
    maxima = []
    for branch in ("off", "actual_hot", "planck_reference"):
        c = compton_coefficients(branch, **fixture)
        maxima.append(c["affine_direct_scaled"])
        zero = compton_coefficients(branch, **dict(fixture, ne=0.))
        require(all(zero[k] == 0 for k in ("Q_C", "Q_UV", "A", "B", "w_source")),
                "zero-electron limit")
    off = compton_coefficients("off", **fixture)
    require(all(off[k] == 0 for k in ("Q_C", "Q_UV", "A", "B", "w_source")), "Compton off")
    reference_T = 2.7255/fixture["scale_factor"]
    eq = compton_coefficients("planck_reference", **dict(fixture, temperature=reference_T,
         w=1.5*fixture["eta"]*reference_T, U_uv=0., M_uv=0.))
    require(eq["Q_C"] == 0 and eq["Q_UV"] == 0, "Planck equilibrium volume source")
    require(abs(eq["w_source"])/max(abs(eq["B"]), 1e-300) < 8e-15, "Planck equilibrium affine source")
    require(max(maxima) < 8e-15, "direct/affine agreement")
    return dict(si_cgs_max_relative=err, affine_volume_max_scaled=max(maxima),
                heat_capacity_relative=relative(derivative_T, direct_T),
                Q_hot_fixture_W_m3=hot["Q_C"], Q_uv_fixture_W_m3=hot["Q_UV"],
                zero_electron_exact=True, off_exact=True, planck_equilibrium=True)


def check_planck_integrals():
    # Independent frequency-spectrum integrals include stimulated recoil.
    i3, e3 = quad(lambda x: x**3/math.expm1(x), 0, 100, epsabs=2e-12, epsrel=2e-13)
    i4, e4 = quad(lambda x: x**4*math.exp(x)/math.expm1(x)**2,
                  0, 100, epsabs=8e-12, epsrel=2e-13)
    radiation_constant = 8*math.pi*KB**4*i3/(H_PLANCK**3*C_LIGHT**3)
    require(relative(i3, math.pi**4/15) < 5e-13, "Planck energy integral")
    require(relative(i4, 4*i3) < 5e-13, "Planck induced+recoil integral")
    require(relative(A_RAD, radiation_constant) < 5e-13, "radiation constant units")
    return dict(energy_integral=i3, recoil_induced_integral=i4,
                quadrature_absolute_errors=[e3, e4],
                A_RAD_J_m3_K4=A_RAD, independent_A_RAD=radiation_constant,
                relative_radiation_constant=relative(A_RAD, radiation_constant),
                effective_recoil_over_kT_U=i4/i3)


def check_continuous_uv():
    a = CoupledThermalAtomic()
    edges = a.photon_bin_edges_eV
    nodes, weights = np.polynomial.legendre.leggauss(4)
    midpoint = (edges[1:]+edges[:-1])/2
    halfwidth = (edges[1:]-edges[:-1])/2
    expected_nodes = (midpoint[:, None]+halfwidth[:, None]*nodes).ravel()
    require(np.array_equal(expected_nodes, a.photon_energy_eV), "actual GL4 nodes")
    p = a.uv_config["number_power_index"]
    density_weights = (halfwidth[:, None]*weights).ravel()*expected_nodes**p
    normalization = float(a.photon_flux_bins_base[0]/density_weights[0])
    require(relative(a.photon_flux_bins_base, normalization*density_weights) < 5e-15,
            "angle-integrated flux normalization")
    v1, e1 = quad(lambda E: E**(p+1), float(edges[0]), float(edges[-1]),
                 epsabs=1e-13, epsrel=2e-13, points=edges[1:-1], limit=200)
    v2, e2 = quad(lambda E: E**(p+2), float(edges[0]), float(edges[-1]),
                 epsabs=1e-12, epsrel=2e-13, points=edges[1:-1], limit=200)
    expected_U = normalization*EV_J*v1/C_LIGHT
    expected_M = normalization*EV_J**2*v2/C_LIGHT
    maxerr = max(relative(a.U_uv_base, expected_U), relative(a.M_uv_base, expected_M))
    require(maxerr < 3e-12, "cached UV GL4/continuous moments")
    # Scalar photon flux Phi_E = c*n_gamma,E. Low-occupation bound at E_min.
    occupation = H_PLANCK**3*C_LIGHT**2*normalization*edges[0]**(p-2)/(8*math.pi*EV_J**3)
    require(occupation < 1e-12, "low-occupation UV approximation fixture")
    return dict(nodes=len(expected_nodes), threshold_split_bins=len(edges)-1,
                U_uv_base_J_m3=a.U_uv_base, M_uv_base_J2_m3=a.M_uv_base,
                independent_U_J_m3=expected_U, independent_M_J2_m3=expected_M,
                max_relative=maxerr, occupation_upper=occupation,
                dimensionless_quadrature_errors=[e1, e2],
                spectrum_owner="THERM01 actual GL4 scalar flux; same prescribed amplitude")


def check_frozen_subflow():
    max_semigroup = max_reference = 0.
    for w, A, B, dt in ((100., 0., 0., .25), (103., 1e-12, 31., 1e-10),
                         (700., .3, 2000., .4), (0., 20., 15., .2)):
        result = frozen_subflow(w, A, B, dt)
        # Independent integrating-factor quadrature, no ODE integration.
        source_integral = quad(lambda s: math.exp(-(2+A)*s), 0, dt,
                               epsabs=1e-15, epsrel=2e-13)[0]
        expected = w*math.exp(-(2+A)*dt)+B*source_integral
        composed = frozen_subflow(frozen_subflow(w, A, B, dt*.37), A, B, dt*.63)
        max_reference = max(max_reference, relative(result, expected))
        max_semigroup = max(max_semigroup, relative(result, composed))
        require(result >= 0, "frozen-subflow positivity")
        equilibrium = B/(2+A)
        require(relative(frozen_subflow(equilibrium, A, B, dt), equilibrium) < 5e-15,
                "frozen equilibrium")
    # Independent Taylor coefficients for a tiny step test the initial slope.
    w, A, B, dt = 13., .7, 8., 2e-8
    increment = frozen_subflow(w, A, B, dt)-w
    taylor = (B-(2+A)*w)*dt-.5*(2+A)*(B-(2+A)*w)*dt**2
    taylor_error = relative(increment, taylor)
    require(max_reference < 5e-15 and max_semigroup < 5e-15 and taylor_error < 1e-8,
            "frozen integral, semigroup or slope")
    return dict(fixture_count=4, max_semigroup_relative=max_semigroup,
                max_direct_relative=max_reference, taylor_increment_relative=taylor_error,
                use="fixed x,Y,geometry algebra only; not coupled time splitting")


def check_compact_full_and_ledgers():
    max_map = max_local = max_transfer = max_atomic = max_affine = max_number = 0.
    geometry_counts = []
    diagnostics_keys = None
    for closure in ("mao2017", "rate_derivative"):
        for branch in ("off", "actual_hot", "planck_reference"):
            cfg = dict(BASE_CONFIG, rr_closure=closure, cmb_branch=branch)
            small = CoupledThermalSystem(cfg)
            full = CoupledThermalSystem(cfg, full=True)
            for index in range(3):
                x, y = physical_state(full, index)
                p = full.point(x, y)
                a = full.full_rhs_from_point(p)
                b = small.rhs(x, restrict63(y))
                # Mapping absolute scale is each full derivative plus one;
                # exact absent channels are separately required to stay zero.
                maperr = float(np.max(abs(a-lift34(b))/np.maximum(abs(a), 1.)))
                max_map = max(max_map, maperr)
                require(np.all(a[40:61][[0, 5, 6]] == 0), "n/tritium RHS exact zero")
                d = full.diagnose_from_point(p, x)
                diagnostics_keys = sorted(d)
                max_local = max(max_local, d["local_ledger_scaled"])
                max_transfer = max(max_transfer, d["local_transfer_scaled"])
                max_atomic = max(max_atomic, d["atomic_source_scaled"])
                max_affine = max(max_affine, d["affine_direct_scaled"])
                require(d["decay_max"] == 0, "decay source exact zero")
                expected_ledger = np.array([d["absorbed_W_baryon"], d["escaped_W_baryon"],
                    d["work_W_baryon"], d["compton_W_baryon"], d["uv_compton_W_baryon"]])/d["H_s"]
                require(relative(full.ledger_from_point(p), expected_ledger) < 6e-15,
                        "five signed ledger columns or units")
                old = donor.ThermalAtomic.thermal_evaluate(full.atomic, p[1], p[3], p[4], p[5])
                max_number = max(max_number, relative(p[6]["dY_dt"], old["dY_dt"], 1e-290))
                require(np.isfinite(np.array([v for k, v in d.items() if k != "signed_observables"])).all(),
                        "finite scalar diagnostics")
            # The public diagnostics path may evaluate geometry once, not twice.
            original_fields = full.geometry.fields
            count = [0]
            def counted_fields(x, state):
                count[0] += 1
                return original_fields(x, state)
            full.geometry.fields = counted_fields
            full.diagnostics(x, y)
            geometry_counts.append(count[0])
    require(max_map < 2e-12, "full/compact physical RHS mapping")
    require(max(max_local, max_transfer, max_atomic) < 5e-12, "local source/transfer conservation")
    require(max_affine < 5e-14, "affine contraction")
    require(max_number == 0., "new energy closure modified number RHS")
    require(geometry_counts == [1]*6, "duplicate geometry evaluation")
    return dict(physical_fixture_states=3, branch_closure_pairs=6,
                max_scaled_RHS_mapping=max_map, max_local_ledger_scaled=max_local,
                max_transfer_scaled=max_transfer, max_atomic_source_scaled=max_atomic,
                max_affine_direct_scaled=max_affine, max_number_rhs_relative=max_number,
                geometry_evaluations_per_diagnostics=geometry_counts,
                diagnostics_keys=diagnostics_keys, exact_absent_n_T_decay=True)


def check_current_state_feedback():
    hot = CoupledThermalSystem(dict(BASE_CONFIG, cmb_branch="actual_hot"), full=True)
    ref = CoupledThermalSystem(BASE_CONFIG, full=True)
    x, y = physical_state(hot, 1)
    altered = y.copy()
    altered[4] *= 1.1
    p0, p1 = hot.point(x, y), hot.point(x, altered)
    r0, r1 = ref.point(x, y), ref.point(x, altered)
    hot_ratio = p1[6]["compton"]["Q_C"]/p0[6]["compton"]["Q_C"]
    ref_difference = r1[6]["compton"]["Q_C"]-r0[6]["compton"]["Q_C"]
    require(relative(hot_ratio, 1.1) < 5e-15, "actual photon monopole must own hot source")
    require(ref_difference == 0., "Planck bath must not be inferred from actual monopole")
    require(p1[7]["H"] != p0[7]["H"], "actual monopole H feedback absent")
    warm = y.copy()
    warm[62] *= 1.5
    pw = hot.point(x, warm)
    require(np.any(pw[6]["dY_dt"] != p0[6]["dY_dt"]), "current T must feed number rates")
    charged = y.copy()
    charged[41] -= .1; charged[42] += .1
    charged[43] -= .1; charged[44] += .1
    pc = hot.point(x, charged)
    new_eta = pc[2]
    charged[62] = 1.5*new_eta*p0[3]
    pc = hot.point(x, charged)
    old_rhs = hot.full_rhs_from_point(p0)
    new_rhs = hot.full_rhs_from_point(pc)
    require(pc[6]["ne"] != p0[6]["ne"], "current ionic electron density absent")
    require(np.any(new_rhs[4:22] != old_rhs[4:22]), "electron feedback into photon opacity absent")
    require(np.array_equal(new_rhs[22:40], old_rhs[22:40]), "neutrino direct Thomson source introduced")
    return dict(actual_hot_monopole_Q_ratio=hot_ratio, reference_monopole_Q_difference=ref_difference,
                old_ne_m3=p0[6]["ne"], modified_ne_m3=pc[6]["ne"],
                temperature_to_rates=True, ionic_to_photon_opacity=True,
                neutrino_direct_Thomson_absent=True)


def check_thermal_partial():
    maxerr = 0.
    records = []
    for closure in ("mao2017", "rate_derivative"):
        system = CoupledThermalSystem(dict(BASE_CONFIG, rr_closure=closure), full=True)
        reference = RecombinationMoments(system.atomic)
        for index in range(3):
            x, y = physical_state(system, index)
            p = system.point(x, y)
            _y, Y, eta, T, uv, nb, n, f = p
            coeff = reference.evaluate(T)
            derivative = coeff["drr_loss_dlogT"] + coeff["ddr_loss_dlogT"]
            if closure == "mao2017":
                derivative = coeff["ddr_loss_dlogT"].copy()
                for i in system.atomic.recombination_indices:
                    key = (int(system.atomic.Z[i]), int(system.atomic.q[i]))
                    row = system.atomic.mao_parameters[system.atomic.mao_keys.index(key)]
                    factor, df = mao_factor(T, row)
                    derivative[i] += KB*T*((coeff["rr_m3_s"][i]+coeff["drr_dlogT"][i])*factor
                                           +coeff["rr_m3_s"][i]*df)
            analytical = -2-n["ne"]*float(Y @ derivative)/(KB*f["H"]*T)*2/(3*eta)-n["compton"]["A"]
            step = 2e-5*y[62]
            plus, minus = y.copy(), y.copy()
            plus[62] += step; minus[62] -= step
            numerical = (system.full_rhs_from_point(system.point(x, plus))[62]
                        -system.full_rhs_from_point(system.point(x, minus))[62])/(2*step)
            error = abs(numerical-analytical)/max(abs(analytical), 1.)
            maxerr = max(maxerr, error)
            records.append(dict(closure=closure, state=index, T_K=T, analytical=analytical,
                                finite_difference=numerical, scaled_error=error))
    require(maxerr < 2e-7, "new full thermal partial including dRR/dT and -A")
    return dict(max_scaled_partial_error=maxerr, gate=2e-7, fixtures=records)


def check_mutation_discrimination():
    f = dict(ne=420., nb=700., eta=1.1, temperature=19000., w=1.5*1.1*19000.,
             H=1.2e-16, U_gamma=8e-9, scale_factor=.07, U_uv=0., M_uv=0.)
    q = compton_coefficients("actual_hot", **f)["Q_C"]
    reference = -4*(6.6524587051e-29)*420.*8e-9*1.380649e-23*19000./(9.1093837139e-31*299792458.)
    mutants = {"extra_c": q*C_LIGHT, "missing_c": q/C_LIGHT,
               "opposite_Q_sign": -q, "Kelvin_used_as_energy_eV": q*(EV_J/KB)}
    separations = {name: abs(value-reference)/abs(reference) for name, value in mutants.items()}
    require(all(v > .1 for v in separations.values()), "Compton unit/sign mutation escaped")
    atom = CoupledThermalAtomic()
    correct = atom.mao_factors_six(13791.)[0]
    # Feeding T_K*eV/kB to scalar formula simulates supplying Kelvin as t_eV.
    wrong = np.array([mao_factor(13791.*EV_J/KB, row)[0] for row in atom.mao_parameters])
    mao_separation = float(np.max(abs(wrong-correct)/abs(correct)))
    require(mao_separation > .1, "Mao Kelvin/eV mutation escaped")
    # Deliberate frozen charge-shift is rejected by the selected-row contract.
    for z, q_initial in atom.mao_keys:
        row = next(r for r in json.loads((ROOT/"vendor/pr121/data/mao2017_selected.json").read_text())["rows"]
                   if (r["initial_Z"], r["initial_q"]) == (z, q_initial))
        require(q_initial != z-row["recombined_s"], "off-by-one charge mutation escaped")
    return dict(expected_rejection=True, compton_relative_mutation_separations=separations,
                mao_temperature_unit_max_relative_separation=mao_separation,
                charge_off_by_one_rejected=True,
                interpretation="test expectation discrimination, not mutated production runs")


def check_error_guards():
    system = CoupledThermalSystem(BASE_CONFIG)
    rejected = []
    for T in (99.9, 1000000.1):
        state = system.y0.copy()
        state[-1] *= T/BASE_CONFIG["T0_K"]
        try:
            system.point(0., state)
        except ValueError as exc:
            require("temperature outside supported" in str(exc), "unexpected thermal-domain failure")
            rejected.append(T)
        else:
            raise AssertionError("out-of-domain trial accepted")
    for bad in (dict(BASE_CONFIG, cmb_branch="combined_hot_and_reference"),
                dict(BASE_CONFIG, rr_closure="unlabelled")):
        try:
            CoupledThermalSystem(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("unlabelled source/closure accepted")
    return dict(temperature_trials_rejected_K=rejected, invalid_branch_and_closure_rejected=True)


def _identity():
    files = ("code/coupled_thermal.py", "code/checks.py", "FROZEN_CONTRACT.md", "provenance/REUSED_FILES.json")
    return {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in files}


def run_checks(output_path):
    """Run the new finite checks once and return a durable, identity-bound receipt.

    The parent runner should reuse a matching PASS receipt. This function
    deliberately has no hidden ODE dispatch and no import of old test suites.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    tag = now.strftime("%Y%m%dT%H%M%S_%fZ")
    log_path = output_path.parent/f"CHECKS_{tag}.log"
    if output_path.exists():
        (output_path.parent/f"CHECKS_previous_receipt_{tag}.log").write_bytes(output_path.read_bytes())
    began = time.perf_counter()
    receipt = dict(unit="THERM02", kind="new-adapter PRE_ODE checks", time_utc=now.isoformat(),
                   command="MPLCONFIGDIR=/tmp/therm02-mpl OPENBLAS_NUM_THREADS=1 python code/checks.py",
                   code_input_sha256=_identity(), python=platform.python_version(),
                   numpy=np.__version__, scipy=scipy.__version__,
                   cosmological_IVPs_executed=0, old_suites_executed=0, checks=[])
    checks = [check_source_identity, check_mao_vectorization, check_compton_units_and_limits,
              check_planck_integrals, check_continuous_uv, check_frozen_subflow,
              check_compact_full_and_ledgers, check_current_state_feedback,
              check_thermal_partial, check_mutation_discrimination, check_error_guards]
    with log_path.open("w") as log:
        log.write(receipt["command"]+"\n")
        log.write("No cosmological ODE; no retained source-table suite.\n")
        for function in checks:
            started = time.perf_counter()
            try:
                evidence = function()
                result = dict(name=function.__name__, status="PASS", evidence=evidence)
            except Exception as exc:
                result = dict(name=function.__name__, status="FAIL", error=repr(exc),
                              traceback=traceback.format_exc())
            result["elapsed_s"] = time.perf_counter()-started
            receipt["checks"].append(result)
            line = json.dumps(result, allow_nan=False)
            print(line, flush=True)
            log.write(line+"\n"); log.flush()
            if result["status"] == "FAIL" and function is check_source_identity:
                break
        receipt["status"] = "PASS" if (len(receipt["checks"]) == len(checks) and
            all(r["status"] == "PASS" for r in receipt["checks"])) else "FAIL"
        receipt["exit_code"] = 0 if receipt["status"] == "PASS" else 1
        receipt["elapsed_s"] = time.perf_counter()-began
        receipt["log_path"] = str(log_path.relative_to(ROOT))
        receipt["scope"] = "finite adapter checks only; trajectory acceptance and independent review pending"
        log.write(f"status={receipt['status']} exit_code={receipt['exit_code']}\n")
    output_path.write_text(json.dumps(receipt, indent=2, allow_nan=False)+"\n")
    print(json.dumps(dict(status=receipt["status"], exit_code=receipt["exit_code"],
                         receipt=str(output_path), elapsed_s=receipt["elapsed_s"])), flush=True)
    return receipt


if __name__ == "__main__":
    result = run_checks(ROOT/"evidence/PRE_ODE_CHECKS.json")
    raise SystemExit(result["exit_code"])
