# REC-PB02 implementation contract

Objective: add a source-bound pure-hydrogen retained-shell and Peebles reduced reference kernel to the existing rec_microphysics Rust crate, with an independently exercised ABI/CLI and an explicit receiver handoff to REI PB02. Advance beyond the already published PB01 derivation.

In scope: named source constants/rates; SI entry points; beta_P versus beta_shell=beta_P/4; per-2p escape versus statistical-shell decay; exact retained-shell event conservation; QSS with declared frozen escape; physical FLRW thick-Sobolev local assembly; independent point comparisons; conditional angular finite-optical-depth study.

Unchanged: current REI Case-A/F00 closure; existing REC selected-He coverage and consumer-admission flags; earlier E1C COM/native ownership; strict historical error <2e-4 and public width <2e-3; existing failed interval [160,161].

Non-goals: full hydrogen/helium cosmological solver; Bianchi line radiative transfer; finite-tilt hydrogen closure; parameter inference; physical uncertainty certification; automatic production admission. A new reference module and receiver adapter candidate are not the current REI production hook.

Conventions: metric (-,+,+,+); proper SI nH [m^-3], rate alpha [m^3/s], beta/Lambda/Ralpha/H [s^-1], temperature K, fractions xp=xe for pure H and x1+xp+x2=1. Constants h,c,kB retained. Source-rounded upstream constants and SI-recomputed physical constants are distinct named profiles.

Acceptance: new native tests and independent source/oracle point comparisons pass; nuclei and event identities hold; nonfinite/out-of-domain/mismatched temperature input is rejected; no double-owned heat/photon source; scalar Peebles validity states listed; runtime/environment failures retained separately. Angular claims limited to h(n)>0, isotropic line source/populations, locally constant coefficients, fixed n1, common Sobolev closure and isotropic angular measure.

Authorization: current user explicitly requested theory/coding loops and backup/publication. Use existing REC branch/PR81; REI receives additive handoff documents on existing branch/PR83. Refresh remote parents before writing and never force push or merge.
