"""Cheap identity and shape tests for the bounded R3G-U3 continuation."""
from pathlib import Path
import math
import importlib.util
import hashlib
from zipfile import ZipFile

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.primordial_2012_continuation import (
    MAX_EXTRA_ACCEPTED, REVIEWED_U2_CHECKPOINT_SHA256,
    REVIEWED_U2_PRODUCER_SHA256, REVIEWED_U2_RECEIPT_SHA256,
    ContinuationCheckpoint, ContinuationHistory,
    _validate_live_limits, load_reviewed_u2_checkpoint,
    _hydrogen_saha_helium_coupling,
)
import full_bianchi_hyrec.trajectory.primordial_2012_continuation as continuation

ROOT = Path(__file__).resolve().parents[2]
U2 = ROOT / "research/rec_r3g_primordial_20261016/full_start_011"
_spec = importlib.util.spec_from_file_location("r3g_u3_verifier", ROOT / "scripts/verify_r3g_continuation.py")
_verifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_verifier)


def test_reviewed_u2_checkpoint_roundtrip_and_native_tails():
    loaded = load_reviewed_u2_checkpoint(
        U2 / "python_accepted_history.npz",
        U2 / "verification.json",
        ROOT / "src/full_bianchi_hyrec/trajectory/primordial_2012_full_start.py",
    )
    assert loaded.reviewed_u2_sha256 == REVIEWED_U2_PRODUCER_SHA256
    assert loaded.receipt_sha256 == REVIEWED_U2_RECEIPT_SHA256
    assert loaded.checkpoint_sha256 == REVIEWED_U2_CHECKPOINT_SHA256
    assert loaded.endpoint["iz"] == 18231
    assert loaded.endpoint["hydrogen_rhs_f7"] == loaded.start.hydrogen_rhs_dln_a[7]
    assert loaded.endpoint["hydrogen_rhs_f6"] == loaded.start.hydrogen_rhs_dln_a[6]
    assert loaded.endpoint["helium_rhs_f7"] == loaded.start.helium_rhs_dln_a[7]
    assert loaded.endpoint["helium_rhs_f6"] == loaded.start.helium_rhs_dln_a[6]
    assert loaded.start.virtual_out.shape == (311, 8)
    assert loaded.start.average_virtual.shape == (311, 8)
    assert loaded.start.lyman_out.shape == (3, 8)


def test_continuation_checkpoint_rejects_unreviewed_producer_identity():
    good = load_reviewed_u2_checkpoint(
        U2 / "python_accepted_history.npz", U2 / "verification.json",
        ROOT / "src/full_bianchi_hyrec/trajectory/primordial_2012_full_start.py")
    with pytest.raises(ValueError, match="reviewed identity"):
        ContinuationCheckpoint(good.start, "0" * 64)


