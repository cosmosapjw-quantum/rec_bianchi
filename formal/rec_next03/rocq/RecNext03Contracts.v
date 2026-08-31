(**
  REC-NEXT-03 conditional algebra contracts.

  This module is deliberately NONAUTHORITATIVE.  It proves only consequences
  of explicit assumptions.  It establishes neither source provenance nor code
  parity and cannot authorize a physical directional face.
*)

From Stdlib Require Import Reals Lra Ring Field.

Open Scope R_scope.

Section ConstantsAndUnits.

Theorem h_eq_two_pi_hbar :
  forall h hbar pi : R,
    2 * pi <> 0 ->
    hbar = h / (2 * pi) ->
    h = 2 * pi * hbar.
Proof.
  intros h hbar pi Hden Hdef.
  rewrite Hdef.
  field.
  exact Hden.
Qed.

Theorem energy_per_unit_from_ordinary_frequency :
  forall h hbar pi nu energy unit_scale : R,
    h = 2 * pi * hbar ->
    energy = h * nu ->
    energy / unit_scale = (2 * pi * hbar * nu) / unit_scale.
Proof.
  intros h hbar pi nu energy unit_scale Hh He.
  rewrite He, Hh.
  reflexivity.
Qed.

End ConstantsAndUnits.

Section TetradPhoton.

Record Spatial3 : Type := mkSpatial3 {
  spatial_x : R;
  spatial_y : R;
  spatial_z : R
}.

Definition spatial_norm_sq (n : Spatial3) : R :=
  spatial_x n ^ 2 + spatial_y n ^ 2 + spatial_z n ^ 2.

(** Quadratic form with signature (-,+,+,+). *)
Definition minkowski_sq (t x y z : R) : R :=
  -(t ^ 2) + x ^ 2 + y ^ 2 + z ^ 2.

Theorem photon_null_of_orthonormal_tetrad_direction :
  forall (scale : R) (n : Spatial3),
    spatial_norm_sq n = 1 ->
    minkowski_sq scale
      (scale * spatial_x n)
      (scale * spatial_y n)
      (scale * spatial_z n) = 0.
Proof.
  intros scale [nx ny nz] Hunit.
  replace (minkowski_sq scale
      (scale * nx) (scale * ny) (scale * nz))
    with (scale ^ 2 * (-1 + spatial_norm_sq (mkSpatial3 nx ny nz))).
  - rewrite Hunit; ring.
  - unfold minkowski_sq, spatial_norm_sq; simpl; ring.
Qed.

End TetradPhoton.

Section DopplerFace.

Definition vFace
  (RH x nu0 dNu nu0dot dlogDNu xdot : R) : R :=
  (((nu0 + x * dNu) * RH - nu0dot) / dNu) - x * dlogDNu - xdot.

Theorem vFace_static :
  forall RH x nu0 dNu : R,
    dNu <> 0 ->
    vFace RH x nu0 dNu 0 0 0 = ((nu0 + x * dNu) / dNu) * RH.
Proof.
  intros RH x nu0 dNu HdNu.
  unfold vFace, Rdiv.
  ring.
Qed.

Theorem vFace_static_pos_iff :
  forall RH x nu0 dNu : R,
    0 < nu0 + x * dNu ->
    0 < dNu ->
    0 < vFace RH x nu0 dNu 0 0 0 <-> 0 < RH.
Proof.
  intros RH x nu0 dNu Hfreq Hwidth.
  rewrite vFace_static by lra.
  assert (Hfactor : 0 < (nu0 + x * dNu) / dNu).
  { apply Rdiv_lt_0_compat; assumption. }
  split; intro H; nra.
Qed.

Theorem vFace_static_neg_iff :
  forall RH x nu0 dNu : R,
    0 < nu0 + x * dNu ->
    0 < dNu ->
    vFace RH x nu0 dNu 0 0 0 < 0 <-> RH < 0.
Proof.
  intros RH x nu0 dNu Hfreq Hwidth.
  rewrite vFace_static by lra.
  assert (Hfactor : 0 < (nu0 + x * dNu) / dNu).
  { apply Rdiv_lt_0_compat; assumption. }
  split; intro H; nra.
Qed.

