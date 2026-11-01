# REC → REI IGM: source-owned local Thomson pilot (R1–R10)
2026-11-01 | non-IVP | noncanonical | draft/HOLD

## Original physical owner
REC PR #183 head c15a1204c5580f278d095e7f24416bf386a5b6c5.
Input is **not** a new primordial Bianchi recombination history: exact REC original HyRec2012 FLRW zbar=20 boundary packet:
research/rec_r3c_rei_bridge_20261015/REI_CONDITIONAL_BOUNDARY.json
Git blob 89cdfc766e2e613760d84274812f2b4432373354,
native HyRec stdout SHA256 6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400,
recipient scenario SHA256 07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696.
REC recipient uses nH_REI=1757.9215875815148 m^-3 (not native HyRec nH), H_FLRW=1.1835101980340536e-16 s^-1, and a conditional neutral-He projection for donor at zbar=20.
HyRec donor is NOT adopted in REI. Astrophysical ionizing photon initial stock is left at original zero.

## R5 explicit derivation
At only the zbar=20 event use ds²=-c²dt²+a²e^(-2b)(dx²+dy²)+a²e^(4b)dz²,
s=db/dt, H²=H_FLRW²+s², q=s/H_FLRW; mu=local propagation-axis cosine.
For a null photon with conserved spatial covariant momentum, dln E/dt =
-[H+s(3mu²-1)] in a non-tilted comoving tetrad.
For proper electron density ne, dτ=c σ_T ne dt and
 dτ/dln(1+z_direction)= (c σ_T ne/H_FLRW) F(q,mu),
 F(q,mu)=[sqrt(1+q²)+q(3mu²-1)]^(-1).
This is the **local directional-redshift Jacobian**, not an integral along the ray.
The separate mean-a quantity is dτ/dln a=cσ_T ne/H with H=H_FLRW sqrt(1+q²).
Equating the two is incorrect outside q=0. The local direction mu evolves along a geodesic and cannot be treated as a fixed global observed angle.

## R6/R7 adversarial algebra and reference
Let A=sqrt(1+q²)-q, B=3q. Then F=1/(A+B mu²).
The angular monopole is I0=integral_0^1 F dmu, and P2 coefficient is
 a2=(5/2) integral_0^1 (3mu²-1)F dmu.
For B>0, I0=atan(sqrt(B/A))/sqrt(A B); for B<0,
 I0=atanh(sqrt(-B/A))/sqrt(-A B). I2=(1-A I0)/B; a2=(5/2)(3 I2-I0).
At q=0 exactly I0=1, a2=0. Symbolically I0'=0, I0''=3/5,
hence I0=1+3q²/10+O(q³); a2=-2q+O(q²).
Wolfram independent algebra plus local scipy.quad and stdlib elementary forms:
q -0.010: I0 1.0000304626831134, a2 +0.02011573906799715.
q -0.005: I0 1.0000075574867307, a2 +0.01002875153735054.
q +0.005: I0 1.0000074431963408, a2 -0.00997160562809775.
q +0.010: I0 1.0000295482477536, a2 -0.01988711879789478.
This validates local algebra, not a coupled cosmological source/transport run.
Literature support for null propagation in Bianchi I: Fleury, Pitrou & Uzan,
Phys Rev D 91 043511 (2015), arXiv:1410.8473v3; exact source derivation is specific to this REC/REI clock.

## R8/R9 decision and actual consumer boundary
Original REI code at PR #318 head 4e9ee7114bff272c68a85d6907f4beeb21f93bb4:
src/rei_bianchi/monolithic_model_b2a.py::electron_density,
Git blob 3d806e1c1d3bb523bb3c339d1a141f67d7f10069,
returns nH_phys*xHII+nHe_phys*(xHeII+2*xHeIII).
Our z20 mapping uses the REI nH normalization; donor xHII=xe is **conditional neutral helium**, not measured He species. We check this arithmetic *semantic* interface only. No native REI input adapter, no electron-history injection, no B2C2 first interval, and no accepted REI-F08 paired history.
The calculated two branches x five q x 21 directions = 210 local model rows,
and 2 x five angular moment summaries = 10 rows.
This is a bounded source-conditioned directional non-IVP diagnostic, *not an EoR prediction*.
R10: preserve accepted central 28/88, REC H5 0/313, REI working 33/88,
REI Physical Fast 4/7; no newly admitted node/cell, no merge, no source owner switch,
no 35Hz relaxation, no production/L4 activation, no new IVP or inherited-budget reset.

## One genuine adversarial finding
A plausible but incorrect implementation sets dτ/dln a equal to dτ/dln(1+z_direction)
for every mu. This deletes the linear quadrupole, even though the angle-average
has zero first shear variation. The source-matched directional Jacobian corrects it.
Another risk is the unpublished/no native consumer adapter: this **remains OPEN**
rather than falsely closing REC_REI_HISTORY_CONSUMER_BINDING.

## Next executable central edge
REI owner must independently source-authorize its FIRST COMPLETE BDF interval (REI-F05)
and physically accept a FLRW/Bianchi matched history (REI-F08) before this conditional
local diagnostic is used as a cosmological prediction. REC adapter is optional for
an H/He-only S0 demonstration; existing REI NO_MORE_IVPS budget scope is preserved.