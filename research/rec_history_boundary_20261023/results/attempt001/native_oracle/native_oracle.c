#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#define NVIRT    311
#define NSUBLYA  140
#define NSUBLYB  271
#define DLNA          (8.49e-5/4.)    /* Time step Delta ln(a). Must be smaller than 8.5e-5 if using radiative transfer */
#define E21  10.198714553953742
#define E31  12.087365397278509
#define E41  12.748393192442178
#define E32  1.8886508433247664
#define E42  2.5496786384884356
double square(double x) { return x*x; }
double interp_Dfnu(double lna_start, double dlna, double *ytab, unsigned int iz, double lna){  
   long ind;
   double frac;

   /* If iz = 0 or 1, radiation field at earlier times is still thermal. 
      Also thermal if iz > 1 and lna < lna_start. */
   if (iz == 0 || iz == 1 || lna < lna_start) return 0.;
   
   /* Check if in range */
   if (lna >= lna_start + dlna*(iz-1)) {
       fprintf(stderr, "Error in interp_Dfnu: lna-value out of range in interpolation routine\n"); 
       fprintf(stderr, "The time-step used is probably too large\n");
       exit(1);
    }
 
    /* If iz >= 2, do a linear interpolation so the spectrum is always positive */
    ind  = (long) floor((lna-lna_start)/dlna);
    frac = (lna-lna_start)/dlna - ind;
    
    return (1.-frac)*ytab[ind] + frac*ytab[ind+1];  

}
void fplus_from_fminus(double Dfplus[NVIRT], double Dfplus_Ly[], double **Dfminus_hist, double *Dfminus_Ly_hist[], 
                       double TR, double zstart, unsigned iz, double z, double Eb_tab[NVIRT]) {
   unsigned b;
   double ainv, lna_start, zp1;
  
   zp1 = 1.+z;
   lna_start = -log(1.+zstart);

   /*** Bins below Lyman alpha ***/
   for (b = 0; b < NSUBLYA-1; b++) {
      ainv = zp1*Eb_tab[b+1]/Eb_tab[b]; 
      Dfplus[b] = interp_Dfnu(lna_start, DLNA, Dfminus_hist[b+1], iz, -log(ainv));
   }
 
   /*** highest bin below Ly-alpha: feedback from optically thick Ly-alpha ***/
   b = NSUBLYA-1; 
   ainv = zp1*E21/Eb_tab[b];
   Dfplus[b] = interp_Dfnu(lna_start, DLNA, Dfminus_Ly_hist[0], iz, -log(ainv));
      
   /*** incoming photon occupation number at Lyman alpha ***/ 
   b = NSUBLYA;     /* next highest bin */
   ainv = zp1*Eb_tab[b]/E21;
   Dfplus_Ly[0] = interp_Dfnu(lna_start, DLNA, Dfminus_hist[b], iz, -log(ainv)); 
   
   /*** Bins between Lyman alpha and beta ***/   
   for (b = NSUBLYA; b < NSUBLYB-1; b++) {
     ainv = zp1*Eb_tab[b+1]/Eb_tab[b]; 
     Dfplus[b] = interp_Dfnu(lna_start, DLNA, Dfminus_hist[b+1], iz, -log(ainv));
   }
   
   /*** highest bin below Ly-beta: feedback from Ly-beta ***/
   b = NSUBLYB-1; 
   ainv = zp1*E31/Eb_tab[b];
   Dfplus[b] = interp_Dfnu(lna_start, DLNA, Dfminus_Ly_hist[1], iz, -log(ainv));
   
   /*** incoming photon occupation number at Lyman beta ***/ 
   b = NSUBLYB;     /* next highest bin */
   ainv = zp1*Eb_tab[b]/E31;
   Dfplus_Ly[1] = interp_Dfnu(lna_start, DLNA, Dfminus_hist[b], iz, -log(ainv)); 
  
   /*** Bins between Lyman beta and gamma ***/   
   for (b = NSUBLYB; b < NVIRT-1; b++) {
     ainv = zp1*Eb_tab[b+1]/Eb_tab[b]; 
     Dfplus[b] = interp_Dfnu(lna_start, DLNA, Dfminus_hist[b+1], iz, -log(ainv));
   }

   /*** highest energy bin: feedback from Ly-gamma ***/
   b = NVIRT-1;
   ainv = zp1*E41/Eb_tab[b];
   Dfplus[b] = interp_Dfnu(lna_start, DLNA, Dfminus_Ly_hist[2], iz, -log(ainv));
             
}
void oracle_rhs(double RLya, double x1s, double *Dtau, double *tvv0,
                double *incoming, double *result) {
  double nH=0., s=0., Dxe2=0., Alpha[2]={0.,0.}, DAlpha[2]={0.,0.};
  double *Dfplus=incoming, *Dfplus_Ly=incoming+NVIRT;
  double *sr=result, *sv=result+2, *Tvv[3]={tvv0, tvv0, tvv0};
  double one_minus_Pib; unsigned b;
   sr[0]     = nH * (s*x1s*DAlpha[0] + Alpha[0]*Dxe2) + 3.* RLya * x1s * 1.664786871919931 *Dfplus_Ly[1]; 
   sr[1]     = nH * (s*x1s*DAlpha[1] + Alpha[1]*Dxe2) + 3.*RLya * x1s * Dfplus_Ly[0]; 
  for(b=0;b<NVIRT;b++){
      one_minus_Pib = Dtau[b] > 1e-6 ? 1.- (1.-exp(-Dtau[b]))/Dtau[b] : Dtau[b]/2. - square(Dtau[b])/6.;
      sv[b]  = Tvv[0][b] * x1s * Dfplus[b] * (1.-one_minus_Pib);         
  }
}

