"""Exact counterexample: axes, corners and cancellation sentinels are insufficient."""
from fractions import Fraction as Q
import itertools
import json

def interaction(m, r):
    return m*r*(m*m-1)*(r*r-1)*(m+r)

def main():
    levels=list(map(Q,('-1','-1/2','-1/4','-1/8','0','1/8','1/4','1/2','1')))
    observed=[]; remaining=[]
    for s,m,r in itertools.product(levels,repeat=3):
        sentinel=m==0 or r==0 or (abs(m)==1 and abs(r)==1) or m==-r
        (observed if sentinel else remaining).append(interaction(m,r))
    assert len(observed)==243 and all(x==0 for x in observed)
    assert interaction(Q(1,2),Q(1,4))==Q(135,2048)
    assert any(x!=0 for x in remaining)
    print(json.dumps({'status':'EXACT_COUNTEREXAMPLE_VERIFIED',
        'polynomial':'m*r*(m*m-1)*(r*r-1)*(m+r)',
        'exactly_zero_at_axis_and_sentinel_cases':len(observed),
        'remaining_cases':len(remaining),'nonzero_remaining':sum(x!=0 for x in remaining),
        'witness_at_m_half_r_quarter':'135/2048',
        'implication':'All 243 controls passing cannot certify the remaining 486 without additional smoothness/error information.',
        'new_ODE_runs':0},indent=2))

if __name__=='__main__':main()
