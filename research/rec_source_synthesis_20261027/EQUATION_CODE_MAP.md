# C2 — equation, data and code correspondence

Paths below are relative to this unit unless explicitly prefixed with another research unit. The workers confirmed the named symbols during implementation preparation. They are the binding targets; actual C5–C8 outcomes will establish execution.

| Quantity / operation | Source and convention | Code target |
|---|---|---|
| HD level energy and radiative frequency | Existing `hd_adapter/lamda_hd.py::load_hd`; `SourceNumber` keeps literal Decimal. Energy in cm^-1, frequency in GHz | `hd_joint/run_diagnostic.py::main` loads existing parser; no qualified line consumer bypass |
| Exact delta, xE | h=6.62607015e-34 J s, c=299792458 m/s, kB=1.380649e-23 J/K, exact SI definitions; source energy×100c and GHz×1e9 | `hd_joint/joint_diagnostic.py::exact_number`, `joint_thermal` |
| Stable paired flux imbalance I | tanh(delta/2); upward-minus-downward convention | `joint_thermal` |
| Stable source deviation D | expm1(-delta)/[-expm1(-xE)] and ratio1+D; mean-intensity Einstein convention A/B=2h nu^3/c^2 | `joint_thermal` |
| Independent thermal reference | Decimal80 exp(-xnu)/(1-exp(-xnu)) and exp(-xE)/(1-exp(-xnu)); original exponential source ratio | `hd_joint/decimal_reference.py::decimal_reference` |
| HD source gap | Existing `line_frequency_gap_Hz`, `transition_qualification` maintain35Hz gate | `hd_joint/run_diagnostic.py::main` records gate separately |
| Source/collider invariance | Original dataset9levels,8lines, colliderIDs2/3; no collision weighting | `hd_joint/targeted_controls.py::run_controls` |
| Native represented clock | `hydrogen.c::interp_Dfnu`, floor((eta-eta0)/dlna); eta=ln(a), exact-real reconstruction from binary64 eta0,dlna | `history_remainder/remainder.py::rational`, `PiecewiseLinear` |
| Query/source binding | SOURCE_CONTEXT query_hex, incoming_index, source_index, cell, sample left/right; outgoing_virtual then outgoing_lyman | `history_remainder/primary.py::bind_and_run` |
| P(q), directional slope | Linear value; right slope for positive travel, left for negative; d=0 explicit | `PiecewiseLinear.value`, `cell_slope`, `directional_slope` |
| Finite retiming remainder | Direct value difference versus independent signed jump sum; excludes start atom; target weight0 | `PiecewiseLinear.retime`, `jump` |
| Chord remainder | Direct difference versus negative Peano jump sum; absolute-jump bound | `PiecewiseLinear.chord` |
| Domain and sign controls | Strict increasing knots, causal rightendpoint excluded, hinge/cancellation/start/target/zero controls | `history_remainder/controls.py::run_controls` |
| Display | Saved derived JSON/CSV only; no recomputation of native history | each subtree `plot_saved.py` |
| Resources | One thread,2GiB; HD60CPU/180wall, history120CPU/240wall primary | `hd_joint/run_bounded.py`, `history_remainder/bounded.py` |

## Physical scope through this path

The HD diagnostic takes level-derived Boltzmann populations and frequency-derived Planck radiation at the same specified T. The common positive rate prefactor cancels from I; no absolute collider mixture or arbitrary normalization is introduced. This diagnostic is callable even when the source bridge gate fails, because its purpose is to measure that mismatch. It does not invoke a previously qualified production consumer to evade that gate.

The history module consumes occupation departure in the original native Wien-reference convention and eta clock. It does not evolve an IVP or translate to proper time. The original query nominal values are compared with the new exact-real reconstruction and their discrepancy is reported as a representation anchor. This is separate from the old geometric-knot anchor.

H5 physical bound composition remains conditional on actual endpoint-error enclosures derived from physical defect, a certified positive ODE tube, stability and curvature inputs. No such missing constants are synthesized by the above path. `E_upper < rho_lower` stays strict. The old inverse-matrix residual rho is not an ODE tube radius.

## Impact boundary

Only `hd_joint/` and `history_remainder/` implement new computations. Earlier parsers, H5 producers/consumers, native C, PB01, KS01 and GEO01 remain unchanged. Parent integration adds reports and scoped DAG observations. The original88 contracts and other owner returns are preserved.

