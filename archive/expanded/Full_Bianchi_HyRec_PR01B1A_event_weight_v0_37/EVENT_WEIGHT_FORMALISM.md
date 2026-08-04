# PR-01B1-A Maxwell-Juettner 2p event conductance

## Scope

This stage locks the microscopic equilibrium conductance of one exact
elastic photon-hydrogen event.  It does not yet integrate over the atom
momentum distribution or deposit the event into frequency-angle cells.

## Maxwell-Juettner measure

For \(p=Mcq\), \(\gamma=\sqrt{1+q^2}\), and
\(z=Mc^2/(k_BT)\),

\[
\int d^3p\,e^{-z\gamma}
=4\pi M^3c^3\frac{K_2(z)}{z}.
\]

Equivalently, using kinetic energy \(K=(\gamma-1)Mc^2\),

\[
F_{\rm MJ}(\boldsymbol p)
=\frac{e^{-K/(k_BT)}}
{4\pi(Mc)^3\theta e^{1/\theta}K_2(1/\theta)},
\qquad \theta=\frac{k_BT}{Mc^2}.
\]

The implementation evaluates the scaled Bessel function
\(e^zK_2(z)\), so the physical recombination value \(z\sim10^9\) is
numerically stable.

## PT-reversed event

For
\[
(P_i,k_i)\rightarrow(P_f,k_f),
\]
the PT reverse is
\[
(\overline P_f,\overline k_f)
\rightarrow
(\overline P_i,\overline k_i),
\qquad
\overline p=(p^0,-\boldsymbol p).
\]

The exact event identities imply
\[
P_f\cdot k_f=P_i\cdot k_i,
\qquad
P_f\cdot k_i=P_i\cdot k_f.
\]
Hence the forward and reverse initial-atom-rest-frame photon frequencies
are identical pairwise.

## Scalar 2p audit response

The provisional scalar response is
\[
\mathcal M_{2p}
=-\frac{f_{12}\nu_\alpha}{2}
\left[
\frac1{\nu_\alpha-\nu_i^*-i\gamma}
+
\frac1{\nu_\alpha+\nu_f^*+i\gamma}
\right],
\]

\[
\mathscr R_e
=\sigma_T\,\frac34(1+\mu_*^2)
\frac{\nu_f^*}{\nu_i^*}
|\mathcal M_{2p}|^2.
\]

This uses the standard Kramers-Heisenberg outgoing/incoming frequency
factor and the normalized scalar Rayleigh phase.  PR-03 replaces this
provisional amplitude by the full seagull + bound + continuum COM-KHW
amplitude.

## Equilibrium conductance

Up to a common event normalization,
\[
\log\mathcal S_f
=\log F_{\rm MJ}(P_i)
-\frac{h\nu_i}{k_BT}
+\log\mathscr R_f.
\]
The reverse expression uses \(P_f,\nu_f,\mathscr R_r\).  Since
\[
K_i+h\nu_i=K_f+h\nu_f
\]
and \(\mathscr R_f=\mathscr R_r\) under PT,
\[
\boxed{\mathcal S_f=\mathcal S_r}.
\]

## Numerical policy

Near the narrow 2p pole, a one-Hz float64 detuning error may create a
\(10^{-10}\)-level response mismatch.  Production therefore stores one
shared event invariant after an independent arbitrary-precision PT audit.
No posterior matrix symmetrization is used.
