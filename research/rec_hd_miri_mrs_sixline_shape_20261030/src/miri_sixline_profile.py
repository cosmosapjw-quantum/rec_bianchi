"""Source-locked HD 15-level MIRI MRS geometric-coverage/model-shape atlas.

Experimental spectra or covariance are NOT inputs. Output is NOT a detection,
observed flux or an instrument uncertainty analysis. Temperatures are exact
Neufeld-2026 LAMDA collision-table knot values only.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, math
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from pr169_neufeld15_reference import parse_lamda
from hd_cmb15 import solve_cmb
from sixline_atlas import SOURCE

C_M_S = 299792458.0
# STScI JWST MIRI MRS 2025/2026 documentation, operational 4.9--27.9 um.
MRS_SUBBANDS = {
 '1A':(4.90,5.74),'1B':(5.66,6.63),'1C':(6.53,7.65),
 '2A':(7.51,8.77),'2B':(8.67,10.13),'2C':(10.01,11.70),
 '3A':(11.55,13.47),'3B':(13.34,15.57),'3C':(15.41,17.98),
 '4A':(17.70,20.95),'4B':(20.69,24.48),'4C':(24.40,27.90)}
DOC='https://jwst-docs.stsci.edu/jwst-mid-infrared-instrument/miri-observing-modes/miri-medium-resolution-spectroscopy'
TEMPERATURES=(1000.,2000.,3000.,4000.)
DENSITIES=(1e2,1e4,1e6,1e8,1e10)
REDSHIFTS=(0.,.1,.25,.5,.75,1.,1.25)
J_UPPERS=tuple(range(5,11))


def sha256(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()

def source_gate(root:Path):
    for f in ('hd_lamda.dat','hd_lamda_altex.dat','hd_population_grids.fits','hd_population_grids_altex.fits'):
        rel='source/zenodo_v2/'+f
        if sha256(root/rel)!=SOURCE[rel]:raise ValueError('SOURCE_SHA_MISMATCH: '+rel)

def rest_wavelengths(model):
    spec={}
    for upper,lower,A,nu in model.rad:
        j=model.levels[upper][0]
        if j in J_UPPERS:
            assert model.levels[lower][0]==j-1
            spec[j] = C_M_S/nu*1e6
    assert set(spec)==set(J_UPPERS)
    return spec

def coverage(rest_um,z):
    return {j: [b for b,(a,c) in MRS_SUBBANDS.items() if a<=wave*(1+z)<=c]
            for j,wave in rest_um.items()}

def min_settings_cover(cov):
    obs={j for j,b in cov.items() if b}
    if not obs:return (0,'')
    for r in (1,2,3):
        for comb in itertools.combinations('ABC',r):
            if all(any(b[-1] in comb for b in cov[j]) for j in obs):
                return r,''.join(comb)
    raise AssertionError('Coverage union impossible')

def positive_log_powers(model,T,n,z):
    obs=solve_cmb(model,float(T),float(n),float(z))
    indexed={int(d['J_upper']):d['net_W_per_HD'] for d in obs['line_power_records']}
    a=np.array([indexed[j] for j in J_UPPERS],dtype=float)
    if not np.all(np.isfinite(a)) or not np.all(a>0):
        raise ArithmeticError('Not positive warm HD line powers')
    return np.log(a),a

def amplitude_free_spread(log_alt,log_std,mask):
    if len(mask)<2:return 0.
    v=log_alt[mask]-log_std[mask]
    return float(np.max(v)-np.min(v))

def profile_shape(log_alt, selected, solver, temperatures=TEMPERATURES):
    """Approximate inf_{T in exact knots, 1e2<=n<=1e10} log ratio spread.

    Grid + bracketing of every neighboring local grid minimum provides a
    deterministic numerical search; the resulting minimum is NOT certified.
    """
    if len(selected)<2:return {'spread':0.,'T_fit_K':None,'density_fit_cm3':None}
    best=(float('inf'),None,None)
    for T in temperatures:
        @lru_cache(maxsize=256)
        def obj(x):
            ls=solver(T,10.**float(x))
            return amplitude_free_spread(log_alt,ls,selected)
        grid=np.linspace(2.,10.,33)
        vals=[obj(float(x)) for x in grid]
        for i,(x,v) in enumerate(zip(grid,vals)):
            candidate=(v,T,float(x))
            if candidate[0]<best[0]:best=candidate
            if 0<i<len(grid)-1 and v<=vals[i-1] and v<=vals[i+1]:
                opt=minimize_scalar(obj,bounds=(float(grid[i-1]),float(grid[i+1])),method='bounded',options={'xatol':1e-8,'maxiter':120})
                if opt.success and opt.fun<best[0]:best=(float(opt.fun),T,float(opt.x))
    return {'spread':best[0],'T_fit_K':best[1],'density_fit_cm3':10**best[2]}

def run(root:Path):
    root=Path(root)
    source_gate(root)
    std=parse_lamda((root/'source/zenodo_v2/hd_lamda.dat').read_bytes(),verify=True)
    alt=parse_lamda((root/'source/zenodo_v2/hd_lamda_altex.dat').read_bytes())
    rest=rest_wavelengths(std)
    assert max(abs(rest[j]-rest_wavelengths(alt)[j]) for j in J_UPPERS)<1e-10
    # Independent rates share radiative spectroscopy; no frequency/source switch.
    redshift_rows=[]
    for z in REDSHIFTS:
        cov=coverage(rest,z)
        nsettings,settings=min_settings_cover(cov)
        redshift_rows.append({'z':z,'observed_J_uppers':','.join(map(str,[j for j in J_UPPERS if cov[j]])),
             'observable_line_count':sum(bool(v) for v in cov.values()),
             'independent_ratios':max(0,sum(bool(v) for v in cov.values())-1),
             'minimum_MRS_settings':nsettings,'one_minimal_setting_cover':settings})
    cache={}
    def std_logs(T,n,z):
        key=(T,round(float(math.log10(n)),12),z)
        if key not in cache:cache[key]=positive_log_powers(std,T,n,z)[0]
        return cache[key]
    cases=[]
    for z in REDSHIFTS:
        cov=coverage(rest,z)
        mask=[i for i,j in enumerate(J_UPPERS) if cov[j]]
        for T in TEMPERATURES:
            for n in DENSITIES:
                log_alt,alt_pow=positive_log_powers(alt,T,n,z)
                log_std,std_pow=positive_log_powers(std,T,n,z)
                direct=amplitude_free_spread(log_alt,log_std,mask)
                # No T interpolation. One inference is conditional on T; second allows
                # only the FOUR exact source table temperatures.
                fixed=profile_shape(log_alt,mask,lambda t,x:std_logs(t,x,z),(T,))
                flexible=profile_shape(log_alt,mask,lambda t,x:std_logs(t,x,z),TEMPERATURES)
                max_power=max(float(max(alt_pow)),float(max(std_pow)))
                min_rel_power=min([float(min(alt_pow[i],std_pow[i]))/max_power for i in mask],default=0.)
                if not (flexible['spread']<=fixed['spread']+3e-7 and fixed['spread']<=direct+3e-7):
                    raise AssertionError('Profile nesting is inconsistent')
                cases.append({'z':z,'T_alt_K':T,'n_alt_cm3':n,'visible_line_count':len(mask),
                       'visible_R':','.join(f'R({J_UPPERS[i]-1})' for i in mask),
                       'direct_logspread':direct,
                       'fixed_T_density_profile_logspread':fixed['spread'],
                       'fixed_T_std_density_cm3':fixed['density_fit_cm3'],
                       'T_and_density_profile_logspread':flexible['spread'],
                       'profile_std_T_K':flexible['T_fit_K'],
                       'profile_std_density_cm3':flexible['density_fit_cm3'],
                       'T_n_profile_ratio_spread_factor':math.exp(flexible['spread']),
                       'visible_model_power_1pct_floor':min_rel_power>=.01,
                       'weakest_visible_power_over_full_sixline_peak':min_rel_power,
                       'NOTE':'unweighted, common-amplitude-free model manifold shape; not a likelihood'})
    out=root/'evidence';out.mkdir(parents=True,exist_ok=True)
    def writecsv(path,data):
        with path.open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');writer.writeheader();writer.writerows(data)
    writecsv(out/'MIRI_MRS_REDSHIFT_COVERAGE.csv',redshift_rows)
    writecsv(out/'MIRI_SOURCE_NUISANCE_PROFILE_140.csv',cases)
    transitions=[]
    for j in J_UPPERS:
        r=rest[j]
        transitions.append({'transition':f'R({j-1})','upper_J':j,'lambda_rest_um':r,
                 'z_max_MIRI_27p9':27.9/r-1.,'z_min_MIRI_4p9':max(0.,4.9/r-1.),
                 'original_frequency_Hz':C_M_S/(r*1e-6)})
    writecsv(out/'MIRI_ORIGINAL_HD_LINE_WINDOW.csv',transitions)
    stats={}
    for rr in redshift_rows:
        z=rr['z'];sc=[c for c in cases if c['z']==z and c['visible_line_count']>=2]
        stats[str(z)]={'n_cases':len(sc),'visible_lines':rr['observable_line_count'],
         'median_direct_logspread':float(np.median([c['direct_logspread'] for c in sc])) if sc else None,
         'median_after_T_nuisance_logspread':float(np.median([c['T_and_density_profile_logspread'] for c in sc])) if sc else None,
         'model_power_1pct_floor_cases':sum(c['visible_model_power_1pct_floor'] for c in sc),
         'residual_over_ln1p10_cases':sum(c['T_and_density_profile_logspread']>math.log1p(.1) for c in sc)}
    summary={'program':'REC_HD_MIRI_MRS_SIXLINE_NUISANCE_GEOMETRY_20261030',
             'science_class':'source-owned physical model atlas, NOT sky data',
             'Neufeld2026_v2_original_inputs':{k:SOURCE[k] for k in SOURCE if k.startswith('source/')},
             'parent_PR':172,'parent_head':'331602990e014e8ff532f6cc6179d6a74a1e3296',
             'instrument_reference':DOC,'effective_MIRI_MRS_um':[4.9,27.9],
             'temperature_original_knots_K':TEMPERATURES,'H2_densities_cm3':DENSITIES,
             'redshifts':REDSHIFTS,'conditions':len(cases),
             'conditions_with_two_plus_geometrically_visible_lines':sum(c['visible_line_count']>=2 for c in cases),
             'source_ratio_shape_metric':'max_i log(Palt_i/Pstd_i) - min_i log(Palt_i/Pstd_i); eliminates arbitrary common HD column normalization',
             'density_fit_interval_cm3':[1e2,1e10],
             'model_selector':'min over exact original four temperature knots; continuous positive H2 density with Neufeld v2 rate files',
             'minimizer':'bounded local refinements on 33-point log-n grid; approximate, not a certified global minimum',
             'redshift_groups':stats,'ratio_normalization':'model net radiative line power per HD molecule; no dust, opacity, line broadening, instrumental sensitivity, noise, or measured flux',
             'source_35Hz_original':'FAIL7/8','canonical_DAG':'28/88','REC_physical_DAG':'0/313','production':'HOLD','merge':False,
             'R6_C9_distinct_author':'NOT_RUN'}
    (out/'MIRI_SHAPE_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    return summary,cases,transitions,redshift_rows

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'))
    s,*_=run(ap.parse_args().root)
    print(json.dumps({'cases':s['conditions'],'geometric_two_plus':s['conditions_with_two_plus_geometrically_visible_lines'],'per_z':s['redshift_groups']},indent=2))
