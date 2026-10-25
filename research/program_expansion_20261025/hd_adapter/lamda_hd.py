"""Pinned LAMDA HD adapter; exact source decimals and separate H2 spin colliders.

This module implements only the frozen 2289-byte 2021-06-07 LAMDA source.
Missing transitions and off-grid collision temperatures raise UnsupportedDomain.
Einstein B coefficients multiply mean specific intensity J_nu, not energy density.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

SOURCE_SHA256 = "0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb"
SOURCE_BYTES = 2289
WU_SOURCE_SHA256 = "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af"
WU_SOURCE_COMMIT = "34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad"
SOURCE_URL = "https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat"
C = Decimal("299792458")
H = Decimal("6.62607015e-34")
KB = Decimal("1.380649e-23")
TEMPERATURES_K = (Decimal(50), Decimal(100), Decimal(200))
ROUNDING_GATE_HZ = Decimal(35)
ROUNDING_TOLERANCE = 128 * sys.float_info.epsilon


class AdapterError(ValueError):
    """Input does not meet the pinned adapter contract."""


class SourceIdentityError(AdapterError):
    pass


class SourceFormatError(AdapterError):
    pass


class UnsupportedDomain(AdapterError):
    pass


class NumericalDomainError(AdapterError):
    pass


def _d(value: Any, label: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool):
        raise AdapterError(f"{label}: boolean is not a number")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise AdapterError(f"{label}: invalid decimal {value!r}") from exc
    if not number.is_finite() or (number <= 0 if positive else number < 0):
        raise AdapterError(f"{label}: expected finite {'positive' if positive else 'nonnegative'} value")
    return number


def _binary64(value: Any, label: str, *, positive: bool = False) -> float:
    exact = _d(value, label, positive=positive)
    converted = float(exact)
    if not math.isfinite(converted) or (exact > 0 and converted == 0):
        raise NumericalDomainError(f"{label}: Decimal-to-binary64 underflow/overflow")
    return converted


def _mul(*values: Decimal) -> Decimal:
    # Exact for the finite, at-most-15-significant-digit pinned source products.
    with localcontext() as context:
        context.prec = 80
        answer = Decimal(1)
        for value in values:
            answer *= value
        return answer


@dataclass(frozen=True)
class SourceNumber:
    literal: str
    value: Decimal

    @classmethod
    def read(cls, literal: str, *, positive: bool = False) -> "SourceNumber":
        if not re.fullmatch(r"[+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", literal):
            raise SourceFormatError(f"invalid finite decimal spelling: {literal!r}")
        return cls(literal, _d(literal, "source decimal", positive=positive))


@dataclass(frozen=True)
class Level:
    id: int
    energy_cm_inverse: SourceNumber
    degeneracy: SourceNumber
    J: int
    source_line: int
    source_tokens: tuple[str, ...]

    @property
    def energy_J(self) -> Decimal:
        return _mul(H, C, Decimal(100), self.energy_cm_inverse.value)


def _energy_gap_J(upper: Level, lower: Level) -> Decimal:
    with localcontext() as context:
        context.prec = 80
        return upper.energy_J - lower.energy_J


@dataclass(frozen=True)
class RadiativeLine:
    id: int
    upper: int
    lower: int
    A_per_s: SourceNumber
    frequency_GHz: SourceNumber
    catalog_upper_energy_over_k_K: SourceNumber
    source_line: int
    source_tokens: tuple[str, ...]

    @property
    def frequency_Hz(self) -> Decimal:
        return _mul(self.frequency_GHz.value, Decimal("1e9"))


@dataclass(frozen=True)
class CollisionPair:
    id: int
    upper: int
    lower: int
    downward_cm3_per_s: tuple[SourceNumber, ...]
    source_line: int
    source_tokens: tuple[str, ...]


@dataclass(frozen=True)
class Collider:
    id: int
    name: str
    source_reference: str
    temperature_nodes_K: tuple[SourceNumber, ...]
    downward_pairs: tuple[CollisionPair, ...]


@dataclass(frozen=True)
class HDDataset:
    source_sha256: str
    source_bytes: int
    description: str
    molecular_weight_u: SourceNumber
    levels: tuple[Level, ...]
    radiative_lines: tuple[RadiativeLine, ...]
    colliders: tuple[Collider, ...]
    _original_bytes: bytes

    def source_roundtrip(self) -> bytes:
        return self._original_bytes

    def level(self, level_id: int) -> Level:
        if type(level_id) is not int:
            raise UnsupportedDomain("level ID must be a source integer")
        for record in self.levels:
            if record.id == level_id:
                return record
        raise UnsupportedDomain(f"level {level_id} is not supplied")

    def line(self, line_id: int) -> RadiativeLine:
        if type(line_id) is not int:
            raise UnsupportedDomain("line ID must be a source integer")
        for record in self.radiative_lines:
            if record.id == line_id:
                return record
        raise UnsupportedDomain(f"radiative line {line_id} is not supplied")

    def collider(self, collider_id: int) -> Collider:
        if type(collider_id) is not int or collider_id not in (2, 3):
            raise UnsupportedDomain("choose collider ID 2 (para-H2) or 3 (ortho-H2); no mixture is defined")
        return next(collider for collider in self.colliders if collider.id == collider_id)

    def downward_rate(self, collider_id: int, upper: int, lower: int, temperature_K: Any) -> Decimal:
        """Exact tabulated rate in m^3/s at an exact source temperature node."""
        collider = self.collider(collider_id)
        self.level(upper)
        self.level(lower)
        temperature = _d(temperature_K, "collision temperature", positive=True)
        if temperature not in TEMPERATURES_K:
            raise UnsupportedDomain(f"temperature {temperature} K is not a tabulated node 50/100/200 K")
        index = TEMPERATURES_K.index(temperature)
        for pair in collider.downward_pairs:
            if (pair.upper, pair.lower) == (upper, lower):
                return _mul(pair.downward_cm3_per_s[index].value, Decimal("1e-6"))
        raise UnsupportedDomain(f"collider {collider_id}: downward pair {upper}->{lower} is missing")

    def upward_rate(self, collider_id: int, lower: int, upper: int, temperature_K: Any) -> float:
        """Thermal detailed-balance construction; same collider, at a source node."""
        down = float(self.downward_rate(collider_id, upper, lower, temperature_K))
        u, l = self.level(upper), self.level(lower)
        temperature = _binary64(temperature_K, "collision temperature", positive=True)
        gap = float(_energy_gap_J(u, l))
        factor = math.exp(-gap / (float(KB) * temperature))
        answer = down * (float(u.degeneracy.value) / float(l.degeneracy.value)) * factor
        if answer == 0.0 or not math.isfinite(answer):
            raise NumericalDomainError("upward-rate underflow/overflow; value not admitted")
        return answer


class _Rows:
    def __init__(self, text: str):
        self.rows = [(number, line.strip()) for number, line in enumerate(text.splitlines(), 1)
                     if line.strip() and not line.lstrip().startswith("!")]
        self.position = 0

    def next(self, label: str) -> tuple[int, str]:
        if self.position == len(self.rows):
            raise SourceFormatError(f"premature EOF reading {label}")
        row = self.rows[self.position]
        self.position += 1
        return row

    def integer(self, label: str, expected: int | None = None) -> int:
        line, text = self.next(label)
        if not re.fullmatch(r"\d+", text):
            raise SourceFormatError(f"line {line}: invalid integer for {label}")
        value = int(text)
        if expected is not None and value != expected:
            raise SourceFormatError(f"line {line}: {label} expected {expected}, got {value}")
        return value


def _integer(text: str, line: int) -> int:
    if not re.fullmatch(r"\d+", text):
        raise SourceFormatError(f"line {line}: invalid integer {text!r}")
    return int(text)


def _parse_unqualified(data: bytes) -> HDDataset:
    """Grammar validation only; private entry for malformed-fixture controls.

    Call parse_hd for source-qualified use. This function never promotes an
    altered source to the pinned source identity.
    """
    try:
        rows = _Rows(data.decode("ascii"))
    except UnicodeDecodeError as exc:
        raise SourceFormatError("source must be ASCII") from exc
    _, description = rows.next("molecule")
    if description != "HD spectroscopy from CDMS version 2 of December 2011":
        raise SourceFormatError("unexpected molecule/spectroscopy identity")
    _, text = rows.next("molecular weight")
    molecular_weight = SourceNumber.read(text, positive=True)
    if molecular_weight.value != 3:
        raise SourceFormatError("HD molecular weight must retain the source value 3.0")
    rows.integer("number of levels", 9)
    levels = []
    for expected_id in range(1, 10):
        number, text = rows.next("level")
        parts = tuple(text.split())
        if len(parts) != 4:
            raise SourceFormatError(f"line {number}: expected four level columns")
        level = Level(_integer(parts[0], number), SourceNumber.read(parts[1]),
                      SourceNumber.read(parts[2], positive=True), _integer(parts[3], number), number, parts)
        if level.id != expected_id or level.J != expected_id - 1 or level.degeneracy.value != 2 * level.J + 1:
            raise SourceFormatError(f"line {number}: inconsistent HD level ID, J or degeneracy")
        if (not levels and level.energy_cm_inverse.value != 0) or (levels and level.energy_J <= levels[-1].energy_J):
            raise SourceFormatError(f"line {number}: source levels must start at zero and increase")
        levels.append(level)
    level_ids = {level.id for level in levels}
    rows.integer("number of radiative transitions", 8)
    radiative = []
    for expected_id in range(1, 9):
        number, text = rows.next("radiative transition")
        parts = tuple(text.split())
        if len(parts) != 6:
            raise SourceFormatError(f"line {number}: expected six radiative columns")
        record = RadiativeLine(*(_integer(parts[i], number) for i in range(3)),
                               *(SourceNumber.read(parts[i], positive=True) for i in range(3, 6)), number, parts)
        if record.id != expected_id or (record.upper, record.lower) != (expected_id + 1, expected_id):
            raise SourceFormatError(f"line {number}: invalid source radiative reference/order")
        radiative.append(record)
    rows.integer("number of colliders", 2)
    colliders = []
    expected_pairs = ((2, 1), (3, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8))
    for expected_id, source_name, name in ((2, "HD-pH2", "para-H2"), (3, "HD-oH2", "ortho-H2")):
        number, reference = rows.next("collider identity/reference")
        parts = reference.split(maxsplit=2)
        if len(parts) != 3 or _integer(parts[0], number) != expected_id or parts[1] != source_name or "Flower (1999" not in parts[2]:
            raise SourceFormatError(f"line {number}: distinct p/o-H2 collider identity/reference required")
        rows.integer("number of collisional transitions", 9)
        rows.integer("number of temperatures", 3)
        number, text = rows.next("temperature nodes")
        temperatures = tuple(SourceNumber.read(value, positive=True) for value in text.split())
        if tuple(value.value for value in temperatures) != TEMPERATURES_K:
            raise SourceFormatError(f"line {number}: temperature nodes must be exactly 50/100/200 K")
        pairs = []
        for pair_id, expected_pair in enumerate(expected_pairs, 1):
            number, text = rows.next("collision pair")
            parts = tuple(text.split())
            if len(parts) != 6:
                raise SourceFormatError(f"line {number}: expected three IDs and three rates")
            ids = tuple(_integer(parts[i], number) for i in range(3))
            if ids[0] != pair_id or ids[1:] != expected_pair or any(i not in level_ids for i in ids[1:]):
                raise SourceFormatError(f"line {number}: inconsistent or missing collision reference")
            pairs.append(CollisionPair(*ids, tuple(SourceNumber.read(x, positive=True) for x in parts[3:]), number, parts))
        colliders.append(Collider(expected_id, name, reference, temperatures, tuple(pairs)))
    if rows.position != len(rows.rows):
        raise SourceFormatError(f"unexpected trailing data at line {rows.rows[rows.position][0]}")
    return HDDataset(hashlib.sha256(data).hexdigest(), len(data), description, molecular_weight,
                     tuple(levels), tuple(radiative), tuple(colliders), data)


def parse_hd(data: bytes) -> HDDataset:
    if not isinstance(data, bytes):
        raise SourceIdentityError("parse_hd requires original bytes")
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != SOURCE_BYTES or digest != SOURCE_SHA256:
        raise SourceIdentityError(f"pinned source mismatch: bytes={len(data)}, sha256={digest}")
    return _parse_unqualified(data)


def load_hd(path: str | Path) -> HDDataset:
    return parse_hd(Path(path).read_bytes())


def line_frequency_gap_Hz(data: HDDataset, line_id: int) -> Decimal:
    line = data.line(line_id)
    with localcontext() as context:
        context.prec = 80
        gap_cm = data.level(line.upper).energy_cm_inverse.value - data.level(line.lower).energy_cm_inverse.value
        return abs(C * Decimal(100) * gap_cm - line.frequency_Hz)


def transition_qualification(data: HDDataset, line_id: int) -> dict[str, Any]:
    """Per-line gate for binding tabulated internal energy to a line photon."""
    line = data.line(line_id)
    gap = line_frequency_gap_Hz(data, line_id)
    return {"line_id": line.id, "upper": line.upper, "lower": line.lower,
            "absolute_gap_Hz": str(gap), "rounding_gate_Hz": str(ROUNDING_GATE_HZ),
            "consistent_internal_energy_photon_binding": gap <= ROUNDING_GATE_HZ,
            "status": "PASS_CATALOG_ROUNDING_GATE" if gap <= ROUNDING_GATE_HZ else "SOURCE_DISCREPANCY_UNQUALIFIED",
            "physical_frequency_uncertainty": None}


def require_energy_frequency_bridge(data: HDDataset, line_id: int) -> RadiativeLine:
    qualification = transition_qualification(data, line_id)
    if not qualification["consistent_internal_energy_photon_binding"]:
        raise UnsupportedDomain(f"line {line_id}: level/photon discrepancy {qualification['absolute_gap_Hz']} Hz exceeds fixed35Hz gate")
    return data.line(line_id)


def einstein_B(data: HDDataset, line_id: int) -> tuple[float, float]:
    line = data.line(line_id)
    frequency = float(line.frequency_Hz)
    B_ul = float(line.A_per_s.value) * float(C) ** 2 / (2 * float(H) * frequency ** 3)
    degeneracy_ratio = (float(data.level(line.upper).degeneracy.value) / float(data.level(line.lower).degeneracy.value))
    return B_ul, degeneracy_ratio * B_ul


def line_coefficients(data: HDDataset, line_id: int, n_lower_per_m3: Any,
                      n_upper_per_m3: Any, phi_per_Hz: Any) -> dict[str, Any]:
    """Pointwise j_nu and signed net alpha_nu; caller owns normalized profile."""
    line = data.line(line_id)
    lower = _binary64(n_lower_per_m3, "lower population")
    upper = _binary64(n_upper_per_m3, "upper population")
    profile = _binary64(phi_per_Hz, "profile value")
    B_ul, B_lu = einstein_B(data, line_id)
    factor = float(H) * float(line.frequency_Hz) / (4 * math.pi) * profile
    emission = factor * upper * float(line.A_per_s.value)
    population_difference = math.fsum((lower * B_lu, -upper * B_ul))
    absorption = factor * population_difference
    if not all(math.isfinite(x) for x in (emission, absorption)):
        raise NumericalDomainError("nonfinite radiative coefficients")
    if upper > 0 and profile > 0 and emission == 0:
        raise NumericalDomainError("emission underflow; zero is not accepted")
    if profile > 0 and population_difference != 0 and absorption == 0:
        raise NumericalDomainError("absorption underflow; zero is not accepted")
    return {"j_nu_J_s_m3_sr_Hz": emission, "alpha_nu_per_m": absorption,
            "population_inversion": lower * B_lu < upper * B_ul,
            "analytic_zero": emission == 0.0 and absorption == 0.0,
            "B_convention": "profile-averaged mean specific intensity J_nu"}


def thermal_line(data: HDDataset, line_id: int, temperature_K: Any,
                 n_lower_per_m3: Any = 1, phi_per_Hz: Any = 1) -> dict[str, float | bool | str]:
    """Thermal line algebra using the identical catalog photon energy throughout."""
    line = data.line(line_id)
    temperature = _binary64(temperature_K, "thermal temperature", positive=True)
    lower = _binary64(n_lower_per_m3, "lower population")
    profile = _binary64(phi_per_Hz, "profile value")
    frequency = float(line.frequency_Hz)
    x = (float(H) * frequency / float(KB)) / temperature
    if not math.isfinite(x) or x >= 700 or x <= 0:
        raise NumericalDomainError("thermal exponent outside stable binary64 algebra domain")
    B_ul, _ = einstein_B(data, line_id)
    degeneracy_ratio = (float(data.level(line.upper).degeneracy.value) / float(data.level(line.lower).degeneracy.value))
    upper = lower * degeneracy_ratio * math.exp(-x)
    factor = float(H) * frequency / (4 * math.pi) * profile
    emission = factor * upper * float(line.A_per_s.value)
    absorption = factor * lower * degeneracy_ratio * B_ul * (-math.expm1(-x))
    planck = 2 * float(H) * frequency ** 3 / float(C) ** 2 / math.expm1(x)
    if not all(math.isfinite(v) for v in (upper, emission, absorption, planck)):
        raise NumericalDomainError("nonfinite thermal line result")
    if lower > 0 and profile > 0 and (upper == 0 or emission == 0 or absorption == 0 or planck == 0):
        raise NumericalDomainError("thermal line underflow; zero is not accepted")
    paired = absorption * planck
    if emission == 0 and paired == 0:
        residual = None
        classification = "ANALYTIC_ZERO"
    else:
        residual = abs(emission - paired) / (abs(emission) + abs(paired))
        classification = "THERMAL_POSITIVE_ABSORPTION"
    return {"n_upper_per_m3": upper, "j_nu_J_s_m3_sr_Hz": emission,
            "alpha_nu_per_m": absorption, "B_nu_W_m2_sr_Hz": planck,
            "normalized_Kirchhoff_residual": residual, "classification": classification,
            "x_photon_over_kT": x, "population_difference_condition": 1 / (-math.expm1(-x)),
            "underflow": False}


def diagnostics(data: HDDataset) -> dict[str, Any]:
    """Finite new-source diagnostics; no solver, IVP or old campaign execution."""
    gaps = [transition_qualification(data, line.id) for line in data.radiative_lines]
    balance = []
    for collider in data.colliders:
        for pair in collider.downward_pairs:
            u, l = data.level(pair.upper), data.level(pair.lower)
            gap = float(_energy_gap_J(u, l))
            for temperature in TEMPERATURES_K:
                down = float(data.downward_rate(collider.id, pair.upper, pair.lower, temperature))
                up = data.upward_rate(collider.id, pair.lower, pair.upper, temperature)
                # Independently invert the Boltzmann relation, rather than
                # comparing the upward routine with itself.
                recovered = up * (float(l.degeneracy.value) / float(u.degeneracy.value)) * math.exp(gap / (float(KB) * float(temperature)))
                residual = abs(recovered - down) / (abs(recovered) + abs(down))
                balance.append({"collider_id": collider.id, "upper": pair.upper, "lower": pair.lower,
                                "temperature_K": str(temperature), "normalized_reverse_residual": residual,
                                "underflow": False})
    kirchhoff = [{"line_id": line.id, "temperature_K": str(temperature),
                 **thermal_line(data, line.id, temperature)}
                for line in data.radiative_lines for temperature in TEMPERATURES_K]
    passed = (all(Decimal(row["absolute_gap_Hz"]) <= ROUNDING_GATE_HZ for row in gaps)
              and all(row["normalized_reverse_residual"] <= ROUNDING_TOLERANCE for row in balance)
              and all(row["normalized_Kirchhoff_residual"] <= ROUNDING_TOLERANCE for row in kirchhoff))
    return {"schema": "REC_HD_ADAPTER_DIAGNOSTICS_V1", "source_sha256": data.source_sha256,
            "source_bytes": data.source_bytes, "shape": {"levels": len(data.levels), "lines": len(data.radiative_lines),
            "colliders": len(data.colliders), "downward_pairs": sum(len(x.downward_pairs) for x in data.colliders),
            "rate_values": sum(len(p.downward_cm3_per_s) for c in data.colliders for p in c.downward_pairs)},
            "frequency_gap_Hz": gaps, "detailed_balance": balance, "Kirchhoff": kirchhoff,
            "float_residual_tolerance": ROUNDING_TOLERANCE, "catalog_rounding_gate_Hz": str(ROUNDING_GATE_HZ),
            "status": "PASS_SCOPED_NUMERICAL_ALGEBRA" if passed else "FAIL_FROZEN_CRITERION",
            "parser_identity_shape_decimal_status": "PASS_PINNED_LITERAL_INGESTION",
            "energy_frequency_consistency_status": "PASS" if all(Decimal(row["absolute_gap_Hz"]) <= ROUNDING_GATE_HZ for row in gaps) else "FAIL_FROZEN_35_HZ_GATE",
            "consistent_internal_energy_photon_binding_approved": all(Decimal(row["absolute_gap_Hz"]) <= ROUNDING_GATE_HZ for row in gaps),
            "physical_rate_uncertainty": None, "spectroscopic_physical_uncertainty": None,
            "vibrational_state": None, "collision_interpolation": "UNSUPPORTED", "mixture_rule": None,
            "production_approved": False, "population_IVP_runs": 0, "old_compiler_runs": 0}


def bind_wu_species(data: HDDataset, module_path: str | Path) -> tuple[Any, ...]:
    """Reuse the pinned supplier Species.from_record, without executing fixtures.

    The explicit state label preserves the unresolved vibrational assignment.
    The imported code must match the exact already-admitted supplier source.
    """
    path = Path(module_path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != WU_SOURCE_SHA256:
        raise SourceIdentityError("WU canonical species source identity mismatch")
    spec = importlib.util.spec_from_file_location("rec_hd_pinned_wu_chem_ledger", path)
    if spec is None or spec.loader is None:
        raise AdapterError("cannot load pinned WU species module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    species = tuple(module.Species.from_record({
        "composition": [{"Z": 1, "A": 1, "isomer": "ground", "count": 1},
                        {"Z": 1, "A": 2, "isomer": "ground", "count": 1}],
        "charge": 0, "state": f"LAMDA_HD:J={level.J};v=UNSPECIFIED", "pool": "material"})
        for level in data.levels)
    if len({item.key() for item in species}) != len(data.levels):
        raise AdapterError("nonunique canonical level identities")
    return species


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="original pinned hd.dat bytes")
    parser.add_argument("--diagnostics", type=Path, required=True, help="new output JSON (must not already exist)")
    parser.add_argument("--wu-module", type=Path, required=True, help="pinned WU chem_ledger.py")
    args = parser.parse_args()
    data = load_hd(args.source)
    result = diagnostics(data)
    result["canonical_WU_species"] = [item.key() for item in bind_wu_species(data, args.wu_module)]
    result["canonical_WU_source_sha256"] = WU_SOURCE_SHA256
    with args.diagnostics.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "shape": result["shape"]}))
    return 0 if result["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
