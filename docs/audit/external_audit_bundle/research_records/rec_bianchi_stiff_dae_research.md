# Frozen research plan — rec_bianchi stiff ODE/DAE remedies

Date: 2026-08-23 (Asia/Seoul)

## Question

Which physics-structured numerical methods can cure or materially mitigate the confirmed adaptive backward-Euler, index-1 DAE, pseudo-transient, full-coupled, characteristic, acceptance, event, provenance, and restart blockers in the current rec_bianchi solver stack?

## Hypotheses and falsifiers

- H1: An explicit semi-explicit index-1 DAE contract with constraint-consistent initialization and post-step projection can bind atomic/radiation algebraic variables without destroying physical invariants. Falsifier: the proposed Jacobian block is singular on a declared physical benchmark or projection changes conserved quantities above tolerance.
- H2: Componentwise physical scales and invariant-aware nonlinear acceptance prevent mixed-scale false convergence. Falsifier: an adversarial small-population or cancellation state passes while its dimensionless residual or invariant defect remains O(1).
- H3: Log/softmax or Patankar-type coordinates can preserve the physical domain without clipping-induced Jacobian inconsistency. Falsifier: the transformed formulation cannot represent required boundary states or violates atom/photon conservation.
- H4: Root-located events plus consistent reinitialization prevent minimum-step overshoot and branch-history discontinuities. Falsifier: split-run and uninterrupted integrations disagree after an isolated transverse event.
- H5: Immutable operator manifests and state-bound hashes can make restart equivalence falsifiable. Falsifier: changing any physical operator input leaves the restart identity unchanged, or equal identities fail bitwise/tolerance replay.

## Methods

- M1 confirmatory: inspect current local solver interfaces and exact failure touchpoints.
- M2 confirmatory: retrieve original numerical-method papers or official solver documentation for DAE initialization, stiff error control, event localization, pseudo-transient continuation, positivity/conservation, characteristic integration, and reproducible restart.
- M3 confirmatory: derive project-specific equations, acceptance conditions, and minimal falsifying tests for each remedy.
- M4 confirmatory: classify every remedy as cure, mitigation, or research option and map it to current files.

## Stopping rules

Stop when every named blocker family has at least one physics-specific remedy, equations, a current-code touchpoint, a falsifier, a cure/mitigation classification, and a primary/official source; do not implement or alter repository files. Independent verification belongs to the parent work unit.

## Out of scope

- Editing solver or tests.
- Reconstructing missing E1C implementation.
- Claiming scientific readiness or production admission.
- Benchmarking methods not present in the current tree.

## Evidence log

