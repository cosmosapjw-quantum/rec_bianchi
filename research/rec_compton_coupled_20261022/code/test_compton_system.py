"""Bounded author preflight for the new Compton adapter; no IVPs are run.

Saved physical states and the unchanged parent are the inherited inputs.
These checks verify implementation algebra, not an independent physical
validation of the grey spectrum or of the test-fluid approximation.
"""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import unittest
from unittest.mock import patch

import numpy as np

from compton_system import (
    ComptonFull63, ThermalSystem, UNIT, THERMAL, OMITTED,
    K_COMPTON, TCMB0_K, thermal_uv,
)
from compton_budget import (
    A_RAD_J_M3_K4, KB_J_K, C_M_S, EV_J,
    hot_electron_power, planck_reference_power, dilute_spectrum_power,
)

DONOR = UNIT.parent / "rec_rei_hheli_sandbox_20261021"
SEEDS = ("s03_m03_r03", "s04_m04_r04")
BRANCHES = ("actual_hot", "planck_reference")
FD_STEP = 6e-6
FD_LIMIT = 3e-6
MEASUREMENTS = {}
INPUTS = {}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    paths = [UNIT / "code/compton_system.py", UNIT / "code/test_compton_system.py",
             UNIT / "FROZEN_CONTRACT.md", OMITTED / "code/compton_budget.py",
             THERMAL / "code/thermal_system.py", THERMAL / "code/thermal_sources.py",
             THERMAL / "code/recombination_moments.py", DONOR / "code/coupled.py",
             DONOR / "code/geometry.py", DONOR / "code/atomic_network.py"]
    paths += list((THERMAL / "data").glob("mao2017*"))
    return {str(p.relative_to(UNIT.parent)): digest(p) for p in sorted(paths)}


def fd_column(fun, y, column, step=FD_STEP):
    """Fourth-order stencil; preserve the inherited u>=0 boundary in column3."""
    h = step * max(1.0, abs(float(y[column])))
    def at(k):
        v = y.copy()
        v[column] += k * h
        return np.asarray(fun(v))
    if column == 3 and y[column] - 2*h < -1e-12:
        return (-25*at(0)+48*at(1)-36*at(2)+16*at(3)-3*at(4))/(12*h)
    return (at(-2)-8*at(-1)+8*at(1)-at(2))/(12*h)


def fd_direction(fun, y, direction, step=FD_STEP):
    return (fun(y-2*step*direction)-8*fun(y-step*direction)+
            8*fun(y+step*direction)-fun(y+2*step*direction))/(12*step)


class ComptonSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs, cls.saved, cls.parents, cls.systems = {}, {}, {}, {}
        for seed in SEEDS:
            config_file = DONOR / "results/pilot_v2/cases" / seed / "RESULT.json"
            cfg = json.loads(config_file.read_text())["config"]
            cfg = dict(cfg, _case_wall_seconds=180.)
            result_dir = THERMAL / "results/thermal8" / (seed+"_mao2017_nominal")
            receipt = json.loads((result_dir / "RESULT.json").read_text())
            data_file = result_dir / "trajectory.npz"
            actual_hash = digest(data_file)
            if actual_hash != receipt["trajectory_sha256"]:
                raise AssertionError("saved trajectory hash mismatch: " + seed)
            with np.load(data_file, allow_pickle=False) as data:
                cls.saved[seed] = (data["x"].copy(), data["raw_state"].copy())
            cls.configs[seed] = cfg
            cls.parents[seed] = ThermalSystem(cfg, "mao2017")
            for branch in BRANCHES:
                cls.systems[seed, branch] = ComptonFull63(cfg, branch)
            INPUTS[seed] = dict(
                config_sha256=digest(config_file), trajectory_sha256=actual_hash,
                receipt_sha256=digest(result_dir / "RESULT.json"),
                physical_state_indices=[0, 54, 108], native_size=63,
            )

    def states(self):
        for seed in SEEDS:
            x, y = self.saved[seed]
            for index in (0, 54, 108):
                yield seed, index, float(x[index]), y[index].copy()

    def test_01_inherited_blocks_scales_and_exclusive_labels(self):
        self.assertEqual(digest(THERMAL/"code/thermal_system.py"),
                         "1ac1336a3e979ec485cec0e4092ca7d6e1ef04aa43b28f525a06231c49e34375")
        count = 0
        for seed, index, x, y in self.states():
            old = self.parents[seed]
            old_rhs, old_jac = old.rhs(x, y), old.jac(x, y)
            for branch in BRANCHES:
                s = self.systems[seed, branch]
                self.assertEqual(s.size, 63)
                self.assertIs(s.yscale, s.scale)
                np.testing.assert_array_equal(s.scale, old.scale)
                np.testing.assert_array_equal(s.rhs(x, y)[:62], old_rhs[:62])
                np.testing.assert_array_equal(s.jac(x, y)[:62], old_jac[:62])
                added = s.jac(x, y) - old_jac
                self.assertEqual(np.count_nonzero(added[:62]), 0)
                self.assertEqual(s.compton_jacobian_row(x, y)[61], 0.)
                count += 1
        for label in ("both", "Planck", "", None):
            with self.assertRaises(ValueError):
                ComptonFull63(self.configs[SEEDS[0]], label)
        MEASUREMENTS["inherited_blocks"] = dict(
            states_and_branches=count, first_62_rhs_rows_exact=True,
            first_62_jacobian_rows_exact=True, update_rank_at_most_one=True,
            no_new_number_or_photon_energy_source=True,
        )

    def test_02_independent_source_owners_and_live_monopole(self):
        max_relative, count = 0., 0
        for seed, index, x, y in self.states():
            for branch in BRANCHES:
                s = self.systems[seed, branch]
                d = s.sample(x, y)
                q_hot = hot_electron_power(d["ne_m3"], d["T_K"], d["U_gamma_actual_J_m3"])
                q_ref = planck_reference_power(d["ne_m3"], d["T_K"], d["T_planck_reference_K"])
                q_uv = dilute_spectrum_power(d["ne_m3"], d["T_K"], d["U_uv_J_m3"], d["M_uv_J2_m3"])
                for name, expected in (("compton_actual_hot_W_m3", q_hot),
                                       ("compton_planck_reference_W_m3", q_ref),
                                       ("compton_uv_W_m3", q_uv)):
                    error = abs(d[name]-expected)/max(abs(expected), 1e-300)
                    max_relative = max(max_relative, error)
                    self.assertLess(error, 2e-14)
                self.assertEqual(d["compton_selected_W_m3"], d["compton_actual_hot_W_m3"] if branch == "actual_hot" else d["compton_planck_reference_W_m3"])
                numerator = 2*(d["compton_selected_W_m3"]+d["compton_uv_W_m3"])
                expected_g = numerator / (3*KB_J_K*d["T_K"]*d["nb_m3"]*d["H_s"]*d["gas_particles_per_baryon"])
                self.assertLess(abs(d["compton_logT_rhs"]-expected_g)/max(1., abs(expected_g)), 2e-14)
                gap = (-4*K_COMPTON*d["ne_m3"]*KB_J_K*d["T_K"] *
                       (d["U_planck_reference_J_m3"]-d["U_gamma_actual_J_m3"]) +
                       4*K_COMPTON*d["ne_m3"]*KB_J_K*d["U_planck_reference_J_m3"]*d["T_planck_reference_K"])
                self.assertLess(abs((q_ref-q_hot)-gap)/max(abs(q_ref), abs(q_hot)), 3e-14)
                changed = y.copy(); changed[4] *= 1.1
                after = s.compton_terms(x, changed)
                self.assertAlmostEqual(after["U_gamma_actual_J_m3"] / d["U_gamma_actual_J_m3"], 1.1, places=14)
                self.assertAlmostEqual(after["compton_actual_hot_W_m3"] / q_hot, 1.1, places=14)
                self.assertEqual(after["compton_planck_reference_W_m3"], d["compton_planck_reference_W_m3"])
                count += 1
        MEASUREMENTS["source_owners"] = dict(
            physical_state_branch_checks=count, max_relative_power_error=max_relative,
            actual_photon_energy_raw_index=4,
            reference_T0_K=TCMB0_K,
            reference_owner="independent bath specified by FROZEN_CONTRACT section 2",
            reference_does_not_replace_actual_radiation=True,
        )

    def test_03_added_row_all_63_columns(self):
        rows = []
        for seed, index, x, y in self.states():
            for branch in BRANCHES:
                s = self.systems[seed, branch]
                analytic = s.compton_jacobian_row(x, y)
                numeric = np.array([fd_column(lambda v: s.compton_logT_rhs(x, v), y, j)
                                    for j in range(63)])
                scaled = np.abs(analytic-numeric)/np.maximum(1., np.maximum(abs(analytic), abs(numeric)))
                row = dict(seed=seed, index=index, branch=branch,
                           max_scaled_error=float(scaled.max()), worst_column=int(np.argmax(scaled)),
                           all_columns=63)
                rows.append(row)
                MEASUREMENTS["added_row_all_columns"] = rows
                self.assertLess(row["max_scaled_error"], FD_LIMIT)
        MEASUREMENTS["added_row_fd_definition"] = dict(
            step=FD_STEP, criterion=FD_LIMIT, total_columns=len(rows)*63,
            normalization="max(1, abs(analytic entry), abs(numeric entry))",
            stencil="fourth-order central; column 3 fourth-order forward at inherited u=0 boundary",
        )

    def test_04_full63_directional_products_and_temperature_columns(self):
        rows = []
        for seed in SEEDS:
            xgrid, ygrid = self.saved[seed]
            x, base = float(xgrid[54]), ygrid[54].copy()
            directions = []
            # Geometry, live photon energy, electrons/eta and temperature mix.
            v = np.zeros(63); v[[1,2,4,22,41,42,48,49,62]] = [.2,.1,.3,-.1,.2,-.2,.1,-.1,.7]
            directions.append(v)
            v = np.zeros(63); v[40:61] = np.linspace(-.2,.2,21); v[62] = -.4
            directions.append(v)
            v = np.zeros(63); v[4:40] = np.linspace(-.15,.15,36); v[62] = .3
            directions.append(v)
            for branch in BRANCHES:
                s = self.systems[seed, branch]
                for T in (1000., 12000., 100000.):
                    y = base.copy(); y[62] = math.log(T)
                    analytic = s.jac(x, y)
                    for number, v in enumerate(directions):
                        numeric = fd_direction(lambda u: s.rhs(x, u), y, v)
                        prediction = analytic @ v
                        scale = max(1., float(np.max(abs(numeric))), float(np.max(abs(prediction))))
                        error = float(np.max(abs(numeric-prediction)) / scale)
                        rows.append(dict(seed=seed, branch=branch, T_K=T, direction=number,
                                         max_scaled_error=error))
                        MEASUREMENTS["full63_directional_products"] = rows
                        self.assertLess(error, FD_LIMIT)
                    numeric_T = fd_column(lambda u: s.rhs(x, u), y, 62)
                    scale = np.maximum(1., np.maximum(abs(numeric_T), abs(analytic[:,62])))
                    self.assertLess(float(np.max(abs(numeric_T-analytic[:,62])/scale)), FD_LIMIT)
        MEASUREMENTS["full63_directional_definition"] = dict(
            products=len(rows), separate_temperature_columns=12,
            temperatures_K=[1000.,12000.,100000.], criterion=FD_LIMIT,
            normalization="max(1, infinity norm of each complete directional product)",
        )

    def test_05_compact_hubble_derivative_matches_owner(self):
        errors = []
        for seed, index, x, y in self.states():
            s = self.systems[seed, "planck_reference"]
            field, network, *_ = s.point(x, y)
            _, owner = s.geometry.jacobian_blocks(x, y[:40], field, network["ne"])
            compact = -s.compton_jacobian_row(x, y)[:40] / s.compton_logT_rhs(x, y)
            error = float(np.max(abs(compact-owner)))
            errors.append(error)
            self.assertLess(error, 3e-15)
            self.assertEqual(set(np.flatnonzero(owner)), {1,2,4,22})
        MEASUREMENTS["compact_hubble_gradient"] = dict(
            physical_states=len(errors), owner="unchanged Geometry.jacobian_blocks",
            nonzero_columns=[1,2,4,22], max_absolute_error=max(errors),
        )

    def test_06_equilibrium_hot_partial_and_flrw_limit(self):
        seed = SEEDS[0]
        x, raw = self.saved[seed]
        hot, ref = self.systems[seed,"actual_hot"], self.systems[seed,"planck_reference"]
        g_hot = []
        for T in (1000.,12000.,100000.):
            y = raw[54].copy(); y[62] = math.log(T)
            g_hot.append(hot.compton_terms(float(x[54]), y)["compton_cmb_logT_rhs"])
        self.assertEqual(len(set(g_hot)), 1)
        y = raw[0].copy()
        xeq = float(x[0])
        target = TCMB0_K/(ref.geometry.source.aref*math.exp(xeq))
        y[62] = math.log(target)
        # CMB source-only equilibrium is below the atomic 100 K domain in
        # this late-time interval. No atomic coefficient is evaluated here.
        eq = ref.compton_terms(xeq, y)
        ne = ref.geometry.baryon_number_density(xeq)*float(ref.atomic.q@(y[40:61]*ref.scale))
        scale = 4*K_COMPTON*ne*KB_J_K*target*eq["U_planck_reference_J_m3"]
        equilibrium_residual = abs(eq["compton_selected_W_m3"])/scale
        self.assertLess(equilibrium_residual, 3e-15)
        with self.assertRaises(ValueError):
            ref.rhs(xeq,y)
        cfg = dict(self.configs[seed], Sigma_F=0., matter_A=0., radiation_A=0.)
        flrw = ComptonFull63(cfg, "actual_hot")
        y = raw[54].copy(); y[:40] = flrw.y0[:40]
        y[1:4] = 0.
        for start in (4,13,22,31):
            y[start:start+9] = 0.; y[start] = 1.
        xf = float(x[54]); f = flrw.geometry.fields(xf, y[:40])
        d = flrw.compton_terms(xf, y)
        expected_U = flrw.geometry.source.rhocrit_j_m3*flrw.geometry.model.omega_gamma/f["a"]**4
        self.assertEqual(d["U_gamma_actual_J_m3"], expected_U)
        self.assertLess(float(np.max(abs(flrw.geometry.normalized(xf, y[:40], f)))), 2e-14)
        old = ThermalSystem(cfg,"mao2017")
        np.testing.assert_array_equal(flrw.rhs(xf,y)[:40], old.rhs(xf,y)[:40])
        self.assertEqual(flrw.rhs(xf,y)[4], 0.)
        MEASUREMENTS["analytic_limits"] = dict(
            hot_cmb_logT_partial_exact_zero=True, hot_logT_rhs_values=g_hot,
            Planck_equilibrium_relative_residual=equilibrium_residual,
            Planck_equilibrium_scope="CMB source only at valid x; Tref below atomic domain, full63 correctly rejects it",
            FLRW_all_higher_multipoles_zero=True,
            FLRW_actual_energy_a_minus_4=True,
            FLRW_no_Compton_source_in_photon_energy=True,
            spectral_reconstruction_claim=False,
        )

    def test_07_neutral_zero_monopole_and_signed_trials(self):
        seed = SEEDS[0]; xgrid, raw = self.saved[seed]
        x = float(xgrid[54]); physical = raw[54].copy()
        errors = []
        for branch in BRANCHES:
            s = self.systems[seed, branch]
            neutral = physical.copy()
            # Preserve each isotope inventory while moving it into neutral
            # states, instead of deleting the almost fully ionized inventory.
            for group in s.atomic.isotope_groups.values():
                indices=np.array(group,dtype=int)
                inventory=float(np.sum(physical[40+indices]*s.scale[indices]))
                neutral[40+indices]=0.
                neutral[40+indices[0]]=inventory/s.scale[indices[0]]
            self.assertEqual(s.compton_logT_rhs(x, neutral), 0.)
            self.assertTrue(np.all(np.isfinite(s.compton_jacobian_row(x, neutral))))
            for j in (41,42,48,49,62):
                a = s.compton_jacobian_row(x,neutral)[j]
                n = float(fd_column(lambda v: s.compton_logT_rhs(x,v), neutral,j))
                error=abs(a-n)/max(1.,abs(a),abs(n)); errors.append(error)
                self.assertLess(error, FD_LIMIT)
            zero_E = physical.copy(); zero_E[4] = 0.
            with self.assertRaises(ValueError):
                s.geometry.fields(x,zero_E[:40])
            # This test double supplies the smooth positive-H Einstein formula
            # at E0=0 solely to test the algebraic source extension. It does not
            # alter the inherited full63 radiation-domain admission rule.
            physical_field=s.geometry.fields(x,physical[:40])
            photon_h2=s.geometry.source.h0**2*s.geometry.model.omega_gamma/physical_field["a"]**4
            def extended_fields(_x,v):
                field=dict(physical_field)
                field["H"]=math.sqrt(physical_field["H"]**2+photon_h2*(v[4]-physical[4]))
                return field
            with patch.object(s.geometry,"fields",side_effect=extended_fields):
                self.assertTrue(math.isfinite(s.compton_logT_rhs(x, zero_E)))
                self.assertTrue(np.all(np.isfinite(s.compton_jacobian_row(x, zero_E))))
                a = s.compton_jacobian_row(x,zero_E)[4]
                n = float(fd_column(lambda v: s.compton_logT_rhs(x,v), zero_E,4))
                error=abs(a-n)/max(1.,abs(a),abs(n)); errors.append(error)
                self.assertLess(error, FD_LIMIT)
            for sign in (-1.,1.):
                trial = physical.copy(); trial[[40,45,46]] = sign*1e-5
                self.assertTrue(np.all(np.isfinite(s.rhs(x,trial))))
                self.assertTrue(np.all(np.isfinite(s.jac(x,trial))))
        MEASUREMENTS["smooth_trial_extension"] = dict(
            zero_electrons_and_zero_photon_monopole=True,
            zero_photon_scope="algebraic source with analytic field test double only; full63 preserves inherited E0>0 guard",
            signed_native_neutron_tritium_trials=4,
            finite_difference_checks=len(errors),max_scaled_error=max(errors),
            physical_nuclear_energy_claim=False,
        )

    def test_08_combined_energy_binding_and_particle_ledger(self):
        residuals, counts = [], 0
        for seed,index,x,y in self.states():
            np.testing.assert_array_equal(y[[40,45,46]], np.zeros(3))
            old = self.parents[seed]
            prior = old.thermal_diagnostics(x,y)
            field, network, T, uv, _, nb = old.point(x,y)
            Y=y[40:61]*old.scale
            eta_dot=float((1+old.atomic.q)@network["dY_dt"])
            for branch in BRANCHES:
                s=self.systems[seed,branch]; d=s.sample(x,y); inherited=s.diagnostics(x,y)
                self.assertEqual(d["gas_energy_J_per_baryon"],prior["gas_energy_J_per_baryon"])
                self.assertEqual(d["ion_source_W_m3"],prior["ion_source_W_m3"])
                self.assertEqual(d["kinetic_net_without_compton_W_m3"],prior["kinetic_net_W_m3"])
                Qgas=d["kinetic_net_W_m3"]+d["ion_source_W_m3"]
                ledger=math.fsum((Qgas,d["compton_bath_source_W_m3"],d["uv_bath_source_W_m3"],d["escaped_radiation_source_W_m3"]))
                scale=sum(abs(v) for v in (Qgas,d["compton_bath_source_W_m3"],d["uv_bath_source_W_m3"],d["escaped_radiation_source_W_m3"]))
                residuals.append(abs(ledger)/scale)
                self.assertLess(residuals[-1],5e-12)
                self.assertEqual(d["source_energy_residual"],d["transfer_ledger_residual_scaled"])
                expected_source=(d["photo_absorbed_W_m3"]-d["total_escape_W_m3"]+d["compton_selected_W_m3"]+d["compton_uv_W_m3"])/(nb*field["H"])
                self.assertLess(abs(d["gas_energy_source_J_per_baryon_per_x"]-expected_source)/max(abs(expected_source),1e-300),3e-14)
                # First law with changing gas particle number and binding store.
                gas_x=1.5*KB_J_K*T*(d["gas_particles_per_baryon"]*s.rhs(x,y)[62]+eta_dot/field["H"])+float(old.atomic.ionization_energy_J@network["dY_dt"])/field["H"]
                expected_x=d["gas_energy_source_J_per_baryon_per_x"]-d["work_J_per_baryon_per_x"]
                self.assertLess(abs(gas_x-expected_x)/max(abs(gas_x),abs(expected_x),1e-300),5e-12)
                self.assertEqual(inherited["net_required_gas_input_W_m3"],Qgas)
                self.assertEqual(inherited["external_bath_W_m3"],d["compton_total_W_m3"])
                self.assertEqual(inherited["bath_minus_escape_W_m3"],d["compton_total_W_m3"]-d["total_escape_W_m3"])
                self.assertEqual(s.point(x,y)[1]["electron_source_m3_s"],network["electron_source_m3_s"])
                counts+=1
        MEASUREMENTS["combined_energy_ledger"] = dict(
            checked_physical_states=counts, max_scaled_residual=max(residuals),criterion=5e-12,
            binding_store_unchanged=True,particle_source_unchanged=True,
            native_n_and_T_exact_zero_at_checked_states=True,
            gas_first_law_with_particle_number=True,
            inherited_diagnostics_agree=True,
        )

    def test_09_UV_precomputation_and_frozen_source_temperature_oracle(self):
        seed=SEEDS[0]; xgrid,raw=self.saved[seed]; x=float(xgrid[54]); y=raw[54].copy()
        rows=[]
        for branch in BRANCHES:
            s=self.systems[seed,branch]
            eps=s.atomic.photon_energy_eV*EV_J; flux=s.atomic.photon_flux_bins_base
            self.assertEqual(s.uv_moments["bin_count"],71)
            self.assertEqual(s._uv_U,float(flux@eps)/C_M_S)
            self.assertEqual(s._uv_M,float(flux@(eps*eps))/C_M_S)
            with patch("compton_system.uv_reference_moments",side_effect=AssertionError("per-call UV quadrature")):
                s.rhs(x,y);s.jac(x,y);s.sample(x,y)
            # Independent temperature-space affine oracle: frozen composition,
            # geometry and baths only; this is algebra, not an evolved IVP.
            d=s.sample(x,y);xe=d["ne_m3"]/d["nb_m3"];eta=d["gas_particles_per_baryon"]
            Usel=d["U_gamma_actual_J_m3"] if branch=="actual_hot" else d["U_planck_reference_J_m3"]
            A=(8*K_COMPTON/3)*(xe/eta)*(Usel+d["U_uv_J_m3"])
            intercept=(8*K_COMPTON/3)*(xe/eta)*(d["M_uv_J2_m3"]/(4*KB_J_K)+(d["U_planck_reference_J_m3"]*d["T_planck_reference_K"] if branch=="planck_reference" else 0.))
            rate=d["H_s"]*d["T_K"]*d["compton_logT_rhs"]
            relative=abs(rate-(-A*d["T_K"]+intercept))/max(abs(rate),1e-300)
            self.assertLess(relative,3e-14)
            # Stable exact frozen-coefficient map composes for positive times.
            star=intercept/A;dt=.3/A
            full=d["T_K"]+(star-d["T_K"])*(-math.expm1(-A*dt))
            half=d["T_K"]+(star-d["T_K"])*(-math.expm1(-A*dt/2))
            twice=half+(star-half)*(-math.expm1(-A*dt/2))
            self.assertLess(abs(full-twice)/abs(full),3e-15)
            rows.append(dict(branch=branch,affine_rate_relative_error=relative,A_s=A,intercept_K_s=intercept))
        MEASUREMENTS["UV_and_frozen_source_oracle"]=dict(
            bin_count=71,initialization_only_moments=True,oracle_checks=rows,
            new_ODE_runs=0,scope="local frozen-source algebra, not full chemistry/expansion solution",
        )


