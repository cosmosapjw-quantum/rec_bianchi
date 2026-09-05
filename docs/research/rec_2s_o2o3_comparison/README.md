# REC 2s: O2/O3 original versus full paired reaction

`O2_O3_REVIEW_PROPOSAL / NOT_PHYSICALLY_AUTHENTICATED`

Fixed parent: `e65ae5c211db4e3375e73410a404f0b23da084d4`.
Parent tree: `e12a4ae4ed17859e4625f80fb0fa86e83a034036`.
This child adds only this directory: a review proposal, a small standalone
checker and its actual results. Production code, original tables, the PR65
contract and historical evidence retain their parent bytes. The current user
request authorizes this comparison and Draft publication; the older root
handoff locates a different REC-NEXT-03 formal execution and is not this task.

The result is a comparison of two scalar laws under explicit assumptions.
Coefficient correspondence does not identify the full native solver with the
paired extension. O1–O6 remain `UNRESOLVED`; the claim remains
`NO_PASS_REC_PHYSICAL_SPLIT`. No physical B, mu, bin boundary, angular kernel,
population history or reference-field owner is selected.

## Evidence and reproducibility

- [O2_O3_REVIEW_PROPOSAL.json](O2_O3_REVIEW_PROPOSAL.json) binds the inherited
  contract and records the alternatives and remaining owner decisions.
- [check_o2_o3.py](check_o2_o3.py) uses Fraction, SymPy, 80-digit mpmath and the
  three existing classes named below. It is a checker, not an adapter/provider.
- [RESULTS.json](RESULTS.json) contains exact residuals, manufactured rates,
  JVPs, conservation ledgers, numerical errors and unexecuted work.
- [COEFFICIENTS_2S.csv](COEFFICIENTS_2S.csv) contains all 140 coefficient and
  temperature-JVP comparisons at the explicitly manufactured diagnostic state.
- [RUN_RECORD.json](RUN_RECORD.json), [CHECKER.log](CHECKER.log) and
  [TARGETED_TEST.log](TARGETED_TEST.log) separate commands, actual execution,
  inherited evidence and limitations. [REVIEW.md](REVIEW.md) records one review.

`DIRECT_SOURCE` means the fixed original source or existing implementation was
inspected. `DERIVED` means the displayed conditional algebra.
`NUMERICALLY_CHECKED` and `IMPLEMENTATION_VERIFIED` are bounded by the actual
results. Algebra is not physical input authentication.

Reproduce from this child or a checkout containing its files and fixed parent:

```bash
PYTHONPATH=src python -B docs/research/rec_2s_o2o3_comparison/check_o2_o3.py
```

Python 3.12, NumPy, SymPy 1.14.0 and mpmath 1.3.0 are used; exact observed
versions are in RESULTS. For new output files add `--output-dir` pointing to
a fresh external directory. Existing results are never overwritten. Run the
existing test node IDs in RUN_RECORD with pytest 8.4.2 and a C compiler for
the coefficient-harness test. No repository dependency file was changed.

Predeclared acceptance: exact Fraction answers and zero SymPy residuals;
140 C/D coefficients within 64 binary64 eps of the 80-digit reference;
temperature derivatives and component-scaled JVPs within 128 eps; the literal
`exp()-1` comparison within the existing C-test bound 2e-13. The smooth
manufactured finite-difference checks use h=1e-3, 5e-4, 2.5e-4, decreasing
error and finest absolute error below 1e-7. Near a null, errors are absolute
or normalized to positive/component magnitudes, never divided by net rate.
These bounds are local arithmetic checks, not a physical error budget.

## Definitions, dimensions and source correspondence

Consider only 2s↔1s and b=0,…,139. The statistical-weight ratio is one. Let
`x_u=x_2s`, `x_g=x_1s` denote populations per H, and let f_t and f_c be
nonnegative scalar photon occupations. The counting variables below are
photon numbers per H, not occupations. Time in the scalar rate is physical
time in seconds; expansion, transport and other atomic channels are excluded
from the isolated reaction ledger. No initial/boundary data are imposed.

Retain ordinary frequency: E=hν=2πℏν, and thermal energy k_B T_r. Original
tabulated energies are reference coordinates in eV. Put

\[
 E_t=E_b,\quad E_c=E_{21}-E_b>0,\quad
 \Theta=T_R=\frac{k_B T_r}{(1\,\mathrm{eV})s_E},\quad
 s_E=f_{\rm sR}^{2}m_{\rm eR},\quad
 a_b=s_A A_{2s,b},\quad s_A=f_{\rm sR}^{8}m_{\rm eR}.
\]

