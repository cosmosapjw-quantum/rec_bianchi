# Preserved first independent-validation failure

Original command: `python code/independent_validate.py --source <locked> --module <locked> --points <primary-80> --out <validation>`.
Exit code 1. `AssertionError` at `assert Decimal(r120['adjoint_vs_primal_error']) < Decimal('1e-90')`.
Cause: the reused adjoint in RESPONSE01 is stored at 80-digit precision, while
this fresh selected primal was computed at 120 digits. The mixed-precision
adjoint/primal discrepancy is therefore limited by the inherited 80-digit
adjoint and cannot be required to satisfy 1e-90.
Targeted repair: validate the inherited adjoint comparison against a correctly
identified mixed-precision 1e-70 gate, while separately comparing genuine
120/80 primal solutions to 1e-65 and float64 SciPy to 1e-9. No change to
PRIMARY 80-digit gates or scientific source. This is a precision-provenance
correction, not tolerating a previously failing source mismatch.
