# REC impact analysis and corrected DAG

## 1. BASS changes since the REC R5D closeout

BASS has advanced beyond the REC-owned trusted-payload gate:

```text
R5D trusted native gate
→ R7 dual-adapter RED
→ R8 constant-pair dual adapter GREEN
→ R8B trusted-native nonregression
→ R9 finite-rank nonaxisymmetric parity RED
→ R10 bounded scalar parity GREEN
→ R10A projection-authority hardening RED
```

The R10 numerical evidence is useful but narrow:

```text
scalar intensity
angularly constant photon/boson source pair
real spherical harmonics on dOmega
finite rank L=0,1,2,3,4,6,8
same implementation used for synthesis and projection
no solver-loop evolution
```

The post-GREEN audit correctly blocks production REC coupling until R10A binds the realized basis matrix, sample layout, actual unit-field vector, time basis, rate divisor, factory-only receipts, use-time integrity, rank evidence ceiling, and continuous-positivity semantics.

### REC impact

* Keep `SourceAuthorityBundle` and positive `(eta,kappa)` ownership unchanged.
* Do not bind a physical donor to the current R10 projection object as a final authority.
* Donor development may continue independently of R10A.
* The eventual REC→BASS handoff must consume a certified projection identity, not a caller-invented SHA string.
* The old source-defined 26-direction face cannot remain the universal target for arbitrary higher rank.

## 2. BASS background line

BASS BG-02 has been downgraded from a production/source-GREEN interpretation to a component-formula oracle with a native xTensor Gauss–Codazzi bridge still RED. The current module does not yet provide a trusted background Einstein provider.

### REC impact

REC may develop rate/source physics against a typed abstract background trajectory interface, but it must not claim an end-to-end background-coupled physical run or freeze BG-02 component associations as the production tensor authority.

## 3. REI changes

REI's mathematics line now derives generic homogeneous spatial Ricci curvature and the homogeneous divergence of a constant STF tensor from the locked commutator and Koszul construction. It includes class-A controls and class-B mixed-sign mutations.

This is a valuable independent oracle, but its own PR states that the four-dimensional Gauss–Codazzi signs, Einstein constraints and propagation are not closed. The runtime lane also remains before the first canonical interval.

### REC impact

* No REC formula ownership changes.
* Record REI M1 as `INDEPENDENT_ORACLE / authority_effect=NONE`.
* Do not consume a REI provider artifact yet.
* Do not make REC donor work wait on REI runtime reconstruction.
* Reserve the future REC→REI splice for exact provider artifacts and time/frame identity, not copied source.

## 4. HTT changes

HTT has a scoped exact full-sky local-observer Lorentz pullback and continues processed cut-sky/response and tensorized MES work. All current HTT lines explicitly withhold global matter-frame tilt, Bianchi attribution and physical REC/reionization feedback.

### REC impact

* Local observer boost remains downstream, output-only HTT functionality.
* REC exports cosmic/source-frame quantities and must not apply the local observer boost internally.
* REC source identities should expose enough frame metadata for BASS/HTT to apply downstream transforms once, not twice.
* HTT response or MES results do not authorize a REC source approximation, closure, or 26-direction face.

## 5. Corrected REC DAG

```text
REC-R5D trusted BASS payload gate                         COMPLETE
FED-02 four-repository reconciliation                    COMPLETE ON PUBLICATION

Parallel lane A — BASS projection authority
  R10 bounded scalar parity                              COMPLETE
  R10A expected RED                                      CURRENT UPSTREAM
  R10A GREEN                                             BLOCKED

Parallel lane B — REC physical donor
  REC-DONOR-01 typed physical source contract RED        OPEN AFTER FED-02
  REC-DONOR-02 minimal donor fixture GREEN               BLOCKED ON RED
  REC-DONOR-03 trajectory/event/JVP provenance           BLOCKED

Parallel lane C — background/provider dependencies
  BASS BG-02 native xTensor bridge                       BLOCKED
  REI first canonical interval/provider                  BLOCKED
  HTT local-observer response                            DOWNSTREAM ONLY

Join
  R10A GREEN
  + REC donor fixture and source identity
  + typed BASS background snapshot
  → REC-BASS-SOURCE-BINDING-RUNTIME-VALIDATION

Then
  representation/state-container parity
  → source-defined physical face
  → REC provider export
```

## 6. Next REC contract

The next REC-owned production-adjacent work should be test-first and representation-neutral. It should require:

1. physical source pair or nonlocal kernel with species, statistics, frame, time basis, energy/frequency support and provenance;
2. exact source identity independent of angular representation;
3. trajectory/event dependence and analytic JVP or fail-closed declaration;
4. source-off, equilibrium/detailed-balance, threshold and positivity controls;
5. no assumption that a fixed 26-node face reconstructs arbitrary rank;
6. no local-observer boost;
7. no integrated-state closure without a declared moment map;
8. an explicit boundary between one-photon local terms and two-photon/Raman nonlocal terms.

Production BASS wiring remains forbidden until the upstream R10A authority and background snapshot gates are available.
