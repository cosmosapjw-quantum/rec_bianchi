"""Bounded diagnostic for mechanism of source-locked HD low-J weak inversion.

Truncated level networks are NOT a replacement physical HD model, only an
operator-level controlled diagnostic to locate minimum pumping graph size.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from pr169_neufeld15_reference import Model
from hd_cmb15 import solve_cmb
from hd_line_transfer import read_models


def truncate(model,Jmax):
    count=Jmax+1
    return Model(model.levels[:count],tuple(x for x in model.rad if x[0]<count),
      {partner:(temps,{pair:vals for pair,vals in rates.items() if pair[0]<count})
       for partner,(temps,rates) in model.collision.items()},model.source_sha256)


def run(root):
    models=read_models(root)
    tr=[];opr=[]
    for source,model in models.items():
      for Jmax in range(1,15):
        reduced=truncate(model,Jmax)
        p=solve_cmb(reduced,4000.,1e4,0.)['populations_J0_to_J14']
        diff=3*p[0]-p[1]
        tr.append({'source':source,'Jmax_included':Jmax,'levels':Jmax+1,
           'J1_population_minus_three_J0':-diff,'inverted':diff<0,
           'Tgas_K':4000.,'nH2_cm3':1e4,'z':0.,
           'interpretation':'conditional truncated-network diagnostic only'})
      for f in (0.,.25,.5,.75,1.):
        p=solve_cmb(model,4000.,1e4,0.,f_ortho=f)['populations_J0_to_J14']
        opr.append({'source':source,'f_ortho_H2':f,
          'J1_population_minus_three_J0':p[1]-3*p[0],
          'inverted':p[1]>3*p[0],'Tgas_K':4000.,'nH2_cm3':1e4,'z':0.})
    out=Path(root)/'evidence'
    for name,rs in [('LOWJ_PUMPING_MECHANISM.csv',tr),('OPR_INVERSION_SENSITIVITY.csv',opr)]:
      with (out/name).open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,list(rs[0]),lineterminator='\n');writer.writeheader();writer.writerows(rs)
    summary={'unit':'Source-locked low-J pumping diagnostic',
             'minimum_level_Jmax_with_inversion':{s:next(x['Jmax_included'] for x in tr if x['source']==s and x['inverted']) for s in models},
             'OPR_test_range':[0.,1.],'all_5_OPR_cases_inverted_per_source':{
                s:all(x['inverted'] for x in opr if x['source']==s) for s in models},
             'scope':'truncation comparison not true physical collisional selection or independent experimental discovery'}
    (out/'INVERSION_MECHANISM_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'))
 print(json.dumps(run(p.parse_args().root),indent=2))
