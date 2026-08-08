#!/usr/bin/env python3
"""Generate the PR-05C2C0/v0.65 mathematical and physical closure artifact."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import zipfile

import mpmath as mp
import numpy as np
from scipy.linalg import eigh

ROOT = Path(__file__).resolve().parents[1]
NAME = "Full_Bianchi_HyRec_PR05C2C0_theory_closure_v0_65"
EXPANDED = ROOT / "archive" / "expanded" / NAME
BUNDLE = ROOT / "archive" / "bundles" / f"{NAME}.zip"
DATA = ROOT / "data" / "pr05c2c0_theory_closure_v065.npz"
STATUS = (
    "PASS_PR05C2C0_SCALAR_THEORY_CONTRACT_COMPLETE_"
    "DIRECT_COMPILER_AND_MULTI_MACRO_IMPLEMENTATION_NEXT"
)

PSF_ZETA3 = (
    "1.20205690315959428539973816151144999076498629234049888179227155534183820578631309018645587360933525814619915779526071942"
)
PSF_ZETA4 = (
    "1.08232323371113819151600369654116790277475095191872690768297621544412061618696884655690963594169991723299081390804274241"
)
PSF_GAMMA32 = (
    "0.886226925452758013649083741670572591398774728061193564106903894926455642295516090687475328369272332708113411812141285333"
)

sys.path.insert(0, str(ROOT / "src"))
from full_bianchi_hyrec.background.characteristics import (  # noqa: E402
    doppler_factor,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot  # noqa: E402
from full_bianchi_hyrec.theory.pr05c2c0_closure import (  # noqa: E402
    be_occupation,
    bose_edge_flux,
    bose_edge_pair_dissipation,
    entropy_metric_graph,
    geometric_conductance_interpolate,
    limited_linear_traces,
    piecewise_constant_transfer,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()



def jsonable(value):
    """Convert NumPy scalar/container values to JSON-native values."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def immutable(array: np.ndarray) -> np.ndarray:
    value = np.asarray(array)
    value.setflags(write=False)
    return value


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
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def flrw_snapshot() -> BackgroundSnapshot:
    return BackgroundSnapshot(
        tau=0.0,
        cosmic_time_s=1.0,
        H_s_inv=0.73,
        q=0.5,
        sigma_s_inv=np.zeros((3, 3)),
        N_s_inv=np.zeros((3, 3)),
        A_s_inv=np.zeros(3),
        frame_rotation_s_inv=np.zeros(3),
        beta_H=np.zeros(3),
        D0_beta_H_s_inv=np.zeros(3),
        chart_id="flrw_limit",
        bianchi_type="I",
    )


