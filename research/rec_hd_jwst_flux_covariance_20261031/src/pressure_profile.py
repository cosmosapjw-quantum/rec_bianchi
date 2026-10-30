"""HH211 ap7: pressure-profile sensitivity of source-authentic HD CMB15 model, not posterior."""
from pathlib import Path
import json,csv,sys,numpy as np
from jwst_conditional_fit import read_flux,make_basis,profile_nonnegative_basis,PRESSURE_LOG_K_CM3

def run(root):
 root=Path(root)
 src=read_flux(root)
 obs=[x for x in src if x['source']=='HH 211' and x['aperture']==7 and x['species']=='HD']
 assert len(obs)==6 and all(x['status']=='detected_positive_printed_error' for x in obs)
 f=np.array([x['value_printed'] for x in obs]);s=np.array([x['sigma_printed'] for x in obs]);single,sk,pairs,pk,_=make_basis(root)
 rows=[]
 for rho in (0.,1.):
  for source in ('std','alternate'):
   for logp in PRESSURE_LOG_K_CM3:
    for model,basis,keys in [('twoT_isobaric',pairs,pk)]:
     selected=[i for i,k in enumerate(keys) if k['source']==source and k['log10_p_over_kB_K_cm3']==logp]
     ch,cs=profile_nonnegative_basis(f,s,basis[selected,:,:],rho=rho)
     i=int(np.argmin(ch));p=keys[selected[i]]
     rows.append(dict(source=source,calibration_rho=rho,log10_p_over_kB_K_cm3=logp,model=model,
        best_chi2=float(ch[i]), temperatures_K=json.dumps([p.get('gas_temperature_K')] if model=='singleT' else [p['warm_temperature_K'],p['hot_temperature_K']]),
        best_amplitudes=json.dumps(list(map(float,cs[i])))))
 out=root/'outputs'/'HH211_ap7_pressure_profile.csv'
 with out.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(8,4.4))
 for src in ('std','alternate'):
  for rho in (0.,1.):
   a=[r for r in rows if r['source']==src and r['calibration_rho']==rho and r['model']=='twoT_isobaric']
   ax.plot([r['log10_p_over_kB_K_cm3'] for r in a],[r['best_chi2'] for r in a],label=f'{src}, rho={rho:g}')
 ax.set_xlabel(r'$\log_{10}[(p/k_B)/(\mathrm{K\,cm}^{-3})]$')
 ax.set_ylabel('Profiled conditional GLS quadratic')
 ax.set_title('HH 211 ap. 7: pressure/source/calibration sensitivity, NOT posterior')
 ax.legend();fig.tight_layout();fig.savefig(root/'figures'/'HH211_ap7_pressure_source_sensitivity.png',dpi=160);plt.close(fig)
 print(json.dumps({'rows':len(rows),'per_source_rho':len(PRESSURE_LOG_K_CM3),'minima':[
  {'source':src,'rho':rho,'min_chi2':min(r['best_chi2'] for r in rows if r['source']==src and r['calibration_rho']==rho and r['model']=='twoT_isobaric')}
  for src in ('std','alternate') for rho in (0.,1.)]},sort_keys=True))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '.'))
