/* First eight native October-2012 FULL H+He accepted steps after izH0.
 * All upstream HyRec C files are compiled unmodified. This harness rebuilds
 * the native He stages, then uses get_rec_next2_HHe and its original FULL
 * photon arrays. Rows contain source states/RHS/branch; spectrum records
 * contain the committed outgoing columns. It is an oracle, not a solver port.
 */
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

static double z_of(long iz) { return (1.+ZSTART)*exp(-DLNA*(double)iz)-1.; }

int main(void) {
  REC_COSMOPARAMS p;
  HRATEEFF rates;
  TWO_PHOTON_PARAMS twog;
  double *xe,*tm,**outgoing,**average,*ly[3];
  double dHePrev,dHePrev2,dHPrev,dHPrev2,delta,xhe,x1,z;
  int post=1;
  long iz;
  int j,b;
  memset(&p,0,sizeof(p)); memset(&rates,0,sizeof(rates)); memset(&twog,0,sizeof(twog));
  p.T0=2.7255; p.obh2=0.0224; p.omh2=0.14309694000000003;
  p.okh2=0.; p.odeh2=0.31113726660800006; p.w0=-1.; p.wa=0.;
  p.Y=0.2454; p.Nnueff=3.03821934419124; p.fsR=p.meR=1.;
  rec_set_derived_params(&p);
  rates.logTR_tab=create_1D_array(NTR); rates.TM_TR_tab=create_1D_array(NTM);
  rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);
  rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);
  rates.logR2p2s_tab=create_1D_array(NTR);
  read_rates(&rates); read_twog_params(&twog);
  xe=create_1D_array(p.izH0+9); tm=create_1D_array(p.izH0+9);
  outgoing=create_2D_array(NVIRT,p.nzrt); average=create_2D_array(NVIRT,p.nzrt);
  for(b=0;b<3;b++) { ly[b]=create_1D_array(p.nzrt); for(iz=0;iz<p.nzrt;iz++) ly[b][iz]=0.; }
  /* calloc-backed histories are initialized explicitly for the U1 prehistory. */
  for(b=0;b<NVIRT;b++) for(iz=0;iz<p.nzrt;iz++) outgoing[b][iz]=average[b][iz]=0.;
  delta=p.fHe;
  for(iz=0;iz<p.izH0 && delta>1.e-8;iz++) {
    z=z_of(iz);
    xe[iz]=rec_xesaha_HeII_III(p.nH0,p.T0,p.fHe,z,&delta,p.fsR,p.meR);
    tm[iz]=p.T0*(1.+z);
  }
  dHePrev2=(xe[iz-2]-xe[iz-4])/(2.*DLNA);
  dHePrev=(xe[iz-1]-xe[iz-3])/(2.*DLNA);
  z=z_of(iz-1);
  xhe=rec_saha_xHeII(p.nH0,p.T0,p.fHe,z,p.fsR,p.meR);
  for(;iz<p.izH0+1;iz++) {
    rec_get_xe_next1_He(&p,z,&xhe,&dHePrev,&dHePrev2,&post);
    z=z_of(iz);
    x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    xe[iz]=(1.-x1)+xhe;
    tm[iz]=rec_Tmss(xe[iz],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
  }
  /* Reconstruct source H derivative history from native xe and He seeds. */
  dHPrev2=(xe[p.izH0-1]-xe[p.izH0-3])/(2.*DLNA)-dHePrev2;
  dHPrev=(xe[p.izH0]-xe[p.izH0-2])/(2.*DLNA)-dHePrev;
  x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
  post=1;
  printf("NODE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
    p.izH0,z,x1,1.-x1,xhe,xe[p.izH0],tm[p.izH0],post);
  for(j=0;j<8;j++) {
    double x1in=x1, xhein=xhe, rhsH, rhsHe;
    unsigned col=(unsigned)j;
    get_rec_next2_HHe(&p,(unsigned)(p.izH0+j),z,tm[p.izH0+j],&x1,&xhe,
      &rates,&twog,outgoing,ly,average,&dHPrev,&dHePrev,&dHPrev2,&dHePrev2,&post);
    rhsH=dHPrev; rhsHe=dHePrev;
    z=z_of(p.izH0+j+1);
    xe[p.izH0+j+1]=(1.-x1)+xhe;
    tm[p.izH0+j+1]=rec_Tmss(xe[p.izH0+j+1],p.T0*(1.+z),
      rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    printf("STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
      j,p.izH0+j+1,z,x1,1.-x1,xhe,xe[p.izH0+j+1],tm[p.izH0+j+1],rhsH,rhsHe,post);
    for(b=0;b<NVIRT;b++) printf("V,%d,%d,%.17g\n",j,b,outgoing[b][col]);
    for(b=0;b<NVIRT;b++) printf("A,%d,%d,%.17g\n",j,b,average[b][col]);
    for(b=0;b<3;b++) printf("L,%d,%d,%.17g\n",j,b,ly[b][col]);
    /* The source post-Saha helper wrote trial outgoing values at j+1. They
       are not accepted. Clear them so subsequent calls can only see columns
       already committed by their own current-state FULL RHS. */
    if(j+1<p.nzrt) {
      for(b=0;b<NVIRT;b++) outgoing[b][j+1]=average[b][j+1]=0.;
      for(b=0;b<3;b++) ly[b][j+1]=0.;
    }
    (void)x1in; (void)xhein;
  }
  return 0;
}
