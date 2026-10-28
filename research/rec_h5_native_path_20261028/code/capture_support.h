#ifndef REC_H5_CAPTURE_SUPPORT_H
#define REC_H5_CAPTURE_SUPPORT_H
/* Included after native hydrogen/history types. No physics declarations changed. */
void cap_init(long izH0,long nz,long nzrt,double zH0,double T0,double nH0,double fHe,double ob,double om,double ok,double ode,double w0,double wa,double Y,double Neff);
void cap_phase(const char*,long);
void cap_node(long,double,double,double,int,double,double,int);
unsigned long cap_last_call(void);
long cap_global_in(void);
double cap_dispatch(const char*,int,double,double,double,double,double,double,HRATEEFF*,TWO_PHOTON_PARAMS*,double**,double*[],double**,double,unsigned,double,double,double);
void cap_full_write(unsigned,double*,double*,double**,double*[],double**,double*,double*,double,double);
void cap_recur(const char*,long,double,double,double,double,double,double,double,int,int,unsigned long);
void cap_seed(const char*,long,double,double,double,double,double,double,double,double);
void cap_final(double**,double*[],double**,double*);
void cap_finish(void);
#endif
