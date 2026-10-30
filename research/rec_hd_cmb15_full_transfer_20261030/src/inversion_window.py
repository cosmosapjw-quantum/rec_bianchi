"""Source-locked HD J=1->0 weak-inversion density windows at original T=4000K.

This is a conditional stationary non-LTE source-model result, not detection,
claim of maser saturation, or source-independent proof of inversion.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from hd_cmb15 import solve_cmb
from hd_line_transfer import read_models,REDSHIFTS,H,K_B


def balance(model,n,z,T=4000.):
    p=solve_cmb(model,T,n,z)['populations_J0_to_J14']
    return model.levels[1][2]/model.levels[0][2]*p[0]-p[1]


def run(root):
    models=read_models(root)
    rs=[];curve=[]
    # Log10 n sampled only as root bracket construction; roots refined by Brent.
    logs=np.linspace(1.,10.,181)
    for s,model in models.items():
      for z in REDSHIFTS:
        vals=[balance(model,10**float(t),z) for t in logs]
        edges=[]
        for i in range(len(logs)-1):
            if vals[i]*vals[i+1]<0:
                xr=brentq(lambda logn:balance(model,10**logn,z),float(logs[i]),float(logs[i+1]),xtol=4e-13)
                edges.append(10**xr)
        if len(edges)!=2:raise ArithmeticError(f'Expected 2 inversions crossings, found {len(edges)} for {s},z={z}')
        if not (balance(model,math.sqrt(edges[0]*edges[1]),z)<0
                and balance(model,edges[0]*.1,z)>0
                and balance(model,edges[1]*10,z)>0):
            raise AssertionError('No bracketing interior inversion')
        rr={'source':s,'Tgas_K':4000.,'z':z,'n_on_cm3':edges[0],'n_off_cm3':edges[1],
            'log_width_dex':math.log10(edges[1]/edges[0]),
            'root_residual_lower':balance(model,edges[0],z),
            'root_residual_upper':balance(model,edges[1],z),
            'original_35Hz':'FAIL7/8','evidence':'Neufeld2026 v2 original rate tables, source-locked stationary CMB15'}
        rs.append(rr)
        for x,y in zip(logs,vals):
            curve.append({'source':s,'z':z,'Tgas_K':4000.,'nH2_cm3':10**float(x),
                          'J1_minus_g1p0':-y,'inversion':y<0})
    out=Path(root)/'evidence';out.mkdir(parents=True,exist_ok=True)
    for filename,data in [('J1_INVERSION_WINDOWS_SOURCE_BOUND.csv',rs),('J1_INVERSION_DENSITY_CURVES.csv',curve)]:
        with (out/filename).open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
    summary={'source':'Neufeld2026 Zenodo v2 original LAMDA standard/alternate',
      'method':'source-locked CMB15 stationary CTMC; log-density bracket and Brent roots, all exact T=4000K original source knot',
      'inversion_windows':len(rs),'sample_curve_points':len(curve),
      'windows':rs,'scope':'physical model conditional, density root numerical not certified and potential background/geometry limitations; no measured maser, no self-consistent saturation'}
    (out/'J1_INVERSION_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    return summary

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'))
 s=run(ap.parse_args().root);print(json.dumps({'windows':s['inversion_windows'],'source_z0':s['windows'][0],'alternate_z0':s['windows'][5]},indent=2))
