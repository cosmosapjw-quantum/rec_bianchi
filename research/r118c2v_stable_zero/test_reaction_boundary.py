from reaction_boundary import conditioned_net,L
def test_conditioned_net():
    # Direct product difference is well-conditioned at depleted donor edge.
    assert conditioned_net(L('2.1e-26'),L(0),L('7.465e-28'))==-L('7.465e-28')
    # Stable increments own near-equilibrium differences.
    assert conditioned_net(L('1e-25'),L(1),L(1))==L('1e-25')
    assert conditioned_net(L('1e-24'),L(0),L(0))==0
