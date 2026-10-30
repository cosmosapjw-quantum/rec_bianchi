"""Original-source model line-ratio degeneracy with H2 density (fixed T, OPR, z).

For a Neufeld alternate extrapolation at physical density 10^6 cm^-3,
find the standard-extrapolation density producing the same R(9)/R(7) ratio.
Report the held-out R(9)/R(4) ratio after calibration to expose residual
non-degenerate shape. Does NOT fit real observed line fluxes.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
from scipy.optimize import brentq
from pr169_neufeld15_reference import parse_lamda
from hd_cmb15 import solve_cmb
from sixline_atlas import SOURCE,bytes_sha

def source_ratios(model,T,n,z=0):
    s=solve_cmb(model,T,n,z)
    v=s['line_power_records']
    get=lambda r:v[r]['net_W_per_HD']
    if min(get(4),get(7),get(9))<=0:
        raise ArithmeticError('Invalid positive line-power ratio')
    return {'R9_over_R7':get(9)/get(7),'R9_over_R4':get(9)/get(4),
            'R8_over_R7':get(8)/get(7)}

def compute(root:Path):
    root=Path(root)
    for name in ('source/zenodo_v2/hd_lamda.dat','source/zenodo_v2/hd_lamda_altex.dat'):
        if bytes_sha(root/name)!=SOURCE[name]:raise ValueError('Source identity gate')
    std=parse_lamda((root/'source/zenodo_v2/hd_lamda.dat').read_bytes(),verify=True)
    alt=parse_lamda((root/'source/zenodo_v2/hd_lamda_altex.dat').read_bytes())
    n_physical=1e6
    data=[]
    for T in (1000.,2000.,3000.,4000.):
        alternate=source_ratios(alt,T,n_physical)
        log_equivalent=brentq(lambda log_n:source_ratios(std,T,10**log_n)['R9_over_R7']-alternate['R9_over_R7'],4.,8.,xtol=1e-11)
        n_equiv=10**log_equivalent
        matched=source_ratios(std,T,n_equiv)
        original_std=source_ratios(std,T,n_physical)
        data.append({'Tgas_K':T,'alternate_true_density_cm3':n_physical,
                    'standard_equivalent_density_cm3':n_equiv,
                    'density_factor':n_equiv/n_physical,
                    'alternate_R9_over_R7':alternate['R9_over_R7'],
                    'standard_at_equivalent_R9_over_R7':matched['R9_over_R7'],
                    'standard_at_true_density_R9_over_R7':original_std['R9_over_R7'],
                    'alternate_R9_over_R4':alternate['R9_over_R4'],
                    'standard_at_equivalent_R9_over_R4':matched['R9_over_R4'],
                    'heldout_R9_over_R4_fractional_source_difference':alternate['R9_over_R4']/matched['R9_over_R4']-1,
                    'alternate_R8_over_R7':alternate['R8_over_R7'],
                    'standard_at_equivalent_R8_over_R7':matched['R8_over_R7'],
                    'heldout_R8_over_R7_fractional_source_difference':alternate['R8_over_R7']/matched['R8_over_R7']-1})
    return data

def main(root:Path):
    data=compute(root)
    dest=Path(root)/'evidence/HELDOUT_SOURCE_DENSITY_DEGENERACY_4_CASES.csv'
    with dest.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
    (Path(root)/'evidence/HELDOUT_DENSITY_DEGENERACY_SUMMARY.json').write_text(json.dumps({'cases':len(data),'baseline_density_cm3':1e6,'matched_ratio':'R9/R7','heldout_ratio':'R9/R4','scope':'source-model degeneracy at same T and redshift z=0; not observational inference','cases_data':data},indent=2)+'\n')
    return data

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True)
    print(json.dumps(main(a.parse_args().root),indent=2))
