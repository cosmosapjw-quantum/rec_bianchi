/-!
# REC-NEXT-03 conditional algebra contracts

This file is deliberately **NONAUTHORITATIVE**.  It proves small algebraic
consequences of explicit hypotheses.  It does not resolve source provenance,
establish parity with the Python implementation, or authorize a physical face.

Conventions used below:

* metric signature `(-,+,+,+)`;
* `h = 2 pi hbar`, with unit conversion kept explicit;
* red inflow means positive Doppler-coordinate face speed;
* blue inflow means negative Doppler-coordinate face speed.
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace RecNext03

section ConstantsAndUnits

/-- The ordinary/ angular Planck-constant relation, conditional on the
definition `hbar = h / (2*pi)`. -/
theorem h_eq_two_pi_hbar
    (h hbar : ℝ) (hbar_def : hbar = h / (2 * Real.pi)) :
    h = 2 * Real.pi * hbar := by
  have hden : 2 * Real.pi ≠ 0 := mul_ne_zero (by norm_num) Real.pi_ne_zero
  have hcross : hbar * (2 * Real.pi) = h :=
    (eq_div_iff hden).mp hbar_def
  calc
    h = hbar * (2 * Real.pi) := hcross.symm
    _ = 2 * Real.pi * hbar := by ring

/-- A unit-scale conversion is algebra only; no natural-unit convention is
introduced by this theorem. -/
theorem energy_per_unit_from_ordinary_frequency
    (h hbar nu energy unitScale : ℝ)
    (h_relation : h = 2 * Real.pi * hbar)
    (energy_def : energy = h * nu) :
    energy / unitScale = (2 * Real.pi * hbar * nu) / unitScale := by
  rw [energy_def, h_relation]

end ConstantsAndUnits

section TetradPhoton

structure Spatial3 where
  x : ℝ
  y : ℝ
  z : ℝ

def Spatial3.normSq (n : Spatial3) : ℝ := n.x ^ 2 + n.y ^ 2 + n.z ^ 2

/-- `(-,+,+,+)` quadratic form on tetrad components. -/
def minkowskiSq (t x y z : ℝ) : ℝ := -(t ^ 2) + x ^ 2 + y ^ 2 + z ^ 2

/-- A unit spatial tetrad direction makes the photon null in signature
`(-,+,+,+)`.  Orthonormality and unit direction are assumptions, not derived
source authority. -/
theorem photon_null_of_orthonormal_tetrad_direction
    (scale : ℝ) (n : Spatial3) (unit_direction : n.normSq = 1) :
    minkowskiSq scale (scale * n.x) (scale * n.y) (scale * n.z) = 0 := by
  calc
    minkowskiSq scale (scale * n.x) (scale * n.y) (scale * n.z) =
        scale ^ 2 * (-1 + n.normSq) := by
      unfold minkowskiSq Spatial3.normSq
      ring
    _ = 0 := by rw [unit_direction]; ring

end TetradPhoton

section DopplerFace

/-- Exact Doppler-coordinate face formula transcribed for conditional checking. -/
def vFace
    (RH x nu0 dNu nu0dot dlogDNu xdot : ℝ) : ℝ :=
  (((nu0 + x * dNu) * RH - nu0dot) / dNu) - x * dlogDNu - xdot

/-- Static line centre, width, and boundary reduce the exact face relation to
the positive/negative scale multiplying `RH`. -/
theorem vFace_static
    (RH x nu0 dNu : ℝ) (dNu_ne_zero : dNu ≠ 0) :
    vFace RH x nu0 dNu 0 0 0 = ((nu0 + x * dNu) / dNu) * RH := by
  unfold vFace
  ring

/-- With positive face frequency and positive Doppler width, the static face
speed has the same positive sign as `RH`. -/
theorem vFace_static_pos_iff
    (RH x nu0 dNu : ℝ)
    (positive_face_frequency : 0 < nu0 + x * dNu)
    (positive_width : 0 < dNu) :
    0 < vFace RH x nu0 dNu 0 0 0 ↔ 0 < RH := by
  rw [vFace_static RH x nu0 dNu (ne_of_gt positive_width)]
  have positive_factor : 0 < (nu0 + x * dNu) / dNu :=
    div_pos positive_face_frequency positive_width
  constructor <;> intro h
  · nlinarith
  · exact mul_pos positive_factor h

