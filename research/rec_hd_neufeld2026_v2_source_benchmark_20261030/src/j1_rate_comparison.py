"""Source-matched J=1->0 two-level radiative power contrast; no external CMB.

The 36 source rate pairs were transcribed from original sha-pinned files stored
in GitHub (originals are never overwritten). Results are source-conditioned models.
"""
import csv
from pathlib import Path
from neufeld15 import H,SI_CONVERSION

ROOT=Path(__file__).resolve().parents[1]


def compare():
    with (ROOT/'input/MATCHED_2021_2026_36_RATE_PAIRS.csv').open() as f:
        rates=list(csv.DictReader(f))
    if len(rates)!=36:raise ValueError('Expected 36 common rate rows')
    for row in rates:
        if float(row['rate_2021_cm3_s'])<=0 or float(row['rate_2026_cm3_s'])<=0:
            raise ValueError('Invalid source rate')
    res=[]
    for T in (100,200):
        filtered=[r for r in rates if int(r['u1based'])==2 and int(r['l1based'])==1 and int(r['T_K'])==T]
        if {r['collider'] for r in filtered}!={'para','ortho'}:raise ValueError('Spin branch source missing')
        old=float(filtered[0]['rate_2021_cm3_s'])
        new=sum(float(r['rate_2026_cm3_s'])*(0.25 if r['collider']=='para' else 0.75) for r in filtered)
        Aold,Anew=5.442e-8,5.442038e-8
        delK=SI_CONVERSION*89.227931612
        def p1(A,q,n):
            d=n*q;u=d*3*__import__('math').exp(-delK/T)
            return u/(u+d+A)
        for density in (1e2,1e4,1e6,1e8,1e10):
            lo=p1(Aold,old,density)*Aold*H*2.674986094e12
            ln=p1(Anew,new,density)*Anew*H*2.674986094e12
            res.append(dict(T_K=T,nH2_cm3=density,q_2021_cm3_s=old,q_2026_cm3_s=new,
                            ncrit_2021_cm3=Aold/old,ncrit_2026_cm3=Anew/new,
                            photon_power_2021_W_perHD=lo,photon_power_2026_W_perHD=ln,
                            ratio_2026_over_2021=ln/lo))
    return res
if __name__=='__main__':
    rows=compare()
    with (ROOT/'evidence/J1_2021_2026_10_COOLING_CASES.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print(len(rows),rows[1],rows[6])