def main():
    start=time.perf_counter(); started=datetime.now(timezone.utc).isoformat()
    before=source_hashes()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ComptonSystemTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    after=source_hashes()
    evidence=dict(
        schema="rec.compton.full63.author_preflight.v1",
        status="PASS" if result.wasSuccessful() and before==after else "FAIL",
        author="moment_implementation; authored adapter and tests; not independent review",
        started_utc=started,wall_seconds=time.perf_counter()-start,
        command="python3 code/test_compton_system.py",
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        failure_details=[dict(test=str(t),traceback=trace) for t,trace in result.failures+result.errors],
        environment=dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform()),
        thresholds=dict(analytic_Jacobian_scaled=FD_LIMIT,source_energy_scaled=5e-12),
        inputs=INPUTS,measurements=MEASUREMENTS,
        source_hashes_before=before,source_hashes_after=after,source_unchanged=before==after,
        execution=dict(new_ODE_runs=0,old_suite_reruns=0),
        scope="bounded numerical/algebra self-checks; Physical HOLD; no spectrum or backreaction validation",
    )
    directory=UNIT/"evidence/runtime_preflight";directory.mkdir(parents=True,exist_ok=True)
    attempt=1
    while (directory/f"attempt_{attempt:02d}_evidence.json").exists():
        attempt+=1
    evidence["attempt"]=attempt
    text=json.dumps(evidence,indent=2,allow_nan=False)+"\n"
    (directory/f"attempt_{attempt:02d}_evidence.json").write_text(text)
    (UNIT/"evidence/COMPTON_SYSTEM_TESTS.json").write_text(text)
    return 0 if evidence["status"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