/-- Under the same positivity hypotheses, the negative signs also agree. -/
theorem vFace_static_neg_iff
    (RH x nu0 dNu : ℝ)
    (positive_face_frequency : 0 < nu0 + x * dNu)
    (positive_width : 0 < dNu) :
    vFace RH x nu0 dNu 0 0 0 < 0 ↔ RH < 0 := by
  rw [vFace_static RH x nu0 dNu (ne_of_gt positive_width)]
  have positive_factor : 0 < (nu0 + x * dNu) / dNu :=
    div_pos positive_face_frequency positive_width
  constructor <;> intro h
  · nlinarith
  · exact mul_neg_of_pos_of_neg positive_factor h

/-- Under the same positivity hypotheses, a static face zero is exactly an
`RH` zero. -/
theorem vFace_static_zero_iff
    (RH x nu0 dNu : ℝ)
    (positive_face_frequency : 0 < nu0 + x * dNu)
    (positive_width : 0 < dNu) :
    vFace RH x nu0 dNu 0 0 0 = 0 ↔ RH = 0 := by
  rw [vFace_static RH x nu0 dNu (ne_of_gt positive_width)]
  have positive_factor : 0 < (nu0 + x * dNu) / dNu :=
    div_pos positive_face_frequency positive_width
  constructor
  · intro h
    rcases mul_eq_zero.mp h with factor_zero | rh_zero
    · exact (ne_of_gt positive_factor factor_zero).elim
    · exact rh_zero
  · rintro rfl
    ring

/-- Piecewise upwind flux.  The zero branch is intentionally the left branch,
but both states give zero flux at exactly zero speed. -/
def upwindFlux (v leftState rightState : ℝ) : ℝ :=
  if 0 ≤ v then v * leftState else v * rightState

theorem upwindFlux_positive
    (v leftState rightState : ℝ) (positive_speed : 0 < v) :
    upwindFlux v leftState rightState = v * leftState := by
  simp [upwindFlux, le_of_lt positive_speed]

theorem upwindFlux_negative
    (v leftState rightState : ℝ) (negative_speed : v < 0) :
    upwindFlux v leftState rightState = v * rightState := by
  simp [upwindFlux, not_le.mpr negative_speed]

theorem upwindFlux_zero (leftState rightState : ℝ) :
    upwindFlux 0 leftState rightState = 0 := by
  simp [upwindFlux]

inductive BoundaryClass
  | inflow
  | outflow
  | grazing
  deriving DecidableEq, Repr

/-- Red-face ownership: positive is inflow, negative is outflow. -/
def classifyRed (v : ℝ) : BoundaryClass :=
  if 0 < v then .inflow else if v < 0 then .outflow else .grazing

/-- Blue-face ownership: negative is inflow, positive is outflow. -/
def classifyBlue (v : ℝ) : BoundaryClass :=
  if v < 0 then .inflow else if 0 < v then .outflow else .grazing

theorem classifyRed_positive (v : ℝ) (h : 0 < v) :
    classifyRed v = .inflow := by simp [classifyRed, h]

theorem classifyBlue_negative (v : ℝ) (h : v < 0) :
    classifyBlue v = .inflow := by simp [classifyBlue, h]

theorem classifyRed_zero : classifyRed 0 = .grazing := by
  simp [classifyRed]

theorem classifyBlue_zero : classifyBlue 0 = .grazing := by
  simp [classifyBlue]

/-- Positive-speed secants at zero see the left state. -/
theorem upwind_right_zero_secant
    (v leftState rightState : ℝ) (positive_speed : 0 < v) :
    (upwindFlux v leftState rightState - upwindFlux 0 leftState rightState) / v =
      leftState := by
  rw [upwindFlux_positive v leftState rightState positive_speed,
    upwindFlux_zero]
  field_simp [ne_of_gt positive_speed]
  <;> ring

/-- Negative-speed secants at zero see the right state. -/
theorem upwind_left_zero_secant
    (v leftState rightState : ℝ) (negative_speed : v < 0) :
    (upwindFlux v leftState rightState - upwindFlux 0 leftState rightState) / v =
      rightState := by
  rw [upwindFlux_negative v leftState rightState negative_speed,
    upwindFlux_zero]
  field_simp [ne_of_lt negative_speed]
  <;> ring

def rightZeroSecant (leftState rightState : ℝ) : ℝ := leftState
def leftZeroSecant (leftState rightState : ℝ) : ℝ := rightState

