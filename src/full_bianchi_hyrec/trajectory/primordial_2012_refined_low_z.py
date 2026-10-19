"""h/2 continuation of the reviewed R3M U6 boundary to the source z=0 stencil.

The original Oct-2012 history.c equations and stage guards are retained.
No photon arrays are read by this stage.  Python and native-C boundaries
remain separate; their last two RHS values are carried, never reseeded.
The original-h U7/U8 modules and their fixed grid constants stay unchanged.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from .primordial_2012_refined_start import DLNA, HyRec2012Cosmology
from .primordial_2012_low_z_to_end import peebles_rhs_ln_a
from .primordial_2012_thermal_transition import source_thermal_rhs

SOURCE_ZIP_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
U5_CHECKPOINT_SHA256 = "7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b"
# The same immutable producer pins as scripts/compare_r3n_time_grids.py.
R3M_FILES = {
    "python_u6_rt.npz": "5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2",
    "native_oracle_stdout.csv": "57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38",
    "verification.json": "1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b",
}
START_IZ = 58389
SOURCE_NZ = math.floor(2. + math.log(8001.) / DLNA)
END_IZ = SOURCE_NZ - 1
MAX_STEPS = END_IZ - START_IZ
SOURCE_X0 = -math.log(8001.)
HISTORICAL_STATUS = {
    "budget": "CLOSED_HOLD_NOT_RESET",
    "u5_original_h": "HOLD_9_FAIL",
    "u5_h2": "HOLD_8_FAIL",
    "REI_activation": False,
}


def sha256(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def input_hashes(raw: Path, source_zip: Path) -> dict[str, str]:
    paths = {name: Path(raw) / name for name in R3M_FILES}
    paths["source_zip"] = Path(source_zip)
    for key, path in paths.items():
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"R3O_INPUT_REGULAR_FILE_REQUIRED:{key}")
    return {key: sha256(path) for key, path in paths.items()}


def check_input_identity(observed: dict[str, str]) -> None:
    if observed != {**R3M_FILES, "source_zip": SOURCE_ZIP_SHA256}:
        raise ValueError("R3O_REVIEWED_INPUT_HASH_MISMATCH")


@dataclass(frozen=True)
class LowZCheckpoint:
    """Accepted input state; prev=F[n-1], prev2=F[n-2] at state n."""

    iz: int
    xe: float
    Tm_K: float
    hydrogen_prev: float
    hydrogen_prev2: float
    thermal_prev: float
    thermal_prev2: float
    peebles_event_iz: int | None = None
    peebles_event_reason: str | None = None

    def validate(self, c: HyRec2012Cosmology) -> None:
        if c != HyRec2012Cosmology() or DLNA != 4.245e-5 or c.izH0 != 36446:
            raise ValueError("R3O_FROZEN_H2_COSMOLOGY_REQUIRED")
        if type(self.iz) is not int or not START_IZ <= self.iz <= END_IZ:
            raise ValueError("R3O_ACCEPTED_GRID_INDEX")
        values = (self.xe, self.Tm_K, self.hydrogen_prev, self.hydrogen_prev2,
                  self.thermal_prev, self.thermal_prev2)
        if (not all(math.isfinite(x) for x in values) or not 0. < self.xe < 1.
                or not 0. < self.Tm_K <= c.T0_K * (1. + c.redshift(self.iz))):
            raise ValueError("R3O_ACCEPTED_STATE_OR_MEMORY_DOMAIN")
        if self.peebles_event_iz is None:
            if self.peebles_event_reason is not None:
                raise ValueError("R3O_EVENT_PAIR")
        elif (type(self.peebles_event_iz) is not int or
              not START_IZ <= self.peebles_event_iz < self.iz or
              self.peebles_event_reason not in ("TR_MIN", "TM_TR_MIN")):
            raise ValueError("R3O_EVENT_RANGE_OR_REASON")


def source_stage_guard(c: HyRec2012Cosmology, z: float,
                       Tm_K: float) -> tuple[bool, str | None]:
    """history.c:578-579, including multiplication/division ordering."""
    if not (math.isfinite(z) and math.isfinite(Tm_K) and z >= 0. and Tm_K > 0.):
        raise ValueError("R3O_GUARD_DOMAIN")
    if not (8.617343e-5 * c.T0_K * (1. + z) / c.fsR / c.fsR / c.meR > .004):
        return False, "TR_MIN"
    if not (Tm_K / c.T0_K / (1. + z) > .1):
        return False, "TM_TR_MIN"
    return True, None


def source_z0_cubic(tail: np.ndarray) -> dict:
    """Global source end clamp: use the last four states, including z<0.

    The negative-z accepted state is an output-only interpolation node; an
    RHS is never evaluated there.  The clamped fraction must not be clipped.
    """
    values = np.asarray(tail, dtype=np.float64)
    if values.shape != (4,) or not np.all(np.isfinite(values)):
        raise ValueError("R3O_Z0_FOUR_FINITE_SOURCE_STATES_REQUIRED")
    raw = (0. - SOURCE_X0) / DLNA
    ix = min(max(math.floor(raw), 1), SOURCE_NZ - 3)
    frac = raw - ix
    y0, y1, y2, y3 = map(float, values)
    value = (-y0 * frac * (1. - frac) * (2. - frac) / 6.
             + y1 * (1. + frac) * (1. - frac) * (2. - frac) / 2.
             + y2 * (1. + frac) * frac * (2. - frac) / 2.
             - y3 * (1. + frac) * frac * (1. - frac) / 6.)
    if not math.isfinite(value):
        raise ArithmeticError("R3O_Z0_INTERPOLATION_NONFINITE")
    return {"value": value, "global_iz": list(range(ix - 1, ix + 3)),
            "raw_index": raw, "clamped_index": ix, "fraction": frac}


def _native_u6_terminal(path: Path, c: HyRec2012Cosmology) -> LowZCheckpoint:
    """Read actual C STEP records, without substituting Python values."""
    previous = current = None
    count = 0
    base = end = params = None
    with Path(path).open() as stream:
        for line in stream:
            if line.startswith("PARAM,"):
                if params is not None:
                    raise ValueError("R3O_NATIVE_DUPLICATE_PARAM")
                params = line.strip().split(",")[1:]
            elif line.startswith("BASE,"):
                if base is not None:
                    raise ValueError("R3O_NATIVE_DUPLICATE_BASE")
                base = line.strip().split(",")[1:]
            elif line.startswith("STEP,"):
                p = line.strip().split(",")[1:]
                if (len(p) != 12 or int(p[0]) != count or
                        int(p[1]) != 53180 + count or p[9:11] != ["1", "0"]):
                    raise ValueError("R3O_NATIVE_U6_STEP_ORDER_OR_STAGE")
                previous, current = current, p
                count += 1
            elif line.startswith("END,"):
                if end is not None:
                    raise ValueError("R3O_NATIVE_DUPLICATE_END")
                end = line.strip().split(",")[1:]
    if (params != ["36446", "21943", "58389"] or base is None or
            len(base) != 8 or int(base[0]) != 53179 or count != 5210 or
            previous is None or current is None or
            end != ["RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION", "53177", "5212", "5210"]):
        raise ValueError("R3O_NATIVE_U6_BOUNDARY_RECORDS")
    if (int(current[1]) != START_IZ or float(current[5]) != 0. or
            abs(float(current[2]) - c.redshift(START_IZ)) > 2.e-12):
        raise ValueError("R3O_NATIVE_U6_TERMINAL_STATE")
    result = LowZCheckpoint(START_IZ, float(current[6]), float(current[7]),
                           float(current[8]), float(previous[8]),
                           float(current[11]), float(previous[11]))
    result.validate(c)
    return result


def load_reviewed_u6_boundary(raw: Path, source_zip: Path) -> dict:
    """Pinned producer input chain, independent Python/C state and RHS tails.

    Only JSON state/step arrays are materialized from the NPZ.  Spectral
    arrays are covered by the whole-file hash and remain unused here.
    Caller must also check these identities after execution (including fail).
    """
    before = input_hashes(raw, source_zip)
    check_input_identity(before)
    receipt = json.loads((Path(raw) / "verification.json").read_text())
    if (receipt.get("source_zip_sha256") != SOURCE_ZIP_SHA256 or
            receipt.get("checkpoint_sha256") != U5_CHECKPOINT_SHA256 or
            receipt.get("first_failure") is not None or
            receipt.get("status") != "PASS_PENDING_INDEPENDENT_REVIEW" or
            receipt.get("python_result") != {
                "full_evaluations": 5210, "rt_stop_iz": START_IZ,
                "status": "RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION", "steps": 5210} or
            receipt.get("same_h_parity", {}).get("status") != "PASS_PENDING_REVIEW"):
        raise ValueError("R3O_REVIEWED_U6_RECEIPT_CONTRACT")
    with np.load(Path(raw) / "python_u6_rt.npz", allow_pickle=False) as archive:
        states = [json.loads(str(s)) for s in archive["states_json"]]
        steps = [json.loads(str(s)) for s in archive["steps_json"]]
    if (len(states) != 5211 or len(steps) != 5210 or
            [s["iz"] for s in states] != list(range(53179, START_IZ + 1)) or
            [s["input_iz"] for s in steps] != list(range(53179, START_IZ)) or
            [s["output_iz"] for s in steps] != list(range(53180, START_IZ + 1))):
        raise ValueError("R3O_PYTHON_U6_STATE_STEP_ORDER")
    c = HyRec2012Cosmology()
    s = states[-1]
    if (s != receipt["last_accepted"]["state"] or
            steps[-1] != receipt["last_accepted"]["step"] or
            s["xHeII"] != 0. or s["post_saha"] is not False or
            s["branch"] != "H_ONLY" or s["xHII"] != s["xe"] or
            s["xH1s"] != 1. - s["xe"] or
            abs(s["z"] - c.redshift(START_IZ)) > 2.e-12 or
            not all(t["coupled"] is True and t["branch"] == "H_ONLY" for t in steps[-2:])):
        raise ValueError("R3O_PYTHON_U6_STOP_STAGE")
    py = LowZCheckpoint(START_IZ, s["xe"], s["Tm_K"],
                        steps[-1]["hydrogen_rhs"], steps[-2]["hydrogen_rhs"],
                        steps[-1]["thermal_rhs"], steps[-2]["thermal_rhs"])
    py.validate(c)
    native = _native_u6_terminal(Path(raw) / "native_oracle_stdout.csv", c)
    if input_hashes(raw, source_zip) != before:
        raise ValueError("R3O_INPUT_MUTATION_DURING_LOAD")
    if not source_stage_guard(c, c.redshift(START_IZ), py.Tm_K)[0]:
        raise ValueError("R3O_U6_EMLA_FIRST_INPUT_GUARD")
    return {"python": py, "native": native, "inputs_sha256": before,
            "parent_review": "PR107 REVIEW_PASS_SAME_H_ONLY (reused)",
            "producer_status_preserved": receipt["status"],
            "historical_status": dict(HISTORICAL_STATUS)}


def continue_refined_low_z(
    checkpoint: LowZCheckpoint,
    c: HyRec2012Cosmology,
    emla_source,
    *,
    max_steps: int,
    before_attempt: Callable | None = None,
    on_accept: Callable | None = None,
    on_checkpoint: Callable | None = None,
    checkpoint_interval: int = 4096,
) -> dict:
    """Advance original EMLA/Peebles and thermal equations on h2.

    on_accept(input, accepted, step) can compare an independent native lane.
    Its failure preserves the already accepted Python state, without treating
    the failed comparison as an admission.  No endpoint interpolation occurs
    on a bounded/incomplete run.  Reaching the final source index with fewer
    than four retained states reports an incomplete interpolation stencil.
    """
    checkpoint.validate(c)
    if (type(max_steps) is not int or not 1 <= max_steps <= END_IZ - checkpoint.iz or
            type(checkpoint_interval) is not int or checkpoint_interval < 1):
        raise ValueError("R3O_STEP_OR_CHECKPOINT_CAP")
    if not callable(getattr(emla_source, "hydrogen_rhs_ln_a", None)):
        raise ValueError("R3O_EMLA_SOURCE_REQUIRED")
    accepted = checkpoint
    states = [checkpoint]
    steps = []

    def emit(phase: str, failure=None):
        if on_checkpoint is not None:
            on_checkpoint({"phase": phase, "accepted_steps": len(steps),
                           "checkpoint": asdict(accepted), "failure": failure,
                           "state_tail": [asdict(s) for s in states[-4:]]})

    emit("START")
    try:
        for _ in range(max_steps):
            current = accepted
            g = current.iz
            z = c.redshift(g)
            if not START_IZ <= g < END_IZ or z < 0.:
                raise ValueError("R3O_RHS_GRID_OR_RT_STAGE")
            if before_attempt is not None:
                before_attempt(current)
            guard, reason = source_stage_guard(c, z, current.Tm_K)
            event = current.peebles_event_iz
            event_reason = current.peebles_event_reason
            if event is None and not guard:
                event, event_reason = g, reason
            model = "PEEBLES" if event is not None else "EMLA2s2p"
            if model == "EMLA2s2p":
                dh = float(emla_source.hydrogen_rhs_ln_a(
                    z=z, x_HII=current.xe, x_e=current.xe, Tm_K=current.Tm_K,
                    fsR=c.fsR, meR=c.meR))
            else:
                dh = peebles_rhs_ln_a(c, z, current.xe, current.Tm_K)
            dt = float(source_thermal_rhs(c, current.xe, current.Tm_K, z))
            if not (math.isfinite(dh) and math.isfinite(dt)):
                raise ArithmeticError("R3O_NONFINITE_SOURCE_RHS")
            candidate = LowZCheckpoint(
                g + 1,
                current.xe + DLNA * (1.25 * dh - .25 * current.hydrogen_prev2),
                current.Tm_K + DLNA * (1.25 * dt - .25 * current.thermal_prev2),
                dh, current.hydrogen_prev, dt, current.thermal_prev,
                event, event_reason,
            )
            candidate.validate(c)
            step = {"input_iz": g, "output_iz": g + 1, "model": model,
                    "hydrogen_rhs": dh, "thermal_rhs": dt,
                    "guard": guard, "guard_reason": reason}
            accepted = candidate
            states.append(accepted)
            steps.append(step)
            if on_accept is not None:
                on_accept(current, accepted, step)
            if len(steps) in (1, 2) or len(steps) % checkpoint_interval == 0 or event == g:
                emit("ACCEPTED")
        complete = accepted.iz == END_IZ
        emit("STOP")
    except BaseException as exc:
        emit("EXCEPTION", {"type": type(exc).__name__, "message": str(exc)})
        raise
    status = "BOUNDED_LOW_Z_COMPLETE"
    if complete:
        status = ("STOP_AT_SOURCE_Z0_CUBIC_STENCIL" if len(states) >= 4
                  else "SOURCE_END_REACHED_INCOMPLETE_Z0_STENCIL")
    return {
        "status": status,
        "accepted_steps": len(steps), "checkpoint": accepted,
        "global_iz": np.array([s.iz for s in states], dtype=np.int64),
        "redshift": np.array([c.redshift(s.iz) for s in states]),
        "xe": np.array([s.xe for s in states]),
        "Tm_K": np.array([s.Tm_K for s in states]),
        "hydrogen_rhs": np.array([s["hydrogen_rhs"] for s in steps]),
        "thermal_rhs": np.array([s["thermal_rhs"] for s in steps]),
        "model": np.array([s["model"] for s in steps], dtype="U8"),
        "z0": ({k: source_z0_cubic(np.array([getattr(s, k) for s in states[-4:]]))
                for k in ("xe", "Tm_K")} if complete and len(states) >= 4 else None),
        "historical_status": dict(HISTORICAL_STATUS),
    }
