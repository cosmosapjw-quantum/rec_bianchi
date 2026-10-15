/* Original HyRec October 2012 EMLA2s2p rate RHS source parity harness.
 * This C file is OUR harness only. Compiled with original unmodified
 * hydrogen.c and hyrectools.c from the archived 2012 source.
 *
 * argv: xe xHII nH_cm^-3 H_s^-1 Tm_eV Tr_eV fsR meR
 * prints d(x_HII)/dln a, original C quasi-steady EMLA2s2p,
 * NOT original FULL radiation-transfer dynamics.
 */
#include <stdio.h>
#include <stdlib.h>
#include "hydrogen.h"
#include "hyrectools.h"

/* The archived 2012 header uses rec_HMLA_dxedlna while hydrogen.c
 * exports rec_HMLA_dxHIIdlna; declare the actual source symbol.
 */
extern double rec_HMLA_dxHIIdlna(double xe, double xHII, double nH,
    double H, double TM, double TR, HRATEEFF *rates, double fsR, double meR);

int main(int argc,char **argv) {
    if(argc!=9) {
        fprintf(stderr,"expected xe xHII nH H TM TR fsR meR\n");
        return 2;
    }
    const double xe=strtod(argv[1],NULL);
    const double xHII=strtod(argv[2],NULL);
    const double nH=strtod(argv[3],NULL);
    const double H=strtod(argv[4],NULL);
    const double Tm=strtod(argv[5],NULL);
    const double Tr=strtod(argv[6],NULL);
    const double fsR=strtod(argv[7],NULL);
    const double meR=strtod(argv[8],NULL);
    HRATEEFF rate_table;
    rate_table.logTR_tab=create_1D_array(NTR);
    rate_table.TM_TR_tab=create_1D_array(NTM);
    rate_table.logAlpha_tab[0]=create_2D_array(NTM,NTR);
    rate_table.logAlpha_tab[1]=create_2D_array(NTM,NTR);
    rate_table.logR2p2s_tab=create_1D_array(NTR);
    read_rates(&rate_table);
    const double rhs=rec_HMLA_dxHIIdlna(
        xe,xHII,nH,H,Tm,Tr,&rate_table,fsR,meR
    );
    printf("%.17e\n",rhs);
    free(rate_table.logTR_tab);
    free(rate_table.TM_TR_tab);
    free_2D_array(rate_table.logAlpha_tab[0],NTM);
    free_2D_array(rate_table.logAlpha_tab[1],NTM);
    free(rate_table.logR2p2s_tab);
    return 0;
}
