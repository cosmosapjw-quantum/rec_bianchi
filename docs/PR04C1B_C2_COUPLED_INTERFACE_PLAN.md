# PR-04C1B/C2 plan — far-boundary deposition and coupled interface solve

## Entry state

PR-04C0/C1A v0.55 supplies six source-identical positive photon packets,
operator ownership, restart serialization and exact cross-representation
number/energy ledgers. No packet has yet been assigned to a COM–KHW cell.

## Design rule

The packet is deposited only into the pre-existing far-boundary/Liouville
state associated with `x=-21.25` or `x=+21.25`. It must not be collapsed into
an interior collision cell. Original HyRec retains full-support free streaming;
COM–KHW retains local collision/Bose/recoil physics. The interface term is
single-owner and appears once in the monolithic residual.

## C1B — boundary state adapter

1. Identify the exact `FR00` and `FB02` outer states and their mode measures,
   interval orientation and photon-energy centroids.
2. Define an unresolved ghost/boundary accumulator carrying photon number and
   photon energy separately from the resolved COM occupation.
3. Map blue `native_to_com` packets into the blue accumulator and red
   `com_to_native` packets out of the red accumulator; reject side or sign
   mismatches.
4. Keep packet restart round-trips bitwise stable.
5. With the interface switch off, reproduce v0.55 and the v0.49/v0.50 collision
   actions exactly.

## C2 — coupled implicit residual

Use log variables for positive resolved occupations and nonnegative variables
for packet accumulators. The monolithic residual includes:

- original-HyRec boundary packet evaluation;
- far-boundary/Liouville transfer;
- 35-state nonlinear Bose collision action;
- native and COM number/transported-energy ledgers;
- existing local atom four-force from collision events only.

Implement an analytic block JVP and compare against central differences and a
high-precision small system. Matrix-free Newton–GMRES may be block
preconditioned, but conservation must be checked on the unpreconditioned
residual.

## Boundary-speed and branch gates

For Bianchi II, a class-B representative and exceptional `VI_-1/9`, use the
existing `BackgroundSnapshot` characteristic adapter and piecewise-linear root
localizer. Every red/blue speed zero inside a timestep must be localized before
integrating signed flux. No endpoint sign heuristic may replace root
localization.

## Hard gates at z~1300,1100,900

- strict positivity of resolved occupations and packet accumulators;
- exact/global photon-number ledger to roundoff;
- exact transported photon-energy exchange between representations;
- atom four-force only from physical collision terms;
- analytic/JVP relative residual `<1e-8` with tighter high-precision controls;
- implicit residual `<1e-11`;
- free-energy nonincrease for the collision substep;
- branch-zero localization and restart parity;
- primitive/direct/Schur native parity retained;
- Bianchi-label firewall at identical local hydrogen-frame state;
- no fitted normalization or direct native/COM state-vector equality.

## Completion boundary

Passing C1B/C2 closes the interface operator but PR-04 is promoted complete
only after PR-04C3 integrates the three snapshot lanes into one common
conservation ledger. Full recombination-history integration remains PR-05 and
FLRW history parity remains PR-06.
