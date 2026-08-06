# PR-05 primitive HyRec trajectory-interface plan

## Goal and bounded entry stage

PR-04 has closed the source-conditioned split-domain **operator contract**. PR-05
must now construct the time-dependent primitive atomic/radiation trajectory
without undoing that separation of representations.

The first bounded stage is **PR-05A / v0.58 — BackgroundSnapshot/RadiationFeedback
schema and primitive-rate source lock**. It freezes ownership, state variables,
units and Jacobian blocks before any full trajectory is attempted.

## Fixed scope and conventions

- metric `(-,+,+,+)`;
- homogeneous scalar background;
- hydrogen orthonormal tetrad;
- ordinary frequency `nu` in Hz;
- explicit `c`, `h`, `k_B`;
- all 11 Bianchi types ultimately supported through one host adapter;
- finite tilt and nonlinear large shear;
- original HyRec and COM–KHW retain separate representation-local radiation
  states;
- no direct native-to-COM state remap, fitted normalization or silent
  high-resolution substitution.

## Scientific rationale

Original HyRec evolves the radiation field simultaneously with level populations
and free-electron fraction while exploiting the sparse structure of the full
radiative-transfer equations. PR-05 therefore cannot be a table lookup around
the v0.57 packet interface. It must expose the primitive atomic/radiation block
as a genuine time-dependent residual.

The canonical source already identifies the primitive rate inputs:

```text
interpolate_rates:
  Alpha[2], DAlpha[2], Beta[2], R2p2s

two-photon tables:
  A2s_tab, A3s3d_tab, A4s4d_tab

native compressed/transport terms requiring an ownership transition:
  Sobolev RLya
  A1s-driven diffusion
  completed/Schur-compressed Tvv
  scalar Dfplus and Dfplus_Ly history feedback
```

No compressed term is removed until its explicit split-domain replacement is
present in the same residual and conservation ledger.

## PR-05A — schema, source lock and ownership theorem

### A1. Typed public interfaces

Freeze the following immutable schemas:

```python
@dataclass(frozen=True)
class BackgroundSnapshot:
    tau: float
    cosmic_time_s: float
    mean_scale_factor: float
    H_s_inv: float
    q: float
    Sigma_ab: NDArray[float]
    N_ab: NDArray[float]
    A_a: NDArray[float]
    frame_rotation_a: NDArray[float]
    beta_H_a: NDArray[float]
    D0_beta_H_a: NDArray[float]
    chart_id: str
    bianchi_type: str
    normalization: str
    branch_flags: Mapping[str, bool]
    constraint_residuals: Mapping[str, float]

@dataclass(frozen=True)
class PrimitiveRateSnapshot:
    alpha_2s_m3_s: float
    alpha_2p_m3_s: float
    dalpha_2s_m3_s: float
    dalpha_2p_m3_s: float
    beta_2s_s_inv: float
    beta_2p_s_inv: float
    R_2p2s_s_inv: float
    A2s_s_inv: NDArray[float]
    A3s3d_s_inv: NDArray[float]
    A4s4d_s_inv: NDArray[float]
    source_hashes: Mapping[str, str]

@dataclass(frozen=True)
class AtomicRadiationState:
    native_radiation: NDArray[float]
    com_occupation: NDArray[float]
    x_1s: float
    x_2s: float
    x_2p: float
    x_e: float
    T_m_K: float
    beta_H_a: NDArray[float]
    interface_accumulators: Mapping[str, float]

@dataclass(frozen=True)
class RadiationFeedback:
    rho_gamma_J_m3: float
    p_gamma_Pa: float
    q_gamma_a_W_m2: NDArray[float]
    pi_gamma_ab_Pa: NDArray[float]
    Q_atom_mu_W_m3: NDArray[float]
    boundary_red_number_flux_per_H_s: float
    boundary_blue_number_flux_per_H_s: float

@dataclass(frozen=True)
class TrajectoryStepLedger:
    number_residual: float
    photon_atom_energy_residual_W_m3: float
    four_force_residual: float
    minimum_state: float
    entropy_production: float
    branch_events: tuple[...]
    source_hashes: Mapping[str, str]
```

The exact names may change during TDD, but dimensions, ownership and semantics
may not drift silently.