Theorem vFace_static_zero_iff :
  forall RH x nu0 dNu : R,
    0 < nu0 + x * dNu ->
    0 < dNu ->
    vFace RH x nu0 dNu 0 0 0 = 0 <-> RH = 0.
Proof.
  intros RH x nu0 dNu Hfreq Hwidth.
  rewrite vFace_static by lra.
  assert (Hfactor : 0 < (nu0 + x * dNu) / dNu).
  { apply Rdiv_lt_0_compat; assumption. }
  split; intro H.
  - apply Rmult_integral in H.
    destruct H as [H | H]; [nra | exact H].
  - rewrite H; ring.
Qed.

Definition upwindFlux (v left_state right_state : R) : R :=
  if Rle_dec 0 v then v * left_state else v * right_state.

Theorem upwindFlux_positive :
  forall v left_state right_state : R,
    0 < v ->
    upwindFlux v left_state right_state = v * left_state.
Proof.
  intros v left_state right_state Hv.
  unfold upwindFlux.
  destruct (Rle_dec 0 v); [reflexivity | lra].
Qed.

Theorem upwindFlux_negative :
  forall v left_state right_state : R,
    v < 0 ->
    upwindFlux v left_state right_state = v * right_state.
Proof.
  intros v left_state right_state Hv.
  unfold upwindFlux.
  destruct (Rle_dec 0 v); [lra | reflexivity].
Qed.

Theorem upwindFlux_zero :
  forall left_state right_state : R,
    upwindFlux 0 left_state right_state = 0.
Proof.
  intros left_state right_state.
  unfold upwindFlux.
  destruct (Rle_dec 0 0); [ring | lra].
Qed.

Inductive BoundaryClass : Type :=
  | Inflow
  | Outflow
  | Grazing.

Definition classifyRed (v : R) : BoundaryClass :=
  if Rlt_dec 0 v then Inflow
  else if Rlt_dec v 0 then Outflow
  else Grazing.

Definition classifyBlue (v : R) : BoundaryClass :=
  if Rlt_dec v 0 then Inflow
  else if Rlt_dec 0 v then Outflow
  else Grazing.

Theorem classifyRed_positive :
  forall v : R, 0 < v -> classifyRed v = Inflow.
Proof.
  intros v Hv; unfold classifyRed.
  destruct (Rlt_dec 0 v); [reflexivity | lra].
Qed.

Theorem classifyBlue_negative :
  forall v : R, v < 0 -> classifyBlue v = Inflow.
Proof.
  intros v Hv; unfold classifyBlue.
  destruct (Rlt_dec v 0); [reflexivity | lra].
Qed.

Theorem classifyRed_zero : classifyRed 0 = Grazing.
Proof.
  unfold classifyRed.
  destruct (Rlt_dec 0 0); [lra |].
  destruct (Rlt_dec 0 0); [lra | reflexivity].
Qed.

Theorem classifyBlue_zero : classifyBlue 0 = Grazing.
Proof.
  unfold classifyBlue.
  destruct (Rlt_dec 0 0); [lra |].
  destruct (Rlt_dec 0 0); [lra | reflexivity].
Qed.

Theorem upwind_right_zero_secant :
  forall v left_state right_state : R,
    0 < v ->
    (upwindFlux v left_state right_state -
      upwindFlux 0 left_state right_state) / v = left_state.
Proof.
  intros v left_state right_state Hv.
  rewrite upwindFlux_positive by exact Hv.
  rewrite upwindFlux_zero.
  field; lra.
Qed.

Theorem upwind_left_zero_secant :
  forall v left_state right_state : R,
    v < 0 ->
    (upwindFlux v left_state right_state -
      upwindFlux 0 left_state right_state) / v = right_state.
Proof.
  intros v left_state right_state Hv.
  rewrite upwindFlux_negative by exact Hv.
  rewrite upwindFlux_zero.
  field; lra.
Qed.

Definition rightZeroSecant (left_state right_state : R) : R := left_state.
Definition leftZeroSecant (left_state right_state : R) : R := right_state.

Theorem zero_secants_agree_iff :
  forall left_state right_state : R,
    rightZeroSecant left_state right_state =
      leftZeroSecant left_state right_state <->
    left_state = right_state.
Proof.
  intros left_state right_state.
  unfold rightZeroSecant, leftZeroSecant.
  tauto.
