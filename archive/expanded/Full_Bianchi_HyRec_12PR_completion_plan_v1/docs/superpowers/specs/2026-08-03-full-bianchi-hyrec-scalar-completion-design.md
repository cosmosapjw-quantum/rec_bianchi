# Full Bianchi–HyRec Scalar Completion Design

## Goal

완료 기준 B를 만족하는 실행 가능한 scalar Full Bianchi–HyRec solver를 만든다. 대상은 spatially homogeneous background이며, 모든 11 Bianchi type, nonlinear large shear, finite tilt, tetrad 및 \(1+3\) formalism을 포함한다. 최종 scalar system은 HYREC급 유효 다준위 원자와 Ly\(\alpha\) frequency–angle transfer를 하나의 보존적·열역학적·stiff evolution system으로 결합해야 한다.

## Canonical architecture

시스템은 다섯 개의 독립 경계로 나눈다.

1. **Geometry characteristic**
   \[
   \{H,\sigma_{\alpha\beta},a_\alpha,n_{\alpha\beta},
   \Omega_\alpha,\beta_{\rm H}^\alpha,D_0\beta_{\rm H}^\alpha\}
   \mapsto
   \{\mathcal R_{\rm H},V_{\rm H}^\alpha,\mathcal A_{{\rm R/B},q}\}.
   \]

2. **Local atomic microphysics**
   hydrogen orthonormal frame에서 exact photon–atom events, true transitions, two-photon/Raman rates를 계산한다. Bianchi type 의존성은 이 계층에 들어오지 않는다.

3. **Radiation representation**
   frequency finite volume과 adaptive spherical harmonics를 결합한다. Collision은 local zonal harmonic kernel로, Bianchi Liouville transport는 harmonic-exact collocation으로 적용한다.

4. **Atomic/radiation coupling**
   HYREC native primitive rates
   \[
   \alpha_{2s},\alpha_{2p},\beta_{2s},\beta_{2p},
   R_{2p2s},A_{2s},A_{3s3d},A_{4s4d}
   \]
   를 유지한다. Sobolev escape, native \(A_{1s}\) diffusion, escape-compressed \(T_{vv}\), scalar \(Df^+_{\rm Ly\alpha}\) closure는 explicit Bianchi transfer로 공동 교체한다.

5. **Monolithic residual**
   \[
   Y=(F_I,F_{O_R},F_{O_B},x_{1s},x_{2s},x_{2p},
   x_e,T_m,\beta_{\rm H}^\alpha)
   \]
   를 하나의 implicit residual/Jacobian으로 진화시킨다.

## Global conventions

- Metric signature: \((-+++)\).
- Photon four-momentum:
  \[
  k^\mu=\left(\frac{h\nu}{c},\frac{h\nu}{c}\boldsymbol n\right).
  \]
- Massive atom four-momentum:
  \[
  P^\mu=(\Gamma Mc,\Gamma Mc\,\boldsymbol\beta),
  \qquad P^2=-M^2c^2.
  \]
- Radiation and matter sources:
  \[
  \nabla_\mu T_\gamma^{\mu\nu}=Q_\gamma^\nu,\qquad
  \nabla_\mu T_{\rm H}^{\mu\nu}=Q_{\rm H}^\nu,\qquad
  Q_\gamma^\nu+Q_{\rm H}^\nu=0.
  \]
- No posterior symmetrization or fitted normalization may hide a failed microphysical gate.
- Every stage produces a ledger, tests, SHA-256 manifest and supersession declaration.

## Completion definition

완료는 다음을 모두 뜻한다.

1. exact recoil·full scalar COM–KHW event kernel;
2. Bose/detailed-balance/entropy/four-force closure;
3. primitive HYREC coupling and FLRW parity;
4. representative class-A, class-B, exceptional runs;
5. all-11 automated sweep;
6. equation/proof/provenance census;
7. performance and release gates.

Fine structure, \(J\)-state interference, polarization and atomic alignment은 이번 12-PR scalar completion의 바깥이다.
