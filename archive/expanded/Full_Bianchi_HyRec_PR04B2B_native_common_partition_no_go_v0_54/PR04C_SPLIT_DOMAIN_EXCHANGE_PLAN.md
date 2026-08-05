# PR-04C plan — split-domain conservative exchange contract

## Classification

`BOUNDED_RESEARCH_PLAN / PR-04C / v0.55-candidate`

## Entry condition

PR-04B2B/v0.54 has established two independent obstructions to a direct
original-HyRec-to-17-cell equality:

1. the positive native physical edge measure is not support-compatible with
   the 17-cell interval `x in [-4.25,4.25]` even at the `M0,M2` level;
2. after restricting support, five moments do not identify seventeen positive
   cell masses without an additional closure.

PR-04C therefore does **not** attempt another global remap. It couples two
representations through an explicit interface carrying conserved fluxes.

## Fixed conventions

- metric signature `(-,+,+,+)`;
- hydrogen orthonormal tetrad;
- ordinary frequency `nu` in Hz;
- `x=(nu-nu_Lya)/Delta_nu_D`, `y=ln nu`, `eta=ln a`;
- `Delta nu=nu_target-nu_source`;
- `Delta E_gamma=h Delta nu`, `Delta E_H=-h Delta nu`;
- `c`, `h`, and `k_B` remain explicit;
- homogeneous background only;
- no free normalization, empirical offset, silent high-resolution
  substitution, or post-hoc trajectory fitting.

## Representation ownership

### COM–KHW collision domain

The scalar COM–KHW module owns the already verified 35-state collision network
on

```text
x in [-21.25, 21.25]
```

consisting of 17 interior, 12 near-exterior and 6 far-exterior states. It owns
local resonant collision events, stimulated Bose factors, recoil moments and
the same-event atom four-force. It does not own free redshifting beyond the
outer boundary or exterior–exterior transport.

### Original-HyRec transport domain

The original-HyRec module owns its full native radiation support, line escape,
free streaming between native frequencies, trajectory history and the
primitive real/virtual-state algebra. It does not silently replace the
COM–KHW collision event tensor in the declared 35-state domain.

### Interface ownership

The interface is defined at the physical frequencies corresponding to
`x=-21.25` and `x=+21.25` in the local hydrogen frame. A single mortar/exchange
object owns the cross-interface transfer. No transfer may be counted in both
subdomain operators.

## Conserved exchange variables

For each side `s in {red,blue}` and timestep, define signed interface ledgers

```text
Phi_N^s       photons per H per second,
Phi_Egamma^s photon energy per H per second,
Phi_EH^s     atom energy per H per second,
Phi_Pa^s     optional tetrad spatial momentum per H per second.
```

The mandatory scalar gates are

```text
Phi_N(native->interface) + Phi_N(interface->COM) = 0,
Phi_Egamma(native->interface) + Phi_Egamma(interface->COM) = 0,
Phi_Egamma^s + Phi_EH^s = 0
```

up to roundoff. Spatial momentum is retained where the existing same-event
four-force data determine it; it must not be inferred from a scalar frequency
moment alone.

No `M2-M4` equality is required across the interface. Those moments remain
representation-local diagnostics unless a source-derived interface packet
measure is available.

## Interface state rule

A cross-interface transfer is represented first as an unresolved positive
packet carrying `(Phi_N,Phi_Egamma)`, not as an arbitrary distribution over the
17 interior cells. If `Phi_N>0`, its energy centroid is

```text
nu_bar = Phi_Egamma/(h Phi_N).
```

The packet is admissible only if `nu_bar` lies on the declared interface side.
The packet is deposited into the existing far-boundary/Liouville module, which
then transports it into or out of the 35-state collision domain. Collapsing the
packet directly into an interior cell is forbidden.

A two-node or higher positive packet reconstruction may be introduced only
when its support and moments are independently source-derived. Tchakaloff-type
existence does not supply uniqueness and is not itself a closure policy.

## PR-04C0 — ownership and no-double-counting theorem

1. Enumerate every native and COM–KHW term by physical process and support.
2. Produce an operator ownership matrix with exactly one owner for every term.
3. Prove that the sum of subdomain and interface operators reproduces the
   uncoupled baseline when the replacement switch is off.
