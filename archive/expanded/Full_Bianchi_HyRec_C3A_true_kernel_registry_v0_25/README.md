# Full Bianchi-HyRec C3A true-kernel and Bianchi registry v0.25

This bundle replaces the synthetic boundary true kernel by the physical
channel-resolved 1+1 Ly-alpha equation and locks the canonical
(a_alpha,n_ab) registry for all 11 Bianchi types.

## Hard results

- exact thermodynamic-factor residual: 5.009101e-15
- channel LTE residual: 4.608527e-15
- bosonic completion residual: 0.000000e+00
- partition residual: 0.000000e+00
- stoichiometry residual: 0.000000e+00
- exact JVP residual: 6.776264e-21
- maximum Bianchi Jacobi residual: 0.000000e+00
- maximum connection metric residual: 0.000000e+00
- maximum direction-norm residual: 1.940297e-16

The compiler algebra is physical. Numerical channel rates and the two
asymmetric profile shapes are regression inputs and must be replaced by
EMLA/two-photon tables in C3B.
