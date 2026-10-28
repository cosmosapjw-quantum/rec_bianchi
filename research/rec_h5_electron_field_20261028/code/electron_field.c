#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "hyrectools.h"
#include "hydrogen.h"
#include "electron_field.h"

struct EFContext { HRATEEFF rates; TWO_PHOTON_PARAMS twog; };
_Thread_local EFDiagnostics *ef_active_diagnostics = NULL;
static const char *SOURCE_SHA = "94b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c";

void ef_observe(int kind, int index, double value) {
    EFDiagnostics *d = ef_active_diagnostics;
    if (!d) return;
    int k = d->events++;
    if (k < EF_EVENT_CAP) { d->values[k] = value; d->kinds[k] = kind; d->indices[k] = index; }
    else d->overflow++;
    if (!isfinite(value)) d->nonfinite++;
    if (value == 0.) d->zero++;
    if (isfinite(value) && fabs(value) < d->min_abs) d->min_abs = fabs(value);
    if (kind == 4) d->schur = value;
}

EFContext *ef_context_new(void) {
    EFContext *c = calloc(1, sizeof(*c));
    if (!c) return NULL;
    c->rates.logTR_tab = create_1D_array(NTR);
    c->rates.TM_TR_tab = create_1D_array(NTM);
    c->rates.logR2p2s_tab = create_1D_array(NTR);
    for (int l=0;l<2;l++) c->rates.logAlpha_tab[l] = create_2D_array(NTM,NTR);
    read_rates(&c->rates);
    read_twog_params(&c->twog);
    return c;
}
void ef_context_free(EFContext *c) {
    if (!c) return;
    free(c->rates.logTR_tab); free(c->rates.TM_TR_tab); free(c->rates.logR2p2s_tab);
    for (int l=0;l<2;l++) free_2D_array(c->rates.logAlpha_tab[l],NTM);
    free(c);
}
size_t ef_tables_count(void) { return 2*NTR*NTM + 2*NTR + NTM + 2 + 5*NVIRT; }
int ef_tables_copy(const EFContext *c, double *out, size_t count) {
    if (!c || !out || count != ef_tables_count()) return 1;
    size_t n=0;
    for (int l=0;l<2;l++) for (int j=0;j<NTM;j++) for (int i=0;i<NTR;i++) out[n++]=c->rates.logAlpha_tab[l][j][i];
    for (int i=0;i<NTR;i++) out[n++]=c->rates.logTR_tab[i];
    for (int i=0;i<NTM;i++) out[n++]=c->rates.TM_TR_tab[i];
    for (int i=0;i<NTR;i++) out[n++]=c->rates.logR2p2s_tab[i];
    out[n++]=c->rates.DlogTR; out[n++]=c->rates.DTM_TR;
    const double *arrays[5]={c->twog.Eb_tab,c->twog.A1s_tab,c->twog.A2s_tab,c->twog.A3s3d_tab,c->twog.A4s4d_tab};
    for (int j=0;j<5;j++) for (int i=0;i<NVIRT;i++) out[n++]=arrays[j][i];
    return n==count ? 0 : 2;
}

