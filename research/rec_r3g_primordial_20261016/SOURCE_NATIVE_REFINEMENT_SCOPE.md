# Source-native time-refinement scope (analysis only)

Status: `DERIVED`, `NOT_RUN`, `HOLD_RICHARDSON_UNRESOLVED`.

The original October 2012 HyRec `hydrogen.c` checks that `DLNA` is below
the smallest logarithmic photon energy separation. The frozen 311-bin grid
therefore permits a smaller time step; a frequency-bin change is not a
prerequisite for `h/2`. The current R3g trajectories and checkpoints,
however, are tied to `h=8.49e-5`, `izH0=18223`, their RT origin and all
source-stage thresholds. Halving only the abundance update is invalid.

For each new `h`, set `eta_RT=-ln(1+z_H0(h))`, `eta_j=eta_RT+j h`, and
`delta_b=ln(E_source,b/E_target,b)`. A retarded query has
`u_b=(eta_j-delta_b-eta_RT)/h`, `k=floor(u_b)`, `theta=u_b-k` and uses
`(1-theta)*out[k]+theta*out[k+1]`. Active queries require `k+1<=j-1`.
Before the source RT origin, the original thermal blackbody prehistory
applies. Ordinary bins use the next higher-frequency outgoing bin; virtual
bins 139, 270 and 310 use Ly-alpha/beta/gamma redward history. Ly-alpha
and Ly-beta incoming queries use virtual bins 140 and 271. Recompute the
RT origin, all stage indices, derivative seeds and full accepted photon
history for each `h`; never clone a coarse checkpoint into a refined run.

The source update `y[j+1]=y[j]+h*(5*f[j]/4-f[j-2]/4)` has smooth-branch
local defect `-2*h^3*y'''/3+O(h^4)`, hence second-order global behavior
under smooth assumptions. Photon two-neighbor interpolation has a factor
`theta_h*(1-theta_h)*h^2`; `theta_h` changes as `h` changes. RT onset
rounding and snapped source-stage transitions also change. An automatic
Richardson `p=2` assertion is therefore unjustified.

The minimum valid numerical experiment is a new independent Python run
from `z=8000` at `h/2`, with its own C numerical variant changing only
`DLNA`, each source/binary hash retained. At the current U4 endpoint,
coarse global index 19227 corresponds to refined indices 38454 (`h/2`)
and 76908 (`h/4`). Compare paired nodes and source stages on the common
grid. One refined level checks time-step sensitivity; three levels are
required before an empirical contraction assessment.

Predeclare identical-resolution C/Python parity criteria from U1-U4.
For three-level comparison define
`e_x=abs(delta_xe)/max(abs(xe_h4),1e-4)` and
`e_T=abs(delta_Tm)/max(abs(Tm_h4),1 K)` with a proposed prefix target
`1e-4` each. Preserve whole-grid differences `D01,D12`; an empirical
contraction gate may require `D12<=0.75*D01` and `2*D12<=1e-4`.
The factor `2*D12` is an empirical estimate, not a rigorous bound.
Record signed differences and observed order on smooth same-stage
segments; keep stage-boundary maxima in the overall error. Noncontraction,
sign oscillation, unstable order, or roundoff-level differences retain
`HOLD_RICHARDSON_UNRESOLVED`.

No refined source-native primordial H+He calculation was executed in this
work. The earlier synthetic `z=900` R3e hydrogen test is not evidence for
primordial convergence. Time refinement also does not remove 311-bin
frequency, atomic-table or source-closure errors.
