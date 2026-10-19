/* Original Oct-2012 h/2 late-time reference, linked with unmodified .c files.
 * The isolated hyrec_params.h copy changes only DLNA to (8.49e-5/2.).
 * Initial state and both RHS memories come from actual R3M native raw rows.
 * FULL at iz>=izH0+nzrt exercises history.c's own switch to EMLA2s2p.
 * The first false outer table guard switches permanently to PEEBLES.
 */
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hyrectools.h"
#include "helium.h"
#include "hydrogen.h"
#include "history.h"
#include "hyrec_params.h"

extern void rec_set_derived_params(REC_COSMOPARAMS *param);
static REC_COSMOPARAMS p;
static HRATEEFF rates;
static int initialized = 0;

static double z_of(long iz) {
  return (1. + ZSTART) * exp(-DLNA * (double)iz) - 1.;
}

int rec_r3o_lowz_init(void) {
  FILE *f;
  if (initialized) return 0;
  if (DLNA != 4.245e-5 || ZSTART != 8000. || ZEND != 0. || MODEL != FULL)
    return -1;
  memset(&p, 0, sizeof(p));
  memset(&rates, 0, sizeof(rates));
  p.T0 = 2.7255; p.obh2 = .0224; p.omh2 = .14309694000000003;
  p.okh2 = 0.; p.odeh2 = .31113726660800006; p.w0 = -1.; p.wa = 0.;
  p.Y = .2454; p.Nnueff = 3.03821934419124; p.fsR = p.meR = 1.;
  rec_set_derived_params(&p);
  if (p.izH0 != 36446 || p.nzrt != 21943 || p.nz != 211717) return -2;
  /* Fail before the source read_rates(), which assumes fopen succeeds. */
  f = fopen(ALPHA_FILE, "r"); if (!f) return -3; fclose(f);
  f = fopen(RR_FILE, "r"); if (!f) return -4; fclose(f);
  rates.logTR_tab = create_1D_array(NTR);
  rates.TM_TR_tab = create_1D_array(NTM);
  rates.logAlpha_tab[0] = create_2D_array(NTM, NTR);
  rates.logAlpha_tab[1] = create_2D_array(NTM, NTR);
  rates.logR2p2s_tab = create_1D_array(NTR);
  read_rates(&rates);
  initialized = 1;
  return 0;
}

/* reason 0: guard true; 1: TR_MIN; 2: TM_TR_MIN. Preserve source order. */
int rec_r3o_lowz_guard(double z, double tm) {
  if (!initialized || !isfinite(z) || !isfinite(tm) || z < 0. || tm <= 0.) return -1;
  if (!(kBoltz*p.T0*(1.+z)/p.fsR/p.fsR/p.meR > TR_MIN)) return 1;
  if (!(tm/p.T0/(1.+z) > TM_TR_MIN)) return 2;
  return 0;
}

double rec_r3o_lowz_dlna(void) { return DLNA; }
long rec_r3o_lowz_nz(void) { return initialized ? p.nz : -1; }
double rec_r3o_lowz_z(long iz) { return z_of(iz); }

/* Common-Python-input original atomic/thermal evaluation; no state import. */
int rec_r3o_lowz_rhs(long iz, int was_peebles, double xe, double tm, double *out) {
  double z, tr, nh, hub;
  int reason, model;
  if (!initialized || !out || iz < p.izH0+p.nzrt || iz >= p.nz-1 ||
      (was_peebles != 0 && was_peebles != 1) ||
      !isfinite(xe) || !(xe > 0. && xe < 1.) || !isfinite(tm) || !(tm > 0.)) return -1;
  z = z_of(iz);
  if (!(tm <= p.T0*(1.+z))) return -2;
  reason = rec_r3o_lowz_guard(z, tm);
  if (reason < 0) return -3;
  model = (was_peebles || reason) ? PEEBLES : EMLA2s2p;
  tr = kBoltz*p.T0*(1.+z);
  nh = 1e-6*p.nH0*(1.+z)*(1.+z)*(1.+z);
  hub = rec_HubbleConstant(&p, z);
  out[0] = rec_dxHIIdlna(model, xe, xe, nh, hub, kBoltz*tm, tr,
    &rates, NULL, NULL, NULL, NULL, p.zH0, (unsigned)(iz-p.izH0), z, p.fsR, p.meR);
  out[1] = rec_dTmdlna(xe, tm, tr/kBoltz, hub, p.fHe, p.fsR, p.meR);
  if (!isfinite(out[0]) || !isfinite(out[1])) return -4;
  return model;
}

