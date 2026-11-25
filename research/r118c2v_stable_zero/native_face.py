"""Frozen original FULL incoming-face distortion, not HMLA history closure."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.constants import e,h,c,k
from scipy.sparse import bmat,csr_matrix
from scipy.sparse.linalg import expm_multiply
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import parse_original_hyrec_snapshot_csv,physical_log_mode_factor_per_H,SOURCE_HPC_EV_CM
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'r118c2u_boundaries'))
from boundary import JoinedDrift,L
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=Path('research/rec_line_native_owner_20261023/inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv')
assert sha(p)=='3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7'
s=parse_original_hyrec_snapshot_csv(p);assert s.fsR==1 and s.meR==1
H=Path('/home/cosmosapjw/Downloads/rec_r118c2k_refined/z1100')
g=np.load(H/'GRAPH128.npz');v=np.load(H/'n128_pulse_4.npz')
n=np.r_[v['nt']+v['initial_dt'],v['nc']+v['initial_dc']].astype(L);d=JoinedDrift(g['et'],g['gt'],g['ec'],g['gc'])
E=d.e.max();assert E==L(s.energy_eV[-1])
delta=L(s.Dfplus[-1]);bb=1/np.expm1(E/L(s.TR_eV_rescaled))
fac=L(8*np.pi)*(L(e)*E/(L(h)*L(c)))**3
oldfactor=L(physical_log_mode_factor_per_H(s)[-1])*L(s.nH_cm3)*1e6
modern_relative=float(fac/oldfactor-1)
# Source owner used its historical hc in eV cm; preserve that physical
# normalization, rather than requiring equality to modern SI constants.
fac=L(8*np.pi)*(E/L(SOURCE_HPC_EV_CM))**3*L(1e6)
assert abs(fac/oldfactor-1)<2e-15
print('modern SI vs original mode factor',modern_relative,flush=True)
rows=[]
for name,du in [('native_physical_1s',s.H_s_inv),('frozen_diagnostic_du',1e-4)]:
 for mode,occupation in [('planck',bb),('native_incoming',bb+delta)]:
    influx=fac*occupation;dx,l=d.affine(n,np.zeros_like(n),L(du),influx)
    nd=abs(dx.sum()+l['escape_N']-l['in_N'])/n.sum()
    ed=abs(dx@d.e+l['escape_U']+l['work']-l['in_U'])/(n@d.e)
    b=np.zeros(len(n)+3);b[d.top]=np.asarray(influx*d.topw,float)
    A=bmat([[d.matrix(),csr_matrix(b[:,None])],[csr_matrix((1,len(b))),csr_matrix((1,1))]],format='csr')
    # Isolate the incoming response by starting from exact zero. A full-stock
    # relative error would completely hide the very small physical influx.
    xx,ll=d.affine(np.zeros_like(n),np.zeros_like(n),L(du),influx)
    ref=expm_multiply(A*du,np.r_[np.zeros(len(n)+3),1.])
    er=float(np.sum(abs(xx-ref[:len(n)]))/max(np.sum(abs(ref[:len(n)])),L('1e-4900')))
    assert max(nd,ed)<1e-14 and er<1e-11 and np.min(n+dx)>=0
    row=dict(case=name,mode=mode,du=du,influx=float(influx),in_N=float(l['in_N']),in_U=float(l['in_U']),number_defect=float(nd),energy_defect=float(ed),incoming_response_relative=er)
    rows.append(row);print(row,flush=True)
out=dict(status='PASS_SCOPED_NATIVE_FROZEN_FACE',snapshot_sha=sha(p),graph_sha=sha(H/'GRAPH128.npz'),initial_state_sha=sha(H/'n128_pulse_4.npz'),native_z=s.z,graph_z=1099.7154650522846,energy=float(E),native_Dfplus=float(delta),planck=float(bb),occupation_ratio=float((bb+delta)/bb),native_constant_relative=float(fac/oldfactor-1),modern_SI_relative=modern_relative,rows=rows,scope='original FULL snapshot at its actual top face and actual H; graph from nearby HMLA bath held fixed; frozen boundary diagnostic not causal evolving FULL closure')
(D/'NATIVE_FACE.json').write_text(json.dumps(out,indent=2)+'\n');print('ratio',out['occupation_ratio'])
