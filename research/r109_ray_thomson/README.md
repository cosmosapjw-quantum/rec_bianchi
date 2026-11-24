# Cold-electron Thomson visibility along a supplied ray

This path consumes a direction history from the geometry solver and one electron
material history over a finite interval. The final row is the receiver. The
propagation direction `e` and matter velocity `beta=v/c` use the same local
normal orthonormal tetrad. The signature is (−,+,+,+). In normal proper time,

```text
dτ/dt = c σ_T n_reference,rest x_e D
D = γ (1 − β·e),    n_e,rest = n_reference,rest x_e .
```

The code takes `c σ_T` from the original F05 constants and converts cm³/s to
m³/s. For a hydrogen-normalized gas, `x_e = (n_HII+n_HeII+2 n_HeIII)/n_H`.
An REI producer can supply its independently evolved total electron density
through its published ratio to the reference. Select one total-density owner
per interval. A cold-electron Thomson collision uses the Thomson cross section
in the electron frame. Re-emission, polarized redistribution, energy-dependent
scattering, chemistry evolution and the construction of the null trajectory
belong to their respective operators.

## Finite-cell integral and Jacobian

On each normal-time cell the model interpolates `ln n_reference` and
`q=x_e D` linearly. Orient the integration variable from the higher-density
endpoint to the lower one and set `λ=ln(n_high/n_low) ≥ 0`.
With `M_j=∫₀¹ s^j exp(−λs) ds`, the exact exposure for this interpolant is

```text
Δτ = c σ_T Δt n_high [(M_0−M_1) q_high + M_1 q_low].
```

Both weights are positive. A Taylor expansion evaluates the moments for small
λ. For λ ≥ 1/2 an exponential recurrence suffices. The library also evaluates
the directional derivative of this same cell integral with respect to
`δ ln n_reference, δx_e, δβ, δe` on a fixed time grid. The direction tangent
satisfies `e·δe=0`. In particular,
`δD = D γ² β·δβ − γ(δβ·e+β·δe)`. Differentiating the exponential need only add
the second moment. The integral includes any supplied change in photon direction;
time shifts of the emitting or receiving event require separate endpoint terms.

Exposure accumulates backwards from τ=0 at the final sample. The last-collision
mass in one bin is `exp(−τ_near)·[−expm1(−Δτ)]`. Its sum over the path is
`1−exp(−τ_total)`. An optically thin bin retains its own Δτ even when the
cumulative optical depth rounds to the adjacent value.

## Run

```sh
cd rust/rec_microphysics
cargo test --offline
cargo build --offline --release --bin rec_ray_thomson
target/release/rec_ray_thomson ray.tsv > visibility.tsv
cd ../..
python3 research/r109_ray_thomson/replay_f08.py \
  rust/rec_microphysics/target/release/rec_ray_thomson
```

The input is one ray per whitespace-separated file, with this header.

```text
normal_t_s n_reference_rest_m3 electrons_per_reference beta_x beta_y beta_z dir_x dir_y dir_z
```

Optional appended columns `N b` may carry the producer's epoch and geometry
metadata. The binary integrates the supplied proper clock and tetrad directions.
At least two strictly chronological samples, a positive reference density,
nonnegative yield, a finite subluminal velocity and a unit ray are required.
For a vacuum interval use a positive reference and zero yield at both ends.
To use a known total with no material reference history, select a positive
constant reference in m⁻³ and set `x_e=n_e,rest/n_ref`; this specifies linear
interpolation of the directional total density. The library exposes
`RaySample::from_ion_densities`, `integrate` and `integrate_tangent`.

## Validation and scope

The frozen F08 oracle covers four histories with 160 accepted gas steps each
and 128 independently supplied directions. It prescribes comoving electrons on
FLRW and diagonal Bianchi I and uses an exponential reference density with
linearly varying electron yield. The replay constructs each ray's normal-tetrad
directions from its original conserved momenta and scale factors, and compares
the new Rust exposures with the archived temporal and redshift-selected
observables. The selected-redshift comparison uses the archived emission times.
The JSON records the SHA-256 hashes and errors. The test suite additionally
checks a moving slab, transverse propagation, reversal, zero electrons, highly
opaque and optically thin cells, bin subdivision, invalid inputs, the full
fixed-clock tangent, and representable long-clock exposures at small density.
Geometry/velocity histories from other Bianchi families can use the same
interface; such inputs require their own family-specific validation.
