"""Generate an independent finer native reference in this cycle only."""
import sys,importlib.util
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent
sys.path.insert(0,str(P/'r118c3p_prehistory'))
import prehistory as p
p.D=D;p.run(False,4,128,'z1110_n128_0',1110.)
# Reconstruct original accepted outgoing and first impulse histories using
# identical source functions, writing only to current research scope.
sys.path.insert(0,str(P/'r118c3r_retarded_tangent'))
import frozen as f
f.D=D;f.P=D;f.run(128,1110)
sys.path.insert(0,str(P/'r118c3s_impulse_tangent'))
path=P/'r118c3s_impulse_tangent/impulses.py'
s=path.read_text().replace("prior=D.parent/'r118c3r_retarded_tangent';","prior=D;").replace("refpath=D.parent/f'r118c3p_prehistory/z1110_n{nt}_0.npz'","refpath=D/f'z1110_n{nt}_0.npz'")
ns={'__file__':str(D/'impulses_refine.py'),'__name__':'refined_impulses'};exec(s,ns);ns['run'](128)
