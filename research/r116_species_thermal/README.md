# R116-REC-SPECIES-THERMAL-01

Baseline REC 6ad757d232a9833e984d18657d169766b27e33a4; theory HTT R115
188ca33d0813082ce23c6ce7a6d9419ef942c540. Bounded C1-C10 implementation.
All fractions per H nucleus, SI rates per proper second, eta normal e-fold.
New species_thermal.rs retains x_HI, x_HeII, x_HeIII, W=chi Tm,
chi=1+fHe+xe. H TLA uses nH alpha(Tm) xp xe, finite Sobolev escape including
xHI=0. Native HeI rate matches archived 2012 helium.c, fsR=meR=1, and uses
the current neutral H opacity, total electrons and neutral He abundance.
NativeHeI is independent-direction averaging of original scalar rate
at Tr(e), H f(e); a conditional approximate closure, NOT exact polarized
anisotropic helium radiation transfer. Tm and Tr may differ in H;
the helium source retains original thermal excited-state assumption.
Native numerical domain 3000..20000 K and tau>=1; not a source-calibrated
accuracy envelope. NeutralHelium requires zero helium ions; never clips.
Supplied uses caller-provided HeI/HeII forward/back rates, including actual
HeIII evolution; no internally qualified anisotropic HeIII rates.
Original HeIII reference is Saha, not kinetic. Native mode does not cross
HeIII/H-only ownership boundaries. No fictitious post-transition reset.

Thermal energy per H = 3/2 kB W; W'=-2/3 Theta/(gamma H) W
+Gamma0 xe(T_C-Tm)/(gamma H)+2 q_ext/(3 kB gamma H).
Gamma0=8 sigma_T U/(3 m_e c), U=a_rad weighted T^4.
Angle-averaged Planck-mixture Compton closure, not spectral transport.
Heat ledger distinguishes physical adiabatic/Compton/external source,
reference matching correction, chemical ionization energy and defect.
No active thermal or binding-energy stress/photon injection implemented.
Matched BE solves scaled difference with damped Newton, finite difference
Jacobian, physical simplex checks, no clamping. Predictor fallback to
reference is only an initial guess; invalid roots reject. State correction
tolerance 8 eps (1+|delta|+|delta_old|) fixed observed tiny-response loss.
Source reference interpolation: linear abundances and W, logarithmic H,
exact FLRW nH,Tr anchors. Source slice has one He mode; no extrapolation.

## Source and execution
source_reference.py runs unmodified vs output-instrumented pinned original
HyRec C; existing stdout byte identical. 105859 native rows; max charge
identity 1.11e-16; same previous accepted integer-z output agrees xe
2.873e-14 and Tm 5.603e-10 K (not byte parity). Full 16 MB trace at
~/Downloads/rec_r116_reference/species_native.tsv, reconstructible by script.
SLICE_RECEIPT.json gives exact SHA of six compact TSV slices (gzip).
slice_reference.py also builds separate helium.c shared library and makes
27 native pointwise oracle fixtures. C vs Rust max relative 3.407e-16.
HEI_C_FIXTURE.tsv is source generated. Test reference identity is exact
for identical point inputs, not a claim of physical accuracy in anisotropy.
verify_history.py runs 21 cases (three redshift windows, eps=0,0.001,0.01).
First-order convergence at eps=0.001; supplied HeIII test is manufactured.
137 total Rust tests pass; examples compile with zero tests. Existing
unnecessary-parentheses warnings retained. Raw final logs compressed.
No independent native subagents exposed; C oracle and analytic BE test
are independent numerical comparisons. No R78 promotion.

Commands (from repo):
 python3 research/r116_species_thermal/source_reference.py NEW_OUTPUT_DIR
 python3 research/r116_species_thermal/slice_reference.py NEW_OUTPUT_DIR
 cargo test --release --locked --manifest-path rust/rec_microphysics/Cargo.toml
 cargo build --release --locked --manifest-path rust/rec_microphysics/Cargo.toml --example species_thermal_history
 python3 research/r116_species_thermal/verify_history.py rust/rec_microphysics/target/release/examples/species_thermal_history NEW_VERIFY_DIR

Remaining: source-qualified kinetic HeIII and full HeI spectral transfer;
physical transition from HeI cutoff to H-only without hidden reset;
joint chemistry/geometry SDIRK2 (T2); active energy-momentum exchange
with spectral photons (T4); REI handoff. Native HeI response is scoped.
