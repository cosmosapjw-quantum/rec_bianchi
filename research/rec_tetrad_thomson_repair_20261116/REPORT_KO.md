# REC Thomson의 Killing-ray/tetrad 오류와 사중극 적분 교정

2026-11-16 KST. 기준 REC #199 `c10e97ab3178c423cc7699684b33e1730d26437a`, WU #199 `6e04dcaf448269216330a75f1364b831c41e6c1e`.

실제 저장된 F08 S0의 640개 native gas/photon 단계, 81,920개 ray 입력에서 Thomson 충돌의 방향·입력 측도·각도 적분을 교정했다. 독립 검토 과정에서 원래 source의 q가 순간 tetrad 방향이 아니라 보존되는 Killing ray label임을 확인했다. 이를 물리 방향으로 변환하면 BI characteristic의 peak photon P/scattered-in은 5.67473766e-6이며, 기존 q-label 계산 3.80254057e-7과 유의하게 다르다. 기존 FAIL과 처음의 q-label l4 적분 교정 결과는 과거 진단으로 보존한다. 이 결과는 F08 S0의 이차 관측량 인터페이스를 개선하며, 중앙의 원래 z20→4 AXBI IGM 원소 abundance 노드를 완료시키지 않는다. 실제 source/clock가 다른 F05, F08, AXBI 사이의 상태 결합은 하지 않았다.

## 현재 조사와 지연 원인

- WU의 branch 이름 210개, REC의 219개를 API 마지막 cursor까지 열람했다. 최신 관련 PR 각 12개의 본문과 현재 선택한 PR의 head, 변경파일, 핵심 코드·결과를 읽었다. 모든 브랜치 내용 전체를 읽었다는 의미는 아니다. 중앙 통합 백업의 `branch_census.json`, `initial_evidence.json`, `repo_evidence.json`이 범위와 근거다; 이 REC PR은 그 전체 조사자료를 복제하지 않는다.
- WU #199 AGENTS에는 11월 1일 IGM 우선 routing이 추가되었으나, 아래에 오래된 R10→R18 및 PHYSxx 우선 지시가 연속으로 남아 있다. 현재 authoritative 지시와 history는 명시적으로 분리돼 있지만, 에이전트가 오래된 세부 목표로 재진입하기 쉬운 구조다. 실제 #191→199는 D/H source 진단을 반복하면서 WU34/49와 중앙28/88의 진전이 0이다. 각각 유용한 민감도 결과여도, named source/state가 없는 D 초기조건 선택을 반복하는 것은 원 목표를 닫지 못한다.
- REC #199는 단순 plot이 아니라 실제 광자 Stokes 자료를 만들었지만, l=2 정확도의 quadrature를 l=2 광자의 사중극 적분에도 충분하다고 사용했다. 사중극 적분에는 광자장과 kernel의 곱인 차수4 다항식이 들어가므로 실제 근거 있는 최소 교정이 있다.
- WU source-domain 검사는 F05 Hmean=2.2532997324143277e-17 s^-1, F08 Hmean=1e-14 s^-1, 비443.7935999435534를 이미 찾았다. source/clock 불일치의 추가 atlas를 만들 필요는 없다. root가 최신 REI #374의 AXBI mission을 확인해 각 provider 입력을 그 source에 결속한다.

## 물리 방향과 측도의 교정

original `science_scenario_v1.json` SHA c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1은 `ISOTROPIC_CONTINUUM_MEASURE; positive quadrature is a declared numerical approximation`를 명시한다. `source.birth_rule`은 q_i=a_i(t_birth) E_birth e_i가 상호작용 사이에서 보존된다고 정의한다. original `source_spectral_support.py`의 `original_checkpoint`는 q를 Killing rays라고 부르고, `original_redshift_g`와 `original_birth_weights`가 아래 변환을 실제 구현한다. 따라서 이것은 discrete physical beams의 가중치를 임의로 바꾸는 연산이 아니라 지정된 continuum angular integral의 수치 quadrature 교정이다.

A(t)=diag(exp(−H_i t)), g(q,t)=|Aq|이면 순간 comoving tetrad의 단위 방향은 n=Aq/g다. 단위 구면 사상의 Jacobian은 J=dΩ_n/dΩ_q=det(A)/g³이다. 실제 native source는 proper-isotropic 방출을 q label에 적재할 때 이미 J를 포함한다. 그러므로 local physical intensity sample은 I_n(q_i) ∝ N_i/J_i이며 J를 다시 곱하면 double counting이다. 원래 REC199의 q_i·q_j 및 q 기반 Stokes frame은 이 변환을 빠뜨렸다.

