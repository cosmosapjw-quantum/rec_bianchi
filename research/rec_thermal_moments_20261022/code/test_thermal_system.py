"""Independent operator/source checks of the full63 thermal continuation.

No ODE integration is performed. The checker reads the original Mao tables,
the immutable REC119 restart and the current root-authored thermal source and
system implementation. Its author implemented recombination_moments.py; that
reused dependency is not claimed as an independent authorship review here.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import unittest

import numpy as np
import scipy

UNIT = Path(__file__).resolve().parents[1]
DONOR = UNIT.parent / 'rec_rei_hheli_sandbox_20261021'
sys.path.insert(0, str(DONOR / 'code'))
from atomic_network import AtomicNetwork
from coupled import CoupledSystem, thermal_uv
from thermal_sources import ThermalSources, mao_factor, temperature_log_rhs
from thermal_system import ThermalSystem

KB = 1.380649e-23
EV = 1.602176634e-19
METRICS = {}
BASE_T = np.array([10., 20., 50., 100., 200., 500., 1000., 2000.,
                   5000., 10000., 20000., 50000., 100000., 200000.,
                   500000., 1000000., 2000000., 5000000., 10000000.])


def source_rows():
    """Parse original rows by (recombined electron count, atomic Z)."""
    pars, calc = {}, {}
    for line in (UNIT / 'data/mao2017_pars.dat').read_text().splitlines():
        values = line.split()
        pars[(int(values[0]), int(values[1]))] = (
            np.array(values[2:9], dtype=float), float(values[9]))
    for line in (UNIT / 'data/mao2017_calc.dat').read_text().splitlines():
        values = line.split()
        calc[(int(values[0]), int(values[1]))] = np.array(values[2:], dtype=float)
    return pars, calc


def formula_from_paper(t_kelvin, parameters, log=np.log, convert_eV=True):
    """Eq7 in its power form, separate from the production exp/log code."""
    t = np.asarray(t_kelvin) * (KB / EV if convert_eV else 1.)
    a0, b0, c0, a1, b1, a2, b2 = parameters
    return (a0 * t**(-b0-c0*log(t))
            * (1+a2*t**(-b2))/(1+a1*t**(-b1)))


def source_hashes():
    paths = []
    for directory in ('code', 'data', 'vendor'):
        paths += [p for p in (DONOR / directory).rglob('*') if p.is_file()
                  and p.suffix in ('.py', '.json', '.txt')]
    return {str(p.relative_to(DONOR)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def directional_difference(system, x, y, direction, h=2e-5):
    fm2 = system.rhs(x, y-2*h*direction)
    fm1 = system.rhs(x, y-h*direction)
    fp1 = system.rhs(x, y+h*direction)
    fp2 = system.rhs(x, y+2*h*direction)
    return (fm2-8*fm1+8*fp1-fp2)/(12*h)


def scaled_error(expected, actual, rhs):
    scale = np.maximum(1., np.maximum(abs(rhs), abs(expected)))
    delta = abs(actual-expected)/scale
    return float(delta.max()), int(delta.argmax())


class TestThermalSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_before = source_hashes()
        cls.atomic = AtomicNetwork()
        cls.source = ThermalSources(cls.atomic)
        cls.alternate = ThermalSources(cls.atomic, 'rate_derivative')
        cls.parent_case = (DONOR / 'results/pilot_v2/cases/s03_m03_r03')
        cls.config = json.loads((cls.parent_case/'RESULT.json').read_text())['config']
        cls.config['_case_wall_seconds'] = 240.
        cls.system = ThermalSystem(cls.config)
        cls.parent_system = CoupledSystem(cls.config)
        with np.load(cls.parent_case/'trajectory.npz') as saved:
            cls.x = float(saved['x'][84])
            cls.z = float(saved['z'][84])
            cls.parent_y = saved['raw_state'][84].copy()
            cls.Y = saved['Y'][84].copy()
        cls.temperature = thermal_uv(cls.x)[0]
        cls.y = np.r_[cls.parent_y, math.log(cls.temperature)]
        cls.pars, cls.calc = source_rows()

    def test_mao_original_tables_and_selected_mapping(self):
        maxima = []
        checked = 0
        for z in (1, 2, 3):
            for q in range(1, z+1):
                s = z-q+1
                pars, mdp = self.pars[(s, z)]
                tabulated = self.calc[(s, z)]
                temperature = q*q*BASE_T
                expected = formula_from_paper(temperature, pars)
                actual, _ = mao_factor(temperature, pars)
                np.testing.assert_allclose(actual, expected, rtol=5e-15, atol=0.)
                # Published mdp is rounded to 0.1 percentage point, and
                # the unparameterized f values to 0.001. This is source
                # reconstruction tolerance, not a fitted physics tolerance.
                tolerance = (mdp/100.+.0005)*tabulated+.0005
                usage = abs(actual-tabulated)/tolerance
                self.assertTrue(np.all(usage <= 1.))
                selected = self.source.rows[(z, q)]
                np.testing.assert_array_equal(
                    selected['a0_b0_c0_a1_b1_a2_b2'], pars)
                np.testing.assert_array_equal(selected['table_temperature_K'], temperature)
                np.testing.assert_array_equal(selected['source_unparameterized_f'], tabulated)
                self.assertEqual(selected['recombined_s'], s)
                self.assertEqual(selected['source_max_deviation_percent'], mdp)
                maxima.append({'initial_Z': z, 'initial_q': q,
                               'max_tolerance_fraction': float(usage.max()),
                               'max_relative_table_error': float(
                                   (abs(actual-tabulated)/tabulated).max())})
                checked += len(tabulated)
        METRICS['mao_source_reconstruction'] = {
            'original_table_rows': 6, 'original_table_points': checked,
            'ion_mapping': 'q_recombining=Z-s_recombined+1',
            'absolute_tolerance': '(mdp/100+0.0005)*f_table+0.0005',
            'per_row': maxima, 'result': 'PASS'}

    def test_mao_mutations_are_detected(self):
        mutations = {'log10_in_eq7': 0, 'Kelvin_instead_of_eV': 0,
                     'wrong_electron_count_mapping': 0}
        for z in (1, 2, 3):
            for q in range(1, z+1):
                pars, mdp = self.pars[(z-q+1, z)]
                table = self.calc[(z-q+1, z)]
                temperature = q*q*BASE_T
                tolerance = (mdp/100.+.0005)*table+.0005
                mutants = {
                    'log10_in_eq7': formula_from_paper(temperature, pars, log=np.log10),
                    'Kelvin_instead_of_eV': formula_from_paper(
                        temperature, pars, convert_eV=False),
                    'wrong_electron_count_mapping': formula_from_paper(
                        temperature, self.pars[(q, z)][0])}
                for name, values in mutants.items():
                    mutations[name] += int(np.count_nonzero(abs(values-table)>tolerance))
        for count in mutations.values():
            self.assertGreater(count, 0)
        METRICS['source_mutations'] = {
            'detected_point_failures': mutations, 'result': 'PASS'}

    def test_mao_factor_and_hybrid_loss_derivatives(self):
        errors = {'mao_df_dlogT': 0., 'hybrid_RR_dloss_dlogT': 0.}
        step = 2e-5
        count = 0
        for temperature in np.geomspace(120., 8e5, 13):
            center = self.source.coefficients(temperature)
            low = self.source.coefficients(temperature*math.exp(-step))
            high = self.source.coefficients(temperature*math.exp(step))
            fd = (high['rr_loss_J_m3_s']-low['rr_loss_J_m3_s'])/(2*step)
            ii = self.atomic.recombination_indices
            analytic = center['drr_loss_dlogT'][ii]
            scale = abs(analytic)+abs(center['rr_loss_J_m3_s'][ii])
            err = float(np.max(abs(fd[ii]-analytic)/scale))
            self.assertLess(err, 1e-7)
            errors['hybrid_RR_dloss_dlogT'] = max(
                errors['hybrid_RR_dloss_dlogT'], err)
            for row in self.source.rows.values():
                params = row['a0_b0_c0_a1_b1_a2_b2']
                f, df = mao_factor(temperature, params)
                fd = (formula_from_paper(temperature*math.exp(step), params)
                      - formula_from_paper(temperature*math.exp(-step), params))/(2*step)
                err = float(abs(df-fd)/(abs(f)+abs(df)))
                self.assertLess(err, 1e-7)
                errors['mao_df_dlogT'] = max(errors['mao_df_dlogT'], err)
                count += 1
        METRICS['source_temperature_derivatives'] = {
            'temperature_nodes': 13, 'independent_factor_checks': count,
            'max_scaled_errors': errors, 'threshold': 1e-7, 'result': 'PASS'}

    def test_all_63_analytic_jacobian_columns(self):
        rhs = self.system.rhs(self.x, self.y)
        jac = self.system.jac(self.x, self.y)
        self.assertEqual(jac.shape, (63, 63))
        columns = []
        for j in range(63):
            direction = np.zeros(63)
            direction[j] = max(1., abs(self.y[j]))
            expected = jac@direction
            if j == 3:
                # Inherited spectator coordinate u is exactly0 and its
                # legacy field guard only permits u>=-1e-12. Keep all probes
                # inside that domain with a fourth-order forward stencil.
                h = 2e-5
                values = [self.system.rhs(self.x,self.y+k*h*direction)
                          for k in range(5)]
                actual = (-25*values[0]+48*values[1]-36*values[2]
                          +16*values[3]-3*values[4])/(12*h)
                stencil = 'five_point_forward_boundary'
            else:
                actual = directional_difference(self.system, self.x, self.y, direction)
                stencil = 'five_point_central'
            error, index = scaled_error(expected, actual, rhs)
            columns.append({'column': j, 'error': error, 'worst_row': index,
                            'stencil': stencil})
        worst = max(columns, key=lambda row: row['error'])
        METRICS['full63_jacobian_columns'] = {
            'x': self.x, 'saved_z': self.z, 'temperature_K': self.temperature,
            'saved_index': 84, 'columns': columns, 'worst': worst,
            'threshold': 3e-6, 'five_point_step': 2e-5,
            'domain_repair': 'column3 uses forward stencil because its '
                             'stored boundary u=0 has legacy u>=-1e-12 guard',
            'scaling': 'componentwise max(1,abs(RHS_i),abs((Jv)_i))',
            'result': 'PASS' if worst['error']<3e-6 else 'FAIL'}
        self.assertLess(worst['error'], 3e-6, str(worst))

    def test_temperature_and_mixed_JVPs_for_both_closures(self):
        rng = np.random.default_rng(20261022)
        directions = [np.eye(63)[62]]
        for _ in range(3):
            vector = np.zeros(63)
            vector[40:61] = rng.uniform(-1., 1., 21)
            vector[[40, 45, 46]] = 0.
            vector[62] = rng.uniform(-1., 1.)
            vector[1:3] = rng.uniform(-.2, .2, 2)
            directions.append(vector)
        rows = []
        for closure in ('mao2017', 'rate_derivative'):
            system = ThermalSystem(self.config, closure)
            for temperature in (1000., 12000., 1e5):
                y = self.y.copy()
                y[62] = math.log(temperature)
                rhs = system.rhs(self.x, y)
                jac = system.jac(self.x, y)
                for index, vector in enumerate(directions):
                    expected = jac@vector
                    actual = directional_difference(system, self.x, y, vector)
                    error, worst = scaled_error(expected, actual, rhs)
                    rows.append({'closure': closure, 'T_K': temperature,
                                 'direction': index, 'error': error, 'worst_row': worst})
        maximum = max(row['error'] for row in rows)
        METRICS['mixed_JVPs'] = {'checks': len(rows), 'rows': rows,
            'max_error': maximum, 'threshold': 3e-6,
            'result': 'PASS' if maximum<3e-6 else 'FAIL'}
        self.assertLess(maximum, 3e-6)

    def test_source_energy_events_and_particle_caloric_identity(self):
        maximum = 0.
        check_count = 0
        rng = np.random.default_rng(739)
        for temperature in (100., 12000., 1e6):
            Y = np.zeros(21)
            for isotope, indices in self.atomic.isotope_groups.items():
                total = self.atomic.isotope_inventory[isotope]
                Y[list(indices)] = total*rng.dirichlet(np.ones(len(indices)))
            for nb, uv in ((1., 0.), (17., .3), (1000., 1.)):
                for source in (self.source, self.alternate):
                    th = source.evaluate(Y, temperature, uv, nb)
                    n = th['network']
                    rates = self.atomic.rates(temperature, uv)
                    ne = nb*float(self.atomic.q@Y)
                    # Explicit event sum independent of matrix-contraction
                    # implementation for the ion binding reservoir.
                    ion_terms = []
                    for i in self.atomic.photo_indices:
                        deltaI = (self.atomic.ionization_energy_J[i+1]
                                  - self.atomic.ionization_energy_J[i])
                        ion_terms.append(nb*Y[i]*rates['photo_s'][i]*deltaI)
                    for i in self.atomic.recombination_indices:
                        deltaI = (self.atomic.ionization_energy_J[i-1]
                                  - self.atomic.ionization_energy_J[i])
                        ion_terms.append(nb*ne*Y[i]*(rates['rr_m3_s'][i]
                                                   + rates['dr_m3_s'][i])*deltaI)
                    ion_reference = math.fsum(ion_terms)
                    qabs = n['photo_absorbed_power_W_m3']
                    kinetic = th['kinetic_net_W_m3']
                    escape = th['total_escape_W_m3']
                    throughput = abs(qabs)+abs(kinetic)+abs(escape)+abs(ion_reference)
                    error = abs(qabs-escape-kinetic-ion_reference)/max(throughput,1e-300)
                    maximum = max(maximum, error, th['energy_source_residual_scaled'])
                    self.assertLess(error, 5e-12)
                    self.assertGreaterEqual(escape, 0.)
                    H = 1.3e-17
                    rlog = temperature_log_rhs(H, temperature, nb, th['eta'],
                              th['particle_source_per_baryon_s'], kinetic)
                    # du/dt+3H(u+p), evaluated from T and particle rates.
                    eta = th['eta']
                    doteta = th['particle_source_per_baryon_s']
                    caloric = (1.5*KB*nb*(eta*temperature*H*rlog+temperature*doteta)
                               +3*H*KB*nb*temperature*eta)
                    self.assertLess(abs(caloric-kinetic)/max(
                        abs(caloric)+abs(kinetic)+throughput,1e-300), 5e-12)
                    check_count += 1
        METRICS['source_energy_and_caloric_identity'] = {
            'physical_native_state_checks': check_count,
            'maximum_source_residual': maximum, 'threshold': 5e-12,
            'n_T': 'exactly zero in all physical source checks', 'result': 'PASS'}

    def test_constant_energy_and_particle_creation_limits(self):
        H, nb, eta, temperature = 2e-17, 3., 1.4, 8000.
        self.assertEqual(temperature_log_rhs(H,temperature,nb,eta,0.,0.), -2.)
        for doteta in (-.3*H*eta, .4*H*eta):
            # Heat supplies precisely expansion work, so energy per baryon
            # is constant and the number change alone sets T proportional1/eta.
            heat = 3*H*nb*KB*temperature*eta
            result = temperature_log_rhs(H,temperature,nb,eta,doteta,heat)
            self.assertAlmostEqual(result, -doteta/(H*eta), places=14)
            # Adding the kinetic cost of newly created particles holds T fixed.
            heat += 1.5*KB*temperature*nb*doteta
            self.assertAlmostEqual(temperature_log_rhs(
                H,temperature,nb,eta,doteta,heat), 0., places=14)
        METRICS['particle_number_limits'] = {
            'adiabatic_dlogT_dloga': -2.,
            'creation_and_removal_constant_energy_checks': 2,
            'fixed_temperature_heat_checks': 2, 'result': 'PASS'}

    def test_parent_blocks_and_non_nuclear_subspace(self):
        old = self.parent_system.rhs(self.x, self.parent_y)
        new = self.system.rhs(self.x, self.y)
        np.testing.assert_allclose(new[:62], old, rtol=5e-14, atol=5e-14)
        old_j = self.parent_system.jac(self.x, self.parent_y)
        new_j = self.system.jac(self.x, self.y)
        np.testing.assert_allclose(new_j[:62,:62], old_j, rtol=5e-14, atol=5e-14)
        np.testing.assert_array_equal(self.Y[[0,5,6]], np.zeros(3))
        np.testing.assert_array_equal(new[[40,45,46]], np.zeros(3))
        METRICS['parent_block_parity'] = {
            'rhs_max_abs': float(abs(new[:62]-old).max()),
            'jac_max_abs': float(abs(new_j[:62,:62]-old_j).max()),
            'T_reconstruction': 'exp(log(T_prescribed)); roundoff allowed',
            'nuclear_flux_zero': True, 'result': 'PASS'}

    def test_alternate_closure_changes_only_energy_at_common_state(self):
        for temperature in (100., 12000., 1e6):
            primary = self.source.coefficients(temperature)
            alternative = self.alternate.coefficients(temperature)
            for name in ('rr_m3_s','dr_m3_s','drr_dlogT','ddr_dlogT',
                         'dr_loss_J_m3_s','ddr_loss_dlogT'):
                self.assertEqual(primary[name].tobytes(), alternative[name].tobytes())
            self.assertGreater(float(np.max(abs(primary['rr_loss_J_m3_s']
                                               -alternative['rr_loss_J_m3_s']))),0.)
        alternate_system = ThermalSystem(self.config, 'rate_derivative')
        f1 = self.system.rhs(self.x,self.y)
        f2 = alternate_system.rhs(self.x,self.y)
        self.assertEqual(f1[:62].tobytes(), f2[:62].tobytes())
        self.assertNotEqual(f1[62], f2[62])
        METRICS['alternative_closure'] = {
            'common_state_first62_byte_identical': True,
            'thermal_rhs_difference': float(f1[62]-f2[62]),
            'result': 'PASS'}

    def test_z_donor_source_bytes_unchanged(self):
        after = source_hashes()
        self.assertEqual(self.source_before, after)
        # Donor constructors also revalidate their original atomic and
        # baseline source manifests; the before/after map records this run.
        AtomicNetwork()
        CoupledSystem(self.config)
        METRICS['donor_source_identity'] = {
            'files': len(after), 'before_equals_after': True,
            'file_sha256': after, 'result': 'PASS'}


def main():
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestThermalSystem)
    run = unittest.TextTestRunner(verbosity=2).run(suite)
    evidence = {
        'schema': 'rec.full63.thermal.operator.tests.v1',
        'decision': 'PASS_SCOPED' if run.wasSuccessful() else 'FAIL',
        'tests_run': run.testsRun, 'ODE_integrations': 0,
        'failures': [{'test':str(t),'traceback':s} for t,s in run.failures],
        'errors': [{'test':str(t),'traceback':s} for t,s in run.errors],
        'metrics': METRICS,
        'wall_s': time.perf_counter()-started,
        'environment': {'python':sys.version.split()[0], 'numpy':np.__version__,
                        'scipy':scipy.__version__, 'platform':platform.platform()},
        'independence': 'Checker author did not author thermal_sources.py or '
                        'thermal_system.py, but authored reused recombination_moments.py.',
        'code_identity': [{'path':str(p.relative_to(UNIT)),
                          'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                          'bytes':p.stat().st_size}
                         for p in [Path(__file__), UNIT/'code/thermal_sources.py',
                                   UNIT/'code/thermal_system.py',
                                   UNIT/'code/recombination_moments.py']],
        'scope': 'Source reconstruction and operator/analytic-Jacobian checks. '
                 'No full cosmic history, missing-process adequacy or global '
                 'convergence certification.'}
    path = UNIT/'evidence/thermal_system_tests.json'
    if path.exists():
        prior = json.loads(path.read_text())
        history = prior.pop('prior_runs',[])
        evidence['prior_runs'] = history+[prior]
    path.write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    return 0 if run.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
