# HD full 15-state source-locked CMB line transfer, weak inversion (2026-10-30)

## Scientific authority, source, assumptions

Exact input: David A. Neufeld (2026), *Excitation of Warm HD and H2 and Implications for the Interstellar Deuterium Abundance*, ApJ **1007**, 16, DOI 10.3847/1538-4357/ae851a; official original Zenodo **v2** record 21165907 (DOI 10.5281/zenodo.21165907). Four source .dat/.fits files are copied as immutable bytes and SHA256 validated before every model run, with per-file checksums in evidence/FULLLINE_SCIENCE_SUMMARY.json. Original Wan et al. (2019) HD-H2 de-excitation source rates for low J, extrapolated J>8 rates in Neufeld's files are distinguished from measured scattering data.

Uniform slab with source-owned 15-level collision and radiative generator, original level degeneracies g_J=2J+1, source A_ul and frequencies; H2 ortho/para fraction =0.75/0.25; Tgas exact source input values {100,400,1000,4000} K (no interpolation); H2 densities 10^2,10^4,10^6,10^8 cm^-3; CMB Tgamma(z)=2.72548(1+z) K, z={0,10,30,50,100}. Metric signature (-,+,+,+); SI h,c,kB retained. Mass for Doppler thermal broadening is source header 3.0 atomic mass units (approximation), with separately chosen microturbulent Doppler b={0,3} km/s. HD column N={10^14,10^16,10^18,10^20} cm^-2, no external continuum beyond CMB, dust, line overlap, chemistry, bulk velocity gradients, or instrument convolution. All reported surface brightness per solid angle is modelled and conditional, not a telescope flux measurement.

## Physical equations (derived, then numerically checked)

Stationary source-owned normalized populations p_i satisfy M p=0, sum_i p_i=1. For Tgamma, nbar_ul=(exp(h nu_ul/(kB Tgamma))-1)^-1. Collisional downward q_ul=nH2[(1-f_o) k_p,ul+f_o k_o,ul] and upward q_lu=q_ul(g_u/g_l)exp[-hc(Eu-El)/(kB Tgas)] using original source energy gaps. Radiative u->l rate A_ul(1+nbar), upward l->u A_ul (g_u/g_l)nbar.

Original positive-power and negative-power terms are preserved:

    P_net,ul = h nu_ul A_ul [p_u(1+nbar_ul) - (g_u/g_l)p_l nbar_ul]  [W/HD].

For an isothermal Doppler Gaussian (frequency profile normalized to 1):

    Delta_nu_D = nu_ul b/c, b^2=2 kB Tgas/m_HD + v_turb^2;
    phi_nu = exp[-((nu-nu_ul)/Delta_nu_D)^2] / (sqrt(pi) Delta_nu_D).

The line absorption coefficient integrated over a column N_HD in m^-2 is

    tau_nu = N_HD [c^2 A_ul/(8 pi nu_ul^2)] [(g_u/g_l)p_l-p_u] phi_nu.

Define D=(g_u/g_l)p_l-p_u. The source function (where D!=0) and excess emergent specific intensity are

    S_nu= [2 h nu_ul^3/c^2] p_u/D,
    Delta I_nu=(S_nu - B_nu(Tgamma)) [1-exp(-tau_nu)].

This is *exact formal transfer for fixed level populations* through a uniform slab. Those populations were solved in the optically thin external-CMB source equation, not self-consistently with trapped emitted photons; thus the physically supported interpretation is restricted by |tau0|<0.1. Rows outside that screened regime are explicitly flagged 'formal_only', not promoted. If D<0, tau<0: the same formal equation provides the unsaturated, weak-gain solution but NOT a saturated maser model.

In the optically thin limit, directly from the Einstein relations:

    Delta I_line(rest) = N_HD P_net,ul/(4 pi)  [W m^-2 sr^-1]

with N_HD in m^-2. The frequency-integrated finite-slab correction is a *purely formal* fixed-population ratio

    beta(tau0)= [1/sqrt(pi)] integral_(R) exp(-x^2) [1-exp(-tau0 exp(-x^2))]/[tau0 exp(-x^2)] dx.

Then Delta I_line,formal=Delta I_line,thin beta(tau0). A separate FLRW *conditional mapping* to observer-frame bolometric surface brightness multiplies by (1+z)^-4. It is not a cosmological history calculation or distance/beam flux.

## Genuine low-J inversion and two-state exclusion

The signed criterion D=3p0-p1 for J1->J0. Under the exact original source at Tgas=4000 K, nH2=1e4 cm^-3, z=0, both standard and alternative rate files produce D<0; at N_HD=1e20 cm^-2, tau0~-5.85e-4 (small gain) and no broad, intense maser claim. Density-window endpoints at z=0: standard {n_on=522.851385,n_off=13766.589} cm^-3, alternative {n_on=522.851385,n_off=13766.6082} cm^-3. The source-knot phase diagram over 9 exact temperatures, 5 redshifts, 2 alternative sources has 90 conditions and 14490 density samples (of these 28 source-temperature-redshift cases exhibit a bounded density inversion window).

For an isolated two-level positive-temperature thermal collision model, let down collision rate q>0, upward q(g1/g0)exp(-h nu/(kB Tgas)), and radiative bath occupation nbar>=0. Stationary p1/p0 divided by g1/g0 equals

    [A nbar + q exp(-h nu/(kB Tgas))]/[A(1+nbar)+q] < 1.

Proof: denominator minus numerator = A + q[1-exp(-h nu/(kB Tgas))] > 0. Therefore an isolated two-level positive-temperature HD J1->J0 model cannot be inverted. The original source-locked J<=2 truncated model is not inverted for the specific T=4000 K,nH2=1e4,z=0 test, but the J<=3 truncated model becomes inverted, as does full J<=14. This is a *controlled diagnostic* of multi-level pumping, not a proof of unique physical mechanism or novelty. Full-model f_ortho in {0,.25,.5,.75,1} retains inversion at that fixed test state.

## Numerical checks and limitations

- 160 source-stationary model states and 17920 line,column,velocity rows were computed, including signed absorption and weak-gain cases (no negative-population clipping).
- 17346 rows satisfy |tau0|<0.1. 574 do not, and are NOT self-consistent trapped-radiation predictions.
- Independent dense NumPy/scipy solve: 16 source states, max |delta p|=7.8825835e-15; adaptive quadrature for 9 tau values compared to 96-node Hermite, max |delta beta|=5.2530202e-13. Rounding effects on tiny populations are separate from physical negative opacity.
- Original CDMS2011 v2 35 Hz FAIL7/8 is unchanged. No replacement of source-owner lines/frequencies. Sung et al. joint calibration/line-center covariance and CDMS historical SPFIT full precision covariance remain unavailable. No sky measurement, observing likelihood, detection significance or claimed new strong no-go.

## Primary citations

Neufeld, D.A. (2026), ApJ 1007, 16, DOI 10.3847/1538-4357/ae851a; source v2 DOI 10.5281/zenodo.21165907.
Francis, L. et al. (2025), A&A 694, A174, DOI 10.1051/0004-6361/202451629 (existing JWST data, NOT a new input here).
Sung, K. et al. (2023), JQSRT 295, 108412, DOI 10.1016/j.jqsrt.2022.108412 (historical experimental line-shape data, NOT an input here).