4. Add a runtime assertion that cross-interface flux is evaluated once and
   applied with opposite signs.

**Hard gate:** no process or flux term has two owners or zero owners.

## PR-04C1 — source-identical boundary instrumentation

Use exact nearest-grid locks near

```text
z approximately 1300, 1100, 900
```

and record, for both physical interfaces:

- local `z,T_m,T_r,n_H,H,x_e,x_1s`;
- native incoming/outgoing occupation data and free-streaming history indices;
- source-identical number and energy fluxes;
- primitive/dense/Schur real–virtual actions;
- COM–KHW boundary-state occupation and collision action;
- boundary-speed sign and every in-step zero localization.

Guard-off original-HyRec binary and baseline-history hashes must remain equal to
v0.53. Public interpolation parity is a separate diagnostic and cannot alter
physical normalization.

## PR-04C2 — conservative interface operator

Implement an `ExchangePacket` and `SplitDomainExchangeOperator` with:

- strict units and sign validation;
- nonnegative packet number;
- exact opposite-sign number/energy application;
- log-variable implicit update for positive occupations;
- analytic residual JVP and central/high-precision reference tests;
- boundary packet restart serialization;
- geometry-independent local microphysics.

The implicit residual must include the interface packet and both subdomain
updates in one conservation ledger, even if the nonlinear solve is block
preconditioned.

## PR-04C3 — multi-snapshot closure

At each locked snapshot compare:

1. unmodified original-HyRec native action;
2. native primitive versus dense/Schur action;
3. uncoupled 35-state COM–KHW action;
4. interface number/energy packet;
5. coupled split-domain residual and JVP.

Required gates:

- photon-number residual;
- photon+atom energy residual;
- optional tetrad four-force residual where available;
- strict occupation positivity;
- BE/equilibrium null in a no-expansion local test;
- free-energy nonincrease for the collision substep;
- boundary branch and zero localization;
- primitive/direct/Schur parity;
- analytic/JVP parity;
- exact guard-off baseline invariance;
- Bianchi II, one class-B model and exceptional `VI_-1/9` local-state firewall.

## PR-04 completion criterion

PR-04 closes only if the split-domain contract gives one common conservative
ledger at all predeclared snapshots without a fitted scale and without direct
state-vector equality. The closure statement must be limited to scalar
homogeneous-background transport. Full trajectory integration belongs to PR-05
and FLRW history parity to PR-06.

If no source-identical positive interface packet can be constructed, publish a
second no-go and retain original-HyRec as an external closure rather than
forcing an inconsistent monolithic operator.

## Numerical-method rationale

Conservative positive remapping methods require an explicit relation between
source and target meshes or an explicitly designed interpolation problem. The
canonical original-HyRec runtime archive does not supply that missing cell
geometry. Mortar and flux-mortar methods instead couple nonmatching
representations through interface flux variables and weak flux continuity. The
PR-04C contract adopts only that structural lesson: the physical number/energy
flux is the interface variable, while each subdomain retains its own internal
representation.

Relevant methodological references:

- Curto & Fialkow, *A duality proof of Tchakaloff's theorem*, JMAA 269 (2002),
  arXiv:math/0207065.
- Zhang, Huang & Qiu, *High-order conservative positivity-preserving
  DG-interpolation ... radiative transfer*, arXiv:1910.11931.
- Girault, Sun, Wheeler & Yotov, *Coupling Discontinuous Galerkin and Mixed
  Finite Element Discretizations using Mortar Finite Elements*, SIAM J. Numer.
  Anal. 46 (2008), DOI 10.1137/060671620.
- Boon, Gläser, Helmig & Yotov, *Flux-Mortar Mixed Finite Element Methods on
  NonMatching Grids*, SIAM J. Numer. Anal. 60 (2022), DOI 10.1137/20M1361407.

## Durable outputs

Implementation, unit/sign registry, ownership matrix, tests, formalism,
three-snapshot CSV/NPZ evidence, JVP references, immutable ledger and manifest,
stage ZIP, Git commits, full bundle, and binary-safe incremental,
remote-milestone and cumulative patches.
