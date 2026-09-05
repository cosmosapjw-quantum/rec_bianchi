"""Manufactured REC-DONOR-02C contracts; no physical source admission."""
from dataclasses import replace
from fractions import Fraction as F
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan

m = importlib.import_module("full_bianchi_hyrec.resolved_deposition")
N = float(2**20)
MU = np.array([2**21, 2**22, 2**23], dtype=float)
ENERGY = 2.0**-60 * np.array([1, 2, 3])
SOURCE_ENERGY = 2.0**-60 * np.array([1.5, 2.5])
B = np.array([[.5, 0], [.5, .5], [0, .5]])
B2 = np.array([[.75, .25], [0, 0], [.25, .75]])
R = np.array([[2., -1.], [4., 3.]])
DR = np.array([[1., 2.], [-2., 1.]])


def layout(**changes):
    values = dict(source_identity="manufactured-packet-source/v1",
                  source_channel_ids=("source-low", "source-high"),
                  target_identity="manufactured-target/v1",
                  target_ids=("target-low", "target-mid", "target-high"),
                  angular_channel_ids=("north", "south"),
                  measure_identity="manufactured-dyadic-density-measure/v1",
                  frame_identity="HYDROGEN_REST_FRAME",
                  time_basis="PHYSICAL_SECONDS",
                  rate_units="photon_packet H^-1 s^-1")
    values.update(changes)
    return m.DepositionLayout(**values)


def plan(matrix=B, **changes):
    values = dict(mode_measure_m3=MU, cell_energy_J=ENERGY,
                  source_energy_J=SOURCE_ENERGY, number_fractions=matrix,
                  angular_weights=[.5, .5], directions=[[0, 0, 1], [0, 0, -1]],
                  measure_id="manufactured-dyadic-density-measure/v1",
                  map_id="explicit-manufactured-map/v1")
    values.update(changes)
    return COMSourceDepositionPlan(**values)


def case():
    p, labels = plan(), layout()
    return p, m.ResolvedDeposition(p, labels), m.PacketRates(R, labels)


def test_action_returns_execution_receipt_after_actual_plan():
    p, binding, rates = case()
    result = binding.apply(rates, n_H_m3=N)
    assert result is not None, "Successful numerical execution must return a bound receipt"
    np.testing.assert_array_equal(result.values, p.apply(R, N))
    np.testing.assert_array_equal(result.values, [[.5, -.25], [.75, .25], [.25, .1875]])
    assert result.receipt.operation_kind == "apply"
    assert result.receipt.numerical_deposition_executed is True
    assert result.receipt.physical_source_authenticated is False
    assert result.receipt.provider_admitted is False


def test_jvp_returns_density_and_fixed_map_execution_receipt():
    p, binding, rates = case()
    result = binding.jvp(rates, m.PacketRates(DR, layout()), n_H_m3=N, dn_H_m3=N/4)
    assert result is not None, "Fixed-map JVP must return a bound execution receipt"
    np.testing.assert_array_equal(result.values, p.jvp(R, DR, N, N/4))
    np.testing.assert_array_equal(result.values,
                                  [[.375, .4375], [.0625, .4375], [-.0625, .109375]])
    assert result.receipt.operation_kind == "jvp"
    assert result.receipt.derivative_scope == "FIXED_MAP_MEASURE_ENERGY_ANGULAR_GRID"


def exact(matrix, rates, density, tangent=None, dn=0):
    """Independent scalar rational sums; never call the production operator."""
    rr = np.asarray(rates)
    if rr.ndim == 1:
        rr = np.stack([rr, rr], axis=1)
    dr = None if tangent is None else np.asarray(tangent)
    if dr is not None and dr.ndim == 1:
        dr = np.stack([dr, dr], axis=1)
    q = lambda x: F(float(x))
    return [[sum(q(matrix[i, s]) * (q(density)*q(rr[s, a]) if dr is None
                  else q(density)*q(dr[s, a])+q(dn)*q(rr[s, a]))
                 for s in range(2))/q(MU[i]) for a in range(2)] for i in range(3)]