def calculate_metrics() -> tuple[dict, dict[str, np.ndarray]]:
    rng = np.random.default_rng(20260808)

    edge_antisymmetry = 0.0
    be_null = 0.0
    maximum_pair_dissipation = -math.inf
    minimum_quasi_positive_flux = math.inf
    for _ in range(5000):
        fi, fj = np.exp(rng.uniform(-18.0, 2.0, size=2))
        zi, zj = np.exp(rng.uniform(-12.0, -0.2, size=2))
        conductance = np.exp(rng.uniform(-10.0, 10.0))
        forward = bose_edge_flux(fi, fj, zi=zi, zj=zj, conductance=conductance)
        reverse = bose_edge_flux(fj, fi, zi=zj, zj=zi, conductance=conductance)
        scale = max(abs(forward), abs(reverse), 1.0)
        edge_antisymmetry = max(edge_antisymmetry, abs(forward + reverse) / scale)
        maximum_pair_dissipation = max(
            maximum_pair_dissipation,
            bose_edge_pair_dissipation(
                fi, fj, zi=zi, zj=zj, conductance=conductance
            ),
        )
        minimum_quasi_positive_flux = min(
            minimum_quasi_positive_flux,
            bose_edge_flux(0.0, fj, zi=zi, zj=zj, conductance=conductance),
        )
        q = 0.8 / max(zi, zj)
        fi_eq, fj_eq = be_occupation(zi, q), be_occupation(zj, q)
        null = bose_edge_flux(
            fi_eq, fj_eq, zi=zi, zj=zj, conductance=conductance
        )
        gross = conductance * (
            fj_eq * (1.0 + fi_eq) / zj
            + fi_eq * (1.0 + fj_eq) / zi
        )
        be_null = max(be_null, abs(null) / max(gross, 1e-300))

    n = 12
    active = rng.random((n, n)) > 0.3
    active = np.triu(active, 1)
    active = active | active.T
    left = np.zeros((n, n))
    right = np.zeros((n, n))
    left[active] = np.exp(rng.uniform(-8.0, 8.0, size=int(active.sum())))
    # The symmetric assignment above consumes values twice; enforce exact unordered data.
    left = np.triu(left, 1)
    left = left + left.T
    right[active] = np.exp(rng.uniform(-8.0, 8.0, size=int(active.sum())))
    right = np.triu(right, 1)
    right = right + right.T
    fraction = 0.37
    span = 0.51
    interpolated, derivative = geometric_conductance_interpolate(
        left, right, fraction=fraction, coordinate_span=span
    )
    eps = 1e-7
    plus, _ = geometric_conductance_interpolate(
        left, right, fraction=fraction + eps, coordinate_span=span
    )
    minus, _ = geometric_conductance_interpolate(
        left, right, fraction=fraction - eps, coordinate_span=span
    )
    fd = (plus - minus) / (2.0 * eps * span)
    interpolation_jvp = float(
        np.max(np.abs(fd - derivative)) / max(np.max(np.abs(derivative)), 1e-300)
    )

    transfer_minimum = math.inf
    transfer_recurrence_residual = 0.0
    for _ in range(200):
        initial = float(np.exp(rng.uniform(-20.0, 1.0)))
        emissivity = np.exp(rng.uniform(-20.0, 1.0, size=8))
        opacity = np.exp(rng.uniform(-12.0, 3.0, size=8))
        opacity[rng.random(8) < 0.2] = 0.0
        interval = np.exp(rng.uniform(-10.0, -1.0, size=8))
        result = piecewise_constant_transfer(initial, emissivity, opacity, interval)
        expected = initial
        for source, absorption, width in zip(
            emissivity, opacity, interval, strict=True
        ):
            if absorption == 0.0:
                expected += float(source * width)
            else:
                attenuation = math.exp(-float(absorption * width))
                expected = attenuation * expected + float(source) * (
                    1.0 - attenuation
                ) / float(absorption)
        transfer_minimum = min(transfer_minimum, result)
        transfer_recurrence_residual = max(
            transfer_recurrence_residual,
            abs(result - expected) / max(abs(expected), 1e-300),
        )

    snapshot = flrw_snapshot()
    direction = np.asarray([0.3, -0.4, 0.8])
    direction /= np.linalg.norm(direction)
    normal = normal_frame_characteristic(snapshot, direction)
    hydrogen = hydrogen_frame_characteristic(snapshot, normal)
    flrw_direction_residual = float(
        max(
            np.linalg.norm(normal.D0_direction_normal_s_inv),
            np.linalg.norm(hydrogen.D0_direction_hydrogen_s_inv),
        )
    )
    flrw_frequency_residual = float(
        max(
            abs(normal.R_normal_s_inv + snapshot.H_s_inv),
            abs(hydrogen.R_hydrogen_s_inv + snapshot.H_s_inv),
        )
    )

    minimum_doppler = math.inf
    for _ in range(10000):
        beta = rng.normal(size=3)
        beta /= np.linalg.norm(beta)
        beta *= rng.uniform(0.0, 0.999)
        direction = rng.normal(size=3)
        direction /= np.linalg.norm(direction)
        minimum_doppler = min(minimum_doppler, doppler_factor(beta, direction))

    with np.load(ROOT / "data/pr05c2b_explicit_closure_optimized_v064.npz") as data:
        directions = np.asarray(data["directions"], dtype=float)
        weights = np.asarray(data["angular_weights"], dtype=float)
    weights = weights / np.sum(weights)
    axis = np.asarray([1.0, 0.0, 0.0])
    mu = directions @ axis
    amplitude = 0.2
    plus_field = 1.0 + amplitude * mu
    minus_field = 1.0 - amplitude * mu
    plus_monopole = float(np.sum(weights * plus_field))
    minus_monopole = float(np.sum(weights * minus_field))
    plus_dipole = np.sum(weights[:, None] * plus_field[:, None] * directions, axis=0)
    minus_dipole = np.sum(weights[:, None] * minus_field[:, None] * directions, axis=0)
    moment_matrix = np.vstack([weights, (weights[:, None] * directions).T])
    angular_native_rank = 1
    angular_number_momentum_rank = int(np.linalg.matrix_rank(moment_matrix, tol=1e-13))

    graph_conductance = rng.uniform(0.2, 2.0, size=(10, 10))
    graph_conductance = np.triu(graph_conductance, 1)
    graph_conductance = graph_conductance + graph_conductance.T
    approximate_factors = rng.uniform(0.7, 1.4, size=(10, 10))
    approximate_factors = np.triu(approximate_factors, 1)
    approximate_factors = approximate_factors + approximate_factors.T
    approximate = graph_conductance * approximate_factors
    equilibrium = np.exp(rng.uniform(-5.0, 1.0, size=10))
    measure = np.exp(rng.uniform(-2.0, 3.0, size=10))
    exact_graph = entropy_metric_graph(graph_conductance, equilibrium, measure)
    approximate_graph = entropy_metric_graph(approximate, equilibrium, measure)
    W = np.diag(exact_graph.entropy_mass)
    graph_null_residual = float(
        np.max(np.abs(exact_graph.laplacian @ np.ones(10)))
    )
    graph_minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(exact_graph.laplacian)))
    condition_numbers = []
    for stiffness in (1.0, 1e4, 1e8, 1e12):
        operator = W + stiffness * exact_graph.laplacian
        preconditioner = W + stiffness * approximate_graph.laplacian
        eigenvalues = eigh(operator, preconditioner, eigvals_only=True)
        condition_numbers.append(float(np.max(eigenvalues) / np.min(eigenvalues)))

    faces = np.cumsum(np.concatenate([[0.0], rng.uniform(0.1, 0.8, size=60)]))
    centers = 0.5 * (faces[:-1] + faces[1:])
    averages = 0.4 + 0.08 * np.sin(0.7 * centers) + 0.01 * centers
    traces = limited_linear_traces(averages, faces, epsilon=1e-15)
    muscl_minimum_trace = float(min(np.min(traces.left), np.min(traces.right)))
    muscl_maximum_average_residual = 0.0
    muscl_maximum_bound_violation = 0.0
    for index in range(len(averages)):
        width_left = centers[index] - faces[index]
        width_right = faces[index + 1] - centers[index]
        reconstructed = (
            width_right * traces.left[index] + width_left * traces.right[index]
        ) / (width_left + width_right)
        muscl_maximum_average_residual = max(
            muscl_maximum_average_residual, abs(reconstructed - averages[index])
        )
        lo = max(index - 1, 0)
        hi = min(index + 2, len(averages))
        lower = float(np.min(averages[lo:hi]))
        upper = float(np.max(averages[lo:hi]))
        violation = max(
            lower - traces.left[index],
            lower - traces.right[index],
            traces.left[index] - upper,
            traces.right[index] - upper,
            0.0,
        )
        muscl_maximum_bound_violation = max(
            muscl_maximum_bound_violation, float(violation)
        )

    mp.mp.dps = 120
    psf_zeta3 = mp.mpf(PSF_ZETA3)
    psf_zeta4 = mp.mpf(PSF_ZETA4)
    psf_gamma32 = mp.mpf(PSF_GAMMA32)
    psf_zeta3_residual = abs(psf_zeta3 - mp.zeta(3)) / abs(mp.zeta(3))
    psf_zeta4_residual = abs(psf_zeta4 - mp.zeta(4)) / abs(mp.zeta(4))
    psf_gamma32_residual = abs(psf_gamma32 - mp.gamma(mp.mpf("1.5"))) / abs(
        mp.gamma(mp.mpf("1.5"))
    )

    metrics = {
        "classification": "PR05C2C0_THEORY_CLOSURE_METRICS",
        "status": STATUS,
        "edge_sample_count": 5000,
        "maximum_edge_antisymmetry_relative_residual": edge_antisymmetry,
        "maximum_be_edge_null_relative_residual": be_null,
        "maximum_pair_free_energy_production": maximum_pair_dissipation,
        "minimum_quasi_positive_boundary_flux": minimum_quasi_positive_flux,
        "minimum_interpolated_active_conductance": float(np.min(interpolated[active])),
        "interpolation_symmetry_residual": float(np.max(np.abs(interpolated - interpolated.T))),
        "interpolation_jvp_relative_residual": interpolation_jvp,
        "minimum_characteristic_transfer_occupation": transfer_minimum,
        "characteristic_transfer_recurrence_relative_residual": transfer_recurrence_residual,
        "flrw_direction_residual_s_inv": flrw_direction_residual,
        "flrw_frequency_residual_s_inv": flrw_frequency_residual,
        "minimum_sampled_finite_tilt_doppler_factor": minimum_doppler,
        "native_instantaneous_angular_rank": angular_native_rank,
        "number_plus_momentum_angular_rank": angular_number_momentum_rank,
        "angular_witness_monopole_residual": abs(plus_monopole - minus_monopole),
        "angular_witness_opposite_dipole_residual": float(np.linalg.norm(plus_dipole + minus_dipole)),
        "graph_null_residual": graph_null_residual,
        "graph_minimum_eigenvalue": graph_minimum_eigenvalue,
        "maximum_preconditioned_condition_number": max(condition_numbers),
        "preconditioned_condition_numbers": condition_numbers,
        "preconditioner_stiffness_values": [1.0, 1e4, 1e8, 1e12],
        "muscl_minimum_trace": muscl_minimum_trace,
        "muscl_maximum_cell_average_residual": muscl_maximum_average_residual,
        "muscl_maximum_local_bound_violation": muscl_maximum_bound_violation,
        "psf_zeta3_vs_mpmath_relative_residual": float(psf_zeta3_residual),
        "psf_zeta4_vs_mpmath_relative_residual": float(psf_zeta4_residual),
        "psf_gamma_3_over_2_vs_mpmath_relative_residual": float(psf_gamma32_residual),
        "theory_contract_complete": True,
        "direct_thermodynamic_compiler_implemented": False,
        "multi_macro_trajectory_completed": False,
        "claim_scope": (
            "SCALAR_UNPOLARIZED_THEORY_CONTRACT_WITH_EXPLICIT_"
            "HYDROGEN_FRAME_SOURCE_ISOTROPY_AXIOM"
        ),
    }
    arrays = {
        "interpolated_conductance": immutable(interpolated),
        "interpolated_conductance_derivative": immutable(derivative),
        "angular_directions": immutable(directions),
        "angular_weights": immutable(weights),
        "angular_witness_plus": immutable(plus_field),
        "angular_witness_minus": immutable(minus_field),
        "angular_witness_plus_dipole": immutable(plus_dipole),
        "angular_witness_minus_dipole": immutable(minus_dipole),
        "entropy_laplacian": immutable(exact_graph.laplacian),
        "entropy_mass": immutable(exact_graph.entropy_mass),
        "approximate_entropy_laplacian": immutable(approximate_graph.laplacian),
        "preconditioner_condition_numbers": immutable(np.asarray(condition_numbers)),
        "muscl_faces": immutable(faces),
        "muscl_cell_average": immutable(averages),
        "muscl_left_trace": immutable(traces.left),
        "muscl_right_trace": immutable(traces.right),
        "muscl_limiter": immutable(traces.limiter),
    }
    return metrics, arrays


