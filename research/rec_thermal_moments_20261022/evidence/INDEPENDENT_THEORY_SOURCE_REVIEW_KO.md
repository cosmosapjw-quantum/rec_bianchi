# REC PR119 후속 열적 source 독립 검토

검토일: 2026-10-22. 기준: `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`, `research/rec_rei_hheli_sandbox_20261021/code/atomic_network.py`, `THEORY_KO.md` R6. 이 문서는 새 source 도입과 수식 검토이다. 기존 126 case ODE를 재실행하지 않았다.

## 1. 이번에 추가할 수 있는 계산

기존 코드에는 absorbed/primary/core powers와 prescribed-T가 요구하는 `Q_net`, `bath_minus_escape`가 이미 있다. 새 기여는 (i) 총 재결합 rate fit의 Maxwellian energy moment를 실제 계산, (ii) 독립 원전 Mao–Kaastra–Badnell2017의 energy-loss factor와 비교, (iii) Li 단일 1s vacancy의 빠른 radiative relaxation을 명시한 energy owner, (iv) 같은 number source를 유지하는 동적 T 실험이다.

## 2. Maxwellian rate와 kinetic loss

비상대론적 Maxwellian, 고정된 초기 이온 내부상태, 온도와 무관한 cross section 또는 effective resonance kernel, 적분·미분 교환 가능성을 전제로 한다. 상대운동 reduced mass를 μ라 하면

`alpha(T)=sqrt(8/(pi*mu))*(kB*T)^(-3/2) * integral_0^inf E*sigma(E)*exp[-E/(kB*T)] dE`.

`L(T)=sqrt(8/(pi*mu))*(kB*T)^(-3/2) * integral_0^inf E^2*sigma(E)*exp[-E/(kB*T)] dE`

이므로 `L=kB*T*((3/2)*alpha+T*dalpha/dT)`. alpha 단위는 m^3/s, L은 J m^3/s이다. 이 등식은 참 cross section에서 계산한 alpha에 대한 직접 유도이다. 실제 코드의 analytic fit을 대입한 값은 **fit-implied moment**이다. alpha의 pointwise fit 정확도만으로 alpha의 derivative 정확도를 인증하지 않는다. T에 의존하는 metastable weight, density suppression, cutoff, stimulated channel을 암묵적으로 섞으면 추가 derivative 항이 필요하다.

VF/Badnell RR식에서 `u=sqrt(T/T0)`, `v=sqrt(T/T1)`, `b=B+C exp(-T2/T)`, `d=b_lnT=C*(T2/T)*exp(-T2/T)`라 두면

`dln(alpha)/dln(T) = -1/2 -(1-b)*u/[2(1+u)] -(1+b)*v/[2(1+v)] + d*[ln(1+u)-ln(1+v)]`.

따라서 `f=L/(kB*T*alpha)=3/2+dln(alpha)/dln(T)`를 log1p로 안정적으로 계산한다.

DR fit `alpha=T^(-3/2) sum c_i exp(-E_i/T)`에서 E_i가 K 단위이면

`L=kB*T^(-3/2) sum c_i*E_i*exp(-E_i/T)`.

기존 cm^3/s→m^3/s 계수 1e-6을 동일하게 적용한다. 음의 c_i는 개별 확률/양의 resonance로 읽지 않는다. fit 전체와 moment의 양성성을 실제 사용 T domain에서 각각 검사한다. 원시 DR가 underflow 0이면 L 역시 직접 가중합으로 계산하고 `L/alpha`의 0/0을 피한다.

Wolfram 현재-turn 독립 대수 검산: Maxwellian kernel와 단일 DR항에 대한 두 차이는 `{0,0}`. 초기 도구 입력 두 건의 `%`/괄호 오류 뒤 명시적 expression으로 수정해 얻은 결과다. 실패 입력을 과학적 반례로 세지 않는다.

## 3. 독립 원전과 실제 data

Mao, Kaastra & Badnell, *The electron energy loss rate due to radiative recombination*, A&A 599 A10 (2017), DOI `10.1051/0004-6361/201629708`, arXiv `1612.01017`.

