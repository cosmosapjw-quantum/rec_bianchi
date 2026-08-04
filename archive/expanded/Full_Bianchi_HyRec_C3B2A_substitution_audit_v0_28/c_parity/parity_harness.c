
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define NVIRT 311
#define NDIFF 80
#define NSUBLYA 140
#define NSUBDIFF (NSUBLYA-NDIFF/2)

static int read_doubles(const char *path, double *x, size_t n){
  FILE *f=fopen(path,"rb");
  if(!f){perror(path); return 1;}
  size_t m=fread(x,sizeof(double),n,f);
  fclose(f);
  return m==n ? 0 : 2;
}
static int write_doubles(const char *path, const double *x, size_t n){
  FILE *f=fopen(path,"wb");
  if(!f){perror(path); return 1;}
  size_t m=fwrite(x,sizeof(double),n,f);
  fclose(f);
  return m==n ? 0 : 2;
}

void solveTXeqB(double *diag, double *updiag, double *dndiag,
                double *X, double *B, unsigned N){
  int i;
  double denom;
  double *alpha=calloc(N,sizeof(double));
  double *gamma=calloc(N,sizeof(double));
  if(!alpha || !gamma) exit(20);

  alpha[0]=updiag[0]/diag[0];
  gamma[0]=B[0]/diag[0];

  for(i=1;i<(int)N;i++){
    denom=diag[i]-dndiag[i]*alpha[i-1];
    alpha[i]=updiag[i]/denom;
    gamma[i]=(B[i]-dndiag[i]*gamma[i-1])/denom;
  }

  X[N-1]=gamma[N-1];
  for(i=(int)N-2;i>=0;i--)
    X[i]=gamma[i]-alpha[i]*X[i+1];

  free(alpha);
  free(gamma);
}

void solve_real_virt(double xr[2], double xv[NVIRT],
                     double Trr[2][2], double *Trv[2],
                     double *Tvr[2], double *Tvv[3],
                     double sr[2], double sv[NVIRT]){
  double *Tvv_inv_Tvr[2];
  double *Tvv_inv_sv;
  double Trr_new[2][2];
  double sr_new[2];
  unsigned i,j,b;
  double det;

  for(i=0;i<2;i++)
    Tvv_inv_Tvr[i]=calloc(NVIRT,sizeof(double));
  Tvv_inv_sv=calloc(NVIRT,sizeof(double));
  if(!Tvv_inv_Tvr[0] || !Tvv_inv_Tvr[1] || !Tvv_inv_sv)
    exit(21);

  for(i=0;i<2;i++){
    for(b=0;b<NSUBDIFF;b++)
      Tvv_inv_Tvr[i][b]=Tvr[i][b]/Tvv[0][b];
    for(b=NSUBLYA+NDIFF/2;b<NVIRT;b++)
      Tvv_inv_Tvr[i][b]=Tvr[i][b]/Tvv[0][b];

    solveTXeqB(
      Tvv[0]+NSUBDIFF,
      Tvv[2]+NSUBDIFF,
      Tvv[1]+NSUBDIFF,
      Tvv_inv_Tvr[i]+NSUBDIFF,
      Tvr[i]+NSUBDIFF,
      NDIFF
    );
  }

  for(i=0;i<2;i++) for(j=0;j<2;j++){
    Trr_new[i][j]=Trr[i][j];
    for(b=0;b<NVIRT;b++)
      Trr_new[i][j]-=Trv[i][b]*Tvv_inv_Tvr[j][b];
  }

  for(b=0;b<NSUBDIFF;b++)
    Tvv_inv_sv[b]=sv[b]/Tvv[0][b];
  for(b=NSUBLYA+NDIFF/2;b<NVIRT;b++)
    Tvv_inv_sv[b]=sv[b]/Tvv[0][b];

  solveTXeqB(
    Tvv[0]+NSUBDIFF,
    Tvv[2]+NSUBDIFF,
    Tvv[1]+NSUBDIFF,
    Tvv_inv_sv+NSUBDIFF,
    sv+NSUBDIFF,
    NDIFF
  );

  for(i=0;i<2;i++){
    sr_new[i]=sr[i];
    for(b=0;b<NVIRT;b++)
      sr_new[i]-=Trv[i][b]*Tvv_inv_sv[b];
  }

  det=Trr_new[0][0]*Trr_new[1][1]
      -Trr_new[0][1]*Trr_new[1][0];

  xr[0]=(Trr_new[1][1]*sr_new[0]
        -Trr_new[0][1]*sr_new[1])/det;
  xr[1]=(Trr_new[0][0]*sr_new[1]
        -Trr_new[1][0]*sr_new[0])/det;

  for(b=0;b<NVIRT;b++)
    xv[b]=Tvv_inv_sv[b]
          -Tvv_inv_Tvr[0][b]*xr[0]
          -Tvv_inv_Tvr[1][b]*xr[1];

  for(i=0;i<2;i++) free(Tvv_inv_Tvr[i]);
  free(Tvv_inv_sv);
}

int main(int argc,char **argv){
  if(argc!=3) return 2;
  char path[4096];
  double Trr_flat[4], Trv_flat[2*NVIRT], Tvr_flat[2*NVIRT];
  double diag[NVIRT], lower[NVIRT], upper[NVIRT];
  double sr[2], sv[NVIRT];

  #define READ_ARRAY(name,ptr,n) do{ \
    snprintf(path,sizeof(path),"%s/%s.bin",argv[1],name); \
    if(read_doubles(path,ptr,n)) return 3; \
  }while(0)

  READ_ARRAY("Trr",Trr_flat,4);
  READ_ARRAY("Trv",Trv_flat,2*NVIRT);
  READ_ARRAY("Tvr",Tvr_flat,2*NVIRT);
  READ_ARRAY("Tvv_diag",diag,NVIRT);
  READ_ARRAY("Tvv_lower",lower,NVIRT);
  READ_ARRAY("Tvv_upper",upper,NVIRT);
  READ_ARRAY("sr",sr,2);
  READ_ARRAY("sv",sv,NVIRT);

  double *Trv[2]={Trv_flat,Trv_flat+NVIRT};
  double *Tvr[2]={Tvr_flat,Tvr_flat+NVIRT};
  double *Tvv[3]={diag,lower,upper};
  double (*Trr)[2]=(double (*)[2])Trr_flat;

  double xr[2],xv[NVIRT],out[2+NVIRT];
  solve_real_virt(xr,xv,Trr,Trv,Tvr,Tvv,sr,sv);

  out[0]=xr[0];
  out[1]=xr[1];
  memcpy(out+2,xv,sizeof(xv));

  return write_doubles(argv[2],out,2+NVIRT);
}
