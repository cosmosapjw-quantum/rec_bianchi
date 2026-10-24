#!/usr/bin/env python3
"""Deterministically instrument October-2012 original HyRec for PR-04B2A.

The canonical archive remains immutable.  This helper patches a temporary
extracted ``hydrogen.c``.  All additions are behind ``PR04B2_DIAGNOSTICS``;
compiling without the macro must reproduce the canonical binary and history
hashes exactly.
"""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path


GLOBAL_NEEDLE = '#include "hydrogen.h"\n\n\n'
GLOBAL_REPLACEMENT = '''#include "hydrogen.h"\n\n#ifdef PR04B2_DIAGNOSTICS\nstatic double pr04b2_Aup[NVIRT];\nstatic double pr04b2_Adn[NVIRT];\nstatic double pr04b2_Gammab[NVIRT];\nstatic double pr04b2_one_minus_Pib[NVIRT];\nstatic double pr04b2_A2p_up;\nstatic double pr04b2_A2p_dn;\n#endif\n\n'''

A2P_NEEDLE = '''    A2p_up *= rescalediff;\n    A2p_dn *= rescalediff; \n    for (b = 0; b < NVIRT; b++) {\n'''
A2P_REPLACEMENT = '''    A2p_up *= rescalediff;\n    A2p_dn *= rescalediff; \n    #ifdef PR04B2_DIAGNOSTICS\n    pr04b2_A2p_up = A2p_up;\n    pr04b2_A2p_dn = A2p_dn;\n    #endif\n    for (b = 0; b < NVIRT; b++) {\n'''

RATE_NEEDLE = '''      one_minus_Pib = Dtau[b] > 1e-6 ? 1.- (1.-exp(-Dtau[b]))/Dtau[b] : Dtau[b]/2. - square(Dtau[b])/6.;\n      Tvv[0][b] = Dtau[b] > 0.? Gammab/one_minus_Pib : 2./(x1s * cube(hPc/twog->Eb_tab[b]/fsR/fsR/meR) * nH /8. /M_PI /H);  /* Added May 2012: proper limit Dtau->0 */\n      sv[b]  = Tvv[0][b] * x1s * Dfplus[b] * (1.-one_minus_Pib);         \n'''
RATE_REPLACEMENT = '''      one_minus_Pib = Dtau[b] > 1e-6 ? 1.- (1.-exp(-Dtau[b]))/Dtau[b] : Dtau[b]/2. - square(Dtau[b])/6.;\n      Tvv[0][b] = Dtau[b] > 0.? Gammab/one_minus_Pib : 2./(x1s * cube(hPc/twog->Eb_tab[b]/fsR/fsR/meR) * nH /8. /M_PI /H);  /* Added May 2012: proper limit Dtau->0 */\n      sv[b]  = Tvv[0][b] * x1s * Dfplus[b] * (1.-one_minus_Pib);         \n      #ifdef PR04B2_DIAGNOSTICS\n      pr04b2_Aup[b] = Aup[b];\n      pr04b2_Adn[b] = Adn[b];\n      pr04b2_Gammab[b] = Gammab;\n      pr04b2_one_minus_Pib[b] = one_minus_Pib;\n      #endif\n'''

LOCAL_NEEDLE = '''   double Alpha[2], DAlpha[2], Beta[2];\n   double ratio;\n\n   ratio = TM/TR;'''
LOCAL_REPLACEMENT = '''   double Alpha[2], DAlpha[2], Beta[2];\n   double ratio;\n\n   #ifdef PR04B2_DIAGNOSTICS\n   double pr04b2_Dfeq[NVIRT];\n   #endif\n\n   ratio = TM/TR;'''

DFEQ_NEEDLE = '''         Dfeq /= x1s*one_minus_Pib*Tvv[0][b];\n         one_minus_exptau = Dtau[b] > 1e-6 ? 1.-exp(-Dtau[b]) : Dtau[b] - square(Dtau[b])/2.;               \n                                \n         Dfminus_hist[b][iz] = Dfplus[b] + (Dfeq - Dfplus[b])*one_minus_exptau;\n     }\n     else Dfminus_hist[b][iz] = Dfplus[b];\n'''
DFEQ_REPLACEMENT = '''         Dfeq /= x1s*one_minus_Pib*Tvv[0][b];\n         #ifdef PR04B2_DIAGNOSTICS\n         pr04b2_Dfeq[b] = Dfeq;\n         #endif\n         one_minus_exptau = Dtau[b] > 1e-6 ? 1.-exp(-Dtau[b]) : Dtau[b] - square(Dtau[b])/2.;               \n                                \n         Dfminus_hist[b][iz] = Dfplus[b] + (Dfeq - Dfplus[b])*one_minus_exptau;\n     }\n     else {\n         Dfminus_hist[b][iz] = Dfplus[b];\n         #ifdef PR04B2_DIAGNOSTICS\n         pr04b2_Dfeq[b] = Dfplus[b];\n         #endif\n     }\n'''

