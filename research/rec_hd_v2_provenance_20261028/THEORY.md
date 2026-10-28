# REC-HD: original-source cross-energy equilibrium diagnostic

Status: derived and executed on **one immutable LAMDA 2021-06-07 HD datafile**. Neither a changed HD model nor a repaired 35 Hz criterion.

## Contract and derivation

HD = neutral (¹H,²H), original printed nine level IDs 1..9, J=0..8 and eight J->J-1 radiative rows. Vibrational label is not qualified; no other isotopologue is present. Level term energies w_j are in cm^-1, printed photon frequencies nu_j in GHz. At each printed temperature T=50,100,200 K, collisional LTE occupations use exact printed E_j=h c 100 w_j, while radiative emission/absorption coefficients use h nu_j and Einstein A/B of the printed line.

Take levels u,l, degeneracies g and one normalized line profile phi(nu), with n_u/n_l=(g_u/g_l) exp[-(E_u-E_l)/(k_B T)]. The Einstein relations are g_l B_lu=g_u B_ul and A_ul/B_ul=2h nu^3/c^2 (for profile-averaged mean intensity convention). Hence

j_nu=(h nu/4pi)n_u A_ul phi, alpha_nu=(h nu/4pi)(n_l B_lu-n_u B_ul)phi,

j_nu/alpha_nu=(2h nu^3/c^2)/(exp[(E_u-E_l)/(k_B T)]-1).

Compared with the Planck B_nu(T)=(2h nu^3/c^2)/(exp[h nu/(k_B T)]-1), the *source-column cross-energy ratio* is

R_j(T) = (j_nu/alpha_nu)/B_nu(T) = expm1(h nu_j/k_B T)/expm1(h c 100 (w_j-w_(j-1))/k_B T).

K_j(T)=R_j(T)-1 is dimensionless. Define signed delta_nu,j=c 100 (w_j-w_(j-1)) - 10^9 nu_j, in Hz, c=299792458 m/s. If delta_nu>0 then K<0; delta_nu<0 then K>0 for T>0. Exact equality K=0 iff the two printed energies coincide (assuming T finite and positive). The 35 Hz criterion tests **printed representation consistency**, not observational line accuracy. Reusing the prior original seven failures is required.

The eight-line graph is a tree. A post hoc ladder E_j=E_0+h sum_{k=1}^j nu_k removes all discrepancies algebraically, but also replaces collisional energies; it cannot identify which printed column is the physical source of truth. This is a constructive *source-choice ambiguity*, not a strong novel no-go theorem or evidence of incorrect experiments.

## Primary-source status and row-specific documentary leads

CDMS original Version 2 / Dec 2011 HTML documentation says lower J''=0 frequency based on Drouin et al (2011), J''=1..3 transitions from Ulivi et al (1991), lower J''=6 transition from Essenwanger and Gush (1984), plus infrared lines Rich et al (1982) in a fit with P(3) omitted. LAMDA HD page and retained input attribute spectroscopy to that CDMS v2. These are **fit-input citations**, not a byte-matched identification of LAMDA's eight printed frequencies as those five measurements. Rows with lower J''=4,5,7 are not individually named as measured in that CDMS HTML documentation. All eight require archived version2 `.cat`, `.egy`, `.par` and LAMDA conversion recipe to bind numeric versions or uncertainties.

CDMS's August2026 Version3 revises the December2011 fit and is a different source identity. It must not substitute for v2 in this frozen node. The LAMDA page's claim of v=1 near 3100 cm^-1 is not consistent with CDMS v2's v=1 origin near 3632 cm^-1; the file itself has only J labels. Do not set an unverified v label merely to smooth this discrepancy.

## Scope

- Derived K at exactly the 24 printed source temperature/line combinations. No thermal-ODE trajectory, density, emissivity profile or population IVP solved.
- No source replacement, line clipping, photoabsorption transfer, missing rates filled, 2026 CDMS v3 import, H-Li registry activation or new species.
- Physical source uncertainty, collision physics accuracy, spectral line fit and actual on-sky radiative error remain unresolved.
