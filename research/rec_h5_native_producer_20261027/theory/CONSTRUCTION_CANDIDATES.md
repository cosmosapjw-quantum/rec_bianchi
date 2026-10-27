# REC-H5-NATIVE-REFERENCE01 — source-matched reference producer

Author role: theory construction delegated by root. Workflow: user-selected
`physmath-research-loop` 1.0.0, R2/R4/R5. This note supplies the candidate
construction and exact equations; root owns the frozen implementation contract,
independent admission, stage status and publication. No scientific runtime or CAS
was executed while constructing this note.

## 1. Choice and actual input availability

The selected next construction is a **native Wien reference derivative,
whole-cell curvature and represented-clock bridge producer for the actual 313
history queries**. It supplies a previously unbound part of the observable map
`G`, with explicit input identities and finite analytic extrema.

The original history archive contains `average_virtual (311,7489)`,
`outgoing_virtual (311,7489)`, `outgoing_lyman (3,7489)`, `eta (7489)`, the
311-bin energy/frequency grids, `source_indices`, `dlna`, `z_start`, and metadata.
Its NPY headers were read without loading or recomputing a trajectory. It does
not contain a full history of `xe`, `xHII`, `TM`, `H` or their derivatives.
The native CSV contains those quantities at one face only. Thus it supports the
reference construction below directly; it does not already contain the
continuous full-state reconstruction needed to evaluate a whole-domain ODE
defect.

The preserved history has SHA256
`d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1`.
The fixed 313-query context has SHA256
`5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8`.

| Candidate | Concrete first construction | Current decision |
|---|---|---|
| Native Wien reference producer | Analytic `G_eta`, `G_etaeta`, exact finite extrema, reference pullback bridge, existing anchor composition on 313 cells | Selected |
| Uniform finite-parameter enclosure of instantaneous native atom/radiation map | Enclose `M(theta)`, its inverse and source/rate functions over a positive thermodynamic box | Useful later; requires uniform coefficient/inverse bounds beyond the already completed pointwise six-column derivative |
| Full same-clock ODE defect and bootstrap | Reconstruct all physical state variables and evaluate `xhat'−F(eta,xhat)` over complete cells and a certified tube | Exact missing inputs are full-state histories, the selected continuous `F`, its domain and initial/model error; do not replace these with radiation samples |
| Repeated represented-linear jump remainder | Recompute previously completed retiming/chord identities | Reuse prior completed results; not this unit's new contribution |

HISTORY02 supplies generic reference offset/JVP and the global `1/e` derivative
bound. The actual 313-cell source binding, finite-cell curvature extrema and
source-clock/native-temperature decomposition below are the new selected
application. Root's latest-source intake must retain the immutable HISTORY02
source pin and its different cosmology and validation scope.

## 2. Source and convention binding

All paths below are relative to `rec_bianchi`.

- `research/rec_history_thermo_20261024/vendor/hydrogen.h`, lines 29–37:
  `E21=10.198714553953742`, `E31=12.087365397278509`,
  `E41=12.748393192442178`, and native `kBoltz=8.617343e-5 eV/K`.
- `research/rec_history_thermo_20261024/vendor/full_2012_atomic_source.py`,
  lines 247–248: radiation temperature is `KB_NATIVE_EV_K*T0*(1+z)`;
  matter temperature has its separate native conversion.
- `research/rec_history_thermo_20261024/vendor/original_hyrec_native.py`,
  line 65 and lines 378–384: the native Boltzmann constant and
  `exp(-energy/temperature_eV)` equilibrium factor; the factor three at the
  population line-centre state is a population degeneracy, not an occupation
  factor to insert in the outgoing photon reference.
- `research/rec_history_thermo_20261024/vendor/hydrogen.c`, lines 633–652:
  direct linear interpolation of signed photon departure, with strict causal
  prefix support. Lines 667–718 bind each incoming energy to its source energy
  and redshifted query. Lines 794–796 bind the three outgoing Lyman departures.
- `research/rec_history_geometry_response_20261026/inputs/history.npz`:
  original radiation histories and energy grid.
