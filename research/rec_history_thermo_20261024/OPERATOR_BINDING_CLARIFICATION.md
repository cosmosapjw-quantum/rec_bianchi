# Local derivative and future coupled operator binding

This postrun clarification limits interpretation; it does not change the executed source, inputs, frozen tolerances or raw results.

Let Phi_s(theta,u) denote this unit's consistently stable real-source evaluation. The exported314x6 block is J_s=partial_theta Phi_s at fixed incoming313 and fixed query/grid/frame. A future differential of this same map is

  delta o = J_s delta theta + K_s delta u,
  K_s = partial_u Phi_s.

REC-HISTORY-RESP01 certified the represented incoming operator K_0=T_0 M_0^{-1}B_0+P_0 associated with its own frozen native binary64 arrays. The current stable evaluation is a distinct represented matrix. The observed M/s/sv/output differences are recorded in NATIVE_STABLE_GAPS.json. Small outgoing value differences alone do not establish an operator-norm bound for K_s-K_0.

Therefore the earlier represented norm interval1.175627229227178..1.1756272292401924 remains a result about K_0. It is not automatically a certificate for K_s, the six new coefficient columns, transcendental rounding, or the full physical history. Before combining the new J_s block with an incoming derivative, the consumer must bind one consistent arithmetic/source identity: either supply and verify K_s for this source or justify a quantitative transfer between K_0 and K_s. No such transfer was computed or admitted in this unit.

The implicit differentiation formula in THEORY.md remains valid for a consistently chosen M,s,T,P. Its reference to combining an existing incoming derivative is a structural decomposition, conditional on this common-operator binding. It does not remove the original RESP01 source identity restrictions.

The full coupled derivative additionally needs the actual admitted history pullback delta u (including query retiming and endpoint/source uncertainty), Bianchi geodesic/direction/frame dependence, and the thermal evolution equations. This unit supplies the local primitive coefficient block; it does not close those remaining H5/H6/H7 obligations.
