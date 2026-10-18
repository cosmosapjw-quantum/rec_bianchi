"""Frozen h/2 U6 boundary and causal controls."""
from pathlib import Path
import sys

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
from verify_r3i_h2_u6_rt_boundary import causal_link_count


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
