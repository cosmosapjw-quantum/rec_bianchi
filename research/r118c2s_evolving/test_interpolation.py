import numpy as np,pytest
from evolving import KernelHistory
def test_log_positive_and_exact_anchors():
    t=np.array([2.,3.,4.]);n=np.array([10.,20.,30.]);K=np.array([[1.,3.],[2.,6.],[3.,12.]])
    p=KernelHistory(t,n,K)
    for i in range(3):assert np.array_equal(p(t[i],n[i]),K[i])
    assert np.all(p(2.5,15)>0)
    with pytest.raises(ValueError):p(1.,10)
