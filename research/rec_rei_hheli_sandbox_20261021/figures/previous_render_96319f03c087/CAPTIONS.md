# Figure captions — conditional preliminary pilot

These figures use **125 hash-verified completed cases out of 125 planned cases**. The case loader verifies the frozen scientific identity, COMPLETE → RESULT → trajectory byte hashes, the full 193-node redshift interval, species order, Frobenius normalization, signed component sums, and electron abundance consistency. Uncompleted cases do not contribute to envelopes or points. Their sweep cells remain blank.

## 01 — Shear and separate stress evolution

All curves are saved trajectories from z=20 to z=2. Shading gives the min–max of completed cases and the black line their median; this is a sampled parameter envelope, not an uncertainty interval or an error bound. Colored curves identify actual initial physical coordinates. The plotted norms are Sigma_F=sqrt(6)|s|/H and Pi_A=sqrt(6) kappa_t |p_A|/H², with kappa_t=8 pi G/c² for energy-density stresses. Signed matter and radiation components are added before taking the total norm. Half-contraction values equal Frobenius values divided by sqrt(2). Symlog axes retain zeros.

## 02 — Physical three-axis sweep

Each endpoint scatter point is one completed case at z=2. The horizontal coordinate is final Sigma_F, the vertical coordinate is signed matter or radiation stress, and color gives initial Sigma_F. The lower panels show signed total stress at the nearest saved node to z=8 and at z=2 on a fixed initial-Sigma slice. Their axis coordinates are initial physical signed Pi_m and Pi_r, not amplitude coefficients A_m/A_r. The actual saved redshift and slice value appear in the titles. Cells are discrete samples without interpolation; grey cells have no completed result.

## 03 — All retained ionic states

Representative case: `s03_m03_r03`. Each curve is the saved number abundance divided by that isotope's initial total inventory. No clipping or instantaneous renormalization is applied. H1 and D have charges 0–1; He3 and He4 have charges 0–2; Li6 and Li7 have charges 0–3, including Li IV. The shared electronic rates across isotopes are an explicit elemental-electronic-equality approximation. The frozen pilot has zero initial neutron and tritium inventory; their saved zero-population status is annotated rather than displayed as active histories. Symlog axes show trace ionic fractions and retain exact zero.

## 04 — Opacity and energy bookkeeping

The same evolving 21-state ion populations supply n_e for the photon Thomson operator and optical-depth integral. Neutrinos remain collisionless. Gas temperature and optically thin UV are prescribed external functions, and the baryonic gas is isotropic. Thermal, ionization, and external-UV energies are retained as test-fluid diagnostics; their energy ratio is not fed back into the Einstein background. Required net gas input, absorbed UV power, bath-minus-escape, and Li I core excitation remain distinct. Neutral-Li inner-shell events use the explicitly assumed single-step charge yield; neither these figures nor the absorption coefficients determine Auger branching or a heating yield.

**Scope:** conditional prescribed T/UV preliminary model; Physical HOLD; global convergence NOT_RUN; production NOT_APPROVED. Existing REC U5 HOLD is unchanged. These plots do not constitute a fully closed thermal, radiation-transfer, or photonuclear calculation.
