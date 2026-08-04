# Reciprocal center-of-mass-resolved KHW formalism

## 1. Fixed-nucleus KHW amplitude

For internal atomic states \(A,B,I\),

\[
\mathcal M_{BA}^{\lambda_o\lambda_i}
=
\delta_{AB}\,\epsilon_i\!\cdot\!\epsilon_o
-\frac{1}{m_e}\sum_I
\left[
\frac{
\langle B|\mathbf p\!\cdot\!\epsilon_o|I\rangle
\langle I|\mathbf p\!\cdot\!\epsilon_i|A\rangle
}{
E_I-E_A-\hbar\omega_i
}
+
\frac{
\langle B|\mathbf p\!\cdot\!\epsilon_i|I\rangle
\langle I|\mathbf p\!\cdot\!\epsilon_o|A\rangle
}{
E_I-E_A+\hbar\omega_o
}
\right].
\]

The differential cross section contains
\((\omega_o/\omega_i)|\mathcal M|^2\).

For a fixed nucleus,

\[
E_A+\hbar\omega_i=E_B+\hbar\omega_o.
\]

Hence Rayleigh scattering \(A=B\) requires
\(\omega_o=\omega_i\). A fixed-nucleus Rayleigh amplitude with arbitrary
\(\omega_i\ne\omega_o\) is not a consistent recoil model.

## 2. Center-of-mass-resolved amplitude

Let the atom have initial momentum \(\mathbf P_i\) and final momentum

\[
\mathbf P_f=\mathbf P_i+\hbar(\mathbf k_i-\mathbf k_o).
\]

The two intermediate center-of-mass momenta are

\[
\mathbf P_i+\hbar\mathbf k_i
\quad\text{(absorption first)}
\]

and

\[
\mathbf P_i-\hbar\mathbf k_o
\quad\text{(emission first)}.
\]

The denominators become

\[
D_I^-=
E_I-E_A+
\frac{|\mathbf P_i+\hbar\mathbf k_i|^2-|\mathbf P_i|^2}{2M}
-\hbar\omega_i,
\]

\[
D_I^+=
E_I-E_A+
\frac{|\mathbf P_i-\hbar\mathbf k_o|^2-|\mathbf P_i|^2}{2M}
+\hbar\omega_o.
\]

Use these denominators in the same KHW numerator structure.

## 3. Exact reciprocity

The time-reversed event is

\[
(-\mathbf P_f,-\mathbf k_o)
\longrightarrow
(-\mathbf P_i,-\mathbf k_i).
\]

With

\[
E_A+\frac{P_i^2}{2M}+\hbar\omega_i
=
E_B+\frac{P_f^2}{2M}+\hbar\omega_o,
\]

the reverse absorption-first denominator equals the forward
absorption-first denominator, and likewise for the emission-first
denominator.  The Wolfram residuals are exactly zero.

Matrix-element reciprocity then follows from Hermiticity/time reversal
of the dipole or momentum operators, subject to the usual polarization
reversal.

## 4. Initial atom at rest

For \(\mathbf P_i=0\) and \(|\mathbf k|=\omega/c\),

\[
D_I^-=
\Delta_I-\hbar\omega_i+
\frac{\hbar^2\omega_i^2}{2Mc^2},
\]

\[
D_I^+=
\Delta_I+\hbar\omega_o+
\frac{\hbar^2\omega_o^2}{2Mc^2}.
\]

For a moving nonrelativistic atom,

\[
D_I^-=
\Delta_I-\hbar\omega_i+
\hbar\omega_i\frac{\mathbf v\cdot\mathbf n_i}{c}
+\frac{\hbar^2\omega_i^2}{2Mc^2},
\]

\[
D_I^+=
\Delta_I+\hbar\omega_o-
\hbar\omega_o\frac{\mathbf v\cdot\mathbf n_o}{c}
+\frac{\hbar^2\omega_o^2}{2Mc^2}.
\]

The first is the Doppler- and absorption-recoil-shifted resonant
denominator.  The second is the smooth crossed denominator.

## 5. Practical decomposition

Use

\[
\mathcal M
=
\mathcal M_{2p}^{\rm pole}
+
\mathcal M_{\rm bg}^{\rm bound}
+
\mathcal M_{\rm bg}^{\rm continuum}
+
\mathcal M_{\rm seagull}.
\]

The stationary elastic limit must reproduce the Lee near-Ly-alpha
series and the Kokubo bound+continuum cross section.  The moving-atom
implementation must instead satisfy the COM-resolved reciprocity gate.
