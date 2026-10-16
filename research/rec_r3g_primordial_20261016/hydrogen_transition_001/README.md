# R3g U4 bounded hydrogen transition

The independently integrated Python original October 2012 HyRec trajectory
resumed the reviewed U3 stop checkpoint at RT `j=382`, global index 18605.
It accepted 622 H-only steps on the source-native `Delta ln(a)=8.49e-5`
grid. The H post-Saha departure first exceeded `3e-4` at output `j=1002`;
that output was still computed by post-Saha. Exactly two subsequent accepted
steps used the original H ODE operator. The final node is global 19227,
`z=1562.918035636796`, `xe=0.9876865008915172`,
`Tm=4262.453568037749 K`.

## Provenance

- Execution commit: `9a2ca205b981abee004844826596c27d443776b5`.
- Original HyRec ZIP SHA-256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- Source capsule SHA-256: `46e5456f6fa5c2a4b9ff10da3e66ebbc575d6b9fe559630e83bc0d94c76efd4d`.
- U3 input STOP NPZ SHA-256: `97e54b568191a037f03822472972008952ee6c0eaedf486367d0c29f1c9bbe8b`.
- Native C stdout SHA-256: `490f09972dc9991fccccbc8af2d0b05244e22f907820d6ee72bc79e1cd16ff73`.
- Complete returned NCP raw archive SHA-256:
  `eef9f413f5ec92559688ceadeea3204d227353845d1a0c5302f8ed5923050d8a`.

The raw archive contains source capsule and manifests, C builds/stdout,
Python accepted rows, checkpoint arrays, first-failure field, and launch
command/timing. `verification.json` and `NCP_RETURN.json` summarize its
measured contents. The run used a create-only namespace
`/root/REC_R3G_HYDROGEN_TRANSITION_20261016_001`.
[`BACKUP_READBACK.json`](BACKUP_READBACK.json) records create-only Dropbox
and Google Drive copies; each remote was fully read back and matched the
archive SHA-256 above.

## Scoped review

Independent read-only review recalculated every one of the 622 C/Python
trajectory rows and all 388,750 spectral comparisons; it also checked all
eight checkpoint prefixes and causal ownership. All fixed tolerances passed.
The maximum scaled `xe` error was `3.3690958985516697e-16`, H RHS error
`1.5456566582194853e-11`, and photon tolerance ratio
`0.017993595275177278`.

The whole command used CPU 40, BLAS/OMP one thread, 2 GiB address-space
cap and external 600 s wall cap. Actual outer wall was 13.34 s, combined
user/system CPU 12.79/0.47 s, peak RSS 137,968 KiB. Process CPU was
separately bounded at 540 s; it is not an aggregate parent-plus-child cap.

This verifies only the original `q=0` source-native interval. The thermal
ODE, later atomic closures, `z=20` donor and time-step convergence remain
unverified.
