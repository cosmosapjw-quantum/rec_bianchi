# REC-DONOR-01 typed physical source contract

## 1. Objective and immutable boundary

This is the first REC-owned, test-first contract for a representation-neutral
primordial-recombination source owner.  The immutable parent is the FED-02
coordination closeout:

```text
commit  926e0c79a3fe7c3f5b24d5c5bb81304332def232
tree    ce0654041d097768fae4f6a52b23c2137558f7be
```

The future production path is:

```text
src/full_bianchi_hyrec/physical_source_authority.py
```

It is absent on this RED branch.  No file under `src/` may change in this
stage.  Tests, one fail-closed runner, one read-only workflow, and bounded
research/audit documentation are the entire allowed delta.

## 2. Physical conventions

The contract retains ordinary SI quantities rather than silently adopting
natural units.

| Quantity | Meaning | Unit/domain |
|---|---|---|
| `f` | total photon occupation | dimensionless, `f >= 0` |
| `E_gamma` | photon energy in the physical source frame | joule, `E_gamma >= 0` |
| `t` | physical proper/source time used by the donor | second |
| `eta` | primary spontaneous/stimulated emission coefficient | `s^-1`, nonnegative |
| `kappa` | primary absorption coefficient | `s^-1`, nonnegative |
| `chi=kappa-eta` | derived affine coefficient | `s^-1`, signed |
| packet rate | two-photon/Raman tracked photon-packet production | photon packet per H per second |

The source-frame convention is the declared hydrogen/atomic rest frame.  It is
not a local-observer sky frame.  The common BASS spacetime convention remains
`(-,+,+,+)`, but this local source object does not create or own a spacetime
background tensor.

For a local bosonic one-photon channel the exact pointwise law is

```text
C[f] = eta*(1+f) - kappa*f
     = eta - (kappa-eta)*f.
```

The primary nonnegative pair is authoritative; `chi` is derived and may be
negative.  The exact directional derivative is

```text
dC = (1+f)*deta - f*dkappa - (kappa-eta)*df.
```

No finite-difference fallback is admitted under an `ANALYTIC_JVP` declaration.
If `kappa > eta`, the finite equilibrium occupation is

```text
f_eq = eta/(kappa-eta).
```

If `eta > kappa`, the affine branch has no finite nonnegative equilibrium and
must not invent one.  At `eta=kappa=0`, the source-off action is exactly zero.

## 3. Local versus nonlocal source laws

A two-photon or Raman source is not a local pair at one photon energy.  Its
value depends on companion-frequency occupation and kernel support.  The
future API must therefore type it separately as a nonlocal photon-packet
kernel.  Two spectra may agree at one target energy and still produce different
packet rates because they differ at companion energies.

A packet rate is not an occupation rate.  The conversion requires an identified
packet-deposition binding containing at least the hydrogen density, phase-space
measure/normalization, and deposition-matrix identity.  The deposition receipt
must state that this conversion was applied exactly once.  A missing binding or
an application count other than one is a hard error.

This is the source-contract form of the existing repository firewall:

```text
packet rate per H per s
+ n_H / phase-space measure
+ identified deposition operator
-> occupation rate per s.
```

The notation does not authorize any particular discretization or physical face.

## 4. Identity and provenance contract

The source semantic identity must bind:

- repository and exact source commit/path/blob;
- content/payload SHA-256 and every input-table SHA-256;
- source algorithm identifier;
- species and quantum statistics;
- physical source frame;
- physical time basis;
- spectral coordinate and support, including endpoint/outside policy;
- background snapshot identity;
- trajectory identity;
- event-surface identity;
- restart-certificate identity;
- source law kind and JVP status.

Changing any load-bearing physical or provenance field changes the semantic
identity.  The object must report `VALIDATED_FACTORY_ONLY` construction.
Caller-supplied digest-shaped strings do not by themselves constitute source
authority.

## 5. Representation firewall

The physical source identity is independent of the receiving angular
representation.  Binding the same source to a full spectral/angular grid and
to spectral PSTF coefficients must retain one source semantic identity while
creating distinct representation identities.

A fixed 26-direction object is not an arbitrary-rank authority.  A declaration
combining `node_count=26` with `ARBITRARY_HIGH_RANK` must fail.  A future bounded
face would require a separately identified represented subspace, rank, nodes,
weights, basis order, exactness, conditioning, analysis/synthesis maps, and
mutation evidence.

