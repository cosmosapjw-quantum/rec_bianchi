# C3B0 — HYREC-2 native source lock

## Pinned source

- Repository: `nanoomlee/HYREC-2`
- Code-search commit: `09e8243d0e08edd3603a94dfbc445ae06cafe139`
- Native files are identified by the blob SHA values in
  `hyrec2_source_evidence.csv`.
- This bundle does not redistribute the complete upstream tables.

## Decision

The next Full Bianchi–HyRec implementation uses the **HYREC FULL native
representation**:

\[
(2s,2p)\oplus 311\ {\rm virtual\ photon\ states}.
\]

The immediate imported primitives are

\[
\alpha_{2s},\quad\alpha_{2p},\quad
\beta_{2s},\quad\beta_{2p},\quad
R_{2p\to2s},
\]

and

\[
E_b,\quad A_{1s,b},\quad A_{2s,b},\quad
A_{3s3d,b},\quad A_{4s4d,b}.
\]

The aggregate virtual-state block is sufficient for the total scalar
radiative-transfer and recombination calculation.

## Non-recoverability statement

HYREC-2 stores

\[
A_{3s3d,b}
=
\left(
\frac{d\Lambda_{3s}}{dE}
+
5\frac{d\Lambda_{3d}}{dE}
\right)\Delta E
\]

rather than separate \(3s\) and \(3d\) arrays. Therefore the following
cannot be reconstructed uniquely from the native tables:

- separate \(3s\) and \(3d\) profiles;
- channel-by-channel \(p_d^i\);
- channel-by-channel \(R_{2p}^{i,+}\);
- a one-to-one population of the provisional C3A channel template.

This is **not** a blocker for the aggregate scalar Full Bianchi–HyRec
operator. It is a blocker only for channel attribution or for claims
that distinguish \(3s\) from \(3d\).

## Mode policy

HYREC-2 `SWIFT` compresses the original FULL calculation into a fitted
correction to a scalar Ly-alpha escape rate. It is retained only as an
FLRW regression target. The anisotropic frequency-angle kernel must use
the FULL virtual-state representation.

## 3000 K source snapshot

At \(T_m=T_r=3000\,{\rm K}\), the pinned interpolation gives

\[
\alpha_{2s}=2.1008694041252002e-13\ {\rm cm^3\,s^{-1}},
\]

\[
\alpha_{2p}=5.5269148068796348e-13\ {\rm cm^3\,s^{-1}},
\]

\[
\beta_{2s}=1.6201858795609985e+02\ {\rm s^{-1}},
\qquad
\beta_{2p}=1.4207815282028739e+02\ {\rm s^{-1}},
\]

\[
R_{2p\to2s}=7.6848089250609939e+02\ {\rm s^{-1}}.
\]

The detailed-balance and interpolation-weight residuals are zero at the
working precision.

## Next executable stage

1. Parse the three native data files from a pinned checkout.
2. Assemble the native \(2+311\) sparse block.
3. Reproduce the scalar HYREC FULL Schur complement in the FLRW limit.
4. Replace each scalar virtual photon bin by the already-locked
   frequency-angle radiation state while retaining the same atomic
   rates in the hydrogen frame.
5. Run Bianchi II, V/VII_h and exceptional VI_-1/9 characteristic
   regressions.
