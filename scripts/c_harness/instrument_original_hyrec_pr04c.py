#!/usr/bin/env python3
"""Instrument canonical October-2012 original HyRec for PR-04C1A.

The canonical archive remains immutable.  All changes to the temporary
``hydrogen.c`` extraction are guarded by ``PR04C_DIAGNOSTICS``.  Compiling the
instrumented source without that macro must reproduce the canonical binary and
history hashes.
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "instrument_original_hyrec_pr04b2.py"
_spec = importlib.util.spec_from_file_location("_pr04b2_instrumenter", LEGACY_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load PR-04B2 source anchors")
_legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy)


def _pr04c(text: str) -> str:
    return text.replace("PR04B2_DIAGNOSTICS", "PR04C_DIAGNOSTICS").replace(
        "pr04b2_", "pr04c_"
    )


OUTPUT_REPLACEMENT = r'''   /* Average radiation field in each bin */
   for (b = 0; b < NVIRT; b++) Dfnu_hist[b][iz] = xv[b]/x1s;

   #ifdef PR04C_DIAGNOSTICS
   {
      static int pr04c_dumped[3] = {0,0,0};
      const double pr04c_targets[3] = {1300.,1100.,900.};
      unsigned pr04c_itarget;
      for (pr04c_itarget=0; pr04c_itarget<3; pr04c_itarget++) {
         const double pr04c_target_z = pr04c_targets[pr04c_itarget];
         const double pr04c_half_step = 0.500001 * DLNA * (1. + pr04c_target_z);
         if (!pr04c_dumped[pr04c_itarget] && fabs(z-pr04c_target_z) <= pr04c_half_step) {
            const char *pr04c_dir = getenv("PR04C_DIAGNOSTIC_DIR");
            char pr04c_path[4096];
            FILE *pr04c_fp;
            if (pr04c_dir == NULL) pr04c_dir = ".";
            snprintf(pr04c_path, sizeof(pr04c_path), "%s/pr04c_z%.0f.csv", pr04c_dir, pr04c_target_z);
            pr04c_fp = fopen(pr04c_path, "w");
            if (pr04c_fp == NULL) { fprintf(stderr, "PR04C diagnostic open failed\n"); exit(87); }
            fprintf(pr04c_fp, "META,target_z,%.17g\n", pr04c_target_z);
            fprintf(pr04c_fp, "META,z,%.17g\n", z);
            fprintf(pr04c_fp, "META,zstart,%.17g\n", zstart);
            fprintf(pr04c_fp, "META,iz_local,%u\n", iz);
            fprintf(pr04c_fp, "META,xe,%.17g\n", xe);
            fprintf(pr04c_fp, "META,xHII,%.17g\n", xHII);
            fprintf(pr04c_fp, "META,x1s,%.17g\n", x1s);
            fprintf(pr04c_fp, "META,nH_cm3,%.17g\n", nH);
            fprintf(pr04c_fp, "META,H_sInv,%.17g\n", H);
            fprintf(pr04c_fp, "META,TM_eV_rescaled,%.17g\n", TM);
            fprintf(pr04c_fp, "META,TR_eV_rescaled,%.17g\n", TR);
            fprintf(pr04c_fp, "META,TM_over_TR,%.17g\n", TM/TR);
            fprintf(pr04c_fp, "META,fsR,%.17g\n", fsR);
            fprintf(pr04c_fp, "META,meR,%.17g\n", meR);
            fprintf(pr04c_fp, "META,dxHIIdlna,%.17g\n", dxedlna);
            fprintf(pr04c_fp, "META,A2p_up_sInv,%.17g\n", pr04c_A2p_up);
            fprintf(pr04c_fp, "META,A2p_dn_sInv,%.17g\n", pr04c_A2p_dn);
            fprintf(pr04c_fp, "META,Dfplus_Lya,%.17g\n", Dfplus_Ly[0]);
            fprintf(pr04c_fp, "META,Dfplus_Lyb,%.17g\n", Dfplus_Ly[1]);
            fprintf(pr04c_fp, "META,Dfminus_Lya,%.17g\n", xr[1]/3./x1s);
            fprintf(pr04c_fp, "META,Dfminus_Lyb,%.17g\n", xr[0]/x1s*exp(-E32/TR));
            fprintf(pr04c_fp, "META,Dfminus_Lyg,%.17g\n", xr[0]/x1s*exp(-E42/TR));
            for (i=0; i<2; i++) {
               fprintf(pr04c_fp, "REAL,%u,%.17g,%.17g,%.17g,%.17g,%.17g\n", i, xr[i], sr[i], Alpha[i], DAlpha[i], Beta[i]);
               for (b=0; b<2; b++) fprintf(pr04c_fp, "TRR,%u,%u,%.17g\n", i, b, Trr[i][b]);
            }
            for (b=0; b<NVIRT; b++) {
               fprintf(pr04c_fp, "VIRTUAL,%u,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
                       b, twog->Eb_tab[b], Dfplus[b], Dfnu_hist[b][iz], Dfminus_hist[b][iz],
                       pr04c_Dfeq[b], Dtau[b], xv[b], sv[b], Tvv[0][b], pr04c_Aup[b], pr04c_Adn[b],
                       pr04c_Gammab[b], pr04c_one_minus_Pib[b]);
               fprintf(pr04c_fp, "TRV,0,%u,%.17g\n", b, Trv[0][b]);
               fprintf(pr04c_fp, "TRV,1,%u,%.17g\n", b, Trv[1][b]);
               fprintf(pr04c_fp, "TVR,0,%u,%.17g\n", b, Tvr[0][b]);
               fprintf(pr04c_fp, "TVR,1,%u,%.17g\n", b, Tvr[1][b]);
               fprintf(pr04c_fp, "TVV,0,%u,%.17g\n", b, Tvv[0][b]);
               fprintf(pr04c_fp, "TVV,1,%u,%.17g\n", b, Tvv[1][b]);
               fprintf(pr04c_fp, "TVV,2,%u,%.17g\n", b, Tvv[2][b]);
            }
            {
               const double pr04c_xs[2] = {-21.25,21.25};
               const char *pr04c_sides[2] = {"red","blue"};
               const double pr04c_dE = E21 * sqrt(2. * TM / mH);
               const double pr04c_lna_start = -log(1.+zstart);
               unsigned pr04c_side;
               for (pr04c_side=0; pr04c_side<2; pr04c_side++) {
                  const double pr04c_E = E21 + pr04c_xs[pr04c_side] * pr04c_dE;
                  unsigned pr04c_source = 0;
                  double pr04c_ainv, pr04c_lna, pr04c_frac, pr04c_y0, pr04c_y1;
                  double pr04c_Df, pr04c_fbb, pr04c_ftotal, pr04c_A;
                  double pr04c_phi_dist, pr04c_phi_ref, pr04c_phi_total;
                  long pr04c_ind;
                  while (pr04c_source < NVIRT && twog->Eb_tab[pr04c_source] <= pr04c_E) pr04c_source++;
                  if (pr04c_source >= NVIRT) { fprintf(stderr, "PR04C interface has no higher native source\n"); exit(88); }
                  pr04c_ainv = (1.+z) * twog->Eb_tab[pr04c_source] / pr04c_E;
                  pr04c_lna = -log(pr04c_ainv);
                  pr04c_ind = (long) floor((pr04c_lna-pr04c_lna_start)/DLNA);
                  pr04c_frac = (pr04c_lna-pr04c_lna_start)/DLNA - pr04c_ind;
                  if (pr04c_ind < 0 || (unsigned)(pr04c_ind+1) > iz) {
                     fprintf(stderr,
                        "PR04C interface history query out of range: target=%.17g z=%.17g iz=%u side=%s x=%.17g E=%.17g source=%u sourceE=%.17g lna=%.17g lna_start=%.17g ind=%ld right=%ld frac=%.17g current_known_max=%u\n",
                        pr04c_target_z, z, iz, pr04c_sides[pr04c_side], pr04c_xs[pr04c_side],
                        pr04c_E, pr04c_source, twog->Eb_tab[pr04c_source], pr04c_lna,
                        pr04c_lna_start, pr04c_ind, pr04c_ind+1, pr04c_frac, iz-1);
                     exit(89);
                  }
                  pr04c_y0 = Dfminus_hist[pr04c_source][pr04c_ind];
                  pr04c_y1 = Dfminus_hist[pr04c_source][pr04c_ind+1];
                  pr04c_Df = (1.-pr04c_frac)*pr04c_y0 + pr04c_frac*pr04c_y1;
                  pr04c_fbb = 1./expm1(pr04c_E/TR);
                  pr04c_ftotal = pr04c_fbb + pr04c_Df;
                  pr04c_A = 8.*M_PI/(nH*cube(hPc/pr04c_E/fsR/fsR/meR));
                  pr04c_phi_dist = H*pr04c_A*pr04c_Df;
                  pr04c_phi_ref = H*pr04c_A*pr04c_fbb;
                  pr04c_phi_total = H*pr04c_A*pr04c_ftotal;
                  fprintf(pr04c_fp,
                     "INTERFACE,%s,%.17g,%.17g,%.17g,%u,%.17g,%.17g,%ld,%ld,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
                     pr04c_sides[pr04c_side], pr04c_xs[pr04c_side], pr04c_dE, pr04c_E,
                     pr04c_source, twog->Eb_tab[pr04c_source], pr04c_lna,
                     pr04c_ind, pr04c_ind+1, pr04c_frac, pr04c_y0, pr04c_y1,
                     pr04c_Df, pr04c_fbb, pr04c_ftotal, pr04c_A,
                     pr04c_phi_dist, pr04c_phi_ref, pr04c_phi_total);
               }
            }
            fclose(pr04c_fp);
            pr04c_dumped[pr04c_itarget] = 1;
         }
      }
   }
   #endif

   for (i = 0; i < 2; i++) free(Trv[i]);
'''


def _replace_once(text: str, needle: str, replacement: str, label: str) -> str:
    count = text.count(needle)
    if count != 1:
        raise ValueError(f"expected exactly one {label} anchor, found {count}")
    return text.replace(needle, replacement, 1)


def instrument_hydrogen_source(text: str) -> str:
    result = text
    replacements = (
        ("global", _legacy.GLOBAL_NEEDLE, _pr04c(_legacy.GLOBAL_REPLACEMENT)),
        ("A2p", _legacy.A2P_NEEDLE, _pr04c(_legacy.A2P_REPLACEMENT)),
        ("rate", _legacy.RATE_NEEDLE, _pr04c(_legacy.RATE_REPLACEMENT)),
        ("local", _legacy.LOCAL_NEEDLE, _pr04c(_legacy.LOCAL_REPLACEMENT)),
        ("Dfeq", _legacy.DFEQ_NEEDLE, _pr04c(_legacy.DFEQ_REPLACEMENT)),
        ("output", _legacy.OUTPUT_NEEDLE, OUTPUT_REPLACEMENT),
    )
    for label, needle, replacement in replacements:
        result = _replace_once(result, needle, replacement, label)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()

    original = args.source.read_text(encoding="utf-8")
    instrumented = instrument_hydrogen_source(original)
    args.source.write_text(instrumented, encoding="utf-8", newline="")
    if args.diff is not None:
        difference = difflib.unified_diff(
            original.splitlines(keepends=True),
            instrumented.splitlines(keepends=True),
            fromfile="canonical/hydrogen.c",
            tofile="instrumented/hydrogen.c",
        )
        args.diff.write_text("".join(difference), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
