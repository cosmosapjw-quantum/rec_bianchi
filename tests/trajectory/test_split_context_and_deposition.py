"""Component proofs, not a coupled COM/native or canonical HyRec replay."""
from dataclasses import dataclass, replace
import copy
import importlib.util
from pathlib import Path
import sys
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    path = ROOT / 'src/full_bianchi_hyrec/trajectory' / (name + '.py')
    assert path.is_file(), 'new component not implemented: ' + name
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


@dataclass(frozen=True)
class Snapshot:
    fsR: float = 1.0
    meR: float = 1.0
    nH_cm3: float = 250.0
    H_s_inv: float = 4.0e-14
    TM_eV_rescaled: float = 0.25
    energy_eV: object = None


@dataclass(frozen=True)
class Replacement:
    snapshot: Snapshot
    doppler_width_eV: float
    interface_abs_x: float
    matrix: object


def context_case():
    s = Snapshot(energy_eV=np.array([10., 10.2, 11.]))
    return Replacement(s, 2.3e-4, 21.25, np.eye(3))


def test_restart_context_roundtrip_and_legacy_refusal():
    m = module('split_scientific_context')
    obj = context_case()
    expected = m.scientific_context(obj, {'electron_volt': 1.602176634e-19})
    bound = m.bind_restart_context({'schema': 'rec-split-domain-restart/v1'}, expected)
    m.require_restart_context(bound, expected)
    with pytest.raises(ValueError, match='schema'):
        m.require_restart_context({'schema': 'rec-split-domain-restart/v1'}, expected)


@pytest.mark.parametrize('field', ['doppler_width_eV', 'interface_abs_x', 'fsR', 'meR',
                                   'nH_cm3', 'H_s_inv', 'TM_eV_rescaled', 'energy_eV', 'matrix'])
def test_every_scientific_change_invalidates_restart(field):
    m = module('split_scientific_context'); obj = context_case()
    before = m.scientific_context(obj, {'E21_eV': 10.198714553953742})
    record = m.bind_restart_context({'schema': 'rec-split-domain-restart/v1'}, before)
    if field == 'matrix':
        a = obj.matrix.copy(); a[0, 1] = np.nextafter(0., 1.)
        changed = replace(obj, matrix=a)
    elif field == 'energy_eV':
        a = obj.snapshot.energy_eV.copy(); a[0] = np.nextafter(a[0], np.inf)
        changed = replace(obj, snapshot=replace(obj.snapshot, energy_eV=a))
    elif field in ('doppler_width_eV', 'interface_abs_x'):
        changed = replace(obj, **{field: getattr(obj, field) * 1.000001})
    else:
        changed = replace(obj, snapshot=replace(obj.snapshot, **{field: getattr(obj.snapshot, field)*1.000001}))
    with pytest.raises(ValueError, match='scientific context'):
        m.require_restart_context(record, m.scientific_context(changed, {'E21_eV': 10.198714553953742}))


def test_context_binds_constants_and_refuses_rehashed_tampering():
    m = module('split_scientific_context'); obj = context_case()
    before = m.scientific_context(obj, {'h': 6.62607015e-34})
    after = m.scientific_context(obj, {'h': 6.62607016e-34})
    record = m.bind_restart_context({'schema': 'rec-split-domain-restart/v1'}, after)
    with pytest.raises(ValueError, match='scientific context'):
        m.require_restart_context(record, before)
    record = m.bind_restart_context({'schema': 'rec-split-domain-restart/v1'}, before)
    record['scientific_context']['conventions']['frequency'] = 'angular_frequency'
    with pytest.raises(ValueError, match='digest'):
        m.require_restart_context(record, before)


def test_array_storage_order_is_explicitly_content_not_physics():
    m = module('split_scientific_context'); obj = context_case()
    a = m.scientific_context(obj, {})
    b = m.scientific_context(replace(obj, matrix=np.asfortranarray(obj.matrix)), {})
    assert a == b
    with pytest.raises((TypeError, ValueError)):
        m.scientific_context(replace(obj, matrix=np.array([object()], dtype=object)), {})
    with pytest.raises(ValueError, match='finite'):
        m.scientific_context(replace(obj, doppler_width_eV=np.nan), {})


def fixture_plan():
    m = module('com_source_deposition')
    # A deliberately synthetic 35-state, 26-direction component fixture.
    # It is not a reconstructed native cell grid or canonical COM network.
    energy = np.linspace(1.5e-18, 1.8e-18, 35)
    measure = np.geomspace(1e10, 8e11, 35)
    dirs = []
    for axis in range(3):
        for sign in (-1., 1.):
            e = np.zeros(3); e[axis] = sign; dirs.append(e)
    for zero in range(3):
        live = [a for a in range(3) if a != zero]
        for s in (-1., 1.):
            for t in (-1., 1.):
                e = np.zeros(3); e[live] = np.array([s, t])/np.sqrt(2.); dirs.append(e)
    import itertools
    dirs.extend(np.array(s)/np.sqrt(3.) for s in itertools.product((-1., 1.), repeat=3))
    dirs = np.array(dirs)
    angular = np.array([1/21]*6 + [4/105]*12 + [9/280]*8)
    B = np.zeros((35, 8))
    for s in range(8): B[3+s, s] = .35; B[4+s, s] = .65
    event_energy = energy @ B
    plan = m.COMSourceDepositionPlan(measure, energy, event_energy, B, angular, dirs,
                                    'synthetic-component-fixture', 'explicit-map-v1')
    return m, plan


