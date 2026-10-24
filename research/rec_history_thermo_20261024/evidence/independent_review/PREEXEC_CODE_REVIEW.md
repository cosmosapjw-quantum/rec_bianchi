# R6 independent static implementation review

Reviewer: `/root/thermo_independent_review`; requested Astra/high, runtime model
identity unobserved. This continues the same theory/source review. No numerical
probe, scientific import, solve, native execution, IVP or old replay was run by
the reviewer. The reviewer changed only its own evidence documents.

## Inspected implementation

All seven prepared files were read: `scalar.py`, `inputs.py`, `source.py`,
`controls.py`, `primary.py`, `run_bounded.py`, and `figures.py`.
ARITHMETIC_ADDENDUM.md was read in full and accepted as the root's preexecution
clarification. Native parity and stable scientific evaluation are kept
separate, with no real-value anchoring trick or tolerance relaxation.

The scalar Dual path implements elementary forward derivatives. The complex
oracle uses ordinary complex arithmetic and the same source equations without
calling Dual propagation. Matrix-state derivatives are solved explicitly from
`s_k-M_k X`. All required coefficient blocks, 314 outgoing rows, 313 algebraic
state rows, ionization/proper-second ionization, number and paired energy
responses are exported. The source transcription preserves the original Gamma
ordering, native thresholds, fixed energy signs, virtual diffusion band and
Lyalpha/beta/gamma row mapping. The pure-H restriction uses the shared xe/xHII
seed and reuses already-computed state columns, without another solve.

The primary solve counter implements base 1 + tangent 6 + complex 6 + mixed
finite differences 12, with a hard ceiling of 25. Manufactured systems are
dimension at most 3 and use 6 floating RHS; independent exact rational Cramer
determinants require no linear solve. Escape controls use 14 depths and
60-digit references. Refusal controls do not invoke a source solve.

## Concrete findings and closure

1. **Complex escape cancellation.** A literal complex evaluation near tau=1e-6
   would compromise oracle derivative accuracy. Root resolved this before
   execution with the consistent stable scientific base in A1. Native small
   p/A polynomials remain, and large-branch polynomial/expm1 values are used
   consistently by analytic, complex and mixed-difference paths. Closed.
2. **Representation ownership.** The initial source signature omitted the
   .03 numerical representation boundary required by A1. The prepared source
   now includes this mask alongside native switches and rate stencils. Closed.
3. **Manufactured reference independence.** The initial exact reference used
   the same implicit derivative RHS as the tested float implementation.
   `exact_cramer` now differentiates independent Fraction determinant
   polynomials and applies the quotient rule. Closed.
4. **Pure-H roundoff criterion.** Root identified that the original pure-H
   comparison only applied the 2e-8 complex criterion. The implementation now
   includes independently seeded restricted coefficient/output comparisons
   and an implicit residual under the frozen 512-epsilon gross criterion.
   The original complex comparison remains. Closed.
5. **Inherited CPU hard limit.** The original parent hard limit of one second
   prevented its child from raising that inherited hard limit to 39 seconds.
   The prepared launcher retains parent soft limit 1 with hard limit 39 (or 9
   for figures), installs child limits, then lowers parent hard limit to 1.
   Full parent process CPU plus child CPU is now reported. Closed.
6. **Figure residual panel.** An interim figure implementation only contained
   scalar error annotations. The prepared figure code now includes a full
   lower panel showing outgoing and maximum-coefficient derivative residuals
   by primitive axis against the frozen 2e-8 criterion. This meets the frozen
   deliverable; no rowwise alternative is required. Closed after rereading
   the prepared figure code.

## Preexecution decision

No remaining material blocker to the prescribed primary computation was found
in the prepared numerical code, bounded launcher or figures after the above
fixes. The reviewed seven-file snapshot is recorded in
`evidence/execution/PREEXEC_STATIC.json`; the final figures.py SHA256 is
`55628b50783bd8d23cb514f4c06b999e9c9e92ff2e7f1ae373ba754656e97614`.
Root owns RUN_READY and scientific acceptance. R6 is a static execution-readiness
review, not evidence that numerical criteria passed. Actual raw results and
the first two PNGs remain pending review in this same reviewer session.

All H5 missing-input and full-coupled-H7 claim boundaries remain in force.
