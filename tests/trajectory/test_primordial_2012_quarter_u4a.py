"""Contract tests for the bounded h/4 U4A restart path."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
import pytest
from types import SimpleNamespace

from full_bianchi_hyrec.trajectory import primordial_2012_quarter_u4a as mod
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_start import QuarterStartCosmology, make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT = ROOT/"research/rec_r3q_h4_continuation_20261020/ncp_event_001/python_continuation.npz"
ZIP = ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def _source():
    c = QuarterStartCosmology()
    return c, make_hmla_source(c, OriginalHyRecPrimitiveRateTable.from_archive(ZIP))


def test_reviewed_checkpoint_identity_and_accepted_prefix():
    assert hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest() == mod.CHECKPOINT_SHA256
    cp = mod.load_reviewed_restart(CHECKPOINT)
    assert cp["state"]["iz"] == 74411
    assert cp["rhs_tail"] == (-.2148617237085924, -.06954421574831805)
    assert cp["virtual_out"].shape == (311, 1519)
    assert np.all(np.isfinite(cp["lyman_out"]))


def test_one_h4_accepted_step_writes_only_current_owned_column():
    cp = mod.load_reviewed_restart(CHECKPOINT)
    c, source = _source()
    got = mod.integrate_u4a(cp, c, source, accepted_steps=1, max_full_evaluations=4)
    assert got.full_evaluations == 4
    assert got.states[-1]["iz"] == 74412
    assert got.steps[0]["photon_col"] == 1519
    assert got.steps[0]["branch"] == "H_ONLY"
    assert math.isnan(got.steps[0]["helium_rhs"])
    assert np.array_equal(got.virtual_out[:, :1519], cp["virtual_out"])
    assert got.virtual_out.shape == (311, 1520)


def test_missing_duplicate_or_uncommitted_history_is_rejected():
    cp = mod.load_reviewed_restart(CHECKPOINT)
    c, source = _source()
    bad = dict(cp); bad["virtual_out"] = np.array(cp["virtual_out"], copy=True); bad["virtual_out"][0, 9] = np.nan
    with pytest.raises(ArithmeticError, match="MISSING_OR_UNCOMMITTED"):
        mod.integrate_u4a(bad, c, source, accepted_steps=1)
    # A duplicate accepted column changes the claimed source ownership length.
    bad = dict(cp); bad["virtual_out"] = np.column_stack((cp["virtual_out"], cp["virtual_out"][:, -1]))
    bad["average_virtual"] = np.column_stack((cp["average_virtual"], cp["average_virtual"][:, -1]))
    bad["lyman_out"] = np.column_stack((cp["lyman_out"], cp["lyman_out"][:, -1]))
    with pytest.raises(ValueError, match="HISTORY_OWNERSHIP"):
        mod.integrate_u4a(bad, c, source, accepted_steps=1)


def test_stage_guards_run_before_source_evaluation(monkeypatch):
    cp = mod.load_reviewed_restart(CHECKPOINT)
    c, source = _source()
    thermal = dict(cp); thermal["state"] = dict(cp["state"]); thermal["state"]["Tm_K"] = 0.
    with pytest.raises(RuntimeError, match="HOLD_THERMAL_STAGE"):
        mod.integrate_u4a(thermal, c, source, accepted_steps=1)
    monkeypatch.setattr(mod, "original_rt_stop_index", lambda _: mod.START_IZ)
    with pytest.raises(RuntimeError, match="HOLD_RT_STAGE"):
        mod.integrate_u4a(cp, c, source, accepted_steps=1)


def test_split_restart_is_identical_to_one_shot_16_steps():
    cp = mod.load_reviewed_restart(CHECKPOINT)
    c, source = _source()
    one = mod.integrate_u4a(cp, c, source, accepted_steps=16, max_full_evaluations=64)
    first = mod.integrate_u4a(cp, c, source, accepted_steps=8, max_full_evaluations=32)
    second = mod.integrate_u4a(mod.restart_checkpoint(first), c, source, accepted_steps=8, max_full_evaluations=32)
    assert one.states[-1] == second.states[-1]
    assert np.array_equal(one.final_predictor, second.final_predictor, equal_nan=True)
    assert np.array_equal(one.virtual_out, second.virtual_out)
    assert np.array_equal(one.average_virtual, second.average_virtual)
    assert np.array_equal(one.lyman_out, second.lyman_out)


def test_post_saha_off_restart_uses_predictor_and_keeps_flag():
    cp=mod.load_reviewed_restart(CHECKPOINT); cp=dict(cp); cp["state"]=dict(cp["state"]); cp["state"]["post_saha"]=False
    c, source=_source()
    got=mod.integrate_u4a(cp,c,source,accepted_steps=1,max_full_evaluations=1)
    expected=cp["state"]["xe"]+mod.DLNA*(1.25*got.steps[0]["hydrogen_rhs"]-.25*cp["rhs_tail"][0])
    assert got.states[-1]["xe"] == expected
    assert got.states[-1]["post_saha"] is False


def test_cumulative_restart_cap_rejects_33rd_accepted_step():
    cp=mod.load_reviewed_restart(CHECKPOINT); c, source=_source()
    first=mod.integrate_u4a(cp,c,source,accepted_steps=16,max_full_evaluations=64)
    with pytest.raises(ValueError,match="CUMULATIVE_ACCEPTED_STEP_CAP"):
        mod.integrate_u4a(mod.restart_checkpoint(first),c,source,accepted_steps=17)


def test_common_input_callback_uses_canonical_h4_two_photon_lanes():
    """The R3R lane check is framed by U4's causal local index, not R3R rows."""
    c, source = _source(); table = _canonical_twophoton_table(ZIP)
    out = SimpleNamespace(dxHII_dln_a=-.1, outgoing_virtual=np.ones(311),
                          average_virtual=np.ones(311), outgoing_lyman=np.ones(3))
    class Oracle:
        def __init__(self): self.c=c; self.calls=[]
        def __call__(self, j, z, xh, xhe, tm, vh, lh):
            self.calls.append((j, vh.shape, lh.shape))
            return {"rhs":out.dxHII_dln_a,"virtual":out.outgoing_virtual,
                    "average":out.average_virtual,"lyman":out.outgoing_lyman}
    oracle=Oracle(); metrics={}
    mod.common_input_observer(oracle, table, metrics)(74411,c.redshift(74411),.99,0.,4400.,np.ones((311,1519)),np.ones((3,1519)),out)
    assert oracle.calls == [(1519,(311,1519),(3,1519))]
    assert metrics["sampled_evaluations"] == 1
