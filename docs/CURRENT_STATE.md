# Current state

- Durable stage: **PR-05C2A / v0.63**.
- Status: `PASS_PR05C2A_DIRECTIONAL_CONSERVATIVE_PILOT_BOUNDED_NO_GO_ANGULAR_THERMODYNAMIC_STIFFNESS_PR05C2B_NEXT`.
- Actual v0.48 Bianchi snapshot sequences now drive direction-resolved finite-volume frequency transport on the locked 35-state COM domain.
- Nine actual-background pilot lanes close number, face-energy, four-force, positivity and JVP gates for a bounded one-second implicit step on the frozen v0.50 COM grid.
- A full source-identical anisotropic coupling is not identified: original-HyRec native history is scalar, the COM face trace requires an explicit numerical closure, and source-temperature mode measures differ from the frozen COM grid by up to about 9.5 percent.
- The canonical macro collision stiffness number is O(1e9), so a source-temperature network adapter and a block preconditioner or asymptotic-preserving reduction are required before PR-05C2B.
