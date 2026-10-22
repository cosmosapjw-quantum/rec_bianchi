/* SI blackbody Compton energy exchange for a nonrelativistic Maxwellian gas.
 * kB,c,h exact SI; me and sigmaT use CODATA2022. No ODE integration. */
#include <math.h>
#include <stddef.h>

static const double kb = 1.380649e-23;
static const double c = 299792458.;
static const double h = 6.62607015e-34;
static const double me = 9.1093837139e-31;
static const double sigma_t = 6.6524587051e-29;

static double radiation_constant(void) {
    const double pi = acos(-1.);
    return 8.*pow(pi,5)*pow(kb,4)/(15.*pow(h,3)*pow(c,3));
}

int compton_terms(size_t n, const double *t, const double *tg,
                  const double *ne, const double *nb, const double *eta,
                  double *q, double *gamma) {
    const double common = sigma_t * radiation_constant()/(me*c);
    for (size_t i=0; i<n; ++i) {
        if (!isfinite(t[i]) || !isfinite(tg[i]) || !isfinite(ne[i]) ||
            !isfinite(nb[i]) || !isfinite(eta[i]) || t[i]<=0. ||
            tg[i]<=0. || ne[i]<0. || nb[i]<=0. || eta[i]<=0.) return 1;
        const double coupling = common*ne[i]*pow(tg[i],4);
        q[i] = 4.*kb*coupling*(tg[i]-t[i]);
        gamma[i] = (8./3.)*coupling/(nb[i]*eta[i]);
        if (!isfinite(q[i]) || !isfinite(gamma[i])) return 2;
    }
    return 0;
}

double compton_frozen_step(double t, double tg, double gamma, double dt) {
    if (!isfinite(t) || !isfinite(tg) || !isfinite(gamma) || !isfinite(dt) ||
        t<=0. || tg<=0. || gamma<0. || dt<0.) return NAN;
    return t + (t-tg)*expm1(-gamma*dt);
}
