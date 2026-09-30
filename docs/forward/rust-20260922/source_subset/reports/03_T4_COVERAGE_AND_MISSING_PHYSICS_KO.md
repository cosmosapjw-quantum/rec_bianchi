# T4 source coverage and missing-physics firewall

## 1. P bound-free numerical coverage

Jacobs source family에서 WU28은 q=0.15...1.0, WU30은 q=1.0,1.2,1.4를 사용한다. 같은 P source family 안에서는 piecewise-linear representative를 q in [0.15,1.4]로 정의할 수 있다.

`E=chi_P+q Ry`이므로 대략 5.4102...22.4173 eV가 represented range이다. 이 범위 밖은 `UNKNOWN`, physical zero가 아니다.

Alignment-inclusive P map에는 sigma_s와 sigma_d가 모두 필요하다. Total sigma만 있는 구간은 scalar unpolarized opacity에는 쓸 수 있어도 full W_P matrix source에는 promotion하지 않는다.

Electron-angle-resolved source에는 relative s/d phase의 imaginary-sign 정보가 추가로 필요하다. 현재 full-angle inclusive map은 그 phase를 제거하지만 anisotropic electron weighting에서는 다시 필요하다.

## 2. S bound-free numerical coverage

WU27 low branch는 Bhatia-derived q≈0.01...1, WU30 high branch는 Jacobs q=1...1.4이다. 두 atomic calculations는 q=1에서 약 -0.713755% 차이가 있으며 동일 model family가 아니다.

따라서 T4는 이 둘을 자동 smooth splice하지 않는다.

- `S_BF_LOW_BHATIA`: finite low-q source branch.
- `S_BF_HIGH_JACOBS`: q in [1,1.4] source branch.
- `S_BF_GLOBAL_STITCH`: `UNRESOLVED`.

E_partner≈20.0135 eV와 584≈21.2180 eV의 hard-photon tests에는 WU30 Jacobs high branch가 직접 적용 가능하다.

## 3. two-photon coverage

Canonical numerical central-band representative는 WU31-A1의 `D86_TABLE_V_LENGTH_LINEAR_B`이다.

- material-frame y domain `[1/40,39/40]`.
- printed length-gauge half-grid를 reflect하고 band 내부에서만 linear interpolation.
- vacuum band event loss `Lambda_B=50.9259 s^-1`, 같은 w에서 계산.
- D86 velocity rows는 gauge comparison이며 평균해 invented uncertainty로 만들지 않는다.
- `51.020`, `50.943`, `50.94 s^-1`를 resolved source 위에 별도 decay로 더하지 않는다.
- y<1/40 또는 y>39/40는 `UNKNOWN`.

WU32 이후 finite-ECG C0 calculations는 endpoint/atomic-convergence research branch이다. G10–G13과 T3 claim chain의 수용 없이 canonical collision spectrum을 교체하지 않는다.

## 4. sharp lines

584와 IR은 현재 heavy-atom sharp-line distribution으로 연결돼 있다. 다음 항목은 아직 별도 물리 closure가 필요하다.

- Doppler/recoil broadening.
- natural/pressure width.
- partial redistribution.
- finite-bin line trace prescription.
- overlapping resonance/coherent Raman treatment.

Tilt 자체는 새 line profile physics가 아니다. Material-frame sharp source를 existing boost로 normal frame에 옮기면 direction-dependent Doppler support가 자동으로 나타난다.

## 5. missing level/channel physics

이번 selected singlet subsystem이 포함하지 않는 항목:

- full He I multilevel network.
- triplet system and intercombination channels not already present elsewhere.
- all bound-free continuum energies.
- ground-state continuum where not already represented by another source module.
- HeIII and complete H/He charge network.
- collisional excitation/de-excitation/ionization beyond the selected radiative lanes.
- coherent inter-level optical density matrix.
- full Raman/two-photon resonance matching.
- finite-nuclear-mass/relativistic/radiative atomic correction to every kernel.

이 항목이 없다는 사실을 current selected source의 FAIL로 바꾸지 않는다. 전체 recombination closure claim에 대해서는 `MISSING_PHYSICS`이다.

## 6. electron/matter closure gaps

Bound-free inverse baseline assumes atom/material-frame isotropic Maxwell electrons. Species drift `u_e != u_He`는 미해결이다.

`H_kin`을 즉시 common material temperature source로 넣으려면 fast electron thermalization and common-temperature closure가 필요하다. 그렇지 않으면 electron kinetic reservoir를 따로 evolve해야 한다.

Photon이 전달한 total momentum은 four-force ledger로 닫히지만 electron, ion, neutral-He 사이 partition에는 Coulomb/momentum-exchange closure가 필요하다.

## 7. cosmological and numerical gaps

T4는 다음을 실행하지 않았다.

- recombination history x_e(z).
- Bianchi-family trajectory.
- LoS/CMB observable.
- production integrator positivity/convergence.
- S4/S5 full suite.
- G10/G11/G12/G13 numerical certification.

따라서 최종 상태는 `SOURCE_TO_TRANSPORT_THEORY_READY`, project-global physics complete가 아니다.