/* State layout: xe, Tm, Hprev, Hprev2, Tprev, Tprev2; output candidate only.
 * A failed candidate leaves the input array untouched. Return model 0 or 2.
 */
int rec_r3o_lowz_step(long iz, int was_peebles, double *state) {
  double nx, nt, hp, hp2, tp, tp2, z;
  int i, reason, model;
  if (!initialized || !state || iz < p.izH0+p.nzrt || iz >= p.nz-1 ||
      (was_peebles != 0 && was_peebles != 1)) return -1;
  for (i=0; i<6; i++) if (!isfinite(state[i])) return -2;
  z = z_of(iz);
  if (!(state[0] > 0. && state[0] < 1. && state[1] > 0. && state[1] <= p.T0*(1.+z))) return -3;
  reason = rec_r3o_lowz_guard(z, state[1]);
  if (reason < 0) return -4;
  model = (was_peebles || reason) ? PEEBLES : FULL;
  hp=state[2]; hp2=state[3]; tp=state[4]; tp2=state[5];
  rec_get_xe_next2_HTm(model, &p, z, state[0], state[1], &nx, &nt,
    &rates, (unsigned)iz, NULL, NULL, NULL, NULL, &hp, &tp, &hp2, &tp2);
  if (!isfinite(nx) || !isfinite(nt) || !isfinite(hp) || !isfinite(tp) ||
      !(nx > 0. && nx < 1. && nt > 0. && nt <= p.T0*(1.+z_of(iz+1)))) return -5;
  state[0]=nx; state[1]=nt; state[2]=hp; state[3]=hp2; state[4]=tp; state[5]=tp2;
  return model == FULL ? EMLA2s2p : PEEBLES;
}

double rec_r3o_lowz_z0(const double *tail) {
  double value, *values;
  int i;
  if (!initialized || !tail) return NAN;
  for (i=0; i<4; i++) if (!isfinite(tail[i])) return NAN;
  values = calloc((size_t)p.nz, sizeof(double));
  if (!values) return NAN;
  for (i=0; i<4; i++) values[p.nz-4+i] = tail[i];
  value = rec_interp1d(-log(8001.), DLNA, values, (unsigned)p.nz, 0.);
  free(values);
  return value;
}

#ifdef R3O_LOWZ_MAIN
static int parse_long(const char *s, long *value) {
  char *end;
  errno=0; *value=strtol(s, &end, 10);
  return errno || *end || s == end;
}
static int parse_double(const char *s, double *value) {
  char *end;
  errno=0; *value=strtod(s, &end);
  return errno || *end || s == end || !isfinite(*value);
}
int main(int argc, char **argv) {
  long iz, count, was_peebles;
  double state[6];
  int i, model;
  if (argc != 10) {
    fprintf(stderr, "usage: native_r3o_lowz START_IZ STEPS WAS_PEEBLES xe Tm Hprev Hprev2 Tprev Tprev2\n");
    return 2;
  }
  if (parse_long(argv[1], &iz) || parse_long(argv[2], &count) ||
      parse_long(argv[3], &was_peebles) || rec_r3o_lowz_init()) return 2;
  if (iz < 58389 || iz >= p.nz-1 || count < 1 || count > p.nz-1-iz ||
      (was_peebles != 0 && was_peebles != 1)) return 2;
  for (i=0; i<6; i++) if (parse_double(argv[i+4], &state[i])) return 2;
  printf("START,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
    iz,z_of(iz),state[0],state[1],state[2],state[3],state[4],state[5]);
  while (count--) {
    model = rec_r3o_lowz_step(iz, (int)was_peebles, state);
    if (model < 0) { fprintf(stderr,"R3O_NATIVE_STEP_FAILURE:%ld:%d\n",iz,model); return 3; }
    was_peebles = model == PEEBLES;
    iz++;
    printf("STEP,%ld,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
      iz,model,z_of(iz),state[0],state[1],state[2],state[3],state[4],state[5]);
  }
  printf("END,%s,%ld\n", iz==p.nz-1 ? "STOP_AT_SOURCE_Z0_CUBIC_STENCIL" : "BOUNDED_LOW_Z_COMPLETE", iz);
  return 0;
}
#endif
