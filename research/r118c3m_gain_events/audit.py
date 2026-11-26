"""Reconstruct all matched gas residuals and separate clock, grid and event-history effects."""
import json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={};checks={}
 for p in sorted(D.glob('weighted*.npz'))+sorted(D.glob('aligned*.npz')):
  z=np.load(p);a=z['rows'];assert np.all(np.diff(a[:,0])>0) and np.all(a[:,7]>0)
  res=np.diff(a[:,1])-np.diff(a[:,0])*a[1:,4];checks[p.stem]=float(max(abs(res)));assert checks[p.stem]<1e-12
 for name,fmt in [('bass128_32','weighted128_{}_bass'),('bass256_32','weighted256_{}_bass'),('flrw128_32','weighted128_{}_flrw'),('bass128_128','weighted128_{}_bass_128ray'),('aligned','aligned128_{}')]:
  a,b=[json.loads((D/(fmt.format(i)+'.json')).read_text()) for i in [0,1]]
  for k in ['prefix_sha','geometry_sha','rates_sha','steps','rays','order','clock']:assert a[k]==b[k]
  x,y=[np.load(D/(fmt.format(i)+'.npz'))['rows'] for i in [0,1]];assert np.array_equal(x[:,0],y[:,0])
  rows[name]=dict(intervals=len(x)-1,delta_final=b['x']-a['x'],delta_join=b['join_x']-a['join_x'],delta_T=b['T']-a['T'],xoff=a['x'],xon=b['x'],max_root=max(a['max_xres'],b['max_xres']),max_atom=max(a['max_atom_res'],b['max_atom_res']),total_gain_difference=b['total_gain_correction']-a['total_gain_correction'],events=[a['events'],b['events']])
 o=dict(rows=rows,checks=checks,clock_delta=rows['bass128_32']['delta_final']-rows['flrw128_32']['delta_final'],scope='actual full represented H-only histories, common mesh within each matched pair; event union first-generation only, later propagated events remain approximate; no donor promotion')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
