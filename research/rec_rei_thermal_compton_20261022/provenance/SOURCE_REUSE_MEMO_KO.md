# THERM02 R2/R3 원전·재사용 검토

검토일: 2026-10-22 UTC. 담당 범위: 문헌·입력 identity 확인, 물리식과 현재 변수의 대응. 새 ODE, 물리 테스트, 과거 suite 재실행은 0회이다. 대상은 `research/rec_rei_thermal_compton_20261022`의 조건부 열·이온 모델이며 전체 핵반응망 또는 방사장 backreaction 완결을 주장하지 않는다.

## 1. 채택 가능한 결과

PR121의 Mao2017 RR 전자 운동에너지 냉각 인자와 PR122의 Thomson–Compton 식은 compact34 모델에 재사용할 수 있다. RR number rate는 원래 네트워크 것을 유지하므로 냉각은 **Mao-factor hybrid**이다. Compton의 실제 방사장 에너지 monopole에 비례하는 hot-electron 항과 별도로 가정한 Planck bath의 완전한 leading-order 교환항은 서로 구별해야 한다. Li 50–60 eV 공명 및 60–200 eV의 완전한 final-yield 입력은 이번 제한된 검색에서도 확보되지 않았다.

공통 상태는 Physical/REC U5 HOLD, global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false를 유지한다. 이 source 검토는 해당 상태를 승격하지 않는다.

## 2. Mao2017: 식, 행, 단위

원전 [S1]의 Eq. (7), Table 2와 CDS ReadMe [S2]를 읽었다. 전자는 Maxwellian, 재결합 전 이온은 바닥준위, 대상은 재결합 후 H-like–Ne-like 계열과 Z≤30이다. Case A는 바닥준위 포획을 포함한다. 원문의 β=L/(kBT)는 rate 단위이며, 현재 코드의 에너지 순간은 L 자체, 단위 J m³ s⁻¹이다.

\[
t=\frac{k_BT}{1\,\mathrm{eV}},\qquad
f(t)=a_0 e^{-b_0\ln t-c_0(\ln t)^2}
\frac{1+a_2t^{-b_2}}{1+a_1t^{-b_1}},\qquad
L_{\rm hybrid}=k_BT\,\alpha_{\rm donor}\,f.
\]

원전의 `log` 표기를 자연로그로 읽는 근거와 114개 원표 값의 대응은 이미 완료된 PR121 source 검증을 재사용한다. 여기서는 그 검증을 다시 실행하지 않았다. 원표 `s`는 최종 bound-electron 수이며 초기 전하는 `q_initial=Z−s+1`이다. CDS 온도 설명을 중성 최종 전하에 문자 그대로 적용하면 0 K 격자가 되므로, PR121에서 원표와 대조된 초기 q² 온도 격자 해석을 유지한다.

| 재결합 | Z | 초기 q | 최종 s | a0 | b0 | c0 | a1 | b1 | a2 | b2 | 원표 최대 fit 편차 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H II→H I | 1 | 1 | 1 | 8.655 | 0.5432 | 0 | 10.18 | 0.5342 | 0 | 0 | 1.2 |
| He II→He I | 2 | 1 | 2 | 2.354 | 0.3367 | 0 | 62.8 | 0.8875 | 21.33 | 0.5675 | 1.5 |
| He III→He II | 2 | 2 | 1 | 17.82 | 0.5398 | 0 | 20.61 | 0.5318 | 0 | 0 | 0.9 |
| Li II→Li I | 3 | 1 | 3 | 4.166 | 0.3110 | 0.007567 | 65.17 | 0.9634 | 10.19 | 0.7434 | 1.9 |
| Li III→Li II | 3 | 2 | 2 | 65.58 | 0.6439 | 0 | 78.78 | 0.6317 | 0 | 0 | 1.3 |
| Li IV→Li III | 3 | 3 | 1 | 27.33 | 0.5385 | 0 | 31.43 | 0.5309 | 0 | 0 | 1.1 |

PR121 공통 실행 지지집합 100–10⁶ K를 확대하지 않는다. 위 편차는 f의 원표 fit 잔차이며 hybrid 전체의 물리 오차 한계가 아니다. DR에는 Mao RR 인자를 곱하지 않는다. 광학적으로 얇은 case-A prompt escape, 동일 전자온도와 원래 isotope-electronic 대응은 추가 전제이다.

