/* Independent, unmodified original HyRec Oct2012 C operator harness.
 * Build together with archived hydrogen.c and hyrectools.c.
 * Export ONLY this adapter, and drop all unused original functions using
 * -ffunction-sections -fvisibility=hidden -Wl,--gc-sections.
 * Input history is contiguous [NVIRT, iz] and [3, iz], time slowest.
 */
#include "hydrogen.h"

__attribute__((visibility("default")))
void rec_r3_native_fplus(
    const double *energies, const double *virtual_hist,
    const double *lyman_hist, unsigned iz, double z_start,
    double z_face, double *virtual_out, double *lyman_out)
{
    double *virt_rows[NVIRT];
    double *ly_rows[3];
    unsigned b;
    for (b = 0; b < NVIRT; ++b)
        virt_rows[b] = (double *)(virtual_hist + b*iz);
    for (b = 0; b < 3; ++b)
        ly_rows[b] = (double *)(lyman_hist + b*iz);

    fplus_from_fminus(virtual_out, lyman_out, virt_rows, ly_rows,
                      0.0, z_start, iz, z_face, (double*)energies);
}
