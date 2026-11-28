"""Literature HeI profile with actual primordial HI ground-state continuum optical depth.
Prescribed net rates, separate channels; this is not a coupled feedback solver."""
from pathlib import Path
import json,sys,numpy as np,hashlib
from scipy.constants import c as clight
D=Path(__file__).resolve().parent;P=D.parent;F=P/'r118c4f_causal_mesh';E=P/'r118c4e_early_events'
sys.path.insert(0,str(D.parents[1]/'src'))
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology,integrate_helium_stages,saha_xH1s
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def profile(x):
 z=x*(1-x);return 19.602*z**3*(1.742-7.2*z+12.8*z*z)/(z+.03)**2
def sigma(E):
 # Nonrelativistic dipole H I 1s analytic Coulomb cross section normalized at threshold.
 E=np.asarray(E,float);s=np.zeros_like(E);thr=13.598434599702;sel=E>=thr;k=np.sqrt(E[sel]/thr-1)
 r=np.ones_like(k);m=k>1e-10;r[m]=np.arctan(k[m])/k[m]
 den=np.ones_like(k);den[m]=-np.expm1(-2*np.pi/k[m])
 s[sel]=6.30e-22*(thr/E[sel])**4*np.exp(4-4*r)/den
 return s
def main():
 z=np.load(F/'HELIUM_CHANNELS.npz');u=z['u'];stage=z['stage'];en=z['energy'];net=z['net_cell'];h=integrate_helium_stages(HyRec2012Cosmology());cos=HyRec2012Cosmology()
 assert np.array_equal(np.asarray(h.z),z['z']);assert np.allclose(-np.log1p(z['z']),u,rtol=0,atol=1e-14)
 a=np.exp(u);HI=np.array([saha_xH1s(cos,float(x),float(zz)) if st=='HeII_RECOMBINATION' else 0 for x,zz,st in zip(h.xHeII,h.z,h.stage)])
 assert np.all((HI>=0)&(HI<=1));H=np.array([cos.hubble_s(float(v)) for v in h.z]);mask=(stage[:-1]=='HeII_RECOMBINATION')&(stage[1:]=='HeII_RECOMBINATION');ix=np.where(mask)[0];assert len(ix)>0
 x,w=np.polynomial.legendre.leggauss(128);x=(x+1)/2;w=w/2;norm=w@profile(x);weights=w*profile(x)/norm
 assert abs(weights.sum()-1)<1e-14 and abs(weights@x-.5)<1e-14 and np.max(abs(profile(x)-profile(1-x)))<1e-12
 thr=13.598434599702;assert sigma(np.array([thr-1e-7,thr,2*thr]))[0]==0 and abs(sigma(np.array([thr]))[0]/6.3e-22-1)<1e-14
 em=np.sum(net[ix],axis=0);rows=[];spectra={}
 for bins in [256,512,1024]:
  grid=np.geomspace(a[ix[0]]*en[0]*min(x)*.98,a[ix[-1]+1]*max(en)*1.02,bins);N=np.zeros((2,bins));emN=np.zeros(2);emK=np.zeros(2);absN=np.zeros(2);absK=np.zeros(2);absE=np.zeros(2);heat=np.zeros(2);redshift=np.zeros(2);emE=np.zeros(2)
  def atten(ul,ur):
   nonlocal redshift
   if ur<=ul:return
   ua=(ul+ur)/2;aa=np.exp(ua);energy=grid/aa
   nHI=cos.nH0_m3/aa**3*np.interp(ua,u,HI);HH=np.interp(ua,u,H);tau=clight*nHI/HH*sigma(energy)*(ur-ul);assert np.min(tau)>=0
   loss=N*(-np.expm1(-tau))[None,:];n0=N@grid;N[:]-=loss;n1=N@grid
   absN[:]+=loss.sum(axis=1);absK[:]+=loss@grid;absE[:]+=loss@energy;heat[:]+=loss@np.maximum(energy-thr,0)
   # Midpoint absorption splits redshift work exactly for the chosen discrete emission/absorption clock.
   redshift[:]+=n0*(np.exp(-ul)-np.exp(-ua))+n1*(np.exp(-ua)-np.exp(-ur))
  def deposit(ch,E,q):
   E=np.atleast_1d(E);q=np.atleast_1d(q);i=np.searchsorted(grid,E)-1;assert min(i)>=0 and max(i)<bins-1;f=(E-grid[i])/(grid[i+1]-grid[i]);np.add.at(N[ch],i,q*(1-f));np.add.at(N[ch],i+1,q*f);emN[ch]+=q.sum();emK[ch]+=q@E
  for i in ix:
   l,r=u[i:i+2];mid=(l+r)/2;am=np.exp(mid);atten(l,mid)
   deposit(0,am*en[0]*x,2*net[i,0]*weights);deposit(1,am*en[1],net[i,1]);emE+=net[i]*en
   atten(mid,r)
  end=a[ix[-1]+1];endN=N.sum(axis=1);endK=N@grid
  nd=emN-absN-endN;kd=emK-absK-endK;ed=emE-absE-endK/end-redshift;heatdef=absE-thr*absN-heat
  assert max(abs(nd))<1e-12 and max(abs(kd))<1e-14 and max(abs(ed))<1e-10 and max(abs(heatdef))<1e-12
  row=dict(bins=bins,net_emitted=emN.tolist(),emitted_energy_eV_per_H=emE.tolist(),absorbed=absN.tolist(),surviving=endN.tolist(),ionization_energy=(thr*absN).tolist(),heat_eV_per_H=heat.tolist(),absorbed_energy=absE.tolist(),redshift_work=redshift.tolist(),number_balance=nd.tolist(),comoving_energy_balance=kd.tolist(),physical_energy_balance=ed.tolist(),heat_balance=heatdef.tolist())
  rows.append(row);spectra[f'E_{bins}']=grid;spectra[f'N_{bins}']=N;print(row,flush=True)
 np.savez_compressed(D/'HEI_HI_TRANSFER.npz',u=u,HI=HI,H=H,profile_x=x,profile_weights=weights,**spectra)
 (D/'HEI_HI_TRANSFER.json').write_text(json.dumps(dict(rows=rows,profile_half_normalization=float(norm/2),profile_ref='Switzer-Hirata I, Appendix A Eq. 103, https://ar5iv.labs.arxiv.org/html/astro-ph/0702143',normalization='full photon marginal = 19.602 shape / integral; source half-domain formula rounded',source_rates_sha=sha(F/'HELIUM_CHANNELS.npz'),source_history_sha=sha(E/'HELIUM_ENERGY.npz'),sigma_threshold_m2=6.3e-22,scope='actual prescribed net HeI effective rate history, literature 2^1S profile, source Saha HI and expanding H clock, conditional pure continuum absorption; 2p escape rates already incorporate HI opacity so 2p attenuation is separate diagnostic not an added physical correction; no backreaction or line redistribution'),indent=2)+'\n')
if __name__=='__main__':main()
