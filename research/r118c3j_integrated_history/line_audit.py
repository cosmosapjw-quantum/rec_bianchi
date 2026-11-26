"""Closed physical Ly-alpha cell diagnostics from actual accepted midpoint outputs."""
from pathlib import Path
import numpy as np,json
from line_cell import evolve,phase,EL,A21
D=Path(__file__).resolve().parent
def run():
 rows=[]
 for file in sorted(D.glob('mid*.npz')):
  z=np.load(file);a=z['rows'];L=z['line'];assert len(L)==len(a)-1
  res=np.diff(a[:,1])-np.diff(a[:,0])*a[1:,4]
  assert np.max(abs(res))<1e-12
  errs=[];sem=[];eqerr=[];flows=[];max_pop=0.
  for j in np.unique(np.linspace(0,len(L)-1,17).astype(int)):
   u,x1,p,f,nh,Tcmb=L[j];T=a[j+1,2];dlog=np.sqrt(2*1.380649e-23*T/(1.6735575e-27*299792458.**2))
   C=phase(nh,dlog);n=C*f;X=x1+p
   assert p>=0 and n>=0
   dt=1/A21;aa,bb,d,root=evolve(p,n,X,C,dt)
   a2,b2,_,_=evolve(aa,bb,X,C,dt);a3,b3,_,_=evolve(p,n,X,C,2*dt)
   errs.append(abs((aa+bb)-(p+n))/max(p+n,1e-300))
   sem.append(max(abs(a2-a3),abs(b2-b3))/max(p+n,1e-300))
   # Stable thermal detailed balance at local radiation temperature, with same ground population and C.
   b0=np.exp(-EL/(8.617333262145e-5*Tcmb));pe=3*x1*b0;ne=C*b0/(1-b0)
   _,_,de,_=evolve(pe,ne,x1+pe,C,dt);eqerr.append(abs(de)/max(pe+ne,1e-300))
   flows.append(float(d));max_pop=max(max_pop,p)
  out=dict(label=file.stem,rows=len(L),max_integrated_x_res=float(np.max(abs(res))),max_number_energy_relative=max(errs),max_semigroup_relative=max(sem),max_thermal_balance_relative=max(eqerr),transfer_range=[min(flows),max(flows)],max_excited_population=max_pop)
  assert out['max_number_energy_relative']<1e-12 and out['max_semigroup_relative']<1e-10 and out['max_thermal_balance_relative']<1e-10
  rows.append(out)
 o=dict(rows=rows,scope='closed single Doppler-width line band, actual accepted endpoint samples, no cosmological escape, no line feedback into original atom')
 (D/'LINE_AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
