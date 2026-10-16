/* Bounded source-stage oracle: stage update, Hubble and Tm use history.c. */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "helium.h"
#include "hydrogen.h"
#include "history.h"

#define TRMAX 0.4
#define KB 8.617343e-5

static double redshift(int i) { return (1+ZSTART)*exp(-DLNA*i)-1; }
static void print_row(int i,double z,double xe,double xHII,double xHeI,double xHeII,
                      double xHeIII,double tm,double rhs,double zin,double h,double xH1,
                      double xHeIIin,int method,int next_post) {
  printf("%d %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %.17g %d %d\n",
    i,z,xe,xHII,xHeI,xHeII,xHeIII,tm,rhs,zin,h,xH1,xHeIIin,method,next_post);
}
int main(void) {
  REC_COSMOPARAMS p={0};
  p.T0=2.7255; p.obh2=.0224; p.omh2=.14309694000000003;
  p.okh2=0.; p.odeh2=.31113726660800006; p.w0=-1.; p.wa=0.;
  p.Y=.2454; p.Nnueff=3.03821934419124; p.fsR=1.; p.meR=1.;
  p.nH0=11.223846333047*p.obh2*(1-p.Y); p.fHe=p.Y/((1-p.Y)*3.97153);
  p.izH0=(long)floor(1+log(KB*p.T0*(1+ZSTART)/TRMAX)/DLNA);
  double *xe=calloc((size_t)p.izH0+1,sizeof(double));
  double delta=p.fHe,xhe=0.,dp2,dp,z; long i=0; int post=1;
  if(!xe) return 3;
  while(i<=p.izH0+2 && delta>1e-8) {
    z=redshift((int)i);
    xe[i]=rec_xesaha_HeII_III(p.nH0,p.T0,p.fHe,z,&delta,p.fsR,p.meR);
    print_row((int)i,z,xe[i],1.,0.,p.fHe-delta,delta,p.T0*(1+z),0.,z,0.,1.,0.,-1,0);
    ++i;
  }
  if(i<4) return 4;
  dp2=(xe[i-2]-xe[i-4])/(2*DLNA);
  dp =(xe[i-1]-xe[i-3])/(2*DLNA);
  z=redshift((int)i-1); xhe=rec_saha_xHeII(p.nH0,p.T0,p.fHe,z,p.fsR,p.meR);
  for(;i<=p.izH0;i++) {
    double zin=redshift((int)i-1), H=rec_HubbleConstant(&p,zin);
    double xHeIIin=xhe;
    double xH1=rec_saha_xH1s(xhe,p.nH0,p.T0,zin,p.fsR,p.meR);
    double xH1in=xH1;
    double rhs=rec_helium_dxHeIIdlna(xH1,xhe,p.nH0,p.T0,p.fHe,H,zin,p.fsR,p.meR);
    int method=post;
    rec_get_xe_next1_He(&p,zin,&xhe,&dp,&dp2,&post);
    z=redshift((int)i);
    xH1=rec_saha_xH1s(xhe,p.nH0,p.T0,z,p.fsR,p.meR);
    { double xhii=1-xH1, xet=xhii+xhe;
      double tm=rec_Tmss(xet,p.T0*(1+z),rec_HubbleConstant(&p,z),p.fHe,p.fsR,p.meR);
      print_row((int)i,z,xet,xhii,p.fHe-xhe,xhe,0.,tm,rhs,zin,H,
          xH1in,xHeIIin,method,post); }
  }
  free(xe); return 0;
}
