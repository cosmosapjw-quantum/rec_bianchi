"""Build a finite oracle from pinned, byte-exact native C excerpts.

This does not compile or run the native recombination program. Only its two
history functions plus literal RHS/storage statements are linked to a wrapper.
Compilation occurs only when the bounded primary harness calls build_oracle.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent / "rec_line_native_owner_20261023"
SOURCE_SHA = "421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b"
HEADER_SHA = "46b4cb3f7a463ddbae966c02114e16f8e079615e4838f5dcbcb6cd1c5a67a83f"


def _function(source: str, name: str) -> str:
    start = re.search(r"^(?:double|void) " + re.escape(name) + r"\(", source, re.M)
    if start is None:
        raise ValueError(f"missing source function {name}")
    begin = source.index("{", start.start())
    level = 0
    for at in range(begin, len(source)):
        if source[at] == "{":
            level += 1
        elif source[at] == "}":
            level -= 1
            if level == 0:
                return source[start.start():at + 1]
    raise ValueError(f"unterminated function {name}")


def _line(source: str, prefix: str) -> str:
    found = [line for line in source.splitlines(keepends=True)
             if line.lstrip().startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"nonunique source line {prefix!r}")
    return found[0]


def _extract(out: Path) -> tuple[Path, dict]:
    src_path = PARENT / "vendor/hydrogen.c"
    params_path = ROOT / "vendor/hyrec_params.h"
    source_bytes = src_path.read_bytes()
    params_bytes = params_path.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA:
        raise ValueError("immutable hydrogen.c source changed")
    if hashlib.sha256(params_bytes).hexdigest() != HEADER_SHA:
        raise ValueError("immutable h4 parameter-header source changed")
    source, params = source_bytes.decode(), params_bytes.decode()
    functions = {name: _function(source, name)
                 for name in ("interp_Dfnu", "fplus_from_fminus")}
    defines = []
    for name in ("NVIRT", "NSUBLYA", "NSUBLYB", "DLNA"):
        line = re.search(r"^#define\s+" + name + r"\s+.*$", params, re.M)
        if line is None:
            raise ValueError(f"missing constant {name}")
        defines.append(line.group(0))
    h_header = (PARENT / "vendor/hydrogen.h").read_text()
    for name in ("E21", "E31", "E41", "E32", "E42"):
        line = re.search(r"^#define\s+" + name + r"\s+.*$", h_header, re.M)
        if line is None:
            raise ValueError(f"missing energy constant {name}")
        defines.append(line.group(0))
    real_lines = _line(source, "sr[0]     =") + _line(source, "sr[1]     =")
    # The probability statement occurs once in assembly and once in storage;
    # select the assembly block without rewriting its literal arithmetic.
    assembly = source[source.index("void populateTS_2photon("):source.index("void solveTXeqB(")]
    prob_line = _line(assembly, "one_minus_Pib = Dtau[b] > 1e-6")
    sv_line = _line(assembly, "sv[b]  =")
    marker = source.index("/* Update fminuses */")
    first = source.index("   for (b = 0; b < NVIRT; b++)", marker)
    final = source.index("\n", source.index("   Dfminus_Ly_hist[2][iz] =", first))
    outgoing = source[first:final]
    fragments = {**functions, "rhs_real_statements": real_lines,
                 "rhs_probability_statement": prob_line,
                 "rhs_virtual_statement": sv_line,
                 "outgoing_storage_statements": outgoing}
    evidence = {"hydrogen_c_sha256": SOURCE_SHA,
                "parameter_header_sha256": HEADER_SHA,
                "parameter_scope": "h4 header; manufactured history grid only, not saved native CSV time spacing",
                "fragments": {}}
    for name, fragment in fragments.items():
        raw = fragment.encode()
        (out / f"{name}.cfrag").write_bytes(raw)
        evidence["fragments"][name] = {"bytes": len(raw),
                                             "sha256": hashlib.sha256(raw).hexdigest(),
                                             "exact_substring_of_source": fragment in source}
    preamble = "#include <math.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
    preamble += "\n".join(defines) + "\ndouble square(double x) { return x*x; }\n"
    rhs_wrapper = """