코드에 필요한 도함수는 해석식으로 계산 가능하다.

\[
\frac{d\ln f}{d\ln T}=-b_0-2c_0\ln t
-\frac{b_2a_2t^{-b_2}}{1+a_2t^{-b_2}}
+\frac{b_1a_1t^{-b_1}}{1+a_1t^{-b_1}}.
\]

6개 전자구조 행을 준비하고 같은 (Z,q)의 isotope 성분으로 사상할 수 있다. 이는 현재 소스 가정 아래의 계산 단순화이며 새로운 상태별 원자자료를 생성하지 않는다.

## 3. Compton: 실제 monopole와 Planck reference의 구별

Sazonov & Sunyaev [S3] PDF를 직접 읽고 Eq. (6), (18), (25)를 확인했다. 등방 Maxwellian 전자, 전자 bulk tilt 없음, kBT와 광자 에너지가 모두 mec²보다 충분히 작은 극한에서

\[
\langle\Delta E_\gamma\rangle=
\frac{E_\gamma(4k_BT-E_\gamma)}{m_ec^2}
\]

가 leading term이다. Eq. (25)의 이 에너지 순간에 작은 Eγ/kBT 비는 별도로 요구되지 않는다. Eq. (18)의 출사각 적분으로 열 Doppler 항은 입사 광자 에너지의 monopole만 필요하다는 대응을 얻는다.

가스 가열을 양으로 두면 실제 저장된 방사장에 대해

\[
Q_{\rm hot}=-\frac{4\sigma_Tc\,n_e k_BT}{m_ec^2}U_{\gamma,\mathrm{actual}},\qquad
U_{\gamma,\mathrm{actual}}=a_R T_0^4 E_{\gamma,0}/a^4.
\]

위 a_R T_0^4 정규화는 원전의 Planck 기준 표기이다. THERM02 actual branch는 donor에 고정된 rho_crit,J × Omega_gamma를 직접 사용하며 이를 새 a_R로 덮어쓰지 않는다. Eγ,0는 full raw index 4이며 일반적으로 1이 아니다. photon source만 사용하고 neutrino 에너지를 섞지 않는다. 반면 독립적으로 가정한 Planck bath에는

\[
T_{\rm ref}=T_0/a,\quad U_{\rm ref}=a_RT_{\rm ref}^4,\quad
Q_{\rm Planck}=\frac{4\sigma_Tc\,n_e k_BU_{\rm ref}}{m_ec^2}(T_{\rm ref}-T).
\]

두 식은 모델 선택의 대안이다. 실제 Uγ와 Tref를 섞어 완전한 anisotropic 교환식으로 선언하거나 두 항을 중복 합산하지 않는다. Eq. (6)의 recoil와 induced 부분은 주파수별 occupation을 요구하며, 기존 각도별 에너지·수 monopole/multipole만으로는 일반적인 스펙트럼을 정하지 못한다. Planck 식의 T=Tref 평형은 recoil+induced를 포함한 occupation 적분에서 나온다.

가스 RHS에 source를 결합하고 반대 부호의 bath debit을 passive ledger에 적분하는 것은 test-fluid 에너지 추적이다. photon hierarchy와 Einstein 쪽의 실제 반작용을 푼 상태로 표시하지 않는다. 원래 PR121/122의 UV 5–200 eV 정규화·적분값을 THERM01의 5–60 eV source에 복사하지 않는다.

## 4. Li final yield의 남은 정확한 입력

최신 확인 논문 [S4]는 PRA 113, 033105, **2026-03-09 출판**이다. Exa metadata의 2026-02-17은 PDF의 acceptance 날짜와 일치하므로 출판일로 사용하지 않는다. 논문은 Li core-excited 구조와 이중 광이온화를 다루며 Data Availability에서는 출판 시 수치자료가 공개되어 있지 않고 저자 요청 방식임을 밝힌다. 저자 공개 출판목록 [S5]까지 확인한 제한된 검색에서 새 numerical final-yield 파일은 발견하지 못했다. 저자에게 연락하지 않았다.

5–60 eV smoothed continuum는 실제 50–60 eV Li 공명을 포함하지 않는다. 60 eV cutoff로 64.39 eV의 기존 직접 1s-hole edge가 닫힌다는 사실은 그 공명들을 배제하는 근거가 아니다. 60–200 eV에는 별도 단일·이중 최종 전하와 state/energy branching 입력이 필요하다. 81.032 eV 이중 제거 문턱과 특정 1s-hole 잔여 에너지 예산의 기존 검토는 유지한다.

