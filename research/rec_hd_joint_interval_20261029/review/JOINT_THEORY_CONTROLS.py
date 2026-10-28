from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
# New independent review controls: shortest-path negative-cycle criterion vs
# direct all-segment conditions, including exact zero radii and lambda=0.
def bellman(delta,r,s,lam):
 n=len(delta); z=n+1;N=n+2;edges=[]
 for j in range(n+1):
  edges.extend([(z,j,lam*r[j]),(j,z,lam*r[j])])
 for j in range(1,n+1):
  edges.extend([(j-1,j,-delta[j-1]+lam*s[j-1]),(j,j-1,delta[j-1]+lam*s[j-1])])
 dist=[Q(0)]*N
 for it in range(N):
  changed=False
  for u,v,w in edges:
   if dist[v]>dist[u]+w:
    dist[v]=dist[u]+w;changed=True
  if not changed:return True
 return False
def segments(delta,r,s,lam):
 for p in range(len(delta)):
  D=S=Q(0)
  for q in range(p+1,len(delta)+1):
   D+=delta[q-1];S+=s[q-1]
   if abs(D)>lam*(r[p]+r[q]+S):return False
 return True
checked=0
# exhaustive tiny n=2 domain: 3^2*2^3*2^2*4=1152 cases
for delta in product(map(Q,[-1,0,1]),repeat=2):
 for r in product(map(Q,[0,1]),repeat=3):
  for s in product(map(Q,[0,1]),repeat=2):
   for lam in map(Q,[0,Q(1,2),1,2]):
    a=bellman(delta,r,s,lam);b=segments(delta,r,s,lam)
    assert a==b,(delta,r,s,lam,a,b);checked+=1
record={'reviewer':'/root/independent_hd_review','scope':'new independent exact tiny negative-cycle-vs-segment controls, not prior HD campaign','domain':{'n':2,'delta':[-1,0,1],'r':[0,1],'s':[0,1],'lambda':['0','1/2','1','2']},'cases':checked,'agreement':True,'zero_radius_zero_defect':segments([Q(0),Q(0)],[Q(0)]*3,[Q(0)]*2,Q(0)),'zero_radius_nonzero_defect':segments([Q(1)],[Q(0)]*2,[Q(0)],Q(1)),'same_sign_counterexample_at_one':segments([Q(1),Q(1)],[Q(1,2)]*3,[Q(0)]*2,Q(1)),'same_sign_counterexample_at_two':segments([Q(1),Q(1)],[Q(1,2)]*3,[Q(0)]*2,Q(2)),'opposite_sign_control':segments([Q(1),Q(-1)],[Q(1,2)]*3,[Q(0)]*2,Q(1))}
Path('/workspace/scratch/e0012d8fd22a/review/JOINT_THEORY_CONTROLS.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
