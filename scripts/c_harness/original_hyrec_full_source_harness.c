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
#include "hydrogen.h"
#include "hyrectools.h"

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
