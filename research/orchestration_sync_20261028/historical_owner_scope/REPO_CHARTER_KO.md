# rec_bianchi 확장 연구 성격 — 2026-10-25

rec_bianchi는 원자·분자·동위원소의 반응망, 실제 스펙트럼의 흡수·방출·재처리, 인과적 복사 이력 및 물질의 열역학을 같은 사건 장부로 연결하는 저장소다. 기존 HyRec 수소 native 연산과 H/He/Li 유한 pilot의 범위를 보존하면서, 일곱 목표 동위원소의 모든 전하 상태와 선택한 분자 동위원소체로 연구 대상을 확장한다. 새 책임 범위는 기존 결과의 물리적 승인 범위를 바꾸지 않는다.

## 실제 출발점과 상태

확장 branch의 권장 base는 PR137의 `ea89c97abeb7a663a813f00e9aadddaf0b32a6a9`, branch `research/rec-history-pullback-20261025`다. 원 owner branch를 갱신하지 않고 별도 additive 경로에서 작업한다. PR137은 draft/open/unmerged다. PB01은 source-history endpoint/query pullback의 실제 전달20/20, 부모 REC-HISTORY는 PARTIAL이다. THERMO01·KS01·PB01의 완료 계산을 재실행하지 않는다.

확인한 원 21-state manifest는 PR119 `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7/research/rec_rei_hheli_sandbox_20261021/data/atomic_model.json` 및 `code/atomic_network.py`다.

| 목표 핵종 | 모든 현재 전하 상태 | 범위 해석 |
|---|---|---|
| H1, D, T | I–II, q=0,1 | 원 manifest는 elemental electronic equality 근사 |
| He3, He4 | I–III, q=0,1,2 | 동위원소별 질량·문턱·rate 검증 별도 |
| Li6, Li7 | I–IV, q=0,1,2,3 | 중성 Li inner-shell 최종 yield 아직 별도 입력 |
| neutron n | q=0 | 원 pilot 초기0; decay energy 미공급 |
| free electron | 전하중성으로 수 결정 | 열전자·비열전자 분포/온도는 별도 물리 변수 |

원 상태 `Y_i=n_i/n_b`, `A·Y=1`, `n_e=n_b q·Y`다. 원 UV는5–200eV의 prescribed isotropic number flux이며 각 bin의 단위는 m^-2 s^-1, flux=c×photon number density다. 기존 원자 fit의 더 넓은 Emax는 runtime source support의 자동 확장이 아니다. 원 pilot은 감쇠·재결합광 feedback·excited kinetics·Auger·secondary ionization·열에너지 closure를 포함하지 않았다. 후속 PR124의 제한된 Compton coupled 결과는 실제 진전으로 재사용한다.

## 확장 임무

1. **원자·분자 population registry와 반응 상태공간.** WU088_HH가 소유한 공통 species identity와 elementary reaction registry를 소비한다.  일곱 핵종의 모든 전하 상태를 유지하고 각 전하 내 필요한 bound/excited/metastable state를 source별로 열거한다. 핵종 질량과 electronic degeneracy를 구분한다. 음이온 및 분자 상태는 새 provider가 실제 선택됐을 때 registry에 추가한다.
2. **분자 동위원소체와 opacity.** 후보 family는 H2/HD/HT/D2/DT/T2 및 해당 분자이온, 선택한 triatomic H/D/T ion 조합, He3/He4–H/D/T, Li6/Li7–H/D/T다. 이는 기존 admitted molecule 목록이 아니라 새 source-intake 대상이다. 실제 bound state, charge, dissociation/ionization/attachment/photodetachment/recombination channel과 nuclear-spin 통계가 제공된 항목만 활성화한다. 분자 species의 A/Z 회계와 생성·파괴 광자의 스펙트럼을 같은 장부에 둔다.
3. **흡수·방출 전체 인접 채널.** bound–bound, bound–free/free–bound, free–free, two-photon/Raman, stimulated/spontaneous emission, scattering/Compton, line escape/reprocessing, molecular photodissociation/formation/dissociative recombination을 source별로 포함한다. WU의 level/transition/elementary branching payload와 bass_cr의 external nonthermal cascade을 소비한다. native Lyα와 detached provider의 동일 사건을 중복 합산하지 않는다.
4. **외부 광자와 바리온 source 소비.** CMB, UVB, stellar/AGN/Xray 및 선택한 external particle source의 실제 energy/angle/time/frame support를 읽어 photo/secondary ionization과 spectral/thermal RHS를 구성한다. 원 source 담당자가 spectrum을 공급한다. integrated rate/heating에서 spectrum을 역으로 추정하지 않는다. z20은 z<=15.1 UVB 범위 밖이다.
5. **thermal/history 실제 결합.** PB01의 fixed-chart pullback에 실제 DY/DQ/Dtheta·reference·geometry·clock·measure를 결속한다. H5 reference/endpoint/curvature uncertainty가 실제 공급되기 전 physical bound는 null이다. H6 trace와 H7 thermal-ODE coupling을 별도로 마감한다.
6. **nuclear adjacency.** neutron/T beta decay, 선택 시 Be7 prehistory/electron-capture·nuclear daughters 등은 nuclear source가 Q, daughter charge/level, recoil, beta/nu spectrum을 제공한 뒤 원자망으로 들어온다. 핵반응률을 전자/핵온도 계산에서 새로 추정하지 않는다. WU088_HH가 elementary nuclear/weak channel과 daughter identity/branching/Q를 소유하고, bass_cr가 외부 비열 daughter의 분포·stopping을 소유한다. REC는 daughter atomic/spectral/thermal consumer다.