Qed.

End DopplerFace.

Section QuantitySeparation.

(** No coercions are declared between these four physical meanings. *)
Record SignedDeltaF : Type := mkSignedDeltaF { signed_delta_f_value : R }.
Record TotalOccupation : Type := mkTotalOccupation { total_occupation_value : R }.
Record PacketPerHydrogenRate : Type := mkPacketPerHydrogenRate {
  packet_per_hydrogen_rate_value : R
}.
Record DepositedOccupationRate : Type := mkDepositedOccupationRate {
  deposited_occupation_rate_value : R
}.

Definition depositPacketRate
  (hydrogen_scale : R) (rate : PacketPerHydrogenRate) : DepositedOccupationRate :=
  mkDepositedOccupationRate
    (hydrogen_scale * packet_per_hydrogen_rate_value rate).

Theorem depositPacketRate_value :
  forall (hydrogen_scale : R) (rate : PacketPerHydrogenRate),
    deposited_occupation_rate_value (depositPacketRate hydrogen_scale rate) =
      hydrogen_scale * packet_per_hydrogen_rate_value rate.
Proof.
  intros; reflexivity.
Qed.

End QuantitySeparation.

Section ConservativeRemap.

Definition remapLeft (a b old_left old_right : R) : R :=
  a * old_left + b * old_right.

Definition remapRight (a b old_left old_right : R) : R :=
  (1 - a) * old_left + (1 - b) * old_right.

Theorem remap_number_identity :
  forall a b old_left old_right : R,
    remapLeft a b old_left old_right + remapRight a b old_left old_right =
      old_left + old_right.
Proof.
  intros; unfold remapLeft, remapRight; ring.
Qed.

Theorem remap_gcl_left :
  forall a b constant : R,
    a + b = 1 ->
    remapLeft a b constant constant = constant.
Proof.
  intros a b constant Hrow.
  unfold remapLeft.
  replace (a * constant + b * constant) with ((a + b) * constant) by ring.
  rewrite Hrow.
  ring.
Qed.

Theorem remap_gcl_right :
  forall a b constant : R,
    a + b = 1 ->
    remapRight a b constant constant = constant.
Proof.
  intros a b constant Hrow.
  unfold remapRight.
  replace ((1 - a) * constant + (1 - b) * constant)
    with ((2 - (a + b)) * constant) by ring.
  rewrite Hrow.
  ring.
Qed.

Theorem remap_jvp_left :
  forall a b old_left old_right d_left d_right epsilon : R,
    remapLeft a b
      (old_left + epsilon * d_left)
      (old_right + epsilon * d_right) =
    remapLeft a b old_left old_right +
      epsilon * remapLeft a b d_left d_right.
Proof.
  intros; unfold remapLeft; ring.
Qed.

Theorem remap_jvp_right :
  forall a b old_left old_right d_left d_right epsilon : R,
    remapRight a b
      (old_left + epsilon * d_left)
      (old_right + epsilon * d_right) =
    remapRight a b old_left old_right +
      epsilon * remapRight a b d_left d_right.
Proof.
  intros; unfold remapRight; ring.
Qed.

End ConservativeRemap.

Section EventsAndRestart.

Inductive EventTag : Type :=
  | R_H_ZERO
  | RED_VX_ZERO
  | BLUE_VX_ZERO.

Theorem event_tags_pairwise_distinct :
  R_H_ZERO <> RED_VX_ZERO /\
  R_H_ZERO <> BLUE_VX_ZERO /\
  RED_VX_ZERO <> BLUE_VX_ZERO.
Proof.
  repeat split; discriminate.
Qed.

Record RestartState (Parent : Type) : Type := mkRestartState {
  accepted_parent : Parent;
  pending_event : EventTag
}.

Arguments accepted_parent {Parent} _.

Definition restartFromAcceptedParent {Parent : Type}
  (parent : Parent) (event : EventTag) : RestartState Parent :=
  mkRestartState Parent parent event.

Theorem restart_preserves_accepted_parent :
  forall (Parent : Type) (parent : Parent) (event : EventTag),
    accepted_parent (restartFromAcceptedParent parent event) = parent.
Proof.
  intros; reflexivity.
Qed.

End EventsAndRestart.
