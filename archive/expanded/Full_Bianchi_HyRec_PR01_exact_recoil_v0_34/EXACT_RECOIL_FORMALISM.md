# PR-01A exact elastic recoil kinematics

## Conventions

Metric signature:

\[
g_{\mu\nu}=(-,+,+,+).
\]

All public four-momenta use SI momentum units,

\[
p^\mu=\left(\frac Ec,\boldsymbol p\right).
\]

Thus

\[
P^2=-M^2c^2,
\qquad
k^2=0.
\]

A photon with hydrogen-frame frequency and direction
\((\nu,\boldsymbol n)\) has

\[
k^\mu=
\frac{h\nu}{c}
(1,\boldsymbol n).
\]

An atom with velocity \(\boldsymbol\beta=\boldsymbol v/c\) has

\[
P^\mu=
\Gamma Mc(1,\boldsymbol\beta).
\]

## Exact rest-frame recoil

In the initial atom rest frame,

\[
P_i^{*\mu}=(Mc,\boldsymbol0).
\]

Energy–momentum conservation is

\[
P_i^*+k_i^*=P_f^*+k_f^*.
\]

Imposing the final atom mass shell gives

\[
\boxed{
\nu_f^*
=
\frac{\nu_i^*}
{1+
\frac{h\nu_i^*}{Mc^2}
(1-\mu^*)}
}
\]

with

\[
\mu^*=
\boldsymbol n_i^*\cdot\boldsymbol n_f^*.
\]

The atom gains

\[
\Delta E_{\rm H}^*
=
h(\nu_i^*-\nu_f^*)\ge0.
\]

## Covariant outgoing scale

For a chosen future null direction \(q_f^\mu\), write

\[
k_f^\mu=\lambda q_f^\mu.
\]

The final mass shell yields

\[
\boxed{
\lambda
=
\frac{P_i\cdot k_i}
{P_i\cdot q_f+k_i\cdot q_f}.
}
\]

## Reverse event

Let

\[
P_f=P_i+k_i-k_f.
\]

The forward mass-shell identity implies

\[
\boxed{
P_f\cdot k_f=P_i\cdot k_i,
}
\]

\[
\boxed{
P_f\cdot k_i=P_i\cdot k_f.
}
\]

Therefore the reverse process, evaluated in the final atom rest frame,
has exactly the corresponding incoming and outgoing rest energies.
The implementation reconstructs the reverse outgoing direction by
Lorentz-transforming the original incoming photon into the final atom
rest frame.

## Same-event four-force

The photon transfer is

\[
\Delta p_\gamma^\mu=k_f^\mu-k_i^\mu.
\]

The atomic transfer is defined from the same event,

\[
\boxed{
\Delta P_{\rm H}^\mu=-\Delta p_\gamma^\mu.
}
\]

For an event-rate density \(\mathcal R\),

\[
Q_\gamma^\mu=\mathcal R\Delta p_\gamma^\mu,
\qquad
Q_{\rm H}^\mu=\mathcal R\Delta P_{\rm H}^\mu,
\]

so

\[
Q_\gamma^\mu+Q_{\rm H}^\mu=0
\]

without a separate recoil-heating prescription.

## Scope

This artifact closes exact elastic kinematics and reverse-event
reconstruction. It does not yet contain:

- the Kramers–Heisenberg event weight;
- thermal velocity integration;
- frequency-cell deposition;
- the v0.33 Kramers–Moyal small-recoil bridge;
- nonlinear anisotropic Bose stimulation.
