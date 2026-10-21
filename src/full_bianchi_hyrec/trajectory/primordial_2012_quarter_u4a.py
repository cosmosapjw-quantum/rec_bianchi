"""Bounded h/4 U4 restart from the reviewed R3Q H-only endpoint.

The checkpoint owns only accepted source columns.  In particular, column
``iz - SOURCE_INDEX_START`` is written after its RHS is evaluated and never
serves as incoming history for that evaluation.  This module intentionally
does not infer an U4 exit from a capped run.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, complete_original_full_atomic,
    populate_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_quarter_start import (
    DLNA, QuarterStartCosmology, make_hmla_source, saha_xH1s, tm_steady_K,
)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    DXHII_MAX, checked_common_input_rhs_ratio, checked_common_input_spectrum_ratio,
)

CHECKPOINT_SHA256 = "7d58202ba6a2141acfc172f85b211e476078d8b273bc2c0d22aaddda5887cda9"
U4A_FINAL_CHECKPOINT_SHA256 = "7d7cf81dafd46672be8018cd7dacaa26f2aa21653a47774206005716ef967529"
U4A_WORKER_RESULT_SHA256 = "b59def277ddf3446020d45a5af931d2155b7fb3496ae3245092d10b71575e95f"
U4A_SOURCE_ZIP_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
SOURCE_INDEX_START = 72892
START_IZ = 74411
U4B_START_IZ = 74443
PREFIX_COLUMNS = 1519
U4B_PREFIX_COLUMNS = 1551
MAX_ACCEPTED = 32
MAX_FULL_EVALUATIONS = 128
DLNT_MAX = 5e-4


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _state_ledger(state: dict) -> None:
    if (not all(math.isfinite(float(state[k])) for k in ("xH1s", "xHII", "xHeII", "xe", "Tm_K"))
            or abs(state["xH1s"] + state["xHII"] - 1.0) > 5e-13
            or abs(state["xe"] - state["xHII"] - state["xHeII"]) > 5e-13):
        raise ArithmeticError("RESTART_SPECIES_LEDGER")


def load_reviewed_restart(path: Path) -> dict:
    """Load exactly the reviewed accepted R3Q endpoint and its causal prefix."""
    if _sha(path) != CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_SHA_MISMATCH")
    with np.load(path, allow_pickle=False) as archive:
        required = {"states_json", "steps_json", "virtual_out", "average_virtual", "lyman_out", "final_predictor", "dlna"}
        if not required <= set(archive.files):
            raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_FIELDS")
        states = tuple(json.loads(str(v)) for v in archive["states_json"])
        steps = tuple(json.loads(str(v)) for v in archive["steps_json"])
        virtual = np.array(archive["virtual_out"], copy=True)
        average = np.array(archive["average_virtual"], copy=True)
        lyman = np.array(archive["lyman_out"], copy=True)
        predictor = np.array(archive["final_predictor"], copy=True)
        dlna = float(archive["dlna"])
    if (len(states) != 1512 or len(steps) != 1511 or states[-1].get("iz") != START_IZ
            or dlna != DLNA or virtual.shape != (NVIRT, PREFIX_COLUMNS)
            or average.shape != (NVIRT, PREFIX_COLUMNS) or lyman.shape != (3, PREFIX_COLUMNS)
            or predictor.shape != (2, 2)):
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_SHAPE_OR_INDEX")
    if any(not np.all(np.isfinite(a)) for a in (virtual, average, lyman, predictor)):
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_NONFINITE")
    state = dict(states[-1])
    expected = {"iz": START_IZ, "branch": "H_ONLY", "post_saha": True,
                "xHeII": 0.0}
    if any(state.get(k) != v for k, v in expected.items()):
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_STAGE")
    if (state["xe"] != state["xHII"] or state["xHII"] != .997938519574773
            or state["xH1s"] != .002061480425227018
            or state["Tm_K"] != 4494.45276699142):
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_STATE")
    tail = tuple(float(x) for x in predictor[1])
    if tail != (-.2148617237085924, -.06954421574831805):
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_RHS_TAIL")
    if [s.get("input_iz") for s in steps[-2:]] != [74409, 74410]:
        raise ValueError("REVIEWED_H4_U4A_CHECKPOINT_RHS_INDICES")
    _state_ledger(state)
    return {"state": state, "rhs_tail": tail, "virtual_out": virtual,
            "average_virtual": average, "lyman_out": lyman,
            "final_predictor": predictor}


def load_u4b_restart(final_checkpoint: Path, accepted_dir: Path) -> dict:
    """Reconstruct U4B only from the frozen U4A final checkpoint and append streams."""
    if _sha(final_checkpoint) != U4A_FINAL_CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_U4A_FINAL_CHECKPOINT_SHA_MISMATCH")
    import json
    with np.load(final_checkpoint, allow_pickle=False) as archive:
        required = {"states_json", "steps_json", "virtual_out", "average_virtual",
                    "lyman_out", "final_predictor", "dlna", "rei_activation"}
        if not required <= set(archive.files):
            raise ValueError("U4B_FINAL_CHECKPOINT_FIELDS")
        states = [json.loads(str(v)) for v in archive["states_json"]]
        steps = [json.loads(str(v)) for v in archive["steps_json"]]
        virtual = np.array(archive["virtual_out"], copy=True)
        average = np.array(archive["average_virtual"], copy=True)
        lyman = np.array(archive["lyman_out"], copy=True)
        predictor = np.array(archive["final_predictor"], copy=True)
        dlna = float(archive["dlna"])
        rei_activation = bool(archive["rei_activation"])
    if (len(states) != 33 or len(steps) != 32 or states[-1].get("iz") != U4B_START_IZ
            or dlna != DLNA or rei_activation or virtual.shape != (NVIRT, U4B_PREFIX_COLUMNS)
            or average.shape != virtual.shape or lyman.shape != (3, U4B_PREFIX_COLUMNS)
            or predictor.shape != (2, 2) or not np.all(np.isfinite(predictor))):
        raise ValueError("U4B_FINAL_CHECKPOINT_SHAPE_OR_INDEX")
    state = dict(states[-1])
    if (state.get("branch") != "H_ONLY" or state.get("xHeII") != 0.0
            or state.get("post_saha") is not True or state.get("xe") != state.get("xHII")
            or not math.isfinite(float(state.get("Tm_K", math.nan)))):
        raise ValueError("U4B_FINAL_CHECKPOINT_STAGE_OR_STATE")
    if ([s.get("input_iz") for s in steps] != list(range(START_IZ, U4B_START_IZ))
            or [s.get("output_iz") for s in steps] != list(range(START_IZ + 1, U4B_START_IZ + 1))
            or [s.get("photon_col") for s in steps] != list(range(PREFIX_COLUMNS, U4B_PREFIX_COLUMNS))):
        raise ValueError("U4B_ACCEPTED_OWNERSHIP_GAP_OR_DUPLICATE")
    if _sha(accepted_dir / "accepted.jsonl") != "4978241e17bdc8c67c0020ba95f8ea9f686ba8b680d48aa9b5f213a51f7f035d":
        raise ValueError("U4B_ACCEPTED_JSONL_SHA_MISMATCH")
    if _sha(accepted_dir / "RESULT.json") != U4A_WORKER_RESULT_SHA256:
        raise ValueError("U4B_WORKER_RESULT_SHA_MISMATCH")
    with (accepted_dir / "RESULT.json").open(encoding="utf-8") as stream:
        worker_result = json.load(stream)
    if (worker_result.get("source_zip_sha256") != U4A_SOURCE_ZIP_SHA256
            or worker_result.get("accepted_end_global_index") != U4B_START_IZ
            or worker_result.get("status") != "PASS_SCOPED_U4A_RESTART"
            or worker_result.get("accepted_artifacts", {}).get("final_checkpoint.npz") != U4A_FINAL_CHECKPOINT_SHA256):
        raise ValueError("U4B_SOURCE_OR_RESULT_BINDING_MISMATCH")
    with (accepted_dir / "MANIFEST.json").open(encoding="utf-8") as stream:
        manifest = json.load(stream)
    rows = [json.loads(line) for line in (accepted_dir / "accepted.jsonl").read_text().splitlines()]
    if len(rows) != 32:
        raise ValueError("U4B_ACCEPTED_JSONL_ROW_COUNT")
    for i, row in enumerate(rows):
        if row.get("state") != states[i + 1] or row.get("step") != steps[i]:
            raise ValueError("U4B_ACCEPTED_JSONL_CHECKPOINT_MISMATCH")
    append_specs = (("accepted_virtual_f64le.bin", virtual, NVIRT),
                    ("accepted_average_f64le.bin", average, NVIRT),
                    ("accepted_lyman_f64le.bin", lyman, 3))
    for name, whole, lanes in append_specs:
        raw = (accepted_dir / name).read_bytes()
        if manifest.get(name) != hashlib.sha256(raw).hexdigest():
            raise ValueError("U4B_ACCEPTED_STREAM_MANIFEST_MISMATCH:" + name)
        if len(raw) != lanes * 32 * 8:
            raise ValueError("U4B_APPEND_STREAM_LENGTH:" + name)
        # Accepted output is appended one FULL evaluation at a time, hence
        # step-major [accepted_step, lane] rather than checkpoint [lane, col].
        appended = np.frombuffer(raw, dtype="<f8").reshape(32, lanes).T
        if not np.array_equal(whole[:, PREFIX_COLUMNS:], appended):
            raise ValueError("U4B_APPEND_STREAM_MISMATCH:" + name)
        if not np.all(np.isfinite(whole)):
            raise ValueError("U4B_HISTORY_NONFINITE:" + name)
    if [s.get("input_iz") for s in steps[-2:]] != [74441, 74442]:
        raise ValueError("U4B_PREDICTOR_INPUT_INDEX")
    _state_ledger(state)
    tail = tuple(float(v) for v in predictor[1])
    rhs = tuple(float(s["hydrogen_rhs"]) for s in steps[-2:])
    if tail != rhs:
        raise ValueError("U4B_PREDICTOR_TAIL_MISMATCH")
    return {"state": state, "rhs_tail": tail, "virtual_out": virtual,
            "average_virtual": average, "lyman_out": lyman,
            "final_predictor": predictor, "accepted_steps": len(steps),
            "source_index_start": SOURCE_INDEX_START, "run_start_iz": U4B_START_IZ,
            "restart_contract": "R3T_U4B_FROM_U4A_FINAL_V1"}


def original_rt_stop_index(c: QuarterStartCosmology) -> int:
    """Original ``rec_set_derived_params`` RT stop translated on the h/4 clock."""
    z, pion = 900.0, 1.0
    while pion > .01 and z > 0.0:
        tr = 8.617343e-5*c.T0_K*(1.+z)/c.fsR/c.fsR/c.meR
        nh = 1.e-6*c.nH0_m3*(1.+z)**3
        rl = 4.662899067555897e15*(c.fsR*c.fsR*c.meR)**3*c.hubble_s(z)/nh
        t4 = tr/(8.617343e-5*1.e4)
        alpha = (c.fsR/c.meR)**2*4.309e-13*t4**(-.6166)/(1.+.6703*t4**.5300)
        beta4 = 3.016103031869581e21*(c.fsR*c.meR)**3*tr*math.sqrt(tr)*math.exp(-.25*13.598286071938324/tr)*alpha
        pion = beta4/(3.*rl + 8.2206*c.fsR**8*c.meR + beta4)
        z -= 10.
    nzrt = math.floor(2. + math.log(8001./(1.+z))/DLNA) - c.izH0
    return c.izH0 + nzrt


@dataclass(frozen=True)
class U4AResult:
    states: tuple[dict, ...]
    steps: tuple[dict, ...]
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    final_predictor: np.ndarray
    full_evaluations: int
    status: str
    rt_stop_iz: int
    run_start_iz: int = START_IZ
    restart_contract: str = "R3T_U4A_74411_V1"


def restart_checkpoint(result: U4AResult) -> dict:
    """Make an in-memory continuation input from accepted output only."""
    if not result.steps:
        raise ValueError("EMPTY_RESTART_RESULT")
    return {"state": dict(result.states[-1]), "rhs_tail": tuple(result.final_predictor[1]),
            "virtual_out": np.array(result.virtual_out, copy=True),
            "average_virtual": np.array(result.average_virtual, copy=True),
            "lyman_out": np.array(result.lyman_out, copy=True),
            "final_predictor": np.array(result.final_predictor, copy=True),
            "run_start_iz": getattr(result, "run_start_iz", START_IZ),
            "restart_contract": getattr(result, "restart_contract", "R3T_U4A_74411_V1")}


def integrate_u4a(checkpoint: dict, c: QuarterStartCosmology, source, *,
                  accepted_steps: int = MAX_ACCEPTED, max_full_evaluations: int = MAX_FULL_EVALUATIONS,
                  observer: Callable | None = None, on_accept: Callable | None = None) -> U4AResult:
    if type(accepted_steps) is not int or not 1 <= accepted_steps <= MAX_ACCEPTED:
        raise ValueError("ACCEPTED_STEP_CAP")
    if type(max_full_evaluations) is not int or not 1 <= max_full_evaluations <= MAX_FULL_EVALUATIONS:
        raise ValueError("FULL_EVALUATION_CAP")
    if type(c) is not QuarterStartCosmology or DLNA != 8.49e-5/4 or c.izH0 != SOURCE_INDEX_START:
        raise ValueError("H4_GRID_OR_RT_START")
    state = dict(checkpoint["state"])
    # A split continuation remains one bounded allocation path; a caller
    # cannot turn the 32-step contract into an unbounded chain of restarts.
    run_start = int(checkpoint.get("run_start_iz", START_IZ))
    contract = checkpoint.get("restart_contract", "R3T_U4A_74411_V1")
    if run_start not in (START_IZ, U4B_START_IZ) or (run_start == U4B_START_IZ and contract != "R3T_U4B_FROM_U4A_FINAL_V1"):
        raise ValueError("RESTART_CONTRACT_OR_START_INDEX")
    if int(state.get("iz", -1)) < run_start:
        raise ValueError("RESTART_STATE_BEFORE_CONTRACT_START")
    if state.get("iz", run_start - 1) - run_start + accepted_steps > MAX_ACCEPTED:
        raise ValueError("CUMULATIVE_ACCEPTED_STEP_CAP")
    virtual0, average0, lyman0 = (np.asarray(checkpoint[k], dtype=float) for k in ("virtual_out", "average_virtual", "lyman_out"))
    if (state.get("branch") != "H_ONLY" or state.get("xHeII") != 0.0
            or state.get("iz", -1) < START_IZ or virtual0.shape[0] != NVIRT
            or average0.shape != virtual0.shape or lyman0.shape != (3, virtual0.shape[1])
            or virtual0.shape[1] != state["iz"] - SOURCE_INDEX_START):
        raise ValueError("RESTART_STAGE_OR_HISTORY_OWNERSHIP")
    if any(not np.all(np.isfinite(a)) for a in (virtual0, average0, lyman0)):
        raise ArithmeticError("RESTART_HISTORY_MISSING_OR_UNCOMMITTED")
    if abs(state["z"] - c.redshift(state["iz"])) > 2e-12:
        raise ValueError("RESTART_REDSHIFT")
    _state_ledger(state)
    tail = tuple(float(v) for v in checkpoint["rhs_tail"])
    if len(tail) != 2 or not all(math.isfinite(v) for v in tail):
        raise ValueError("RESTART_PREDICTOR")
    predictor0 = np.asarray(checkpoint.get("final_predictor"), dtype=float)
    if predictor0.shape != (2, 2) or not np.all(np.isfinite(predictor0)):
        raise ValueError("RESTART_HELIUM_PREDICTOR")
    expected_source = make_hmla_source(c, source.table)
    if any(getattr(source, k) != getattr(expected_source, k) for k in ("h", "omega_cb", "omega_r_h2", "omega_de_h2", "omega_b_h2", "y_he_mass", "tcmb0_K")):
        raise ValueError("H4_ATOMIC_SOURCE_COSMOLOGY_MISMATCH")
    n0, n = virtual0.shape[1], virtual0.shape[1] + accepted_steps + 1
    virtual = np.full((NVIRT, n), np.nan); average = np.full((NVIRT, n), np.nan); lyman = np.full((3, n), np.nan)
    virtual[:, :n0], average[:, :n0], lyman[:, :n0] = virtual0, average0, lyman0
    table = _canonical_twophoton_table(source.table.archive_path)
    rt_stop = original_rt_stop_index(c)
    evaluations = 0; states = [state]; steps: list[dict] = []; dprev2, dprev = tail

    def rhs(g: int, xh: float, tm: float, *, z_override: float | None = None):
        nonlocal evaluations
        j = g - SOURCE_INDEX_START
        if j < n0 or j >= n or np.any(~np.isfinite(virtual[:, :j])) or np.any(~np.isfinite(lyman[:, :j])):
            raise ArithmeticError(f"UNACCEPTED_PHOTON_HISTORY_READ:{j}")
        if evaluations >= max_full_evaluations:
            raise RuntimeError("FULL_EVALUATION_CAP")
        z = c.redshift(g) if z_override is None else z_override
        incoming = causal_incoming_from_accepted_histories(energies_eV=table.energy_eV,
            virtual_history=virtual[:, :j], lyman_history=lyman[:, :j], z_start=c.redshift(SOURCE_INDEX_START),
            iz=j, z_face=z, dlna=DLNA, shear_q=0.)
        tr = c.T0_K*(1.+z)
        if tm == tr: tm = math.nextafter(tm, 0.)
        out = complete_original_full_atomic(populate_original_full_atomic(source, z=z, xHII=xh, xe=xh,
            Tm_K=tm, incoming_virtual=incoming.virtual_distortion[0], incoming_lyman=incoming.lya_lyb_incoming_distortion[0]))
        evaluations += 1
        if not math.isfinite(out.dxHII_dln_a) or not 0. <= out.normalized_matrix_residual <= 2e-10:
            raise ArithmeticError(f"FULL_SOURCE_OR_SCHUR:{g}")
        if observer is not None: observer(g, z, xh, 0., tm, virtual[:, :j].copy(), lyman[:, :j].copy(), out)
        return out

    for _ in range(accepted_steps):
        s = states[-1]; g = s["iz"]; z = s["z"]; j = g - SOURCE_INDEX_START
        # These native conditions are tested before source evaluation or photon write.
        if not 1. - s["Tm_K"]/c.T0_K/(1.+z) < DLNT_MAX:
            raise RuntimeError(f"HOLD_THERMAL_STAGE_BEFORE_ENDPOINT:{g}")
        if not g < rt_stop:
            raise RuntimeError(f"HOLD_RT_STAGE_BEFORE_ENDPOINT:{g}")
        current = rhs(g, s["xe"], s["Tm_K"])
        virtual[:, j], average[:, j], lyman[:, j] = current.outgoing_virtual, current.average_virtual, current.outgoing_lyman
        zout = c.redshift(g+1)
        if s["post_saha"]:
            zprobe = (1.+z)*math.exp(-DLNA)-1.
            q = saha_xH1s(c, 0., zprobe)
            dq = (1.+zprobe)*(saha_xH1s(c, 0., zprobe-.5)-saha_xH1s(c, 0., zprobe+.5))
            x = 1.-q; tr = c.T0_K*(1.+zprobe); delta = .01*q
            f0 = rhs(g+1, x, tr, z_override=zprobe).dxHII_dln_a
            fp = rhs(g+1, x+delta, tr, z_override=zprobe).dxHII_dln_a
            fm = rhs(g+1, x-delta, tr, z_override=zprobe).dxHII_dln_a
            jac = (fp-fm)/2./delta
            if not math.isfinite(jac) or jac == 0.: raise ArithmeticError(f"POST_SAHA_JACOBIAN:{g+1}")
            x1 = q+(dq+f0)/jac; post_next = abs(x1-q) <= DXHII_MAX; xe = 1.-x1
        else:
            xe = s["xe"] + DLNA*(1.25*current.dxHII_dln_a - .25*dprev2)
            x1 = 1.-xe; post_next = False
        if not math.isfinite(xe) or not 0. <= xe <= 1.: raise ArithmeticError(f"NONPHYSICAL_ACCEPTED_NODE:{g+1}")
        ns = {"iz":g+1, "z":zout, "xH1s":x1, "xHII":1.-x1, "xHeII":0., "xe":xe,
              "Tm_K":tm_steady_K(c, xe, zout, c.hubble_s(zout)), "post_saha":post_next, "branch":"H_ONLY"}
        _state_ledger(ns); states.append(ns)
        steps.append({"input_iz":g, "output_iz":g+1, "branch":"H_ONLY", "hydrogen_rhs":current.dxHII_dln_a,
                      "helium_rhs":math.nan, "schur_residual":current.normalized_matrix_residual, "photon_col":j})
        if on_accept is not None:
            on_accept(dict(ns), dict(steps[-1]), current)
        dprev2, dprev = dprev, current.dxHII_dln_a
        # U4B is an event-bounded continuation. Preserve and stop on its first
        # accepted post-Saha exit; the historical U4A run contract is unchanged.
        if run_start == U4B_START_IZ and not ns["post_saha"]:
            break
    # history.c keeps the helium derivative memory through the H-only stage;
    # it is historical causal state, even though H-only does not update it.
    cols = n0 + len(steps); predictor = np.array([predictor0[0], [dprev2, dprev]])
    status = "POST_SAHA_EXIT_WITHIN_BOUND" if any(not s["post_saha"] for s in states[1:]) else "NO_EVENT_WITHIN_BOUND"
    return U4AResult(tuple(states), tuple(steps), virtual[:, :cols].copy(), average[:, :cols].copy(), lyman[:, :cols].copy(), predictor, evaluations, status, rt_stop, run_start, contract)


def common_input_observer(oracle, source_table, metrics: dict) -> Callable:
    """Return the frozen R3Q/R3R same-h arithmetic check callback."""
    line_ev = np.array((10.198714553953742, 12.087365397278509, 12.748393192442178))
    def observe(j, z, xh, xhe, tm, vh, lh, out):
        local_j = j - SOURCE_INDEX_START
        cs = oracle(local_j, z, xh, xhe, tm, vh, lh)
        r = checked_common_input_rhs_ratio(out.dxHII_dln_a, cs["rhs"], local_j)
        metrics["max_rhs_scaled"] = max(metrics.get("max_rhs_scaled", 0.), r)
        if r > 2e-10: raise ArithmeticError(f"COMMON_INPUT_FULL_RHS_PARITY:j={j}")
        tr = 8.617343e-5*oracle.c.T0_K*(1.+z)
        for name, py, cv, ev in (("virtual", out.outgoing_virtual, cs["virtual"], source_table.energy_eV), ("average", out.average_virtual, cs["average"], source_table.energy_eV), ("lyman", out.outgoing_lyman, cs["lyman"], line_ev)):
            ratio = checked_common_input_spectrum_ratio(py, cv, 1./np.expm1(ev/tr), local_j)
            val = float(np.max(ratio)); metrics[f"max_{name}_tolerance_ratio"] = max(metrics.get(f"max_{name}_tolerance_ratio", 0.), val)
            if val > 1.: raise ArithmeticError(f"COMMON_INPUT_PHOTON_PARITY:j={j}:field={name}")
        metrics["sampled_evaluations"] = metrics.get("sampled_evaluations", 0) + 1
    return observe
