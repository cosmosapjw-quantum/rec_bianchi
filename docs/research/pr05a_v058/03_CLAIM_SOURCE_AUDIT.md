# Claim/source audit

The source symbol `DAlpha` is not a derivative. In `hydrogen.c::interpolate_rates` it is explicitly `Alpha(Tm,Tr)-Alpha(Tr,Tr)`. The public schema therefore names it `delta_alpha`; derivative fields are separately named `d_*`. Alpha is converted from cm^3/s to m^3/s. Beta, R2p2s and integrated-bin A tables remain s^-1. The 2p detailed-balance rate carries the source factor 1/3, paired with a 2p degeneracy of 3 in the equilibrium population.
