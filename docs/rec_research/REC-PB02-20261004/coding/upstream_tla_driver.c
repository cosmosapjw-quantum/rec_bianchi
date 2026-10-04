/* Independently written caller. Compile against pinned, unmodified upstream
   hydrogen.c and hyrectools.c, kept outside the distributed packet. */
#include <stdio.h>
#include <math.h>
#include "hydrogen.h"
int main(void) {
    REC_COSMOPARAMS cosmo = {0};
    INJ_PARAMS injection = {0};
    cosmo.fsR=1.0; cosmo.meR=1.0; cosmo.inj_params=&injection;
    double T,n,H,x;
    puts("temperature_k,n_h_cm3,hubble_s,xp,alpha_cm3_s,beta_p_s,r_alpha_s,c,dxp_dt_s");
    while (scanf("%lf %lf %lf %lf", &T,&n,&H,&x)==4) {
        if (!(T>0 && n>0 && H>0 && x>=0 && x<1)) return 2;
        double Tr=T*kBoltz;
        double alpha=alphaB_PPB(Tr,1,1);
        double beta=SAHA_FACT(1,1)*Tr*sqrt(Tr)*exp(-0.25*EI/Tr)*alpha;
        double r=LYA_FACT(1,1)*H/n/(1-x);
        double cf=(3*r+L2s1s)/(3*r+L2s1s+beta);
        double dx=H*rec_TLA_dxHIIdlna(&cosmo,x,x,n,H,Tr,Tr,1.0);
        printf("%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",T,n,H,x,alpha,beta,r,cf,dx);
    }
    return ferror(stdin)?3:0;
}
