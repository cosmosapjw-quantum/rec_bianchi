/* Native common-checkpoint restart adapter for the reviewed R3Q H-only node.
 * It imports scalar endpoint/predictor and accepted V/A/L columns supplied by
 * the controller.  It does not rebuild or claim an independent C history.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hyrectools.h"
#include "hydrogen.h"
#include "history.h"
#include "hyrec_params.h"
extern void rec_set_derived_params(REC_COSMOPARAMS *param);
#define START 72892L
#define U4A_RESTART 74411L
#define U4A_PREFIX 1519L
#define U4B_RESTART 74443L
#define U4B_PREFIX 1551L
static double zof(long iz) { return 8001.*exp(-DLNA*(double)iz)-1.; }
int main(int argc,char **argv) {
  REC_COSMOPARAMS p; HRATEEFF rates; TWO_PHOTON_PARAMS twog;
  double **v,**a,*ly[3],xe,tm,dprev,dprev2,z; long n,j,b,start,prefix; int post,steps,u4b;
  if(argc!=12) return 2;
  steps=atoi(argv[1]); if((steps<1||steps>32)||DLNA!=8.49e-5/4.) return 3;
  xe=strtod(argv[2],0); tm=strtod(argv[3],0); dprev2=strtod(argv[4],0); dprev=strtod(argv[5],0); post=atoi(argv[6]);
  start=strtol(argv[7],0,10); prefix=strtol(argv[8],0,10);
  if(!((start==U4A_RESTART&&prefix==U4A_PREFIX)||(start==U4B_RESTART&&prefix==U4B_PREFIX))) return 6;
  u4b=(start==U4B_RESTART);
  memset(&p,0,sizeof(p)); memset(&rates,0,sizeof(rates)); memset(&twog,0,sizeof(twog));
  p.T0=2.7255;p.obh2=.0224;p.omh2=.14309694000000003;p.odeh2=.31113726660800006;p.w0=-1.;p.Y=.2454;p.Nnueff=3.03821934419124;p.fsR=p.meR=1.;rec_set_derived_params(&p);
  if(p.izH0!=72892||start-p.izH0!=prefix||p.nzrt<=prefix+steps) return 4;
  rates.logTR_tab=create_1D_array(NTR);rates.TM_TR_tab=create_1D_array(NTM);rates.logAlpha_tab[0]=create_2D_array(NTM,NTR);rates.logAlpha_tab[1]=create_2D_array(NTM,NTR);rates.logR2p2s_tab=create_1D_array(NTR);read_rates(&rates);read_twog_params(&twog);
  v=create_2D_array(NVIRT,p.nzrt);a=create_2D_array(NVIRT,p.nzrt);for(b=0;b<3;b++)ly[b]=create_1D_array(p.nzrt);
  for(b=0;b<NVIRT;b++)for(j=0;j<p.nzrt;j++)v[b][j]=a[b][j]=NAN;for(b=0;b<3;b++)for(j=0;j<p.nzrt;j++)ly[b][j]=NAN;
  /* Each file is controller-exported C-order [lane, accepted-column]. */
  { FILE *f=fopen(argv[10],"rb"); if(!f)return 5; for(b=0;b<NVIRT;b++)if(fread(a[b],sizeof(double),prefix,f)!=prefix)return 5; if(fgetc(f)!=EOF)return 5; fclose(f); }
  { FILE *f=fopen(argv[11],"rb"); if(!f)return 5; for(b=0;b<3;b++)if(fread(ly[b],sizeof(double),prefix,f)!=prefix)return 5; if(fgetc(f)!=EOF)return 5; fclose(f); }
  /* Import all previously accepted V lanes in source-column order. */
  { FILE *f=fopen(argv[9],"rb"); if(!f)return 5; for(b=0;b<NVIRT;b++)if(fread(v[b],sizeof(double),prefix,f)!=prefix)return 5; if(fgetc(f)!=EOF)return 5; fclose(f); }
  for(n=0;n<steps;n++) { long g=start+n; unsigned col=(unsigned)(g-72892); z=zof(g);
    /* Match the Python U4B event/stage guards before any RHS or history write. */
    if(u4b && !(1.-tm/(p.T0*(1.+z)) < DLNT_MAX)) return 7;
    if(u4b && g>=p.izH0+p.nzrt) return 8;
    /* history.c receives the global source index and derives col=iz-izH0. */
    rec_get_xe_next1_H(&p,z,xe,tm,&xe,&rates,(unsigned)g,&twog,v,ly,a,&dprev,&dprev2,&post);
    z=zof(g+1);tm=rec_Tmss(xe,p.T0*(1.+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
    printf("STEP,%ld,%ld,%.17g,%.17g,%.17g,%.17g,%d\n",n,g+1,z,1.-xe,xe,tm,post);
    printf("RHS,%ld,%.17g,%.17g\n",n,dprev2,dprev);
    for(b=0;b<NVIRT;b++)printf("V,%ld,%ld,%.17g\n",n,b,v[b][col]);
    for(b=0;b<NVIRT;b++)printf("A,%ld,%ld,%.17g\n",n,b,a[b][col]);
    for(b=0;b<3;b++)printf("L,%ld,%ld,%.17g\n",n,b,ly[b][col]);
    if(u4b && !post) break;
  }
  return 0;
}