void oracle_outgoing(double *X, double *incoming, double x1s, double TR,
                     double *Dtau, double *tvr, double *tvv, double *result) {
  double *xr=X, *xv=X+2, *Dfplus=incoming;
  double *Tvr[2]={tvr,tvr+NVIRT};
  double *Tvv[3]={tvv,tvv+NVIRT,tvv+2*NVIRT};
  double *Dfminus_hist[NVIRT], *Dfminus_Ly_hist[3];
  double one_minus_Pib, Dfeq, one_minus_exptau; unsigned b,iz=0;
  for(b=0;b<NVIRT;b++) Dfminus_hist[b]=result+b;
  for(b=0;b<3;b++) Dfminus_Ly_hist[b]=result+NVIRT+b;
   for (b = 0; b < NVIRT; b++) {
     if (Dtau[b] > 1e-30) {
         one_minus_Pib = Dtau[b] > 1e-6 ? 1.- (1.-exp(-Dtau[b]))/Dtau[b] : Dtau[b]/2. - square(Dtau[b])/6.;
         Dfeq  = -xr[0]*Tvr[0][b] - xr[1]*Tvr[1][b];
         Dfeq -=  (b == 0       ?  xv[1]*Tvv[2][0]:
                   b == NVIRT-1 ?  xv[NVIRT-2]*Tvv[1][NVIRT-1]:    
                   xv[b+1]*Tvv[2][b] + xv[b-1]*Tvv[1][b]);        
         Dfeq /= x1s*one_minus_Pib*Tvv[0][b];
         one_minus_exptau = Dtau[b] > 1e-6 ? 1.-exp(-Dtau[b]) : Dtau[b] - square(Dtau[b])/2.;               
                                
         Dfminus_hist[b][iz] = Dfplus[b] + (Dfeq - Dfplus[b])*one_minus_exptau;
     }
     else Dfminus_hist[b][iz] = Dfplus[b];
   }
    
   Dfminus_Ly_hist[0][iz] = xr[1]/3./x1s;    
   Dfminus_Ly_hist[1][iz] = xr[0]/x1s*exp(-E32/TR); 
   Dfminus_Ly_hist[2][iz] = xr[0]/x1s*exp(-E42/TR); 
}

double oracle_dlna(void) { return DLNA; }
void oracle_mapping(double *history, unsigned cols, unsigned iz, double zstart,
                    double z, double *energy, double *result) {
  double *bins[NVIRT], *lines[3]; unsigned b;
  for(b=0;b<NVIRT;b++) bins[b]=history+b*cols;
  for(b=0;b<3;b++) lines[b]=history+(NVIRT+b)*cols;
  fplus_from_fminus(result,result+NVIRT,bins,lines,0.,zstart,iz,z,energy);
}
