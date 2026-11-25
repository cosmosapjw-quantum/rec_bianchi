"""Use a well-conditioned direct difference at an empty donor boundary."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2r_stable_extent'))
from stable_extent import StableReaction,L
def conditioned_net(stable,A,B):
    gross=A+B;direct=A-B
    # Condition number <=4 in this branch, so direct difference is safe.
    # When both gross rates are exactly zero, the physical net is zero.
    if gross==0 or abs(direct)>=gross/4:return direct
    return stable
class BoundaryReaction(StableReaction):
    def net_rates(self,s,event,delta=L(0)):
        f,g,A,B=super().net_rates(s,event,delta)
        return conditioned_net(f,A,B),g,A,B
    def local_rates(self,s,event):
        r=super().local_rates(s,event)
        def trial(x):
            f,g,A,B=r(x);return conditioned_net(f,A,B),g,A,B
        return trial