void oracle_rhs(double RLya, double x1s, double *Dtau, double *tvv0,
                double *incoming, double *result) {
  double nH=0., s=0., Dxe2=0., Alpha[2]={0.,0.}, DAlpha[2]={0.,0.};
  double *Dfplus=incoming, *Dfplus_Ly=incoming+NVIRT;
  double *sr=result, *sv=result+2, *Tvv[3]={tvv0, tvv0, tvv0};
  double one_minus_Pib; unsigned b;
""" + real_lines + "  for(b=0;b<NVIRT;b++){\n" + prob_line + sv_line + "  }\n}\n"
    out_wrapper = """
void oracle_outgoing(double *X, double *incoming, double x1s, double TR,
                     double *Dtau, double *tvr, double *tvv, double *result) {
  double *xr=X, *xv=X+2, *Dfplus=incoming;
  double *Tvr[2]={tvr,tvr+NVIRT};
  double *Tvv[3]={tvv,tvv+NVIRT,tvv+2*NVIRT};
  double *Dfminus_hist[NVIRT], *Dfminus_Ly_hist[3];
  double one_minus_Pib, Dfeq, one_minus_exptau; unsigned b,iz=0;
  for(b=0;b<NVIRT;b++) Dfminus_hist[b]=result+b;
  for(b=0;b<3;b++) Dfminus_Ly_hist[b]=result+NVIRT+b;
""" + outgoing + "\n}\n"
    map_wrapper = """
double oracle_dlna(void) { return DLNA; }
void oracle_mapping(double *history, unsigned cols, unsigned iz, double zstart,
                    double z, double *energy, double *result) {
  double *bins[NVIRT], *lines[3]; unsigned b;
  for(b=0;b<NVIRT;b++) bins[b]=history+b*cols;
  for(b=0;b<3;b++) lines[b]=history+(NVIRT+b)*cols;
  fplus_from_fminus(result,result+NVIRT,bins,lines,0.,zstart,iz,z,energy);
}
"""
    c_text = preamble + "\n".join(functions.values()) + rhs_wrapper + out_wrapper + map_wrapper
    c_path = out / "native_oracle.c"
    c_path.write_text(c_text)
    evidence["wrapper_sha256"] = hashlib.sha256(c_path.read_bytes()).hexdigest()
    (out / "EXTRACTION.json").write_text(json.dumps(evidence, indent=2) + "\n")
    return c_path, evidence


class NativeOracle:
    def __init__(self, path: Path, evidence: dict):
        self.path, self.evidence = path, evidence
        self.lib = ctypes.CDLL(str(path))
        ptr = ctypes.POINTER(ctypes.c_double)
        self.ptr = ptr
        self.lib.interp_Dfnu.argtypes = [ctypes.c_double, ctypes.c_double, ptr,
                                        ctypes.c_uint, ctypes.c_double]
        self.lib.interp_Dfnu.restype = ctypes.c_double
        self.lib.oracle_mapping.argtypes = [ptr, ctypes.c_uint, ctypes.c_uint,
                                           ctypes.c_double, ctypes.c_double, ptr, ptr]
        self.lib.oracle_mapping.restype = None
        self.lib.oracle_rhs.argtypes = [ctypes.c_double, ctypes.c_double, ptr, ptr, ptr, ptr]
        self.lib.oracle_rhs.restype = None
        self.lib.oracle_outgoing.argtypes = [ptr, ptr, ctypes.c_double, ctypes.c_double,
                                            ptr, ptr, ptr, ptr]
        self.lib.oracle_outgoing.restype = None
        self.lib.oracle_dlna.argtypes = []
        self.lib.oracle_dlna.restype = ctypes.c_double
        self.h = self.lib.oracle_dlna()

    def _array(self, x):
        return np.ascontiguousarray(x, dtype=np.float64)

    def _p(self, x):
        return x.ctypes.data_as(self.ptr)

    def interpolate(self, eta0, h, values, iz, eta):
        y = self._array(values)
        return self.lib.interp_Dfnu(eta0,h,self._p(y),iz,eta)

    def mapping(self, history, iz, zstart, z, energies):
        hist, e = self._array(history), self._array(energies)
        out = np.zeros(313)
        self.lib.oracle_mapping(self._p(hist),hist.shape[1],iz,zstart,z,self._p(e),self._p(out))
        return out

    def rhs(self, r0, x1s, dtau, tvv0, incoming):
        args = [self._array(x) for x in (dtau,tvv0,incoming)]
        out = np.zeros(313)
        self.lib.oracle_rhs(r0,x1s,*[self._p(x) for x in args],self._p(out))
        return out

    def outgoing(self, X, incoming, x1s, TR, dtau, tvr, tvv):
        args = [self._array(x) for x in (X,incoming,dtau,tvr,tvv)]
        out = np.zeros(314)
        self.lib.oracle_outgoing(self._p(args[0]),self._p(args[1]),x1s,TR,
                                 *[self._p(x) for x in args[2:]],self._p(out))
        return out


def build_oracle(output_dir: Path) -> NativeOracle:
    out = Path(output_dir) / "native_oracle"
    out.mkdir(parents=True, exist_ok=False)
    c_path, evidence = _extract(out)
    compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if compiler is None:
        raise RuntimeError("COMPILER_MISSING")
    so_path = out / "native_oracle.so"
    command = [compiler,"-std=c11","-O2","-fPIC","-shared",str(c_path),"-lm","-o",str(so_path)]
    run = subprocess.run(command,capture_output=True,text=True,timeout=20,check=False)
    (out / "compile.stdout").write_text(run.stdout)
    (out / "compile.stderr").write_text(run.stderr)
    evidence["compile_command"] = command
    evidence["compile_exit_code"] = run.returncode
    (out / "BUILD.json").write_text(json.dumps(evidence,indent=2) + "\n")
    if run.returncode:
        raise RuntimeError(f"finite C oracle compilation failed: {run.stderr}")
    return NativeOracle(so_path,evidence)
