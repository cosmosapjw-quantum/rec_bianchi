/* Native October-2012 h/2 oracle for the U4 post-Saha exit.
 * Reconstruct every stage from z=8000; never import Python states. Only the
 * newly accepted columns beginning at global 37207 are emitted. The original
 * copied header has exactly one active DLNA token changed to h/2.
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

static void print_row(int i,double z,double xe,double xHII,double xHeI,double xHeII,
                      double xHeIII,double tm,double rhs,double zin,double h,double xH1,
                      double xHeIIin,int method,int next_post) {
  printf("HE,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d\n",
    i,z,xe,xHII,xHeI,xHeII,xHeIII,tm,rhs,zin,h,xH1,xHeIIin,method,next_post);
}

#ifndef R3I_SHARED
int main(void) {
  REC_COSMOPARAMS p;
  HRATEEFF rates;
  TWO_PHOTON_PARAMS twog;
  double *xe,*tm,**outgoing,**average,*ly[3];
  int event=-1,event_type=0,max_extra=4096;
  const char *extra_env=getenv("R3I_MAX_EXTRA_ACCEPTED");
  double dHePrev,dHePrev2,dHPrev,dHPrev2,delta,xhe,x1,z;
  int post=1;
  long iz;
  int j,b;
  memset(&p,0,sizeof(p)); memset(&rates,0,sizeof(rates)); memset(&twog,0,sizeof(twog));
  if(extra_env) {
    char *end;
    long requested=strtol(extra_env,&end,10);
    if(*end!='\0' || requested<1 || requested>4096) return 5;
    max_extra=(int)requested;
  }
  p.T0=2.7255; p.obh2=0.0224; p.omh2=0.14309694000000003;
  p.okh2=0.; p.odeh2=0.31113726660800006; p.w0=-1.; p.wa=0.;
  p.Y=0.2454; p.Nnueff=3.03821934419124; p.fsR=p.meR=1.;
  rec_set_derived_params(&p);
  if(p.izH0!=36446 || p.izH0+1>50000) return 4;
  printf("PARAM,%ld,%ld,%ld\n",p.izH0,p.nzrt,p.izH0+p.nzrt);
  rates.logTR_tab=create_1D_array(NTR); rates.TM_TR_tab=create_1D_array(NTM);
  rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);
  rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);
  rates.logR2p2s_tab=create_1D_array(NTR);
  read_rates(&rates); read_twog_params(&twog);
  xe=create_1D_array(p.izH0+761+4096+1); tm=create_1D_array(p.izH0+761+4096+1);
  outgoing=create_2D_array(NVIRT,p.nzrt); average=create_2D_array(NVIRT,p.nzrt);
  for(b=0;b<3;b++) { ly[b]=create_1D_array(p.nzrt); for(iz=0;iz<p.nzrt;iz++) ly[b][iz]=NAN; }
  /* calloc-backed histories are initialized explicitly for the U1 prehistory. */
  for(b=0;b<NVIRT;b++) for(iz=0;iz<p.nzrt;iz++) outgoing[b][iz]=average[b][iz]=NAN;
  delta=p.fHe;
  for(iz=0;iz<p.izH0 && delta>1.e-8;iz++) {
    z=z_of(iz);
    xe[iz]=rec_xesaha_HeII_III(p.nH0,p.T0,p.fHe,z,&delta,p.fsR,p.meR);
    tm[iz]=p.T0*(1.+z);
    print_row((int)iz,z,xe[iz],1.,0.,p.fHe-delta,delta,tm[iz],0.,z,0.,1.,0.,-1,0);
  }
  dHePrev2=(xe[iz-2]-xe[iz-4])/(2.*DLNA);
  dHePrev=(xe[iz-1]-xe[iz-3])/(2.*DLNA);
  z=z_of(iz-1);
  xhe=rec_saha_xHeII(p.nH0,p.T0,p.fHe,z,p.fsR,p.meR);
  for(;iz<p.izH0+1;iz++) {
    double zin=z,H=rec_HubbleConstant(&p,z),xin=xhe;
    double x1in=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    double rhs=rec_helium_dxHeIIdlna(x1in,xhe,p.nH0,p.T0,p.fHe,H,z,p.fsR,p.meR);
    int method=post;
    rec_get_xe_next1_He(&p,z,&xhe,&dHePrev,&dHePrev2,&post);
    z=z_of(iz);
    x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    xe[iz]=(1.-x1)+xhe;
    tm[iz]=rec_Tmss(xe[iz],p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    print_row((int)iz,z,xe[iz],1.-x1,p.fHe-xhe,xhe,0.,tm[iz],rhs,zin,H,x1in,xin,method,post);
  }
  /* Reconstruct source H derivative history from native xe and He seeds. */
  dHPrev2=(xe[p.izH0-1]-xe[p.izH0-3])/(2.*DLNA)-dHePrev2;
  dHPrev=(xe[p.izH0]-xe[p.izH0-2])/(2.*DLNA)-dHePrev;
  x1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
  post=1;
  printf("NODE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
    p.izH0,z,x1,1.-x1,xhe,xe[p.izH0],tm[p.izH0],post);
  for(j=0;j<761+max_extra;j++) {
    double rhsH, rhsHe=NAN;
    int was_post=post, branch=(xhe > XHEII_MIN);
    unsigned col=(unsigned)j;
    if(j>=761 && event>=0 && j>=event+2) break;
    if(j>=761) {
      if(j==761)
        printf("BASE,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
          p.izH0+j,z,x1,1.-x1,xhe,xe[p.izH0+j],tm[p.izH0+j],post);
      double thermal=1.-tm[p.izH0+j]/p.T0/(1.+z);
      if(!(thermal<DLNT_MAX)) {
        fprintf(stderr,"HOLD_THERMAL_STAGE_BEFORE_ENDPOINT:%ld\n",p.izH0+j);
        return 6;
      }
      if(j>=p.nzrt) {
        fprintf(stderr,"HOLD_RT_STAGE_BEFORE_ENDPOINT:%ld\n",p.izH0+j);
        return 7;
      }
      if(branch) { fprintf(stderr,"HOLD_HELIUM_STAGE_REENTRY:%ld\n",p.izH0+j); return 8; }
      if(!post && event<0) {
        fprintf(stderr,"HOLD_POST_SAHA_EXIT_BEFORE_REVIEWED_BASE:%ld\n",p.izH0+j);
        return 9;
      }
    }
    if(branch) {
      get_rec_next2_HHe(&p,(unsigned)(p.izH0+j),z,tm[p.izH0+j],&x1,&xhe,
        &rates,&twog,outgoing,ly,average,&dHPrev,&dHePrev,&dHPrev2,&dHePrev2,&post);
      xe[p.izH0+j+1]=(1.-x1)+xhe;
      rhsHe=dHePrev;
    } else {
      /* Source H-only branch passes TOTAL previous xe, with helium now neutral. */
      rec_get_xe_next1_H(&p,z,xe[p.izH0+j],tm[p.izH0+j],
        xe+p.izH0+j+1,&rates,(unsigned)(p.izH0+j),&twog,
        outgoing,ly,average,&dHPrev,&dHPrev2,&post);
      x1=1.-xe[p.izH0+j+1];
      xhe=0.;
    }
    rhsH=dHPrev;
    z=z_of(p.izH0+j+1);
    tm[p.izH0+j+1]=rec_Tmss(xe[p.izH0+j+1],p.T0*(1.+z),
      rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    if(j>=761) {
      printf("STEP,%d,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d\n",
        j-761,p.izH0+j+1,z,x1,1.-x1,xhe,xe[p.izH0+j+1],
        tm[p.izH0+j+1],rhsH,rhsHe,post,branch);
      for(b=0;b<NVIRT;b++) printf("V,%d,%d,%.17g\n",j-761,b,outgoing[b][col]);
      for(b=0;b<NVIRT;b++) printf("A,%d,%d,%.17g\n",j-761,b,average[b][col]);
      for(b=0;b<3;b++) printf("L,%d,%d,%.17g\n",j-761,b,ly[b][col]);
    }
    if(j+1<p.nzrt) {
      for(b=0;b<NVIRT;b++) outgoing[b][j+1]=average[b][j+1]=NAN;
      for(b=0;b<3;b++) ly[b][j+1]=NAN;
    }
    if(event<0 && j>=761 && was_post && !post) { event=j+1; event_type=2; }
  }
  printf("EVENT,%d,%d,%d\n",event<0 ? -1:event-761,event_type,j-761);
  return 0;
}

#endif
#ifdef R3I_SHARED
/* Original HyRec2012 C source oracle for PR92 R3b.
 * The original hydrogen.c/hyrectools.c functions are compiled UNMODIFIED.
 * This adapter exposes their actual populateTS_2photon, solve_real_virt and
 * rec_HMLA_2photon_dxHIIdlna, with canonical current-history writeback.
 *
 * To avoid unsafe global chdir in a threaded code path, initialize once
 * while running in an extracted original HyRec/ data directory.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

extern double rec_HMLA_2photon_dxHIIdlna(
    double xe, double xHII, double nH, double H, double TM, double TR,
    HRATEEFF *rate_table, TWO_PHOTON_PARAMS *twog,
    double **Dfminus_hist, double *Dfminus_Ly_hist[], double **Dfnu_hist,
    double zstart, unsigned iz, double z, double fsR, double meR);

static HRATEEFF rate_table;
static TWO_PHOTON_PARAMS twog;
static int loaded = 0;
static void setup(void) {
    if (loaded) return;
    rate_table.logTR_tab=create_1D_array(NTR);
    rate_table.TM_TR_tab=create_1D_array(NTM);
    rate_table.logAlpha_tab[0]=create_2D_array(NTM,NTR);
    rate_table.logAlpha_tab[1]=create_2D_array(NTM,NTR);
    rate_table.logR2p2s_tab=create_1D_array(NTR);
    read_rates(&rate_table);
    read_twog_params(&twog);
    loaded=1;
}

/* Native 2+311 matrix and source snapshot output, identical arrays as raw C.
 * Input xHII,xe dimensionless, nH [cm^-3], H [s^-1], TM,TR [eV].
 * All output buffers must be contiguous double and hold indicated elements.
 */
__attribute__((visibility("default")))
void rec_r3b_populate(double xe, double xHII, double nH, double H,
                     double TM, double TR, double *Dfplus, double *Dfplus_Ly,
                     double *Trr_out, double *Trv_out, double *Tvr_out,
                     double *Tvv_out, double *sr_out, double *sv_out,
                     double *Dtau_out, double *Alpha_out, double *DAlpha_out,
                     double *Beta_out, double *xr_out, double *xv_out)
{
    double rr[2][2];
    double rv[2][NVIRT], vr[2][NVIRT], vv[3][NVIRT];
    double *rp[2] = {rv[0],rv[1]};
    double *vp[2] = {vr[0],vr[1]};
    double *tridiag[3] = {vv[0],vv[1],vv[2]};
    double sr[2], sv[NVIRT], tau[NVIRT], al[2], da[2], be[2], xr[2],xv[NVIRT];
    memset(rr,0,sizeof(rr));
    memset(rv,0,sizeof(rv));
    memset(vr,0,sizeof(vr));
    memset(vv,0,sizeof(vv));
    setup();
    populateTS_2photon(rr,rp,vp,tridiag,sr,sv,tau,xe,xHII,TM,TR,
                      nH,H,&rate_table,&twog,Dfplus,Dfplus_Ly,al,da,be,1.,1.);
    solve_real_virt(xr,xv,rr,rp,vp,tridiag,sr,sv);
    memcpy(Trr_out,rr,sizeof(rr));
    memcpy(Trv_out,rv,sizeof(rv));
    memcpy(Tvr_out,vr,sizeof(vr));
    memcpy(Tvv_out,vv,sizeof(vv));
    memcpy(sr_out,sr,sizeof(sr));
    memcpy(sv_out,sv,sizeof(sv));
    memcpy(Dtau_out,tau,sizeof(tau));
    memcpy(Alpha_out,al,sizeof(al));
    memcpy(DAlpha_out,da,sizeof(da));
    memcpy(Beta_out,be,sizeof(be));
    memcpy(xr_out,xr,sizeof(xr));
    memcpy(xv_out,xv,sizeof(xv));
}

/* Calls the FULL original 2012 atomic+radiation source function and returns
 * its electron derivative and its accepted index iz outgoing virtual/lyman/
 * average spectrum. All prior outgoing histories are passed unchanged by
 * caller as flattened C-order [NVIRT,iz], [3,iz]. No input reference xe(z).
 * Memory capacity iz+1 allows one appended step.
 */
__attribute__((visibility("default")))
double rec_r3b_original_full_step(
    double xe,double xHII,double nH,double H,double TM,double TR,
    double zstart,unsigned iz,double z,
    const double *accepted_virtual,const double *accepted_lyman,
    double *out_virtual,double *out_lyman,double *out_average)
{
    unsigned b,j;
    double **v=create_2D_array(NVIRT,iz+1);
    double **avg=create_2D_array(NVIRT,iz+1);
    double *ly[3];
    double value;
    for(b=0;b<3;b++) ly[b]=create_1D_array(iz+1);
    for(b=0;b<NVIRT;b++)
      for(j=0;j<iz;j++) v[b][j]=accepted_virtual[b*iz+j];
    for(b=0;b<3;b++)
      for(j=0;j<iz;j++) ly[b][j]=accepted_lyman[b*iz+j];
    setup();
    value=rec_HMLA_2photon_dxHIIdlna(
        xe,xHII,nH,H,TM,TR,&rate_table,&twog,v,ly,avg,zstart,iz,z,1.,1.);
    for(b=0;b<NVIRT;b++) {
      out_virtual[b]=v[b][iz];
      out_average[b]=avg[b][iz];
    }
    for(b=0;b<3;b++) out_lyman[b]=ly[b][iz];
    free_2D_array(v,NVIRT);
    free_2D_array(avg,NVIRT);
    for(b=0;b<3;b++) free(ly[b]);
    return value;
}

#endif