새 구현은 w0∝w4(q)J를 초기 physical solid-angle weight로 만들고, 순간 n grid에서 full Cartesian fourth-order moments를 정확하게 만족하는 최소 Euclidean 보정 w=w0+Mᵀ(MMᵀ)^−1(b−Mw0)를 계산한다. 여기서 M의 15행은 degree4 homogeneous monomial이며 b는 구면 평균이다. 현재 640개 stage에서 positivity와 moment identities를 실제 확인한다. 6차 독립 representation control도 별도로 계산한다. incoming collision mass는 m_i∝w_i N_i/J_i를 original total에 맞춰 정규화하고, Thomson phase와 Stokes basis는 n을 사용한다. 이로써 isotropic physical source N_i∝J_i의 Q/U와 elastic 변화는0이다. 처음 isotropic한 고정 q 질량을 shear 아래 자유전파시키면 Q_ab=−(2/5)t σ_ab+O((σt)^2)를 얻으며 독립 분석적 control로 검사했다.

최종 파일은 `thomson_tetrad.py`, `run_native_tetrad.py`, `results_tetrad/RESULT.json`, `test_tetrad.py`이다. 아래 q-grid degree4 유도는 필요한 기초 quadrature 교정이며 `results/`는 q-label diagnostic로만 읽는다.

## 기초 degree4 quadrature 유도

metric은 (-,+,+,+), 전자 comoving orthonormal tetrad, tilt=0, elastic nonrelativistic Thomson, incoming unpolarized field를 유지한다. `n_i`는 단위 H 핵당 ray photon number이며 `e_i`는 eV/H이다. 고정 original grid는 z=±1/8,±3/8,±5/8,±7/8의 8개 ring, 각 ring 16개 equally spaced azimuth다. 원래 source `q`의 byte SHA는 a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92.

정규화 intensity I(q)=I0+q^T S q (S는 symmetric trace-free)이면

Q_ab = [∫ I(q)(q_a q_b−δ_ab/3)dΩ]/∫I(q)dΩ = 2 S_ab/(15 I0).

마지막 등식은 구면의 2차·4차 등방 tensor 적분에서 나온다. 기존 weight w2=[1+(4/63)(z²−21/64)]/128은 0차·2차 moment만 정확하다. ∫I qq의 4차 moment에는 편향을 남기며, 실제 characteristic source에 나타난 약1.1648% 편차를 설명한다.

최소 Euclidean weight 보정이 1,z²,z⁴의 span 안에 있다고 두고 ∑w z^(0,2,4)=(1,1/3,1/5)를 정확히 푼다.

w4(z) = [68083/61440 − (64517/47520) z² + (2641/1485) z⁴]/128.

ring별 개별 ray weight는 ±7/8:35201/4055040, ±5/8:2989/450560, ±3/8:10057/1351680, ±1/8:34447/4055040이고 모두 양수다. 따라서 ∑w4=1, ∑w4 q_aq_b=δ_ab/3, ∑w4 q_aq_bq_cq_d=(δ_abδ_cd+δ_acδ_bd+δ_adδ_bc)/15. azimuth16점은 여기 쓰인 |m|≤4 Fourier 성분을 정확히 적분한다. 이로써 arbitrary l≤2 input의 사중극을 정확하게 재현한다. 이는 고차 harmonic이 있는 실제 source의 continuum 오차 보증과는 다른 명제다.

native 원본은 그대로 두고 충돌 계산용 양의 질량을 m_i = n_i w4_i (∑n)/(∑n w4)로 정의한다. 별도 energy channel에도 같은 선형 quadrature와 독립 total 보존 정규화를 적용한다. K_ij=(3/4) w4_i[1+(q_i·q_j)²]는 양수·column stochastic이고 K w4=w4다. original source가 지정한 p=−expm1(−c σ_T n_e Δt)를 사용하여 Δm=p(Km−m)으로 계산한다. 전체 photon 수와 elastic photon energy의 합 변화는0이다. 양의 coherency tensor가 주는 Stokes Q/U는 기존 convention Q=I_theta−I_phi를 유지한다. 새 교정은 gas thermal budget을 바꾸지 않는다.

작은 source 사중극에서 isotropic 1/3을 큰 총합 뒤에 빼면 소거 오차가 생기므로, `quadrupole`은 I/〈I〉−1을 먼저 구성한다. 정확한 2차 moment가 isotropic term을 해석적으로0으로 만든다는 사실을 이용한 동등한 계산이다.

## 실제 물리 tetrad 계산과 검사

