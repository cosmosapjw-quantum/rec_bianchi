#include <stdio.h>
#include <stdlib.h>
#include "hydrogen.h"
int main(int argc, char **argv) {
  double TK = argc > 1 ? strtod(argv[1], NULL) : 3000.0;
  TWO_PHOTON_PARAMS twog;
  double *Aup = calloc(NVIRT, sizeof(double));
  double *Adn = calloc(NVIRT, sizeof(double));
  double A2p_up=0.0, A2p_dn=0.0;
  if (!Aup || !Adn) return 2;
  read_twog_params(&twog);
  populate_Diffusion(Aup, Adn, &A2p_up, &A2p_dn, TK*kBoltz, twog.Eb_tab, twog.A1s_tab);
  printf("temperature_K,%.17g\n", TK);
  printf("A2p_up_s_inv,%.17g\n", A2p_up);
  printf("A2p_dn_s_inv,%.17g\n", A2p_dn);
  printf("virtual_index,Eb_eV,Aup_s_inv,Adn_s_inv\n");
  for (unsigned b=NSUBLYA-NDIFF/2; b<NSUBLYA+NDIFF/2; ++b)
    printf("%u,%.17g,%.17g,%.17g\n", b, twog.Eb_tab[b], Aup[b], Adn[b]);
  free(Aup); free(Adn); return 0;
}
