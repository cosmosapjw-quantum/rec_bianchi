from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from full_bianchi_hyrec.trajectory.primordial_rei_interface import (
    build_boundary_packet,
    joule_per_m3_to_erg_per_cm3,
    source_number_fractions,
    write_packet_create_only,
    _safe_child,
    _interpolate_four_point_ln_a,
    _validate_native_grid_row,
    _source_state,
    R3G_COSMOLOGY,
    HYREC_H100_S_INV,
    HYREC_RADIATION_H2_PER_K4,
    HYREC_NU_DENSITY_FACTOR,
    HYREC_NH0_PER_OMBH2,
    source_number_fractions,
    _richardson_reasons,
    _parity_reasons,
    _require_density_match,
    _canonical_sha,
    REQUIRED_PARITY_METRICS,
    NATIVE_LNA_STEP,
)

ROOT = Path(__file__).resolve().parents[2]
PARTIAL = ROOT / "research/rec_r3g_primordial_20261016/rei_interface_001/INPUT_HISTORY_STATUS.json"
TARGET_SHA = "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"


def test_actual_partial_r3g_evidence_holds_without_fabricating_z20(tmp_path):
    packet = build_boundary_packet(PARTIAL, target_scenario_sha256=TARGET_SHA)
    assert packet["schema"] == "rec.primordial.rei_boundary.v1"
    assert packet["scope"] == "ORIGINAL_HYREC_2012_STAGE_SEQUENCE_FLRW_Q0"
    assert packet["decision"] == "HOLD_MISSING_VALIDATED_HISTORY"
    assert packet["source_boundary"] is None
    assert packet["recipient_comparison"] is None
    assert packet["activation"] == "DISABLED_REQUIRES_SEPARATE_REI_APPROVAL"
    assert packet["adopted_into_REI"] is False
    assert any("exact z=20 native row is not required" in x for x in packet["hold_reasons"])
    assert packet["source_evidence_status"] == "PARTIAL"
    assert packet["clock_convention"]["reference_z"] == 20.
    output = tmp_path / "boundary.json"
    digest = write_packet_create_only(packet, output)
    raw = output.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    with pytest.raises(FileExistsError):
        write_packet_create_only(packet, output)
    assert output.read_bytes() == raw


def test_superficial_pass_labels_cannot_promote_synthetic_history(tmp_path):
    # Labels and two plausible rows cannot substitute for independently
    # verified full coverage, source parity, convergence, review and REI bytes.
    manifest = json.loads(PARTIAL.read_text())
    manifest["status"] = "PASS"
    manifest["scope"] = "ORIGINAL_HYREC_2012_STAGE_SEQUENCE_FLRW_Q0"
    manifest["independently_integrated"] = True
    mp = tmp_path / "superficial_pass.json"
    mp.write_text(json.dumps(manifest))
    packet = build_boundary_packet(mp, target_scenario_sha256=TARGET_SHA)
    assert packet["decision"] == "HOLD_MISSING_VALIDATED_HISTORY"
    assert packet["source_boundary"] is None
    assert packet["recipient_comparison"] is None
    assert any("missing admission evidence" in reason for reason in packet["hold_reasons"])


def test_boolean_invalid_fraction_and_si_conversion_guards():
    with pytest.raises(ValueError, match="boolean"):
        source_number_fractions(True)
    with pytest.raises(ValueError, match="strictly between"):
        source_number_fractions(2.0)
    assert joule_per_m3_to_erg_per_cm3(1.0) == 10.0
    with pytest.raises(ValueError, match="boolean"):
        joule_per_m3_to_erg_per_cm3(False)


def test_path_escape_and_invalid_identity_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="safe manifest-relative"):
        _safe_child(tmp_path, "../outside", "history")
    with pytest.raises(ValueError, match="safe manifest-relative"):
        _safe_child(tmp_path, "/tmp/absolute.json", "history")
    with pytest.raises(ValueError, match="frozen donor comparison baseline"):
        build_boundary_packet(PARTIAL, target_scenario_sha256="0"*64)


def test_updated_schema_validates_actual_refusal_packet():
    import jsonschema
    packet = build_boundary_packet(PARTIAL, target_scenario_sha256=TARGET_SHA)
    schema = json.loads((ROOT / "schemas/rec_primordial_rei_boundary_v1.schema.json").read_text())
    jsonschema.Draft202012Validator(schema).validate(packet)