def test_continuation_history_refuses_partial_or_non_two_step_event_success():
    ncols = 8
    base = dict(
        iz=np.arange(18223, 18232), z=np.linspace(1702., 1701., 9),
        xH1s=np.full(9, .001), xHII=np.full(9, .999),
        xHeII=np.full(9, .0002), xe=np.full(9, .9992), Tm_K=np.full(9, 4600.),
        post_saha=np.ones(9, dtype=bool),
        source_branch_h_only=np.zeros(9, dtype=bool),
        helium_cutoff_crossed=np.zeros(9, dtype=bool),
        hydrogen_post_saha_off_crossed=np.zeros(9, dtype=bool),
        hydrogen_rhs_dln_a=np.zeros(ncols), helium_rhs_dln_a=np.zeros(ncols),
        virtual_out=np.zeros((311, ncols)), average_virtual=np.zeros((311, ncols)),
        lyman_out=np.zeros((3, ncols)), matrix_residual=np.zeros(ncols),
        accepted_extra=0, full_evaluations=0, event="NONE",
        branch_steps_after_event=0,
        status="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED",
        reviewed_u2_sha256=REVIEWED_U2_PRODUCER_SHA256,
        common_input_evaluations=0, common_input_sample_columns=(),
        common_input_max_rhs_scaled=0., common_input_max_virtual_ratio=0.,
        common_input_max_average_ratio=0., common_input_max_lyman_ratio=0.,
    )
    obj = ContinuationHistory(**base)
    assert obj.accepted_extra == 0
    assert not obj.virtual_out.flags.writeable
    bad = dict(base, event="HYDROGEN_POST_SAHA_OFF",
               status="EVENT_TWO_STEPS_COMPLETE", branch_steps_after_event=1)
    with pytest.raises(ValueError, match="exactly two"):
        ContinuationHistory(**bad)
    wrong_grid = dict(base, z=np.array([1702., 1701., 1700., 1699., 1698., 1697., 1696., 1695., np.nan]))
    with pytest.raises(ValueError, match="nonfinite z"):
        ContinuationHistory(**wrong_grid)
    too_many = dict(base, common_input_evaluations=65,
                    common_input_sample_columns=tuple(range(65)))
    with pytest.raises(ValueError, match="sample cap"):
        ContinuationHistory(**too_many)


def test_event_completion_uses_global_endpoint_and_local_common_sample_column():
    nodes, cols = 12, 11
    iz = np.arange(18223, 18223 + nodes)
    xhe = np.full(nodes, .0002); xhe[9:] = 0.
    xh = np.full(nodes, .999); xe = xh + xhe
    post = np.ones(nodes, dtype=bool); post[9:] = False
    he_cross = np.zeros(nodes, dtype=bool); he_cross[9] = True
    h_cross = np.zeros(nodes, dtype=bool); h_cross[9] = True
    branch = np.zeros(nodes, dtype=bool); branch[9:] = True
    obj = ContinuationHistory(
        iz=iz, z=np.linspace(1702., 1700.9, nodes), xH1s=1.-xh, xHII=xh,
        xHeII=xhe, xe=xe, Tm_K=np.full(nodes, 4590.), post_saha=post,
        source_branch_h_only=branch, helium_cutoff_crossed=he_cross,
        hydrogen_post_saha_off_crossed=h_cross,
        hydrogen_rhs_dln_a=np.zeros(cols), helium_rhs_dln_a=np.zeros(cols),
        virtual_out=np.zeros((311,cols)), average_virtual=np.zeros((311,cols)),
        lyman_out=np.zeros((3,cols)), matrix_residual=np.zeros(cols),
        accepted_extra=3, full_evaluations=0,
        event="HELIUM_CUTOFF+HYDROGEN_POST_SAHA_OFF", branch_steps_after_event=2,
        status="EVENT_TWO_STEPS_COMPLETE", reviewed_u2_sha256=REVIEWED_U2_PRODUCER_SHA256,
        common_input_evaluations=1, common_input_sample_columns=(11,),
        common_input_max_rhs_scaled=0., common_input_max_virtual_ratio=0.,
        common_input_max_average_ratio=0., common_input_max_lyman_ratio=0.,
        endpoint_diagnostic_column=int(iz[11]), endpoint_diagnostic_rhs=0.,
        endpoint_diagnostic_matrix_residual=0.)
    assert obj.helium_cutoff_crossed[9] and obj.hydrogen_post_saha_off_crossed[9]
    assert obj.source_branch_h_only[9]
    assert obj.endpoint_diagnostic_column == int(iz[11])
    assert obj.common_input_sample_columns == (11,)
    bad = dict(
        iz=iz, z=np.linspace(1702.,1700.9,nodes), xH1s=1.-xh, xHII=xh,
        xHeII=xhe, xe=xe, Tm_K=np.full(nodes,4590.), post_saha=post,
        source_branch_h_only=branch, helium_cutoff_crossed=he_cross,
        hydrogen_post_saha_off_crossed=h_cross,
        hydrogen_rhs_dln_a=np.zeros(cols), helium_rhs_dln_a=np.zeros(cols),
        virtual_out=np.zeros((311,cols)), average_virtual=np.zeros((311,cols)),
        lyman_out=np.zeros((3,cols)), matrix_residual=np.zeros(cols),
        accepted_extra=3, full_evaluations=0,
        event="HELIUM_CUTOFF+HYDROGEN_POST_SAHA_OFF", branch_steps_after_event=2,
        status="EVENT_TWO_STEPS_COMPLETE", reviewed_u2_sha256=REVIEWED_U2_PRODUCER_SHA256,
        common_input_evaluations=1, common_input_sample_columns=(int(iz[11]),),
        common_input_max_rhs_scaled=0., common_input_max_virtual_ratio=0.,
        common_input_max_average_ratio=0., common_input_max_lyman_ratio=0.,
        endpoint_diagnostic_column=int(iz[11]), endpoint_diagnostic_rhs=0.,
        endpoint_diagnostic_matrix_residual=0.)
    with pytest.raises(ValueError, match="common-input C oracle sample"):
        ContinuationHistory(**bad)