def test_number_energy_and_four_moments_use_physical_measure():
    m, p = fixture_plan()
    rates = np.arange(1., 9.)[:, None] * (1 + .2*p.directions[:, 0])[None, :] * 1e-13
    nH = 2.5e8
    action = p.apply(rates, nH)
    number = np.einsum('i,a,ia->', p.mode_measure_m3, p.angular_weights, action)
    energy = np.einsum('i,i,a,ia->', p.cell_energy_J, p.mode_measure_m3, p.angular_weights, action)
    expected_number = nH*np.einsum('a,sa->', p.angular_weights, rates)
    expected_energy = nH*np.einsum('s,a,sa->', p.source_energy_J, p.angular_weights, rates)
    assert abs(number-expected_number) <= 8e-15*abs(expected_number)
    assert abs(energy-expected_energy) <= 8e-15*abs(expected_energy)
    output = p.photon_power_four_vector(action)
    expected = p.source_power_four_vector(rates, nH)
    np.testing.assert_allclose(output, expected, rtol=8e-14, atol=1e-35)
    assert output[1] > 0 and output[0] > 0


def test_nonuniform_measure_and_signed_absorption_are_not_native_proxy_jump():
    m, p = fixture_plan(); rates = np.array([1.,-2.,3.,-4.,5.,-6.,7.,-8.])*1e-13
    action = p.apply(rates, 2.5e8)
    assert np.any(action < 0)  # source term, not a proposed positive state
    wrong_proxy_number = action.sum()
    correct_number = np.einsum('i,a,ia->',p.mode_measure_m3,p.angular_weights,action)
    assert not np.isclose(wrong_proxy_number,correct_number,rtol=1e-3,atol=1e-30)
    np.testing.assert_allclose(correct_number,2.5e8*rates.sum(),rtol=1e-14)


def test_fixed_map_jvp_includes_density_derivative():
    _, p = fixture_plan(); nH = 2.5e8; dnH = 7e7
    rates = np.linspace(1e-13,8e-13,8); dr = np.linspace(-2e-13,3e-13,8)
    analytic = p.jvp(rates, dr, nH, dnH)
    eps = 1e-4
    numerical = (p.apply(rates+eps*dr,nH+eps*dnH)-p.apply(rates-eps*dr,nH-eps*dnH))/(2*eps)
    np.testing.assert_allclose(analytic,numerical,rtol=2e-10,atol=1e-29)


@pytest.mark.parametrize('kind',['negative','number','energy','measure','angular','direction','nonfinite'])
def test_invalid_deposition_is_rejected_before_action(kind):
    m,p=fixture_plan()
    mu=p.mode_measure_m3.copy(); E=p.cell_energy_J.copy(); Es=p.source_energy_J.copy()
    B=p.number_fractions.copy(); w=p.angular_weights.copy(); e=p.directions.copy()
    if kind=='negative': B[0,0]=-1e-8
    if kind=='number': B[3,0]+=.01
    if kind=='energy': Es[0]*=1.001
    if kind=='measure': mu[0]=0
    if kind=='angular': w*=4*np.pi
    if kind=='direction': e[0]*=2
    if kind=='nonfinite': B[0,0]=np.nan
    with pytest.raises(ValueError):
        m.COMSourceDepositionPlan(mu,E,Es,B,w,e,'fixture','explicit-map-v1')


def test_bad_rate_shape_or_density_is_not_silently_broadcast():
    _,p=fixture_plan()
    for rate,density in [(1.,2.5e8),(np.ones((8,1)),2.5e8),(np.ones(8),0.),(np.ones(8),np.nan)]:
        with pytest.raises(ValueError):p.apply(rate,density)


def test_plan_copies_inputs_and_does_not_fit_or_normalize_weights():
    m,p=fixture_plan()
    assert not p.number_fractions.flags.writeable
    bad=p.number_fractions.copy();bad[3,0]+=.01
    with pytest.raises(ValueError,match='number'):
        m.COMSourceDepositionPlan(p.mode_measure_m3,p.cell_energy_J,p.source_energy_J,
                                 bad,p.angular_weights,p.directions,'fixture','bad')


def test_validated_map_cannot_be_made_writeable():
    _,p=fixture_plan()
    with pytest.raises(ValueError): p.number_fractions.setflags(write=True)


def test_direction_guard_matches_inherited_harmonic_grid():
    m,p=fixture_plan();e=p.directions.copy();e[0]*=1+2e-13
    m.COMSourceDepositionPlan(p.mode_measure_m3,p.cell_energy_J,p.source_energy_J,
                             p.number_fractions,p.angular_weights,e,'fixture','source-guard')


def test_two_moment_map_is_not_a_thermal_equilibrium_certificate():
    _,p=fixture_plan()
    thermal_energy_J=4.1e-20
    native_planck=1/np.expm1(p.source_energy_J/thermal_energy_J)
    restricted_planck=p.number_fractions.T@(1/np.expm1(p.cell_energy_J/thermal_energy_J))
    # Conservation and positivity alone cannot certify spectral/thermal parity.
    assert np.max(np.abs(restricted_planck-native_planck)/native_planck)>1e-5
