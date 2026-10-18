"""Small real-checkpoint source tests plus paired-runner failure controls.

Real U4 states validate the gather/atomic surface only, not the U5-to-U6
trajectory or its performance. The expensive U5 input is not downloaded by CI.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import zipfile

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"scripts")]
from compare_r3k_u6_backends import array_digest, result_digests, require_identical
from full_bianchi_hyrec.trajectory.owned_flrw_history import OwnedFLRWHistory
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    _canonical_twophoton_table, populate_original_full_atomic, complete_original_full_atomic)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    HyRec2012Cosmology, make_hmla_source, DLNA)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from verify_r3i_h2_start import FullSourceCOracle

ARCHIVE = ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
U4 = ROOT/"research/rec_r3i_time_refinement_20261016/h2_u4_post_saha_exit_001/ncp_run_001/python_u4_exit.npz"
U4_SHA = "7ad1476c78d08218e42ac616dc43d03dd8eb232c44bfb66a8f20a237dcce6943"


def tiny_result():
    return SimpleNamespace(states=({"iz": 1, "xe": .3}, {"iz": 2, "xe": .2}),
                           steps=({"hydrogen_rhs": -.1},), event={}, full_evaluations=1,
                           status="HOLD_CAP_BEFORE_RT_BOUNDARY", rt_stop_iz=58389,
                           virtual_out=np.zeros((311, 2)),
                           average_virtual=np.zeros((311, 2)), lyman_out=np.zeros((3, 2)))


def test_logical_bytes_do_not_depend_on_C_or_Fortran_layout():
    a = np.arange(30, dtype=np.float64).reshape(5, 6)
    assert array_digest(a) == array_digest(np.asfortranarray(a))
    assert array_digest(a[:, ::2]) == array_digest(a[:, ::2].copy())


@pytest.mark.parametrize("field", ["virtual_out", "average_virtual", "lyman_out"])
def test_any_single_bit_field_change_fails_pair(field):
    left, right = tiny_result(), tiny_result()
    getattr(right, field)[0, 0] = -0.0
    with pytest.raises(ArithmeticError, match="BACKEND_BYTE_MISMATCH"):
        require_identical(result_digests(left), result_digests(right))


def test_state_rhs_and_endpoint_are_bound():
    left = tiny_result()
    for key, changed in (("states", ({"iz": 1, "xe": .3}, {"iz": 2, "xe": .21})),
                         ("steps", ({"hydrogen_rhs": -.11},)),
                         ("rt_stop_iz", 58390)):
        right = deepcopy(left)
        setattr(right, key, changed)
        with pytest.raises(ArithmeticError, match="BACKEND_BYTE_MISMATCH"):
            require_identical(result_digests(left), result_digests(right))


def test_nonfinite_and_dtype_are_rejected_not_hashed_as_success():
    value = np.zeros((3, 4))
    value[0, 0] = np.nan
    with pytest.raises(ValueError, match="NONFINITE"):
        array_digest(value)
    with pytest.raises(ValueError, match="DTYPE"):
        array_digest(np.zeros((3, 4), dtype=np.float32))
    require_identical(result_digests(tiny_result()), result_digests(tiny_result()))


@pytest.fixture(scope="module")
def real_source(tmp_path_factory):
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == (
        "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27")
    assert hashlib.sha256(U4.read_bytes()).hexdigest() == U4_SHA
    with np.load(U4, allow_pickle=False) as saved:
        states = [json.loads(str(s)) for s in saved["states_json"]]
        fields = {key: np.array(saved[key], copy=True) for key in
                  ("virtual_out", "average_virtual", "lyman_out")}
    folder = tmp_path_factory.mktemp("r3k_original_h2")
    members = ("hydrogen.c", "hydrogen.h", "helium.c", "helium.h", "history.h",
               "hyrectools.c", "hyrectools.h", "hyrec_params.h", "Alpha_inf.dat",
               "R_inf.dat", "two_photon_tables.dat")
    with zipfile.ZipFile(ARCHIVE) as z:
        for name in members:
            z.extract("HyRec/"+name, folder)
    native = folder/"HyRec"
    header = native/"hyrec_params.h"
    before = header.read_bytes()
    token = b"#define DLNA          8.49e-5"
    assert before.count(token) == 1
    header.write_bytes(before.replace(token, b"#define DLNA          (8.49e-5/2.)", 1))
    lib = folder/"liboriginal.so"
    harness = ROOT/"scripts/c_harness/original_hyrec_r3i_h2_continuation_harness.c"
    command = ["gcc", "-std=gnu99", "-O2", "-fno-fast-math", "-shared", "-fPIC",
               "-DR3I_SHARED", "-I", str(native), str(harness),
               str(native/"hydrogen.c"), str(native/"helium.c"),
               str(native/"hyrectools.c"), "-lm", "-o", str(lib)]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    c = HyRec2012Cosmology()
    rates = OriginalHyRecPrimitiveRateTable.from_archive(ARCHIVE)
    table = _canonical_twophoton_table(ARCHIVE)
    return (states, fields, c, make_hmla_source(c, rates), table,
            FullSourceCOracle(lib, native, c))


@pytest.mark.parametrize("offset", [-17, -9, -1])
def test_real_U4_owned_gather_and_original_C_atomic_snapshot(real_source, offset):
    states, fields, c, source, table, oracle = real_source
    state = states[offset]
    assert state["xHeII"] == 0.
    j = int(state["iz"]) - c.izH0
    prefix = {key: value[:, :j] for key, value in fields.items()}
    assert prefix["virtual_out"].shape == (311, j)
    owner = OwnedFLRWHistory(
        energies_eV=table.energy_eV, z_start=c.redshift(c.izH0), dlna=DLNA,
        virtual=prefix["virtual_out"], average=prefix["average_virtual"],
        lyman=prefix["lyman_out"], capacity=j+1)
    ref = causal_incoming_from_accepted_histories(
        energies_eV=table.energy_eV, virtual_history=prefix["virtual_out"],
        lyman_history=prefix["lyman_out"], z_start=c.redshift(c.izH0),
        iz=j, z_face=state["z"], dlna=DLNA, shear_q=0.)
    incoming_v, incoming_l = owner.incoming(state["z"])
    assert incoming_v.tobytes() == ref.virtual_distortion[0].tobytes()
    assert incoming_l.tobytes() == ref.lya_lyb_incoming_distortion[0].tobytes()
    tr = c.T0_K*(1+state["z"])
    tm = math.nextafter(state["Tm_K"], 0.) if state["Tm_K"] == tr else state["Tm_K"]
    actual = complete_original_full_atomic(populate_original_full_atomic(
        source, z=state["z"], xHII=state["xe"], xe=state["xe"], Tm_K=tm,
        incoming_virtual=incoming_v, incoming_lyman=incoming_l))
    expected = oracle(j, state["z"], state["xe"], 0., tm,
                      prefix["virtual_out"], prefix["lyman_out"])
    maxima = {}
    for label, py, native, energy in (
            ("virtual", actual.outgoing_virtual, expected["virtual"], table.energy_eV),
            ("average", actual.average_virtual, expected["average"], table.energy_eV),
            ("lyman", actual.outgoing_lyman, expected["lyman"],
             np.array([10.198714553953742, 12.087365397278509, 12.748393192442178]))):
        bb = 1/np.expm1(energy/(8.617343e-5*tr))
        tol = 1e-7*np.maximum(np.abs(py), np.abs(native)) + 1e-10*bb
        ratio = np.abs(py-native)/tol
        assert np.all(np.isfinite(ratio)) and np.all(ratio <= 1.)
        maxima[label] = float(np.max(ratio))
    rhs = abs(actual.dxHII_dln_a-expected["rhs"])/max(1., abs(expected["rhs"]))
    assert rhs <= 2e-10
    assert actual.normalized_matrix_residual <= 2e-10
    owner.append(expected_index=j, virtual=actual.outgoing_virtual,
                 average=actual.average_virtual, lyman=actual.outgoing_lyman)
    assert owner.accepted_columns == j+1
    v, a, ly = owner.readonly_views()
    assert v[:, j].tobytes() == actual.outgoing_virtual.tobytes()
    assert a[:, j].tobytes() == actual.average_virtual.tobytes()
    assert ly[:, j].tobytes() == actual.outgoing_lyman.tobytes()
    folder = os.environ.get("REC_R3K_EVIDENCE_DIRECTORY")
    if folder:
        out = Path(folder)
        out.mkdir(parents=True, exist_ok=True)
        (out/f"real_U4_{state['iz']}.json").write_text(json.dumps({
            "checkpoint_sha256": U4_SHA, "global_index": state["iz"],
            "z": state["z"], "accepted_prefix_columns": j,
            "gather_bitwise_equal": True, "native_C_atomic_tolerance_ratio": maxima,
            "rhs_scaled_difference": rhs, "schur_residual": actual.normalized_matrix_residual,
            "status": "PASS_REAL_U4_SOURCE_SNAPSHOT_ONLY", "U5_temporal_parity": "NOT_RUN",
        }, indent=2, sort_keys=True)+"\n")
