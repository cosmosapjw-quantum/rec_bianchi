# GEO01 implementation and execution boundary

## Preparation state

The lower-tier executor authored the owned `code/` modules. The requested tier
is gpt-6.1-sol/high; actual runtime model identity is unobserved. At C5, no
scientific code has been executed. Preparation consists of archive integrity,
unchanged input copying, metadata inspection, syntax compilation and byte
identity freezing. Original PB/KS/THERMO routines are never imported or replayed.

`inputs/SOURCE_IDENTITIES.json` lists all nine unchanged donor files and the
whole archive/member identity checks for PB01, nested KS01 and nested THERMO01.
The original 35,239,470-byte history is copied unchanged. The saved PB chart
carries the 313 queries, actual slopes, 626 endpoint slots and conservative
fixed-cell radii. Native target metadata comes from the original CSV. Source
routing is an outgoing-history index; target energies are separately built as
311 Ebin entries, E21, E31. No source index is used as a target energy index.

## New modules

- `geometry.py`: controlled diagonal-shear derivatives, independent exact
  rational degree<=4 sphere-rule moment proof, guarded source/direction domains,
  and stable shifted binary64 roots with 32-iteration and residual checks.
- `decimal_oracle.py`: original Delta-law bisection using 80-digit Decimal
  arithmetic and full exponentials. It does not call the shifted root or stable
  binary64 increment. Exact binary64 integer ratios seed Lambda, x, g and h;
  exact rational squared directions seed all 96 finite roots. An oracle-only
  strict bracket `Lambda/(1+2t), Lambda/(1-2t)` avoids endpoint rounding
  rejection. It does not enlarge the actual fixed-cell query domain.
- `primary.py`: native source identity binding, ten distinct refusing guards,
  both analytic shears, 313x14x4 finite roots, high-precision finite derivatives,
  five scalar Ks actions, and one exact Fraction interval-vector action.
- `run_bounded.py`: root RUN_READY and exact C5 source/input snapshot gate,
  pre-start 40CPU/120wall primary or 10CPU/30wall figures boundary, one thread,
  1GiB address-space cap, immutable attempt directories and no automatic retry.
- `figures.py`: reads saved primary results only; writes two PNG/PDF figures.
- `prepare.py`: syntax and byte identity preparation without scientific imports.

The first ordinary scalar root is charged before entry. Decimal roots and
operator/interval actions have separate hard counters. Binary64 roots store
iterations, residuals, query increments, anchored departures and total
occupations for every sampled configuration. A root failure saves the completed
partial array before returning. All failures preserve earlier files and counters.

## Numerical scales and scope

Analytic acceptance uses componentwise absolute operation grosses, never a
physical floor or max(1,...). First-derivative gross is
`(|g|+xW)*Lambda*sum(w*|v|)`. Second gross expands the q'' and Wien terms using
absolute products: `(|g|+xW)*(2Lambda*AA^2+2Lambda^2*(C+AA^2)) +
(x^2+x)W*Lambda^2*AA^2`, with `AA=sum(w*|v|)`.
The angular comparisons add the rule's weighted directional gross to the
absolute closed-expression gross where needed. Exact zero gross requires
exact zero error. The Decimal finite oracle uses the same stated absolute
operation scale, evaluated independently at high precision. Ordinary second
differences remain diagnostics and are never an acceptance substitute.

The anchored departure is `u0 + Delta u`. Total occupation is
`W(x) + u0 + Delta u = u0 + g*delta + W(x*exp(delta))`. Both signs are exported
separately. A negative total sample is returned as a scoped domain finding.
The lambda-zero branch returns the exact stored incoming departure.

The exact interval result encloses the action of saved K intervals on the
represented binary64 second-mean vector. It excludes new coefficient/libm
error, physical uncertainty and any total source derivative. The event uses
the same saved coefficient identity, retains direct incident subtraction,
and constructs atomic energy as the exact negative of radiation energy.

## Commands after root authorization

Run from any directory with the available Python interpreter:

```
python /tmp/rec_history_resume_20261026/rec_bianchi/research/rec_history_geometry_response_20261026/code/run_bounded.py primary
python /tmp/rec_history_resume_20261026/rec_bianchi/research/rec_history_geometry_response_20261026/code/run_bounded.py figures
```

Each execution writes its command, pre/post source snapshots, raw stderr/stdout,
child inclusive CPU, execution wall, high-water RSS and actual return status.
Primary hard caps: 17,528 binary64 scalar roots, 96 Decimal roots, 5 matvecs,
1 interval action, 0 RHS, 0 solves, 0 IVP, 0 native runtime/build. Root controls
the separate review and diagnosed-repair reserves; unused time is not approval.

C5 identities also bind this document and the frozen contract/theory. Do not
edit them between preparation and primary/figure execution. Amendments require
an explicit new preexecution snapshot and root review before a run.
