/* Independent original October-2012 native h/4 reference, bounded start only.
 * Compile against a temporary frozen source copy whose only edit is the
 * active DLNA token (8.49e-5/4.). The source ZIP and source operators stay fixed.
 * No Python or h/2 state is accepted. The complete He history is rebuilt here.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef R3O_H4_SHARED
#include "hyrectools.h"
#include "helium.h"
#include "hydrogen.h"
#include "history.h"
#include "hyrec_params.h"

extern void rec_set_derived_params(REC_COSMOPARAMS *param);

static double z_of(long iz) { return 8001.*exp(-DLNA*(double)iz)-1.; }

static void he_row(long i, double z, double xe, double h, double he1,
                   double he2, double he3, double tm, double rhs,
                   double zin, double H, double x1in, double hein,
                   int method, int post) {
  printf("HE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d\n",
         i,z,xe,h,he1,he2,he3,tm,rhs,zin,H,x1in,hein,method,post);
}

static void memory_row(int j, double he2, double he, double h2, double h) {
  printf("MEM,%d,%.17g,%.17g,%.17g,%.17g\n",j,he2,he,h2,h);
}

int main(int argc, char **argv) {
  REC_COSMOPARAMS p;
  HRATEEFF rates;
  TWO_PHOTON_PARAMS twog;
  double *xe, *tm, **outgoing, **average, *ly[3];
  double dHe, dHe2, dH, dH2, delta, xhe, x1, z;
  int post=1, j, b, steps=8;
  long iz, capacity;
  if(argc==2) {
    char *end=NULL;
    long parsed=strtol(argv[1],&end,10);
    if(!end || *end || end==argv[1] || parsed<0 || parsed>8) return 2;
    steps=(int)parsed;
  } else if(argc!=1) return 2;
  memset(&p,0,sizeof(p)); memset(&rates,0,sizeof(rates)); memset(&twog,0,sizeof(twog));
  p.T0=2.7255; p.obh2=0.0224; p.omh2=0.14309694000000003;
  p.okh2=0.; p.odeh2=0.31113726660800006; p.w0=-1.; p.wa=0.;
  p.Y=0.2454; p.Nnueff=3.03821934419124; p.fsR=p.meR=1.;
  rec_set_derived_params(&p);
  if(DLNA!=8.49e-5/4. || p.izH0!=72892 || p.nzrt<=steps) return 4;
  printf("META,%.17g,%ld,%ld,%d\n",DLNA,p.izH0,p.nzrt,steps);
  xe=create_1D_array(p.izH0+steps+1); tm=create_1D_array(p.izH0+steps+1);
  delta=p.fHe;
  for(iz=0;iz<p.izH0 && delta>1.e-8;iz++) {
    z=z_of(iz);
    xe[iz]=rec_xesaha_HeII_III(p.nH0,p.T0,p.fHe,z,&delta,p.fsR,p.meR);
    tm[iz]=p.T0*(1.+z);
    he_row(iz,z,xe[iz],1.,0.,p.fHe-delta,delta,tm[iz],0.,z,0.,1.,0.,-1,0);
  }
  if(iz<4 || delta>1.e-8) return 5;
  dHe2=(xe[iz-2]-xe[iz-4])/2./DLNA;
  dHe=(xe[iz-1]-xe[iz-3])/2./DLNA;
  z=z_of(iz-1);
  xhe=rec_saha_xHeII(p.nH0,p.T0,p.fHe,z,p.fsR,p.meR);
  for(;iz<p.izH0+1;iz++) {
    double zin=z, H=rec_HubbleConstant(&p,z), hein=xhe;
    double x1in=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    double rhs=rec_helium_dxHeIIdlna(x1in,xhe,p.nH0,p.T0,p.fHe,H,z,p.fsR,p.meR);
    int method=post;
    rec_get_xe_next1_He(&p,z,&xhe,&dHe,&dHe2,&post);
    z=z_of(iz); x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    xe[iz]=(1.-x1)+xhe;
    tm[iz]=rec_Tmss(xe[iz],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    he_row(iz,z,xe[iz],1.-x1,p.fHe-xhe,xhe,0.,tm[iz],rhs,zin,H,x1in,hein,method,post);
  }
  dH2=(xe[p.izH0-1]-xe[p.izH0-3])/2./DLNA-dHe2;
  dH=(xe[p.izH0]-xe[p.izH0-2])/2./DLNA-dHe;
  x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR); post=1;
  printf("NODE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
         p.izH0,z,x1,1.-x1,xhe,xe[p.izH0],tm[p.izH0],post);
  memory_row(-1,dHe2,dHe,dH2,dH);
  if(steps==0) {
    printf("DONE,%ld,0,%.17g\n",p.izH0+1,DLNA);
    free(xe); free(tm); return 0;
  }
  rates.logTR_tab=create_1D_array(NTR); rates.TM_TR_tab=create_1D_array(NTM);
  rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);
  rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);
  rates.logR2p2s_tab=create_1D_array(NTR);
  read_rates(&rates); read_twog_params(&twog);
  /* Only accepted start columns plus one scratch post-Saha column exist.
   * param.nzrt retains the original source value; no later RT state is made.
   */
  capacity=steps+1;
  outgoing=create_2D_array(NVIRT,capacity); average=create_2D_array(NVIRT,capacity);
  for(b=0;b<3;b++) ly[b]=create_1D_array(capacity);
  for(iz=0;iz<capacity;iz++) {
    for(b=0;b<NVIRT;b++) outgoing[b][iz]=average[b][iz]=NAN;
    for(b=0;b<3;b++) ly[b][iz]=NAN;
  }
  for(j=0;j<steps;j++) {
    if(xhe<=XHEII_MIN) return 6;
    get_rec_next2_HHe(&p,(unsigned)(p.izH0+j),z,tm[p.izH0+j],&x1,&xhe,
                     &rates,&twog,outgoing,ly,average,&dH,&dHe,&dH2,&dHe2,&post);
    z=z_of(p.izH0+j+1); xe[p.izH0+j+1]=(1.-x1)+xhe;
    tm[p.izH0+j+1]=rec_Tmss(xe[p.izH0+j+1],p.T0*(1.+z),
                            rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    printf("STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
           j,p.izH0+j+1,z,x1,1.-x1,xhe,xe[p.izH0+j+1],tm[p.izH0+j+1],dH,dHe,post);
    for(b=0;b<NVIRT;b++) printf("V,%d,%d,%.17g\n",j,b,outgoing[b][j]);
    for(b=0;b<NVIRT;b++) printf("A,%d,%d,%.17g\n",j,b,average[b][j]);
    for(b=0;b<3;b++) printf("L,%d,%d,%.17g\n",j,b,ly[b][j]);
    memory_row(j,dHe2,dHe,dH2,dH);
    /* Trial j+1 is not accepted and is never allowed to seed future input. */
    for(b=0;b<NVIRT;b++) outgoing[b][j+1]=average[b][j+1]=NAN;
    for(b=0;b<3;b++) ly[b][j+1]=NAN;
  }
  printf("DONE,%ld,%d,%.17g\n",p.izH0+1,steps,DLNA);
  free(xe); free(tm); free_2D_array(outgoing,NVIRT); free_2D_array(average,NVIRT);
  for(b=0;b<3;b++) free(ly[b]);
  free(rates.logTR_tab); free(rates.TM_TR_tab); free(rates.logR2p2s_tab);
  for(b=0;b<2;b++) free_2D_array(rates.logAlpha_tab[b],NTM);
  return 0;
}
#else
/* Reuse the clock-free ABI wrapper. Original hydrogen.c obtains the h4 DLNA
 * from the same temporary header used by the independent trajectory build.
 */
#include "original_hyrec_full_source_harness.c"
#endif