- `research/rec_history_geometry_response_20261026/inputs/target_native_snapshot.csv`:
  original face `z=1099.9986525171403`, `iz_local=5127`,
  native `TR_eV_rescaled=0.25882399309326415`, and bin energies.
- `research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json`:
  exact binary64 hex queries, source-channel indices, cells, stored geometric
  endpoint times, endpoint samples, geometric alpha, native alpha, nominal
  incoming values and existing representation radii.

For this source-specific construction, source constants, `T0=2.728 K`, energies,
`z` and saved coordinates are interpreted as the exact reals represented by
their recorded binary64 values. In particular, use the source-native binary64
`kBoltz`; replacing it with a modern SI-derived value changes the model.
Record the literal token, binary64 hex and this interpretation. A separate
literal-decimal or SI comparison would need its own explicit model label.

The photon occupation and its departure are dimensionless. The clock is
dimensionless `eta=ln(a)`. `fsR=meR=1` is fixed. No Planck-for-Wien replacement,
frequency-density Jacobian, p/o-H2 mixing, temperature extrapolation, native
solver execution or new IVP belongs in this construction.

## 3. Continuous reference and observable derivatives

Let `kN` be the fixed native Boltzmann constant and define the exact selected
reference law

    T_R(eta) = kN*T0*exp(-eta),
    kappa_E = E/(kN*T0),
    x_E(eta) = kappa_E*exp(eta),
    w_E(eta) = exp(-x_E(eta)),
    G_E(eta,f) = f-w_E(eta).

`E` is the source channel energy, in eV. This defines a smooth reference on any
finite eta interval with positive `E,kN,T0`. It is not defined by interpolating
the saved reference values.

