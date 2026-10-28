/* Observation only: raw values already produced by the original transition. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "hyrectools.h"
#include "hydrogen.h"
#include "history.h"
#include "capture_support.h"

#define CAP_N 7489
static FILE *nodes,*calls,*writes,*recur,*seeds,*qss;
static long origin,global_n;
static const char *phase="HEIII_SAHA";
static unsigned long count=0,detailed=0,active_id=0,last_id=0,write_count=0;
static unsigned long last_writer[CAP_N];
static int selected[CAP_N];
static const char *directory;

static void fail(const char *why){fprintf(stderr,"CAPTURE_STOP:%s\n",why);fflush(NULL);exit(86);}
static FILE *open_file(const char *name,const char *mode){
    char path[4096];FILE *f;
    if(snprintf(path,sizeof(path),"%s/%s",directory,name)>=(int)sizeof(path))fail("PATH_LENGTH");
    f=fopen(path,mode);if(!f)fail(name);return f;
}
static void put_array(FILE*f,const double*a,unsigned n){
    unsigned j;fputc('[',f);for(j=0;j<n;j++){if(j)fputc(',',f);fprintf(f,"\"%a\"",a[j]);}fputc(']',f);
}
void cap_init(long izH0,long nz,long nzrt,double zH0,double T0,double nH0,double fHe,double ob,double om,double ok,double ode,double w0,double wa,double Y,double Neff){
    FILE*f;int i;directory=getenv("REC_H5_CAPTURE_DIR");if(!directory)fail("NO_DIRECTORY");origin=izH0;if(nzrt<CAP_N)fail("PREFIX_LONGER_THAN_NATIVE_ALLOCATION");
    nodes=open_file("COMMITTED.jsonl","w");calls=open_file("CALLS.jsonl","w");writes=open_file("WRITES.jsonl","w");
    recur=open_file("RECURRENCE.jsonl","w");seeds=open_file("INITIALIZATION.jsonl","w");qss=open_file("QSS_WRITES.jsonl","w");
    f=open_file("SELECTED_SLOTS.txt","r");while(fscanf(f,"%d",&i)==1){if(i<0||i>=CAP_N)fail("SELECTED_INDEX");selected[i]=1;}fclose(f);
    f=open_file("VARIABLE_SEMANTICS.json","w");fprintf(f,"{\"real\":\"native real departures xi-xi_equilibrium_with_1s; indices0=2s,1=2p\",\"virtual\":\"native virtual departures xv=x1s*Dfnu; not absolute populations\",\"photon_arrays\":\"dimensionless occupation departures\",\"call_temperatures\":\"actual dispatcher eV arguments\",\"coefficient_temperatures\":\"actual FULL eV values after native rescale\",\"nonnegativity_of_departures_required\":false}\n");fclose(f);
    f=open_file("PARAMETERS.json","w");
    fprintf(f,"{\"izH0\":%ld,\"nz\":%ld,\"nzrt\":%ld,\"zH0\":\"%a\",\"T0_K\":\"%a\",\"nH0_m3\":\"%a\",\"fHe\":\"%a\",\"obh2\":\"%a\",\"omh2\":\"%a\",\"okh2\":\"%a\",\"odeh2\":\"%a\",\"w0\":\"%a\",\"wa\":\"%a\",\"Y\":\"%a\",\"Nnueff\":\"%a\",\"h\":\"%a\",\"fsR\":1,\"meR\":1,\"retained_rows\":7489,\"dtype\":\"IEEE754_binary64\",\"byte_order\":\"native\",\"row_order\":\"channel_then_local_time\",\"little_endian\":%s}\n",izH0,nz,nzrt,zH0,T0,nH0,fHe,ob,om,ok,ode,w0,wa,Y,Neff,(double)DLNA,(*(unsigned char*)&(uint16_t){1})?"true":"false");
    fclose(f);
}
void cap_phase(const char *name,long n){phase=name;global_n=n;}
void cap_node(long n,double z,double xe,double tm,int partition,double xH1s,double xHeII,int neutral){
    long i=n-origin;if(i< -4||i>=CAP_N)return;
    fprintf(nodes,"{\"global\":%ld,\"local\":%ld,\"phase\":\"%s\",\"z\":\"%a\",\"xe\":\"%a\",\"Tm_K\":\"%a\",\"partition_observed\":%s,\"helium_neutral\":%s,\"xH1s\":",n,i,phase,z,xe,tm,partition?"true":"false",neutral?"true":"false");
    if(partition)fprintf(nodes,"\"%a\",\"xHII\":\"%a\",\"xHeII\":\"%a\"",xH1s,1.-xH1s,xHeII);
    else fprintf(nodes,"null,\"xHII\":null,\"xHeII\":%s",neutral?"\"0x0p+0\"":"null");
    fprintf(nodes,"}\n");
}
unsigned long cap_last_call(void){return last_id;}
long cap_global_in(void){return global_n;}
double cap_dispatch(const char *site,int model,double xe,double xHII,double nH,double H,double TM,double TR,HRATEEFF*rate,TWO_PHOTON_PARAMS*twog,double**out,double*ly[],double**avg,double zstart,unsigned iz,double z,double fs,double me){
    double result;unsigned long id=++count;int keep=(iz<CAP_N);
    if(count>200000)fail("GLOBAL_CALL_CAP");if(keep&&++detailed>40000)fail("DETAILED_CALL_CAP");active_id=id;
    result=rec_dxHIIdlna(model,xe,xHII,nH,H,TM,TR,rate,twog,out,ly,avg,zstart,iz,z,fs,me);
    if(keep)fprintf(calls,"{\"id\":%lu,\"global\":%ld,\"slot\":%u,\"phase\":\"%s\",\"site\":\"%s\",\"model\":%d,\"z\":\"%a\",\"xe\":\"%a\",\"xHII\":\"%a\",\"nH_cm3\":\"%a\",\"H_s_inv\":\"%a\",\"TM_eV\":\"%a\",\"TR_eV\":\"%a\",\"fsR\":\"%a\",\"meR\":\"%a\",\"dxHII_deta\":\"%a\"}\n",id,origin+(long)iz,iz,phase,site,model,z,xe,xHII,nH,H,TM,TR,fs,me,result);
    last_id=id;active_id=0;return result;
}
void cap_full_write(unsigned slot,double*xr,double*xv,double**out,double*ly[],double**avg,double*incoming,double*incoming_ly,double TM,double TR){
    unsigned b;if(slot>=CAP_N)return;if(!active_id)fail("WRITE_WITHOUT_CALL");last_writer[slot]=active_id;write_count++;
    fprintf(writes,"{\"id\":%lu,\"slot\":%u,\"coefficient_TM_eV\":\"%a\",\"coefficient_TR_eV\":\"%a\"}\n",active_id,slot,TM,TR);
    if(!selected[slot])return;
    fprintf(qss,"{\"id\":%lu,\"slot\":%u,\"real\":",active_id,slot);put_array(qss,xr,2);fprintf(qss,",\"virtual\":");put_array(qss,xv,NVIRT);
    fprintf(qss,",\"incoming_virtual\":");put_array(qss,incoming,NVIRT);fprintf(qss,",\"incoming_lyman\":");put_array(qss,incoming_ly,2);
    fprintf(qss,",\"outgoing_virtual\":[");for(b=0;b<NVIRT;b++){if(b)fputc(',',qss);fprintf(qss,"\"%a\"",out[b][slot]);}
    fprintf(qss,"],\"outgoing_lyman\":[");for(b=0;b<3;b++){if(b)fputc(',',qss);fprintf(qss,"\"%a\"",ly[b][slot]);}
    fprintf(qss,"],\"average_virtual\":[");for(b=0;b<NVIRT;b++){if(b)fputc(',',qss);fprintf(qss,"\"%a\"",avg[b][slot]);}fprintf(qss,"]}\n");
}
void cap_recur(const char*component,long n,double xin,double xout,double F,double p,double p2,double ap,double ap2,int sigma,int integrated,unsigned long id){
    long i=n-origin;if(i< -5||i>=CAP_N)return;
    fprintf(recur,"{\"component\":\"%s\",\"global_in\":%ld,\"local_in\":%ld,\"phase\":\"%s\",\"call_id\":%lu,\"sigma\":%d,\"integrated\":%s,\"xin\":\"%a\",\"xout\":\"%a\",\"current\":\"%a\",\"prev\":\"%a\",\"prev2\":\"%a\",\"after_prev\":\"%a\",\"after_prev2\":\"%a\",\"h\":\"%a\"}\n",component,n,i,phase,id,sigma,integrated?"true":"false",xin,xout,F,p,p2,ap,ap2,(double)DLNA);
}
void cap_seed(const char*component,long next,double p,double p2,double x1,double x2,double x3,double x4,double sub1,double sub2){
    fprintf(seeds,"{\"component\":\"%s\",\"next_global\":%ld,\"source_global_indices\":[%ld,%ld,%ld,%ld],\"prev\":\"%a\",\"prev2\":\"%a\",\"x_n_minus1\":\"%a\",\"x_n_minus2\":\"%a\",\"x_n_minus3\":\"%a\",\"x_n_minus4\":\"%a\",\"subtract_prev\":\"%a\",\"subtract_prev2\":\"%a\",\"h\":\"%a\"}\n",component,next,next-1,next-2,next-3,next-4,p,p2,x1,x2,x3,x4,sub1,sub2,(double)DLNA);
}
static void dump_rows(const char*name,double**a,unsigned n){FILE*f=open_file(name,"wb");unsigned b;for(b=0;b<n;b++)if(fwrite(a[b],sizeof(double),CAP_N,f)!=CAP_N)fail("RAW_WRITE");fclose(f);}
void cap_final(double**out,double*ly[],double**avg,double*energy){FILE*f;dump_rows("outgoing_virtual.f64",out,NVIRT);dump_rows("outgoing_lyman.f64",ly,3);dump_rows("average_virtual.f64",avg,NVIRT);f=open_file("energy_eV.f64","wb");if(fwrite(energy,sizeof(double),NVIRT,f)!=NVIRT)fail("ENERGY_WRITE");fclose(f);f=open_file("LAST_WRITERS.json","w");fprintf(f,"[");for(unsigned i=0;i<CAP_N;i++){if(i)fputc(',',f);fprintf(f,"%lu",last_writer[i]);}fprintf(f,"]\n");fclose(f);}
void cap_finish(void){FILE*f=open_file("CAPTURE_SUMMARY.json","w");fprintf(f,"{\"global_calls\":%lu,\"detailed_calls\":%lu,\"full_write_events\":%lu,\"retained_rows\":7489,\"complete_native_program\":true}\n",count,detailed,write_count);fclose(f);fclose(nodes);fclose(calls);fclose(writes);fclose(recur);fclose(seeds);fclose(qss);}
