import numpy as np
from fit_graph import cut_fit,L
def test_fit_exact_energy_and_action():
    e=np.array([0.,1.,2.],dtype=L)
    g=np.array([[0.,2.,1.],[2.,0.,3.],[1.,3.,0.]],dtype=L)
    A=np.diag(g.sum(axis=1))-g
    # Pair response per conductance: rate entering i from j.
    a=np.array([.3,.6,.4],dtype=L)
    F=a[None,:]-a[:,None]
    q=(g*F).sum(axis=1)
    fit,info=cut_fit(A,e,[(F,q)])
    assert fit.min()>=0
    assert np.max(abs((np.diag(fit.sum(axis=1))-fit)@e-A@e))<1e-12
    assert np.max(abs((fit*F).sum(axis=1)-q))<1e-8
