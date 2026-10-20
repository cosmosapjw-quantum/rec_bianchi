"""Diagnostic-only original R3Q worker with inherited hard limits retained."""
import cProfile
import json
from pathlib import Path
import resource
import runpy
import sys

output = Path(sys.argv[1])
target = sys.argv[2]
sys.argv = sys.argv[2:]
original_setrlimit = resource.setrlimit
applied = []

def bounded_setrlimit(kind, limits):
    inherited = resource.getrlimit(kind)
    def smaller(a, b):
        if a == resource.RLIM_INFINITY:
            return b
        if b == resource.RLIM_INFINITY:
            return a
        return min(a, b)
    hard = smaller(limits[1], inherited[1])
    soft = smaller(smaller(limits[0], inherited[0]), hard)
    original_setrlimit(kind, (soft, hard))
    applied.append({'resource': kind, 'requested': list(limits),
                    'inherited': list(inherited), 'applied': [soft, hard]})

resource.setrlimit = bounded_setrlimit
profiler = cProfile.Profile()
try:
    profiler.runcall(runpy.run_path, target, run_name='__main__')
finally:
    resource.setrlimit = original_setrlimit
    profiler.dump_stats(str(output / 'worker.pstats'))
    (output / 'inherited_limit_clamps.json').write_text(json.dumps(applied, indent=2)+'\n')