int ef_evaluate(EFContext *c, const double *P, size_t P_count,
                const double *incoming, size_t incoming_count,
                const double *lyman, size_t lyman_count, int model,
                const char *phase, int helium_neutral, const char *units,
                const char *temperature_origin, const char *source_sha256,
                EFOutput *o) {
    if (!o) return 1;
    memset(o,0,sizeof(*o));
    if (!c || !P || !incoming || !lyman || P_count!=8 || incoming_count!=NVIRT || lyman_count!=2) return o->status=1;
    if (model!=FULL || !phase || strcmp(phase,"H_STEADY") || helium_neutral!=1) return o->status=2;
    if (!units || strcmp(units,"native_cm3_s_eV_eta") || !temperature_origin || strcmp(temperature_origin,"dispatcher")) return o->status=3;
    if (!source_sha256 || strcmp(source_sha256,SOURCE_SHA)) return o->status=4;
    for (int i=0;i<8;i++) if (!isfinite(P[i])) return o->status=5;
    for (int i=0;i<NVIRT;i++) if (!isfinite(incoming[i])) return o->status=5;
    for (int i=0;i<2;i++) if (!isfinite(lyman[i])) return o->status=5;
    double xe=P[0],xHII=P[1],nH=P[2],H=P[3],TM=P[4],TR=P[5],fsR=P[6],meR=P[7];
    if (H<=0. || nH<=0. || TM<=0. || TR<=0. || xHII<0. || xHII>=1. || xe<0. || xe!=xHII || fsR!=1. || meR!=1.) return o->status=6;
    /* Exact original dispatcher-to-FULL temperature prelude, once. */
    double ratio=TM/TR;
    rescale_T(&TR,fsR,meR);
    TM=ratio*TR;
    if (!isfinite(TM) || !isfinite(TR) || TR<TR_MIN || TR>TR_MAX || TM/TR<TM_TR_MIN || TM/TR>TM_TR_MAX) return o->status=6;
    double local_incoming[NVIRT],local_lyman[2];
    memcpy(local_incoming,incoming,sizeof(local_incoming)); memcpy(local_lyman,lyman,sizeof(local_lyman));
    double *Trv[2],*Tvr[2],*Tvv[3];
    for (int i=0;i<2;i++) Trv[i]=create_1D_array(NVIRT);
    for (int i=0;i<2;i++) Tvr[i]=create_1D_array(NVIRT);
    for (int i=0;i<3;i++) Tvv[i]=create_1D_array(NVIRT);
    o->kernel_calls=1;
    populateTS_2photon(o->A,Trv,Tvr,Tvv,o->sr,o->sv,o->Dtau,xe,xHII,TM,TR,nH,H,&c->rates,&c->twog,local_incoming,local_lyman,o->Alpha,o->DAlpha,o->Beta,fsR,meR);
    EFDiagnostics *previous=ef_active_diagnostics;
    ef_active_diagnostics=&o->diagnostics;
    o->diagnostics.min_abs=INFINITY;
    for (int b=0;b<NVIRT;b++) if (b<NSUBLYA-NDIFF/2 || b>=NSUBLYA+NDIFF/2) ef_observe(3,b,Tvv[0][b]);
    solve_real_virt(o->xr,o->xv,o->A,Trv,Tvr,Tvv,o->sr,o->sv);
    ef_active_diagnostics=previous;
    o->x1=1.-xHII;
    o->s=SAHA_FACT(fsR,meR)*TR*sqrt(TR)*exp(-EI/TR)/nH;
    o->Delta=xe*xHII-o->s*o->x1;
    o->FH=-(nH*(o->s*o->x1*o->DAlpha[0]+o->Alpha[0]*o->Delta)-o->xr[0]*o->Beta[0]
            +nH*(o->s*o->x1*o->DAlpha[1]+o->Alpha[1]*o->Delta)-o->xr[1]*o->Beta[1])/H;
    o->coefficient_TM_eV=TM; o->coefficient_TR_eV=TR; o->H=H; o->nH=nH;
    for (int i=0;i<2;i++) { memcpy(o->B[i],Trv[i],sizeof(o->B[i])); memcpy(o->C[i],Tvr[i],sizeof(o->C[i])); }
    for (int i=0;i<3;i++) memcpy(o->V[i],Tvv[i],sizeof(o->V[i]));
    int bad=!isfinite(o->FH);
    for (int i=0;i<2;i++) if (!isfinite(o->xr[i])) bad=1;
    for (int i=0;i<NVIRT;i++) if (!isfinite(o->xv[i])) bad=1;
    if (bad || o->diagnostics.events!=EF_EVENT_CAP || o->diagnostics.zero || o->diagnostics.nonfinite || o->diagnostics.overflow) o->status=7;
    for (int i=0;i<2;i++) free(Trv[i]);
    for (int i=0;i<2;i++) free(Tvr[i]);
    for (int i=0;i<3;i++) free(Tvv[i]);
    return o->status;
}