def test_synthetic_four_point_interpolation_exports_charge_closed_species_only_as_fixture():
    import math
    zref = 20.0
    target = -math.log1p(zref)
    fhe = source_number_fractions(.2454)["fHe_helium_nuclei_per_hydrogen_nucleus"]
    rad = HYREC_RADIATION_H2_PER_K4*R3G_COSMOLOGY["T0_K"]**4*(1+HYREC_NU_DENSITY_FACTOR*R3G_COSMOLOGY["N_eff_massless"])
    h_expected = HYREC_H100_S_INV*math.sqrt(R3G_COSMOLOGY["omega_m_h2"]*21**3+rad*21**4+R3G_COSMOLOGY["omega_lambda_h2"])
    nh_expected = HYREC_NH0_PER_OMBH2*R3G_COSMOLOGY["omega_b_h2"]*(1-.2454)*21**3
    rows = []
    # Cubic xe and states make this an actual interpolation test. Synthetic
    # values are unit-test fixtures and cannot satisfy production admission.
    for i, offset in enumerate((-2., -1., 1., 2.)):
        x = target + offset*1e-3
        t = x-target
        xh = .0002 + 1e-5*t
        xhe2 = .001 + 1e-5*t
        xhe3 = .0001 + 2e-6*t
        xe = xh + fhe*(xhe2+2*xhe3)
        rows.append({"index":i,"ln_a":x,"stage":"SYNTHETIC_TEST_ONLY",
            "xHII_per_H":xh,"xHeII_per_He":xhe2,"xHeIII_per_He":xhe3,"xe_per_H":xe,
            "Tm_K":10.+t,"H_s_inv":h_expected,"nH_m3":nh_expected})
    row = _interpolate_four_point_ln_a(rows,zref)
    assert row["interpolation"]["method"] == "four_point_lagrange_ln_a"
    state = _source_state(row, source_number_fractions(.2454), R3G_COSMOLOGY)
    species = state["species_per_source_normalization"]
    assert abs(species["xe_per_H"] - (species["xHII_per_H"] + fhe*(species["xHeII_per_He"]+2*species["xHeIII_per_He"]))) <= 1e-12
    assert abs(sum(species[k] for k in ("xHeI_per_H","xHeII_per_H","xHeIII_per_H"))-species["helium_inventory_per_H"]) <= 5e-13
    assert species["xHeI_per_H"] > 0
    assert state["thermal_energy_density_erg_cm3"] == pytest.approx(10*state["thermal_energy_density_J_m3"])


def test_interpolation_rejects_bad_charge_and_native_grid_rejects_arbitrary_spacing():
    import math
    target=-math.log(21.)
    rows=[]
    for i,offset in enumerate((-2.,-1.,1.,2.)):
        x=target+offset*1e-3
        rows.append({"index":i,"ln_a":x,"stage":"fixture","xHII_per_H":.01,
            "xHeII_per_He":.02,"xHeIII_per_He":.001,"xe_per_H":.5,
            "Tm_K":3.,"H_s_inv":1e-16,"nH_m3":1.})
    with pytest.raises(ValueError, match="charge inventory"):
        _interpolate_four_point_ln_a(rows,20.)
    _validate_native_grid_row(0,-math.log(8001.))
    with pytest.raises(ValueError, match="source-native ln"):
        _validate_native_grid_row(1,-math.log(8001.)+8.49e-5+1e-4)


def _numeric_refinement_fixture(tmp_path):
    steps = [NATIVE_LNA_STEP/2, NATIVE_LNA_STEP/4]
    refinements = []
    for i, step in enumerate(steps):
        raw = f"independent refinement {i}\n".encode()
        name = f"refinement_{i}.jsonl"
        (tmp_path/name).write_bytes(raw)
        refinements.append({"run_id":f"r{i}", "history_path":name,
                            "history_sha256":hashlib.sha256(raw).hexdigest(),
                            "step_size":step, "status":"PASS"})
    tolerances = {name: .2 for name in REQUIRED_PARITY_METRICS}
    sha = _canonical_sha(tolerances)
    metrics = {name:{"baseline_value":1.04, "coarse_refinement_value":1.01,
                     "fine_refinement_value":1.0025, "observed_order":2.,
                     "extrapolated_value":1., "error_bound":.0025}
               for name in REQUIRED_PARITY_METRICS}
    conv = {"independent_refinements":refinements, "richardson_status":"PASS",
            "richardson":{"status":"PASS", "metrics":metrics},
            "predeclared_tolerances":tolerances, "tolerance_contract_sha256":sha}
    producer = {"convergence_tolerance_contract_sha256":sha}
    reviewer = {"convergence_tolerance_contract_sha256":sha}
    return conv, producer, reviewer


def test_refinement_rejects_duplicate_history_bytes_despite_distinct_ids(tmp_path):
    conv, producer, reviewer = _numeric_refinement_fixture(tmp_path)
    assert not _richardson_reasons(conv, "0"*64, tmp_path, producer, reviewer)
    first = conv["independent_refinements"][0]
    second = conv["independent_refinements"][1]
    second["history_path"] = first["history_path"]
    second["history_sha256"] = first["history_sha256"]
    assert any("not independent" in x for x in _richardson_reasons(
        conv, "0"*64, tmp_path, producer, reviewer))