- E-L1 local, HEAD `5a09f3797210284f83a1a1adb0e0092d1ac48475`; `pyproject.toml` requires NumPy >=2.0 and SciPy >=1.15. Current adaptive controller accepts the one-full-step state while estimating error with two half steps; nonlinear/physical rejection shares the LTE-only controller factor; history candidate receives only the parent history (`adaptive_macro.py:515-655`).
- E-L2 local, `time_dependent_native.py:573-600` and `history_ownership.py:388-406`; the residual is already expressible as `F(eta,y,ydot)=0` with one differential electron row and algebraic native rows, making a semi-explicit index-1 formulation testable once the algebraic Jacobian rank and conservation null modes are made explicit.
- E-L3 local, `pseudotransient_continuation.py:344-379,406-579`; default convergence uses a global state-derived floor and the dense PTC equation; this is the direct touchpoint for componentwise physics scaling, DAE mass structure, and recoverable globalization.
- E-L4 local, `full_coupled_adaptive.py:512-732`; Newton/GMRES convergence is decided before all returned energy/four-force/entropy ledgers, so solver convergence and physical admission are not the same predicate.
- E-L5 local, `characteristic_angular.py:61-240,262-421`; geometry is fixed-step midpoint/RK4, transfer is positive-exact for constant coefficients, but the JVP uses cancellation-prone divided differences and the frequency-face residual does not estimate path/occupation error.
- E-W1 official SUNDIALS IDA 7.6 docs, retrieved 2026-08-23, https://sundials.readthedocs.io/en/v7.6.0/ida/Usage/ ; decisive clauses: `IDACalcIC` can compute algebraic `y_a` and differential `ydot_d` from differential `y_d`; IDA exposes differential/algebraic IDs, inequality constraints, custom positive error weights, roots, and recoverable residual/Jacobian failures.
- E-W2 official SUNDIALS IDA mathematics, retrieved 2026-08-23, https://sundials.readthedocs.io/en/v6.2.0/ida/Mathematics_link.html ; decisive equations: `||LTE||_WRMS <= 1`; Jacobian action contains `dF/dy + alpha dF/dydot`; rootfinder is sign-change based and may miss even-multiplicity roots.
- E-W3 official PETSc 3.25 event/restart docs, retrieved 2026-08-23, https://petsc.org/release/manualpages/TS/TSSetEventHandler/ and https://petsc.org/main/manualpages/TS/TSRestartStep/ ; event callback may change solution/operator, and multistep/FSAL methods must restart after discontinuous state or coefficient changes.
- E-P1 Coffey, Kelley, Keyes, SIAM JSC 25 (2003), DOI 10.1137/S106482750241044X; establishes pseudo-transient continuation theory for semi-explicit index-1 DAEs, not arbitrary singular or unscaled residual systems.
- E-P2 Eisenstat and Walker, SIAM JSC 17 (1996), DOI 10.1137/0917003; decisive condition `||F+J s|| <= eta_k ||F||` and adaptive forcing avoids oversolving far from a root.
- E-P3 Knoll and Keyes, JCP 193 (2004), DOI 10.1016/j.jcp.2003.08.010; JFNK requires physics-relevant preconditioning even when Jv is matrix-free.
- E-P4 Chang and Cooper, JCP 6 (1970), DOI 10.1016/0021-9991(70)90001-X; their Fokker-Planck discretization preserves nonnegativity, particle conservation, and analytic equilibrium. Burchard et al., Applied Numerical Mathematics 47 (2003), DOI 10.1016/S0168-9274(03)00101-6, gives positive conservative modified Patankar production-destruction schemes.
- E-P5 Jin, SIAM JSC 21 (1999), DOI 10.1137/S1064827598334599; asymptotic-preserving schemes remain useful without resolving the vanishing kinetic relaxation parameter.
- E-P6 Lindquist, Annals of Physics 37 (1966), DOI 10.1016/0003-4916(66)90207-7; covariant radiation transport uses the Lorentz-invariant occupation/intensity `I_nu/nu^3`. Munthe-Kaas, Applied Numerical Mathematics 29 (1999), DOI 10.1016/S0168-9274(98)00030-0, constructs RK methods on manifolds.
- E-P7 Al-Mohy and Higham, SIAM JSC 33 (2011), DOI 10.1137/100788860; phi functions/exponential actions are handled with backward-error-controlled series/scaling rather than cancellation-prone raw quotients.
- E-P8 Ogita, Rump, Oishi, SIAM JSC 26 (2005), DOI 10.1137/030601818; accurate summation/dot products can reach roughly twice-working-precision accuracy without globally changing precision.
- E-P9 NIST FIPS 180-4, DOI 10.6028/NIST.FIPS.180-4; SHA-256 detects changed canonical bytes with high probability but does not decide which physics inputs must be serialized.
- E-X1 confirmatory derivation check, command `python` with mpmath 80-digit scalar transfer and stiff decay: for `z=1e-2,1e-8,1e-20`, the derived stable `psi(z)=((1+z)exp(-z)-1)/z^2` series agreed with the high-precision derivative to the reported precision; for `y'=-1000y`, `h=1e-3`, the two-half-BE error was `0.0765650` versus full-BE `0.1321206`, while their difference was `0.0555556`. Exit 0. This confirms the algebra, not implementation behavior.
