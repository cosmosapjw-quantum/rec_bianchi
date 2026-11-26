"""Advective narrow-band line-cell QSS with geometry-owned redshift rate."""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3j_integrated_history'))
from line_cell import phase,A21,EL
sys.path.insert(0,str(D.parent/'r118c3i_event_quadrature'))
from line_pair import LY
B=Path.home()/'worktrees/bass-r109-native-20261124/research/r118c3e_geometry_tracks/plusfine.csv'
def run():
 z=np.load(D.parent/'r118c3j_integrated_history/mid1024_1.npz');L=z['line'];g=np.genfromtxt(B,names=True,delimiter=',');u=np.log(g['a'])
 rows=[]
 for j in np.unique(np.linspace(0,len(L)-1,33).astype(int)):
  t,x,p,fin,nh,Tr=L[j];Tm=z['rows'][j+1,2];H=np.interp(t,u,g['h'])*2.1842852410855023e-18
  width=np.sqrt(2*1.380649e-23*Tm/(1.6735575e-27*299792458.**2));C=phase(nh,width);k=H/width;KC=k*C
  tau=A21*(3*x-p)/KC
  # Stable difference f*-fin and net rate; avoid cancellation near equilibrium.
  num=p-(3*x-p)*fin;diff=A21*num/(A21*(3*x-p)+KC);net=KC*diff
  native=LY*H/(nh*1e-6*x)*num
  rows.append(dict(u=float(t),k=float(k),C=float(C),tau=float(tau),rate_ratio=float(net/native),prefactor_ratio=float(KC/(3*x)/(LY*H/(nh*1e-6*x))),net=float(net),fstar=float(fin+diff)))
  assert fin+diff>=0 and tau>0
 o=dict(rows=rows,scope='fixed actual atom population and angular-weighted input; direction H_n enters k, here mean H; uniform-band advective QSS, not complete Sobolev transfer')
 (D/'LINE.json').write_text(json.dumps(o,indent=2)+'\n');print('ratio',min(q['rate_ratio'] for q in rows),max(q['rate_ratio'] for q in rows),'tau',min(q['tau'] for q in rows),max(q['tau'] for q in rows),'prefactor',rows[0]['prefactor_ratio'])
if __name__=='__main__':run()
