# C5 implementation clarifications approved before execution

These are explicit interpretations of the frozen source contract. They do not
change physical closure, input, time step, tolerances or admission boundary.

1. **Endpoint references and QSS capture times.** The626 endpoint references are
   (source-channel,local-time) bindings. Detailed QSS capture uses the deduplicated
   integer times `{cell,cell+1 over313 original query rows} union {5127}`. Every
   actual FULL write in those slots retains its native2real/311virtual solution
   and outgoing arrays, allowing last-writer selection from actual event order.

2. **Native argument and coefficient temperature views.** In hydrogen.c730–752,
   rec_HMLA_2photon_dxHIIdlna receives TM/TR, computes ratio=TM/TR, calls
   rescale_T(&TR,fsR,meR), and assigns TM=ratio*TR before coefficient assembly.
   `CALLS.jsonl` fields TM_eV/TR_eV are the actual dispatcher arguments.
   `WRITES.jsonl` coefficient_TM_eV/coefficient_TR_eV are the actual FULL
   post-rescale values. The common writer affine path uses the explicitly
   labelled dispatcher view; target CSV temperature parity uses coefficient
   fields corresponding to its TM_eV_rescaled/TR_eV_rescaled fields.

3. **Native solution vectors are departures.** The source comment preceding
   hydrogen.c765–767 states that xr/xv solve differences from equilibrium with
   the ground state. `real[0]` is the native2s departure, `real[1]` the2p
   departure; the source line795 computes Lyman alpha from xr[1]/3/x1s.
   `virtual` is the native departure xv=x1s*Dfnu. These raw vectors are not
   absolute populations. No equilibrium restoration or nonnegative-population
   test is applied. VARIABLE_SEMANTICS.json and the affine packet repeat this
   meaning; conditional Mv=s theory uses v as this departure vector.

4. **Derivative-memory initialization.** Source history.c525–526,546–547 and
   575–576 seed memories from four previous samples, sometimes subtracting
   helium derivative memories. INITIALIZATION.jsonl stores actual samples,
   their four global indices, subtractor memories, h and initialized prev/prev2.
   The analyzer forms the exact represented expression and checks its rounding
   residual against64*eps64 times the sum of absolute operation terms, including
   the observed result. Zero gross requires exact zero. These are labelled
   SOURCE_SECANT_INITIALIZATION_NOT_RHS.

5. **Memory shifts also apply to post-Saha records.** Every recurrence record
   validates actual after_prev=current and after_prev2=old_prev before deciding
   whether its branch was differential. A post-Saha record receives rho=null
   and no ODE recurrence check, while its original memory shift remains checked.
   The neutral-H differential branch uses sigma=-1 as corrected THEORY eq2.

6. **Observed operand order and definedness.** Post-Saha base/plus/minus callsite
   wrappers remain operands of the original C expressions. Their ids are
   assigned on actual wrapper entry, without imposing a textual execution
   order. Hooks for undefined early partition variables pass literal0 with
   an explicit partition=false flag; they never load an uninitialized local.

7. **Frozen floating comparison factor.** eps64 is exactly2^-52. Retained array
   and target parity retain512eps component scale; recurrence and initialization
   retain64eps operation gross. No zero floor, new precision or tolerance
   widening is introduced.
