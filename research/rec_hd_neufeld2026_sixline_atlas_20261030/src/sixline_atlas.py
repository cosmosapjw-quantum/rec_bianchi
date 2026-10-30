"""Source-locked Neufeld (2026) standard/alternate HD six-line model atlas.

Science, not observation: J_upper=5..10 pure rotational HD, optically thin,
original Neufeld 2026 CMB model output, fixed HD column cancels in line ratios.

Inputs are the *byte-identical* 270-state/3780-line original-source model
outputs from independent PR171. The four Zenodo v2 original bytes are also
SHA-locked in this package to distinguish true source ownership.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

SOURCE = {
    'source/zenodo_v2/hd_lamda.dat': 'f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb',
    'source/zenodo_v2/hd_lamda_altex.dat': '66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac',
    'source/zenodo_v2/hd_population_grids.fits': '0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1',
    'source/zenodo_v2/hd_population_grids_altex.fits': '1fc3588b32e1423a5c56c68df43ee0385f38f62424615971857b403bf02d45de',
    'input/CMB15_STANDARD_VS_ALTEX_270_STATES.csv': '77ff228765534fc2ed1e53524676748174936d33bca21a285bc7a0c55963943f',
    'input/CMB15_STANDARD_VS_ALTEX_3780_LINE_PAIRS.csv': '34df6177f1a219c8537741aea4dfb82e90752f3a00c0b0b28919565b85534365',
}
FLOORS = (0.0, 0.001, 0.01, 0.05, 0.1)
C_MS = 299792458.0


def bytes_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_inputs(root: Path) -> None:
    for name, expected in SOURCE.items():
        actual = bytes_sha(root / name)
        if actual != expected:
            raise ValueError(f'Incorrect raw source identity: {name}: {actual}')


def load_csv(root: Path, relative: str) -> list[dict]:
    with (root / relative).open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def original_spectroscopy(root: Path) -> list[dict]:
    """Extract original radiative line identities without reinterpreting models."""
    f = root / 'source/zenodo_v2/hd_lamda.dat'
    rows = []
    for line in f.read_text().splitlines():
        parts = line.split()
        if len(parts) == 6 and parts[0].isdigit() and parts[1].isdigit():
            rows.append({'upper': int(parts[1])-1, 'lower':int(parts[2])-1,
                         'frequency_Hz': float(parts[4])*1e9, 'Einstein_A_s':float(parts[3])})
    if len(rows) != 14 or {x['upper'] for x in rows} != set(range(1,15)):
        raise ValueError('Original Neufeld LAMDA radiative identities unexpected')
    return rows


def analyze(root: Path) -> tuple[list[dict],list[dict],dict]:
    root = Path(root)
    verify_inputs(root)
    lines = load_csv(root, 'input/CMB15_STANDARD_VS_ALTEX_3780_LINE_PAIRS.csv')
    states = load_csv(root, 'input/CMB15_STANDARD_VS_ALTEX_270_STATES.csv')
    if len(lines)!=3780 or len(states)!=270:
        raise ValueError('Source-model numerical row contract not matched')
    spectrum = {x['upper']:x for x in original_spectroscopy(root)}
    state_index = {(float(x['Tgas_K']),float(x['nH2_cm3']),float(x['z'])):x for x in states}
    grouped = defaultdict(dict)
    for x in lines:
        k = float(x['Tgas_K']),float(x['nH2_cm3']),float(x['z'])
        up = int(x['J_upper'])
        if up in grouped[k] or up not in spectrum or int(x['J_lower'])!=up-1:
            raise ValueError('Duplicated or invalid transition')
        if not math.isclose(float(x['frequency_Hz']),spectrum[up]['frequency_Hz'],rel_tol=1e-13):
            raise ValueError('Source original frequency mismatch')
        grouped[k][up] = x
    if set(grouped)!=set(state_index) or any(len(v)!=14 for v in grouped.values()):
        raise ValueError('Source numerical atlas incomplete')
    max_ledger_rel=0.0
    pairs=[]
    hot_states=0
    for (T,n,z),entries in sorted(grouped.items()):
        for src,tk in [('std','std_net_cooling_W_per_HD'),('alt','alternate_net_cooling_W_per_HD')]:
            calc = math.fsum(float(v[src+'_net_W_per_HD']) for v in entries.values())
            truth = float(state_index[(T,n,z)][tk])
            rel=abs(calc-truth)/max(abs(calc),abs(truth),1e-42)
            max_ledger_rel=max(max_ledger_rel,rel)
            if rel>3e-14:
                raise AssertionError(f'Parent line-to-total ledger discrepancy {T,n,z,src,rel}')
        if T<1000:
            continue
        hot_states+=1
        six={j:entries[j] for j in range(5,11)}
        peak=max(float(v[s+'_net_W_per_HD']) for v in six.values() for s in ('std','alt'))
        if peak<=0:
            raise ValueError('No positive warm emission anchor')
        for low,high in itertools.combinations(range(5,11),2):
            lo,hi=six[low],six[high]
            std_low,std_high=float(lo['std_net_W_per_HD']),float(hi['std_net_W_per_HD'])
            alt_low,alt_high=float(lo['alt_net_W_per_HD']),float(hi['alt_net_W_per_HD'])
            if min(std_low,std_high,alt_low,alt_high)<=0:
                raise ValueError('Invalid warm positive emitted power; cannot take log ratio')
            ratio_std=std_high/std_low
            ratio_alt=alt_high/alt_low
            delta=ratio_alt/ratio_std-1.0
            logshift=math.log(ratio_alt)-math.log(ratio_std)
            frac_floor=min(std_low,std_high,alt_low,alt_high)/peak
            pairs.append({'Tgas_K':T,'nH2_cm3':n,'z':z,
                          'ratio_name':f'R({high-1})/R({low-1})',
                          'J_upper_numerator':high,'J_upper_denominator':low,
                          'rest_numerator_um':C_MS/spectrum[high]['frequency_Hz']*1e6,
                          'rest_denominator_um':C_MS/spectrum[low]['frequency_Hz']*1e6,
                          'standard_num_W_per_HD':std_high,'standard_denom_W_per_HD':std_low,
                          'alternate_num_W_per_HD':alt_high,'alternate_denom_W_per_HD':alt_low,
                          'standard_ratio':ratio_std,'alternate_ratio':ratio_alt,
                          'relative_source_delta':delta, 'log_source_delta':logshift,
                          'min_four_line_power_over_sixline_peak':frac_floor,
                          'qualifies_floor_0p1pct':frac_floor>=0.001,
                          'qualifies_floor_1pct':frac_floor>=0.01,
                          'qualifies_floor_5pct':frac_floor>=0.05})
    if hot_states!=120 or len(pairs)!=1800:
        raise AssertionError('Warm grid must have 120 conditions / 1,800 ratios')
    def peak_for(floor):
        qualify=[x for x in pairs if x['min_four_line_power_over_sixline_peak']>=floor]
        if not qualify:
            return {'count':0}
        top=max(qualify,key=lambda x:abs(x['relative_source_delta']))
        return {'count':len(qualify),'max_abs_relative_delta':abs(top['relative_source_delta']),
                'case':{k:top[k] for k in ('Tgas_K','nH2_cm3','z','ratio_name','relative_source_delta','standard_ratio','alternate_ratio','min_four_line_power_over_sixline_peak')}}
    floor_metrics={f'{int(1000*v)}_permille':peak_for(v) for v in FLOORS}
    ratio_stat=[]
    for (j,k) in itertools.combinations(range(5,11),2):
        select=[x for x in pairs if x['J_upper_denominator']==j and x['J_upper_numerator']==k]
        good=[x for x in select if x['qualifies_floor_1pct']]
        if good:
            vals=sorted(abs(x['relative_source_delta']) for x in good)
            mid=(vals[(len(vals)-1)//2]+vals[len(vals)//2])/2
            strongest=max(good,key=lambda x:abs(x['relative_source_delta']))
            ratio_stat.append({'ratio':f'R({k-1})/R({j-1})','valid_1pct_count':len(good),
                               'max_abs_change':abs(strongest['relative_source_delta']),
                               'median_abs_change':mid,'peak_T_K':strongest['Tgas_K'],
                               'peak_density_cm3':strongest['nH2_cm3'],'peak_z':strongest['z']})
    ratio_stat.sort(key=lambda x:x['max_abs_change'],reverse=True)
    sample=[x for x in pairs if x['ratio_name']=='R(9)/R(7)' and x['Tgas_K']==1000 and x['z']==0]
    density_sweep=sorted(sample,key=lambda x:x['nH2_cm3'])
    if len(density_sweep)!=5:
        raise AssertionError('Expected five physical source densities')
    summary={'program':'REC_HD_NEUFELD2026_SIXLINE_ATLAS_20261030','model':'Neufeld2026 Zenodo v2 original standard vs altex 15-level HD collision sources; optically thin CMB source models',
             'parent_pr':171,'parent_head':'8e1f51397cc3019642668daf4b2f2c39ff5126d5',
             'temperature_K':[1000,2000,3000,4000],'densities_cm3':[1e2,1e4,1e6,1e8,1e10],
             'redshifts':[0,10,30,50,73,100],'warm_physical_source_conditions':hot_states,
             'pair_ratio_cases':len(pairs),'num_MIRI_rest_frame_lines':6,
             'original_full_source_states':270,'original_full_line_pairs':3780,
             'max_parent_line_to_total_relative_residual':max_ledger_rel,
             'brightness_filter_description':'minimum of 4 physical model line powers from two transitions/two source variants, divided by the maximum of 12 warm six-line powers in same state; NOT an instrument detectability threshold',
             'floor_metrics':floor_metrics,'ranked_sixline_ratios_1pct':ratio_stat,
             'R9_over_R7_z0_1000K_density_sweep':density_sweep,
             'scope':'conditional source-model luminosity ratios (not sky flux, observed JWST detections, abundance, likelihood or thermal-history IVP)',
             'native_distinct_author_review':'NOT_RUN',
             'canonical_DAG':'28/88','REC_physical_DAG':'0/313','original_35Hz':'FAIL7/8','production':'HOLD','auto_next_node':False}
    return pairs,ratio_stat,summary


def write_csv(path: Path, rows: list[dict]):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def run(root: Path):
    pairs,rank,summary=analyze(root)
    out=Path(root)/'evidence';out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'SIXLINE_1800_SOURCE_RATIO_CASES.csv',pairs)
    write_csv(out/'SIXLINE_15_PAIR_RANKINGS.csv',rank)
    (out/'SIXLINE_SCIENCE_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
    args=ap.parse_args();print(json.dumps(run(args.root),indent=2))
