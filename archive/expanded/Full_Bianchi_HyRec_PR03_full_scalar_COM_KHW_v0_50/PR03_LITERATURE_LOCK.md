# PR-03 literature and provenance lock

Retrieved and cross-checked on 2026-08-05. These sources fix the bounded scalar-elastic Kramers–Heisenberg–Waller implementation and its audits; they do not enlarge the v0.50 scope beyond the limitations in `PR03_ledger.json`.

1. Mitsuru Kokubo, “Rayleigh and Raman scattering cross-sections and phase matrices of the ground-state hydrogen atom, and their astrophysical implications,” *MNRAS* **529** (2024) 2131–2149, DOI `10.1093/mnras/stae515`, arXiv `2308.04959`.
   - Lock used: explicit ground-state hydrogen KHW construction, Rayleigh/Raman channel distinction, angular phase structure.
2. Hee-Won Lee and Hee Il Kim, “Rayleigh scattering cross-section redward of Lyα by atomic hydrogen,” *MNRAS* **347** (2004) 802–806, DOI `10.1111/j.1365-2966.2004.07255.x`, arXiv `astro-ph/0402023`.
   - Lock used: infinite bound-state sum plus continuum integral and the infrared cross-section scaling proportional to the fourth power of frequency.
3. Hee-Won Lee, “Exact low-energy expansion of the Rayleigh scattering cross-section by atomic hydrogen,” *MNRAS* **358** (2005) 1472–1476, DOI `10.1111/j.1365-2966.2005.08859.x`.
   - Lock used: exact low-energy coefficients, Dalgarno–Lewis cross-check, and static-polarizability/infrared audit.

## Tool provenance

- Web search: used for source discovery and bibliographic cross-checking.
- Wolfram connector: not exposed in this runtime.
- Precise Special Functions connector: not exposed in this runtime.
- Explicit fallbacks: SymPy exact identities; `mpmath` 90–100 decimal calculations; SciPy positive quadrature and Faddeeva implementation.
