/* Independent native C oracle for R3G-U3 continuation.
 * All upstream HyRec C translation units are compiled unmodified.  This
 * harness reconstructs source U1, advances the eight source-native FULL
 * H+He rows to global index 18231, then continues until the first native
 * branch event plus two accepted rows, or the caller's strict row cap.
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

static void print_spectra(int col, double **out, double **avg, double *ly[3]) {
  int b;
  for (b=0;b<NVIRT;b++) printf("V,%d,%d,%.17g\n",col,b,out[b][col]);
  for (b=0;b<NVIRT;b++) printf("A,%d,%d,%.17g\n",col,b,avg[b][col]);
  for (b=0;b<3;b++) printf("L,%d,%d,%.17g\n",col,b,ly[b][col]);
}

static void clear_column(int col, double **out, double **avg, double *ly[3]) {
  int b;
  for (b=0;b<NVIRT;b++) out[b][col]=avg[b][col]=0.;
  for (b=0;b<3;b++) ly[b][col]=0.;
}

int main(int argc, char **argv) {
  REC_COSMOPARAMS p; HRATEEFF rates; TWO_PHOTON_PARAMS twog;
  double *xe,*tm,**outgoing,**average,*ly[3];
  double dHePrev,dHePrev2,dHPrev,dHPrev2,delta,xhe,x1,z;
  int post=1, first_event_mask=0, cumulative_crossing_mask=0;
  int branch_steps=0, cap=2048, j,b, accepted_extra=0;
  long iz;
  if(argc>1) cap=atoi(argv[1]);
  if(cap<1 || cap>2048) { fprintf(stderr,"INVALID_EXTRA_ROW_CAP\n"); return 2; }
  memset(&p,0,sizeof(p)); memset(&rates,0,sizeof(rates)); memset(&twog,0,sizeof(twog));
  p.T0=2.7255; p.obh2=.0224; p.omh2=.14309694000000003;
  p.okh2=0.; p.odeh2=.31113726660800006; p.w0=-1.; p.wa=0.;
  p.Y=.2454; p.Nnueff=3.03821934419124; p.fsR=p.meR=1.;
  rec_set_derived_params(&p);
  printf("META,%ld,%ld,%.17g\n",p.izH0,p.nzrt,p.zH0);
  rates.logTR_tab=create_1D_array(NTR); rates.TM_TR_tab=create_1D_array(NTM);
  rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);
  rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);
  rates.logR2p2s_tab=create_1D_array(NTR);
  read_rates(&rates); read_twog_params(&twog);
  xe=create_1D_array(p.izH0+cap+16); tm=create_1D_array(p.izH0+cap+16);
  outgoing=create_2D_array(NVIRT,p.nzrt); average=create_2D_array(NVIRT,p.nzrt);
  for(b=0;b<3;b++) { ly[b]=create_1D_array(p.nzrt); for(iz=0;iz<p.nzrt;iz++) ly[b][iz]=0.; }
  for(b=0;b<NVIRT;b++) for(iz=0;iz<p.nzrt;iz++) outgoing[b][iz]=average[b][iz]=0.;

  delta=p.fHe;
  for(iz=0;iz<p.izH0 && delta>1.e-8;iz++) {
    z=z_of(iz);
    xe[iz]=rec_xesaha_HeII_III(p.nH0,p.T0,p.fHe,z,&delta,p.fsR,p.meR);
    tm[iz]=p.T0*(1.+z);
  }
  dHePrev2=(xe[iz-2]-xe[iz-4])/(2.*DLNA);
  dHePrev =(xe[iz-1]-xe[iz-3])/(2.*DLNA);
  z=z_of(iz-1); xhe=rec_saha_xHeII(p.nH0,p.T0,p.fHe,z,p.fsR,p.meR);
  for(;iz<p.izH0+1;iz++) {
    rec_get_xe_next1_He(&p,z,&xhe,&dHePrev,&dHePrev2,&post);
    z=z_of(iz); x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    xe[iz]=(1.-x1)+xhe;
    tm[iz]=rec_Tmss(xe[iz],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
  }
  dHPrev2=(xe[p.izH0-1]-xe[p.izH0-3])/(2.*DLNA)-dHePrev2;
  dHPrev =(xe[p.izH0]-xe[p.izH0-2])/(2.*DLNA)-dHePrev;
  x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
  post=1;

  /* U2 accepted columns 0..7, retained as the exact causal prehistory. */
  for(j=0;j<8;j++) {
    long in=p.izH0+j; double h0=dHPrev, he0=dHePrev;
    get_rec_next2_HHe(&p,(unsigned)in,z,tm[in],&x1,&xhe,&rates,&twog,
      outgoing,ly,average,&dHPrev,&dHePrev,&dHPrev2,&dHePrev2,&post);
    xe[in+1]=(1.-x1)+xhe; z=z_of(in+1);
    tm[in+1]=rec_Tmss(xe[in+1],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    (void)h0; (void)he0;
    if(j+1<p.nzrt) clear_column(j+1,outgoing,average,ly);
  }
  iz=p.izH0+8; z=z_of(iz);
  xe[iz]=(1.-x1)+xhe;
  printf("NODE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
    iz,z,x1,1.-x1,xhe,xe[iz],tm[iz],post);

  for(j=0;j<cap;j++) {
    long in=iz; int rel=(int)(in-p.izH0); double rhsH=0.,rhsHe=0.;
    double oldpost=(double)post, oldxhe=xhe, xh_in;
    int h_only=(xhe<=XHEII_MIN), next_h_only=0, he_cross=0, post_cross=0;
    if(rel+1>=p.nzrt) { printf("END,HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY,%d,%d,%d,%d\n",first_event_mask,cumulative_crossing_mask,branch_steps,8+accepted_extra); return 0; }
    if(h_only && !(1.-tm[in]/(p.T0*(1.+z)) < DLNT_MAX)) {
      printf("END,HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY,%d,%d,%d,%d\n",first_event_mask,cumulative_crossing_mask,branch_steps,8+accepted_extra); return 0;
    }
    if(h_only) { /* Source branch follows accepted He state, not event label. */
      xh_in=xe[in]; x1=1.-xh_in;
      rec_get_xe_next1_H(&p,z,xh_in,tm[in],xe+in+1,&rates,(unsigned)in,
        &twog,outgoing,ly,average,&dHPrev,&dHPrev2,&post);
      rhsH=dHPrev; rhsHe=0.;
      xhe=0.; x1=1.-xe[in+1];
    } else {
      xh_in=1.-x1;
      get_rec_next2_HHe(&p,(unsigned)in,z,tm[in],&x1,&xhe,&rates,&twog,
        outgoing,ly,average,&dHPrev,&dHePrev,&dHPrev2,&dHePrev2,&post);
      rhsH=dHPrev; rhsHe=dHePrev;
      xe[in+1]=(1.-x1)+xhe;
    }
    z=z_of(in+1);
    if(h_only) xe[in+1]=(1.-x1)+xhe;
    tm[in+1]=rec_Tmss(xe[in+1],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    he_cross=(oldxhe>XHEII_MIN && xhe<=XHEII_MIN);
    post_cross=(oldpost==1. && post==0);
    next_h_only=(xhe<=XHEII_MIN);
    printf("STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d,%d,%d,%d,%d\n",
      j+8,in+1,z,x1,1.-x1,xhe,xe[in+1],tm[in+1],rhsH,rhsHe,post,
      cumulative_crossing_mask,he_cross,post_cross,h_only,next_h_only);
    print_spectra(rel,outgoing,average,ly);
    accepted_extra++;
    /* Discard any post-Saha probe written one column beyond this accepted input. */
    if(rel+1<p.nzrt) clear_column(rel+1,outgoing,average,ly);
    if(he_cross) cumulative_crossing_mask|=1;
    if(post_cross) cumulative_crossing_mask|=2;
    if(first_event_mask==0 && (he_cross || post_cross)) {
      first_event_mask=(he_cross?1:0)|(post_cross?2:0); branch_steps=0;
    } else if(first_event_mask!=0) branch_steps++;
    iz=in+1;
    if(first_event_mask!=0 && branch_steps>=2) break;
  }
  printf("END,%s,%d,%d,%d,%d\n",first_event_mask==0?"BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED":branch_steps>=2?"EVENT_TWO_STEPS_COMPLETE":"HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE",
    first_event_mask,cumulative_crossing_mask,branch_steps,8+accepted_extra);
  return 0;
}
