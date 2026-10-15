"""Checks acceptance gate and a deliberate source-integrity failure."""
from __future__ import annotations
from pathlib import Path
import importlib.util
import pytest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('verify_r3f_result',ROOT/'scripts/verify_r3f_result.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)


def test_local_source_verified_result():
    d=ROOT/'research/rec_r3f_ncp_yhe_20261016/local49_fine'
    if not d.exists():pytest.skip('independent measured local result not packaged with CI source')
    receipt=x.verify(d,'local')
    assert receipt['decision']=='PASS_SCOPED_ORIGINAL_HYREC_FULL_Q0_YHE_ONLY'


def test_mode_gate_prevents_false_claim():
    d=ROOT/'research/rec_r3f_ncp_yhe_20261016/local49_fine'
    if not d.exists():pytest.skip('local evidence not available')
    with pytest.raises(ValueError,match='mode mismatch'):
        x.verify(d,'ncp')
