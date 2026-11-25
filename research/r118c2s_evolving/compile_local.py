import argparse,json,hashlib,time
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.recoil.calibrated_source import Bath,compile_isotropic
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,compile_integrals,assemble,Scatter
from evolving import ActualBath
P=argparse.ArgumentParser();P.add_argument('--offset',type=float,required=True);P.add_argument('--out',type=Path,required=True);a=P.parse_args();a.out.mkdir(exist_ok=False)
H=Path('/home/cosmosapjw/Downloads/rec_r118c2f_compiled_final');rates=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
st=json.loads((H/'STATES.json').read_text())['states']['z1100'];hist=json.loads((H/'z900_HISTORY.json').read_text())['states'];bh=ActualBath(hist,st)
z=st['z']-a.offset;v=bh.point(z);bath=Bath(v['T_m_K'],v['n1s']);t=time.monotonic()
data=compile_isotropic(bath,(4,),2);np.savez_compressed(a.out/'SOURCE.npz',**data)
print('source compiled',z,time.monotonic()-t,flush=True)
q=prepare(data,4);net=RefinedTwoS(rates,q,128);integ=compile_integrals(net,bath);edges,report=assemble(net,data,integ);sc=Scatter(net,edges)
np.savez_compressed(a.out/'GRAPH128.npz',i=sc.i,j=sc.j,K=sc.K,new=sc.new,cross=sc.cross,et=net.et,gt=net.gt,ec=net.ec,gc=net.gc,events=np.array(net.events,dtype=np.longdouble),parent_offsets=net.offset,bounds=net.bounds)
with np.load('/home/cosmosapjw/Downloads/rec_r118c2k_refined/z1100/GRAPH128.npz') as g,np.load(a.out/'GRAPH128.npz') as w:
 for k in ('et','gt','ec','gc','events','i','j','new','cross','bounds','parent_offsets'):assert np.array_equal(g[k],w[k]),k
out=dict(status='COMPILED_SAME_GRAPH',z=z,bath=v,report=report,seconds=time.monotonic()-t,history_sha=sha(H/'z900_HISTORY.json'),states_sha=sha(H/'STATES.json'),rate_sha=sha(rates),hashes={p.name:sha(p) for p in a.out.iterdir() if p.is_file()})
(a.out/'RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n');print('complete',z,out['seconds'],len(sc.K),flush=True)