Here the notation for Θ means the numerical source thermal coordinate in eV;
exponents E/Θ use the same reference eV coordinates. Physical photon energy
is s_E E_b (1 eV in J). The ratios fsR and meR are dimensionless. A_b is the
already normalized integrated bin coefficient in s⁻¹, not a differential
density in energy. Neither a width nor an extra photon factor is applied.

Define q_c=exp(-E_c/Θ), q_t=exp(-E_t/Θ), w_t=q_t and
n_c=q_c/(1-q_c). The endpoints E_c=0 and x_g=0 for the inverse below are
outside their stated domains; no limiting cell prescription is inferred.

`DIRECT_SOURCE`: the [PR65 excerpts](../original_hyrec_2s_input_trace/SOURCE_EXCERPTS.txt)
contain `read_twog_params` (hydrogen.c:270–347), normalization (287–290),
`populateTS_2photon` (413–532), the rate scaling (429), C/D assignments
(470–473), and the already-rescaled temperature contract (409, 56–58).

\[
 C_b=\frac{a_b}{1-q_c}=a_b(1+n_c),\qquad
 D_b=C_bq_c=a_bn_c,\qquad C_b-D_b=a_b.
\]

The existing `OriginalHyRecTwoPhotonRamanTable.from_archive` reads the locked
ZIP and normalizes A2s once. Its `evaluate_canonical_coupling` returns the
existing `CanonicalTwoPhotonRamanCoupling`: `real_to_virtual[0,b]=C_b`,
`virtual_to_real[0,b]=D_b`, `Tvr[0,b]=-C_b`, `Trv[0,b]=-D_b`. The sum over
the specified 140 C_b is only this subdomain's diagonal addition. The complete
routine has 311 bins and additional real/virtual, diffusion and source terms.

The checker compares these values against independent 80-digit evaluation
with the actual binary64 inputs lifted exactly. It separately evaluates the
literal original coefficient formula in Python; that is not C execution.
The existing C coefficient test compiles original hydrogen.c and calls its
actual reader, but its harness transcribes the coefficient formulas rather
than calling `populateTS_2photon`. Its actual execution is separately logged.
The full original matrix routine and recombination history are not run here.

## O3: native law and full Bose law

For a prescribed blackbody companion and the native approximation
`1+f_t → 1` in the forward term, the scalar net event/tracked-photon rate is

\[
 R_N=C_bx_u-D_bx_gf_t
     =a_b[x_u(1+n_c)-x_gn_cf_t].
\]

The existing `PhysicalTwoPhotonRamanBin(process="two_photon", ratio=1)` uses

\[
 \Gamma_+=a_bx_u(1+f_c)(1+f_t),\qquad
 \Gamma_-=a_bx_gf_cf_t,\qquad R_P=\Gamma_+-\Gamma_-.
\]

Gamma± are nonnegative event rates per H per second; R_P is signed. Each
event has one tracked high-energy photon. These expressions do not yet give
df_t/dt. Expanding the difference gives exactly

\[
 \boxed{R_P-R_N=
 a_bx_u(1+n_c)f_t
 +a_b(f_c-n_c)[x_u(1+f_t)-x_gf_t].}
\]

The first term restores high-energy stimulation. The second changes the
companion field. Setting f_c=n_c removes only the second term. At f_t=0
the two laws still differ if f_c≠n_c and x_u≠0. With a vacuum companion and
tracked field, both give a_b x_u; summing this spontaneous coefficient gives
s_A (8.2206 s⁻¹) x_u. None of these limits authenticates actual input fields.

The native approximation requires f_t≪1 to suppress the dropped forward
factor. This is an absolute/forward-rate approximation and need not be a
small relative error in a nearly cancelling net rate. The supplied
manufactured f_t=1/3 and 1/4 deliberately expose the distinction; they are
not precision claims for a recombination epoch.

## Distinct null tests

At the conditional LTE population ratio x_u/x_g=q_cq_t and f_c=n_c,

\[
 R_N=a_bx_gn_c(q_t-f_t),\qquad
 R_P=a_bx_gn_c[q_t(1+f_t)-f_t].
\]

Thus the native law has a Wien null at f_t=q_t, while the full pair has a
Planck null at f_t=q_t/(1-q_t). Cross-evaluation gives

\[
 R_N(f_t=n_t)=-\frac{a_bx_gn_cq_t^2}{1-q_t},\qquad
 R_P(f_t=q_t)=a_bx_gn_cq_t^2.
\]