@pytest.mark.parametrize("matrix", [B, B2], ids=["B", "B2"])
@pytest.mark.parametrize("isotropic", [False, True])
def test_fraction_action_jvp_and_moment_consistency(matrix, isotropic):
    p, labels = plan(matrix), layout()
    binding = m.ResolvedDeposition(p, labels)
    rr, dr = (R[:, 0], DR[:, 0]) if isotropic else (R, DR)
    packet, tangent = m.PacketRates(rr, labels), m.PacketRates(dr, labels)
    a = binding.apply(packet, n_H_m3=N).values
    j = binding.jvp(packet, tangent, n_H_m3=N, dn_H_m3=N/4).values
    assert [[F(float(x)) for x in row] for row in a] == exact(matrix, rr, N)
    assert [[F(float(x)) for x in row] for row in j] == exact(matrix, rr, N, dr, N/4)
    np.testing.assert_array_equal(a, p.apply(rr, N))
    np.testing.assert_array_equal(j, p.jvp(rr, dr, N, N/4))
    for angle in range(2):
        ra = rr if isotropic else rr[:, angle]
        dra = dr if isotropic else dr[:, angle]
        for output, source in [(a, N*ra), (j, N*dra+N/4*ra)]:
            assert sum(F(float(MU[i]))*F(float(output[i, angle])) for i in range(3)) == sum(map(F, source))
            assert sum(F(float(ENERGY[i]))*F(float(MU[i]))*F(float(output[i, angle])) for i in range(3)) == sum(F(float(SOURCE_ENERGY[s]))*F(float(source[s])) for s in range(2))
    np.testing.assert_array_equal(p.photon_power_four_vector(a), p.source_power_four_vector(rr, N))


@pytest.mark.parametrize("field,value", [
    ("source_identity", "other-source"), ("source_channel_ids", ("source-high", "source-low")),
    ("target_identity", "other-target"), ("target_ids", ("target-mid", "target-low", "target-high")),
    ("angular_channel_ids", ("south", "north")), ("measure_identity", "other-measure")])
def test_same_length_identity_or_order_mismatch_rejected(field, value):
    _, binding, packet = case()
    wrong = m.PacketRates(R, layout(**{field: value}))
    with pytest.raises(ValueError, match="layout"):
        binding.apply(wrong, n_H_m3=N)
    with pytest.raises(ValueError, match="layout"):
        binding.jvp(packet, wrong, n_H_m3=N, dn_H_m3=N/4)


@pytest.mark.parametrize("bad", [None, "a"*64, {"deposition_matrix_sha256": "a"*64}])
def test_operator_must_be_actual_plan(bad):
    with pytest.raises((TypeError, ValueError)):
        m.ResolvedDeposition(bad, layout())


@pytest.mark.parametrize("field,value", [
    ("frame_identity", "OBSERVER_FRAME"), ("time_basis", "CONFORMAL_TIME"),
    ("rate_units", "s^-1"), ("source_channel_ids", ("x", "x")),
    ("target_ids", ()), ("angular_channel_ids", "north"),
    ("source_identity", ""), ("target_identity", " x "), ("measure_identity", "bad\n")])
def test_invalid_units_frame_time_and_layout_rejected(field, value):
    with pytest.raises((TypeError, ValueError)):
        layout(**{field: value})


@pytest.mark.parametrize("change", [
    {"source_channel_ids": ("x",)}, {"target_ids": ("x",)},
    {"angular_channel_ids": ("x",)}, {"measure_identity": "wrong-measure"}])
def test_plan_axis_lengths_and_measure_identity_checked(change):
    with pytest.raises(ValueError):
        m.ResolvedDeposition(plan(), layout(**change))


@pytest.mark.parametrize("bad", [1., np.ones((2, 1)), np.ones((1, 2)), np.ones((2, 2, 1)),
    [True, False], [[True, 1], [2, 3]], [1+0j, 2], [np.nan, 1], [np.inf, 1],
    ["1", "2"], np.array([1, 2], dtype=object)])
def test_invalid_rate_arrays_rejected(bad):
    with pytest.raises((ValueError, TypeError)):
        m.PacketRates(bad, layout())


@pytest.mark.parametrize("bad", [True, np.bool_(True), 1+0j, np.nan, np.inf, [1.], "1"])
def test_invalid_density_and_density_tangent_rejected(bad):
    _, binding, packet = case()
    with pytest.raises((ValueError, TypeError)):
        binding.apply(packet, n_H_m3=bad)
    with pytest.raises((ValueError, TypeError)):
        binding.jvp(packet, packet, n_H_m3=N, dn_H_m3=bad)


@pytest.mark.parametrize("bad", [0., -1.])
def test_nonpositive_density_rejected(bad):
    _, binding, packet = case()
    with pytest.raises(ValueError):
        binding.apply(packet, n_H_m3=bad)


@pytest.mark.parametrize("field", ["dB", "dmu", "d_energy", "d_directions", "d_angular_weights", "moving_map", "event_crossing"])
def test_moving_map_and_event_inputs_rejected(field):
    _, binding, packet = case()
    with pytest.raises(TypeError):
        binding.jvp(packet, packet, n_H_m3=N, dn_H_m3=0., **{field: 0.})


