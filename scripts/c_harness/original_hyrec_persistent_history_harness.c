/* Original October-2012 HyRec H-only FULL temporal oracle.
 * The upstream C hydrogen.c / hyrectools.c remain byte-unchanged.
 * This shim calls the actual native FULL RHS while passing persistent,
 * row-major [NVIRT,capacity], [3,capacity] accepted photon histories.
 * Only indices < iz are initialized; original routine writes exactly iz.
 * No repeated quadratic copying, no future-history input, no Python RHS.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "hydrogen.h"
#include "hyrectools.h"

extern double rec_HMLA_2photon_dxHIIdlna(
    double xe, double xHII, double nH, double H, double TM, double TR,
    HRATEEFF *rate_table, TWO_PHOTON_PARAMS *twog,
    double **Dfminus_hist, double *Dfminus_Ly_hist[], double **Dfnu_hist,
    double zstart, unsigned iz, double z, double fsR, double meR);

static HRATEEFF rates;
static TWO_PHOTON_PARAMS two_photon;
static int is_initialized = 0;

static void initialize_original(void) {
    if (is_initialized) return;
    rates.logTR_tab = create_1D_array(NTR);
    rates.TM_TR_tab = create_1D_array(NTM);
    rates.logAlpha_tab[0] = create_2D_array(NTM,NTR);
    rates.logAlpha_tab[1] = create_2D_array(NTM,NTR);
    rates.logR2p2s_tab = create_1D_array(NTR);
    read_rates(&rates);
    read_twog_params(&two_photon);
    is_initialized = 1;
}

/* All dimensional inputs are identical to the unmodified original C:
 * nH [cm^-3], H [s^-1], Tm/Tr [eV], redshifts dimensionless, iz native step.
 * Caller is responsible for ownership and lifetime of (N+1) long rows.
 * This function is not an independent integrator and owns no ODE update.
 */
__attribute__((visibility("default")))
double rec_r3e_original_native_rhs_persistent(
    double xe, double xHII, double nH, double H,
    double Tm_eV, double Tr_eV, double zstart, unsigned iz, double z,
    double **accepted_virtual, double **accepted_lyman,
    double **average_virtual)
{
    if (!isfinite(xe) || !isfinite(xHII) || !isfinite(nH) ||
        !isfinite(H) || !isfinite(Tm_eV) || !isfinite(Tr_eV) ||
        !isfinite(zstart) || !isfinite(z) ||
        nH<=0. || H<=0. || Tm_eV<=0. || Tr_eV<=0.) {
        fprintf(stderr,"invalid R3e thermodynamic inputs\n");
        abort();
    }
    initialize_original();
    return rec_HMLA_2photon_dxHIIdlna(
        xe,xHII,nH,H,Tm_eV,Tr_eV,
        &rates,&two_photon,
        accepted_virtual,accepted_lyman,average_virtual,
        zstart,iz,z,1.,1.);
}