- Primary: https://arxiv.org/abs/1612.01017
- Full text: https://arxiv.org/html/1612.01017 (Exa full-text 조회 성공; 일반 web open 실패와 구분)
- Publisher: https://www.aanda.org/articles/aa/pdf/2017/03/aa29708-16.pdf
- Data: https://cdsarc.cds.unistra.fr/ftp/J/A+A/599/A10/
- Metadata: https://cdsarc.cds.unistra.fr/viz-bin/ReadMe/J/A+A/599/A10?format=html&tex=true

논문 Eqs(1)–(6)는 RR number coefficient와 electron kinetic loss를 별도 적분하여 `L=kB*T*alpha*f`로 정의한다. Eq(7)의 f fit에는 T를 eV 단위로 넣는다. 식의 log는 **자연로그**다. Li I의 c0 != 0 행을 원 `calc.dat`와 대조하면 자연로그 최대1.874% 오차로 해당 `pars.dat`의 1.9%에 들어가며, log10은22.829% 차이가 난다.

`f(T_eV)=a0*T_eV^(-b0-c0*ln(T_eV))*(1+a2*T_eV^(-b2))/(1+a1*T_eV^(-b1))`.

행은 **재결합된 이온**의 전자 수 s와 원자번호 Z를 쓴다. 기존 코드의 recombining charge q에 대한 정확한 대응은 `s=Z-q+1`. 표 grid는 `q^2*[10,20,50,100,200,500,...,1e7] K`. ReadMe가 c를 "recombined charge"라고 부르지만 중성종에서 그 값을 문자대로0으로 쓰면 불가능하며 q=Z-s+1로 모든 6행의 공개 fit 최대편차를 재현했다. 이 source 설명 교정은 근거와 함께 유지해야 한다.

실제 내려받은 bytes:

| 파일 | byte | SHA256 |
|---|---:|---|
| mao_readme.txt | 6491 | 37944450bffce2a375a2491cef8c97ab8d0962f082832c9393015194012b6ed4 |
| calc.dat | 30600 | bf7ad20e10ff7045fc83b4c4c4148132c291f315213c5fc7b00ae820c76aa58a |
| pars.dat | 22185 | a3c97fdf8101da6d33cc838f7fd4e142bcf3740c37b48d89e76c47ae91575d12 |

전체6행 mapping/params/19점 oracle/비교는 `RR_MAO_COMPARISON.json`에 있다. 100–12000K의1001점에서 derivative-fit f와 Mao f의 최대 상대 차이는 HII0.370%, HeII2.265%, HeIII0.593%, LiII3.468%, LiIII2.070%, LiIV1.264%. 100–1e6K에서는 HeII12.86%, LiII14.31%, LiIII5.26%까지 커진다. 이 값은 두 source/closure의 차이이며, 참 물리 오차나 전역 ODE 오차 인증이 아니다.

Mao f를 기존 VF/Badnell alpha와 곱할 경우 원 number rate를 보존하는 **hybrid source closure**라고 기록한다. Mao 원 계산의 alpha 자체를 대신 사용했다고 하지 않는다. derivative-fit branch와 Mao-factor branch를 함께 비교하면 원 number source를 고정한 thermal modeling sensitivity를 분리할 수 있다.

## 4. Li I 단일 1s vacancy의 의미

기존 fit의 1s ionization edge64.39eV, 중성→LiII threshold5.392eV를 사용하면 residual excitation은58.998eV이다. 다음 LiII→LiIII threshold75.64eV보다 낮다. 따라서 **그 단일 잔류1s2s 상태의 자발적 한 단계 Auger ionization**에는 필요한 에너지가 없다. 이것은 retained single-vacancy channel의 유도이며 모든 lithium photoabsorption이나 direct double ionization을 배제하는 명제가 아니다. 외부 photon이81.032eV 이상이면 ground LiIII를 만드는 correlated double/shake-off 채널은 에너지상 가능하며 별도 source cross section이 필요하다.

