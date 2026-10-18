"""Source-stage and causal continuity tests for bounded h/2 U4 exit."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory import primordial_2012_refined_u4_exit as mod
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    HyRec2012Cosmology,make_hmla_source,
)
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable

ROOT=Path(__file__).resolve().parents[2]
CHECKPOINT=ROOT/"research/rec_r3i_time_refinement_20261016/h2_continuation_001/ncp_run_001/python_continuation.npz"
ZIP=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def test_reviewed_checkpoint_sha_and_tail(tmp_path):
    assert hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()==mod.CHECKPOINT_SHA256
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    assert cp["state"]["iz"]==37207
    assert cp["rhs_tail"]==(-0.2140541132585438,-0.06964592995647713)
    assert cp["virtual_out"].shape==(311,761)
    damaged=tmp_path/"modified.npz"
    raw=CHECKPOINT.read_bytes();damaged.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
    with pytest.raises(ValueError,match="SHA_MISMATCH"):
        mod.load_frozen_checkpoint(damaged)


def test_one_accepted_h_only_step_uses_only_own_history():
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    c=HyRec2012Cosmology()
    source=make_hmla_source(c,OriginalHyRecPrimitiveRateTable.from_archive(ZIP))
    got=[]
    result=mod.integrate_u4_exit(cp,c,source,max_extra_accepted=1,
                                 max_full_evaluations=4,
                                 on_accept=lambda state,step,out:got.append((state,step)))
    assert result.status=="CAP_BEFORE_EVENT_PLUS_TWO"
    assert result.full_evaluations==4
    assert result.states[-1]["iz"]==37208
    assert result.steps[0]["photon_col"]==761
    assert result.steps[0]["branch"]=="H_ONLY"
    assert math.isnan(result.steps[0]["helium_rhs"])
    assert result.virtual_out.shape==(311,762)
    assert np.array_equal(result.virtual_out[:,:761],cp["virtual_out"])
    assert len(got)==1
    assert result.steps[0]["schur_residual"]<2e-10


def test_stage_and_cap_guards_before_source_evaluation(monkeypatch):
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    c=HyRec2012Cosmology()
    source=make_hmla_source(c,OriginalHyRecPrimitiveRateTable.from_archive(ZIP))
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP"):
        mod.integrate_u4_exit(cp,c,None,max_extra_accepted=4097)
    with pytest.raises(ValueError,match="FULL_EVALUATION_CAP"):
        mod.integrate_u4_exit(cp,c,None,max_full_evaluations=16385)
    cp_bad=mod.load_frozen_checkpoint(CHECKPOINT)
    cp_bad["state"]["Tm_K"]=0.
    with pytest.raises(RuntimeError,match="HOLD_THERMAL_STAGE"):
        mod.integrate_u4_exit(cp_bad,c,source,max_extra_accepted=1)
    cp_bad=mod.load_frozen_checkpoint(CHECKPOINT)
    monkeypatch.setattr(mod,"original_rt_stop_index",lambda _ :mod.START_IZ)
    with pytest.raises(RuntimeError,match="HOLD_RT_STAGE"):
        mod.integrate_u4_exit(cp_bad,c,source,max_extra_accepted=1)


def test_bad_schur_residual_cannot_commit(monkeypatch):
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    c=HyRec2012Cosmology()
    source=make_hmla_source(c,OriginalHyRecPrimitiveRateTable.from_archive(ZIP))
    monkeypatch.setattr(mod,"complete_original_full_atomic",lambda _:
        SimpleNamespace(dxHII_dln_a=0.,normalized_matrix_residual=math.nan))
    accepted=[]
    with pytest.raises(ArithmeticError,match="FULL_SOURCE_OR_SCHUR"):
        mod.integrate_u4_exit(cp,c,source,max_extra_accepted=1,
                              on_accept=lambda *_:accepted.append(1))
    assert not accepted