OUTPUT_NEEDLE = '''   /* Average radiation field in each bin */\n   for (b = 0; b < NVIRT; b++) Dfnu_hist[b][iz] = xv[b]/x1s;   \n\n   for (i = 0; i < 2; i++) free(Trv[i]);\n'''
OUTPUT_REPLACEMENT = '''   /* Average radiation field in each bin */\n   for (b = 0; b < NVIRT; b++) Dfnu_hist[b][iz] = xv[b]/x1s;   \n\n   #ifdef PR04B2_DIAGNOSTICS\n   {\n      static int pr04b2_dumped = 0;\n      const double pr04b2_target_z = 1100.;\n      const double pr04b2_half_step = 0.500001 * DLNA * (1. + pr04b2_target_z);\n      if (!pr04b2_dumped && fabs(z-pr04b2_target_z) <= pr04b2_half_step) {\n         const char *pr04b2_path = getenv("PR04B2_DIAGNOSTIC_PATH");\n         FILE *pr04b2_fp = fopen(pr04b2_path == NULL ? "pr04b2_snapshot.csv" : pr04b2_path, "w");\n         if (pr04b2_fp == NULL) { fprintf(stderr, "PR04B2 diagnostic open failed\\n"); exit(87); }\n         fprintf(pr04b2_fp, "META,target_z,%.17g\\n", pr04b2_target_z);\n         fprintf(pr04b2_fp, "META,z,%.17g\\n", z);\n         fprintf(pr04b2_fp, "META,zstart,%.17g\\n", zstart);\n         fprintf(pr04b2_fp, "META,iz_local,%u\\n", iz);\n         fprintf(pr04b2_fp, "META,xe,%.17g\\n", xe);\n         fprintf(pr04b2_fp, "META,xHII,%.17g\\n", xHII);\n         fprintf(pr04b2_fp, "META,x1s,%.17g\\n", x1s);\n         fprintf(pr04b2_fp, "META,nH_cm3,%.17g\\n", nH);\n         fprintf(pr04b2_fp, "META,H_sInv,%.17g\\n", H);\n         fprintf(pr04b2_fp, "META,TM_eV_rescaled,%.17g\\n", TM);\n         fprintf(pr04b2_fp, "META,TR_eV_rescaled,%.17g\\n", TR);\n         fprintf(pr04b2_fp, "META,TM_over_TR,%.17g\\n", TM/TR);\n         fprintf(pr04b2_fp, "META,fsR,%.17g\\n", fsR);\n         fprintf(pr04b2_fp, "META,meR,%.17g\\n", meR);\n         fprintf(pr04b2_fp, "META,dxHIIdlna,%.17g\\n", dxedlna);\n         fprintf(pr04b2_fp, "META,A2p_up_sInv,%.17g\\n", pr04b2_A2p_up);\n         fprintf(pr04b2_fp, "META,A2p_dn_sInv,%.17g\\n", pr04b2_A2p_dn);\n         fprintf(pr04b2_fp, "META,Dfplus_Lya,%.17g\\n", Dfplus_Ly[0]);\n         fprintf(pr04b2_fp, "META,Dfplus_Lyb,%.17g\\n", Dfplus_Ly[1]);\n         fprintf(pr04b2_fp, "META,Dfminus_Lya,%.17g\\n", xr[1]/3./x1s);\n         fprintf(pr04b2_fp, "META,Dfminus_Lyb,%.17g\\n", xr[0]/x1s*exp(-E32/TR));\n         fprintf(pr04b2_fp, "META,Dfminus_Lyg,%.17g\\n", xr[0]/x1s*exp(-E42/TR));\n         for (i=0; i<2; i++) {\n            fprintf(pr04b2_fp, "REAL,%u,%.17g,%.17g,%.17g,%.17g,%.17g\\n", i, xr[i], sr[i], Alpha[i], DAlpha[i], Beta[i]);\n            for (b=0; b<2; b++) fprintf(pr04b2_fp, "TRR,%u,%u,%.17g\\n", i, b, Trr[i][b]);\n         }\n         for (b=0; b<NVIRT; b++) {\n            fprintf(pr04b2_fp, "VIRTUAL,%u,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",\n                    b, twog->Eb_tab[b], Dfplus[b], Dfnu_hist[b][iz], Dfminus_hist[b][iz],\n                    pr04b2_Dfeq[b], Dtau[b], xv[b], sv[b], Tvv[0][b], pr04b2_Aup[b], pr04b2_Adn[b],\n                    pr04b2_Gammab[b], pr04b2_one_minus_Pib[b]);\n            fprintf(pr04b2_fp, "TRV,0,%u,%.17g\\n", b, Trv[0][b]);\n            fprintf(pr04b2_fp, "TRV,1,%u,%.17g\\n", b, Trv[1][b]);\n            fprintf(pr04b2_fp, "TVR,0,%u,%.17g\\n", b, Tvr[0][b]);\n            fprintf(pr04b2_fp, "TVR,1,%u,%.17g\\n", b, Tvr[1][b]);\n            fprintf(pr04b2_fp, "TVV,0,%u,%.17g\\n", b, Tvv[0][b]);\n            fprintf(pr04b2_fp, "TVV,1,%u,%.17g\\n", b, Tvv[1][b]);\n            fprintf(pr04b2_fp, "TVV,2,%u,%.17g\\n", b, Tvv[2][b]);\n         }\n         fclose(pr04b2_fp); pr04b2_dumped = 1;\n      }\n   }\n   #endif\n\n   for (i = 0; i < 2; i++) free(Trv[i]);\n'''


def _replace_once(text: str, needle: str, replacement: str, label: str) -> str:
    count = text.count(needle)
    if count != 1:
        raise ValueError(f"expected exactly one {label} anchor, found {count}")
    return text.replace(needle, replacement, 1)


def instrument_hydrogen_source(text: str) -> str:
    result = text
    for label, needle, replacement in (
        ("global", GLOBAL_NEEDLE, GLOBAL_REPLACEMENT),
        ("A2p", A2P_NEEDLE, A2P_REPLACEMENT),
        ("rate", RATE_NEEDLE, RATE_REPLACEMENT),
        ("local", LOCAL_NEEDLE, LOCAL_REPLACEMENT),
        ("Dfeq", DFEQ_NEEDLE, DFEQ_REPLACEMENT),
        ("output", OUTPUT_NEEDLE, OUTPUT_REPLACEMENT),
    ):
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
