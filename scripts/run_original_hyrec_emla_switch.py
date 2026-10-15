#!/usr/bin/env python3
"""Reproduce original Oct2012 HyRec C EMLA2s2p switch in an isolated folder.

No modification of the canonical archive or current REC checkout sources:
the *copied* source header has its single MODEL FULL line switched to
MODEL EMLA2s2p, all other native files kept identical. This is a
source-identifiable native approximate-model reference, not FULL.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,datetime
from pathlib import Path

from full_bianchi_hyrec.recoil.original_hyrec_native import (
    ORIGINAL_HYREC_ARCHIVE_SHA256,safe_extract_original_hyrec_archive,
)

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
EXPECTED_FLRW_INPUT_SHA="523eeef77af15c00404962afc0f63ff907897b6d7535ea782e46bd46538395b3"
EXPECTED_NATIVE_SWITCH_OUTPUT_SHA="75d4bd873fa45b941a58a2977c5f8206002fedead134499d2a16a976b49d38d6"
# The source output byte identity is separately tracked in the previous
# native replay receipt; comparisons are computed on numerical values.
def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    q=p.parse_args()
    if q.outdir.exists() and any(q.outdir.iterdir()):
        p.error("output directory exists/nonempty; no overwrite")
    if sha(ARCHIVE)!=ORIGINAL_HYREC_ARCHIVE_SHA256:
        raise ValueError("original 2012 source authority has changed")
    if sha(q.input)!=EXPECTED_FLRW_INPUT_SHA:
        raise ValueError("matched FLRW input identity has changed")
    q.outdir.mkdir(parents=True,exist_ok=True)
    source_dir=q.outdir/"source"
    safe_extract_original_hyrec_archive(ARCHIVE,source_dir)
    native=source_dir/"HyRec"
    header=native/"hyrec_params.h"
    content=header.read_bytes()
    if content.count(b"#define MODEL FULL")!=1:
        raise ValueError("original C MODEL macro missing or ambiguous")
    header.write_bytes(content.replace(b"#define MODEL FULL",b"#define MODEL EMLA2s2p"))
    compile_cmd=[
        "gcc","-std=gnu11","-O2","-w",
        "hyrectools.c","helium.c","hydrogen.c","history.c","hyrec.c",
        "-lm","-o","hyrec_EMLA",
    ]
    built=subprocess.run(compile_cmd,cwd=native,capture_output=True,text=True,timeout=45)
    (q.outdir/"COMPILE_STDOUT.txt").write_text(built.stdout)
    (q.outdir/"COMPILE_STDERR.txt").write_text(built.stderr)
    if built.returncode:
        raise RuntimeError("gcc native EMLA compile failed: "+built.stderr[-450:])
    with q.input.open("rb") as fh:
        ref=subprocess.run(["./hyrec_EMLA"],cwd=native,stdin=fh,
                           capture_output=True,timeout=75)
    out=q.outdir/"EMLA_NATIVE_HISTORY.txt"
    out.write_bytes(ref.stdout)
    (q.outdir/"RUNTIME_STDERR.txt").write_bytes(ref.stderr)
    if ref.returncode!=0 or len(ref.stdout.splitlines())!=8001:
        raise RuntimeError("native C EMLA numerical baseline failed")
    if sha(out)!=EXPECTED_NATIVE_SWITCH_OUTPUT_SHA:
        raise ValueError("source-switched C EMLA binary output differs from pinned comparator")
    receipt={
        "schema":"rec.original_HyRec2012.EMLA_switch.v1",
        "source_mode":"Original C EMLA2s2p, not the default full RT mode",
        "source_archive_sha256":ORIGINAL_HYREC_ARCHIVE_SHA256,
        "changed_exact_original_header_line":"#define MODEL FULL -> #define MODEL EMLA2s2p",
        "original_header_sha256":hashlib.sha256(content).hexdigest(),
        "switched_header_sha256":sha(header),
        "matched_input_sha256":sha(q.input),
        "output_sha256":sha(out),
        "output_rows":len(ref.stdout.splitlines()),
        "C_compile_exit":built.returncode,"C_run_exit":ref.returncode,
    }
    (q.outdir/"SOURCE_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
if __name__=="__main__":
    main()