def test_calls_existing_methods_once_without_formula_replication(monkeypatch):
    calls = []
    for name in ("apply", "jvp"):
        original = getattr(COMSourceDepositionPlan, name)
        def spy(self, *args, _name=name, _original=original, **kwargs):
            calls.append(_name)
            return _original(self, *args, **kwargs)
        monkeypatch.setattr(COMSourceDepositionPlan, name, spy)
    _, binding, packet = case()
    binding.apply(packet, n_H_m3=N)
    binding.jvp(packet, packet, n_H_m3=N, dn_H_m3=-N/4)
    assert calls == ["apply", "jvp"]


@pytest.mark.parametrize("operation", ["apply", "jvp"])
@pytest.mark.parametrize("bad", [np.full((3, 2), np.inf), np.full((3, 2), np.nan), np.zeros((1, 2))])
def test_invalid_core_output_cannot_produce_success(monkeypatch, operation, bad):
    _, binding, packet = case()
    monkeypatch.setattr(COMSourceDepositionPlan, operation, lambda *args: bad)
    with pytest.raises((FloatingPointError, ValueError)):
        if operation == "apply":
            binding.apply(packet, n_H_m3=N)
        else:
            binding.jvp(packet, packet, n_H_m3=N, dn_H_m3=0.)


def test_real_overflow_propagates_without_receipt():
    _, binding, _ = case()
    huge = m.PacketRates(np.full((2, 2), 1e308), layout())
    with np.errstate(over="ignore", invalid="ignore"), pytest.raises(FloatingPointError):
        binding.apply(huge, n_H_m3=1e308)


def test_mutable_callers_cannot_change_binding_or_receipt():
    matrix, rates, dr, ids = B.copy(), R.copy(), DR.copy(), ["source-low", "source-high"]
    labels = layout(source_channel_ids=ids)
    p = plan(matrix)
    binding = m.ResolvedDeposition(p, labels)
    packet, tangent = m.PacketRates(rates, labels), m.PacketRates(dr, labels)
    before = binding.jvp(packet, tangent, n_H_m3=N, dn_H_m3=N/4)
    matrix[:] = 42; rates[:] = 42; dr[:] = 42; ids.reverse()
    after = binding.jvp(packet, tangent, n_H_m3=N, dn_H_m3=N/4)
    assert before.receipt == after.receipt
    np.testing.assert_array_equal(before.values, after.values)
    for a in [packet.values, tangent.values, binding.plan.number_fractions, before.values]:
        with pytest.raises(ValueError):
            a.setflags(write=True)
    with pytest.raises(AttributeError):
        before.receipt.provider_admitted = True


@pytest.mark.parametrize("field", ["number_fractions", "mode_measure_m3", "cell_energy_J",
                                   "source_energy_J", "angular_weights", "directions"])
def test_every_actual_plan_array_enters_identity(field):
    p, binding, _ = case()
    value = getattr(p, field).copy()
    if field == "number_fractions":
        value = B2
    elif field == "angular_weights":
        value = [.25, .75]
    elif field == "directions":
        value = value[::-1]
    elif field == "mode_measure_m3":
        value = value*2
    else:
        value[0] = np.nextafter(value[0], np.inf)
    other = m.ResolvedDeposition(replace(p, **{field: value}), layout())
    assert binding.plan_identity != other.plan_identity


@pytest.mark.parametrize("field,value", [
    ("source_channel_ids", ("source-high", "source-low")),
    ("target_ids", ("target-high", "target-mid", "target-low")),
    ("angular_channel_ids", ("south", "north")), ("source_identity", "another-source")])
def test_ordered_ids_are_bound_to_plan_and_input_identity(field, value):
    _, binding, packet = case()
    changed = layout(**{field: value})
    other = m.ResolvedDeposition(plan(), changed)
    a = binding.apply(packet, n_H_m3=N)
    b = other.apply(m.PacketRates(R, changed), n_H_m3=N)
    assert a.receipt.plan_identity != b.receipt.plan_identity
    assert a.receipt.input_identity != b.receipt.input_identity


def test_rates_density_and_tangents_change_input_and_result_identity():
    _, binding, packet = case()
    a = binding.apply(packet, n_H_m3=N)
    for rates, n in [(m.PacketRates(R*2, layout()), N), (packet, N*2)]:
        b = binding.apply(rates, n_H_m3=n)
        assert a.receipt.input_identity != b.receipt.input_identity
        assert a.receipt.result_identity != b.receipt.result_identity
        assert a.receipt.plan_identity == b.receipt.plan_identity
    j = binding.jvp(packet, m.PacketRates(DR, layout()), n_H_m3=N, dn_H_m3=N/4)
    for dr, dn in [(DR*2, N/4), (DR, N/2)]:
        changed = binding.jvp(packet, m.PacketRates(dr, layout()), n_H_m3=N, dn_H_m3=dn)
        assert j.receipt.input_identity != changed.receipt.input_identity
        assert j.receipt.result_identity != changed.receipt.result_identity


