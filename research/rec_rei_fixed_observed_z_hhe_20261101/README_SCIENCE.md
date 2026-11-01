# REC–REI | source-owned H/He fixed-observed-redshift Thomson response

2026-11-01. EXPLORATORY / SOURCE-CONDITIONAL / FIRST VARIATION / NOT ADMITTED CANONICALLY.

## Source locks
- Original physical H/He epochs: rei_bianchi PR #319, HEAD a51cf20df6afa5d98bd96be01a5e68c3cfe72785, original Git blob aaf60834dcc095025ad6261515fa5535d5b30894, exactly duplicated as SOURCE_REI319_11_EPOCHS_BYTE_EXACT.csv (11 saved source-conditioned model epochs, not measurements).
- REC parent PR #184, immutable HEAD 4d7749068b8d9fab12d1f61f1c2158688d7b94c5. Its z20 HyRec2012 donor is NOT adopted into this new source. Geometry uses only the conditional adopted LRS signed-q parameterization, calibrated with REI PR319 flat FLRW H(z).
- Underlying UVB context: Puchwein et al., MNRAS 485 47–68 (2019), DOI 10.1093/mnras/stz222; REI #319 is source-conditioned synthetic-initial-condition Python Case-A chemistry, not native Rust F05 or observed CMB tau.
- Comparison BASS #306 HEAD edfed2152c8fc28a6c96fc59341c4d10538c2937 supplies fixed-observed-z Sachs response on DIFFERENT original Einstein–Vlasov background. No source-owner equivalence established.

## Mathematical derivation and conventions
Metric (-,+,+,+), keep c and sigma_T. LRS Bianchi I ds²=-c²dt²+a² exp(-2b)(dx²+dy²)+a² exp(4b) dz². s=dot b=qref Hf(20)[(1+z)/21]^3, H_B²=Hf²+s². REI319 H0=67.4 km/s/Mpc, Om=.315, Or=9.27e-5, OL=1-Om-Or, YHe=.245; differs slightly from REC #184 illustrative background and helium.

Observer is comoving locally at source zlo=5.81, NOT at Earth z=0. Conserved spatial photon momenta yield

  E_em/E_obs = (1+z_em)/(1+zlo) sqrt[(1-mu²) exp(2b_em)+mu² exp(-4b_em)].

Define K(z)=Hf(20)/21³ times integral_zlo^z ((1+z')²/Hf(z')) dz', and R(z)=c sigmaT ne(z)/Hf(z). To first order b=-qref K. At fixed observed redshift, the emitter's mean cosmic redshift moves by delta ln(1+z_em)=qref K(1-3mu²). Consequently:

  tau_obs(z,mu;qref)=tau_REI319_FLRW(z)+qref K(z) R(z) (1-3mu²)+O(qref²);
  a2(z)=-2 qref K(z) R(z)+O(qref²); first sky monopole perturbation=0.

At fixed mean cosmic time, instead, the comoving homogeneous Thomson tau has zero FIRST-ORDER directional term; confusing these two surfaces is a physical error. Units: K,R,tau,a2 are dimensionless, c sigmaT ne and Hf have s^-1. This is a local observer fixed-redshift *first derivative*, not exact finite-shear tau, a photon Boltzmann collision solution, or a new coupled IGM history.

## Actual 11 source-epoch physical results
At qref=+.01 (linear response coefficient only):

| Actual source z | Original FLRW segment tau | K(z) | linearized a2 |
|---:|---:|---:|---:|
|10|0.01738941213755|0.129651847181|-5.85081810e-8|
|9.98682|0.01738927260492|0.129197451340|-5.42937579e-7|
|8.99410|0.01666163849003|0.095765120303|-2.90813742e-5|
|8.06930|0.01444181279243|0.066083028420|-4.02938989e-5|
|8.00430|0.01421852736877|0.064051847929|-4.04824570e-5|
|7.24984|0.01086289204813|0.041020881577|-3.69109083e-5|
|6.99667|0.00938849869713|0.033523248007|-3.32701628e-5|
|6.48644|0.00580327606948|0.018776012554|-2.21552484e-5|
|6.13594|0.00285729068226|0.008934322946|-1.11655237e-5|
|6.00037|0.00166486212940|0.005192583056|-6.39596724e-6|
|5.81000|0|0|0|

Nontrivial: the strongest sampled reset-branch response is at z≈8, not its almost neutral z10 initialization. The z8.004 coefficient is 0.2847% of its source-owned FLRW segment optical depth.

For the SEPARATE REI #319 synthetic source-prehistory (z15.1 start), z10 xHII=0.1856732600 and tau(zlo,z10)=0.02124625716114 are reported, but the corresponding helium species are absent from the original 11-row Git witness. Enforce the physical bound 0 ≤ He electrons per H ≤ 2fHe, fHe=YHe/[4(1-YHe)]. Then at qref=.01:
-0.0001013710708254 ≤ a2 ≤ -0.0000540975835427. This is a conservative missing-He **physical envelope**, not a posterior or same-initial-state run.

## Execution and hostile review
Local full producer generated 1,155 new first-order directional rows, 55 multipoles, 10 physical He-bound rows and five independently evaluated exact-geodesic controls; original 11 owner rows were reused and not double counted. Normal Python 14/14 PASS, Python -O 14/14 PASS, compileall PASS. Wolfram symbolic redshift/monopole/P2 check PASS. At z8.004, an independently root-solved finite-shear photon redshift + sparse log-ne PCHIP numerical control agrees with derivative at q→0 to 1.73156e-10 relative error. The full q=.01 finite-shear comparison differs by up to ~0.18% in chosen axis ray, but sparse PCHIP is NOT an accepted native REI history.

Reintegrating tau from only eleven saved electron epochs yields -0.344625% interpolation bias relative to REI319 source-published tau. Therefore do not overwrite original source tau. The Git quick reproducer computes 1,155+55 original-epoch response values; full tested producer, source-inclusive science data, test suite and figures are separate archive. Distinct-author referee NOT_RUN; this is one same-author adversarial pass only.

## Authority and next central physics
Original REI canonical 28/88 (+0), working 33/88 (+0), Physical Fast 4/7 (+0); REC physical H5 0/313 (+0). REI PR #320 source-authentic first canonical interval remains BLOCKED at tick160→161 of 131072; no new F05/F08 admission, no source swap, no force push, no merge, no tolerances relaxed, no new IVP or budget reset, no L4/production.

**Next:** central REI first-interval nonlinear same-parent difference and source-owner feedback repair under unchanged gates; then integrate a SAME-OWNER accepted Bianchi electron/history/photon transport response. No further auxiliary atlas by default.