Frequency-integrated `G` or `J` targets are also not interchangeable with the
frequency-resolved source.  They require an explicit target-specific moment-map
binding; absence of that binding is a hard closure error.

## 6. Frame and downstream-observer firewall

The REC donor exports source-frame quantities and metadata.  Applying a local
observer boost to the source owner is forbidden.  The local-observer sky
pullback belongs downstream to HTT; global matter/electron tilt and cosmic
transport belong to separately typed BASS physics.  No boost may be used to
replace missing source-frame or global-tilt physics.

## 7. Trajectory, event, and restart contract

A source instance is valid only for the exact trajectory binding used to create
its semantic identity.  At minimum the binding contains a background snapshot,
trajectory identifier, event surface, restart certificate, and physical time
basis.  Reusing the source with a different restart or event identity fails
closed.

This RED does not solve event differentiation.  In particular, it does not
claim that one-sided derivatives across ownership switches form a Frechet JVP.
A later event/saltation node must handle that separately.

## 8. Test matrix

The three controls verify the immutable parent metadata, the existing
nonauthoritative constant-pair primitive, and the repository physical-face and
unit firewalls.

The thirteen future behaviours are:

| Test | Load-bearing obligation |
|---|---|
| `test_future_module_exposes_minimal_typed_authority_surface` | bounded public API exists |
| `test_local_source_binds_physical_metadata_and_provenance` | species/statistics/frame/time/support/provenance bound |
| `test_source_identity_is_representation_neutral_and_mutation_sensitive` | physical mutation changes identity; grid/PSTF binding does not |
| `test_positive_primary_rates_and_signed_net_affine_rate` | nonnegative primary pair, signed derived `chi` |
| `test_stimulated_emission_action_and_source_off_control` | exact bosonic affine law and source-off limit |
| `test_equilibrium_detailed_balance_and_amplifying_branch_boundary` | finite equilibrium only on the admitted branch |
| `test_energy_threshold_support_and_units_are_explicit` | joule support and `s^-1` action |
| `test_local_analytic_jvp_is_exact_without_finite_difference_fallback` | exact analytic tangent |
| `test_two_photon_and_raman_kernels_are_nonlocal_not_local_pairs` | nonlocal law and no-JVP status kept separate |
| `test_packet_rate_requires_once_only_deposition_authority` | packet/occupation unit conversion applied once |
| `test_trajectory_event_and_restart_identity_fail_closed` | runtime source reuse is exact-binding only |
| `test_integrated_state_requires_explicit_moment_map_binding` | no implicit `G/J` closure |
| `test_no_universal_26_direction_authority_and_no_local_observer_boost` | no arbitrary-rank 26-face; no downstream boost in REC |

## 9. Expected RED

```text
classification             PASS_EXPECTED_REC_DONOR01_TYPED_PHYSICAL_SOURCE_RED
tests                      16
intentional failures       13
passing controls            3
errors                       0
skips                        0
future production path      absent
production source delta     none
worktree                    clean
```

An import error in an existing dependency, a missing interpreter package, a
collection error, a changed production file, a dirty worktree, or a different
failure set is not an admissible RED.

## 10. Scope exclusions

This stage does not provide:

- authenticated incoming physical source values;
- a source-identical angular face;
- BASS projection or state-container wiring;
- a BASS background provider;
- a REI provider or REC--REI splice;
- finite electron tilt;
- local-observer processing;
- integrated-state closure;
- physical event/saltation JVPs;
- provider export, likelihood, or science promotion.

The terminal claim remains:

```text
NO_REC_PHYSICAL_SOURCE_AUTHORITY
NO_SOURCE_IDENTICAL_PHYSICAL_FACE_ADMISSION
NO_REC_PROVIDER_EXPORT
NO_PASS_REC_PHYSICAL_SPLIT
```

## 11. Next node

Only after exact RED execution and readback:

```text
REC-DONOR-02_MINIMAL_REPRESENTATION_NEUTRAL_SOURCE_GREEN
```

The GREEN implementation should remain standard-library-only and add exactly
one production module before any receiving representation or solver coupling is
considered.
