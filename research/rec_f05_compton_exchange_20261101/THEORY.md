# REC-F05 accepted source: instantaneous electron–CMB Compton energy budget

Date 2026-11-01; owner rec_bianchi; immutable parent REC #193
`488c68a69050401c96f730b192f38b498f6ceddd`.
REI original F05 source TAR SHA256
`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.
Original official accepted tick 160/131072; 46,080 source-native H/He cells.
The three shape-audit lanes are a SINGLE physical source population.

## Scientific question and relation to the IGM goal (R1–R4)

Compute the *instantaneous, source-conditioned* electron–isotropic-CMB Compton
kinetic-energy exchange and its relative scale to source gas kinetic energy at
the original accepted F05 tick160. This extends REC #193's measured electron
Thomson collision RATE to an energy-exchange law and estimates the size of a
possible missing thermal interaction term. It is not another opacity sky and
does not alter or rerun the source worker. REI #360 already treats the
H/He gas EOS, so this unit does NOT claim the EOS as novel.

Primary model identity: Ali-Haïmoud & Hirata, *Phys Rev D* 83, 043513 (2011),
DOI:10.1103/PhysRevD.83.043513, matter-temperature Compton equation (Eq. 12).
The original source uses H/He numbers and accepted endpoint log-temperature
boxes. Here we condition on an *additional* CMB blackbody bath
`Tgamma=T0*(1+z)` with `T0=2.728 K` (the original HyRec reference value).
The four-group REI F05 ionizing photons are NOT reinterpreted as that bath.

## Derivation (R5–R7)

Cgs units: `c=29979245800 cm/s`, `sigma_T=6.6524587051e-25 cm²`,
`k_B=1.380649e-16 erg/K`, `m_e=9.1093837139e-28 g`,
`a_R=7.5657e-15 erg cm^-3 K^-4`.
Signature convention (-,+,+,+). For each comoving original cell at the
source's proper-time end, define
`Ne = N_HII + N_HeII + 2 N_HeIII` and `T_e=exp(logT)`.
With a common nonrelativistic Maxwellian gas/electron temperature,
the leading Thomson/Compton energy transfer *to gas* is

    dU_gas,j/dt |_C = (4 sigma_T a_R Tgamma^4 k_B)/(m_e c)
                       * Ne_j * (Tgamma - T_e,j) .

Equivalent form: `4 sigma_T c (a_R Tgamma^4) Ne
* [k_B(Tgamma-T_e)/(m_e c²)]`.
This follows by multiplying the primary source temperature coupling
`dT_m/dt|_C = 8 sigma_T a_R Tgamma^4 x_e (Tgamma-T_m)/
[3 (1+f_He+x_e) m_e c]`
by `(3/2) N_H (1+f_He+x_e) k_B` at fixed particle count.
All units reduce to erg/s. Positive means gas heating, negative cooling.

The *gas translational* energy (not ionization-binding energy) is

    U_gas,j = (3/2) k_B T_e,j (N_H,j + N_He,j + Ne_j).

Conserve `N_H,j` and `N_He,j` from original tick0 initial NPZ.
For original endpoint intervals `Ne in [Nel,Neu]`,
`T in [Tl,Tu]`, evaluate the four corners of the bilinear Compton
function for guaranteed algebraic box enclosure. For original 46,080
cells `Tl>Tgamma` so every local Compton power is *negative*.
For positive energy, lower and upper bounds come from the monotone
endpoint products. The volume is not needed since Ne is a cell *number*.

Original frozen source first-interval z=5.95; Tgamma=18.9596 K.
The accepted source clock `t160=779495799866.9248046875 s`
gives `dt_tick=t160/160` by original tick measure. A diagnostic, NOT
integrated trajectory, is

    f_frozen_tick = abs(dU_C/dt at tick160)*dt_tick / U_gas(tick160).

Using interval bounds gives `f_lower = -Q_upper*dt/U_upper`
and `f_upper = -Q_lower*dt/U_lower`, with all terms positive.

## Adversarial review and adoption (R6–R10)

- This quantity is the *instantaneous* source-scoped Compton power; it does
  not assert that the original REI F05 integrator included this term.
- The specified isotropic CMB bath is an extra model input; original
  four-group ionizing photons are not merged with CMB photons.
- A finite frozen-tick fraction is NOT an IVP-integrated energy-loss bound
  without time-variation control. It cannot resolve REI owner's original
  2e-4 local-error gate, independent of its numerical magnitude.
- The `3/2 kT` energy neglects ionization potential and excludes photons,
  geometry and gravitational dynamics. It does NOT certify the total EOS.
- Populations and temperature are source-locked accepted intervals, not
  46,080 statistically independent runs. The three audit lanes are one.
- Error categories: source hashes = BYTE_IDENTITY; box arithmetic =
  source-conditional interval; f64 arithmetic = numerical approximation;
  nonrelativistic Compton closure = physical modeling assumption.
- A real time-integrated Compton source correction needs accepted state
  histories at intermediate times plus the coupled photon/T evolution.
  No fabricated tick161, Bianchi null ray, LoS tau, y-sky or CMB prediction.
- Production HOLD; no source owner swap, no merge, no force-push, no
  tolerance change; REI canonical 28/88, working 33/88, REC H5 0/313,
  every canonical delta zero.

This is a single new physical diagnostic with a minimal follow-on:
send the signed `Q_C` and frozen-tick fraction as a possible F05 thermal
feedback term to the original owner *for scientific evaluation*, not adoption.