def test_richardson_rejects_shallow_pass_and_unbound_tolerances(tmp_path):
    conv, producer, reviewer = _numeric_refinement_fixture(tmp_path)
    conv["richardson"] = {"status":"PASS"}
    assert any("inventory is incomplete" in x for x in _richardson_reasons(
        conv, "0"*64, tmp_path, producer, reviewer))
    conv, producer, reviewer = _numeric_refinement_fixture(tmp_path)
    producer["convergence_tolerance_contract_sha256"] = "0"*64
    assert any("not bound" in x for x in _richardson_reasons(
        conv, "0"*64, tmp_path, producer, reviewer))
    conv, producer, reviewer = _numeric_refinement_fixture(tmp_path)
    key = next(iter(REQUIRED_PARITY_METRICS))
    conv["richardson"]["metrics"][key]["extrapolated_value"] = 1.5
    assert any("extrapolated value" in x for x in _richardson_reasons(
        conv, "0"*64, tmp_path, producer, reviewer))


def test_parity_refuses_arbitrary_metric_and_unbound_tolerance():
    tolerances = {name:.01 for name in REQUIRED_PARITY_METRICS}
    parity = {"predeclared_metric_inventory":sorted(REQUIRED_PARITY_METRICS),
              "tolerances":tolerances,
              "metrics":{name:.001 for name in REQUIRED_PARITY_METRICS},
              "tolerance_contract_sha256":_canonical_sha(tolerances)}
    producer = {"parity_tolerance_contract_sha256":_canonical_sha(tolerances)}
    reviewer = {"parity_tolerance_contract_sha256":_canonical_sha(tolerances)}
    assert not _parity_reasons(parity, producer, reviewer)
    parity["metrics"] = {"arbitrary_weak_metric":0.}
    assert any("inventory is incomplete" in x for x in _parity_reasons(parity, producer, reviewer))
    parity["metrics"] = {name:.001 for name in REQUIRED_PARITY_METRICS}
    reviewer["parity_tolerance_contract_sha256"] = "0"*64
    assert any("not bound" in x for x in _parity_reasons(parity, producer, reviewer))


def test_source_charge_and_density_use_scaled_inventory_tolerance():
    import math
    z = 20.
    fh = source_number_fractions(.2454)["fHe_helium_nuclei_per_hydrogen_nucleus"]
    rad = HYREC_RADIATION_H2_PER_K4*R3G_COSMOLOGY["T0_K"]**4*(1+HYREC_NU_DENSITY_FACTOR*R3G_COSMOLOGY["N_eff_massless"])
    h = HYREC_H100_S_INV*math.sqrt(R3G_COSMOLOGY["omega_m_h2"]*21**3+rad*21**4+R3G_COSMOLOGY["omega_lambda_h2"])
    nh = HYREC_NH0_PER_OMBH2*R3G_COSMOLOGY["omega_b_h2"]*(1-.2454)*21**3
    base = {"z":z,"stage":"FIXTURE","interpolation":{},"xe_per_H":.0002+fh*.001,
            "xHII_per_H":.0002,"xHeII_per_He":.001,"xHeIII_per_He":0.,
            "Tm_K":10.,"H_s_inv":h,"nH_m3":nh,
            "xHII_determination":"FIXTURE","xHeII_determination":"FIXTURE",
            "xHeIII_determination":"FIXTURE"}
    _source_state(base, source_number_fractions(.2454), R3G_COSMOLOGY)
    bad = dict(base, xe_per_H=base["xe_per_H"]+7e-13)
    with pytest.raises(ValueError, match="charge ledger"):
        _source_state(bad, source_number_fractions(.2454), R3G_COSMOLOGY)
    bad = dict(base, nH_m3=nh*(1+5e-11))
    with pytest.raises(ValueError, match="frozen cosmology"):
        _source_state(bad, source_number_fractions(.2454), R3G_COSMOLOGY)
    bad = dict(base, H_s_inv=h*(1+5e-11))
    with pytest.raises(ValueError, match="source H does not match"):
        _source_state(bad, source_number_fractions(.2454), R3G_COSMOLOGY)


def test_recipient_h_and_nh_reject_intermediate_relative_discrepancies():
    # These errors formerly fell below the 2e-10 guard but exceed the frozen
    # same-unit 1e-12 inventory criterion.
    h = 1e-16
    nh = 2e3
    _require_density_match(h*(1+5e-13), h, "recipient H")
    _require_density_match(nh*(1+5e-13), nh, "recipient nH")
    with pytest.raises(ValueError, match="recipient H does not match"):
        _require_density_match(h*(1+5e-11), h, "recipient H")
    with pytest.raises(ValueError, match="recipient nH does not match"):
        _require_density_match(nh*(1+5e-11), nh, "recipient nH")
