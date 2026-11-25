"""Audit actual graph/trajectory bytes and finite claims, no new science admission."""
import argparse,hashlib,json,gzip,re
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable,A2S_THRESHOLD_EV
p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--compiled',type=Path,required=True);a=p.parse_args()
D=Path(__file__).resolve().parent;repo=D.parents[1];L=np.longdouble
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
archive=repo/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
tab=OriginalHyRecTwoPhotonRamanTable.from_archive(archive);sources=[];allcases=[];graphs=[];state_error=0.;neterr=0.
for bath in ('z1100','z1300','z900'):
 r=a.raw/bath;v=json.loads((r/'RESULTS.json').read_text())
 assert (a.raw/(bath+'.exit')).read_text().strip()=='0'
 assert sha(a.compiled/(bath+'.npz'))==v['source_sha256'] and sha(archive)==v['rate_sha256'] and sha(r/'QUAD.npz')==v['quad_sha256']
 assert [g['n'] for g in v['graphs']]==[16,32,64,128]
 err=[max(q['relative'] for q in g['action']) for g in v['graphs']]
 assert all(x>y for x,y in zip(err,err[1:])) and err[-1]<.001
 for g in v['graphs']:
  n=g['n'];assert g['original_blocks']==459 and g['relifted_blocks']==34 and g['new_blocks']==6
  assert g['coarse_error']<1e-10 and g['moment_error']<1e-10 and g['thermal_error']<1e-12
  with np.load(r/f'GRAPH{n}.npz') as z:
   i,j,K=z['i'],z['j'],z['K'];assert len(i)==len(j)==len(K)==g['edges']
   assert np.all(i<j) and len(set(zip(i,j)))==len(i) and np.min(K)>0
   assert np.min(z['gt'])>0 and np.min(z['gc'])>0
   ev=z['events'];ti,ci,sg,rr,oi=ev.T;ti=ti.astype(int);ci=ci.astype(int);oi=oi.astype(int)
   assert np.all(abs(z['et'][ti]+sg*z['ec'][ci]-L(A2S_THRESHOLD_EV))<1e-16)
   rates=np.zeros(311,dtype=L);en=rates.copy();np.add.at(rates,oi,rr);np.add.at(en,oi,rr*z['et'][ti])
   assert np.max(abs(rates-tab.A2s_s_inv)/np.maximum(tab.A2s_s_inv,1e-300))<2e-15
   assert np.max(abs(en-tab.A2s_s_inv*tab.energy_eV)/np.maximum(tab.A2s_s_inv*tab.energy_eV,1e-300))<2e-15
  g['graph_sha256']=sha(r/f'GRAPH{n}.npz');graphs.append(g)
 for c in v['cases']:
  name=c['case'];assert c['max_N']<1e-11 and c['max_E']<1e-11
  assert sha(r/(name+'.npz'))==c['state_sha256']
  c['history_sha256']=sha(r/(name+'.json'))
  hist=json.loads((r/(name+'.json')).read_text());assert len(hist)==c['steps']
  if c['kind']!='thermal':neterr=max(neterr,max(x['scatter']['net_energy_relative'] for x in hist))
  with np.load(r/(name+'.npz')) as z:
   assert np.min(z['nt']+z['dt'])>=0 and np.min(z['nc']+z['dc'])>=0 and 0<=z['n2']+z['d2']<=z['neutral']
   dn=z['dt']-z['initial_dt'];dc=z['dc']-z['initial_dc'];da=z['d2']-z['initial_d2'];t=c['terminal'];scale=L(t['gross'])
   res=dn@z['et']+dc@z['ec']+L(A2S_THRESHOLD_EV)*da+L(t['bath_energy'])
   state_error=max(state_error,float(abs(res)/(scale*L(A2S_THRESHOLD_EV))))
   assert abs(np.sum(dn)+da)/scale<1e-11 and abs(res)/(scale*L(A2S_THRESHOLD_EV))<1e-11
  allcases.append(c)
 if bath=='z1100':
  refs=sorted(v['reference'],key=lambda x:x['steps']);assert [x['steps'] for x in refs]==[1,2,4,8,16]
  e=[x['delta_n2_relative'] for x in refs];assert all(1.9<x/y<2.1 for x,y in zip(e,e[1:]))
 sources.append(v)
 (D/(bath+'_RESULTS.json')).write_text(json.dumps(v,indent=2)+'\n')
assert len(graphs)==12 and len(allcases)==40 and sum(c['steps'] for c in allcases)==147
logs={}
for f in ['/tmp/r118c2k_rec_red.log','/tmp/r118c2k_rec_green.log','/tmp/r118c2k_rec_py.log','/tmp/r118c2k_rec_rust.log']+[str(a.raw/(b+'.log')) for b in ('z1100','z1300','z900')]:
 p=Path(f);q=D/(p.name+'.gz');q.write_bytes(gzip.compress(p.read_bytes(),mtime=0));logs[q.name]=sha(q)
rt=Path('/tmp/r118c2k_rec_rust.log').read_text();n=sum(map(int,re.findall(r'test result: ok\. (\d+) passed',rt)));assert n==146 and 'test result: FAILED' not in rt
assert '16 passed' in Path('/tmp/r118c2k_rec_py.log').read_text()
out=dict(status='PASS_SCOPED',parent='7a1c593973ea74ccb13b987a30ebc1623f8b4cd4',scope='mixed physical registry; 34 relifted and 6 new blocks, fixed T/HII/2p; 0.1 s finite evolution',graphs=12,cases=40,steps=147,max_coarse=max(g['coarse_error'] for g in graphs),max_marginal=max(g['moment_error'] for g in graphs),max_phase=max(g['phase_error'] for g in graphs),max_thermal=max(g['thermal_error'] for g in graphs),max_action128=max(q['relative'] for g in graphs if g['n']==128 for q in g['action']),max_N=max(c['max_N'] for c in allcases),max_E=max(c['max_E'] for c in allcases),max_independent_E=state_error,max_nonthermal_net_scatter_error=neterr,reference=refs,rust_tests=n,python_tests=16,full_owner_swap='HOLD',raw=str(a.raw),files={f.name:sha(f) for f in D.iterdir() if f.is_file() and f.name!='ACCEPTANCE.json'})
(D/'ACCEPTANCE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2))
