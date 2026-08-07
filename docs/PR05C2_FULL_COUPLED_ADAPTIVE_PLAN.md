# PR-05C2 full coupled adaptive trajectory

Couple the v0.62 canonical-macro controller to the 35-state COM--KHW collision state, split-domain red/blue interface accumulators, and actual time-dependent `BackgroundSnapshot` characteristics. Preserve typed scalar-history ownership, exactly-once macro commit, and canonical Sobolev/A1s/Tvv owners.

Hard gates: shifted JVP <1e-8; gross backward and algebraic residuals <1e-11; strict positivity without clipping; photon number; exact face energy; cosmological redshift work; collision photon/atom four-force; zero interface atom source; event-time and tolerance refinement; restart determinism; fixed-local-state Bianchi firewall.
