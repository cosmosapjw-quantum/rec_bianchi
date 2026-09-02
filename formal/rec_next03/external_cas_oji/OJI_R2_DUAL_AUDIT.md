# REC-NEXT-03 OJI R2 Dual Audit

**Stage:** `REC_NEXT03_EXTERNAL_CAS_OCTAVE_JAS_JULIA_R2`

**Disposition:** `PASS_BOUNDED_EXTERNAL_FORMULA_ORACLE_R2`

**Authority effect:** `NONE`

**Scientific claim effect:** `NONE`

## Exact tested implementation

```text
implementation commit  bd7a703c8807145e137a65fdc079d947208ea0c8
implementation tree    84fc1a91da0e2b6b8e3138d951082fe52df6401d
workflow run           33690507393
workflow conclusion    SUCCESS
```

The run checked out the implementation commit directly. Engine and aggregate receipts bind the same forty-hex source head and explicitly reject GitHub's ephemeral pull-request merge commit as formula evidence.

## Failure-preserving lineage

The parent run `33678531383` reached Julia 1.12.7, Nemo 0.56.1 and Symbolics 7.39.0, passed `I01,I02,I04,I06,I07,I08,I09`, and then stopped at `I03` because `iszero(::BasicSymbolic)` produced a symbolic object in Boolean short-circuit evaluation. No algebraic disagreement was established.

R2 removes that fragile Boolean path. It verifies

\[
F_3(\chi)-\left(f_0+\eta\tau\right)=\chi Q_2(\chi)
\]

as an exact polynomial identity over \(\mathbb Q\) independently in JAS and Nemo. Hence the formal analytic series has constant term \(f_0+\eta\tau\), matching the direct Octave/SymPy limit without making Octave count as an independent algebra core.

The former combined event check is also split into:

```text
I07R  R_H=0 does not imply red-face speed=0
I07B  blue-face speed=0 does not imply R_H=0
I07D  exact red-minus-blue face-speed identity
```

and the hostile surface-merger mutation is split into `M05R` and `M05B`.

## PHYS-MATH audit

### Conventions and dimensions

- metric signature: `(-,+,+,+)`;
- spatial orientation: `epsilon_123=+1`;
- photon propagation direction: `e^a`;
- BASS outward-sky direction adapter: `n_sky^a=-e^a`;
- ray parameter: `s=c*t`, with dimension `L`;
- `ell` is reserved for angular multipole rank;
- `R_s,V_s` have dimension `L^-1`, while `R_t=c R_s` and `V_t=c V_s` have dimension `T^-1`.

### Surviving identities

The exact-head aggregate contains three execution axes and two independent algebra cores. Coverage is:

```text
three axes:
I01 I03 I04 I06 I07R I07B I07D I08 I09

two axes:
I02 I05 I10
```

The load-bearing zero-net-coefficient limit `I03` is no longer a single-wrapper result: JAS and Julia/Nemo independently verify its exact formal-series divisibility, while Octave/SymPy verifies the direct limit.

### Hostile controls

```text
three axes:
M01 M03 M04 M05R M05B M06 M07 M08

two axes:
M02
```

Every declared hostile mutation has at least two execution axes. Octave remains a SymPy-backed cross-language wrapper and is not counted as a third independent algebra core.

### Scope boundary

These results verify a bounded formula-oracle contract only. They do not materialize the source-identical ordered 26-direction physical face, validate the full moving-map interface, authorize a recombination-history provider, or establish numerical/scientific parity.

The homogeneous photon Formula SSOT remains a formula-only authority with cold non-tilted electron-rest Thomson scattering. Finite electron tilt, recombination/reionization implementation, truncation, line-of-sight integration, numerical evolution, parameter inference and likelihood claims remain outside that formula core.

## PHYS-MATH-CODE audit

### Genuine strengths

1. The original Julia failure is preserved rather than relabelled as a formula failure.
2. JAS and Julia/Nemo use distinct exact algebra implementations.
3. The Julia Project and generated Manifest are checked against exact SHA-256 values and exact direct-package versions.
4. Every engine receipt contains package or lock hashes, runtime versions, raw logs, normalized identities and hostile mutations.
5. Engine receipts and the aggregate are bound to the exact source head.
6. Aggregate admission requires all mandatory engines, two independent cores, exact critical-identity overlap, mutation coverage and authority-effect `NONE`.

### Remaining blockers

- The repository-wide `verify-durable-backup` workflow remains non-green because immutable historical evidence contains trailing whitespace and a blank EOF. Those bytes are outside this R2 change and are not silently normalized here.
- The OJI matrix does not establish the missing physical 26-direction face or the REC provider.
- It does not replace the BASS-owned common frame/photon FormulaIR authority.
- It does not validate production Rust/Python integration, performance, a full recombination history, or downstream REI consumption.
- A fresh connected Wolfram execution was attempted during closeout but the Wolfram MCP endpoint returned a network error. No fresh Wolfram PASS is claimed by this document.

## Literature role lock

Yang and Li, arXiv:2101.09674, is used only as a numerical-method cross-check for cancellation-free evaluation of the exponential-integrator function

\[
\phi_1(z)=\frac{e^z-1}{z}=\sum_{k=0}^{\infty}\frac{z^k}{(k+1)!}.
\]

It supports using a local series/scaling strategy near zero. It does not determine REC signs, source ownership, Git identity, admissible face data or provider status.

## Plot/CRAG reading

The aggregate coverage plots now have no one-axis identity. `I03`, `I07R`, `I07B` and `I07D` lie on all three execution axes. `M02` remains the narrowest hostile control with two axes because JAS is intentionally a polynomial oracle and does not claim the full exponential-sign differential check.

Surviving claim:

```text
THREE_EXECUTION_AXES_PASS_THE_DECLARED_BOUNDED_CONTRACT
TWO_INDEPENDENT_EXACT_ALGEBRA_CORES_COVER_ALL_CRITICAL_IDENTITIES
```

Rejected claims:

```text
THREE_INDEPENDENT_ALGEBRA_CORES
SOURCE_IDENTICAL_PHYSICAL_FACE
REC_PROVIDER_READY
PASS_REC_PHYSICAL_SPLIT
NUMERICAL_OR_SCIENCE_VALIDITY
```

## Next scientific node

After this append-only oracle closeout is durably read back, the next REC-owned scientific node is:

```text
REC_FACE_SOURCE_AUTHORITY_PREINTAKE
```

Its job is to obtain and validate causal, source-identical, ordered 26-direction data and provenance. It must not infer physical face data from the OJI formula checks.
