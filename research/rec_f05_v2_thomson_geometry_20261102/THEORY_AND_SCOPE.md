# REC source-matched F05 Thomson geometry branch | 2026-11-02

Original REC parent #196 HEAD 832551b69801eea008daf2c8cf19881c28649075.
Original owner REI #365 HEAD fab9429140038974a98f3ad3212036b0227e600e.
V2 owner conditional source REI #366 HEAD a09ea7b999c90a692de07c74352f835707e65838.
Original F05 TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b.
Original F05 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.
Original accepted tick160 state numerical SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01.
Original V2 NONAUTHORITATIVE tick161 NPZ SHA256 c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823.

## R1–R4 scientific target

REC #196 already performed 184,320 original source event records.
REI #366 already performed 46,080 candidate tick161 H/He OTS source records,
and #367 already performed the four accepted time-point RHS.
Repeating those source-only atlases adds no science. This REC unit uniquely
binds the original collision coefficient to a physically declared geometry:
original F05 frozen-volume source versus an optional expanding matter-cell
continuation. Direct source data, not an invented photon map, are used.

The exact original F05 forcing_bounds operator was read and evaluated at
source ticks 0,64,128,160,161: z is identically 5.95 within binary64
interval bounds, the original proper V_j is frozen, and a positive source
Hubble rate near 2.253429258545391e-17 s^-1 enters thermal cooling.
This is NOT automatically an original-code physics error. Original
model splitting may intentionally keep the source geometry frozen.

## R5 microscopic collision and expansion derivation

Metric signature (-,+,+,+), cgs constants c=29979245800 cm/s,
sigma_T=6.6524587051e-25 cm^2, Mpc=3.085677581491367e24 cm.
For exact source H/He numbers N_e = N_HII+N_HeII+2N_HeIII, define
the proper rest-frame Thomson rate:

    Gamma_T,j = sigma_T*c*N_e,j/V_j [s^-1].

Native ORIGINAL source frozen forcing:

    V_j^F = W_j (Mpc in cm)^3 / (1+5.95)^3,
    Gamma_160^F = sigma_T*c*N_e,160/V_j^F,
    Gamma_161^F = sigma_T*c*N_e,161(V2)/V_j^F.

For a separate explicitly conditional FLRW-type comoving-cell continuation,
theta=3 H on one source microtick dt, with H from original F05 source:

    V_161^E = V_160^F exp(3H dt),
    Gamma_161^E = Gamma_161^F exp(-3H dt).

Exact finite-change decomposition in the two distinct interpretations:

    delta_Gamma_chem = Gamma_161^F-Gamma_160^F,
    delta_Gamma_geom = Gamma_161^E-Gamma_161^F,
    delta_Gamma_total= delta_Gamma_chem+delta_Gamma_geom.

The differential comoving interpretation is

    d ln Gamma_T/dt = (dot N_e)/N_e - theta.

In conformal time the collision coefficient for a homogeneous frame
is a*n_e*sigma_T*c; the Bianchi photon null-ray clock, direction,
electron peculiar velocity and actual Sachs polarization coupling
are NOT supplied by this static source comparison.
Do not claim any line-of-sight tau, visibility, or observed CMB.

For source H interval [Hlo,Hhi] and positive dt, the optional geometry
factor lies in [exp(-3Hhi dt), exp(-3Hlo dt)]. The original source
population intervals from accepted tick160 and V2 shadow tick161
provide intervals of Ne, and the source proper volume is positive.
Use positive-product endpoints and signed interval differences. For
the geometry difference Gamma_F*(f-1), retain its correlated negative
sign; do not inflate it with independent endpoint subtraction.

Output per native cell: source proper V, two source electron boxes,
Gamma_160, Gamma_161_frozen, Gamma_161_expanded and three distinct
finite-change boxes. Report strict sign categories under each model,
with the same one source realization counted once across three REI lanes.

## R6 hostile review and condition boundaries

A frozen source z=5.95 intentionally yields dot V=0; an expanding
microtick is therefore a DIFFERENT explicit physical model, not a patch
to the official original 26-event worker. The comparison asks whether
a photon collision consumer may use a frozen coefficient without
specifying the geometry and corresponding baryon rest frame.

The V2 tick161 is conditional and NONAUTHORITATIVE; original V1
tick161 FAIL remains preserved. A V2 common-parent discrete defect
pass is not a rigorous continuum ODE local/global error certificate.
Require candidate parent arrays and accepted source tick160 arrays
to match exactly in all 5 species and temperature, as established
by source actual equality in REC parent. Original three lanes are
not independent universes.

Native original source source time, H and proper V are locked by
exact original kernel/TAR hashes and original head. The expansion
factor is an assumption only; any Bianchi generalization must use
theta=div(u) from the SAME geometry and proper clock, with tilt
factors resolved separately. Non-outward-rounded binary64 results
are numerical enclosures under source intervals, not MPFR proofs.

## R7–R10 and coding path

Generate one 46,080-row physical source-conditioned collision response,
with independent full-row source-free check, tamper-negative tests,
source-native H and volume evidence, and a single clean draft/backup.
The physical finding is the relative importance of electron chemistry
versus expanding-volume dilution and any *definite* cell sign reversals.
Stop subsequent source-only proxy atlases. Next actual canonical path is
the separately active REI owner V2 worker official tick161 accept/reject,
then source-clock matched Bianchi null rays.

At every phase: REI canonical 28/88 (+0), working 33/88 (+0),
Physical Fast 4/7 (+0), REC H5 physical 0/313 (+0).
PRODUCTION HOLD; NO_MERGE; NO_FORCE_PUSH; NO_OWNER_SWAP;
NO_TOLERANCE_CHANGE; NO_AUTO_NEXT; NATIVE_SUBAGENT NOT_RUN.
Scientific context: Ma & Bertschinger ApJ 455:7 (1995) Thomson
Boltzmann hierarchy, and original Pawlik & Schaye MNRAS (2011)
multifrequency coupled radiative transfer. Literature is not the
authority for this exact source snapshot.
