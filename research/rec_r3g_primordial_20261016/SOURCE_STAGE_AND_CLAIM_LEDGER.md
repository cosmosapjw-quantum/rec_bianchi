# R3g source-stage and claim ledger

Source baseline: original October 2012 HyRec ZIP SHA-256
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`;
REC PR #98 HEAD `7f7ca8d3d497b9b9ef90b46b33f8bd6f981b17b1`.
The cosmology is the R3f baseline, with `T0=2.7255 K`,
`omega_b h^2=0.0224`, `omega_m h^2=0.14309694000000003`,
`YHe=0.2454`, and `Neff=3.03821934419124`.

## Original source variables and clock

Metric signature is `(-+++)`. In the FLRW limit,
`ds^2=-c^2 dt^2+a(t)^2 d x^2`, `1+z=a^(-1)`, and
`d ln(a)/dt=H`, so `dt/dz=-1/[(1+z)H]`. The original source
integrates on `h=DLNA=8.49e-5`, `z_i=8001 exp(-i h)-1` from `z=8000`.
It writes output through cubic interpolation of its own internal history.

`x_e=n_e/n_H`, `n_H=n_H0(1+z)^3` and
`f_He=YHe/[3.97153(1-YHe)]` are source conventions. The He abundances
`xHeI`, `xHeII`, `xHeIII` are number densities divided by `n_H`;
`x_e=xHII+xHeII+2*xHeIII`. The source's H and He ion fractions do not
all become independent ODE variables at once.

| Source phase | Source location | State and closure |
| --- | --- | --- |
| HeIII to HeII | `history.c:508-515`, `helium.c` | Algebraic He Saha, H fully ionized, `Tm=Tr`; exit when `xHeIII<=1e-8`. |
| HeII to HeI | `history.c:280-317,525-537` | He post-Saha, then source predictor ODE; H Saha closure; `Tm=rec_Tmss`. Ends at inclusive `izH0`. |
| Joint H/He | `history.c:326-410,546-556` | He predictor ODE, H post-Saha then H predictor ODE; FULL H atomic RHS and causal photon history; stop when `xHeII<=1e-6`. |
| H, thermal steady | `history.c:417-450,559-568` | Neutral-He source cutoff; H post-Saha/ODE and `rec_Tmss`; stop at source temperature threshold. |
| H plus thermal ODE | `history.c:458-485,575-584` | Source predictor on `x_e,Tm`; FULL switches to EMLA at source RT boundary. |
| Late H | `history.c:586-597` | Peebles closure below table/temperature bounds. |

FULL hydrogen uses 2 real levels (`2s`, `2p`) and 311 *algebraic* virtual
photon bins. The existing Python instantaneous source solves their block
system by banded Schur elimination. Only outgoing columns from accepted
steps may enter subsequent retarded photon interpolation. Source trial
evaluations during H post-Saha alter a scratch future column in C; the Python
trajectory must discard such candidate outgoing values and keep the accepted
history length unchanged. The spectrum is a distortion from the Planck
reference, so a blackbody before the original H RT start has zero distortion.
This is distinct from erasing an already produced history at `z=900`.

Temperature `Tr=T0(1+z)` is in kelvin; hydrogen atomic routines convert to
eV with source `kBoltz`. The source hydrogen number density is converted
from `m^-3` to `cm^-3` by `1e-6` at the atomic-rate call. Proper-time
opacity `c sigma_T n_e` has units `s^-1`; its `ln(a)` coefficient is
`c sigma_T n_e/H`.

## Verified bounded result and ceiling

U1 independently integrates 18,224 source-grid rows, indices `0..18223`,
from HeIII Saha through the end of the HeII-to-HeI phase. The original-C
oracle calls the unmodified `rec_get_xe_next1_He`, `rec_HubbleConstant`, and
`rec_Tmss`. Its pinned final receipt is
[`helium_stage_001/verification.json`](helium_stage_001/verification.json).
Independent scientific review admitted **U1 scoped PASS**: maximum
`x_e` relative error `2.1756662172518215e-16`, maximum `Tm` relative error
`0`, maximum absolute `xHeII` error `1.3877787807814457e-16`, and
common-input He RHS scaled error `1.0331312128564999e-12`.
The first actual He source-predictor update is at index `12084`.

An earlier verifier failure at index `7733` remains a diagnostic:
the independently propagated He state differs by one binary64 ulp near
equilibrium, amplifying the trajectory-to-trajectory He RHS difference to
`4.865929668126399e-6`. The same-input RHS map passes its fixed
`2e-10` criterion. This does not establish a full primordial history or
time-step convergence.

U2 continues the independent U1 endpoint through 8 accepted H+He FULL
source-grid steps (global state indices `18223..18231`). Its final reviewed
receipt is [`full_start_011/verification.json`](full_start_011/verification.json).
The Python trajectory performs 32 FULL atomic evaluations, commits 8
outgoing virtual/Lyman columns, and discards 24 post-Saha trial outputs.
Independent original-C integration agrees on all 9 states and all 8 source
flags. The maximum absolute `xHeII` difference is
`5.421010862427522e-20`; printed `xHII`, `xe`, and `Tm` agree exactly.
All 2,488 outgoing virtual, 2,488 virtual-bin-average, and 24 Lyman
comparisons pass the fixed photon criterion. The largest tolerance ratios
are `5.031786161775726e-6`, `5.1232699759945545e-6`, and
`2.5375235708045017e-6`, respectively. The U2 independent review
admitted **scoped PASS** only for these eight steps. Source-native longer
continuation and a `z=20` result remain unverified.

U2 had classified verifier failures before its final receipt. In particular,
an earlier C spectrum label reversal made the outgoing/average comparison
invalid, and one startup `MemoryError` run (`full_start_008`) has only a
tool-transcript traceback, with no durable stdout/stderr or exit code.
`full_start_009` has a durable memory-limit failure receipt. The validated
run sets BLAS/OMP thread counts before NumPy import and retains the original
2 GiB address-space limit. No missing `_008` receipt is reconstructed.

U3 resumes the independently computed U2 state and causal photon history.
The NCP run accepted 374 additional source-grid steps, from global index
18231 to 18605, and evaluated the Python FULL atomic source 1,497 times.
The first HeII cutoff (`xHeII<=1e-6`) occurs at global index 18603,
`z=1648.004601195495`; the run then accepts exactly two H-only steps.
The final state is `z=1647.72462398495`, `xe=xHII=0.9979258049614494`,
`xHeII=0`, and `Tm=4493.594294033827 K`. H post-Saha remains active.
The raw NCP archive was returned byte-identically to the owner PC (SHA-256
`6160a4810eda1edeb2db5c96ffd342202d87bb223c91d0d9bdf3331bc44a2527`).
The compact run receipt is [`continuation_001/verification.json`](continuation_001/verification.json)
and the return receipt is [`continuation_001/NCP_RETURN.json`](continuation_001/NCP_RETURN.json).

An independent reviewer recomputed all 374 original-C/Python state and RHS
comparisons and all 233,750 spectral values from raw output and admitted
**U3 scoped PASS**. Maximum scaled errors were `1.11247806e-16` for `xe`,
`7.08642520e-11` for H RHS, `9.05525654e-16` for He RHS; maximum photon
tolerance ratio was `0.00121115801`. The largest Schur normalized residual
was `7.12302942e-16`. The accepted outgoing history remained causal; the
endpoint diagnostic was not committed as a photon-history column. The
command used one NCP CPU, 2 GiB virtual-address limit, BLAS/OMP one thread,
and an external 600 s timeout. Actual whole-command wall time was 8.97 s,
user plus system CPU 8.89 s, and peak RSS 115,596 KiB. The Python
`RLIMIT_CPU=540s` is process-local, not a cumulative parent-plus-child cap.
No full-history or refinement result follows from this bounded PASS.

## Actual symbolic checks

Wolfram Language returned zero for the Saha logarithmic derivative residual
and helium quadratic residual. An xAct/xCoba calculation with
`g=diag(-c^2,a(t)^2,a(t)^2,a(t)^2)` returned
`Gamma^t_xx=a a'/c^2`, `Gamma^x_tx=a'/a`, `Gamma^t_tt=0`,
`u.u=-c^2`, null-geodesic `d ln(nu)/dt=-H`, and zero clock residuals for
`d ln(a)/dt=H`, `dz/dt=-(1+z)H`, and `dt/dz=-1/[(1+z)H]`.
Wolfram also returned a zero block-equation residual after Schur
elimination and a zero residual for the implicit linear Compton/adiabatic
thermal step; its stiff-coupling limit was `Tm->Tr`.
These algebraic checks do not verify atomic tables, accepted-step parity,
or full-history convergence.

## REI boundary

The existing PR #94 donor at `z=20` is an original-C-only, opt-in
comparison with `x_e=0.000210349192936` and `Tm=9.306042400380866 K`.
It projects helium neutral conditionally because C stdout lacks independent
species. A new Python `z=20` donor requires a validated independent FULL
history; no REI production scenario or checkpoint is changed here.

The versioned REC-owned interface in `primordial_rei_interface.py` can
represent the source and recipient number-density conventions separately,
interpolate a *validated* source-native history at `z=20`, and compute
Thomson/thermal quantities. It checks full-grid, source-stage, source-parity,
independent-review and numerical-refinement evidence before admitting a
physical boundary. Its actual output in
[`rei_interface_005/BOUNDARY_HOLD.json`](rei_interface_005/BOUNDARY_HOLD.json)
is `HOLD_MISSING_VALIDATED_HISTORY`, with both boundary records null,
activation disabled and `adopted_into_REI=false`. Independent review passed
the implementation's fail-closed checks, including duplicate refinement,
fake Richardson/parity evidence and same-unit H/nH consistency, but did not
admit a `z=20` scientific value. The final-code command and tests are in
[`rei_interface_005/REPAIR_RECEIPT.json`](rei_interface_005/REPAIR_RECEIPT.json).
