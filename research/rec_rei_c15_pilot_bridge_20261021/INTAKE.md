# REC to REI C15 pilot bridge: intake

2026-10-21. Scope: contribute to today's non-tilted Bianchi I preliminary Sigma/Pi plots. The selected demonstrator is the existing **LRS**, warm-start **a=0.1999 to 0.2**, C15 H/He + radiation + massive Vlasov feedback model, not a full z=20 to 4 EoR solution. No performance benchmark or production activation is requested.

## Latest evidence read before implementation

- REC PR114 current base `df95a074730ea0d13d609cf88d448f01f4a47ef1`: new U4B 74443->74475, source `a09e1d249d4cf4b706c09571fa7f231c8084c251`; numerical scoped PASS, full allocation accounting UNRESOLVED. Reuse; not a prerequisite for this warm REI pilot.
- REI PR141 C15 `80825585f9fe31d2ee0d5af545ada3fa1f52be72`, science `f6a1c10aa6d3f7252a9e68a77c2c4b62c41e77f0`: actual coupled warm H/He model, 8 saved histories. Archive 1680554 bytes SHA256 `a159546829ff963b354b2c8feaa5da8b5536363f870ce6a4d3a966746d9c06a4` recovered from Drive and whole-byte hash checked in this session.
- REI PR147 canonical response `3b85dedce84d37b3e165da00685a8a984950aafe`: positive canonical Vlasov/radiation alternative, not equivalent to C15 chemistry. Archive 400528 bytes SHA256 `15a131380dc232998ad798de84fc17239605bce9350802c34f63011085e61da5` recovered and checked. Other concurrent conversations report geometry sweeps; these are leads, not new admitted results here.
- REI initial-Pi supplier `21342736456be226af2de8c00feeb132499d89ab`: physically positive quadrupolar radiation closure; background-only, not substituted for H/He coupling.
- REI PR129 `fa20d75e344a28c833a47cbca82315ccbbdf6882`: original stress-free H/He histories and stable incremental proper clocks, reused only within scope.
- REI PR211 RUN19 `c9deb933761a8d2593d1176aee028cd423bdbc05`: coefficient-only prepared/cache reuse, not automatically interchangeable with C15's warm C11 rate owner.
- REI PR210 BRPERF01 `e4c8133288614638792888367ca10b2ded3138ff`: exact prepared rates and frozen-photon pool; coupled source-on admission remains separate.
- REI PR198 `3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8`: 144/246 backlog complete, old caps/debits preserved; no replay of backlog for this pilot.
- BASS_HE PR78 `38493edccd9344c11fd66e63e1d938f77c2b093f`: native references 4/4 and HPC64 canary 1/1 complete, prepared queue empty. Reuse immutable cache/pool patterns; no re-execution or multiplication of speedup ratios.

REC/REI branch metadata, relevant PR/source files, personal-context conversation leads, recent Library progress report, Drive and Dropbox listings were inspected. This is NOT an all-files/all-private-conversations completeness claim. Existing local/NCP processes were not inspected here: Remote Desktop Commander returned a current service quota error. Local Python execution works. Native subagents NOT_RUN; serial verification is used.

## Chosen contribution

Preserve C15 donor bytes and equations. Add signed tensor-norm coordinates, an exact affine initial stress map, immutable per-process setup caches, and a bounded shared-node case dispatcher. Initial gamma/nu quadrupoles share A; massive fraction 0.1 and initial massive quadrupole 0. The norm convention is explicit: Frobenius coordinates plus half-contraction compatibility columns. Pressure in J/m^3 and H in s^-1 use kappa_t=8*pi*G/c^2=c^2*kappa_E.

Other Codex sessions are not an exclusion condition. Dispatch only independent cases fitting observed affinity/cgroup/CPU-idle/memory headroom and cooperative leases; never signal unrelated PIDs. Keep BLAS threads=1. No detailed timing benchmark and no speedup claim.

## DAG at intake

R1/C1 intake COMPLETE_SCOPED; prior results COMPLETE_REUSED. R2 reuse selection COMPLETE_SCOPED. R3/C3 normalization and resource contract IN_PROGRESS. C5 implementation, C6 minimal correctness, R7 preliminary scientific pilot, C9 serial audit, C10 publication/backup PENDING. Full EoR, generic non-LRS support, polarized Thomson and global source Q^a closure remain NOT_ADMITTED.
