#!/usr/bin/env python3
"""Build PR-05C2C1B2B1E1B0/v0.75 dynamic-macro ownership evidence.

This bounded stage does not solve a full atomic/native/COM macro.  It proves
that the currently durable original-HyRec native block and the v0.74 COM--KHW
interior operator overlap on the same physical frequency support, and it locks
a fail-closed ownership contract for the replacement stage.
"""
from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (  # noqa: E402
    parse_original_hyrec_boundary_snapshot_csv,
)
from full_bianchi_hyrec.trajectory.dynamic_macro_ownership import (  # noqa: E402
    audit_dynamic_atomic_macro_ownership,
    current_v074_ownership_config,
    naive_dynamic_atomic_ownership_config,
    resolved_split_domain_contract_witness,
)
from full_bianchi_hyrec.trajectory.primitive_rates import LYMAN_ALPHA_ENERGY_EV  # noqa: E402

VERSION = 75
STAGE = "PR-05C2C1B2B1E1B0/v0.75"
NAME = "Full_Bianchi_HyRec_PR05C2C1B2B1E1B0_dynamic_macro_ownership_no_go_v0_75"
STATUS = (
    "PASS_BOUNDED_NO_GO_DYNAMIC_ATOMIC_MACRO_OWNERSHIP_OVERLAP_"
    "SPLIT_DOMAIN_REPLACEMENT_REQUIRED"
)
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c1b2b1e1b0_dynamic_macro_ownership_v075.npz"
FORMALISM = ROOT / "docs" / "PR05C2C1B2B1E1B0_DYNAMIC_MACRO_OWNERSHIP_FORMALISM.md"
REPORT = ROOT / "docs" / "PR05C2C1B2B1E1B0_RESEARCH_REPORT.md"
NEXT_PLAN = ROOT / "docs" / "PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT_PLAN.md"
SOURCE = (
    ROOT
    / "archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55"
    / "pr04c_z1100.csv"
)
RESEARCH_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip"
CODING_HARNESS = ROOT / "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip"
RESEARCH_HARNESS_SHA256 = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CODING_HARNESS_SHA256 = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for key in sorted(arrays):
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, np.asarray(arrays[key]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{key}.npy", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, buffer.getvalue(), compresslevel=9)


def deterministic_zip(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(source)), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def validate_harness(archive: Path, expected: str, validator: str, work: Path, log: Path) -> dict[str, object]:
    observed = sha256(archive)
    if observed != expected:
        raise RuntimeError(f"harness SHA mismatch: {archive}")
    destination = work / archive.stem
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise RuntimeError(f"corrupt harness: {archive}")
        zipped.extractall(destination)
    matches = list(destination.rglob(validator))
    if len(matches) != 1:
        raise RuntimeError(f"cannot uniquely locate {validator}")
    result = subprocess.run(
        [sys.executable, str(matches[0])],
        cwd=matches[0].parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"harness validation failed: {archive}")
    return {"archive": archive.name, "sha256": observed, "validator": validator, "passed": True}


def markdown_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)
    generated_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    with tempfile.TemporaryDirectory(prefix="pr05c2c1b2b1e1b0_") as temporary:
        work = Path(temporary)
        research_receipt = validate_harness(
            RESEARCH_HARNESS,
            RESEARCH_HARNESS_SHA256,
            "tools/validate_workspace.py",
            work,
            EXPANDED / "RESEARCH_HARNESS_VALIDATION.log",
        )
        coding_receipt = validate_harness(
            CODING_HARNESS,
            CODING_HARNESS_SHA256,
            "tools/validate_harness.py",
            work,
            EXPANDED / "CODING_HARNESS_VALIDATION.log",
        )

    parsed = parse_original_hyrec_boundary_snapshot_csv(SOURCE)
    snapshot = parsed.trajectory
    width = float(parsed.boundaries[0].doppler_width_eV)
    interface_abs_x = 21.25
    configs = {
        "current_v074": current_v074_ownership_config(),
        "naive_dynamic_atomic": naive_dynamic_atomic_ownership_config(),
        "resolved_contract_witness": resolved_split_domain_contract_witness(),
    }
    audits = {
        name: audit_dynamic_atomic_macro_ownership(
            snapshot,
            doppler_width_eV=width,
            config=config,
            interface_abs_x=interface_abs_x,
        )
        for name, config in configs.items()
    }
    current = audits["current_v074"]
    naive = audits["naive_dynamic_atomic"]
    witness = audits["resolved_contract_witness"]

    energy = np.asarray(snapshot.energy_eV, dtype=float)
    x = (energy - LYMAN_ALPHA_ENERGY_EV) / width
    inside = np.abs(x) <= interface_abs_x

    support_rows: list[dict[str, object]] = []
    for i in range(energy.size):
        support = "COM_INTERIOR" if inside[i] else ("NATIVE_LEFT_EXTERIOR" if x[i] < 0.0 else "NATIVE_RIGHT_EXTERIOR")
        support_rows.append(
            {
                "native_index": i,
                "energy_eV": f"{energy[i]:.17e}",
                "doppler_x": f"{x[i]:.17e}",
                "support": support,
                "Aup_s_inv": f"{snapshot.Aup_s_inv[i]:.17e}",
                "Adn_s_inv": f"{snapshot.Adn_s_inv[i]:.17e}",
                "Gamma_s_inv": f"{snapshot.Gamma_s_inv[i]:.17e}",
                "Tvr_2s_s_inv": f"{snapshot.Tvr[0, i]:.17e}",
                "Tvr_2p_s_inv": f"{snapshot.Tvr[1, i]:.17e}",
                "Trv_2s_s_inv": f"{snapshot.Trv[0, i]:.17e}",
                "Trv_2p_s_inv": f"{snapshot.Trv[1, i]:.17e}",
            }
        )
    write_csv(EXPANDED / "NATIVE_POINT_SUPPORT.csv", support_rows)

    edge_rows: list[dict[str, object]] = []
    edge_mid = []
    edge_rate = []
    edge_class_code = []
    for i in range(energy.size - 1):
        forward = abs(float(snapshot.Tvv[2, i]))
        reverse = abs(float(snapshot.Tvv[1, i + 1]))
        rate = max(forward, reverse)
        if rate == 0.0:
            continue
        if inside[i] and inside[i + 1]:
            classification = "INSIDE_INTERIOR"
            code = 0
            current_owner = "ORIGINAL_HYREC_NATIVE_AND_COM_OVERLAP"
            target_owner = "COM_KHW_INTERIOR"
        elif bool(inside[i]) != bool(inside[i + 1]):
            classification = "CROSS_INTERFACE"
            code = 1
            current_owner = "SPLIT_DOMAIN_INTERFACE_DECLARED_BUT_NATIVE_EDGE_STILL_PRESENT"
            target_owner = "SPLIT_DOMAIN_INTERFACE"
        else:
            classification = "OUTSIDE_EXTERIOR"
            code = 2
            current_owner = "ORIGINAL_HYREC_NATIVE"
            target_owner = "ORIGINAL_HYREC_EXTERIOR"
        midpoint = 0.5 * (x[i] + x[i + 1])
        edge_mid.append(midpoint)
        edge_rate.append(rate)
        edge_class_code.append(code)
        edge_rows.append(
            {
                "left_index": i,
                "right_index": i + 1,
                "left_x": f"{x[i]:.17e}",
                "right_x": f"{x[i + 1]:.17e}",
                "midpoint_x": f"{midpoint:.17e}",
                "forward_abs_s_inv": f"{forward:.17e}",
                "reverse_abs_s_inv": f"{reverse:.17e}",
                "classification": classification,
                "current_owner": current_owner,
                "required_owner": target_owner,
            }
        )
    write_csv(EXPANDED / "DIFFUSION_EDGE_REGISTRY.csv", edge_rows)

    audit_rows: list[dict[str, object]] = []
    for name, audit in audits.items():
        audit_rows.append(
            {
                "configuration": name,
                "interior_native_count": audit.com_interior_native_count,
                "inside_diffusion_edges": audit.diffusion_inside_edge_count,
                "cross_diffusion_edges": audit.diffusion_cross_edge_count,
                "outside_diffusion_edges": audit.diffusion_outside_edge_count,
                "Aup_interior_fraction": f"{audit.canonical_up_rate_interior_fraction:.17e}",
                "Adn_interior_fraction": f"{audit.canonical_down_rate_interior_fraction:.17e}",
                "Tvr_interior_fraction": f"{audit.real_to_virtual_abs_interior_fraction:.17e}",
                "Trv_interior_fraction": f"{audit.virtual_to_real_abs_interior_fraction:.17e}",
                "overlap_count": audit.overlap_count,
                "unowned_count": audit.unowned_process_count,
                "replacement_complete": int(audit.replacement_complete),
                "contract_witness_only": int(audit.contract_witness_only),
                "macro_ready": int(audit.dynamic_atomic_macro_ready),
                "unresolved_processes": "|".join(audit.unresolved_processes),
            }
        )
    write_csv(EXPANDED / "OWNERSHIP_AUDIT.csv", audit_rows)

    process_rows = [
        {
            "physical_process": "scalar_Dfplus_history",
            "current_owner": "typed_characteristic_history",
            "required_owner": "typed_characteristic_history",
            "status": "CLOSED",
        },
        {
            "physical_process": "native_A1s_diffusion_inside_COM_support",
            "current_owner": "original_HyRec_native_and_COM_KHW",
            "required_owner": "COM_KHW_interior_only",
            "status": "OVERLAP_BLOCKER",
        },
        {
            "physical_process": "native_A1s_diffusion_cross_interface",
            "current_owner": "native_edge_present_plus_interface_contract",
            "required_owner": "split_domain_interface_only",
            "status": "REPLACEMENT_BLOCKER",
        },
        {
            "physical_process": "native_A1s_diffusion_exterior",
            "current_owner": "original_HyRec_native_full",
            "required_owner": "original_HyRec_exterior_only",
            "status": "SPLIT_REQUIRED",
        },
        {
            "physical_process": "atomic_real_virtual_source_inside_COM_support",
            "current_owner": "original_HyRec_native_full",
            "required_owner": "COM_interior_deposition",
            "status": "SOURCE_ROUTING_BLOCKER",
        },
        {
            "physical_process": "atomic_real_virtual_source_exterior",
            "current_owner": "original_HyRec_native_full",
            "required_owner": "original_HyRec_exterior_only",
            "status": "SPLIT_REQUIRED",
        },
        {
            "physical_process": "completed_Tvv_real_virtual_algebra",
            "current_owner": "original_HyRec_full",
            "required_owner": "exterior_Schur_plus_COM_interior_plus_interface",
            "status": "SCHUR_REPLACEMENT_BLOCKER",
        },
        {
            "physical_process": "COM_nonlinear_stimulated_collision",
            "current_owner": "COM_KHW_interior",
            "required_owner": "COM_KHW_interior",
            "status": "CLOSED_SUBBLOCK",
        },
    ]
    write_csv(EXPANDED / "PROCESS_OWNERSHIP_MATRIX.csv", process_rows)

    metrics = {
        "stage": STAGE,
        "status": STATUS,
        "generated_utc": generated_utc,
        "source_z": float(snapshot.z),
        "source_index": int(snapshot.iz_local),
        "doppler_width_eV": width,
        "interface_abs_x": interface_abs_x,
        "native_virtual_count": current.native_virtual_count,
        "com_interior_native_count": current.com_interior_native_count,
        "com_interior_native_indices": list(current.com_interior_native_indices),
        "minimum_interior_x": current.minimum_interior_x,
        "maximum_interior_x": current.maximum_interior_x,
        "left_exterior_x": current.left_exterior_x,
        "right_exterior_x": current.right_exterior_x,
        "diffusion_inside_edge_count": current.diffusion_inside_edge_count,
        "diffusion_cross_edge_count": current.diffusion_cross_edge_count,
        "diffusion_outside_edge_count": current.diffusion_outside_edge_count,
        "diffusion_cross_edges": [list(edge) for edge in current.diffusion_cross_edges],
        "diffusion_cross_rate_s_inv": current.diffusion_cross_rate_s_inv,
        "canonical_up_rate_interior_fraction": current.canonical_up_rate_interior_fraction,
        "canonical_down_rate_interior_fraction": current.canonical_down_rate_interior_fraction,
        "real_to_virtual_abs_interior_fraction": current.real_to_virtual_abs_interior_fraction,
        "virtual_to_real_abs_interior_fraction": current.virtual_to_real_abs_interior_fraction,
        "current_v074_ready": current.dynamic_atomic_macro_ready,
        "naive_dynamic_atomic_ready": naive.dynamic_atomic_macro_ready,
        "contract_witness_ready": witness.dynamic_atomic_macro_ready,
        "contract_witness_only": witness.contract_witness_only,
        "current_unresolved": list(current.unresolved_processes),
        "naive_unresolved": list(naive.unresolved_processes),
        "no_fitted_normalization": True,
        "no_native_cell_inference": True,
        "dynamic_macro_not_executed": True,
        "full_coupled_endpoint_not_claimed": True,
        "next": "PR05C2C1B2B1E1C_EXTERIOR_NATIVE_COM_INTERIOR_INTERFACE_REPLACEMENT",
    }
    write_json(EXPANDED / "NUMERICAL_METRICS.json", metrics)

    deterministic_npz(
        EXPANDED / "pr05c2c1b2b1e1b0_dynamic_macro_ownership_v075.npz",
        {
            "energy_eV": energy,
            "doppler_x": x,
            "inside_com_support": inside.astype(np.int8),
            "Aup_s_inv": snapshot.Aup_s_inv,
            "Adn_s_inv": snapshot.Adn_s_inv,
            "Tvr_s_inv": snapshot.Tvr,
            "Trv_s_inv": snapshot.Trv,
            "Tvv_s_inv": snapshot.Tvv,
            "edge_midpoint_x": np.asarray(edge_mid),
            "edge_rate_s_inv": np.asarray(edge_rate),
            "edge_class_code": np.asarray(edge_class_code, dtype=np.int8),
        },
    )

    # Plot 1: rate mass support.
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.axvspan(-interface_abs_x, interface_abs_x, alpha=0.15, label="COM support")
    ax.semilogy(x, np.maximum(np.abs(snapshot.Aup_s_inv), 1e-300), label="|Aup|")
    ax.semilogy(x, np.maximum(np.abs(snapshot.Adn_s_inv), 1e-300), label="|Adn|")
    ax.axvline(-interface_abs_x, linestyle="--")
    ax.axvline(interface_abs_x, linestyle="--")
    ax.set_xlim(-80.0, 80.0)
    ax.set_xlabel("Hydrogen-frame Doppler coordinate x")
    ax.set_ylabel("Canonical rate [s$^{-1}$]")
    ax.set_title("Original-HyRec real–virtual rates overlap the COM interior")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EXPANDED / "NATIVE_COM_SUPPORT_OVERLAP.png", dpi=220)
    plt.close(fig)

    # Plot 2: diffusion topology.
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    mids = np.asarray(edge_mid)
    rates = np.asarray(edge_rate)
    classes = np.asarray(edge_class_code)
    names = [(0, "inside"), (1, "cross-interface"), (2, "outside")]
    for code, label in names:
        mask = classes == code
        ax.semilogy(mids[mask], np.maximum(rates[mask], 1e-300), "o", label=label)
    ax.axvspan(-interface_abs_x, interface_abs_x, alpha=0.15)
    ax.set_xlim(-80.0, 80.0)
    ax.set_xlabel("Edge midpoint x")
    ax.set_ylabel("max adjacent diffusion rate [s$^{-1}$]")
    ax.set_title("Canonical native diffusion graph crosses the split-domain interfaces")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EXPANDED / "NATIVE_DIFFUSION_OWNERSHIP.png", dpi=220)
    plt.close(fig)

    formalism = r"""
# PR-05C2C1B2B1E1B0 dynamic-macro ownership formalism

## Scope and conventions

The metric signature is `(-,+,+,+)`.  Photon frequency is ordinary frequency
in Hz; the original-HyRec virtual registry is stored in eV and converted to the
hydrogen-frame Doppler coordinate

\[
x_b=\frac{E_b-E_{\rm Ly\alpha}}{\Delta E_D}.
\]

The COM collision domain is the fixed interior interval \(|x|\le 21.25\).
Original-HyRec virtual states are zero-width point spikes.  No finite native
cell boundaries are inferred.

## Ownership obstruction

At the locked \(z\simeq1100\) snapshot, eight canonical virtual spikes lie in
the COM interior.  The full original-HyRec block contains adjacent Ly-alpha
diffusion edges, real-to-virtual and virtual-to-real source couplings, and the
completed real/virtual algebra on those same frequencies.  The v0.74 COM--KHW
operator already owns nonlinear stimulated redistribution on the interior.
Therefore the naive full residual

\[
R_{\rm naive}=R_{\rm native}^{\rm full}+R_{\rm COM}^{\rm interior}
+R_{\rm atomic}^{\rm full}
\]

has duplicate physical owners.

A mathematically admissible target contract has the form

\[
R=R_{\rm native}^{\rm exterior}
 +R_{\rm COM}^{\rm interior}
 +R_{\rm interface}^{\rm cross}
 +R_{\rm atomic}^{\rm ext/int},
\]

where the two cross-interface diffusion edges are evaluated exactly once by the
interface owner, the interior atomic source is deposited into the COM
representation, and the completed native algebra is replaced by an exterior
Schur block.  This is a contract witness, not an implementation claim.

## Completion rule

The native/COM owner swap is complete only when the replacement residual,
analytic JVP, photon-number and photon/atom energy ledger, four-force ownership,
restart state, and source parity are present in the same durable stage.  Until
then full dynamic atomic/native/COM macro construction fails closed.
"""
    report = f"""
# PR-05C2C1B2B1E1B0 research report

## Decision

`{STATUS}`

The proposed immediate dynamic atomic/history macro is blocked before nonlinear
solution.  This is not a solver-convergence failure.  It is a process-ownership
failure: the full original-HyRec native block and the v0.74 COM interior act on
the same physical frequency support.

## Quantitative evidence

- Native spikes in COM support: **{current.com_interior_native_count}**, indices
  `{current.com_interior_native_indices[0]}..{current.com_interior_native_indices[-1]}`.
- Adjacent native diffusion edges: **{current.diffusion_inside_edge_count}**
  interior, **{current.diffusion_cross_edge_count}** crossing, and
  **{current.diffusion_outside_edge_count}** exterior.
- Canonical Aup rate mass in the COM interior:
  **{current.canonical_up_rate_interior_fraction:.9%}**.
- Canonical Adn rate mass in the COM interior:
  **{current.canonical_down_rate_interior_fraction:.9%}**.
- Absolute real-to-virtual coupling fraction in the interior:
  **{current.real_to_virtual_abs_interior_fraction:.9%}**.
- Absolute virtual-to-real coupling fraction in the interior:
  **{current.virtual_to_real_abs_interior_fraction:.9%}**.

The result is insensitive to any inferred native cell width because no such
width is introduced.  The obstruction follows from the canonical point-spike
centres and the source matrices themselves.

## Claim boundary

Durable: support census, overlap theorem, fail-closed production gate, explicit
target ownership contract, tests, plots, CSV/NPZ evidence.

Not claimed: exterior Schur operator implementation, owner swap, full dynamic
atomic macro, accepted-history append, or full Bianchi--HyRec endpoint.
"""
    next_plan = r"""
# PR-05C2C1B2B1E1C split-domain replacement plan

## Objective

Replace overlapping full-native/interior-COM ownership by an explicit
exterior-native / interior-COM / interface-crossing contract at the locked
\(z\simeq1100\) Bianchi-II state.

## C1. Exact support registry

Use the canonical point-spike indices `136..143` as the interior native set.
Do not infer finite native cells.  Freeze the two cross edges `(135,136)` and
`(143,144)` as interface-owned processes.

## C2. Native exterior operator

Construct an exterior-only primitive native matrix.  Eliminate the interior
virtual variables with a source-derived Schur complement or expose them as COM
source variables.  Prove primitive/exterior-Schur parity on exterior observables.

## C3. Interior atomic deposition

Route one-photon and canonical two-photon/Raman real--virtual source terms whose
point support lies inside the COM domain into the COM representation.  Preserve
nonnegative paired rates, detailed balance, and analytic JVPs.

## C4. Cross-interface diffusion

Represent the two crossing diffusion edges as a single-owner interface packet.
Apply equal and opposite photon-number and exact photon-energy entries to the
adjacent representations; pure representation crossing has zero atom source.

## C5. Owner swap gate

The old full-native terms may be disabled only in the same commit that provides:

- replacement residual;
- analytic JVP;
- photon-number, energy, and four-force ledger;
- restart serialization;
- primitive/direct/Schur parity;
- interface-off and FLRW-limit parity.

## C6. Return to the dynamic macro

Only after C1--C5 pass may the source-derived v0.73 parent and the v0.74 COM
root be coupled to dynamic atomic populations and typed history.  Preconditioner
and Rust work remain deferred until that full physical residual is admissible.
"""
    markdown_write(FORMALISM, formalism)
    markdown_write(REPORT, report)
    markdown_write(NEXT_PLAN, next_plan)
    for target in (FORMALISM, REPORT, NEXT_PLAN):
        shutil.copy2(target, EXPANDED / target.name)

    phase_docs = {
        "01_RESEARCH_CONTRACT.md": """
# 01 Research contract

Question: may the v0.74 COM interior root be coupled directly to the complete
original-HyRec atomic/native/history block without duplicate physical owners?
Success requires a point-support census, a process-ownership matrix, exact
source fractions, counterexamples, and a fail-closed code contract.
""",
        "02_EVIDENCE_ACQUISITION.md": """
# 02 Evidence acquisition

Primary evidence is the canonical October-2012 original-HyRec source snapshot,
the v0.50/v0.74 COM--KHW operator, the v0.55 interface registry, the v0.61 typed
history owner, and source matrices `Tvv`, `Tvr`, `Trv`, `Aup`, `Adn`.  External
literature is used only to justify representation-local states coupled by a
single interface flux; it does not replace repository evidence.
""",
        "03_CLAIM_SOURCE_AUDIT.md": """
# 03 Claim/source audit

Source-derived: virtual point centres, native diffusion graph, real/virtual
source matrices, COM support, interface faces.  Derived here: exact support
classification and ownership obstruction.  Not source-derived: any native cell
width or empirical remap; both remain forbidden.
""",
        "04_HYPOTHESIS_SPACE.md": """
# 04 Hypothesis space

H_A: full native plus COM interior is admissible. Rejected by overlapping
support and process owners.  H_B: only the atomic source overlaps. Rejected;
native A1s diffusion and completed Tvv also overlap.  H_C: an
exterior-native/interior-COM/interface split can be admissible. Survives as a
contract witness, pending implementation.
""",
        "05_ADVERSARIAL_REVIEW.md": """
# 05 Adversarial review

Attacks include zero-width versus inferred-cell ambiguity, tiny-rate masking,
turning off both owners, assigning a cross edge twice, leaving history unowned,
and interpreting a contract witness as implemented physics.  The audit uses
point support only, counts all nonzero edges, and fails closed on overlap or
missing ownership.
""",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": """
# 06 validation and dimensional closure

Doppler `x` and support fractions are dimensionless.  `Aup`, `Adn`, `Tvv`,
`Tvr`, and `Trv` have units s^-1 in the source representation.  The audit does
not form a physical action by summing incompatible representations; it only
classifies support and owner identity.  Metric `(-,+,+,+)`, ordinary Hz and
explicit `c,h,k_B` remain unchanged.
""",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"""
# 07 Verification design and results

Eight native point states lie in the COM domain.  Six nonzero native diffusion
edges are interior, two cross the interfaces, and seventy are exterior.  Aup
and Adn interior fractions are {current.canonical_up_rate_interior_fraction:.9%}
and {current.canonical_down_rate_interior_fraction:.9%}.  Current and naive
configs fail; only the explicit split-domain contract witness passes.
""",
        "08_EXTERNAL_GATE.md": """
# 08 External gate

A full dynamic macro remains blocked until the exterior native operator,
interior COM atomic deposition, cross-interface packet, residual, analytic JVP,
conservation ledger, and restart state coexist.  No fitted normalization,
centre-derived native cells, or silent double ownership is permitted.
""",
        "09_FORMALIZATION.md": """
# 09 Formalization

The executable contract is implemented in
`trajectory.dynamic_macro_ownership`.  It is a fail-closed precondition for
constructing the future dynamic macro, not a duplicate solver.
""",
        "10_CLOSEOUT_AND_HANDOFF.md": f"""
# 10 Closeout and handoff

The bounded result is `{STATUS}`.  Next is the split-domain replacement stage;
dynamic atomic/history macro solution, preconditioner selection, and Rust
optimization remain deferred.
""",
    }
    for name, text in phase_docs.items():
        markdown_write(EXPANDED / name, text)

    write_json(
        EXPANDED / "CLAIM_BOUNDARY.json",
        {
            "complete": [
                "canonical point-support overlap census",
                "process ownership matrix",
                "fail-closed dynamic macro readiness gate",
                "explicit split-domain target contract witness",
            ],
            "not_complete": [
                "exterior native Schur operator",
                "interior atomic source deposition",
                "cross-edge replacement implementation",
                "full dynamic atomic/native/history macro",
                "accepted history append",
            ],
        },
    )
    write_json(
        EXPANDED / "HARD_GATE_LEDGER.json",
        {
            "status": STATUS,
            "current_v074_macro_ready": False,
            "naive_dynamic_atomic_macro_ready": False,
            "contract_witness_ready": True,
            "contract_witness_is_implementation_evidence": False,
            "no_fitted_normalization": True,
            "no_native_cell_inference": True,
            "owner_swap_required_before_dynamic_macro": True,
        },
    )
    write_json(
        EXPANDED / "SOURCE_PROVENANCE.json",
        {
            "source_snapshot": str(SOURCE.relative_to(ROOT)),
            "source_snapshot_sha256": sha256(SOURCE),
            "research_harness": research_receipt,
            "coding_harness": coding_receipt,
            "canonical_hyrec_archive": "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip",
            "canonical_hyrec_archive_sha256": "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27",
        },
    )
    write_json(
        EXPANDED / "HARNESS_EXECUTION_RECEIPT.json",
        {"research": research_receipt, "coding": coding_receipt, "sequence": ["research", "coding"]},
    )
    write_json(
        EXPANDED / "PR05C2C1B2B1E1B0_ledger.json",
        {
            "classification": "PR05C2C1B2B1E1B0_LEDGER",
            "stage": STAGE,
            "status": STATUS,
            "generated_utc": generated_utc,
            "metrics": metrics,
            "claim_boundary": json.loads((EXPANDED / "CLAIM_BOUNDARY.json").read_text()),
            "next": "PR-05C2C1B2B1E1C split-domain replacement",
        },
    )

    shutil.copy2(ROOT / "state/PR05C2C1B2B1E1B0_TDD_RED.log", EXPANDED / "TDD_RED.log")
    shutil.copy2(ROOT / "state/PR05C2C1B2B1E1B0_TDD_GREEN.log", EXPANDED / "TDD_GREEN.log")

    verifier = f'''#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/"NUMERICAL_METRICS.json").read_text())
assert m["status"]=={STATUS!r}
assert m["native_virtual_count"]==311
assert m["com_interior_native_count"]==8
assert m["com_interior_native_indices"]==list(range(136,144))
assert m["diffusion_inside_edge_count"]==6
assert m["diffusion_cross_edge_count"]==2
assert m["diffusion_outside_edge_count"]==70
assert m["canonical_up_rate_interior_fraction"]>0.97
assert m["canonical_down_rate_interior_fraction"]>0.97
assert m["real_to_virtual_abs_interior_fraction"]>0.90
assert m["virtual_to_real_abs_interior_fraction"]>0.90
assert not m["current_v074_ready"]
assert not m["naive_dynamic_atomic_ready"]
assert m["contract_witness_ready"]
assert m["contract_witness_only"]
assert m["no_fitted_normalization"]
assert m["no_native_cell_inference"]
assert m["dynamic_macro_not_executed"]
assert len(list(csv.DictReader((ROOT/"NATIVE_POINT_SUPPORT.csv").open())))==311
with np.load(ROOT/"pr05c2c1b2b1e1b0_dynamic_macro_ownership_v075.npz") as data:
    assert data["energy_eV"].shape==(311,)
    assert int(np.sum(data["inside_com_support"]))==8
for line in (ROOT/"MANIFEST_SHA256.txt").read_text().splitlines():
    digest,name=line.split("  ",1)
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
print(m["status"])
'''
    verifier_path = EXPANDED / "verify_PR05C2C1B2B1E1B0.py"
    verifier_path.write_text(verifier, encoding="utf-8")
    verifier_path.chmod(0o755)

    # Copy numerical payload to repository data before the artifact manifest.
    shutil.copy2(EXPANDED / "pr05c2c1b2b1e1b0_dynamic_macro_ownership_v075.npz", DATA)

    manifest_lines = []
    for path in sorted(EXPANDED.rglob("*")):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            manifest_lines.append(f"{sha256(path)}  {path.relative_to(EXPANDED)}")
    (EXPANDED / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    deterministic_zip(EXPANDED, BUNDLE)

    # Compact self-check.
    check = subprocess.run([sys.executable, str(verifier_path)], cwd=EXPANDED, check=False)
    if check.returncode:
        raise SystemExit(check.returncode)
    print(json.dumps({"status": STATUS, "artifact": str(BUNDLE), "sha256": sha256(BUNDLE)}))


if __name__ == "__main__":
    main()
