# PR-05C2C1B2B1E1C split-domain replacement plan

## Objective

Replace overlapping full-native/interior-COM ownership by an explicit
exterior-native / interior-COM / interface-crossing contract at the locked
\(z\simeq1100\) Bianchi-II state.

## C1. Exact support registry

Use the canonical point-spike indices `136..143` as the interior native set.
Do not infer finite native cells.  Freeze the two cross edges `(135,136)` and
`(143,144)` as interface-owned processes.

## C2. Native exterior operator

Construct an exterior-only primitive native matrix.  Eliminate the interior
virtual variables with a source-derived Schur complement or expose them as COM
source variables.  Prove primitive/exterior-Schur parity on exterior observables.

## C3. Interior atomic deposition

Route one-photon and canonical two-photon/Raman real--virtual source terms whose
point support lies inside the COM domain into the COM representation.  Preserve
nonnegative paired rates, detailed balance, and analytic JVPs.

## C4. Cross-interface diffusion

Represent the two crossing diffusion edges as a single-owner interface packet.
Apply equal and opposite photon-number and exact photon-energy entries to the
adjacent representations; pure representation crossing has zero atom source.

## C5. Owner swap gate

The old full-native terms may be disabled only in the same commit that provides:

- replacement residual;
- analytic JVP;
- photon-number, energy, and four-force ledger;
- restart serialization;
- primitive/direct/Schur parity;
- interface-off and FLRW-limit parity.

## C6. Return to the dynamic macro

Only after C1--C5 pass may the source-derived v0.73 parent and the v0.74 COM
root be coupled to dynamic atomic populations and typed history.  Preconditioner
and Rust work remain deferred until that full physical residual is admissible.
