"""Compare complete original Neufeld 2026 standard-vs-alternative HD non-LTE FITS.

Uses two individually source-hashed FITS and two source-hashed original LAMDA files.
Only cells with all 15 finite LOGPOP points receive full-integrated-cooling claims;
masked values remain missing and the lower bound is clearly marked.
"""
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, math
import numpy as np
from fits_source_grid import load_fits
from pr169_neufeld15_reference import parse_lamda, H

SOURCE_MD5 = {'standard':'c45c4740011df579a973a7c336c5bc22',
              'alternate':'1f0275f383786c890bfbb0c83bb4f74b'}
SOURCE_SHA256 = {'standard':'f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb',
              'alternate':'66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac'}

def run(data_dir:Path,output_dir:Path):
    sources={}
    for typ,suffix in [('standard',''),('alternate','_altex')]:
        raw=(data_dir/f'hd_lamda{suffix}.dat').read_bytes()
        if hashlib.md5(raw).hexdigest()!=SOURCE_MD5[typ] or hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256[typ]:
            raise ValueError('Neufeld .dat original byte mismatch')
        model=parse_lamda(raw,verify=typ=='standard')
        source=load_fits(data_dir/f'hd_population_grids{suffix}.fits',source_kind=typ)
        sources[typ]=(model,source)
    a,fa=sources['standard'];b,fb=sources['alternate']
    if len(a.levels)!=15 or len(a.rad)!=14 or len(b.rad)!=14:raise ValueError('Source structure mismatch')
    if not np.array_equal(fa['temperatures_K'],fb['temperatures_K']) or not np.array_equal(fa['densities_cm3'],fb['densities_cm3']):
        raise ValueError('FITS grids are not source-identical')
    # Independent original sources use the same published A and observed frequencies.
    for x,y in zip(a.rad,b.rad):
        if x!=y:raise ValueError('Radiative data are different; cross-grid cooling would not be a controlled comparison')
    qkeys=set(a.collision[2][1]);assert set(b.collision[2][1])==qkeys
    qreport=[]
    for partner in (2,3):
        original=a.collision[partner][1];altex=b.collision[partner][1]
        for edge in sorted(qkeys):
            x=original[edge];y=altex[edge]
            if len(x)!=len(y):raise ValueError('Source temperature rate length mismatch')
            qreport.append((partner,edge[0],edge[1],any(i!=j for i,j in zip(x,y)),max(abs(i-j)/i for i,j in zip(x,y))))
    pstd=fa['populations'];palt=fb['populations']; v=np.array([A*H*nu for _,_,A,nu in a.rad])
    # Radiative transition is upper J+1 -> lower J for all 14 source lines.
    if [r[0] for r in a.rad]!=list(range(1,15)) or [r[1] for r in a.rad]!=list(range(14)):
        raise ValueError('Source E1 transition ordering not adjacent')
    std_line=pstd[:,:,1:]*v[None,None,:]
    alt_line=palt[:,:,1:]*v[None,None,:]
    full_valid=(~np.isnan(pstd).any(axis=2))&(~np.isnan(palt).any(axis=2))
    # For incompletely specified populations, finite known spontaneous emission is
    # a strict nonnegative LOWER BOUND; not a complete measured cooling power.
    lower_std=np.nansum(std_line,axis=2); lower_alt=np.nansum(alt_line,axis=2)
    ratio=np.where(full_valid,(lower_alt-lower_std)/lower_std,np.nan)
    absratio=np.abs(ratio)
    vals=absratio[np.isfinite(absratio)]
    if vals.size==0:raise ValueError('No source-complete cells to compare')
    output_dir.mkdir(parents=True,exist_ok=True)
    cases=[]
    for i,T in enumerate(fa['temperatures_K']):
        for j,n in enumerate(fa['densities_cm3']):
            cases.append({'T_K':float(T),'nH2_cm3':float(n),
                'std_nan_levels':int(fa['nan_by_cell'][i,j]),'altex_nan_levels':int(fb['nan_by_cell'][i,j]),
                'full15_integrated_cooling_qualified':bool(full_valid[i,j]),
                'std_known_spont_cooling_lower_bound_W_per_HD':float(lower_std[i,j]),
                'altex_known_spont_cooling_lower_bound_W_per_HD':float(lower_alt[i,j]),
                'full15_cooling_fraction_altex_vs_std':float(ratio[i,j]) if full_valid[i,j] else None,
                'std_f_J1':float(pstd[i,j,1]) if np.isfinite(pstd[i,j,1]) else None,
                'altex_f_J1':float(palt[i,j,1]) if np.isfinite(palt[i,j,1]) else None,
                'std_f_J9':float(pstd[i,j,9]) if np.isfinite(pstd[i,j,9]) else None,
                'altex_f_J9':float(palt[i,j,9]) if np.isfinite(palt[i,j,9]) else None})
    outfile=output_dir/'NEUFELD2026_ORIGINAL_17871_CELLS.csv'
    with outfile.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
    w_i,w_j=np.unravel_index(np.nanargmax(absratio),absratio.shape)
    # Restrict comparisons that reference high-J resolved transitions to full15 sources.
    summary={
        'source_type':'NEUFELD_2026_ZENODO_V2_STANDARD_VS_ALT_EXTRAPOLATION',
        'source_files':{k:{'dat_sha256':SOURCE_SHA256[k],'fits_sha256':sources[k][1]['source_sha256'],
                           'nan_count':sources[k][1]['nan_count'],'fits_nan_header':sources[k][1]['metadata_nan_count']} for k in sources},
        'grid':{'temperature_n':len(fa['temperatures_K']),'density_n':len(fa['densities_cm3']),
                'all_cells':len(cases),'full15_both_finite_cells':int(full_valid.sum()),
                'masked_cells':int((~full_valid).sum())},
        'original_collisional_rate_comparison':{
            'source_rate_rows':len(qreport),'changed_rows':sum(x[3] for x in qreport),
            'unchanged_below_J9':sum(not x[3] for x in qreport if x[1] <=8),
            'changed_below_J9':sum(x[3] for x in qreport if x[1] <=8),
            'changed_above_J8':sum(x[3] for x in qreport if x[1]>8),
            'max_relative_rate_change':max(x[4] for x in qreport)},
        'cooling_full15':{
            'max_abs_fraction_change':float(np.max(vals)),
            'median_abs_fraction_change':float(np.median(vals)),
            'fraction_gt_0p1pct':float(np.mean(vals>0.001)),
            'fraction_gt_1pct':float(np.mean(vals>0.01)),
            'signed_change_at_max':float(ratio[w_i,w_j]),
            'max_case_T_K':float(fa['temperatures_K'][w_i]),
            'max_case_nH2_cm3':float(fa['densities_cm3'][w_j]),
            'std_at_max_W_per_HD':float(lower_std[w_i,w_j]),
            'altex_at_max_W_per_HD':float(lower_alt[w_i,w_j])},
        'not_claimed':['masked cells full HD cooling rate','empirical molecular abundance','production/owner 35Hz validation','any cosmological history IVP'],
        'canonical_DAG':'28/88','REC_physical_DAG':'0/313','owner_35Hz':'FAIL7/8','production':'HOLD'}
    (output_dir/'NEUFELD2026_ORIGINAL_GRID_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();print(json.dumps(run(a.input,a.output),indent=2))
