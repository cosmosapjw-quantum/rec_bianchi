# R117 REC stage-resolved SDIRK2
Baseline cb1685271e32223400df0817895952895087ef31.
H/He/W matched difference equation, same physical closure as R116-B.
g=1-1/sqrt(2), stage1 at eta+g*h, stage2 at eta+h.
The first-stage algebraic difference increment is used for the explicit
(1-g)h*F1 term of stage2. Nonlinear state simplex checks remain unchanged.
Stage inputs belong to the caller; no new kinetic HeIII or spectral source.
Weighted heat ledger uses physical stage rates plus explicit reference
correction, which is not physical heat. State reconstruction roundoff
and stiff raw residual remain measurable, not claimed exact.
The R116 BE root loop was factored into a common helper; one old 1024-step
H-history regression is byte identical.

141 Rust tests pass, including exact matched null, scalar stability function,
tiny heat increment, nonautonomous stiff manufactured analytic solution and
rejection of negative stiff pure-decay result. The latter illustrates that
L stability does not imply positivity. No clipping/adaptive retry.
21 real-reference/prescribed-direction cases: exact null for all three
windows, successful runs, H endpoint successive difference ratios
4.31677 (xe), 4.43514 (Tm); He 3.21289/2.046875; thermal xe at roundoff
floor, Tm 5.94824. Not universal or stiff-uniform second order.
The reference is piecewise interpolated, and stage order is one.
Source closure and reference interpolation are distinct error sources.

Commands:
 cargo test --release --locked --manifest-path rust/rec_microphysics/Cargo.toml
 cargo test --release --locked --manifest-path rust/rec_microphysics/Cargo.toml --examples
 cargo build --release --locked --manifest-path rust/rec_microphysics/Cargo.toml --example species_sdirk_history
 python3 research/r117_sdirk/verify.py rust/rec_microphysics/target/release/examples/species_sdirk_history NEW_OUTPUT
Original reference and provenance in research/r116_species_thermal.
Alexander 1977 doi:10.1137/0714068; partitioned coupling needs separate proof.
