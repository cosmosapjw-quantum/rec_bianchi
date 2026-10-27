# HD successor: required precision identified; complete source deck not recovered

Unit `REI-COUPLED-FOLLOWUP-20261026`. Canonical `REC-HD-ADAPTER`, lead `cosmosapjw-quantum/rec_bianchi`. Investigation date2026-10-26. No scientific computation/test was run. Original seven failures,35Hz gate, LAMDA2289-byte input and prior evidence remain unchanged. New canonical completion increment0.

The prior [source resolution](../../blocker_parallel_20261026/atomic/HD_SOURCE_RESOLUTION.md) is reused. Its exact old residuals are not recomputed. This follow-up adds the following useful source-selection result: **a standard rounded CDMS catalogue, or even its default energy listing, is insufficient by format alone to certify the original35Hz consistency gate.** A high-precision same-fit term/frequency deck is needed; repeating the old tests or downloading only the12-line catalogue would not resolve that obligation.

## Derived precision requirement

The original gate tests `abs(100*c*(e_u-e_l)-nu) <= 35 Hz`, with wavenumbers in cm^-1, frequency in Hz and exact `c=299792458 m/s`.

For independent nearest-rounded fields with increments `q_e` cm^-1 and `q_nu` Hz, a common underlying transition is guaranteed to satisfy

`abs(residual) <= 100*c*q_e + q_nu/2`.

This is triangle inequality over two term energies and one frequency. It describes serialization error; experimental/model uncertainty is a different quantity.

[CDMS's own file-format documentation](https://cdms.astro.uni-koeln.de/classic/general) gives the ordinary MHz catalogue frequency as F13.4 and lower-state energy as F10.4 cm^-1. Consequently `q_nu=100 Hz`, `q_e=10^-4 cm^-1`, and the format-only bound is `2,997,924.58+50=2,997,974.58 Hz`. This does not prove every particular row fails35Hz; it proves that the documented precision alone cannot guarantee that gate.

The same documentation gives the default `.egy` energies as F18.6 cm^-1. Pairing those independently rounded term energies with ordinary catalogue frequencies still gives `29,979.2458+50=30,029.2458 Hz`. Thus the earlier suggestion to recover an `.egy` file is qualified: **its default printed precision is not enough**. Full model parameters plus an owner-exported adequate-precision term/frequency deck, or a documented higher-precision export, are needed. Merely adding trailing zeros changes neither information content nor this bound.

One sufficient serialization choice is `q_e=10^-9 cm^-1`, `q_nu=10 Hz`, giving the original `34.9792458 Hz` bound. This is an acceptance specification for a new source export, not authorization to change source values, switch models, or claim35Hz physical measurement accuracy. The selected line frequencies must come from the same fit/term energies; measured-frequency substitutions require separate provenance and cannot be assumed exactly compatible.

## Successor identity and actual retrieval

[CDMS species003501 documentation](https://cdms.astro.uni-koeln.de/cgi-bin/cdmsinfo?file=e003501.cat) identifies HD v=0, version3, August2026 and12 listed lines. It describes an Euler-type fit, theory-based initial parameters, recent precise combination differences and rejected older measurements. This is a real candidate source identity, not an adopted numerical deck. Version2/current metadata were already observed in the prior loop; this turn reconfirmed the version3 entry. No complete numerical catalogue, term list, model parameter file or immutable snapshot was recovered.

Actual retrieval boundaries:

| Surface | Observation |
|---|---|
| Current species documentation | Search/open returned version3 metadata; primary reference `turn82search0`, earlier full view `turn77view0` |
| `https://cdms.astro.uni-koeln.de/classic/entries/c003501.cat` | Direct HTTP retrieval returned503 upstream connection timeout; earlier search extraction timed out |
| Same entry with `?download=1` | HTTP503; no catalogue content |
| `https://cdms.astro.uni-koeln.de/classic/predictions/catalog/c003501.cat` | HTTP503; Exa timeout, including download-query variant |
| `https://cdms.astro.uni-koeln.de/cgi-bin/cdmssearch?file=c003501.cat` | Live HTTP503; search produced an empty frame page; earlier extractor's cached tabular link was inaccessible |
| `cdms.ph1.uni-koeln.de` official host variant | Species/catalogue extraction timed out |
| HTTP entry URL |15-second timeout, no bytes; no fallback source was substituted |
| `classic/predictions/daten/` directory | Primary index accessible, no listed HD-specific subdirectory; absence here is not proof no source exists elsewhere |
| CDMS VAMDC query | Official documented endpoint identified below; web reader rejected/inaccessible; direct request result recorded in retrieval receipt |

The official [VAMDC endpoint documentation](https://cdms.astro.uni-koeln.de/cdms/portal/general) supports a GET query at `https://cdms.astro.uni-koeln.de/cdms/tap/sync?LANG=VSS2&REQUEST=doQuery&FORMAT=XSAMS&QUERY=SELECT+All+WHERE+MoleculeStoichiometricFormula=%27HD%27`. A successful response would still need its species/version/fit identity and printed precision inspected. A complete XML response would not automatically establish that it is version3 or uses one energy convention.

Primary source metadata for the new precision derivation: CDMS general `turn87search0`, CDMS's published format table `turn87search3`, VAMDC interface `turn87search1`; directory `turn83view0`. These are tool retrieval locators; no source-byte hash is claimed for a file that was not obtained. Failed HTTP bodies are network diagnostics, not scientific data.

## Exact bounded next action

Source acquisition can resume when the owner/CDMS supplies a versioned high-precision same-fit deck: nine v=0,J0..8 term values, eight adjacent-J predicted frequencies, explicit centroids/hyperfine convention, positive/negative catalogue-tag interpretation, model/experimental uncertainties and original source identity. Preserve original version2 columns as historical evidence. The next authority decision must justify the successor's state relation and collision-energy convention before an affected implementation/test run is frozen. Ordinary `.cat` or default `.egy` precision is not sufficient evidence for an automatic substitution.

No synthetic cumulative-frequency ladder is adopted. No tolerance is enlarged. No unchanged old test or IVP is rerun. Stop the current acquisition branch here because repeated unavailable endpoints add neither source evidence nor a viable computation. `REC-HD-ADAPTER` stays HOLD; no other molecular node is closed by this literature result.
