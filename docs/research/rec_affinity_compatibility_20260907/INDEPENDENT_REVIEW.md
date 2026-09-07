# Independent read-only review

Reviewer: `/root/affinity_review`, a separate fresh-context Codex reviewer.
One review covers physics/math and implementation/provenance. Neither scientific
suite was rerun. No source edit, publication or secondary review was performed.

Reviewed PR77 source: 4125f7f39b29b710ad6ca673520ae46a426b564f.
Reviewed new scientific source: 7eb64cb8d65c1fa22f49c019f3c8ce4fb1d22bdc.
Reviewed accompanying current worktree documents, evidence and corrected figure.

Disposition: no P0/P1 blocking findings on either axis.

- The pair-affinity necessity/sufficiency proof, entropy signs, conservation
  ledgers and counterexample interval are correct under the stated fixed-measure,
  single-reaction, positive-state, g=1 assumptions.
- Exact manufactured fixtures are distinguished from binary64 inputs. The
  physical claim ceiling remains intact.
- Inspected source blobs and commit/tree identities match the executions.
  Decoded PR77 log matches RESULT_EXTRACTED.json. The three log wrappers match
  their recorded received-log byte counts and SHA-256 values.
- New stdout, CSV and payload agree. The corrected figure represents the results.

Nonblocking coverage qualifications incorporated into MAIN_REVIEW_KO:

1. PR77's 3-state × 8-direction high-precision JVP test is chi-only;
   log_control has one base/mixed-direction comparison.
2. PR77 test_10 central-differences the independent reference against its own
   derivative. API JVP coverage comes from test_02/test_03.
3. The new entropy difference holds the API vector field direction fixed and
   establishes an instantaneous directional derivative, not time integration.

After review, SVG-only serialization whitespace was repaired. Path tokens, text
labels and PNG bytes remained unchanged; evidence is in FORMAT_REPAIR.json.
The scientific script, source, tests and numerical payload were unchanged.
No numerical repair or additional review was warranted.
