"""Fail-closed, opt-in HD rotational-line consumer bridge.

Research-only wrapper around the pinned REC 2026-10-29 `lamda_hd.py` source.
This is NOT a physical correction, source replacement, or default runtime path.
No raw LAMDA/CDMS data are embedded or republished here.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import importlib.util
from pathlib import Path
import sys

ADAPTER_GIT_BLOB = "632a8a094e7eedd24a1ec3132fec20765d6e39da"
LAMDA_SHA256 = "0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb"
LAMDA_BYTES = 2289
FROZEN_GATE_HZ = Decimal("35")
C = Decimal("299792458")

class SourcePinError(ValueError):
    pass

class EnergyBridgeHeld(ValueError):
    pass


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def load_pinned_adapter(path: str | Path):
    path = Path(path)
    raw = path.read_bytes()
    actual = git_blob_sha1(raw)
    if actual != ADAPTER_GIT_BLOB:
        raise SourcePinError(f"REC HD adapter Git blob mismatch: {actual}")
    spec = importlib.util.spec_from_file_location("pinned_rec_hd_adapter_readonly", path)
    if spec is None or spec.loader is None:
        raise SourcePinError("adapter not importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _strict_bridge_core(module, data, line_id: int) -> dict:
    """Internal gate model for injected synthetic fixtures and verified adapter.

    Caller must load data via `module.load_hd(private_raw_path)`; the source
    identity is enforced again here to avoid a diagnostic clone's silent use.
    """
    if type(line_id) is not int:
        raise EnergyBridgeHeld("line_id must be an exact integer")
    if (getattr(data, "source_sha256", None) != LAMDA_SHA256
            or getattr(data, "source_bytes", None) != LAMDA_BYTES):
        raise SourcePinError("pinned LAMDA HD source identity missing")
    q = module.transition_qualification(data, line_id)
    try:
        gap = Decimal(str(q["absolute_gap_Hz"]))
    except (KeyError, InvalidOperation, ValueError) as exc:
        raise EnergyBridgeHeld("missing/invalid independent gap evidence") from exc
    if (not gap.is_finite() or gap < 0 or gap > FROZEN_GATE_HZ
            or q.get("consistent_internal_energy_photon_binding") is not True):
        raise EnergyBridgeHeld(f"line {line_id}: independent source gap {gap} Hz; original 35 Hz gate held")
    # Do not replace `require_energy_frequency_bridge` with a parallel,
    # potentially divergent implementation; require the actual owner gate too.
    try:
        line = module.require_energy_frequency_bridge(data, line_id)
    except Exception as exc:
        raise EnergyBridgeHeld(f"line {line_id}: original REC bridge rejected") from exc
    if getattr(line, "id", None) != line_id:
        raise EnergyBridgeHeld("original bridge returned another line")
    return {"line_id": line_id, "gap_Hz": str(gap),
            "source": LAMDA_SHA256, "gate_Hz": str(FROZEN_GATE_HZ),
            "scope": "SOURCE_ROUNDING_ONLY", "physical_approval": False}


def validate_pinned_raw_bytes(raw: bytes) -> None:
    """Authenticate the actual source bytes, not only an object's SHA label."""
    if not isinstance(raw, bytes) or len(raw) != LAMDA_BYTES or hashlib.sha256(raw).hexdigest() != LAMDA_SHA256:
        raise SourcePinError("original raw LAMDA bytes do not match immutable source lock")


def strict_bridge(module, data, line_id: int) -> dict:
    """Fail-closed entry: authentic adapter class, raw source, original 35 Hz gate."""
    path = getattr(module, "__file__", None)
    if not path:
        raise SourcePinError("module file path missing: cannot authenticate adapter")
    try:
        actual = git_blob_sha1(Path(path).read_bytes())
    except (OSError, ValueError) as exc:
        raise SourcePinError("unreadable pinned adapter source") from exc
    if actual != ADAPTER_GIT_BLOB:
        raise SourcePinError(f"HD module blob mismatched: {actual}")
    if type(data) is not getattr(module, "HDDataset", None):
        raise SourcePinError("data is not the exact pinned REC HDDataset class")
    try:
        validate_pinned_raw_bytes(data.source_roundtrip())
    except (AttributeError, OSError) as exc:
        raise SourcePinError("unavailable original HD source bytes") from exc
    return _strict_bridge_core(module, data, line_id)


def guarded_line_coefficients(module, data, line_id: int, n_lower_per_m3,
                              n_upper_per_m3, phi_per_Hz) -> dict:
    """Opt-in demo: reject an HD line that fails independent energy bridge.

    In genuine intensity-only use of a catalog line without level-energy
    coupling, a different scientifically justified interface may be needed.
    This wrapper is intentionally narrower and never rewrites the owner code.
    """
    evidence = strict_bridge(module, data, line_id)
    out = module.line_coefficients(data, line_id, n_lower_per_m3,
                                   n_upper_per_m3, phi_per_Hz)
    return {"coefficients": out, "source_bridge": evidence,
            "production_approved": False}


def covariance_free_gap_sd_bounds(sigma_upper_cm1, sigma_lower_cm1) -> tuple[Decimal, Decimal]:
    """CM^-1 -> Hz upper/lower SD bounds from covariance PSD, not a CI.

    Valid ONLY if the supplied decimals are marginal 1-sigma standard
    deviations of the SAME joint fit (not errors of unrelated catalog lines).
    """
    try:
        su, sl = (Decimal(str(x)) for x in (sigma_upper_cm1, sigma_lower_cm1))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid energy marginal SD") from exc
    if not su.is_finite() or not sl.is_finite() or min(su, sl) < 0:
        raise ValueError("marginal SD must be finite and nonnegative")
    factor = C * Decimal(100)
    return abs(su-sl)*factor, (su+sl)*factor


def exact_fixed_phi_policy_ratios(nu_hz, delta_hz) -> dict[str, Fraction]:
    """Fixed A,populations,local-frequency-profile value: B,j,alpha,S ratios.

    Distinct from own-line-centre fixed-velocity-width comparisons in PR155.
    Ratios are valid only when line opacity is nonzero and both policies use
    precisely the same profile-per-Hz value, at their respective frequencies.
    """
    def rational(x):
        if isinstance(x, bool):
            raise ValueError("boolean frequency")
        try:
            return Fraction(str(x))
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError("non-rational frequency") from exc
    nu, delta = rational(nu_hz), rational(delta_hz)
    if nu <= 0 or nu + delta <= 0:
        raise ValueError("nonpositive source or mutated frequency")
    r = (nu+delta)/nu
    return {"B_ul": 1/r**3, "j_nu": r, "alpha_nu": 1/r**2,
            "source_function": r**3}


if __name__ == "__main__":
    raise SystemExit("Library-only research guard. Run the targeted test suite; source/physical gate remains held.")
