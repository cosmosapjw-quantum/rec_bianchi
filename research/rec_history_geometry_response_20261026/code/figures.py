"""Two saved-data figures only. No input, geometry, root or source module reads."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
UNIT=Path(__file__).resolve().parents[1]
R=UNIT/'results/primary001'
def read(name):
 with np.load(R/name,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def signed(ax,arrays):
 values=np.concatenate([abs(np.ravel(a)) for a in arrays]);nz=values[values>0]
 threshold=float(np.quantile(nz,.2)) if len(nz) else 1.
 ax.set_yscale('symlog',linthresh=threshold);ax.grid(alpha=.23)
 return threshold

def main():
 out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
 a=read('ANALYTIC_v1.npz');b=read('SOURCE_BINDING.npz');f=read('FINITE_DIAGNOSTICS.npz');c=read('SCALAR_COMPOSITION.npz')
 dec=json.loads((R/'DECIMAL_CHECKS.json').read_text());comp=json.loads((R/'SCALAR_COMPOSITION.json').read_text())
 plt.rcParams.update({'font.size':10,'axes.titlesize':12,'figure.dpi':120,'savefig.dpi':180})
 index=np.arange(313);thresholds={};fig,axes=plt.subplots(2,1,figsize=(10.8,7.5),layout='constrained')
 q=a['quadrupole_closed'][:,0,0];m=a['monopole_coefficient_per_S2']
 axes[0].plot(index,q,color='#1c5e9b',lw=1.4);axes[0].set(title='First shear quadrupole: Q11 derivative, v = (1, -1/2, -1/2)',ylabel='occupation / lambda')
 axes[1].plot(index,m,color='#a83b31',lw=1.4);axes[1].set(title='Second monopole coefficient per sum(v_i squared)',ylabel='occupation / lambda squared / S2',xlabel='Native incoming query index (0–310 virtual, 311 Ly-alpha, 312 Ly-beta)')
 for i,ax in enumerate(axes):
  thresholds['coefficient_'+str(i)]=signed(ax,[q if i==0 else m]);ax.axhline(0,color='.4',lw=.6)
  for j in (139,270,311,312):ax.axvline(j,color='.55',lw=.5,alpha=.5)
 fig.suptitle('GEO01 • actual 313-query fixed-history propagation partial',fontsize=15)
 fig.text(.5,-.015,'Signed symlog axes. Geometry/source history held fixed; no anisotropic collision or physical H6 admission.',ha='center',fontsize=9)
 for ext in ('png','pdf'):fig.savefig(out/f'geometry_coefficients.{ext}',bbox_inches='tight')
 plt.close(fig)
 fig,axs=plt.subplots(2,2,figsize=(12,8.1),layout='constrained')
 ax=axs[0,0];truth=a['mean_u2_closed'];ax.plot(index,truth,label='analytic mean',lw=1.5,color='black');ax.plot(index,f['mean_second_h'],label='14 rays, +/-h',lw=.9,alpha=.8);ax.plot(index,f['mean_second_half'],label='14 rays, +/-h/2',lw=.9,alpha=.8);thresholds['finite']=signed(ax,[truth,f['mean_second_h'],f['mean_second_half']]);ax.set(title='Ordinary finite second differences (diagnostic)',xlabel='Incoming query index',ylabel='occupation / lambda squared');ax.legend(fontsize=8)
 ax=axs[0,1]
 for div,marker in ((1,'o'),(2,'s')):
  rows=[d for d in dec if d['step_divisor']==div];ax.semilogy(np.arange(len(rows)),[max(float(d['first_normalized_error']),float(d['second_normalized_error']),1e-80) for d in rows],marker,ms=4,label='h' if div==1 else 'h/2')
 ax.axhline(2e-7,color='#a83b31',ls='--',label='frozen limit 2e-7');ax.set(title='Decimal80 full-exponential finite oracle',xlabel='Six selected rows x four squared directions',ylabel='max first/second error / operation gross');ax.grid(alpha=.23);ax.legend(fontsize=8)
 ax=axs[1,0];ax.plot(np.arange(314),c['outgoing_mean_second'],lw=1.2,color='#397c55');thresholds['scalar']=signed(ax,[c['outgoing_mean_second']]);ax.set(title='Saved scalar Ks acting on the second incoming mean',xlabel='Native outgoing index',ylabel='occupation / lambda squared')
 ax=axs[1,1];ax.axis('off');ax.text(.02,.95,'Single Ly-alpha event second response',va='top',fontsize=12,weight='bold');ax.text(.02,.78,f"Number: {comp['number_second']:.8e} m^-3 s^-1 / lambda^2\n\nRadiation: {comp['radiation_energy_second']:.8e} J m^-3 s^-1 / lambda^2\n\nAtomic: {comp['atomic_energy_second']:.8e} J m^-3 s^-1 / lambda^2\n\nAtomic = exact negative of radiation\nDirect incoming subtraction retained\n\nInterval: represented-vector propagation only",va='top',fontsize=10,linespacing=1.4)
 fig.suptitle('GEO01 • finite verification and frozen scalar composition',fontsize=15)
 for ext in ('png','pdf'):fig.savefig(out/f'verification_and_scalar_response.{ext}',bbox_inches='tight')
 plt.close(fig)
 files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir())}
 (out/'ASSET_IDENTITIES.json').write_text(json.dumps({'files':files,'symlog_linthresh':thresholds,'source':'saved results/primary001 only','scientific_roots':0,'matvecs':0,'source_rebuilds':0},indent=2)+'\n')
if __name__=='__main__':main()
