#!/usr/bin/env sage
"""Exact Q/libSingular checks; deliberately NONAUTHORITATIVE."""
import json
import sys
from sage.rings.integer import Integer as SageInteger

checks = []

def record(check_id, holds, detail=None):
    item = {"id": check_id, "holds": bool(holds)}
    if detail is not None:
        item["detail"] = detail
    checks.append(item)

def emit(status, code, toolchain):
    if type(code) not in (int, SageInteger):
        raise TypeError(f"unsupported exit-code type: {type(code).__name__}")
    code = int(code)
    report = {
        "schema": "REC_NEXT03_SAGE_SINGULAR_FORMAL_V1",
        "authority": "NONAUTHORITATIVE",
        "physical_authority_status": "NOT_ESTABLISHED",
        "implementation_parity_status": "NOT_ESTABLISHED",
        "status": status,
        "exit_code": code,
        "toolchain": toolchain,
        "arithmetic": "EXACT_RATIONAL_Q",
        "event_surfaces": [
            "CHARACTERISTIC_R_H_ZERO",
            "RED_FACE_V_X_ZERO",
            "BLUE_FACE_V_X_ZERO",
        ],
        "source_claim_inputs": [
            {
                "path": "src/full_bianchi_hyrec/trajectory/directional_face_admission.py",
                "lines": "213-246",
                "scope": "red/blue Doppler-coordinate speeds and half-range signs",
            },
            {
                "path": "src/full_bianchi_hyrec/trajectory/directional_face_admission.py",
                "lines": "340-349",
                "scope": "exact-zero characteristic-rate witness uses R_H",
            },
        ],
        "independent_math_obligations": [
            "CONTENT_COLUMN_CONSERVATION_1T_P_EQ_1T",
            "CONSTANT_STATE_MEASURE_GCL_P_MOLD_EQ_MNEW",
            "DIFFERENTIATED_GCL_AND_CONTENT_JVP",
            "ADJACENT_TWO_NODE_NUMBER_AND_ENERGY",
            "PAIRWISE_DISTINCT_ZERO_EVENT_SURFACES",
        ],
        "authority_firewalls": {
            "remap": "No approved physical 26-node remap matrix is supplied or admitted.",
            "events": "Algebraic counterexamples do not implement localization or restart.",
            "deposition": "Adjacent support/locality is a proposed axiom, not source authority.",
        },
        "checks": checks,
        "failed_check_ids": [item["id"] for item in checks if not item["holds"]],
    }
    sys.stdout.write(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
    raise SystemExit(code)

try:
    from sage.all import QQ, PolynomialRing, matrix, vector
    from sage.version import version as sage_version
except Exception as exc:
    record("sage_libsingular_available", False, type(exc).__name__)
    emit("ENVIRONMENT_UNAVAILABLE_NONAUTHORITATIVE", 69, {})

try:
    sage_version = str(sage_version)
    PolynomialRing(QQ, names=("libsingular_probe",), implementation="singular")
except Exception as exc:
    record("sage_libsingular_available", False, type(exc).__name__)
    emit("ENVIRONMENT_UNAVAILABLE_NONAUTHORITATIVE", 69,
         {"sage": locals().get("sage_version", "UNKNOWN")})

record("sage_libsingular_available", True)

try:
    # P maps old photon contents to new photon contents: N_new=P N_old.
    # 1^T P=1^T conserves number; P m_old=m_new preserves a constant f
    # because N=m f.  These are proposed obligations, not implementation facts.
    names = []
    for prefix in ("p", "dp"):
        names.extend(f"{prefix}{i}{j}" for i in range(3) for j in range(2))
    for prefix, count in (("mn", 3), ("dmn", 3), ("mo", 2), ("dmo", 2),
                          ("N", 2), ("dN", 2)):
        names.extend(f"{prefix}{i}" for i in range(count))
    names.append("fconstant")
    ring = PolynomialRing(QQ, names=names, order="degrevlex", implementation="singular")
    x = ring.gens_dict()
    P = matrix(ring, 3, 2, [x[f"p{i}{j}"] for i in range(3) for j in range(2)])
    dP = matrix(ring, 3, 2, [x[f"dp{i}{j}"] for i in range(3) for j in range(2)])
    mn = vector(ring, [x[f"mn{i}"] for i in range(3)])
    dmn = vector(ring, [x[f"dmn{i}"] for i in range(3)])
    mo = vector(ring, [x[f"mo{i}"] for i in range(2)])
    dmo = vector(ring, [x[f"dmo{i}"] for i in range(2)])
    N = vector(ring, [x[f"N{i}"] for i in range(2)])
    dN = vector(ring, [x[f"dN{i}"] for i in range(2)])

    column_constraints = [sum(P[i, j] for i in range(3)) - 1 for j in range(2)]
    dcolumn_constraints = [sum(dP[i, j] for i in range(3)) for j in range(2)]
    measure_constraints = [sum(P[i, j] * mo[j] for j in range(2)) - mn[i]
                           for i in range(3)]
    dmeasure_constraints = [
        sum(dP[i, j] * mo[j] + P[i, j] * dmo[j] for j in range(2)) - dmn[i]
        for i in range(3)
    ]
    Nnew = P * N
    dNnew = P * dN + dP * N
    number_residual = sum(Nnew) - sum(N)
    number_certificate = sum(column_constraints[j] * N[j] for j in range(2))
    dnumber_residual = sum(dNnew) - sum(dN)
    dnumber_certificate = sum(
        dcolumn_constraints[j] * N[j] + column_constraints[j] * dN[j]
        for j in range(2)
    )
    constant_symbol = x["fconstant"]
    constant_recovery_residual = P * (constant_symbol * mo) - constant_symbol * mn
    constant_recovery_certificate = constant_symbol * vector(ring, measure_constraints)
    dconstant_recovery_residual = (
        dP * (constant_symbol * mo) + P * (constant_symbol * dmo)
        - constant_symbol * dmn
    )
    dconstant_recovery_certificate = constant_symbol * vector(ring, dmeasure_constraints)
    record("symbolic_column_gcl_shape", len(column_constraints) == 2)
    record("symbolic_differentiated_column_gcl_shape", len(dcolumn_constraints) == 2)
    record("symbolic_column_gcl_number_certificate",
           (number_residual - number_certificate) == 0)
    record("symbolic_differentiated_column_gcl_jvp_certificate",
           (dnumber_residual - dnumber_certificate) == 0)
    record("symbolic_measure_gcl_constant_recovery_certificate",
           constant_recovery_residual == constant_recovery_certificate)
    record("symbolic_differentiated_measure_gcl_certificate",
           dconstant_recovery_residual == dconstant_recovery_certificate)

    # A nontrivial exact feasible remap and tangent.
    q = lambda numerator, denominator=1: QQ(numerator) / QQ(denominator)
    Pw = matrix(QQ, [[q(3, 4), q(1, 4)], [q(1, 4), q(3, 4)]])
    mold = vector(QQ, [2, 4]); mnew = vector(QQ, [q(5, 2), q(7, 2)])
    dPw = matrix(QQ, [[q(-1, 4), q(1, 8)], [q(1, 4), q(-1, 8)]])
    one2 = vector(QQ, [1, 1]); zero2 = vector(QQ, [0, 0])
    dmold = vector(QQ, [1, -1]); dmnew = vector(QQ, [q(1, 2), q(-1, 2)])
    record("feasible_rational_nonnegative", all(value >= 0 for value in Pw.list()))
    record("feasible_rational_column_gcl", one2 * Pw == one2)
    record("feasible_rational_measure_gcl", Pw * mold == mnew)
    record("feasible_rational_dcolumn_gcl", one2 * dPw == zero2)
    record("feasible_rational_dmeasure_gcl",
           dPw * mold + Pw * dmold == dmnew)
    Nold = vector(QQ, [3, 5]); dNold = vector(QQ, [-2, 1])
    Nnew = Pw * Nold; dNnew = dPw * Nold + Pw * dNold
    record("feasible_rational_content_jvp_number",
           sum(Nnew) == sum(Nold) and sum(dNnew) == sum(dNold))
    fconstant = q(7, 5)
    recovered = vector(QQ, [value / mnew[i]
                            for i, value in enumerate(Pw * (fconstant * mold))])
    record("feasible_rational_f_equals_N_over_m_recovery",
           recovered == vector(QQ, [fconstant, fconstant]))

    # Singular proves a total-measure mismatch has no solution to both GCLs.
    small = PolynomialRing(QQ, names=("a", "b", "c", "d"),
                           order="degrevlex", implementation="singular")
    a, b, c, d = small.gens()
    feasible_ideal = small.ideal([a + c - 1, b + d - 1,
                                  2*a + 4*b - q(5, 2),
                                  2*c + 4*d - q(7, 2)])
    infeasible_ideal = small.ideal([a + c - 1, b + d - 1,
                                    2*a + 4*b - q(5, 2),
                                    2*c + 4*d - 4])
    record("singular_feasible_ideal_nonunit", small(1) not in feasible_ideal)
    record("singular_total_measure_mismatch_unit_ideal",
           small(1) in infeasible_ideal)

    # Adjacent two-node number/energy identities over Q(EL,Es,ER,...).
    energies = PolynomialRing(QQ, names=("EL", "Es", "ER", "dEL", "dEs", "dER"),
                              order="degrevlex", implementation="singular")
    field = energies.fraction_field()
    EL, Es, ER, dEL, dEs, dER = field.gens()
    delta = ER - EL
    bleft = (ER - Es) / delta; bright = (Es - EL) / delta
    dbleft = ((dER - dEs)*delta - (ER - Es)*(dER - dEL)) / delta**2
    dbright = ((dEs - dEL)*delta - (Es - EL)*(dER - dEL)) / delta**2
    record("adjacent_symbolic_number", bleft + bright == 1)
    record("adjacent_symbolic_energy", EL*bleft + ER*bright == Es)
    record("adjacent_symbolic_dnumber", dbleft + dbright == 0)
    record("adjacent_symbolic_denergy",
           dEL*bleft + EL*dbleft + dER*bright + ER*dbright == dEs)
    feasible_weights = (q(5 - 3, 5 - 2), q(3 - 2, 5 - 2))
    infeasible_weights = (q(5 - 6, 5 - 2), q(6 - 2, 5 - 2))
    record("adjacent_feasible_rational_example", feasible_weights == (q(2, 3), q(1, 3)))
    record("adjacent_infeasible_outside_bracket_example",
           min(infeasible_weights) < 0 and sum(infeasible_weights) == 1)

    # Exact counterexamples: the three zero-event surfaces are not identical.
    def face_speed(RH, nu0, width, xface, nudot=0, dlogwidth=0, xdot=0):
        return ((nu0 + xface*width)*RH - nudot)/width - xface*dlogwidth - xdot

    RH_only_red = face_speed(q(0), q(10), q(2), q(-1), nudot=q(1))
    RH_only_blue = face_speed(q(0), q(10), q(2), q(1), nudot=q(1))
    record("event_surface_R_H_only_witness",
           RH_only_red != 0 and RH_only_blue != 0,
           {"R_H": "0", "v_red": str(RH_only_red), "v_blue": str(RH_only_blue)})
    red_zero = face_speed(q(1), q(10), q(2), q(-1), xdot=q(4))
    blue_nonzero = face_speed(q(1), q(10), q(2), q(1), xdot=q(0))
    red_nonzero = face_speed(q(1), q(10), q(2), q(-1), xdot=q(0))
    blue_zero = face_speed(q(1), q(10), q(2), q(1), xdot=q(6))
    record("event_surface_red_only_witness",
           q(1) != 0 and red_zero == 0 and blue_nonzero != 0,
           {"R_H": "1", "v_red": str(red_zero), "v_blue": str(blue_nonzero)})
    record("event_surface_blue_only_witness",
           q(1) != 0 and blue_zero == 0 and red_nonzero != 0,
           {"R_H": "1", "v_red": str(red_nonzero), "v_blue": str(blue_zero)})

except Exception as exc:
    record("internal_exception", False, repr(exc))
    emit("INTERNAL_ERROR_NONAUTHORITATIVE", 70, {"sage": sage_version})

all_hold = all(item["holds"] for item in checks)
emit("FORMAL_IDENTITIES_HOLD_NONAUTHORITATIVE" if all_hold else
     "FORMAL_CHECK_FAILURE_NONAUTHORITATIVE",
     0 if all_hold else 1,
     {"sage": sage_version, "polynomial_backend": "libSingular"})