Since `x'=x`, direct differentiation gives

    w'   = -x exp(-x),
    w''  = (x^2-x) exp(-x),
    w''' = (-x^3+3x^2-x) exp(-x).

Consequently

    G_f=1, G_ff=G_etaf=0,
    G_eta=x exp(-x),
    G_etaeta=-(x^2-x) exp(-x).

For two occupation arguments at the same eta,
`|G(eta,f1)-G(eta,f2)|=|f1-f2|`. The scalar Lipschitz constant is exactly one
in the unit occupation coordinate. If the declared scalar state norm is
`|delta f|/s_f`, the constant is `s_f`. This must not be labelled as the
Lipschitz constant of the still-undeclared full coupled state map.

### Finite-cell extrema

On a cell `[a,b]`, let `[x_a,x_b]` be the corresponding positive x interval.
Since x is strictly increasing, a finite exact formula for the reference
curvature bound is

    M2_ref = max |(x^2-x)exp(-x)|

over the endpoints and any included roots

    r_minus=(3-sqrt(5))/2,
    r_plus =(3+sqrt(5))/2.

Proof: the derivative with respect to eta is
`-x(x^2-3x+1)exp(-x)`. Interior nonzero extrema occur exactly at these two
positive roots. The zero at x=1 cannot increase the absolute maximum. The
endpoint case handles a singleton interval, including x=1. Likewise the exact
supremum of `|w'|=x exp(-x)` needs only the endpoints and x=1 if included.
For a cell proved to lie wholly above r_plus, both extrema reduce to their
left endpoint; that simplification must follow a verified interval-domain
comparison rather than an assumed numerical regime.

## 4. Exact reference translation preserves defect and stability

This lemma specifies how the reference producer will connect to a future
same-clock physical ODE. Suppose the full occupation state obeys

    f' = F_f(eta,f).

For the exact reference translation `y=f-w(eta)`, define

    F_y(eta,y) = F_f(eta,y+w(eta))-w'(eta).

Then y obeys `y'=F_y(eta,y)`. Given an absolutely continuous approximate path
`fhat`, set `yhat=fhat-w`. Direct substitution yields the identity

    yhat'-F_y(eta,yhat) = fhat'-F_f(eta,fhat).

Thus the exact reference translation preserves the ODE defect. It also
preserves `yhat-y=fhat-f`, every fixed norm of that error, and the state
Lipschitz bound, because the same reference translation is applied to both
arguments of F. A tube around fhat is translated to the equal-radius tube
around yhat, with existence/bootstrap obligations unchanged. The argument
extends to a full vector state by translating only the photon components.

This is a conditional change-of-variables lemma; it supplies no numerical
full-state `F`, `d`, `L`, initial error or tube radius. If an approximate or
different reference is used, its actual value/derivative differences must be
added explicitly rather than setting them to zero.

## 5. Characteristic matching and native-temperature bridge

For incoming target energy `Et` and higher source energy `Es`, the exact
characteristic query associated with the represented target redshift z is

    q_ideal = -ln((1+z)*Es/Et).

Native source code computes the frequency ratio and logarithm in floating
arithmetic; the fixed H5 query `qhat` is the recorded binary64 result. Keep
qhat as the query used by the current H5 packet. Define

    x_t = Et/[kN*T0*(1+z)],
    delta_q = qhat-q_ideal.

Then `x_s(q_ideal)=x_t`, so the exact common-reference identity is

    w_s(q_ideal)=exp(-x_t).

At the actual fixed represented query the signed characteristic-reference
bridge is

    B_char = w_s(qhat)-exp(-x_t)
           = exp(-x_t)*expm1[-x_t*expm1(delta_q)].

This stable form exposes both the sign and the small nonzero bridge. Avoid
forming a tiny bridge by subtracting two separately rounded binary64
occupation values.

Let `TRhat` be the exact real represented by the fixed native CSV temperature.
It is a separate input from the analytic real product `kN*T0*(1+z)`. Define

    w_native = exp(-Et/TRhat),
    B_TR = exp(-x_t)-w_native,
    B_total = B_char+B_TR = w_s(qhat)-w_native.

The component split retains the native arithmetic/continuous-model distinction.
It does not infer a physical temperature uncertainty from a floating-point
representation difference. All three signed quantities can be enclosed as
deterministic reference-conversion terms for the stated arguments.

The exact source routing is inherited from SOURCE_CONTEXT: source indices
0..310 denote the outgoing virtual bins, 311/312/313 denote outgoing
Lyman alpha/beta/gamma. Incoming indices 0..310 use their corresponding target
virtual energies; incoming 311/312 use E21/E31. Cross-check those bindings
against native hydrogen.c's special adjacent-line cases before evaluating any
reference term.

Physical retiming from qhat to q_ideal additionally changes the physical
occupation itself. B_char controls only the known reference component.
PB01's query-coordinate error/regularity obligations remain the correct place
for the physical retiming component.

## 6. Reference chord and preserved native anchor

Use the existing H5 geometric cell, not an unannounced replacement of its
clock: `a=eta_left_hex`, `b=eta_right_hex`, `q=qhat`,
`alpha=(q-a)/(b-a)` as an exact rational. Define

    Iw = (1-alpha)w_s(a)+alpha w_s(b),
    J_ref = Iw-w_s(q).

The ordinary linear-interpolation remainder gives

    |J_ref| <= M2_ref*(q-a)*(b-q)/2.

The coefficient is already present as
`pointwise_curvature_coefficient_exact` in the old H5 context. Reuse or exactly
check that identity; do not rerun old source or matrix work. If the complete
cell has x>1 then w''>0, so convexity further implies `J_ref>=0`.

Let the two stored departure samples be yL,yR, the fixed nominal incoming
value be uhat and `Iy=(1-alpha)yL+alpha*yR`. The existing signed anchor is
`r_anchor=uhat-Iy`; its absolute value is the preserved
`anchor_representation_radius_exact`. Then the following exact identity holds:

    [uhat+w_native] - [(1-alpha)(yL+w_s(a))+alpha(yR+w_s(b))]
       = r_anchor-J_ref-B_total.

This connects the actual native reconstructed absolute occupation to an
absolute-endpoint geometric interpolant using the same stored samples. A
valid bound for this deterministic representation bridge is

    R_bridge = |r_anchor| + upper(|J_ref|) + upper(|B_total|).

The signed direct identity should also be evaluated independently to expose
sign mistakes. It is not a new physical interpolation epsilon: the physical
endpoint errors and physical absolute-occupation curvature are still required.
Do not add an exponential factor to native direct departure interpolation.

If useful for domain reporting, `P_y(t)+w_s(t)` has the conservative whole-cell
lower bound `min(yL,yR)+w_s(b)`. A positive lower endpoint of that bound proves
positivity of this represented reconstruction on the cell. It is not a
full-state ODE tube or an existence proof, and should not be named rho.

## 7. Finite implementation contract suggested to root

### Inputs and arithmetic

Use immutable SOURCE_CONTEXT, the native CSV, the original history energy grid,
native constants and their existing source identities. Root fixes the precise
source snapshot and whether original history bytes are reread or the already
verified energy extraction is reused. No old primary/certificate run is needed.
Every scalar source value is converted from its recorded binary64 hex to an
exact rational before interval/high-precision arithmetic.

For authoritative enclosures use outward interval arithmetic for every
conversion, product, quotient, logarithm, square root and exponential. A
minimal practical implementation may use Decimal directed arithmetic and
one-neighbour outward enclosures of correctly rounded elementary operations,
provided that elementary-rounding contract is explicitly documented and
checked against primary Python documentation. Mathematical enclosure and
binary64 candidate agreement are separate tests. Independent higher precision
is useful for diagnostics but does not alone prove outward containment.

Do not force a single sign if a signed bridge enclosure contains zero. For
critical-point inclusion, interval overlap with a cell requires conservative
inclusion or a higher-precision decision, not exclusion by a rounded scalar.

### Required per-query output

- Source/target energy identities, cell endpoints, qhat, exact alpha and existing
  anchor radius; all 313 input-to-output bindings.
- Enclosures for x at endpoints/query, w, G_eta, G_etaeta, scalar occupation
  Lipschitz factor, and whole-cell `M1_ref`, `M2_ref`.
- Which analytic critical points were included and any regime simplification.
- Separate signed `B_char`, `B_TR`, `B_total`, `J_ref`, direct chord residual,
  chord upper bound and the native-to-absolute-interpolant bridge identity.
- Optional represented-occupation lower bound, explicitly labelled as such.
- A partial producer packet with `reference_bounds` complete and
  `physical_query_bounds`, full-state K, physical M2, defect, stability, tube,
  initial error and physical epsilon still null unless separately supplied.

### Discriminating controls

1. Analytic derivative identities and the two curvature stationary points.
2. A cell crossing each critical point; cells on both sides of x=1; a point
   cell at x=1; positive energy/temperature and ordered-cell domain refusals.
3. Ideal characteristic match gives B_char=0 exactly at the mathematical level;
   finite represented q shifts have the analytically predicted sign.
4. Native-temperature equality gives B_TR=0; isolated temperature mismatch is
   kept separate from q mismatch.
5. Constant/affine reference toy controls and an actual convex-reference chord
   verify sign and the `1/2*(q-a)*(b-q)` coefficient.
6. Independent direct absolute-interpolant evaluation checks
   `r_anchor-J_ref-B_total` without importing the production decomposition.
7. An explicitly chosen smooth toy F checks the reference-translation defect
   identity algebraically, with no IVP solve.

An enclosure may be wide yet valid. Any tighter accuracy criterion for useful
printing/transport must be fixed before execution and must not replace the
mathematical containment requirement.

## 8. Exact remaining physical inputs and scope

The selected reference law and all finite-cell reference bounds can be
completed from actual fixed input data. H5's full physical packet additionally
needs the physical state trajectory and its continuous F, fixed state norm,
initial error, model discrepancy, whole-domain defect/stability, certified
positive uniform open tube, physical endpoint errors and absolute-occupation
curvature or a source-derived equivalent. `M2_ref` is one known term in
`y''=f''-w''`, not a replacement for the missing physical `f''` bound.

Keep `physical_epsilon=null`, `physical_outgoing_bound=null`, and physical
coverage `0/313` until those actual inputs are supplied. This construction does
not alter HD data, H6/H7 status, old budgets, production or REI activation.
No strong no-go or general novelty claim is proposed; the new contribution is
the exact source-specific computational binding and partial producer output.
