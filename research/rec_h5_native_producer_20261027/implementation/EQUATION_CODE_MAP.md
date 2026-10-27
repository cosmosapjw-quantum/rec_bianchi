# C2 equation–data–code map
The source walk inspected the actual prepared modules before scientific execution. C5 will pin their admitted bytes after implementation finishes.

| Mathematical/data operand | Actual input and conversion | Prepared code path |
|---|---|---|
| Exact native constants and source locks | hydrogen.h decimal tokens -> binary64 -> Fraction; locked file SHA256 | code/native_reference.py: read_sources, fraction64 |
| 313 stored geometric cells | SOURCE_CONTEXT endpoint/query hex and exact rational alpha/coefficient/anchor | read_sources verifies route, prefix and exact rational relations |
| Target/source energies | Tagged CSV VIRTUAL energy field2; hydrogen.h E21/E31/E41; special Lyman routes | read_sources returns raw source scalars and binding metadata |
| Native represented temperature | CSV META TR_eV_rescaled -> exact binary64 rational, separate from real kN*T0*(1+z) | read_sources and produce |
| Outward real arithmetic | Exact rational interval conversion, directed basic operations, expanded elementary values | code/interval80.py: I and elementary |
| w and first three derivatives | x=Es exp(eta)/(kN T0); explicit theorem formulas | interval80.derivatives |
| Whole-cell M1_ref/M2_ref | Endpoint candidates, interval-safe critical candidates, proved monotone branch | interval80.envelopes |
| Characteristic and temperature bridges | qstar/delta, nested expm1, separate native temperature | native_reference.produce |
| Chord and old anchor | exact geometric alpha, stored signed samples and anchor rational | native_reference.produce |
| Independent original-point evaluation | Separate raw-input conversion and direct exp/interpolant differences at140 digits | code/point_reference140.py: evaluate |
| Boundary and analytic controls | Critical cells, exact equality, domain errors, chord and translation identities | code/controls.py: run_controls |
| Plot transport | Float conversion of saved numeric diagnostics only | code/plot_results.py: plot_packet |
| Bounded execution and provenance | Frozen argv, one thread, CPU/wall/address-space limits | code/run_bounded.py (wrapper completion at C5) |

The source callback returns direct signed occupation departures. No exponential factor is inserted into that native interpolation. G=f-w is used to reconstruct and compare the absolute interpolant through the derived additive bridge.

## Cause classification and two pre-execution numerical clarifications
The open full H5 packet is an actual-input dependency: the photon archive and one native face do not provide a full coupled physical trajectory. It is not an implementation excuse to fill unavailable radii with surrogate values.

Two numerical boundary details were identified during implementation preparation. Exact elementary identities at zero/one must remain exact rather than introducing subnormal neighbors. A merely possible critical point may enlarge an upper supremum bound but may contribute to a certified lower supremum endpoint only with proved membership. C3 formalizes both; the delegated implementer applies the minimal correction before first execution. The frozen native physical model and primary80/independent140 precision remain unchanged.
