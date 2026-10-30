"""HD J1/J0 source-locked physical inversion diagram at nine ORIGINAL T knots.

No temperature interpolation: statuses are only evaluated for Neufeld v2 source
T grid; redshift denotes isotropic CMB T0*(1+z) boundary, not a cosmological IVP.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from hd_line_transfer import read_models,REDSHIFTS
from hd_cmb15 import solve_cmb

TEMPERATURE_KNOTS=(100.,200.,300.,400.,600.,1000.,2000.,3000.,4000.)


def balance(model,T,n,z):
    pop=solve_cmb(model,T,n,z)['populations_J0_to_J14']
    return (model.levels[1][2]/model.levels[0][2])*pop[0]-pop[1]


def run(root):
    models=read_models(root)
    logns=np.linspace(2.,10.,161)
    rows=[];curve=[]
    for name,model in models.items():
     for T in TEMPERATURE_KNOTS:
      for z in REDSHIFTS:
       values=[balance(model,T,10**float(logn),z) for logn in logns]
       cross=[]
       for i in range(len(logns)-1):
         if values[i]*values[i+1]<0:
           x=brentq(lambda a:balance(model,T,10**a,z),float(logns[i]),float(logns[i+1]),xtol=4e-13)
           cross.append(10**x)
       if len(cross) not in (0,2):
         raise ArithmeticError(f'Non-closed inversion island for {name}, {T}, z {z}: {cross}')
       most_neg=min(values)
       rows.append({'source':name,'Tgas_K':T,'z':z,'has_J1_inversion':len(cross)==2,
         'n_inversion_on_cm3':cross[0] if cross else None,
         'n_inversion_off_cm3':cross[1] if cross else None,
         'min_positive_pop_balance':most_neg,
         'max_gain_population_in_grid':-most_neg if most_neg<0 else 0,
         'num_crossings':len(cross),
         'meaning':'non-LTE 15-level source-original CMB, f_ortho=0.75; not observed maser'})
       for a,v in zip(logns,values):
         curve.append({'source':name,'Tgas_K':T,'z':z,'nH2_cm3':10**float(a),
           'J1_overpop_minus_threeJ0':-v,'inversion':v<0})
    out=Path(root)/'evidence'
    for name,rs in [('J1_INVERSION_T_Z_PHASE_WINDOWS.csv',rows),('J1_INVERSION_T_Z_N_DENSE_ATLAS.csv',curve)]:
     with (out/name).open('w',newline='',encoding='utf8') as f:
       w=csv.DictWriter(f,list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
    d={'original_source_temperatures_K':list(TEMPERATURE_KNOTS),
      'redshifts':list(REDSHIFTS),'cases':len(rows),'density_samples':len(curve),
      'inversion_condition_cases':sum(x['has_J1_inversion'] for x in rows),
      'source_standard_inversion_conditions':sum(x['has_J1_inversion'] and x['source']=='std' for x in rows),
      'source_alternative_inversion_conditions':sum(x['has_J1_inversion'] and x['source']=='alternate' for x in rows),
      'cases':rows,'note':'No external radiation except CMB, no gas temperature interpolation or populations modified by own emergent line'}
    # Explicitly distinguish case count from case records.
    d['case_count']=len(rows)
    (out/'J1_INVERSION_T_Z_PHASE_SUMMARY.json').write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
    return d

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=Path('.'))
 r=run(a.parse_args().root)
 print(json.dumps({'conditions':r['case_count'],'dense_state_points':r['density_samples'],
                   'std_inverted':r['source_standard_inversion_conditions'],
                   'alternate_inverted':r['source_alternative_inversion_conditions']},indent=2))
