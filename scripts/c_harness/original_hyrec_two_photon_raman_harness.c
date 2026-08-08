#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "hydrogen.h"

int main(int argc, char **argv) {
  if (argc != 4) {
    fprintf(stderr, "usage: %s TR_eV fsR meR\n", argv[0]);
    return 2;
  }
  const double TR = strtod(argv[1], NULL);
  const double fsR = strtod(argv[2], NULL);
  const double meR = strtod(argv[3], NULL);
  if (!(TR > 0.0 && fsR > 0.0 && meR > 0.0)) return 3;

  TWO_PHOTON_PARAMS twog;
  read_twog_params(&twog);
  const double scale = pow(fsR, 8.0) * meR;
  double total_2s = 0.0;
  double total_2p = 0.0;
  double r2[NVIRT], vr2[NVIRT], rp[NVIRT], vrp[NVIRT];

  for (unsigned b = 0; b < NVIRT; ++b) {
    const double energy = twog.Eb_tab[b];
    const double dbfact = exp((energy - E21) / TR);
    r2[b] = scale * twog.A2s_tab[b]
          / fabs(exp((energy - E21) / TR) - 1.0);
    vr2[b] = r2[b] * dbfact;
    const double r3 = exp(-E32 / TR) / 3.0 * scale * twog.A3s3d_tab[b]
                    / fabs(exp((energy - E31) / TR) - 1.0);
    const double r4 = exp(-E42 / TR) / 3.0 * scale * twog.A4s4d_tab[b]
                    / fabs(exp((energy - E41) / TR) - 1.0);
    rp[b] = r3 + r4;
    vrp[b] = rp[b] * 3.0 * dbfact;
    total_2s += r2[b];
    total_2p += rp[b];
  }
  const double total = total_2s + total_2p;
  for (unsigned b = 0; b < NVIRT; ++b) {
    printf("%u %.17e %.17e %.17e %.17e %.17e\n",
           b, r2[b], vr2[b], rp[b], vrp[b], total);
  }
  return 0;
}
