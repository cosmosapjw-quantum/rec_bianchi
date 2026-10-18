"""Bounded h/2 thermal continuation invariants at the reviewed U4 boundary."""
from pathlib import Path
import hashlib
import math
import sys

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory import primordial_2012_refined_u5_thermal as mod
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import HyRec2012Cosmology, make_hmla_source
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from r3i_u5_average_forensic import numerical_gates, phi80
import r3i_u5_average_forensic as forensic
from verify_r3i_h2_u5_thermal import CombinedOracle, KB_EV_K
CHECKPOINT=ROOT/"research/rec_r3i_time_refinement_20261016/h2_u4_post_saha_exit_001/ncp_run_001/python_u4_exit.npz"
ZIP=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def test_reviewed_identity_and_thermal_memory(tmp_path):
    assert hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()==mod.CHECKPOINT_SHA256
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    assert cp["state"]["iz"]==38452
    assert cp["state"]["xHeII"]==0. and cp["state"]["post_saha"] is False
    assert len(cp["temperature_tail"])==4
    assert cp["rhs_tail"]==(-0.4919330230209214,-0.45204486161530666)
    assert cp["virtual_out"].shape==(311,2006)
    corrupt=tmp_path/"corrupt.npz"
    data=CHECKPOINT.read_bytes();corrupt.write_bytes(data[:-1]+bytes([data[-1]^1]))
    with pytest.raises(ValueError,match="SHA_MISMATCH"):
        mod.load_frozen_checkpoint(corrupt)


def test_one_accepted_steady_step_preserves_causal_prefix():
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    c=HyRec2012Cosmology()
    source=make_hmla_source(c,OriginalHyRecPrimitiveRateTable.from_archive(ZIP))
    accepted=[]
    result=mod.integrate_u5_thermal(cp,c,source,max_extra_accepted=1,
        max_full_evaluations=1,on_accept=lambda s,step,out:accepted.append(step))
    assert result.status=="HOLD_CAP_BEFORE_THERMAL_EVENT_PLUS_TWO"
    assert result.event is None and result.full_evaluations==1
    assert result.states[-1]["iz"]==38453
    assert result.steps[0]["photon_col"]==2006
    assert result.steps[0]["coupled"] is False
    assert result.steps[0]["thermal_rhs"] is None
    assert math.isfinite(result.steps[0]["hydrogen_rhs"])
    assert np.array_equal(result.virtual_out[:,:2006],cp["virtual_out"])
    assert len(accepted)==1


def test_pre_source_caps_and_stage_guards():
    cp=mod.load_frozen_checkpoint(CHECKPOINT)
    c=HyRec2012Cosmology()
    with pytest.raises(ValueError,match="EXTRA_ACCEPTED_CAP"):
        mod.integrate_u5_thermal(cp,c,None,max_extra_accepted=20001)
    with pytest.raises(ValueError,match="FULL_EVALUATION_CAP"):
        mod.integrate_u5_thermal(cp,c,None,max_full_evaluations=20001)
    cp["state"]["post_saha"]=True
    with pytest.raises(ValueError,match="CHECKPOINT_SOURCE_STAGE"):
        mod.integrate_u5_thermal(cp,c,None,max_extra_accepted=1)


def test_new_mean_photon_gates_are_separate_and_domain_bounded():
    tau=2.e-5
    owner={"bin":8,"tau":tau,"raw":1.e-11,"incoming":1.e-11,"Q":2.e-12,
           "phi64":1.-(1.-math.exp(-tau))/tau,"A80":str(phi80(tau)),
           "phi80":str(phi80(tau)),
           "phi_bound":2.**-53/tau+4*2.**-53,
           "raw_reconstruction_absolute":0.,"source_reconstruction_absolute":0.}
    same=numerical_gates(owner,dict(owner),1.e-10)
    assert same["original_gate"]["status"]=="PASS"
    assert same["decimal80_ieee_gate"]["status"]=="PASS"
    other=dict(owner,raw=1.e-5)
    split=numerical_gates(owner,other,1.e-10)
    assert split["original_gate"]["status"]=="FAIL"
    assert split["decimal80_ieee_gate"]["status"]=="FAIL"
    outside=numerical_gates(dict(owner,tau=1.e-3),other,1.e-10)
    assert outside["decimal80_ieee_gate"]["status"]=="HOLD_OUTSIDE_DIAGNOSTIC_DOMAIN"
    diffusion=numerical_gates(dict(owner,bin=100),dict(other,bin=100),1.e-10)
    assert diffusion["original_gate"]["status"]=="FAIL"
    assert diffusion["decimal80_ieee_gate"]["status"]=="HOLD_OUTSIDE_DIAGNOSTIC_DOMAIN"


def test_thermal_c_oracle_uses_production_tr_operand_order():
    c=HyRec2012Cosmology()
    oracle=object.__new__(CombinedOracle)
    oracle.c=c
    received=[]
    oracle.tfn=lambda *args: received.append(args) or args[2]
    z=836.125
    got=oracle.thermal_rhs(.12,2200.,z)
    expected=(KB_EV_K*c.T0_K*(1.+z))/KB_EV_K
    assert got==expected and received[0][2]==expected


def test_forensic_writes_owner_histories_before_diagnostic(tmp_path,monkeypatch):
    sample={"bin":8,"tau":2.e-5,"raw":1.e-11,"incoming":1.e-11,"Q":2.e-12,
            "phi64":1.,"phi80":"1","A80":"1e-11","phi_bound":1.e-11,
            "raw_reconstruction_absolute":0.,"source_reconstruction_absolute":0.}
    monkeypatch.setattr(forensic,"_owner",lambda owner,*args,**kwargs:
                        {**sample,"owner":owner})
    c=HyRec2012Cosmology()
    table=type("Table",(),{"energy_eV":np.full(311,10.)})()
    state={"iz":38452,"z":1563.05,"xe":.98,"Tm_K":4262.}
    vh=np.ones((311,2));lh=np.zeros((3,2))
    report=forensic.preserve_failure(tmp_path,j=2,b=8,
        python_state=state,c_state=state,py_vh=vh,py_lh=lh,c_vh=vh,c_lh=lh,
        py_raw=1.e-11,c_raw=1.e-11,c=c,source=None,table=table,oracle=None,
        source_dir=tmp_path,source_identities={"test":"mechanical"})
    folder=tmp_path/"average_first_failure"
    assert report["status"]=="DIAGNOSTIC_COMPLETE"
    assert (folder/"forensic_input.json").is_file()
    assert (folder/"forensic_result.json").is_file()
    assert np.array_equal(np.load(folder/"c_virtual.npy"),vh)
    assert len(report["accepted_history_sha256"])==4
    with pytest.raises(FileExistsError):
        forensic.preserve_failure(tmp_path,j=2,b=8,python_state=state,c_state=state,
            py_vh=vh,py_lh=lh,c_vh=vh,c_lh=lh,py_raw=1.e-11,c_raw=1.e-11,
            c=c,source=None,table=table,oracle=None,source_dir=tmp_path,
            source_identities={"test":"repeat forbidden"})