def test_same_source_different_conservative_maps_are_not_identical():
    _, binding, packet = case()
    a = binding.apply(packet, n_H_m3=N)
    b = m.ResolvedDeposition(plan(B2), layout()).apply(packet, n_H_m3=N)
    assert a.receipt.source_identity == b.receipt.source_identity
    assert a.receipt.input_identity == b.receipt.input_identity
    assert a.receipt.plan_identity != b.receipt.plan_identity
    assert a.receipt.result_identity != b.receipt.result_identity
    assert np.max(np.abs(b.values-a.values)) == .75


def test_output_redeposition_rejected_and_original_packet_repeatable():
    _, binding, packet = case()
    output = binding.apply(packet, n_H_m3=N)
    for already_converted in [output, output.values, output.values.copy()]:
        with pytest.raises((TypeError, ValueError)):
            binding.apply(already_converted, n_H_m3=N)
        with pytest.raises((TypeError, ValueError)):
            m.PacketRates(already_converted, layout())
    assert binding.apply(packet, n_H_m3=N).receipt == output.receipt
    # Equal source/target dimensions must not defeat the quantity-type guard.
    labels = layout(target_ids=("left", "right"))
    p = plan(np.eye(2), mode_measure_m3=MU[:2], cell_energy_J=SOURCE_ENERGY)
    small = m.ResolvedDeposition(p, labels)
    converted = small.apply(m.PacketRates(R, labels), n_H_m3=N)
    with pytest.raises((TypeError, ValueError)):
        m.PacketRates(converted.values, labels)


def test_receipt_binds_actual_bytes_and_explicit_units():
    _, binding, packet = case()
    result = binding.jvp(packet, m.PacketRates(DR, layout()), n_H_m3=N, dn_H_m3=N/4)
    receipt = result.receipt
    assert receipt.output_array_digest == hashlib.sha256(np.asarray(result.values, dtype="<f8").tobytes()).hexdigest()
    assert receipt.units == "s^-1"
    assert receipt.provenance_class == "DECLARED_NUMERICAL_INPUTS_NOT_AUTHENTICATED"
    data = json.loads(receipt.input_payload_json)
    assert data["rates"]["sha256"] == hashlib.sha256(R.astype("<f8").tobytes()).hexdigest()
    assert data["rate_tangent"]["sha256"] == hashlib.sha256(DR.astype("<f8").tobytes()).hexdigest()
    assert float.fromhex(data["n_H_m3"]) == N
    assert float.fromhex(data["dn_H_m3"]) == N/4
    assert data["derivative_scope"] == receipt.derivative_scope


def test_identities_deterministic_in_two_fresh_processes():
    script = ("import runpy,json; d=runpy.run_path("+repr(str(Path(__file__).resolve()))+")"
              "; p,b,r=d['case'](); a=b.apply(r,n_H_m3=d['N']);"
              " j=b.jvp(r,d['m'].PacketRates(d['DR'],d['layout']()),n_H_m3=d['N'],dn_H_m3=d['N']/4);"
              " print(json.dumps([a.receipt.input_identity,a.receipt.plan_identity,a.receipt.result_identity,"
              "j.receipt.input_identity,j.receipt.result_identity]))")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]/"src"), PYTHONDONTWRITEBYTECODE="1")
    a, b = [subprocess.check_output([sys.executable, "-c", script], env=env, text=True) for _ in range(2)]
    assert a == b
    assert len(json.loads(a)) == 5


@pytest.mark.parametrize("target", ["packet", "tangent", "plan", "output"])
def test_public_ndarray_header_mutation_cannot_change_bound_meaning(target):
    _, binding, packet = case()
    tangent = m.PacketRates(DR, layout())
    before = binding.apply(packet, n_H_m3=N)
    before_jvp = binding.jvp(packet, tangent, n_H_m3=N, dn_H_m3=N/4)
    expected = np.asarray(before.values).copy()
    external = {"packet": packet.values, "tangent": tangent.values, "plan": binding.plan.mode_measure_m3,
                "output": before.values}[target]
    external.dtype = np.int64  # read-only storage alone does not prevent this
    after = binding.apply(packet, n_H_m3=N)
    assert before.receipt == after.receipt
    assert before_jvp.receipt == binding.jvp(packet, tangent, n_H_m3=N, dn_H_m3=N/4).receipt
    np.testing.assert_array_equal(after.values, expected)
    np.testing.assert_array_equal(before.values, expected)