최종 `results_tetrad/RESULT.json`은 원 scenario·q·photon bytes를 모두 lock한다. characteristic photon P/scattered-in peak=5.674737659418663e-6, fixed-hat=5.144026512301197e-6. characteristic source의 physical quadrupole l4–LS2 최대 상대차2.39988255e-8, l4–l6 4.07485810e-7; fixed-hat photon l4–LS2 최대1.31411730e-6, l4–l6 2.22566112e-5다. 최종 numerical values는 RESULT.json을 정본으로 사용한다. 9개 추가 physical tests가 scenario continuum 의미, source frame/Jacobian, zero-shear, analytic l2, physical isotropic source null, first-order shear, 보존·양성성, discrete-beam 오용 거부와 실제 source gate를 검증한다.

## 보존한 초기 q-label 교정의 계산과 검사

원본 photon-angle SHA `70ea9b3b4ffbe6b0b25c15a17182c3170b0f96fdb5d42209f90bff27d0bbe2a1`을 byte 검증해 사용했다. 새 native IVP 재실행은0이다. 실행은 `OPENBLAS_NUM_THREADS=1 python3 run_native_l4.py`, CPU 약4.04초. 결과 `results/RESULT.json`과 1,280개 channel/stage moment, 81,920개 새 Stokes row를 남겼다.

- fixed-hat tick142 photon quadrupole: l4–기존 LS l≤2 상대차0.001484642750872897, l4–l6 상대차0.025146173690120992. 모두 기존0.03 아래다. 후자는 cancellation-sensitive stage의 남은 finite-representation 민감도다.
- characteristic photon quadrupole의 l4–LS 최대 상대차1.1196092353242573e-6. peak P/scattered-in=3.8468324528223545e-7. fixed-hat peak=1.4707247285573026e-7. FLRW controls ≤1.84e-16.
- 전체 elastic ledger residual/(p total) 최대3.3243568083612015e-16. 양의 확률·phase·출력 질량·Stokes PSD를 검사했다.
- 정확 유리수 polar0/2/4 moment, 일반 STF l2 analytic reference, old degree2 negative control, collision 보존·양성성, isotropic Q/U=0, wrong grid/probability 입력 거부, 실제 source의 동일3% gate: 7개 tests PASS.
- 별도 저자 검토는 초기 q-label의 수치 검산을 통과시켰지만 물리 tetrad 해석은 거부했다. 최종 physical-frame 계산은 `reviews/REC_TETRAD_REVIEW.md`와 JSON에 PASS_SCOPED로 기록됐다. 독립 SVD moment solve, long-double centered tensors 및 3×3 coherency로 640단계·1,280 tensor·81,920 ray를 재검산했다. 최대 tensor 오차1.462e-16, IQU/(p total) 오차1.421e-17이며, physical tests도 독립적으로9/9 통과했다.

문헌 근거: Hu & White, Phys. Rev. D56,596 (1997), doi:10.1103/PhysRevD.56.596, https://arxiv.org/abs/astro-ph/9702170. Exa에서 원 arXiv/APS를 확인했으며 SciSpace 검색은 문헌 발견 경로다. phase/spin quadrupole dependence는 선행 물리이며, 이번 기여는 원래 REC source와 quadrature의 구체적 오류 수정 및 실제 source 결과다.

## 역할과 다음 구현

WU는 실제 선택된 원자·이온 reaction rate/Q/stoichiometry/provider validity를 소유한다. REI의 source-qualified species 초기조건·density·clock·spectrum이 없는 D/H·HD sensitivity atlas를 추가하지 않는다. WU 최신 source-domain 결과는 재사용하고 AXBI main run에서 기존 H/He provider의 정확한 함수·단위·thermal threshold를 owner가 요청할 때만 수정한다. H–Li registry 확장은 보존하되 미사용 모든 종을 중앙 선행조건으로 만들지 않는다.

REC는 selected source의 emissivity/absorption/recombination/electron and Thomson collision operator를 소유한다. 이번 결과의 다음 소비자는 source-matched photon transport이며 중앙 AXBI abundance 목적의 필수 선행조건으로 지정하지 않는다. 원래 abundance run을 막는 실제 opacity/energy row가 확인되면 그 row를 우선한다. 광자장 q128 밖의 harmonic·수렴·multiple scattering·polarization transport·CMB observer 예측은 별도 실제 요청에 묶는다.

REI는 scenario/IC/redshift/clock/geometry/provider 선택과 결합 abundance history, 그리고 최종 acceptance를 소유한다. BASS geometry와 REC collisions를 서로 다른 source에서 임의로 합치지 않는다. 증거상 원 목표를 바꾸는 추가 시나리오가 필요하면 명시적 물리 선택으로 남긴다.
