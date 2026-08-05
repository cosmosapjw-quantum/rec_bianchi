# PR-04A literature and source lock

Primary public anchors checked for this stage:

1. Official HyRec page, Y. Ali-Haimoud: original HyRec uses a numerical
   time-dependent radiative-transfer calculation; default HYREC-2 uses
   correction functions.  The page lists October 2012, May 2012 and January
   2011 stable releases.  https://cosmo.nyu.edu/yacine/hyrec/hyrec.html
2. Y. Ali-Haimoud and C. Hirata, Phys. Rev. D 83, 043513 (2011),
   arXiv:1011.3758: simultaneous multilevel-atom and radiative-transfer
   calculation.
3. N. Lee and Y. Ali-Haimoud, Phys. Rev. D 102, 083517 (2020),
   arXiv:2007.14114: effective four-level HYREC-2 and correction functions
   derived from original HyRec.

Executable source authority in this artifact is the exact durable HYREC-2
commit/blob registry in `PR04_INPUT_LOCK.json`.  Web snippets are contextual
literature evidence, not substitutes for pinned source bytes.

The Wolfram and Precise Special Functions plugins were not exposed in this
runtime.  Exact algebra was checked with SymPy; high-precision null and
frequency conversions used mpmath; positive numerical quadrature used SciPy.