For q_c=1/2, q_t=1/4, x_g=1/2, x_u=1/16 and a_b=1 s⁻¹, n_c=1:

| Tracked field | Native R_N | Full Bose R_P | Paired Gamma+ | Paired Gamma− |
|---|---:|---:|---:|---:|
| Planck f_t=1/3 | −1/24 | 0 | 1/6 | 1/6 |
| Wien f_t=1/4 | 0 | 1/32 | 5/32 | 1/8 |

Every rate is per H per second. Fraction supplies exact arithmetic; SymPy
checks the general identities and the existing paired API supplies the
binary64 comparison. Manufactured frequency metadata (1,2,3)×10¹⁴ Hz enforce
the pair energy relation and q_t=q_c² at a corresponding toy temperature;
they are explicitly not the physical hydrogen 2s frequencies.

## O2: conditional number and energy accounting

For a signed net event rate R and the isolated pair law, the proposed ledger is

| Quantity | Collision contribution per H |
|---|---:|
| Upper population x_u | −R |
| Ground population x_g | +R |
| Tracked photon count N_t | +R |
| Companion photon count N_c | +R |
| Atomic excitation energy | −E21_phys R |
| Tracked photon energy | +Et_phys R |
| Companion photon energy | +Ec_phys R |

This conserves x_u+x_g and energy because E21_phys=Et_phys+Ec_phys. Photon
number itself is not conserved: d(N_t+N_c)/dt=R+R=2R follows from two
distinct ledgers, not from multiplying the tracked vector by two. Reversing
the sign consumes both photons and excites the atom. At fixed energies the
linearized ledgers replace R with δR and retain the same cancellations.
Varying physical energies additionally contributes R δE; complete energy
closure then requires δE21=δEt+δEc. No moving map is constructed.

Two alternatives are presented for owner review, with neither selected:

1. Evolve both photon members and the atomic response using separate,
   non-overlapping, once-counted photon ledgers with their own support.
2. Evolve the tracked member while prescribing the blackbody companion. Then
   the atom-plus-tracked subsystem transfers Ec_phys R to the companion bath;
   its own energy change is −Ec_phys R. Maintaining a prescribed bath requires
   the corresponding reservoir bookkeeping (or a justified infinite-bath
   approximation). A dynamical blackbody temperature is not supplied here.

The existing paired API returns scalar rates and JVPs; it does not execute
these population/companion updates. Applying the same stoichiometry to R_N is
a conditional reduced-law ledger, not a claim that original HyRec evolves
two independent photon distributions or an independent two-level population
ODE. Native populations also use steady-state and ground-state approximations.
Actual atomic response, bath ownership and omitted-sector accounting remain O2/O3
owner decisions. No angular direction, B, mu or integration region follows
from this scalar conservation law.

## O3: inverse distortion transformation and JVP

Let z_b=x_g(f_t-w_t) denote the signed native departure coordinate. For x_g>0,

\[
 f_t=w_t+\frac{z_b}{x_g},\qquad
 \delta f_t=\delta w_t+\frac{\delta z_b}{x_g}
                 -\frac{z_b}{x_g^2}\delta x_g.
\]

The total occupation must also be nonnegative. The inverse is undefined at
x_g=0 even when z_b=0; no continuation/clamping is defined. The reference
field, frame, time variable and directions need explicit ownership before a
production adapter can use this expression. Signed z_b is neither f_t nor
a photon-cell number.

Writing F=x_u(1+f_c)(1+f_t)-x_g f_c f_t, the full pair JVP is

\[
\begin{aligned}
 \delta R_P={}&F\delta a_b+a_b\big[
 (1+f_c)(1+f_t)\delta x_u-f_cf_t\delta x_g\\
 &+[x_u(1+f_t)-x_gf_t]\delta f_c
 +[x_u(1+f_c)-x_gf_c]\delta f_t\big].
\end{aligned}
\]

Substitute the full inverse JVP above into the existing `PhysicalTwoPhotonRamanBin.jvp`;
do not silently set either δw_t or the denominator term to zero. The checker
uses nonzero z_b, δw_t, δx_g and δz_b and records exact nonzero errors caused
by each omission. No new production inverse is implemented.

For the native law, the corresponding computational expression is

\[
 R_N=C_bx_u-D_b(x_gw_t+z_b),
\]
\[
 \delta R_N=x_u\delta C_b+C_b\delta x_u
 -(x_gw_t+z_b)\delta D_b
 -D_b(w_t\delta x_g+x_g\delta w_t+\delta z_b).
\]

