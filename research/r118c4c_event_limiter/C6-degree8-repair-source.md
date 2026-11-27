# C6-degree8-repair-source | R118-C4C REC

Degree8 default HiGHS LP produced negative exact minimum after 8 cuts on both signs (channel 238); preserve failures. Tighten feasibility tolerances to 1e-10 and increase exact-minimum cut iterations to 32, unchanged physical positivity threshold and moments. New distinct degree8tight variant, do not overwrite original results.