남은 입력은 에너지별 최종 charge/state 단면적, 적분 전자 운동에너지, 잔여 준위 에너지와 탈출 광자 에너지, 일관된 threshold/normalization/uncertainty이다. 공명 간 간섭이 있는 Fano 분해항을 독립적인 양의 branch 확률로 취급하지 않는다. 현재 상태는 **MISSING_EXACT_INPUT, PARTIAL_SCOPE**이며, 완전한 Li ionic-yield closure 실패를 보편적 불가능성 정리로 해석하지 않는다.

## 5. 실제 재사용 파일과 검토 범위

`vendor_pr121/` 아래 6개 파일은 REC PR121 HEAD `892aad5c3e9fb0b2abd021154b62a42c39277125`의 동일 경로에서 얻었다. 모든 SHA256과 byte 수는 동봉 JSON에 기록했다. calc.dat, pars.dat, selected.json은 기존 source lock의 값과 정확히 일치한다. 코드의 21종 순서·원래 α와 DR 처리·에너지 owner를 유지하고 새 compact34 adapter에 필요한 사상만 검토한다.

- `code/thermal_sources.py`
- `code/recombination_moments.py`
- `data/mao2017_calc.dat`
- `data/mao2017_pars.dat`
- `data/mao2017_selected.json`
- `provenance/MAO_SOURCE_LOCK.json`

PR122 HEAD `04c0b10c1f1ec38d57c751369c553b638979e453`의 THEORY_KO.md와 provenance/SOURCES.json도 직접 읽었다. 해당 8개·109-node restart cohort의 postprocessed Compton budget은 그대로 재사용하는 과거 결과이며 새 THERM02 cohort나 THERM01 8개와 합산하지 않는다.

도구 사용은 Exa 검색 2회(각 5개 결과 요청), SciSpace 검색 1회(10개 결과), Exa 원문 fetch, GitHub의 pinned 파일 fetch, 원문 PDF 읽기였다. 핵심 논문 3편(Mao, Sazonov–Sunyaev, Li2026), 보조 primary 문서 4종(CDS ReadMe·2개 numerical table·저자 목록)을 검토했다. CDS numerical bytes는 live server에서 새로 받은 자료가 아니라 pinned PR121 byte snapshot이다. Exa pars.dat fetch는 SOURCE_NOT_AVAILABLE였고 A&A 직접 PDF는 HTTP 403이었다. 공개 arXiv 저자본으로 Eq. (7)과 Table 2를 확인했다. arXiv PDF는 v1(2016-12-03)로 표시되며 자동 조판 header의 2021-10-30은 새 연구 출판일로 사용하지 않는다.

R2/R3 결과: 선택한 Mao hybrid와 Thomson source에는 소스·변수 대응이 확보되었다. Li complete final yield 의존성은 열려 있다. 부모 작업의 새 adapter 검증과 유한 coupled campaign은 이 메모 이후 별도 실행 책임이며 여기서는 실행하지 않았다.

## 원전

- [S1] Mao, Kaastra & Badnell (2017), A&A 599 A10, DOI 10.1051/0004-6361/201629708. https://www.aanda.org/articles/aa/full_html/2017/03/aa29708-16/aa29708-16.html ; 저자본 https://arxiv.org/abs/1612.01017
- [S2] CDS J/A+A/599/A10. https://cdsarc.cds.unistra.fr/ftp/J/A+A/599/A10/ReadMe ; calc.dat 및 pars.dat는 같은 디렉터리.
- [S3] Sazonov & Sunyaev (2000), ApJ 543, 28–55, DOI 10.1086/317078. https://arxiv.org/pdf/astro-ph/9910280v3
- [S4] Müller, Kheifets, Bray & Fursa (2026), PRA 113, 033105, DOI 10.1103/l4xt-3sxy. https://journals.aps.org/pra/pdf/10.1103/l4xt-3sxy
- [S5] A. S. Kheifets 공개 출판목록. https://people.physics.anu.edu.au/~ask107/publications.html

원문 전체 PDF와 검색 receipt는 이 작업의 임시 검토 자료이다. 공개 연구 unit에는 이 메모·provenance JSON·필요한 6개 재사용 파일과 원 저자 attribution을 채택하고 원문 전체 추출본은 포함하지 않는다.
