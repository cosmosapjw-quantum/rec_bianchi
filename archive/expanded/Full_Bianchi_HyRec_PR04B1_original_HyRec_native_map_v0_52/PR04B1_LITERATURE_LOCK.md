# Literature and source-role lock

- Official HyRec page: the previous stable releases include October 2012,
  May 2012 and January 2011. Original HyRec performs numerical time-dependent
  radiative transfer, including Lyman feedback, two-photon/Raman processes and
  Ly-alpha frequency diffusion.
- Ali-Haimoud & Hirata (2011), arXiv:1011.3758: full radiative transfer with
  simultaneous radiation-field, level-population and free-electron evolution.
- Lee & Ali-Haimoud (2020), arXiv:2007.14114: HYREC-2 is an effective four-level
  implementation whose Ly-alpha escape correction is computed using original
  HyRec and tabulated.

The owner-supplied ZIP is byte-locked. The official web page identifies an
October-2012 stable release, and ZIP timestamps place `history.c` and `Makefile`
on 2012-10-05. Internal C headers still say May 2012. Because this runtime did
not independently download the official binary, exact equality to the current
server-side October-2012 bytes is not claimed.
