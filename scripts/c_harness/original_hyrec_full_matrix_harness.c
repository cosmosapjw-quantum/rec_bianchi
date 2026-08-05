#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "hyrectools.h"
#include "hydrogen.h"

int main(void) {
  HRATEEFF rates;
  TWO_PHOTON_PARAMS twog;
  double Trr[2][2], *Trv[2], *Tvr[2], *Tvv[3];
  double sr[2], sv[NVIRT], Dtau[NVIRT];
  double Dfplus[NVIRT], Dfplus_Ly[2] = {1e-8, 2e-9};
  double Alpha[2], DAlpha[2], Beta[2];
  double xr[2], xv[NVIRT];
  double TK=3000.0, TM=TK*kBoltz, TR=TK*kBoltz;
  double nH=250.0, H=5e-14, xe=0.5, xHII=0.5, fsR=1.0, meR=1.0;

  rates.logTR_tab=create_1D_array(NTR);
  rates.TM_TR_tab=create_1D_array(NTM);
  rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);
  rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);
  rates.logR2p2s_tab=create_1D_array(NTR);
  read_rates(&rates); read_twog_params(&twog);
  for (int i=0;i<2;i++) { Trv[i]=create_1D_array(NVIRT); Tvr[i]=create_1D_array(NVIRT); }
  for (int i=0;i<3;i++) Tvv[i]=create_1D_array(NVIRT);
  for (unsigned b=0;b<NVIRT;b++) {
    double y=(twog.Eb_tab[b]-E21)/0.03;
    Dfplus[b]=1e-8*exp(-0.5*y*y);
  }
  populateTS_2photon(Trr,Trv,Tvr,Tvv,sr,sv,Dtau,xe,xHII,TM,TR,nH,H,&rates,&twog,Dfplus,Dfplus_Ly,Alpha,DAlpha,Beta,fsR,meR);
  solve_real_virt(xr,xv,Trr,Trv,Tvr,Tvv,sr,sv);
  printf("META,temperature_K,%.17g\n",TK);
  printf("META,nH_cm3,%.17g\n",nH);
  printf("META,H_s_inv,%.17g\n",H);
  printf("META,xe,%.17g\n",xe);
  printf("META,xHII,%.17g\n",xHII);
  for(int i=0;i<2;i++) for(int j=0;j<2;j++) printf("Trr,%d,%d,%.17g\n",i,j,Trr[i][j]);
  for(int i=0;i<2;i++) printf("sr,%d,0,%.17g\n",i,sr[i]);
  for(int i=0;i<2;i++) printf("xr,%d,0,%.17g\n",i,xr[i]);
  for(unsigned b=0;b<NVIRT;b++) {
    printf("sv,%u,0,%.17g\n",b,sv[b]);
    printf("Dtau,%u,0,%.17g\n",b,Dtau[b]);
    printf("xv,%u,0,%.17g\n",b,xv[b]);
    for(int i=0;i<2;i++) {
      printf("Trv,%d,%u,%.17g\n",i,b,Trv[i][b]);
      printf("Tvr,%d,%u,%.17g\n",i,b,Tvr[i][b]);
    }
    for(int k=0;k<3;k++) printf("Tvv,%d,%u,%.17g\n",k,b,Tvv[k][b]);
  }
  return 0;
}
