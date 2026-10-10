/* Endpoint-only driver based on original HyRec/hyrec.c. All evolution and
 * interpolation routines are compiled from the byte-pinned original archive. */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "hyrectools.h"
#include "helium.h"
#include "hydrogen.h"
#include "history.h"
#include "hyrec_params.h"

int main(int argc, char **argv) {
    REC_COSMOPARAMS p;
    HRATEEFF rates;
    TWO_PHOTON_PARAMS two;
    double *xe, *Tm, **Df, *lines[3];
    const double epochs[] = {20., 15.9};
    const double x0 = -log(1. + ZSTART);
    FILE *history;
    int epoch;
    long i, center;
    double endpoint_xe, endpoint_Tm, nH, Tgamma;

    rates.logTR_tab = create_1D_array(NTR);
    rates.TM_TR_tab = create_1D_array(NTM);
    rates.logAlpha_tab[0] = create_2D_array(NTM, NTR);
    rates.logAlpha_tab[1] = create_2D_array(NTM, NTR);
    rates.logR2p2s_tab = create_1D_array(NTR);
    read_rates(&rates);
    read_twog_params(&two);
    rec_get_cosmoparam(stdin, stderr, &p);
    xe = create_1D_array(p.nz);
    Tm = create_1D_array(p.nz);
    Df = create_2D_array(NVIRT, p.nzrt);
    for (i = 0; i < 3; ++i) lines[i] = create_1D_array(p.nzrt);
    rec_build_history(&p, &rates, &two, xe, Tm, Df, lines);

    for (i = 0; i < p.nz; ++i) {
        if (!isfinite(xe[i]) || !isfinite(Tm[i]) || xe[i] < 0. ||
            xe[i] > 1. + 2. * p.fHe || Tm[i] <= 0.) {
            fprintf(stderr, "NONPHYSICAL_HISTORY_NODE index=%ld xe=%.17g Tm=%.17g\n", i, xe[i], Tm[i]);
            return 2;
        }
    }
    if (argc != 2 || !(history = fopen(argv[1], "w"))) return 4;
    fprintf(history, "ln_a,xe_per_H,Tm_K\n");
    for (i = 0; i < p.nz; ++i)
        fprintf(history, "%.17g,%.17g,%.17g\n", x0+i*DLNA, xe[i], Tm[i]);
    if (fclose(history)) return 5;
    printf("[\n");
    for (epoch = 0; epoch < 2; ++epoch) {
    const double z = epochs[epoch], x = -log1p(z);
    if (epoch) printf(",\n");
    endpoint_xe = rec_interp1d(x0, DLNA, xe, p.nz, x);
    endpoint_Tm = rec_interp1d(x0, DLNA, Tm, p.nz, x);
    if (!isfinite(endpoint_xe) || endpoint_xe < 0. || endpoint_xe > 1. ||
        !isfinite(endpoint_Tm) || endpoint_Tm <= 0.) return 3;
    center = (long) floor((x - x0) / DLNA);
    if (center < 1) center = 1;
    if (center > p.nz - 3) center = p.nz - 3;
    nH = p.nH0 * pow(1. + z, 3.);
    Tgamma = p.T0 * (1. + z);

    printf("{\n\"schema\":\"P02B-FLRW-ENDPOINT-v1\",\n");
    printf("\"cosmology\":{\"T0_K\":%.17g,\"obh2\":%.17g,\"omh2\":%.17g,\"okh2\":%.17g,\"odeh2\":%.17g,\"w0\":%.17g,\"wa\":%.17g,\"Y\":%.17g,\"Nnueff\":%.17g,\"fsR\":%.17g,\"meR\":%.17g},\n",
        p.T0,p.obh2,p.omh2,p.okh2,p.odeh2,p.w0,p.wa,p.Y,p.Nnueff,p.fsR,p.meR);
    printf("\"grid\":{\"DLNA\":%.17g,\"ln_a_start\":%.17g,\"nz\":%ld,\"nzrt\":%ld,\"interpolation_center\":%ld},\n",(double)DLNA,x0,p.nz,p.nzrt,center);
    printf("\"endpoint\":{\"z\":%.17g,\"a\":%.17g,\"ln_a\":%.17g,\"Tgamma_K\":%.17g,\"Tm_K\":%.17g,\"nH_m3\":%.17g,\"nHe_m3\":%.17g,\"fHe\":%.17g,\"H_s1\":%.17g,\"xe_per_H\":%.17g,\"ne_m3\":%.17g,\"xHII\":%.17g,\"xHI\":%.17g,\"xHeI\":1,\"xHeII\":0,\"xHeIII\":0},\n",
        z,1./(1.+z),x,Tgamma,endpoint_Tm,nH,p.fHe*nH,p.fHe,
        rec_HubbleConstant(&p,z),endpoint_xe,endpoint_xe*nH,endpoint_xe,1.-endpoint_xe);
    printf("\"helium_mapping\":\"neutral-after-original-HyRec-cutoff\",\n");
    printf("\"native_history_domain_check\":\"PASS\",\n\"support\":[");
    for (i = center - 1; i <= center + 2; ++i) {
        printf("%s{\"index\":%ld,\"ln_a\":%.17g,\"z\":%.17g,\"xe_per_H\":%.17g,\"Tm_K\":%.17g}",
            i == center - 1 ? "" : ",",i,x0+i*DLNA,exp(-(x0+i*DLNA))-1.,xe[i],Tm[i]);
    }
    printf("]\n}\n");

    }
    printf("]\n");

    free(rates.logTR_tab); free(rates.TM_TR_tab);
    free_2D_array(rates.logAlpha_tab[0],NTM);
    free_2D_array(rates.logAlpha_tab[1],NTM);
    free(rates.logR2p2s_tab); free(xe); free(Tm);
    free_2D_array(Df,NVIRT);
    for (i = 0; i < 3; ++i) free(lines[i]);
    return 0;
}