### A2. Primitive-rate source census

For each primitive coefficient, record:

- canonical source function and line range;
- source-table member SHA-256;
- original cgs/eV dimension;
- public SI conversion;
- degeneracy factors;
- dependence on `T_r`, `T_m/T_r`, `n_H`, `x_e`, `x_1s`, `fsR`, `meR`;
- detailed-balance reverse coefficient;
- derivative/JVP formula or controlled automatic-differentiation fallback.

Required parity lanes:

1. original C `interpolate_rates` versus Python adapter;
2. 80- to 120-digit independent interpolation references at selected knots and
   off-grid temperatures;
3. finite-difference versus analytic rate derivatives;
4. Saha/Planck equilibrium null.

### A3. One-owner removal/replacement matrix

Create a fail-closed matrix with columns

```text
term | current owner | replacement owner | removal condition | conservation
```

for at least:

- Ly-alpha Sobolev escape;
- native `A1s` diffusion;
- escape-compressed `Tvv`/Schur action;
- scalar `Dfplus`/`Dfplus_Ly` feedback;
- COM–KHW collision and recoil;
- red/blue interface packets;
- Hubble/redshift free streaming.

Hard gates:

```text
duplicate owner = 0
unowned term = 0
removed_without_replacement = 0
interface evaluation count = 1
opposite-sign application count = 2
pure interface atom source = 0
```

### A4. First primitive residual skeleton

At one source-conditioned snapshot, assemble

```text
R = R_native_transport
  + R_primitive_atomic
  + R_COM_collision
  + R_interface
  + R_thermatter
  + R_ledger.
```

The initial PR-05A implementation may freeze geometry during the step, but it
must consume a real `BackgroundSnapshot` and return a real `RadiationFeedback`.
No chart-internal class may leak into local microphysics.

Production nonlinear variables should remain log-positive for occupations and
nonnegative populations where appropriate. Population constraints such as

```text
x_1s+x_2s+x_2p+x_e+... = 1
```

must be enforced by a declared parametrization or algebraic constraint, not by
post-step clipping.

### A5. Bounded one-step gates

Use the locked source-conditioned lanes near `z=1300,1100,900` and require:

- primitive C/Python rate parity;
- Saha/Planck null;
- M-matrix or equivalent positivity evidence for the linearized atomic block;
- exact photon number and photon+atom energy ledger;
- analytic/JVP relative residual `<1e-8`;
- implicit residual/backward error `<1e-11`;
- strict positivity without clipping;
- exact restart;
- interface-off reproduction of v0.57;
- no future history endpoint;
- Bianchi-type-independent local microphysics at fixed hydrogen-frame state.

## PR-05B — time-dependent primitive atomic/radiation block

After PR-05A freezes the contract:

1. make the native radiation and real atomic populations dynamical;
2. replace the selected compressed terms jointly, not piecemeal;
3. derive the full analytic block JVP;
4. close Saha/Planck, number, energy, four-force, positivity and entropy gates;
5. compare dense, Schur and matrix-free actions without using Schur compression
   as the production time derivative.

## PR-05C — short adaptive trajectory

Integrate a short redshift interval with:

- adaptive implicit or IMEX stepping;
- exact event localization for every boundary-speed zero;
- conservative post-event restart;
- timestep refinement;
- checkpoint/restart parity;
- componentwise ledger at every accepted step.

PETSc `TS` is the primary integration target because it supports ODE/DAE
formulations, implicit nonlinear solves through SNES, IMEX ARK methods and event
handlers. SUNDIALS ARKODE/IDA remains an independent design/reference lane, not
a second production implementation in PR-05A.

## Explicit exclusions

PR-05 does not claim FLRW recombination-history parity until PR-06. It also does
not yet perform the all-11 production sweep, which remains PR-07 through PR-10.

## Durable outputs for PR-05A

- implementation and RED/GREEN tests;
- primitive-rate source/units registry;
- ownership/removal theorem;
- one-step residual and analytic JVP;
- CSV/NPZ numerical evidence;
- formalism, evidence ledger and adversarial audit;
- immutable ZIP and SHA-256 manifest;
- state/roadmap/handoff update;
- self-contained feature Git bundle and full recovery Git bundle.
