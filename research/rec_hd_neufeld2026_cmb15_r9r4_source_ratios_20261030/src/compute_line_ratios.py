"""Source-locked HD 15-level optically thin R(9)/R(4) line-ratio sensitivity.

R(J): (J+1)->J. This uses original Neufeld2026 standard/alternate
collision-rate models, distinct from any CDMS 2011 owner-spectrum approval.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

LINE_SHA = '34df6177f1a219c8537741aea4dfb82e90752f3a00c0b0b28919565b85534365'
STATES_SHA = '77ff228765534fc2ed1e53524676748174936d33bca21a285bc7a0c55963943f'


def _read_locked(path: Path, sha: str) -> list[dict]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError(f'Source SHA256 mismatch for {path.name}')
    return list(csv.DictReader(raw.decode('utf8').splitlines()))


def compute(lines_csv: Path, states_csv: Path):
    lines = _read_locked(lines_csv, LINE_SHA)
    states = _read_locked(states_csv, STATES_SHA)
    assert len(lines) == 3780 and len(states) == 270
    groups = {}
    for row in lines:
        key = (float(row['Tgas_K']), float(row['nH2_cm3']), float(row['z']))
        group = groups.setdefault(key, {})
        upper = int(row['J_upper'])
        assert upper not in group and int(row['J_lower']) == upper - 1
        group[upper] = row
    assert len(groups) == 270 and all(len(g) == 14 for g in groups.values())
    sidx = {(float(x['Tgas_K']), float(x['nH2_cm3']), float(x['z'])): x for x in states}
    assert groups.keys() == sidx.keys()
    # Guard that all 14 line powers actually reconstruct the independent
    # paired total outputs, not just a particular two-line ratio.
    maximum_ledger_error = 0.0
    for key, entries in groups.items():
        state = sidx[key]
        for src in ('std', 'alt'):
            total = sum(float(e[src+'_net_W_per_HD']) for e in entries.values())
            ref_key = 'std_net_cooling_W_per_HD' if src == 'std' else 'alternate_net_cooling_W_per_HD'
            actual = float(state[ref_key])
            err = abs(total - actual) / max(abs(total), abs(actual),1e-42)
            maximum_ledger_error = max(maximum_ledger_error,err)
            if err > 3e-14:
                raise AssertionError(f'Line-to-total energy ledger violated: {key}, {src}: {err}')
    ratio_rows = []
    for (T,n,z), items in sorted(groups.items()):
        if z!=0 or T < 1000 or n < 1e4:
            continue
        r4=items[5]  # R(4) is J=5 -> 4
        r9=items[10] # R(9) is J=10 -> 9
        w = [float(r4[k]) for k in ('std_net_W_per_HD','alt_net_W_per_HD')]
        y = [float(r9[k]) for k in ('std_net_W_per_HD','alt_net_W_per_HD')]
        if min(*w,*y) <= 0:
            raise ValueError('Line flux ratio invalid because source output non-positive')
        std_ratio = y[0]/w[0]
        alt_ratio = y[1]/w[1]
        ratio_rows.append(dict(Tgas_K=T,nH2_cm3=n,z=z,
                               std_R4_W_per_HD=w[0],alt_R4_W_per_HD=w[1],
                               std_R9_W_per_HD=y[0],alt_R9_W_per_HD=y[1],
                               std_R9_over_R4=std_ratio,alt_R9_over_R4=alt_ratio,
                               alt_over_std_ratio_minus_1=alt_ratio/std_ratio-1))
    if len(ratio_rows)!=16:
        raise AssertionError('Unexpected number of physically selected warm cases')
    maxcase = max(ratio_rows,key=lambda x:abs(x['alt_over_std_ratio_minus_1']))
    return ratio_rows, dict(
        unit='REC_HD_NEUFELD2026_CMB15_LINE_RATIO_20261030',
        total_source_states=270,source_line_records=3780,selected_warm_cases=len(ratio_rows),
        selection='Tgas>=1000 K, nH2>=1e4 cm^-3, z=0, optically thin, single HD column',
        source_originals='Neufeld 2026 Zenodo v2 standard vs altex; high-J J>8 rate extrapolation conditional',
        R9='upper J=10 -> lower J=9',R4='upper J=5 -> lower J=4',
        maximum_paired_total_energy_ledger_relative_error=maximum_ledger_error,
        max_abs_relative_ratio_change=maxcase['alt_over_std_ratio_minus_1'],
        max_case=maxcase,
        median_abs_relative_ratio_change=0.5*sum(sorted(abs(v['alt_over_std_ratio_minus_1']) for v in ratio_rows)[7:9]),
        canonical_DAG='28/88',physical_DAG='0/313',original_35Hz='FAIL7/8',production='HOLD',
        source_line_sha256=LINE_SHA,source_states_sha256=STATES_SHA,
        caveat='Model-predicted line luminosity ratio; not measured flux or HD/H2 abundance inference.'
    )


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--lines',type=Path,required=True)
    p.add_argument('--states',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    rows,summary=compute(a.lines,a.states)
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'HD_R9_R4_SOURCE_RATIO_16_WARM_CASES.csv').open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
    (a.output/'HD_R9_R4_SOURCE_RATIO_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
