import numpy as np
from opacity import positive_graph,pair_terms,L
def test_positive_graph_and_bose():
 e=np.array([1.,2.,3.],dtype=L)
 d=np.array([1.,-2.,1.],dtype=L);A=np.outer(d,d)+np.outer([1.,-1.,0.],[1.,-1.,0.])
 g,info=positive_graph(A,e)
 assert np.min(g)>=0 and np.allclose(g,g.T)
 assert abs(e@(np.diag(g.sum(axis=1))-g)@e-e@A@e)<1e-15
 z=np.exp(-e/10);x=L('.7');fp=1/np.expm1(e/10);v=np.zeros(3,dtype=L)
 gam,em,net=pair_terms(g,z,fp,v,x)
 assert min(gam)>=0 and max(abs(net))<1e-15 and abs(net.sum())<1e-15
 v=np.array([.01,-.02,.03],dtype=L)
 gam,em,net=pair_terms(g,z,fp,v,x)
 assert max(abs(em-gam*v-net))<1e-15 and abs(net.sum())<1e-15

def test_energy_action_preserving_positive_graph():
    from opacity import energy_action_graph
    # Exact Galerkin form of a fine pair whose interpolants straddle a node.
    e=np.array([0.,1.,2.],dtype=L)
    d=np.array([.6,-.2,-.4],dtype=L)
    A=np.outer(d,d)
    g,info=energy_action_graph(A,e)
    assert np.min(g)>=0
    B=np.diag(g.sum(axis=1))-g
    assert np.max(abs(B@e-A@e))<1e-15
    assert abs(e@B@e-e@A@e)<1e-15