/-- A common zero-speed derivative is possible only when the two upwind states
agree. -/
theorem zero_secants_agree_iff (leftState rightState : ℝ) :
    rightZeroSecant leftState rightState = leftZeroSecant leftState rightState ↔
      leftState = rightState := by
  rfl

end DopplerFace

section QuantitySeparation

/- These wrappers intentionally have no coercions between them.  Any physical
conversion must therefore be an explicit, separately reviewed function. -/

structure SignedDeltaF where
  value : ℝ

structure TotalOccupation where
  value : ℝ

structure PacketPerHydrogenRate where
  value : ℝ

structure DepositedOccupationRate where
  value : ℝ

/-- One explicit conversion seam; `hydrogenScale` carries the caller's unit
contract and is not assigned authority here. -/
def depositPacketRate
    (hydrogenScale : ℝ) (rate : PacketPerHydrogenRate) : DepositedOccupationRate :=
  ⟨hydrogenScale * rate.value⟩

@[simp] theorem depositPacketRate_value
    (hydrogenScale : ℝ) (rate : PacketPerHydrogenRate) :
    (depositPacketRate hydrogenScale rate).value = hydrogenScale * rate.value := by
  rfl

end QuantitySeparation

section ConservativeRemap

/-- Two-cell column-conservative remap components. -/
def remapLeft (a b oldLeft oldRight : ℝ) : ℝ := a * oldLeft + b * oldRight
def remapRight (a b oldLeft oldRight : ℝ) : ℝ :=
  (1 - a) * oldLeft + (1 - b) * oldRight

/-- Exact number conservation for every pair of column fractions. -/
theorem remap_number_identity (a b oldLeft oldRight : ℝ) :
    remapLeft a b oldLeft oldRight + remapRight a b oldLeft oldRight =
      oldLeft + oldRight := by
  unfold remapLeft remapRight
  ring

/-- The left component preserves a constant state when the row sum is one. -/
theorem remap_gcl_left
    (a b constant : ℝ) (row_sum : a + b = 1) :
    remapLeft a b constant constant = constant := by
  calc
    remapLeft a b constant constant = (a + b) * constant := by
      unfold remapLeft
      ring
    _ = constant := by rw [row_sum]; ring

/-- The right component obeys the same geometric-conservation-law condition. -/
theorem remap_gcl_right
    (a b constant : ℝ) (row_sum : a + b = 1) :
    remapRight a b constant constant = constant := by
  calc
    remapRight a b constant constant = (2 - (a + b)) * constant := by
      unfold remapRight
      ring
    _ = constant := by rw [row_sum]; ring

/-- Exact linear JVP identity for the left remap component. -/
theorem remap_jvp_left
    (a b oldLeft oldRight dLeft dRight epsilon : ℝ) :
    remapLeft a b (oldLeft + epsilon * dLeft) (oldRight + epsilon * dRight) =
      remapLeft a b oldLeft oldRight + epsilon * remapLeft a b dLeft dRight := by
  unfold remapLeft
  ring

/-- Exact linear JVP identity for the right remap component. -/
theorem remap_jvp_right
    (a b oldLeft oldRight dLeft dRight epsilon : ℝ) :
    remapRight a b (oldLeft + epsilon * dLeft) (oldRight + epsilon * dRight) =
      remapRight a b oldLeft oldRight + epsilon * remapRight a b dLeft dRight := by
  unfold remapRight
  ring

end ConservativeRemap

section EventsAndRestart

/-- Distinct event types; equality of their numerical root times does not
collapse their physical meanings. -/
inductive EventTag
  | R_H_ZERO
  | RED_VX_ZERO
  | BLUE_VX_ZERO
  deriving DecidableEq, Repr

theorem event_tags_pairwise_distinct :
    EventTag.R_H_ZERO ≠ .RED_VX_ZERO ∧
    EventTag.R_H_ZERO ≠ .BLUE_VX_ZERO ∧
    EventTag.RED_VX_ZERO ≠ .BLUE_VX_ZERO := by
  decide

structure RestartState (Parent : Type) where
  acceptedParent : Parent
  event : EventTag

def restartFromAcceptedParent {Parent : Type}
    (parent : Parent) (event : EventTag) : RestartState Parent :=
  ⟨parent, event⟩

@[simp] theorem restart_preserves_accepted_parent {Parent : Type}
    (parent : Parent) (event : EventTag) :
    (restartFromAcceptedParent parent event).acceptedParent = parent := by
  rfl

end EventsAndRestart

end RecNext03
