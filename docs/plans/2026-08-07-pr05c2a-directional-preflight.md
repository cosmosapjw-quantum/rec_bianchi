# PR-05C2A directional coupling preflight implementation plan

> Execute with TDD and durable evidence. This stage must not claim a fully source-identical anisotropic native/COM trajectory unless the angular boundary state, finite-volume face trace, source-temperature COM measure and macro-stiff collision solve are all identified and verified.

## Goal

Connect the locked v0.48 `BackgroundSnapshot` characteristics to the v0.50 35-state COM--KHW collision domain in a conservative direction-resolved pilot, then determine whether the available canonical sources identify the full adaptive coupling requested by PR-05C2.

## Scope

- actual Bianchi II, class-B `VI_h` and exceptional `VI_-1/9` snapshot sequences;
- the positive-weight angular grid stored with v0.48;
- the locked 35-state v0.50 COM--KHW network;
- scalar original-HyRec red/blue boundary occupations near `z=1300,1100,900`;
- conservative upwind frequency transport, exact face-energy ledger and zero computational-interface atom source;
- bounded implicit collision/transport pilots and analytic JVP;
- identifiability and stiffness audits.

Out of scope: inventing an angle-resolved native boundary field, silently treating a cell average as a canonical face trace, retuning the frozen COM measure to a new Doppler temperature, or claiming an unpreconditioned canonical macro solve from a one-second pilot.

## Tasks

1. Add failing tests for interpolation of locked background sequences, source-derived boundary roots, conservative frequency transport, exact energy accounting, JVP parity and angular scalarization non-uniqueness.
2. Implement `BackgroundSnapshotSequence` with Hubble-normalized local-rate rescaling and source-root localization.
3. Implement a finite-volume `ConservativeFrequencyLiouville` operator on the locked 35-state intervals.
4. Implement the log-positive collision/transport implicit pilot and analytic JVP.
5. Add identifiability audits for angular rank, face reconstruction, source-temperature mode measure and macro collision stiffness.
6. Run nine source-conditioned pilot lanes, record componentwise number/energy/four-force/entropy/JVP evidence, and issue a bounded no-go whenever a source-identical full coupling is not identified.
7. Produce formalism, research-harness evidence, immutable artifact ZIP, state ledgers, verification receipts and Git bundles.

## Hard gates

- all three locked Bianchi sequences have source-derived red/blue roots;
- Hubble-normalized geometry is invariant under local source-H rescaling;
- discrete global photon-number residual is at roundoff;
- exact face-energy identity closes without assigning an atom source to a representation crossing;
- analytic JVP relative discrepancy is below `1e-8`;
- all one-second implicit pilots are strictly positive and converge;
- collision entropy production is nonpositive;
- any underidentified angular/face/temperature measure or macro stiffness is recorded as a blocker, not fitted away.