def test_helium_post_saha_source_stencil_allows_negative_trial(monkeypatch):
    from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
    cosmology = HyRec2012Cosmology()
    trials = []
    def fake_saha(_c, xhe, _z):
        trials.append(xhe)
        return 0.2 + xhe
    monkeypatch.setattr(continuation, "saha_xH1s", fake_saha)
    result = _hydrogen_saha_helium_coupling(cosmology, 1.e-8, 1500.)
    assert math.isfinite(result)
    assert min(trials) < 0.0
    trials.clear()
    assert _hydrogen_saha_helium_coupling(cosmology, 0.0, 1500.) == 0.0
    assert not trials


def test_frozen_common_input_schedule_and_caps_are_explicit():
    base_cols = (8, 9, 16, 32, 64, 128, 256, 512, 1024, 2048)
    assert len(base_cols) <= 64
    _validate_live_limits(2048, 8192)


def test_source_capsule_identity_is_not_git_dependent():
    verifier = ROOT / "scripts/verify_r3g_continuation.py"
    text = verifier.read_text()
    assert 'BASE_REPOSITORY_REVISION = "140f0e67e2a880fc6d40d298e3bfff0de229f7df"' in text
    assert "zip_member_hashes()" in text
    assert "--execution-manifest" in text


def test_controller_manifest_binds_revision_capsule_and_owned_files(tmp_path):
    record = {"controller_verified":True,
        "base_revision":_verifier.BASE_REPOSITORY_REVISION,
        "execution_revision":"a"*40,"capsule_manifest_sha256":"b"*64,
        "source_zip_sha256":_verifier.PINNED_ZIP_SHA,
        "u3_files_sha256":{p:_verifier.sha(ROOT/p) for p in _verifier.U3_TRACKED_FILES}}
    path=tmp_path/"controller.json"
    import json
    path.write_text(json.dumps(record))
    assert _verifier.validate_execution_manifest(path)["execution_revision"] == "a"*40
    record["u3_files_sha256"][_verifier.U3_TRACKED_FILES[0]]="0"*64
    path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError,match="U3_FILE_HASH_MISMATCH"):
        _verifier.validate_execution_manifest(path)


def test_controller_manifest_binds_execution_and_all_owned_file_hashes(tmp_path):
    record = {"controller_verified":True,
        "base_revision":_verifier.BASE_REPOSITORY_REVISION,
        "execution_revision":"a"*40,"capsule_manifest_sha256":"b"*64,
        "source_zip_sha256":_verifier.PINNED_ZIP_SHA,
        "u3_files_sha256":{p:_verifier.sha(ROOT/p) for p in _verifier.U3_TRACKED_FILES}}
    path = tmp_path / "controller.json"
    import json
    path.write_text(json.dumps(record))
    assert _verifier.validate_execution_manifest(path)["execution_revision"] == "a"*40
    record["u3_files_sha256"][_verifier.U3_TRACKED_FILES[0]] = "0"*64
    path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError,match="U3_FILE_HASH_MISMATCH"):
        _verifier.validate_execution_manifest(path)