## 식과 물리 소유권

반응 c의 proper event rate를 R_c [m^-3 s^-1], stoichiometry를 nu_ic로 두면 d n_i/dt + theta n_i = sum_c nu_ic R_c다. d/deta, eta=ln(a)를 쓰면 proper-time RHS를 H로 나눈다. 실제 volume/clock가 바뀌는 경우 그 변환도 미분한다.

분리된 species 온도라면 U_th=sum_s(3/2)n_s k_B T_s이며, 공통 T를 선택하면
C_V dT/dt = Q_th + W - (3/2)k_B T sum_s(dn_s/dt)_reaction,
C_V=(3/2)k_B sum_s n_s다. 이 식은 단원자 비상대론 병진 모형의 조건부 식이다. 회전·진동·내부 excitation이 활성인 분자의 C_V를 이 계수로 대체하지 않는다. 내부상태 의존 C_V와 binding U_int는 source와 partition/level model에 맞춰 별도 소유한다.

한 사건에서
Delta E_th+Delta E_nonthermal+Delta E_binding+Delta E_gamma+Delta E_nuclear+Delta E_nu+Delta E_external=0.
부호쌍은 한 canonical 사건 값에서 만들어 독립 합산의 ULP 차이로 동일 사건을 이중 소유하지 않는다. 전자 생성, heat-capacity 변화, ionization binding, spectral band boundary, nuclear mass, nonthermal birth/stopping은 각각 다른 항이다. 흡수 에너지를 그대로 heating으로 두지 않는다.

복사 band의 에너지는 volume emissivity/opacity와 양 끝 boundary flux를 모두 포함한다. 같은 photon이 native→COM 또는 band→band 경계를 지날 때 source emission으로 다시 세지 않는다. matter/radiation STF는 각각 저장하고 signed sum을 취한 뒤 관측 norm을 만든다.

## 저장소 분업

| 연구 산출물 | 최적 책임 저장소 | REC의 역할 |
|---|---|---|
| species/nucleus/isotope identity와 elementary atomic·molecular·nuclear channel/branching/energy | WU088_HH | units, state/threshold, photon event와 species map 소비 |
| 외부 nonthermal photon/electron/baryon distributions, cascades, stopping, secondary production | bass_cr | 실제 source packet과 spectral/thermal deposition 소비 |
| differential finite-mass collision, thermalization, species energy/momentum/STF 및 heat-capacity closure | BASS_HE | 실제 Q_s/nu_s/uncertainty를 열·반응 RHS로 연결 |
| radiation history, spectral transfer, atomic/molecular thermodynamics | rec_bianchi | 직접 소유 |
| geometry/background, covariant coupling, transport stock, source transaction | bass | REC event를 공급; 같은 ledger 중복 생성 금지 |
| cosmological scenario, source/absorber/environment assembly, coupled conservation/observables, cross-repo scheduling | rei_bianchi | bass geometry와 선택한 matter/radiation 소스를 scenario에 결속 |
| implicit solve/restart/error control | Vigil | physical operator contract 공급, 솔버 재설계 독립 |

## 연구 승인과 재개

각 새 species/channel에는 immutable source identity, support, units, count/label, frame/clock/volume, daughter state, energy owner, uncertainty와 실제 consumer ACK가 필요하다. 보존식 roundoff PASS는 provider/model uncertainty를 인증하지 않는다. source가 없으면 해당 물리 채널만 INPUT_DEPENDENT로 두고 독립적인 source intake·유도는 진행한다.

원 REC-C3 최적화, H5/H6/H7 owner와 reserve를 유지한다. 새 실행은 기존 예산을 초기화하지 않고 별도 물리 입력/가설/오차배분/중단조건을 고정한 뒤 시작한다. AGENTS root는 현재 REC137에서404였으며 중앙 실제 AGENTS의 tiered-scientific rule을 적용한다. 요청 모델은 Astra-tier, 실제 runtime 모델은 NOT_OBSERVABLE이다. science, 실행,CI,전달 상태를 따로 기록한다.


## 공통 소유권 정합

이 prospective 문서의 lead는 ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md를 따른다. WU species identity/elementary branching, REC level populations/spectra/history, HE differential collision/thermalization, CR external nonthermal distributions/stopping, BASS geometry/background/covariant coupling, REI selected scenario/assembly다. REC의 network registry는 WU identity의 consumer projection이며 별도 경쟁 identity owner가 아니다. LAMDA/CDMS/JPL/ExoMol source adapters와 level-resolved spectroscopy는 REC가 lead한다.

현재의 일곱 동위원소 목록은 WU의 확장 가능한 target catalog에서 실제 확인한 초기 view다. 미래 scope의 상한이나 모든 intended target의 완전 열거가 아니다. 새 (Z,A,isomer), 분자 isotope composition, signed charge, internal state, collider, electron-pool ID는 실제 source로 확장하고 missing data는 coverage gap으로 남긴다.
