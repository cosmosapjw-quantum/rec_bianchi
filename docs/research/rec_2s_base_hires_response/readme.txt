                                             HYREC
          A code for primordial hydrogen and helium recombination
                         including radiative transfer
                             by Yacine Ali-Haïmoud and Chris Hirata
                                          Version: May 2012



Contents of the package:
Source code files:

hyrectools.c, hyrectools.h: array creation and interpolation routines (previously arrays.c/h)


helium.c, helium.h:               helium recombination routines

hydrogen.c, hydrogen.h:           hydrogen recombination routines

history.c, history.h:             ODE integration routines

hyrec.c, hyrec_params.h:           main recombination program and accuracy parameters

Data files:

Alpha_inf.dat: table of effective recombination coefficients for hydrogen
A2s(Tm, Tr) and A2p(Tm, Tr) (in cm3s-1) for 0.004 ≤ Tr ≤ 0.4 eV and 0.1 ≤ Tm/Tr ≤ 1.

R_inf.dat: table of effective 2p →2s transfer rate for hydrogen
R2p,2s(Tr) (in s-1), for 0.004 ≤ Tr ≤ 0.4 eV.
[Effective rates are extrapolated to an infinite number of excited states of hydrogen, nmax →∞]

two_photon_tables.dat: table of two-photon transition rates. Columns are:
Eb (in eV), 3A2p,1s ϕLyα(ν) Δνb (in s-1), dΛ2s,1s/dν Δνb (in s-1), (dΛ3s,1s/dν + 5 dΛ3d,1s/dν) Δνb (in s-1),
(dΛ4s,1s/dν + 5 dΛ4d,1s/dν) Δνb (in s-1).

input.dat: example input file for cosmological parameters (see below for a description)
Using HYREC:

Compiling the code:

Open a terminal session, enter the HyRec folder, and type at the command line, if gcc is your C
compiler (-O3 is an optimizing option, it makes the code run a little faster):

gcc -lm -O3 hyrectools.c helium.c hydrogen.c history.c hyrec.c -o hyrec

Computing a recombination history:

Once you have compiled the code, simply type at the command line:

./hyrec

You will be prompted to enter the value of the following cosmological parameters:
T0 [CMB temperature today, in Kelvin], Ωbh2 [baryon density], Ωmh2 [total matter density,
CDM+ baryons], Ωkh2 [curvature density], ΩΛh2 [dark energy density], w0, wa [parameters of
the dark energy equation of state, w(a) = w0 + wa(1 - a)], Nν,eff [effective number of neutrino
species]. The fine-structure constant and electron mass can also be entered as inputs (see below).

Once you have entered all required parameters, the code will compute the recombination history
and print three columns to the screen: redshift z from 8000 down to 0, spaced by Δz = 1, free
electron fraction xe, and ratio of matter to radiation temperature Tm/Tr.

Using input and output files:

If you do not want a prompt to appear every time you run the code, you can switch it off by
setting, at the beginning of hyrec_params.h:                 #define PROMPT 0
You can enter your input cosmological parameters into a file, in the order written above.
If your input file is named input.dat (see example provided in the package), and you wish the
recombination history to be printed out to the output file output.dat instead of the screen, type
at the command line:

./hyrec < input.dat > output.dat

If you use HYREC, please cite the companion paper:

Y. Ali-Haïmoud & C. M. Hirata, 2010, Phys. Rev. D 83, 043513 (2011)
You may also refer to the following papers, on which this work relies substantially:

Y. Ali-Haïmoud & C. M. Hirata, Phys. Rev. D 82, 063521 (2010)
C. M. Hirata, Phys. Rev. D 78, 023001 (2008)
E. R. Switzer & C. M. Hirata, Phys. Rev. D 77, 083008 (2008)

Switches
HYREC computes by default what we believe is the most accurate recombination history. If you
would like to see yourself what the difference is with previous physical models, or what impact
various new effects have on recombination, we have left some switches to play with (for
hydrogen recombination only):

