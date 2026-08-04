# Proposed background adapter contract

The radiation/atomic solver must not import chart-internal state classes.
It consumes a stable snapshot:

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
```

The radiation solver returns:

```python
@dataclass(frozen=True)
class RadiationFeedback:
    rho_gamma: float
    p_gamma: float
    q_gamma_a: NDArray[float]
    pi_gamma_ab: NDArray[float]
    Q_atom_mu: NDArray[float]
    boundary_red_flux: float
    boundary_blue_flux: float
```

The monolithic residual owns conversions between normalized and physical quantities.
The local atomic kernel receives only hydrogen-frame characteristics and physical densities,
so it remains independent of Bianchi type.
