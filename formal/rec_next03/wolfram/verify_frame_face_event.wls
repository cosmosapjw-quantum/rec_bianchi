#!/usr/bin/env wolframscript
(* NONAUTHORITATIVE exact formula checks; never production/source authority. *)
ClearAll["Global`*"];
args = Rest[$ScriptCommandLine];
pos = FirstPosition[args, "--output", Missing["NotFound"]];
If[MissingQ[pos] || pos[[1]] == Length[args],
  Print["usage: wolframscript -file verify_frame_face_event.wls --output FILE"];
  Exit[2]
];
output = args[[pos[[1]] + 1]];
CreateDirectory[DirectoryName[ExpandFileName[output]], CreateIntermediateDirectories -> True];
checks = {};
AddCheck[id_String, value_] := Module[{ok = TrueQ[value]},
  AppendTo[checks, <|"id" -> id, "authority" -> "NONAUTHORITATIVE", "passed" -> ok|>]; ok
];
Emit[status_String, code_Integer] := Module[{report},
  report = <|
    "schema" -> "REC_NEXT03_WOLFRAM_FORMAL_V2",
    "authority" -> "NONAUTHORITATIVE",
    "claim_scope" -> "EXACT_TRANSCRIPTION_CHECK_NOT_IMPLEMENTATION_SOURCE_OR_PRODUCTION_AUTHORITY",
    "status" -> status, "exit_code" -> code,
    "toolchain" -> <|"wolfram" -> $Version, "system_id" -> $SystemID,
      "xact_xtensor_loaded" -> TrueQ[xActLoaded]|>,
    "formula_package" -> <|
      "path" -> "REC_BIANCHI_FORMULA_DERIVATION_PACKAGE_20260831(1).zip",
      "sha256" -> "15f0d1af469f333d14488900b6ef031aaba071643efecdc850f4720aa7155e12",
      "authority" -> "NONAUTHORITATIVE_PROPOSED_FORMULAE"
    |>,
    "event_surfaces" -> {"CHARACTERISTIC_R_H_ZERO", "RED_FACE_V_X_ZERO", "BLUE_FACE_V_X_ZERO"},
    "proposed_formula_ids" -> <|
      "tetrad" -> "NONAUTHORITATIVE:HYDROGEN_STANDARD_BOOST_TETRAD_V1",
      "deposition" -> "NONAUTHORITATIVE:ADJACENT_TWO_NODE_BARYCENTRIC_DEPOSITION_V1"
    |>,
    "authority_firewalls" -> <|
      "delta_f_vs_total_f" -> "UNPROVED_AUTHORITY_FIREWALL: signed Delta_f requires an approved f_ref adapter before total-f use",
      "packet_rate_vs_occupation_rate" -> "UNPROVED_AUTHORITY_FIREWALL: two-photon/Raman packet rates require exactly-once n_H B_is/mu_i deposition"
    |>,
    "source_premises" -> {
      "formula-package:REC_BIANCHI_NONCODING_BLOCKER_DERIVATION_20260831.md:86-105,187-232,254-287,309-372,426-595,781-814,1261-1281",
      "formula-package:rec_bianchi_formula_checks_v1.wl:checks 1,4,6-8",
      "docs/PR05C2C0_THEORY_CLOSURE_FORMALISM.md:10-20,37-147,642-667,780-799",
      "src/full_bianchi_hyrec/background/characteristics.py:49-183",
      "src/full_bianchi_hyrec/trajectory/directional_face_admission.py:213-246,340-349"
    },
    "checks" -> checks,
    "failed_check_ids" -> Lookup[Select[checks, Not[TrueQ[#["passed"]]] &], "id", {}]
  |>;
  Quiet@Check[Export[output, report, "RawJSON"], Print["cannot write report"]; Exit[70]];
  Print[StringTemplate["REC_NEXT03_FORMAL WOLFRAM `` checks=`` failed=`` report=``"][
    status, Length[checks], Count[checks, x_ /; ! TrueQ[x["passed"]]], output]];
  Exit[code]
];
xActLoaded = Quiet@Check[Needs["xAct`xTensor`"] ; True, False];
If[! xActLoaded, Emit["ENVIRONMENT_GAP", 69]];

DefManifold[M4, 4, {a, b, d, q}];
DefMetric[-1, xg[-a, -b], CD];
AddCheck["xact_metric_symmetry", ToCanonical[xg[a, b] - xg[b, a]] === 0];
g4 = DiagonalMatrix[{-1, 1, 1, 1}];
n4 = {1, 0, 0, 0}; e4 = {0, ex, ey, ez};
mdot[u_, v_] := Expand[u . g4 . v];
spatialAssumptions = Element[{ex, ey, ez}, Reals] && ex^2 + ey^2 + ez^2 == 1;
hPlanck = 2 Pi hbar; p4 = (hPlanck nu/cLight) (n4 + e4);
AddCheck["signature_minus_plus_plus_plus", Sort[Eigenvalues[g4]] === {-1, 1, 1, 1}];
AddCheck["tetrad_timelike_norm", mdot[n4, n4] === -1];
AddCheck["tetrad_spatial_norm", FullSimplify[mdot[e4, e4] == 1, spatialAssumptions]];
AddCheck["photon_null", FullSimplify[mdot[p4, p4] == 0, spatialAssumptions]];
AddCheck["ordinary_frequency_energy_h_equals_2pi_hbar",
  FullSimplify[-cLight mdot[n4, p4] == 2 Pi hbar nu, spatialAssumptions]];

(* Rotation-free standard boost: Lambda^T eta Lambda=eta and det Lambda=+1. *)
bb = {b1, b2, b3}; bnorm2 = bb.bb; gam = 1/Sqrt[1 - bnorm2];
boost = Table[0, {4}, {4}]; boost[[1, 1]] = gam;
Do[boost[[1, i + 1]] = gam bb[[i]]; boost[[i + 1, 1]] = gam bb[[i]], {i, 1, 3}];
Do[boost[[i + 1, j + 1]] = KroneckerDelta[i, j] +
  (gam - 1) bb[[i]] bb[[j]]/bnorm2, {i, 1, 3}, {j, 1, 3}];
boostAssumptions = Element[bb, Reals] && 0 < bnorm2 < 1;
AddCheck["proposed_standard_boost_orthonormal",
  FullSimplify[Transpose[boost].g4.boost == g4, boostAssumptions]];
AddCheck["proposed_standard_boost_proper_determinant",
  FullSimplify[Det[boost] == 1, boostAssumptions]];

gamma = 1/Sqrt[1 - beta2]; doppler = gamma (1 - betaDotE);
abAssumptions = Element[{beta2, betaDotE}, Reals] && 0 <= beta2 < 1 && betaDotE^2 <= beta2;
AddCheck["doppler_positive", FullSimplify[doppler > 0, abAssumptions]];
alpha = (gamma - 1) betaDotE/beta2 - gamma;
AddCheck["aberrated_direction_unit", FullSimplify[
  (1 + 2 alpha betaDotE + alpha^2 beta2)/doppler^2 == 1,
  abAssumptions && beta2 > 0]];

(* Moving Doppler-coordinate chain rule and distinct zero surfaces. *)
ClearAll[nuH, nu0, width, rateH, dnu0, dlogw, xb, dxb, t];
movingExpr = ((nuH Exp[rateH t]) - (nu0 + dnu0 t))/(width Exp[dlogw t]) - (xb + dxb t);
movingExact = FullSimplify[SeriesCoefficient[movingExpr, {t, 0, 1}]];
movingDeclared = (nuH rateH - dnu0)/width - ((nuH - nu0)/width) dlogw - dxb;
AddCheck["moving_doppler_chain_rule", FullSimplify[movingExact == movingDeclared, width > 0]];
nuFace = nuAbs + xFace dNu;
vx = (nuFace RH - nuAbsDot)/dNu - xFace dLogDNu - xFaceDot;
AddCheck["static_grid_RH_vx_relation", FullSimplify[
  (vx /. {nuAbsDot -> 0, dLogDNu -> 0, xFaceDot -> 0}) == nuFace RH/dNu]];
AddCheck["RH_zero_not_general_vx_zero", (vx /. {RH -> 0, nuAbs -> 1, dNu -> 1,
  xFace -> 0, nuAbsDot -> 1, dLogDNu -> 0, xFaceDot -> 0}) === -1];
AddCheck["vx_zero_not_general_RH_zero", (vx /. {RH -> 1, nuAbs -> 1, dNu -> 1,
  xFace -> 0, nuAbsDot -> 1, dLogDNu -> 0, xFaceDot -> 0}) === 0];
flux[v_] := gFace (Max[v, 0] fLeft + Min[v, 0] fRight);
AddCheck["red_inflow_positive_speed", FullSimplify[
  (flux[vRed] /. {fLeft -> fNativeRed, fRight -> fComRed}) == gFace vRed fNativeRed, vRed > 0]];
AddCheck["blue_inflow_negative_speed", FullSimplify[
  (flux[vBlue] /. {fLeft -> fComBlue, fRight -> fNativeBlue}) == gFace vBlue fNativeBlue, vBlue < 0]];
AddCheck["grazing_flux_zero", flux[0] === 0];

(* Thermal nulls: formula identities only, not channel-byte/normalization authority. *)
ClearAll[aT, bT, uT, gDeg, xLower, xGround];
fA = Exp[-aT]/(1 - Exp[-aT]); fB = Exp[-bT]/(1 - Exp[-bT]);
AddCheck["proposed_one_photon_planck_null", FullSimplify[
  (gDeg xLower Exp[-aT]) (1 + fA) - gDeg xLower fA == 0,
  aT > 0 && gDeg > 0 && xLower >= 0]];
AddCheck["proposed_two_photon_packet_planck_null", FullSimplify[
  (gDeg xGround Exp[-(aT + bT)]) (1 + fA) (1 + fB) - gDeg xGround fA fB == 0,
  aT > 0 && bT > 0 && gDeg > 0 && xGround >= 0]];
fTrackedR = Exp[-(uT + bT)]/(1 - Exp[-(uT + bT)]);
fCompR = Exp[-bT]/(1 - Exp[-bT]);
AddCheck["proposed_raman_packet_planck_null", FullSimplify[
  (gDeg xGround Exp[-uT]) fCompR (1 + fTrackedR) -
    gDeg xGround fTrackedR (1 + fCompR) == 0,
  uT > 0 && bT > 0 && gDeg > 0 && xGround >= 0]];

(* Constant transfer, analytic JVP, and regular chi->0 limits. *)
ClearAll[chi, dt, f0, etaSrc, df0, detaSrc, dchi, ddt, s];
transmission = Exp[-chi dt]; phi = (1 - transmission)/chi;
transfer = transmission f0 + etaSrc phi;
declaredJVP = transmission df0 + phi detaSrc +
  (-dt transmission f0 + etaSrc (chi dt transmission - (1 - transmission))/chi^2) dchi +
  transmission (etaSrc - chi f0) ddt;
exactJVP = FullSimplify[D[
  Exp[-(chi + s dchi) (dt + s ddt)] (f0 + s df0) +
  (etaSrc + s detaSrc) (1 - Exp[-(chi + s dchi) (dt + s ddt)])/(chi + s dchi), s] /. s -> 0,
  chi != 0];
AddCheck["constant_transfer_jvp", FullSimplify[exactJVP == declaredJVP, chi != 0]];
AddCheck["constant_transfer_phi_chi_zero", FullSimplify[Limit[phi, chi -> 0] == dt]];
AddCheck["constant_transfer_solution_chi_zero", FullSimplify[Limit[transfer, chi -> 0] == f0 + etaSrc dt]];
AddCheck["constant_transfer_dchi_chi_zero", FullSimplify[
  Limit[D[transfer, chi], chi -> 0] == -dt f0 - etaSrc dt^2/2]];

(* Unique adjacent two-node weights under the proposed locality/minimal-support axiom. *)
ClearAll[EL, ER, Es, dEL, dER, dEs]; deltaE = ER - EL;
bL = (ER - Es)/deltaE; bR = (Es - EL)/deltaE;
dbL = FullSimplify[D[((ER + t dER) - (Es + t dEs))/
  ((ER + t dER) - (EL + t dEL)), t] /. t -> 0];
dbR = FullSimplify[D[((Es + t dEs) - (EL + t dEL))/
  ((ER + t dER) - (EL + t dEL)), t] /. t -> 0];
AddCheck["proposed_adjacent_two_node_number", FullSimplify[bL + bR == 1, ER != EL]];
AddCheck["proposed_adjacent_two_node_energy", FullSimplify[EL bL + ER bR == Es, ER != EL]];
AddCheck["proposed_adjacent_two_node_nonnegative", FullSimplify[
  0 < bL < 1 && 0 < bR < 1, Element[{EL, Es, ER}, Reals] && EL < Es < ER]];
AddCheck["proposed_adjacent_two_node_dnumber", FullSimplify[dbL + dbR == 0, ER != EL]];
AddCheck["proposed_adjacent_two_node_denergy", FullSimplify[
  dEL bL + EL dbL + dER bR + ER dbR == dEs, ER != EL]];

If[AllTrue[checks, TrueQ[#["passed"]] &], Emit["PASS", 0], Emit["FAIL", 1]];
