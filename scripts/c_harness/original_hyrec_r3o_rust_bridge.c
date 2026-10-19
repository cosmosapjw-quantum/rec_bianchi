/* Isolated R3O extension. No original source or existing harness is edited.
 * The include intentionally shares p/rates with the original-C oracle.
 * Calls are serialized by the standalone Rust process, never Python callbacks.
 */
#include "original_hyrec_r3o_lowz_harness.c"

/* Continuous log(a) elapsed from the reviewed native U6 boundary.
 * This is explicitly EMLA2s2p, never FULL, never a cross-stage calculation.
 * Output layout is dxe/dln(a), dTm/dln(a), both at the actual supplied state.
 */
int rec_r3o_rust_continuous(double tau, double span, double xe, double tm, double *out) {
  double z, tr, nh, hub;
  if (!initialized || !out || !isfinite(tau) || !isfinite(span) ||
      !(span > 0. && span <= 32.*DLNA) || tau < 0. || tau > span ||
      !isfinite(xe) || !(xe > 0. && xe < 1.) || !isfinite(tm) || !(tm > 0.)) return -10;
  z = (1.+ZSTART) * exp(-DLNA*58389. - tau) - 1.;
  if (z < 0. || !(tm <= p.T0*(1.+z)) || rec_r3o_lowz_guard(z, tm) != 0) return -11;
  tr = kBoltz*p.T0*(1.+z);
  if (!(tr/p.fsR/p.fsR/p.meR < TR_MAX)) return -12;
  nh = 1e-6*p.nH0*(1.+z)*(1.+z)*(1.+z);
  hub = rec_HubbleConstant(&p, z);
  out[0] = rec_dxHIIdlna(EMLA2s2p, xe, xe, nh, hub, kBoltz*tm, tr,
    &rates, NULL, NULL, NULL, NULL, p.zH0, (unsigned)(58389-p.izH0), z, p.fsR, p.meR);
  out[1] = rec_dTmdlna(xe, tm, tr/kBoltz, hub, p.fHe, p.fsR, p.meR);
  return isfinite(out[0]) && isfinite(out[1]) ? EMLA2s2p : -13;
}

/* Frozen-checkpoint thermal coefficients: Tr[K], A, lambda=2+A, Teq.
 * Away from the source's Tr/Tm-1<1e-10 branch, F_T=A*Tr-(2+A)*Tm.
 * These coefficients support an analytic Jacobian check, not a replacement RHS.
 */
int rec_r3o_rust_thermal_coefficients(double xe, double tm, double *out) {
  double z, tr, hub, a;
  if (!initialized || !out || !(xe > 0. && xe < 1.) || !isfinite(xe) ||
      !(tm > 0.) || !isfinite(tm)) return -20;
  z = z_of(58389);
  tr = kBoltz*p.T0*(1.+z)/kBoltz;
  if (!(tr/tm-1. >= 1e-10)) return -21;
  hub = rec_HubbleConstant(&p, z);
  a = p.fsR*p.fsR/p.meR/p.meR/p.meR*4.91466895548409e-22*tr*tr*tr*tr*xe/(1.+xe+p.fHe)/hub;
  out[0]=tr; out[1]=a; out[2]=2.+a; out[3]=a*tr/(2.+a);
  return isfinite(a) && a > 0. ? 0 : -22;
}
