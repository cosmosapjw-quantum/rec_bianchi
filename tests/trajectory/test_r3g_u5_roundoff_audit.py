"""Focused contract guards for the saved U5 roundoff audit."""
from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest

SCRIPT=Path(__file__).resolve().parents[2]/"scripts/audit_r3g_u5_roundoff.py"
spec=importlib.util.spec_from_file_location("audit_r3g_u5_roundoff",SCRIPT)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_decimal_phi_uses_exact_binary64_input_and_known_first_worst():
    first=audit.phi80(1.391865007501364e-06)
    worst=audit.phi80(1.468362417950462e-06)
    assert first == Decimal("6.9593218086942786948653994856681373500386307246012052868600546282716534782e-7")
    assert worst == Decimal("7.3418084962733114692184069407335341082702205100102138263682869991130758136e-7")
    assert audit.phi80(1.391865007501364e-06) != Decimal("1")-(Decimal("1")-(-Decimal(str(1.391865007501364e-06))).exp())/Decimal(str(1.391865007501364e-06))


def test_only_nine_original_average_failures_are_admitted():
    base={"virtual":[],"average":list(audit.FAIL_PAIRS),"lyman":[]}
    audit.require_expected_failures(base)
    for channel,pair in (("virtual",(2218,8)),("lyman",(2218,1)),("average",(5000,11))):
        changed={k:list(v) for k,v in base.items()}
        changed[channel].append(pair)
        with pytest.raises(ValueError,match="UNEXPECTED_PHOTON_FAILURE_COORDINATES"):
            audit.require_expected_failures(changed)


def test_manufactured_average_perturbation_exceeding_budget_rejects():
    audit.require_bound(1e-19,1e-20,1e-18)
    with pytest.raises(ValueError,match="PHI_PROPAGATED_BUDGET"):
        audit.require_bound(1.1e-18,1e-20,1e-18)
    with pytest.raises(ValueError,match="NONFINITE_DIAGNOSTIC_BOUND"):
        audit.require_bound(float("nan"),1e-20,1e-18)


def test_rhs_memory_and_phi_domain_mutations_reject():
    assert audit.require_scaled_pair(2.0,2.0,2e-8,"HYDROGEN_MEMORY")==0
    for label,limit in (("HYDROGEN_RHS",2e-7),("HYDROGEN_MEMORY",2e-8)):
        with pytest.raises(ValueError,match=label+"_PARITY"):
            audit.require_scaled_pair(2.0+4*limit,2.0,limit,label)
    audit.require_phi_domain(8,1.391865007501364e-6)
    for b,tau in ((100,1.391865007501364e-6),(8,1e-6),(8,1e-4)):
        with pytest.raises(ValueError,match="PHI_DIAGNOSTIC_DOMAIN"):
            audit.require_phi_domain(b,tau)


def test_pinned_input_hash_rejects_before_npz_or_trajectory_load(tmp_path):
    for name in audit.INPUT_SHA:
        (tmp_path/name).write_bytes(b"mutated")
    with pytest.raises(ValueError,match="IMMUTABLE_INPUT_SHA_MISMATCH"):
        audit.audit(tmp_path)