With w21=exp(-E21/Θ)=q_cq_t and z_u=x_u-x_g w21,
R_N=C_b z_u-D_b z_b because D_b w_t=C_b w21. The tangent equality also
requires δz_u=δx_u-w21 δx_g-x_g δw21 and the differentiated identity
δD_b w_t+D_b δw_t=δC_b w21+C_b δw21. The checker verifies both identities.
One cannot freeze the reference in one representation while differentiating
it in the other and claim equal JVPs.

## Prescribed blackbody companion: temperature chain rule

For fixed reference energies and θ=log Θ, write y_c=E_c/Θ, y_t=E_t/Θ:

\[
 \delta n_c=y_c n_c(1+n_c)\delta\theta,\qquad
 \delta w_t=y_t w_t\delta\theta.
\]

Consequently δC_b=(1+n_c)δa_b+a_bδn_c and
δD_b=n_cδa_b+a_bδn_c. At fixed a_b, both log-temperature derivatives equal
a_b y_c n_c(1+n_c). These match the existing canonical derivative arrays.
The paired JVP must receive δf_c=δn_c when the blackbody closure is retained.
Its signature accepts independent occupation directions; it does not infer
the caller's temperature or reference-field closure.

If physical temperature and the constants' ratios vary together,

\[
 \delta\theta=\delta\ln T_r-2\delta\ln f_{\rm sR}-\delta\ln m_{\rm eR},
 \qquad
 \delta a_b=a_b(8\delta\ln f_{\rm sR}+\delta\ln m_{\rm eR}).
\]

Feed this δθ, not unconverted δlog T_r, to
`CanonicalTwoPhotonRamanCoupling.jvp`. The 140-row audit includes this chain
using the existing API. A_b and reference energies are fixed. In physical
units the equivalent general occupation rule is
δn=n(1+n)[(E/(k_B T_r))δlog T_r−δE/(k_B T_r)]; no cell motion is implied.

For the manufactured Planck point above, holding z_b=1/24, x_g=1/2,
x_u=1/16 and a_b=1 fixed while varying log temperature gives

\[
 \delta f_c=2\ln2,\quad\delta w_t=\delta f_t=\tfrac12\ln2,\quad
 \delta R_P=-\tfrac{17}{48}\ln2.
\]

Omitting the companion term changes the JVP by +(log 2)/6; omitting the
reference term changes it by +3(log 2)/16. A distinct path that varies the
LTE upper population and both Planck occupations has zero tangent. This is
consistent with an equilibrium manifold and does not turn the fixed-z
temperature derivative into a null.

## Limits and owner action

Scalar, unpolarized 2s counting and ratio one are the declared scope.
No Raman/3s/4s extension, angle-pair distribution, recoil correction,
anisotropic closure, transport or physical population evolution is inferred.
Existing test coverage outside this scalar subset is reported as such.

PR65's historical v0.68 C residual 1.634693744337258e-14 remains a historical
record. Its old tests, PR65's previous table test and previous CI are not
counted as new executions. New executions and any runtime failures are in
RUN_RECORD, and their logs are preserved without replacing old evidence.

The single next action is owner review of the proposed counting/companion
closure and field/reference/JVP contract, identifying the actual responsible
input sources. Acceptance of the algebra alone completes no O1–O6 field and
does not authorize physical input authentication, provider admission, ready,
merge or science promotion.


## Separate sibling research discovered before publication

[Draft PR66](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/66) is a
separate branch on the same PR65 parent. Its research and closeout were read
at `bb205f4f02459863d1a5e3179057c5bd34c598e4`; its reported execution source is
`c2ee9da5235e0cda6d582f156859801fc082bb34`. The earlier 14 symbolic checks and
420 high-precision diagnostic points are sibling context, not fresh counts
in this child. Its original-C/production-module tests were explicitly not run.
Its different manufactured population example is not substituted for the
user's exact 1/2, 1/16 example here.

The present child supplies the general nonblackbody-companion difference,
the requested exact null example, direct calls to existing coefficient/paired
APIs, a newly run existing C-coefficient test, and explicit inverse/reference/
denominator and thermal-coordinate JVP checks. It neither imports that branch
nor supersedes its evidence or owner proposals. Its fixed parent remains PR65.
This historical-context paragraph was added after the frozen independent
review; no new mathematical or numerical execution is claimed by the addition.
