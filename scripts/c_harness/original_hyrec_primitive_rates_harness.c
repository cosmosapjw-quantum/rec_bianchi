/* Source-parity harness for hydrogen.c::interpolate_rates.
 * Usage: harness TR_eV_rescaled TM_over_TR fsR meR
 * Output order: Alpha[0:2], DAlpha[0:2], Beta[0:2], R2p2s.
 */
#include <stdio.h>
#include <stdlib.h>

#include "hydrogen.h"
#include "hyrectools.h"

int main(int argc, char **argv) {
    HRATEEFF rate_table;
    double Alpha[2], DAlpha[2], Beta[2], R2p2s;
    double TR, TM_TR, fsR, meR;

    if (argc != 5) {
        fprintf(stderr, "usage: %s TR TM_TR fsR meR\n", argv[0]);
        return 2;
    }
    TR = strtod(argv[1], NULL);
    TM_TR = strtod(argv[2], NULL);
    fsR = strtod(argv[3], NULL);
    meR = strtod(argv[4], NULL);

    rate_table.logTR_tab = create_1D_array(NTR);
    rate_table.TM_TR_tab = create_1D_array(NTM);
    rate_table.logAlpha_tab[0] = create_2D_array(NTM, NTR);
    rate_table.logAlpha_tab[1] = create_2D_array(NTM, NTR);
    rate_table.logR2p2s_tab = create_1D_array(NTR);
    read_rates(&rate_table);
    interpolate_rates(Alpha, DAlpha, Beta, &R2p2s, TR, TM_TR, &rate_table, fsR, meR);

    printf("%.17e %.17e %.17e %.17e %.17e %.17e %.17e\n",
           Alpha[0], Alpha[1], DAlpha[0], DAlpha[1],
           Beta[0], Beta[1], R2p2s);

    free(rate_table.logTR_tab);
    free(rate_table.TM_TR_tab);
    free_2D_array(rate_table.logAlpha_tab[0], NTM);
    free_2D_array(rate_table.logAlpha_tab[1], NTM);
    free(rate_table.logR2p2s_tab);
    return 0;
}