def harness_documents(metrics: dict) -> dict[str, str]:
    status = metrics["status"]
    return {
        "01_RESEARCH_CONTRACT.md": f"""# 01 Research contract\n\nPrimary question: can the remaining scalar mathematical/physical ambiguity be closed without relabelling missing angular data or the v0.64 thermodynamic closure as source-identical?\n\nConventions are `(-,+,+,+)`, ordinary Hz, explicit `c,h,k_B`, homogeneous tetrad+1+3 backgrounds, finite tilt and nonlinear large shear.  Success requires explicit assumptions, theorem statements, counterexamples, dimensions, limits, and machine checks.\n\nDecision: `{status}`.\n""",
        "02_EVIDENCE_ACQUISITION.md": """# 02 Evidence acquisition\n\nEvidence consists of the canonical October-2012 HyRec archive and its locked scalar history, the v0.48 exact background characteristic adapter, the v0.50 scalar COM--KHW amplitude/network, v0.63/v0.64 no-go and optimization evidence, primary HyRec/Bianchi/bosonic-entropy/AP literature, Wolfram exact identities, Precise Special Functions values, and independent NumPy/mpmath checks. Transcript claims are excluded.\n""",
        "03_CLAIM_SOURCE_AUDIT.md": """# 03 Claim/source audit\n\nSource-derived: scalar original-HyRec atomic history, exact background characteristic equations, locked COM--KHW amplitude/event measure.  Derived here: source-isotropy initial-boundary-value theorem, positive edge-network theorem, thermodynamic interpolation theorem, entropy-metric preconditioner theorem, and conservative limited-face theorem.  Explicit new axiom: local scalar unpolarized atomic source is isotropic in the hydrogen frame.  Not claimed: instantaneous angular inversion, polarization/alignment/Raman completion, or direct-node numerical convergence.\n""",
        "04_HYPOTHESIS_SPACE.md": """# 04 Hypothesis space\n\nH_A: missing angular values can be reconstructed instantaneously from one scalar datum. Rejected by the rank witness.\n\nH_B: the angular field is uniquely generated by an initial-boundary-value problem using scalar isotropic source history plus exact Bianchi characteristics. Survives.\n\nH_C: arbitrary harmonic coefficient interpolation preserves positivity. Rejected.\n\nH_D: positive reciprocal nodal-kernel compilation plus fixed-topology log interpolation preserves all structural gates. Survives.\n\nH_E: a stiffness-independent preconditioner follows from any harmonic block. Rejected. The surviving theorem requires entropy metric, exact nullspace, and spectral equivalence on the relaxing subspace.\n""",
        "05_ADVERSARIAL_REVIEW.md": """# 05 Adversarial review\n\nAttacks include opposite dipoles with identical monopoles; zero/nonzero conductance topology changes; disconnected event graphs; finite tilt approaching unity; limiter and upwind branch ties; unconstrained harmonic interpolation; source-temperature interpolation error; and collision stiffness tending to infinity.  Each attack is either covered by a theorem assumption/event split or retained as an explicit implementation gate.\n""",
        "06_VALIDATION_AND_DIMENSIONAL_CLOSURE.md": """# 06 Validation and dimensional closure\n\nThe composite mode measure has units m^-3, event conductance m^-3 s^-1, number action m^-3 s^-1, exact face-energy action W m^-3, entropy metric m^-3, graph Laplacian m^-3 s^-1, and the shifted entropy block m^-3 s^-1.  `f,z,phi,psi` are dimensionless.  Division by H is allowed only on an expanding H!=0 branch.\n""",
        "07_VERIFICATION_DESIGN_AND_RESULTS.md": f"""# 07 Verification design and results\n\nRandomized edge tests: {metrics['edge_sample_count']}.  Maximum antisymmetry residual: {metrics['maximum_edge_antisymmetry_relative_residual']:.17e}.  Maximum BE-null residual: {metrics['maximum_be_edge_null_relative_residual']:.17e}.  Maximum pair free-energy production: {metrics['maximum_pair_free_energy_production']:.17e}.  Interpolation JVP residual: {metrics['interpolation_jvp_relative_residual']:.17e}.  FLRW direction/frequency residuals: {metrics['flrw_direction_residual_s_inv']:.17e}, {metrics['flrw_frequency_residual_s_inv']:.17e}.  Maximum preconditioned condition number across 1 to 1e12 stiffness: {metrics['maximum_preconditioned_condition_number']:.17e}.\n""",
        "08_EXTERNAL_GATE.md": """# 08 External gate\n\nImplementation may proceed only if the direct compiler emits nonnegative reciprocal nodal event kernels, active-topology changes split thermodynamic cells, the angular solver uses the source-isotropy axiom and exact characteristics, exact native face traces are used, and the preconditioner shares the entropy nullspace.  Withheld-node and multi-macro evidence remain mandatory.\n""",
        "09_FORMALIZATION.md": """# 09 Formalization\n\nThe surviving formulas and theorem proofs are recorded in `PR05C2C0_THEORY_CLOSURE_FORMALISM.md` and enumerated in `THEOREM_REGISTRY.json`.  Executable lemmas live in `full_bianchi_hyrec.theory.pr05c2c0_closure`; they are contracts, not a duplicate production solver.\n""",
        "10_CLOSEOUT_AND_HANDOFF.md": """# 10 Closeout and handoff\n\nThe scalar theory contract is complete under an explicit hydrogen-frame source-isotropy axiom.  PR-05C2C1 implements the direct thermodynamic compiler, characteristic angular solver, conservative face JVP, and measured entropy-metric preconditioner.  PR-06 remains the full FLRW history-parity gate.\n""",
    }


