"""Frozen h/2 U6 boundary and causal controls."""
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u4_exit import original_rt_stop_index
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u6_rt_boundary import (
    CHECKPOINT_SHA256, H_RHS_TAIL, T_RHS_TAIL, START_IZ, PREFIX_COLUMNS,
    MAX_EXTRA_ACCEPTED, load_frozen_checkpoint, integrate_u6_rt_boundary)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from verify_r3i_h2_u6_rt_boundary import (
    causal_link_count, check_thermal_event_row, AcceptedEvidenceWriter, last_jsonl)


def test_frozen_boundary_and_predictor_tails():
    c=HyRec2012Cosmology()
    assert original_rt_stop_index(c)==58389
    assert START_IZ+MAX_EXTRA_ACCEPTED==58389
    assert PREFIX_COLUMNS==START_IZ-c.izH0
    assert H_RHS_TAIL==(-0.056163878950571774,-0.0561296548568869)
    assert T_RHS_TAIL==(-2280.408518685064,-2281.8526711832496)
    assert len(CHECKPOINT_SHA256)==64


def test_checkpoint_byte_identity_hard_gate(tmp_path):
    wrong=tmp_path/"wrong.npz"
    wrong.write_bytes(b"not the reviewed U5 checkpoint")
    with pytest.raises(ValueError,match="REVIEWED_H2_U5_CHECKPOINT_SHA_MISMATCH"):
        load_frozen_checkpoint(wrong)


def test_zero_or_overcap_step_rejected_before_source_use():
    c=HyRec2012Cosmology()
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP"):
        integrate_u6_rt_boundary({},c,None,max_extra_accepted=0)
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP"):
        integrate_u6_rt_boundary({},c,None,max_extra_accepted=5211)


def test_all_313_source_links_retain_accepted_past():
    rates=OriginalHyRecPrimitiveRateTable.from_archive(
        ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
    table=_canonical_twophoton_table(rates.archive_path)
    assert causal_link_count(table,PREFIX_COLUMNS)==313
    assert causal_link_count(table,21942)==313


def test_thermal_event_requires_all_finite_native_fields():
    expected={"delta":0.0005000545426558922,
              "thermal_seed_prev2":-2295.1209635684745,
              "thermal_seed_prev":-2295.028818021708}
    good=["THERMAL_EVENT","53177",str(expected["delta"]),
          str(expected["thermal_seed_prev2"]),str(expected["thermal_seed_prev"])]
    check_thermal_event_row(good,expected)
    with pytest.raises(ArithmeticError,match="C_PRIOR_THERMAL_EVENT_FIELDS"):
        check_thermal_event_row(good[:-1],expected)
    with pytest.raises(ArithmeticError,match="C_PRIOR_THERMAL_NONFINITE"):
        check_thermal_event_row(good[:3]+["nan",good[4]],expected)
    with pytest.raises(ArithmeticError,match="C_PRIOR_THERMAL_NONFINITE"):
        check_thermal_event_row(good[:4]+["inf"],expected)


def test_attempt_and_accepted_bytes_survive_later_rejection(tmp_path):
    writer=AcceptedEvidenceWriter(tmp_path)
    out=SimpleNamespace(dxHII_dln_a=-.05,normalized_matrix_residual=1.e-15,
        outgoing_virtual=np.arange(311,dtype=float),
        average_virtual=np.arange(311,dtype=float)*.1,
        outgoing_lyman=np.arange(3,dtype=float))
    writer.attempt(53179,836.,.0054,2280.,16733)
    writer.source(53179,out)
    writer.accept({"iz":53180},{"input_iz":53179},out)
    writer.attempt(53180,835.,.0053,2279.,16734)
    writer.close()
    assert last_jsonl(tmp_path/"python_attempts.jsonl")["input_iz"]==53180
    assert last_jsonl(tmp_path/"python_source_evaluations.jsonl")["input_iz"]==53179
    assert last_jsonl(tmp_path/"python_accepted_partial.jsonl")["state"]["iz"]==53180
    assert (tmp_path/"python_partial_virtual_f64le.bin").stat().st_size==311*8
    assert (tmp_path/"python_partial_average_f64le.bin").stat().st_size==311*8
    assert (tmp_path/"python_partial_lyman_f64le.bin").stat().st_size==3*8