def test_native_end_record_accepts_bounded_and_hold_without_promoting_to_pass():
    bounded = _verifier.validate_end_fields(
        ["BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED", "0", "0", "0", "2056"], 2048)
    assert bounded["status"] == "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    hold = _verifier.validate_end_fields(
        ["HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY", "0", "0", "0", "17"], 9)
    assert hold["status"].startswith("HOLD_NEXT_STAGE_REQUIRED")
    with pytest.raises(ValueError, match="FALSE_EVENT_SUCCESS"):
        _verifier.validate_end_fields(["EVENT_TWO_STEPS_COMPLETE", "0", "0", "2", "11"], 3)
    dual = _verifier.validate_end_fields(
        ["EVENT_TWO_STEPS_COMPLETE", "1", "3", "2", "10"], 2)
    assert dual["first_event_flags"] == 1
    assert dual["cumulative_crossing_flags"] == 3


def test_branch_comparison_separates_input_and_output_nodes():
    _verifier.compare_source_branch(False, True, False, True, 17)
    with pytest.raises(ArithmeticError, match="SOURCE_INPUT_BRANCH_PARITY"):
        _verifier.compare_source_branch(False, True, True, True, 17)


def test_source_dir_complete_tree_mutation_is_rejected(tmp_path, monkeypatch):
    archive = tmp_path / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
    archive.parent.mkdir(parents=True)
    files = {"history.c":b"h", "helium.c":b"he", "hydrogen.c":b"h2",
             "hyrec_params.h":b"params", "R_inf.dat":b"rates", "helium.h":b"header"}
    with ZipFile(archive,"w") as zf:
        for name,data in files.items(): zf.writestr("HyRec/"+name,data)
        zf.writestr("__MACOSX/HyRec/._history.c",b"metadata")
    source = tmp_path / "capsule/HyRec"; source.mkdir(parents=True)
    for name,data in files.items(): (source/name).write_bytes(data)
    monkeypatch.setattr(_verifier,"ROOT",tmp_path)
    monkeypatch.setattr(_verifier,"PINNED_ZIP_SHA",_verifier.sha(archive))
    monkeypatch.setattr(_verifier,"PINNED_SOURCE",{k:hashlib.sha256(files[k]).hexdigest()
        for k in ("history.c","helium.c","hydrogen.c","hyrec_params.h")})
    assert _verifier.safe_source(source,tmp_path/"evidence") == source
    (source/"R_inf.dat").write_bytes(b"mutated table")
    with pytest.raises(RuntimeError,match="COMPLETE_TREE_MISMATCH"):
        _verifier.safe_source(source,tmp_path/"evidence")


def test_exception_checkpoint_is_create_only_and_keeps_failure_metadata(tmp_path):
    payload = {"phase":"EXCEPTION", "accepted_extra":8,
               "global_iz":np.arange(18223,18232),
               "failure":{"type":"ArithmeticError","message":"first failure"}}
    _verifier.save_checkpoint(tmp_path, payload)
    meta = tmp_path / "checkpoint_0008_exception.json"
    assert meta.is_file()
    import json
    assert json.loads(meta.read_text())["failure"]["message"] == "first failure"
    with pytest.raises(FileExistsError):
        _verifier.save_checkpoint(tmp_path, payload)


def test_execution_caps_are_hard_limits():
    _validate_live_limits(2048, 8192)
    with pytest.raises(ValueError):
        _validate_live_limits(MAX_EXTRA_ACCEPTED + 1, 8192)
    with pytest.raises(ValueError):
        _validate_live_limits(2048, 8193)