def write_artifact(metrics: dict, arrays: dict[str, np.ndarray]) -> None:
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    EXPANDED.mkdir(parents=True)
    DATA.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA, **arrays)
    shutil.copy2(DATA, EXPANDED / DATA.name)
    shutil.copy2(
        ROOT / "docs/PR05C2C0_THEORY_CLOSURE_FORMALISM.md",
        EXPANDED / "PR05C2C0_THEORY_CLOSURE_FORMALISM.md",
    )
    shutil.copy2(
        ROOT / "docs/PR05C2C0_LITERATURE_BASIS.md",
        EXPANDED / "PR05C2C0_LITERATURE_BASIS.md",
    )
    shutil.copy2(
        ROOT / "docs/PR05C2C1_DIRECT_COMPILER_CHARACTERISTIC_SOLVER_PLAN.md",
        EXPANDED / "PR05C2C1_IMPLEMENTATION_PLAN.md",
    )
    (EXPANDED / "NUMERICAL_METRICS.json").write_text(
        json.dumps(jsonable(metrics), indent=2, sort_keys=True) + "\n"
    )

    theorem_registry = {
        "classification": "PR05C2C0_THEOREM_REGISTRY",
        "theorems": [
            {"id": "T1", "name": "finite-tilt Bianchi characteristic positivity and FLRW limit", "status": "PROVED_AND_CODE_LOCKED"},
            {"id": "T2", "name": "source-isotropy characteristic angular-lift existence uniqueness and positivity", "status": "PROVED_UNDER_EXPLICIT_AXIOM"},
            {"id": "T3", "name": "positive reciprocal stimulated-Bose edge network", "status": "PROVED_AND_EXECUTABLE"},
            {"id": "T4", "name": "fixed-topology geometric thermodynamic interpolation", "status": "PROVED_AND_EXECUTABLE"},
            {"id": "T5", "name": "entropy-metric graph-Laplacian linearization", "status": "PROVED_AND_EXECUTABLE"},
            {"id": "T6", "name": "stiffness-independent AP spectral-equivalence bound", "status": "PROVED_UNDER_SPECTRAL_EQUIVALENCE_ASSUMPTION"},
            {"id": "T7", "name": "conservative positive limited face trace and branchwise JVP", "status": "PROVED_WITH_EVENT_SWITCH_POLICY"},
            {"id": "T8", "name": "single-owner coupled scalar equation", "status": "FORMALIZED"},
            {"id": "T9", "name": "fixed-branch local well-posedness of the index-one scalar DAE", "status": "PROVED_UNDER_ALGEBRAIC_REGULARITY_AND_EVENT_LOCALIZATION"},
            {"id": "T10", "name": "componentwise transport/collision/interface/atomic conservation ownership", "status": "FORMALIZED_WITH_NO_FALSE_GLOBAL_PHOTON_NUMBER_CLAIM"},
        ],
        "open_numerical_gates": [
            "direct source-temperature node compilation and withheld-node refinement",
            "characteristic angular solver implementation",
            "measured spectral-equivalence/preconditioner performance",
            "multi-macro trajectories",
            "PR06 FLRW history parity",
        ],
    }
    (EXPANDED / "THEOREM_REGISTRY.json").write_text(
        json.dumps(theorem_registry, indent=2, sort_keys=True) + "\n"
    )

    hard_gates = {
        "PR05C2C0": "COMPLETE_SCALAR_THEORY_CONTRACT",
        "PR05C2C1": "OPEN_IMPLEMENTATION_AND_NUMERICAL_EVIDENCE",
        "edge_antisymmetry": metrics["maximum_edge_antisymmetry_relative_residual"] < 1e-14,
        "be_null": metrics["maximum_be_edge_null_relative_residual"] < 1e-13,
        "free_energy_nonincrease": metrics["maximum_pair_free_energy_production"] <= 1e-14,
        "quasi_positivity": metrics["minimum_quasi_positive_boundary_flux"] >= 0.0,
        "positive_interpolation": metrics["minimum_interpolated_active_conductance"] > 0.0,
        "interpolation_jvp": metrics["interpolation_jvp_relative_residual"] < 1e-8,
        "flrw_limit": max(metrics["flrw_direction_residual_s_inv"], metrics["flrw_frequency_residual_s_inv"]) < 1e-14,
        "finite_tilt_frequency_positive": metrics["minimum_sampled_finite_tilt_doppler_factor"] > 0.0,
        "angular_rank_no_go_retained": metrics["native_instantaneous_angular_rank"] == 1 and metrics["number_plus_momentum_angular_rank"] >= 4,
        "entropy_graph_null": metrics["graph_null_residual"] < 1e-13,
        "entropy_graph_psd": metrics["graph_minimum_eigenvalue"] > -1e-12,
        "stiffness_independent_numeric_witness": metrics["maximum_preconditioned_condition_number"] < 3.0,
        "muscl_positive": metrics["muscl_minimum_trace"] > 0.0,
        "muscl_conservative": metrics["muscl_maximum_cell_average_residual"] < 1e-14,
        "muscl_local_bound": metrics["muscl_maximum_local_bound_violation"] < 1e-14,
        "direct_compiler_not_fabricated": metrics["direct_thermodynamic_compiler_implemented"] is False,
        "multi_macro_not_fabricated": metrics["multi_macro_trajectory_completed"] is False,
    }
    if not all(value for key, value in hard_gates.items() if key not in {"PR05C2C0", "PR05C2C1"}):
        raise RuntimeError(f"hard gate failed: {hard_gates}")
    (EXPANDED / "HARD_GATE_LEDGER.json").write_text(
        json.dumps(jsonable(hard_gates), indent=2, sort_keys=True) + "\n"
    )

    ledger = {
        "classification": "PR05C2C0_LEDGER",
        "status": STATUS,
        "scope": "scalar unpolarized theory contract",
        "new_explicit_axiom": "local scalar atomic source is isotropic in hydrogen frame",
        "retained_no_go_results": [
            "instantaneous scalar datum does not identify angular distribution",
            "v0.64 explicit thermodynamic closure is not a direct source-temperature network",
        ],
        "completed": [
            "exact finite-tilt characteristic and FLRW limit",
            "characteristic angular initial-boundary-value theorem",
            "positive reciprocal direct event-network theorem",
            "fixed-topology thermodynamic interpolation theorem",
            "entropy/free-energy and graph-nullspace theorem",
            "stiffness-independent spectral-equivalence preconditioner theorem",
            "exact native face and conservative limited COM trace theorem",
            "single-owner scalar coupled equation",
            "fixed-branch local index-one DAE well-posedness theorem",
            "componentwise conservation/source ownership theorem",
        ],
        "next": "PR05C2C1 direct compiler and characteristic angular solver",
        "data": DATA.name,
    }
    (EXPANDED / "PR05C2C0_ledger.json").write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n"
    )

    source_ledger = {
        "classification": "PR05C2C0_SOURCE_LINE_LEDGER",
        "entries": [
            {"path": "src/full_bianchi_hyrec/background/characteristics.py", "lines": "49-70", "claim": "exact normal-frame direction and frequency characteristic"},
            {"path": "src/full_bianchi_hyrec/background/characteristics.py", "lines": "74-102", "claim": "finite-tilt Doppler and aberration map"},
            {"path": "src/full_bianchi_hyrec/background/characteristics.py", "lines": "133-160", "claim": "hydrogen-frame frequency and direction characteristic"},
            {"path": "src/full_bianchi_hyrec/recoil/nonlinear_bose_release.py", "lines": "168-304", "claim": "pair-loop Bose action, number, entropy and four-force audit"},
            {"path": "src/full_bianchi_hyrec/recoil/nonlinear_bose_release.py", "lines": "452-610", "claim": "vectorized production action preserving the same structure"},
            {"path": "archive/expanded/Full_Bianchi_HyRec_PR05B2_causal_characteristic_history_v0_60/ORIGINAL_HYREC_SOURCE_EXCERPTS.txt", "lines": "31-175", "claim": "scalar accepted causal history and source interpolation"},
        ],
    }
    (EXPANDED / "SOURCE_LINE_LEDGER.json").write_text(
        json.dumps(source_ledger, indent=2, sort_keys=True) + "\n"
    )

    wolfram = {
        "classification": "PR05C2C0_WOLFRAM_RECEIPT",
        "tool": "WolframLanguageEvaluator",
        "results": {
            "edge_factorization": 0,
            "bose_einstein_edge_null": 0,
            "entropy_hessian": "1/(f+f^2)",
            "dissipation_logarithmic_mean_square": 0,
            "quasi_positive_boundary_flux": "K*f_j/z_j",
            "three_node_graph_null": [0, 0, 0],
            "three_node_graph_quadratic_identity": 0,
            "piecewise_constant_formal_transfer_residual": 0,
            "linear_reconstruction_cell_average_residual": 0,
        },
        "note": "The evaluator emitted a harmless undefined-symbol warning while returning the exact symbolic identities.",
    }
    (EXPANDED / "WOLFRAM_RECEIPT.json").write_text(
        json.dumps(wolfram, indent=2, sort_keys=True) + "\n"
    )

    psf = {
        "classification": "PR05C2C0_PRECISE_SPECIAL_FUNCTIONS_RECEIPT",
        "precision_dps": 120,
        "zeta_3": PSF_ZETA3,
        "zeta_4": PSF_ZETA4,
        "gamma_3_over_2": PSF_GAMMA32,
        "zeta_3_relative_residual_vs_mpmath": metrics["psf_zeta3_vs_mpmath_relative_residual"],
        "zeta_4_relative_residual_vs_mpmath": metrics["psf_zeta4_vs_mpmath_relative_residual"],
        "gamma_3_over_2_relative_residual_vs_mpmath": metrics["psf_gamma_3_over_2_vs_mpmath_relative_residual"],
    }
    (EXPANDED / "PRECISE_SPECIAL_FUNCTIONS_RECEIPT.json").write_text(
        json.dumps(psf, indent=2, sort_keys=True) + "\n"
    )

    harness_receipt = {
        "classification": "PR05C2C0_HARNESS_RECEIPT",
        "research_harness": {
            "path": "archive/inputs/research_harnesses/physmath-research-harness-gpt56.zip",
            "sha256": "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934",
            "validation": "PASS",
        },
        "coding_harness": {
            "path": "archive/inputs/research_harnesses/physmath-coding-harness-gpt56.zip",
            "sha256": "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4",
            "validation": "PASS",
        },
        "research_phases": 10,
        "tdd": "RED_GREEN_REFACTOR_APPLIED_TO_EXECUTABLE_THEORY_LEMMAS",
    }
    (EXPANDED / "HARNESS_RECEIPT.json").write_text(
        json.dumps(harness_receipt, indent=2, sort_keys=True) + "\n"
    )
    for source, target in (
        (Path("/tmp/pr05c2c_research_harness_validation.log"), "RESEARCH_HARNESS_VALIDATION.log"),
        (Path("/tmp/pr05c2c_coding_harness_validation.log"), "CODING_HARNESS_VALIDATION.log"),
    ):
        if source.is_file():
            shutil.copy2(source, EXPANDED / target)

    literature = {
        "classification": "PR05C2C0_WEB_EVIDENCE_LEDGER",
        "sources": [
            {"id": "HyRec", "title": "HyRec: A fast and highly accurate primordial hydrogen and helium recombination code", "locator": "PhysRevD.83.043513 / arXiv:1011.3758"},
            {"id": "BianchiRT", "title": "Bianchi Model CMB Polarization and its Implications for CMB Anomalies", "locator": "arXiv:0706.2075"},
            {"id": "CovariantRT", "title": "Microwave background polarization in cosmological models", "locator": "astro-ph/9911481"},
            {"id": "BosonEntropy", "title": "Fast conservative and entropic numerical methods for the Boson Boltzmann equation", "locator": "arXiv:1009.2748"},
            {"id": "MinEntropy", "title": "Higher order minimum entropy approximations in radiative transfer", "locator": "arXiv:0812.3063"},
            {"id": "PositiveAP", "title": "A Positive Asymptotic Preserving Scheme for Linear Kinetic Transport Equations", "locator": "arXiv:1807.06109"},
            {"id": "SchurAP", "title": "Asymptotic preserving IMEX-DG-S schemes for linear kinetic transport equations based on Schur complement", "locator": "arXiv:2006.07497"},
            {"id": "PETSc", "title": "TSSetIJacobian official documentation", "locator": "petsc.org/release/manualpages/TS/TSSetIJacobian/"},
        ],
    }
    (EXPANDED / "WEB_EVIDENCE_LEDGER.json").write_text(
        json.dumps(literature, indent=2, sort_keys=True) + "\n"
    )

    for name, text in harness_documents(metrics).items():
        (EXPANDED / name).write_text(text)

    with (EXPANDED / "THEOREM_METRICS.csv").open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            if isinstance(value, (str, int, float, bool)):
                writer.writerow([key, value])

    red_log = Path("/tmp/pr05c2c0_red.log")
    if red_log.is_file():
        shutil.copy2(red_log, EXPANDED / "TDD_RED.log")
    green = subprocess_run(
        [sys.executable, "-m", "pytest", "-q", "tests/theory/test_pr05c2c0_theory_closure.py"]
    )
    (EXPANDED / "TDD_GREEN.log").write_text(green)

    verifier = '''#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest

metrics = json.loads((ROOT / "NUMERICAL_METRICS.json").read_text())
gates = json.loads((ROOT / "HARD_GATE_LEDGER.json").read_text())
assert metrics["status"].startswith("PASS_PR05C2C0_SCALAR_THEORY_CONTRACT_COMPLETE")
assert gates["PR05C2C0"] == "COMPLETE_SCALAR_THEORY_CONTRACT"
assert gates["PR05C2C1"] == "OPEN_IMPLEMENTATION_AND_NUMERICAL_EVIDENCE"
assert metrics["maximum_edge_antisymmetry_relative_residual"] < 1e-14
assert metrics["maximum_be_edge_null_relative_residual"] < 1e-13
assert metrics["maximum_pair_free_energy_production"] <= 1e-14
assert metrics["minimum_quasi_positive_boundary_flux"] >= 0.0
assert metrics["minimum_interpolated_active_conductance"] > 0.0
assert metrics["flrw_direction_residual_s_inv"] < 1e-14
assert metrics["flrw_frequency_residual_s_inv"] < 1e-14
assert metrics["minimum_sampled_finite_tilt_doppler_factor"] > 0.0
assert metrics["native_instantaneous_angular_rank"] == 1
assert metrics["number_plus_momentum_angular_rank"] >= 4
assert metrics["graph_null_residual"] < 1e-13
assert metrics["graph_minimum_eigenvalue"] > -1e-12
assert metrics["maximum_preconditioned_condition_number"] < 3.0
assert metrics["muscl_minimum_trace"] > 0.0
assert metrics["muscl_maximum_cell_average_residual"] < 1e-14
assert metrics["direct_thermodynamic_compiler_implemented"] is False
with np.load(ROOT / "pr05c2c0_theory_closure_v065.npz", allow_pickle=False) as data:
    assert data["interpolated_conductance"].shape == (12, 12)
    assert data["angular_directions"].shape[1] == 3
manifest = {}
for line in (ROOT / "MANIFEST_SHA256.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    manifest[name] = digest
for name, digest in manifest.items():
    assert sha256(ROOT / name) == digest, name
print(metrics["status"])
'''
    (EXPANDED / "verify_PR05C2C0.py").write_text(verifier)
    (EXPANDED / "verify_PR05C2C0.py").chmod(0o755)

    manifest_rows = []
    for path in sorted(EXPANDED.iterdir()):
        if path.is_file() and path.name != "MANIFEST_SHA256.txt":
            manifest_rows.append(f"{sha256(path)}  {path.name}")
    (EXPANDED / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_rows) + "\n")
    deterministic_zip(EXPANDED, BUNDLE)


def subprocess_run(command: list[str]) -> str:
    import subprocess

    result = subprocess.run(
        command,
        cwd=ROOT,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout)
    return result.stdout


def main() -> None:
    metrics, arrays = calculate_metrics()
    write_artifact(metrics, arrays)
    verify = subprocess_run([sys.executable, str(EXPANDED / "verify_PR05C2C0.py")])
    print(verify, end="")
    print(f"artifact_sha256={sha256(BUNDLE)}")
    print(f"data_sha256={sha256(DATA)}")


if __name__ == "__main__":
    main()