Saghiri et al., *Dielectronic Recombination of Ground-State and Metastable Li+ Ions*, arXiv:physics/9907030 (1999), https://arxiv.org/pdf/physics/9907030 . 원문 abstract 및 pp1–2는 Li+(1s2s 3S) 자연 radiative lifetime52.2±5.0s를 보고하고 singlet1s2s1S lifetime~0.5ms, triplet~50s를 설명한다. 따라서 retained process에서 H, photo/RR/DR rates와 이 시간을 대조해 short-lived level을 제거할 근거를 만들 수 있다. 높은 밀도 quenching이나 광자 재흡수까지 이 근거가 해결하지는 않는다.

본 cosmological pilot의 optically thin cascade 가정 아래 `Q_core`를 escaping radiation으로 할당하고 `Q_primary`만 즉시 kinetic bath에 넣는 closure가 일관적이다. local thermalization, escaping photons, 미해결 correlated channels의 지위를 명시한다. 임의의 "Auger double yield"를58.998eV core에 부여해 electron source를 늘리는 것은 이 retained state의 energy ledger와 충돌한다.

## 5. 동적 온도와 총 에너지 owner

`nbdot=-3H nb`, `Y_i=n_i/nb`, `f=sum_i Y_i+q·Y`, `ng=nb*f`, `u_th=3kB*T*ng/2`, `p=ng*kB*T`이다. nuclear reactions가 없는 현재 species 집합에서는 `sum_i dotY_i=0`, 따라서 `fdot=q·dotY`. 일반 형식은 `fdot=(1+q)·dotY`다.

`Tdot=-2H*T-T*fdot/f+2 Q_kin/(3 kB nb f)`.

photo/RR/DR만 보유하는 새 closure에서는

`Q_kin=Q_primary-ne*nb*sum_i Y_i*(L_RR,i+L_DR,i)`.

`u_ion=nb I·Y`, `dotu_ion+3H u_ion=nb I·dotY`.

RR/DR escape는 각 downward jump의 ionic energy와 제거된 kinetic energy를 모두 가져간다. `Q_escape=Q_core+ne*nb*sum_i Y_i*[chi_(i-1)*(alpha_RR,i+alpha_DR,i)+L_RR,i+L_DR,i]`라 두면

`Q_abs-Q_escape=Q_kin+nb I·dotY`.

이 관계를 RHS 수준과 저장 output에서 검사하면 ionization energy/heat의 이중계산을 잡을 수 있다. Q_kin의 recombination cooling과 온도식의 particle-number 항은 물리적 역할이 다르다. 저에너지 전자를 선택적으로 제거하면 kinetic energy가 감소하면서도 남은 입자의 T는 증가할 수 있다.

현재 바리온 pi_b=0이므로 shear work term은0이고 θ=3H를 쓴다. 동적 CMB의 기존 Thomson 항은 recoil-free이므로 그 항을 Compton heating으로 재해석하지 않는다. Compton/CI/excitation/CX/free-free와 secondary deposition을 추가하면 각각 새 energy owner/source가 필요하다. 이 단계에서는 photo/RR/DR conditional thermal model의 결과로 보고한다.

## 6. 권장 claim와 검증

- Maxwellian identity: derived, CAS checked.
- VF/Badnell temperature-fit moment: implementation 및 finite-T 검증 대상. 원자의 정확한 cooling certified라고 쓰지 않는다.
- Mao rows: primary source bytes acquired, six mappings/formula independently checked.
- Li single-vacancy fast radiative relaxation: energy inequality derived, metastable lifetime literature-supported; optically thin escape는 모델 가정.
- 다음 실행: 저장 z≈8 endpoint에서 새63state logT branch를 시작; 기존126 재적분0. 최소 하나의 Mao-factor alternative가 있다면 closure sensitivity를 실제로 분리.
- mandatory checks: atomic number/charge ledger, T derivative column, analytic Jacobian directional check, total-energy identity, logT positivity/domain guard, matching initial saved state, physical limits Q=0 & fdot=0에서 T∝a^-2, source alternative versus solver tolerance distinction.
