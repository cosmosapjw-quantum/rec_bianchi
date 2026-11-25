"""Re-use actual C2K frozen graphs and initial states, not recompiled surrogates."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,Scatter
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"r118c2n_exact_extent"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2r_stable_extent"))
from extent_map import coupled_step, source_step, extent, ExtentRejected
from stable_extent import StableReaction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2o_stiff_scatter"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2q_activity_bath"))
from patankar_scatter import PatankarScatter
from stable_activity import StableScatter,bath_at
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2s_evolving"))
from evolving import ActualBath,KernelHistory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2t_cosmological"))
from drift import Redshift
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"r118c2m_adaptive_extent"))
from adaptive import estimate
p=argparse.ArgumentParser()
p.add_argument('--raw',type=Path,required=True);p.add_argument('--compiled',type=Path,required=True)
p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
p.add_argument('--bath',choices=['z900','z1100','z1300'],required=True);p.add_argument('--n',type=int,default=128)
p.add_argument('--kind',choices=['pulse','actual','thermal'],default='pulse')
p.add_argument('--duration',type=float,default=1.);p.add_argument('--clock',choices=['physical','accelerated'],required=True);a=p.parse_args()
def sha(f):
    with open(f,'rb') as g:return hashlib.file_digest(g,'sha256').hexdigest()
raw=a.raw/a.bath;prior=json.loads((raw/'RESULTS.json').read_text())
cf=a.compiled/(a.bath+'.npz');assert sha(cf)==prior['source_sha256'];assert sha(a.rates)==prior['rate_sha256']
with np.load(cf) as z:q=prepare({k:z[k] for k in z.files},4)
net=RefinedTwoS(a.rates,q,a.n)
gf=raw/f'GRAPH{a.n}.npz'
with np.load(gf) as g:
    for k in ('et','gt','ec','gc'):assert np.array_equal(g[k],getattr(net,k)),k
    assert np.array_equal(g['events'],np.array(net.events,dtype=L))
    edges=list(zip(g['i'],g['j'],g['K'],g['cross'],g['new']))
sc=Scatter(net,edges)
sf=raw/f'n{a.n}_{a.kind}_{2 if a.kind=="thermal" else 4}.npz'
row=next(x for x in prior['cases'] if x['case']==sf.stem)
assert sha(sf)==row['state_sha256']
with np.load(sf) as v:
    base=State(v['nt'],v['nc'],L(v['n2']),L(v['neutral']),v['initial_dt'].copy(),v['initial_dc'].copy(),L(v['initial_d2']))
nt,nc=len(base.nt),len(base.nc);scale=max(base.n2,L('1e-30'))
ii,jj,sg,rate,_=map(np.asarray,zip(*net.events));ii=ii.astype(int);jj=jj.astype(int);sg=sg.astype(L);rate=rate.astype(L)

assert a.bath=='z1100'
H=Path('/home/cosmosapjw/Downloads');D=Path(__file__).resolve().parent
states=json.loads((a.compiled/'STATES.json').read_text())['states']
anchor=states['z1100'];histpath=a.compiled/'z900_HISTORY.json';bh=ActualBath(json.loads(histpath.read_text())['states'],anchor)
r0=bh.point(anchor['z']);assert abs(r0['n1s']/q['n1s']-1)<1e-14
ends=[]
for name in ('end','mid'):
    p=H/('rec_r118c2s_'+name);r=json.loads((p/'RECEIPT.json').read_text())
    assert r['status']=='COMPILED_SAME_GRAPH' and r['history_sha']==sha(histpath) and r['rate_sha']==sha(a.rates)
    for f,h in r['hashes'].items():assert sha(p/f)==h
    g=np.load(p/'GRAPH128.npz')
    assert np.array_equal(g['i'],sc.i) and np.array_equal(g['j'],sc.j)
    ends.append((p,r,g['K']))
p1,rr1,k1=ends[0];pm,rrm,km=ends[1]
def beta(T):return -1/L(T)
K=KernelHistory([beta(rr1['bath']['T_m_K']),beta(anchor['T_m_K'])],[rr1['bath']['n1s'],q['n1s']],np.stack([k1,sc.K]))
mid=K(beta(rrm['bath']['T_m_K']),rrm['bath']['n1s'])
interp=dict(max_edge_rel=float(np.max(abs(mid/km-1))),global_l1=float(np.sum(abs(mid-km))/np.sum(km)),cross_l1=float(np.sum(abs(mid[sc.cross]-km[sc.cross]))/np.sum(km[sc.cross])),new_l1=float(np.sum(abs(mid[sc.new]-km[sc.new]))/np.sum(km[sc.new])))
assert interp['global_l1']<1e-5 and interp['new_l1']<1e-5
print('full local graph midpoint',interp,flush=True)


graphs=[]
for name in ('z900','z1100','z1300'):
 pp=a.raw/name/'GRAPH128.npz';gg=np.load(pp)
 for k in ('i','j','et','gt','ec','gc','events'):assert np.array_equal(gg[k],np.load(gf)[k]),k
 graphs.append((states[name],gg['K'],sha(pp)))
wide=KernelHistory([beta(graphs[k][0]['T_m_K']) for k in (0,2)],[graphs[k][0]['n_1s_m3'] for k in (0,2)],np.stack([graphs[k][1] for k in (0,2)]))
rows=[];sources={}
for name,pair in [('z1000',(0,1)),('z1200',(1,2))]:
 root=H/('rec_r118c2v_'+name);rec=json.loads((root/'RECEIPT.json').read_text());assert rec['status']=='COMPILED_SAME_GRAPH'
 for f,h in rec['hashes'].items():assert sha(root/f)==h
 gg=np.load(root/'GRAPH128.npz');T=rec['bath']['T_m_K'];den=rec['bath']['n1s'];ref=gg['K']
 for k in ('i','j','et','gt','ec','gc','events'):assert np.array_equal(gg[k],np.load(gf)[k]),k
 loc=KernelHistory([beta(graphs[k][0]['T_m_K']) for k in pair],[graphs[k][0]['n_1s_m3'] for k in pair],np.stack([graphs[k][1] for k in pair]))
 for kind,suffix in [('actual',4),('pulse',4),('thermal',2)]:
    f=raw/f'n128_{kind}_{suffix}.npz';priorcase=next(x for x in prior['cases'] if x['case']==f.stem);assert sha(f)==priorcase['state_sha256']
    with np.load(f) as v:state=State(v['nt'],v['nc'],L(v['n2']),L(v['neutral']),v['initial_dt'].copy(),v['initial_dc'].copy(),L(v['initial_d2']))
    nb,sb=bath_at(net,sc,state,T);nb.q['n1s']=den;sb.K=ref;f0,g0=sb.rates(state);gross=np.sum(g0)
    for key,ka in [('wide',wide(beta(T),den)),('refined',loc(beta(T),den))]:
       sb.K=ka;f1,g1=sb.rates(state);diff=f1-f0;d=np.zeros(nt,dtype=L);np.add.at(d,sc.i,diff);np.add.at(d,sc.j,-diff)
       row=dict(holdout=name,probe=kind,scope=key,K_l1=float(np.sum(abs(ka-ref))/np.sum(ref)),divergence_over_gross=float(np.sum(abs(d))/gross),new_energy_relative=float(abs(diff[sc.new]@sc.de[sc.new])/max(abs(f0[sc.new]@sc.de[sc.new]),L('1e-4900'))),state_sha=sha(f))
       rows.append(row);print(row,flush=True)
 sources[name]=dict(receipt_sha=sha(root/'RECEIPT.json'),hashes=rec['hashes'],bath=rec['bath'])
a.out.write_text(json.dumps(dict(status='SCOPED_TWO_FULL_GRAPH_HOLDOUTS',scope='actual HMLA bath at z1000,1200, held-out full graph; fixed z1100 three state probes, not actual evolved stocks at holdout bath',sources=sources,anchors_sha=[x[2] for x in graphs],rows=rows),indent=2)+'\n')
