"""Source-authentic HD neutral rotational lab anchor graph, 1984+2022.

No CDMS v3, no inverse fit, no assumed source covariance, no production switch.
All decimal-source literals are accepted only under their pinned SHA256.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from decimal import Decimal as D, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = D(299792458)  # exact SI m/s
H = D('6.62607015e-34')  # exact SI J s
KB = D('1.380649e-23') # exact SI J/K
HZ_CM = 100*C
SOURCES = {
 'source/LAB_1984_ANCHORS.json': '670bc546ea5c35a103325a119ade1766906aed24492a38150cc631169ef2675f',
 'source/LAB_2022_FROZEN.json': '831129e12774e75846ebdb13a50db70c0ace1b16545fec9504bb6388e4f7a882',
 'pinned/CDMS2011_V2_EGY_TRANSCRIPTION_PR162.json': '8ebb7e640e965694c720c74fbacec97b487c471019707194f3ef2c97df4a8e13',
 'pinned/LAMDA_HD_SOURCE_TRANSCRIPTION_PR161.json': 'd44406daf59616c982ca7a33bb3ee962138130588dfb74c7b801972c933da796'
}

def read_sources(root=ROOT):
 out={}
 for name,expected in SOURCES.items():
  raw=(Path(root)/name).read_bytes()
  if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError(f'SOURCE_IDENTITY_MISMATCH: {name}')
  out[name]=json.loads(raw.decode('utf-8'))
 return out

def rank_exact(matrix):
 # integer incidence, finite Gaussian elimination using Fraction for exact rank.
 from fractions import Fraction
 a=[[Fraction(v) for v in row] for row in matrix]
 m=len(a); n=len(a[0]) if m else 0; r=0
 for col in range(n):
  pivot=next((j for j in range(r,m) if a[j][col]),None)
  if pivot is None: continue
  a[r],a[pivot]=a[pivot],a[r]
  v=a[r][col];a[r]=[x/v for x in a[r]]
  for j in range(m):
   if j!=r and a[j][col]:
    q=a[j][col];a[j]=[x-q*y for x,y in zip(a[j],a[r])]
  r+=1
 return r

def components(edges,n=9):
 adj=[set() for _ in range(n)]
 for u,l in edges: adj[u].add(l);adj[l].add(u)
 found=set();out=[]
 for s in range(n):
  if s not in found:
   todo=[s];block=[]
   while todo:
    j=todo.pop()
    if j in found:continue
    found.add(j);block.append(j);todo.extend(sorted(adj[j]-found))
   out.append(sorted(block))
 return sorted(out,key=lambda x:x[0])

def incidence(u,l):
 a=[0]*9;a[u]=1;a[l]=-1;return a

def dec(s):return format(s,'f')

def compute(source):
 with localcontext() as ctx:
  ctx.prec=68
  lab84=source['source/LAB_1984_ANCHORS.json'];lab22=source['source/LAB_2022_FROZEN.json']
  cdms=source['pinned/CDMS2011_V2_EGY_TRANSCRIPTION_PR162.json'];lam=source['pinned/LAMDA_HD_SOURCE_TRANSCRIPTION_PR161.json']
  if lab84['schema']!='REC_HD_GROUND_ROTATIONAL_PRIMARY_1984_V1' or lab84['doi']!='10.1139/p84-213':raise ValueError('1984 wrong source')
  if not (lab84['source_representation'].startswith('PUBLISHER_PRIMARY_ABSTRACT') and len(lab84['measurements'])==3):raise ValueError('1984 source role')
  if cdms['raw_file_obtained'] is not False or lam['exact_source_bytes_acquired'] is not False:raise ValueError('Unexpected raw-source role')
  if [x['J'] for x in cdms['levels']]!=list(range(9)) or [x['upper_J'] for x in lam['radiative_lines']]!=list(range(1,9)):raise ValueError('J ordering mismatch')
  cdms_E=[D(x['E_cm1']) for x in cdms['levels']]
  rad=lam['radiative_lines'];photons=[D(x['nu_GHz'])*10**9 for x in rad]
  obs=[]; rows=[];lte=[]
  for x in lab22['source_original_publications']:
   u=x['upper_J']; l=x['lower_J']; y=D(x['measured_Hz']);sig=D(x['reported_uncertainty_Hz'])
   obs.append((u,l,y,sig,'2022',x['doi']))
  for x in lab84['measurements']:
   u=x['upper_J'];l=x['lower_J'];y=D(x['wavenumber_cm1'])*HZ_CM;sig=D(x['reported_uncertainty_cm1'])*HZ_CM
   if u-l!=1 or x['line']!=f'R({l})':raise ValueError('1984 R(J) quantum assignment mismatch')
   obs.append((u,l,y,sig,'1984',lab84['doi']))
  if len(obs)!=5:raise ValueError('five direct lab constraints required')
  inc=[incidence(u,l) for u,l,*_ in obs]; groups=components([(u,l) for u,l,*_ in obs]); r=rank_exact(inc)
  inca=inc+[incidence(1,0)];groupsa=components([(u,l) for u,l,*_ in obs]+[(1,0)])
  if r!=5 or len(groups)!=4 or rank_exact(inca)!=6 or len(groupsa)!=3:raise ValueError('Graph physics rank/connected components mismatch')
  for u,l,y,sig,year,doi in obs:
   modelp=sum(photons[l:u],D(0));egy=(cdms_E[u]-cdms_E[l])*HZ_CM
   a = D(rad[u-1]['A_s1']) if u-l==1 else None
   row={'uJ':u,'lJ':l,'experiment':year,'source_DOI':doi,'measured_Hz':dec(y),'reported_measurement_uncertainty_Hz':dec(sig),'measured_minus_2021_photon_Hz':dec(y-modelp),'measured_minus_2011_v2_printed_egy_Hz':dec(y-egy),'source_2021_photon_sum_Hz':dec(modelp),'cdms_2011_printed_egy_Hz':dec(egy),'model_covariance':None,'lab_joint_covariance':None,'source_residual_is_statistical_sigma':False,'einstein_A_2021_s_inv':dec(a) if a else None}
   if a is not None:
    row.update({'photon_energy_J':dec(H*y),'wavelength_m':dec(C/y),'spontaneous_power_per_upper_HD_W':dec(a*H*y),'spontaneous_lifetime_s':dec(1/a)})
    for temperature in (50,100,200):
     t=D(temperature)
     ratio=D(2*u+1)/D(2*l+1)*(-(H*y)/(KB*t)).exp()
     lte.append({'uJ':u,'lJ':l,'T_K':temperature,'LTE_n_upper_over_lower':dec(ratio),'physical_status':'CONDITIONAL_LTE_NOT_OBSERVED','lab_measurement_year':year})
   rows.append(row)
  # 2011 nominal J1-0 is an inherited source anchor, not a new direct 1984/2022 measurement.
  x=photons[0];v20=obs[0][2];v31=obs[1][2];v43=obs[2][2]
  anchored_levels=[D(0),x,v20,x+v31,x+v31+v43]
  source_prefix=[D(0)]
  for p in photons[:4]:source_prefix.append(source_prefix[-1]+p)
  conditional=[{'J':j,'nominal_anchored_E_minus_E0_Hz':dec(e),'difference_from_inherited_photon_cumulative_Hz':dec(e-source_prefix[j]),'status':'CONDITIONAL_ON_2011_NOMINAL_J1_0_AND_INCOMPLETE_COVARIANCE'} for j,e in enumerate(anchored_levels)]
  return {'schema':'REC_HD_1984_2022_MEASURED_ROTATIONAL_GRAPH_V1','new_primary_1984_measurements':3,'reused_2022_measurements':2,'source_2011_nominal_anchor_edges':1,'measurement_graph_rank':r,'measurement_graph_nullity':9-r,'measurement_graph_components':groups,'with_2011_nominal_anchor_rank':rank_exact(inca),'with_2011_nominal_anchor_nullity':9-rank_exact(inca),'with_2011_nominal_anchor_components':groupsa,'missing_physical_observation_bridge_edges_given_anchor':[[5,4],[8,7]],'experimental_rows':rows,'experimental_LTE_rows':lte,'conditional_lowJ_levels':conditional,'source_covariance':None,'lab_cross_covariance':None,'original_CDMS_2011_v2_raw_bytes':None,'source_2021_LAMDA_raw_bytes':None,'old_35Hz':'FAIL7/8_PRESERVED','parent_PR162':'4d60f74db02d7435add062eaefb15739e68c4b55','canonical_DAG':'28/88','REC_physical_DAG':'0/313','production':'HOLD'}

def write_csv(path,records):
 if not records:return
 with open(path,'w',encoding='utf-8',newline='') as handle:
  fields=list(dict.fromkeys(k for row in records for k in row))
  wr=csv.DictWriter(handle,fieldnames=fields,lineterminator='\n');wr.writeheader();wr.writerows(records)

def save(result,outdir):
 outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
 (outdir/'MEASURED_ROTATIONAL_GRAPH.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 write_csv(outdir/'EXPERIMENTAL_LINE_ATLAS.csv',result['experimental_rows'])
 write_csv(outdir/'CONDITIONAL_LTE.csv',result['experimental_LTE_rows'])
 write_csv(outdir/'CONDITIONAL_LOWJ_LEVELS.csv',result['conditional_lowJ_levels'])

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path,default=ROOT/'evidence'); a=parser.parse_args()
 save(compute(read_sources(a.root)),a.output)
