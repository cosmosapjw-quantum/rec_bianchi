"""Saved-history diagnostics for the unchanged R3I-CONVERGENCE-v1 contract.

This module does not integrate, seed, resample a checkpoint, or admit physics.
Original HyRec's four-point *output* interpolation is separate from its
two-neighbor causal photon interpolation. Missing stencils are never filled.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

import numpy as np

H0 = 8.49e-5
X0 = -math.log(8001.)
UNIT_ROUNDOFF = 2.**-53
FIELD_FLOORS = {"xe": 1.e-4, "Tm_K": 1.}
REPORT_Z = (1563., 836., 1100., 20., 0.)
WINDOWS_Z = {"H_transition": (1553., 1573.), "thermal_transition": (826., 846.)}
SOURCE_ZIP_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"


def grid_step(level: int) -> float:
    if type(level) is not int or level not in (0, 1, 2):
        raise ValueError("GRID_LEVEL_MUST_BE_0_1_2")
    return H0 / 2**level


def grid_size(level: int) -> int:
    return math.floor(2. + math.log(8001.) / grid_step(level))


def cubic_stencil(level: int, x: float) -> tuple[np.ndarray, float, np.ndarray]:
    """Use the original GLOBAL grid clamp, never a partial-history clamp."""
    h, n = grid_step(level), grid_size(level)
    if not math.isfinite(x) or not X0 <= x <= X0 + h*(n-1):
        raise ValueError("INTERPOLATION_OUTSIDE_SOURCE_GRID")
    raw = (x-X0)/h
    i = min(max(math.floor(raw), 1), n-3)
    f = raw-i
    w = np.array((-f*(1.-f)*(2.-f)/6.,
                  (1.+f)*(1.-f)*(2.-f)/2.,
                  (1.+f)*f*(2.-f)/2.,
                  -(1.+f)*f*(1.-f)/6.), dtype=float)
    return np.arange(i-1, i+3, dtype=np.int64), f, w


def original_cubic(values, fraction: float) -> float:
    """hyrectools.c::rec_interp1d term order, including the end stencil."""
    y = np.asarray(values, dtype=float)
    if y.shape != (4,) or not np.all(np.isfinite(y)) or not math.isfinite(fraction):
        raise ValueError("CUBIC_NONFINITE_OR_SHAPE")
    y0, y1, y2, y3 = map(float, y)
    f = float(fraction)
    value = (-y0*f*(1.-f)*(2.-f)/6.
             +y1*(1.+f)*(1.-f)*(2.-f)/2.
             +y2*(1.+f)*f*(2.-f)/2.
             -y3*(1.+f)*f*(1.-f)/6.)
    if not math.isfinite(value):
        raise ValueError("CUBIC_OVERFLOW")
    return value


@dataclass(frozen=True)
class GridHistory:
    level: int
    global_iz: np.ndarray
    values: dict[str, np.ndarray]
    parity_abs: dict[str, np.ndarray | None]
    quantization_abs: dict[str, np.ndarray | None]
    regime: np.ndarray
    boundary_lna: tuple[float, ...]
    provenance: dict

    def __post_init__(self):
        grid_step(self.level)
        g = np.asarray(self.global_iz)
        if (g.ndim != 1 or g.size < 4 or g.dtype.kind not in "iu" or
                g.dtype.kind == "b" or g[0] < 0 or g[-1] >= grid_size(self.level) or
                not np.array_equal(g, np.arange(int(g[0]), int(g[0])+g.size))):
            raise ValueError("HISTORY_CONTIGUOUS_GLOBAL_GRID_REQUIRED")
        g = np.array(g, dtype=np.int64, copy=True)
        vals, parity, quant = {}, {}, {}
        if set(self.values) != set(FIELD_FLOORS):
            raise ValueError("HISTORY_FIELDS")
        for key in FIELD_FLOORS:
            v = np.array(self.values[key], dtype=float, copy=True)
            if v.shape != g.shape or not np.all(np.isfinite(v)) or np.any(v <= 0.):
                raise ValueError("HISTORY_NONFINITE_OR_PHYSICAL_DOMAIN")
            vals[key] = v
            for source, target in ((self.parity_abs, parity), (self.quantization_abs, quant)):
                a = source.get(key)
                if a is None:
                    target[key] = None
                else:
                    a = np.array(a, dtype=float, copy=True)
                    if a.shape != g.shape or not np.all(np.isfinite(a)) or np.any(a < 0.):
                        raise ValueError("UNCERTAINTY_NONFINITE_NEGATIVE_OR_SHAPE")
                    target[key] = a
        regimes = np.asarray(self.regime)
        if regimes.shape != g.shape or regimes.dtype.kind not in "US":
            raise ValueError("REGIME_LABELS_REQUIRED")
        # Validate decoded labels: str(b'') is nonempty but decodes to ''.
        regimes = np.char.strip(np.array(regimes, dtype=str, copy=True))
        if any(not str(s) for s in regimes):
            raise ValueError("REGIME_LABELS_REQUIRED")
        b = tuple(float(x) for x in self.boundary_lna)
        if any(not math.isfinite(x) or not X0 <= x <= 0. for x in b):
            raise ValueError("BOUNDARY_LNA_DOMAIN")
        p = dict(self.provenance)
        if p.get("kind") not in ("independent_python", "manufactured"):
            raise ValueError("INDEPENDENT_PYTHON_OR_EXPLICIT_MANUFACTURED_REQUIRED")
        if p.get("checkpoint_resampled") is not False:
            raise ValueError("RESAMPLED_OR_UNKNOWN_CHECKPOINT_REJECTED")
        if p.get("q") != 0 or p.get("REI_activation") is not False:
            raise ValueError("Q0_REI_FALSE_REQUIRED")
        if p.get("source_zip_sha256") != SOURCE_ZIP_SHA256:
            raise ValueError("ORIGINAL_SOURCE_IDENTITY")
        if not isinstance(p.get("physics_id"), str) or not p["physics_id"]:
            raise ValueError("PHYSICS_ID_REQUIRED")
        coverage = p.get("boundary_coverage_lna")
        if coverage is not None:
            coverage = np.asarray(coverage, dtype=float)
            if (coverage.shape != (2,) or not np.all(np.isfinite(coverage)) or
                    not X0 <= coverage[0] < coverage[1] <= 0.):
                raise ValueError("BOUNDARY_COVERAGE_DOMAIN")
            p["boundary_coverage_lna"] = coverage.tolist()
        if p["kind"] == "independent_python":
            physics = p.get("physics_contract")
            if (not isinstance(physics, dict) or
                    hashlib.sha256(json.dumps(physics, sort_keys=True).encode()).hexdigest() != p["physics_id"] or
                    physics.get("source_zip_sha256") != SOURCE_ZIP_SHA256 or
                    physics.get("atomic_thermal") != "original_oct2012" or
                    physics.get("stage_rule") != "original_oct2012" or
                    physics.get("predictor") != "current_and_prev2" or
                    physics.get("q") != 0 or physics.get("REI_activation") is not False or
                    not isinstance(physics.get("cosmology"), dict) or
                    not re.fullmatch(r"[0-9a-f]{40}", str(p.get("source_commit", "")))):
                raise ValueError("PHYSICAL_PROVENANCE_DIGEST_OR_OPERATOR")
        for a in [g, *vals.values(), *parity.values(), *quant.values()]:
            if a is not None:
                a.setflags(write=False)
        regimes = np.array(regimes, dtype=str, copy=True)
        regimes.setflags(write=False)
        for key, value in (("global_iz", g), ("values", vals), ("parity_abs", parity),
                           ("quantization_abs", quant), ("regime", regimes),
                           ("boundary_lna", b), ("provenance", p)):
            object.__setattr__(self, key, value)

    def sample(self, x: float) -> dict | None:
        indices, fraction, weights = cubic_stencil(self.level, x)
        local = indices-int(self.global_iz[0])
        if local[0] < 0 or local[-1] >= self.global_iz.size:
            return None
        fields = {}
        for key in FIELD_FLOORS:
            fields[key] = {"value": original_cubic(self.values[key][local], fraction)}
            for name, source in (("parity_abs", self.parity_abs),
                                 ("quantization_abs", self.quantization_abs)):
                a = source[key]
                # Signed cubic weights must never cancel an uncertainty bound.
                bound = None if a is None else float(np.sum(np.abs(weights)*a[local]))
                if bound is not None and not math.isfinite(bound):
                    raise ValueError("PROPAGATED_UNCERTAINTY_OVERFLOW")
                fields[key][name] = bound
        labels = set(map(str, self.regime[local]))
        return {"fields": fields, "regime": next(iter(labels)) if len(labels) == 1 else "MIXED_STENCIL",
                "stencil": indices.tolist(), "fraction": fraction,
                "clamped_stencil": not 0. <= fraction <= 1.,
                "lebesgue_factor": float(np.sum(np.abs(weights)))}


def signed_triplet(values, parity_abs, quantization_abs, *, scale_floor: float,
                   boundary: bool = False, boundary_coverage_known: bool = True) -> dict:
    """Original signed differences and gates; p is descriptive, not an order proof."""
    v = np.asarray(values, dtype=float)
    if (v.shape != (3,) or not np.all(np.isfinite(v)) or
            not math.isfinite(scale_floor) or scale_floor <= 0.):
        raise ValueError("TRIPLET_VALUES_OR_SCALE")
    d01, d12 = float(v[0]-v[1]), float(v[1]-v[2])
    scale = max(abs(float(v[2])), scale_floor)
    if not all(math.isfinite(t) for t in (d01, d12, scale)):
        raise ValueError("TRIPLET_OVERFLOW")
    out = {"D01": d01, "D12": d12, "scale": scale,
           "scaled_D01": d01/scale, "scaled_D12": d12/scale,
           "floor01": None, "floor12": None, "p_observed": None}
    missing = any(t is None for t in (*parity_abs, *quantization_abs))
    if missing:
        out["classification"] = "UNCERTAINTY_MISSING"
        return out
    e, q = (np.asarray(t, dtype=float) for t in (parity_abs, quantization_abs))
    if (e.shape != (3,) or q.shape != (3,) or
            not np.all(np.isfinite(e)) or not np.all(np.isfinite(q)) or
            np.any(e < 0.) or np.any(q < 0.)):
        raise ValueError("TRIPLET_UNCERTAINTY")
    thresholds = []
    for a, b in ((0, 1), (1, 2)):
        threshold = max(32.*UNIT_ROUNDOFF*max(abs(v[a]), abs(v[b]), scale_floor),
                        10.*float(e[a]+e[b]), 10.*float(q[a]+q[b]))
        if not math.isfinite(threshold):
            raise ValueError("TRIPLET_FLOOR_OVERFLOW")
        thresholds.append(threshold)
    out["floor01"], out["floor12"] = thresholds
    if boundary:
        status = "STAGE_BOUNDARY"
    elif not boundary_coverage_known:
        status = "BOUNDARY_COVERAGE_UNKNOWN"
    elif abs(d01) <= thresholds[0] or abs(d12) <= thresholds[1]:
        status = "ROUNDOFF_UNRESOLVED"
    elif (d01 > 0.) != (d12 > 0.):
        status = "NONMONOTONE"
    else:
        status = "RESOLVED_SAME_SIGN"
        # Difference of logs also handles extreme finite ratios without overflow.
        out["p_observed"] = math.log2(abs(d01))-math.log2(abs(d12))
    out["classification"] = status
    return out


def default_targets() -> np.ndarray:
    """Coarse source ln(a) nodes, z=0, named report points and window endpoints."""
    n = math.floor(-X0/H0)
    x = X0+H0*np.arange(n+1, dtype=float)
    extra_z = list(REPORT_Z)+[z for w in WINDOWS_Z.values() for z in w]
    return np.unique(np.r_[x, [-math.log1p(z) for z in extra_z]])


def boundary_interval(x: float) -> tuple[float, float]:
    """Inclusive +/-4h, allowing indexed-coordinate arithmetic error.

    The error scale uses the terms in X0+g*h, not ulps of the small result:
    cancellation near ln(a)=0 makes result ulps inadequate. Two conservative
    gamma_3 envelopes cover the compared coordinates and interval arithmetic.
    Only diagnostic membership is padded; no grid or physical stage is moved.
    """
    radius = 4.*H0
    gamma3 = 3.*UNIT_ROUNDOFF/(1.-3.*UNIT_ROUNDOFF)
    padding = 2.*gamma3*(abs(X0)+abs(x-X0)+radius)
    return (math.nextafter(x-radius-padding, -math.inf),
            math.nextafter(x+radius+padding, math.inf))


def compare_histories(histories: list[GridHistory], targets=None) -> dict:
    levels = [g.level for g in histories]
    if not histories or len(levels) != len(set(levels)):
        raise ValueError("EMPTY_OR_DUPLICATE_GRID_LEVEL")
    if len({g.provenance["physics_id"] for g in histories}) != 1:
        raise ValueError("PHYSICS_IDENTITY_MISMATCH")
    if len({g.provenance["kind"] for g in histories}) != 1:
        raise ValueError("MIXED_MANUFACTURED_AND_PHYSICAL")
    x = default_targets() if targets is None else np.asarray(targets, dtype=float)
    if (x.ndim != 1 or not x.size or not np.all(np.isfinite(x)) or
            np.any(np.diff(x) <= 0.) or x[0] < X0 or x[-1] > 0.):
        raise ValueError("TARGET_DOMAIN_OR_ORDER")
    out = {"schema": "rec.r3n.convergence-diagnostics.v1", "contract": "R3I-CONVERGENCE-v1",
           "levels_present": sorted(levels), "levels_missing": sorted(set((0, 1, 2))-set(levels)),
           "input_domains": {str(g.level): {"global_iz": [int(g.global_iz[0]), int(g.global_iz[-1])],
                "z_range": [math.exp(-(X0+grid_step(g.level)*int(g.global_iz[-1])))-1.,
                            math.exp(-(X0+grid_step(g.level)*int(g.global_iz[0])))-1.],
                "nodes": int(g.global_iz.size), "provenance": g.provenance} for g in histories},
           "scientific_admission": "NOT_ESTABLISHED_BY_DIAGNOSTIC", "global_order_claim": False,
           "preserve": {"U5_h": "HOLD_9_FAIL", "U5_h2": "HOLD_8_FAIL",
                        "historical_budget": "CLOSED_HOLD_NOT_RESET", "REI_activation": False},
           "rows": [], "regions": {}}
    if out["levels_missing"]:
        out.update(status="INSUFFICIENT_LEVELS", global_coverage=False,
                   reason="Independent h/h2/h4 histories are required; no surrogate levels were created.")
        return out
    hs = sorted(histories, key=lambda g: g.level)
    boundaries = [b for g in hs for b in g.boundary_lna]
    for g in hs:
        changes = np.flatnonzero(g.regime[1:] != g.regime[:-1])+1
        boundaries.extend(X0+grid_step(g.level)*int(g.global_iz[i]) for i in changes)
    windows = [boundary_interval(b) for b in boundaries]
    missing = 0
    for xx in x:
        ss = [g.sample(float(xx)) for g in hs]
        if any(s is None for s in ss):
            missing += 1
            continue
        labels = {s["regime"] for s in ss}
        regime = next(iter(labels)) if len(labels) == 1 else "MISMATCHED_REGIME"
        near = (regime in ("MIXED_STENCIL", "MISMATCHED_REGIME", "UNKNOWN") or
                any(lo <= float(xx) <= hi for lo, hi in windows))
        wanted_lo, wanted_hi = boundary_interval(float(xx))
        wanted_lo, wanted_hi = max(X0, wanted_lo), min(0., wanted_hi)
        boundary_known = all(g.provenance.get("boundary_coverage_lna") is not None and
            g.provenance["boundary_coverage_lna"][0] <= wanted_lo and
            g.provenance["boundary_coverage_lna"][1] >= wanted_hi for g in hs)
        fields = {}
        for key, floor in FIELD_FLOORS.items():
            fields[key] = signed_triplet([s["fields"][key]["value"] for s in ss],
                [s["fields"][key]["parity_abs"] for s in ss],
                [s["fields"][key]["quantization_abs"] for s in ss],
                scale_floor=floor, boundary=near, boundary_coverage_known=boundary_known)
        out["rows"].append({"lna": float(xx), "z": math.exp(-float(xx))-1.,
                            "regime": regime, "stage_neighborhood": near,
                            "boundary_coverage_known": boundary_known,
                            "clamped_stencil": any(s["clamped_stencil"] for s in ss),
                            "fields": fields})
    # A caller's narrow target list must not masquerade as the global contract.
    covers_endpoints = all(g.sample(X0) is not None and g.sample(0.) is not None for g in hs)
    canonical_targets = np.array_equal(x, default_targets())
    out["global_coverage"] = bool(covers_endpoints and canonical_targets and missing == 0)
    out["target_count"] = int(x.size)
    out["missing_stencil_targets"] = missing
    rows = out["rows"]
    selectors = {"available_domain": rows}
    for label in sorted({r["regime"] for r in rows}):
        selectors["regime:"+label] = [r for r in rows if r["regime"] == label]
    selectors["stage_neighborhood"] = [r for r in rows if r["stage_neighborhood"]]
    selectors["clamped_stencil"] = [r for r in rows if r["clamped_stencil"]]
    selectors["boundary_coverage_unknown"] = [r for r in rows if not r["boundary_coverage_known"]]
    for label, (lo, hi) in WINDOWS_Z.items():
        selectors[label] = [r for r in rows if -math.log1p(hi) <= r["lna"] <= -math.log1p(lo)]
    for label, selected in selectors.items():
        if not selected:
            out["regions"][label] = {"status": "NO_COVERAGE", "points": 0}
            continue
        summary = {"points": len(selected), "fields": {}}
        all_gates = True
        for key in FIELD_FLOORS:
            ds = [r["fields"][key] for r in selected]
            d01 = max(abs(d["scaled_D01"]) for d in ds)
            d12 = max(abs(d["scaled_D12"]) for d in ds)
            gates = {"sensitivity": d12 <= 1.e-4, "contraction": d12 <= .75*d01,
                     "twice_fine_difference": 2.*d12 <= 1.e-4}
            counts = {s: sum(d["classification"] == s for d in ds)
                      for s in sorted({d["classification"] for d in ds})}
            summary["fields"][key] = {"maxnorm_D01": d01, "maxnorm_D12": d12,
                                       "original_gates": gates, "classifications": counts}
            all_gates &= all(gates.values())
        summary["status"] = "NUMERIC_TARGETS_MET" if all_gates else "NUMERIC_TARGETS_NOT_MET"
        out["regions"][label] = summary
    out["status"] = ("MANUFACTURED_DIAGNOSTIC" if hs[0].provenance["kind"] == "manufactured" else
                     "COMPLETE_DIAGNOSTIC_PENDING_REVIEW" if out["global_coverage"] else
                     "PARTIAL_DOMAIN_DIAGNOSTIC")
    out["p_interpretation"] = "Resolved signed three-level slope only; not a theorem, asymptotic error bound, or physical approval."
    return out
