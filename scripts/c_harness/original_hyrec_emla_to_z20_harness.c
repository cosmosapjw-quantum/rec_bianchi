/* Independent original C replay oracle through the U7 EMLA z=20 stencil.
 * All upstream HyRec C translation units remain unmodified. This is a
 * separate harness and does not alter the saved U5 first-failure run.
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

/* Same-input EMLA oracle. Inputs retain the original source cgs/eV units. */
double rec_r3g_u7_emla_rhs(double xe,double tmK,double trK,double nHcm3,
                           double H,double fsR,double meR) {
  static HRATEEFF rates; static int ready=0;
  if (!ready) {
    memset(&rates,0,sizeof(rates));
    rates.logTR_tab=create_1D_array(NTR);rates.TM_TR_tab=create_1D_array(NTM);
    rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);
    rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);
    rates.logR2p2s_tab=create_1D_array(NTR);
    read_rates(&rates);ready=1;
  }
  return rec_dxHIIdlna(EMLA2s2p,xe,xe,nHcm3,H,kBoltz*tmK,kBoltz*trK,
    &rates,NULL,NULL,NULL,NULL,0.,0,0.,fsR,meR);
}

double rec_r3g_u7_thermal_rhs(double xe,double tmK,double trK,double H,
                              double fHe,double fsR,double meR) {
  return rec_dTmdlna(xe,tmK,trK,H,fHe,fsR,meR);
}

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
  int branch_steps=0, cap=374, u4cap=622, u4_accepted=0, u5cap=8192, u5_accepted=0, thermal_event=-1, coupled=0, u6cap=2604, u6_accepted=0, u7cap=40804, u7_accepted=0, j,b, accepted_extra=0;
  long allocated_nodes;
  long iz;
  if(argc>1) u7cap=atoi(argv[1]);
  if(u7cap<1 || u7cap>40804) { fprintf(stderr,"INVALID_U7_EXTRA_ROW_CAP\n"); return 2; }
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
  allocated_nodes=p.izH0+51776+16;
  if(allocated_nodes<=p.izH0+51776) {
    fprintf(stderr,"U7_NODE_ALLOCATION_OVERFLOW\n"); return 2;
  }
  xe=create_1D_array(allocated_nodes); tm=create_1D_array(allocated_nodes);
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
  if (accepted_extra!=374 || iz!=p.izH0+382 || xhe!=0. || !post || branch_steps!=2) {
    fprintf(stderr,"U3_REPLAY_ENDPOINT_MISMATCH:%d:%ld:%.17g:%d:%d\n",accepted_extra,iz,xhe,post,branch_steps);
    return 3;
  }
  /* The U3 endpoint diagnostic is not an accepted source column. */
  printf("U4NODE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
    iz,z,x1,1.-x1,xhe,xe[iz],tm[iz],post);
  first_event_mask=0; branch_steps=0;
  for(j=0;j<u4cap;j++) {
    long in=iz; int rel=(int)(in-p.izH0), oldpost=post;
    double rhsH=0., tr=p.T0*(1.+z);
    if(in+1>=allocated_nodes) { fprintf(stderr,"U4_NODE_CAPACITY_EXCEEDED\n"); return 5; }
    if(rel+1>=p.nzrt) { printf("U4END,HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY,0,0,%d\n",j); return 0; }
    if(1.-tm[in]/tr>=DLNT_MAX) {
      printf("U4END,HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY,0,0,%d\n",j); return 0;
    }
    if(xhe!=0.) { fprintf(stderr,"U4_HELIUM_NONZERO\n"); return 4; }
    rec_get_xe_next1_H(&p,z,xe[in],tm[in],xe+in+1,&rates,(unsigned)in,
      &twog,outgoing,ly,average,&dHPrev,&dHPrev2,&post);
    rhsH=dHPrev; iz=in+1; z=z_of(iz); x1=1.-xe[iz];
    tm[iz]=rec_Tmss(xe[iz],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    printf("U4STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d\n",
      rel,iz,z,x1,xe[iz],xe[iz],tm[iz],rhsH,post,oldpost && !post);
    print_spectra(rel,outgoing,average,ly);
    u4_accepted++;
    if(rel+1<p.nzrt) clear_column(rel+1,outgoing,average,ly);
    if(first_event_mask==0 && oldpost && !post) { first_event_mask=1; branch_steps=0; }
    else if(first_event_mask!=0) branch_steps++;
    if(first_event_mask!=0 && branch_steps>=2) break;
  }
  printf("U4END,%s,%d,%d,%d\n",first_event_mask==0?"BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED":branch_steps>=2?"EVENT_TWO_STEPS_COMPLETE":"HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE",
    first_event_mask,branch_steps,u4_accepted);
  if(u4_accepted!=622 || iz!=p.izH0+1004 || post || xhe!=0.) {
    fprintf(stderr,"U4_REPLAY_ENDPOINT_MISMATCH:%d:%ld:%d:%.17g\n",u4_accepted,iz,post,xhe); return 6;
  }
  printf("U5NODE,%ld,%.17g,%.17g,%.17g,0,%.17g,%.17g,%d\n",
    iz,z,1.-xe[iz],xe[iz],xe[iz],tm[iz],post);
  {
    double dTprev=0.,dTprev2=0., seedprev=0.,seedprev2=0.;
    for(j=0;j<u5cap;j++) {
      long in=iz; int rel=(int)(in-p.izH0);
      double tr=p.T0*(1.+z), oldxe=xe[in], oldtm=tm[in], rhsH=0.,rhsT=NAN;
      int stage_coupled;
      if(rel>=p.nzrt) { printf("U5END,HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY,%d,%d,%d\n",thermal_event,coupled,u5_accepted); return 0; }
      if(thermal_event<0 && 1.-oldtm/tr>=DLNT_MAX) {
        thermal_event=rel;
        dTprev2=(tm[in-1]-tm[in-3])/(2.*DLNA);
        dTprev =(tm[in]-tm[in-2])/(2.*DLNA);
        seedprev=dTprev; seedprev2=dTprev2;
        printf("U5EVENT,%d,%.17g,%.17g,%.17g\n",thermal_event,1.-oldtm/tr,seedprev2,seedprev);
      }
      stage_coupled=thermal_event>=0;
      if(stage_coupled && (!(kBoltz*tr/p.fsR/p.fsR/p.meR>TR_MIN) || !(oldtm/tr>TM_TR_MIN))) {
        printf("U5END,HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY,%d,%d,%d\n",thermal_event,coupled,u5_accepted); return 0;
      }
      if(stage_coupled) {
        rhsT=rec_dTmdlna(oldxe,oldtm,tr,rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
        rec_get_xe_next2_HTm(FULL,&p,z,oldxe,oldtm,xe+in+1,tm+in+1,
          &rates,(unsigned)in,&twog,outgoing,ly,average,
          &dHPrev,&dTprev,&dHPrev2,&dTprev2);
      } else {
        rec_get_xe_next1_H(&p,z,oldxe,oldtm,xe+in+1,&rates,(unsigned)in,
          &twog,outgoing,ly,average,&dHPrev,&dHPrev2,&post);
      }
      rhsH=dHPrev; iz=in+1; z=z_of(iz);
      if(!stage_coupled)
        tm[iz]=rec_Tmss(xe[iz],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
      printf("U5STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%.17g,%.17g,%.17g,%.17g\n",
        rel,iz,z,1.-xe[iz],xe[iz],tm[iz],rhsH,rhsT,stage_coupled,
        dHPrev,dHPrev2,stage_coupled?dTprev:NAN,stage_coupled?dTprev2:NAN);
      print_spectra(rel,outgoing,average,ly);
      u5_accepted++;
      if(rel+1<p.nzrt) clear_column(rel+1,outgoing,average,ly);
      if(stage_coupled) coupled++;
      if(coupled>=2) break;
    }
    printf("U5END,%s,%d,%d,%d\n",coupled>=2?"THERMAL_EVENT_TWO_STEPS_COMPLETE":
      thermal_event<0?"BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED":
      "HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE",
      thermal_event,coupled,u5_accepted);
    if(u5_accepted!=7364 || thermal_event!=8366 || coupled!=2 ||
       iz!=p.izH0+8368 || post || xhe!=0.) {
      fprintf(stderr,"U5_REPLAY_ENDPOINT_MISMATCH:%d:%d:%d:%ld:%d:%.17g\n",
        u5_accepted,thermal_event,coupled,iz,post,xhe); return 7;
    }
    printf("U6NODE,8368,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
      iz,z,1.-xe[iz],xe[iz],tm[iz],dHPrev,dHPrev2,dTprev,dTprev2);
    for(j=0;j<u6cap;j++) {
      long in=iz; int rel=(int)(in-p.izH0);
      double tr=p.T0*(1.+z), oldxe=xe[in], oldtm=tm[in], rhsT;
      if(rel>=p.nzrt) {
        printf("U6END,STOP_BEFORE_EMLA2S2P_RT_BOUNDARY,%d,%d\n",rel,u6_accepted);
        return 0;
      }
      if(!(kBoltz*tr/p.fsR/p.fsR/p.meR>TR_MIN) || !(oldtm/tr>TM_TR_MIN)) {
        printf("U6END,HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY,%d,%d\n",rel,u6_accepted);
        return 0;
      }
      rhsT=rec_dTmdlna(oldxe,oldtm,tr,rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
      rec_get_xe_next2_HTm(FULL,&p,z,oldxe,oldtm,xe+in+1,tm+in+1,
        &rates,(unsigned)in,&twog,outgoing,ly,average,
        &dHPrev,&dTprev,&dHPrev2,&dTprev2);
      iz=in+1; z=z_of(iz);
      printf("U6STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
        rel,iz,z,1.-xe[iz],xe[iz],tm[iz],dHPrev,rhsT,dHPrev2,dTprev,dTprev2);
      print_spectra(rel,outgoing,average,ly);
      u6_accepted++;
      if(rel+1<p.nzrt) clear_column(rel+1,outgoing,average,ly);
    }
    printf("U6END,%s,%d,%d\n",u6_accepted==2604?"STOP_BEFORE_EMLA2S2P_RT_BOUNDARY":
      "BOUNDED_INTERVAL_COMPLETE_BEFORE_RT",(int)(iz-p.izH0),u6_accepted);
    if (u6_accepted!=2604 || iz!=p.izH0+p.nzrt || xhe!=0. || post) {
      fprintf(stderr,"U7_START_SOURCE_SWITCH_MISMATCH:%d:%ld:%ld\n",u6_accepted,iz,p.izH0+p.nzrt);
      return 8;
    }
    printf("U7NODE,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
      (int)(iz-p.izH0),iz,z,xe[iz],tm[iz],dHPrev,dHPrev2,dTprev,dTprev2);
    for(j=0;j<u7cap;j++) {
      long in=iz; int rel=(int)(in-p.izH0);
      double tr=p.T0*(1.+z),oldxe=xe[in],oldtm=tm[in],nH,H,rhsH,rhsT;
      double oldHprev=dHPrev,oldHprev2=dHPrev2,oldTprev=dTprev,oldTprev2=dTprev2;
      if (rel< p.nzrt || rel>=51776 || in+1>=allocated_nodes) {
        fprintf(stderr,"U7_SOURCE_STAGE_OR_CAPACITY:%d:%ld\n",rel,in); return 9;
      }
      if (!(oldxe>0. && oldxe<1. && oldtm>0. && oldtm<=tr &&
            kBoltz*tr/p.fsR/p.fsR/p.meR>TR_MIN && oldtm/tr>TM_TR_MIN)) {
        printf("U7END,HOLD_NEXT_STAGE_REQUIRED:EMLA_STATE_OR_TABLE,%d,%d\n",rel,u7_accepted);
        return 0;
      }
      nH=1e-6*p.nH0*(1.+z)*(1.+z)*(1.+z);
      H=rec_HubbleConstant(&p,z);
      rhsH=rec_dxHIIdlna(EMLA2s2p,oldxe,oldxe,nH,H,kBoltz*oldtm,kBoltz*tr,
        &rates,&twog,outgoing,ly,average,p.zH0,rel,z,p.fsR,p.meR);
      rhsT=rec_dTmdlna(oldxe,oldtm,tr,H,p.fHe,p.fsR,p.meR);
      rec_get_xe_next2_HTm(FULL,&p,z,oldxe,oldtm,xe+in+1,tm+in+1,
        &rates,(unsigned)in,&twog,outgoing,ly,average,
        &dHPrev,&dTprev,&dHPrev2,&dTprev2);
      iz=in+1;z=z_of(iz);
      printf("U7STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,EMLA2s2p\n",
        rel,in, z_of(in),oldxe,oldtm,rhsH,rhsT,oldHprev,oldHprev2,oldTprev,oldTprev2,
        (double)iz,z,xe[iz],tm[iz]);
      u7_accepted++;
    }
    if(u7_accepted==40804) {
      double target=-log(21.),x0=-log(8001.);
      long ix=(long)floor((target-x0)/DLNA);
      double frac=(target-x0)/DLNA-ix;
      printf("U7Z20,%.17g,%.17g,%ld,%.17g\n",
        rec_interp1d(x0,DLNA,xe,(unsigned)(iz+1),target),
        rec_interp1d(x0,DLNA,tm,(unsigned)(iz+1),target),ix,frac);
    }
    printf("U7END,%s,%d,%d\n",u7_accepted==40804?"STOP_AT_Z20_CUBIC_STENCIL":
      "BOUNDED_EMLA_INTERVAL_COMPLETE_BEFORE_Z20_STENCIL",(int)(iz-p.izH0),u7_accepted);
    (void)seedprev; (void)seedprev2;
  }
  return 0;
}