In hyrec_params.h, you can choose to use the full recombination calculation (which is the
default), in which case leave the following line unchanged: #define MODEL FULL
You can also choose to use Peebles’ effective three-level atom model, in which case you should
change the above line to:                                    #define MODEL PEEBLES
or an effective three-level atom model for hydrogen with a fudge factor F = 1.14, similar to the
first version of RECFAST, in which case change the line to: #define MODEL RECFAST
 You can also use the correct effective four-level atom model, but with Lyα only (treated in the
Sobolev approximation) and 2s--1s two-photon decays (treated with a simple total decay rate),
no feedback or other radiative transfer effects, with:        #define MODEL EMLA2s2p

When using the FULL calculation, you can, if you wish, switch on and off two-photon processes
and diffusion. Various switches are available in hydrogen.h. By default, all switches should be
on (value = 1). You can switch them off (value = 0) if you wish. All switches set to zero
corresponds to an effective four-level atom model with Lyα, Lyβ and Lyγ treated in the Sobolev
approximation and feedback between them.
The available switches are EFFECT_A (correct handling of 2s--1s decays and absorptions, both
in the radiative transfer and to compute the total 2s--1s decay rate), EFFECT_B (sub-Lyα two-
photon transitions), EFFECT_C (super-Lyα two-photon transitions), EFFECT_D (Raman
scattering), and DIFFUSION (frequency diffusion in Lyα).

Printing out the Lyman-lines distortion:

It is now possible to print out the Lyman distortion (from half the Lyα frequency to the Lyγ
frequency; not including distortion photons from helium recombination). To do so, use the switch
#define PRINT_SPEC in hyrec_params.h , and modify the desired redshifts if necessary.
It is recommended to use the higher accuracy tables and integration parameters in
hyrec_params.h to obtain a smoother spectrum.
Varying the fine-structure constant and the electron mass:

The user can now easily input a different fine-structure constant or electron mass at
recombination than today’s value (they are however assumed to be constant during
recombination). This can be done by uncommenting the appropriate paragraph in history.c
(line 100) and providing α(rec)/α(today) and me(rec)/me(today) as input parameters, either at the
command line or in an input file.

Revision history
• First release: November 2010.
• Second release: January 2011
- Numerical integration switches from post-Saha expansions to explicit ODE integration were changed. The code is
  now well behaved for a wide range of cosmologies (in the previous version, numerical instabilities appeared at
  high redshift for some cosmologies). For more details, see Secs. V E (for hydrogen) and VI B (for helium) in the
  companion paper.

- The range of temperatures for the tabulated effective rates was extended to allow computations of the
  recombination history down to z = 20 (instead of 200 in the previous version). The used effective rates were
  extrapolated from rates computed with nmax up to 600 (vs. 500 in the previous version) in order to reach sufficient
  accuracy even at low temperatures.

- The differential two-photon decay rate from 2s, dΛ2s,1s/dν is now automatically normalized to the total 2s--1s
  decay rate Λ2s,1s , the value of which can be set by the user with the constant L2s1s in hydrogen.h.


• Third release: May 2012 (this version)
- File names were changed (arrays.c renamed hyrectools.c) and some of the contents of
  hyrec.c were transferred to history.c, for ease of inclusion into a Boltzmann code.
- The post-Saha expansion was made more accurate.
- The numerical solution of radiative transfer was made more robust by analytically subtracting
  nearly canceling terms, and computing departures from thermal equilibrium. The Lyman-lines
  spectrum can now be easily extracted.
- The integration is extended down to z = 0 with Peebles’ model once Tr < 0.004 eV
  (corresponding to z ≃ 15).
- The explicit dependences on the fine-structure constant and electron mass are now included.
- For more details, refer to the technical explanatory supplement and the comments in the source
  files.


This code is provided “as is” and no guarantees are given regarding its accuracy.
For questions or issues, please email yacine@ias.edu

Last updated May 3rd, 2012.
