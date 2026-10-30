# REC-HD: CMB 복사-충돌 정상상태와 실측 선중심 적색편이 관측량

**범위:** `REC_HD_CMB_SPECTRAL_BALANCE_20261030` (2026-10-30 KST). 현재 증거 기반의 실측 HD line 중심과 2021 LAMDA 복사·충돌률을 결합하되 소스 자격을 엄격하게 분리한 탐색적 물리 연구. **부모:** `cosmosapjw-quantum/rec_bianchi` Draft PR #166 HEAD `152663436e9a3ee9f88414e91d00d4e0771e7670`. PR #165의 Voigt 산출물은 독립 형제 브랜치이며 조상으로 삼지 않았다.

## 1. 실제 원천과 물리 데이터의 분리

- 보존된 원래 `REC_HD_NONLTE_20261030_SOURCE.zip` (PR #161, SHA256 `27fee6fc9cd815100b60e57bf730f9855ea49b41c280b15d4ceed3d3913695ac`)의 **LAMDA 2021 표시값 전사 JSON**, SHA256 `d44406daf59616c982ca7a33bb3ee962138130588dfb74c7b801972c933da796`: HD v=0 회전준위 9개 J=0,…,8의 에너지와 통계중량; 인접 8개 Einstein A와 **독립 표기된** source photon frequencies; p-H₂/o-H₂ 각각 9개 하향 충돌경로 × 실제 원천 온도 50/100/200 K, 총 54개 충돌률 literal. 원본 LAMDA `hd.dat` 2,289 bytes는 이 세션에 원격 바이트로 재획득되지 않았다. 소스는 공식 LAMDA 페이지 `https://home.strw.leidenuniv.nl/~moldata/HD.html`, 원전 데이터 주소 `https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat`. 충돌률의 출처 Flower (1999), 분광 CDMS 2011 v2.
- PR #164 보존된 Sung et al. 네 **실제 측정** 회전선 R(0)–R(3) 출판값 전사 JSON, SHA256 `e568752432b1dc45e2b5ca37f8b767dad0ced0cea2c289fa29dc77ccdbf8da32`, DOI `10.1016/j.jqsrt.2022.108412`. 전체 실험의 9개 관계/rank 6/세 cycle은 기존 PR #166 증거로 유지하며 **실측이 새로 9개 추가됐다는 주장 금지**.
- CDMS `https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/`는 2011 `HD.fit/.par/.lin/c003501i.cat/.egy` 원본의 서버 목록까지 발견되었으나 실제 원본 바이트와 2011 fit covariance는 미획득. 2019 `.cat` 또는 2026 v3를 대체 사용하지 않았다.
- 새로운 공개 비교 원천 Neufeld (2026), ApJ 1007,16, DOI `10.3847/1538-4357/ae851a`; Zenodo `10.5281/zenodo.21165907`에 2026 9준위 이상 non-LTE HD `.dat/.fits`와 대안 외삽 및 실제 JWST 추론 자료 존재. 원본 데이터 바이너리 미다운로드이므로 **이번 계산의 입력으로 사용하지 않음**.
- CMB 온도 고정값 `T₀ = 2.72548 K`는 Fixsen (2009), DOI `10.1088/0004-637X/707/2/916`, literature central value. 이 값은 조건부 외부 복사장 가정이며 우주 thermal history를 풀었다는 뜻이 아니다.

## 2. 기호·단위·source gate

SI `c=299792458 m/s`, `h=6.62607015×10⁻³⁴ J s`, `k_B=1.380649×10⁻²³ J/K`. `n_{H2}`는 cm⁻³, 충돌률 `q`는 cm³ s⁻¹이므로 `nq`는 s⁻¹. `g_J=2J+1`. `E_J/(hc)`는 cm⁻¹로 출력된 LAMDA term 값이며, `ν^E_{u l}=100c[ E_u/(hc)-E_l/(hc) ]`를 물리 모델의 내재적 energy-gap frequency로 정의한다. 이는 인접 전이의 별도 원본 photon frequency `ν^P`와 **서로 다른 소스 필드**이다.

원래 `|ν^E−ν^P|≤35 Hz` gate는 J=1→0 **PASS**, J=2→1,…,8→7 **FAIL7/8** 유지. 따라서 아래 full-9 정상상태는 `DIAGNOSTIC_ONLY`이다. `ν^E`에 기초한 닫힌 energy ledger는 계산 내부 정의일 뿐 `ν^P`의 실험 오차를 해결한 것은 아니다. `ν^P`를 묵시적으로 갱신하지 않으며 원본 생산 입력 변경 없음.

## 3. 2준위 구성적 유도 (J=0,1에 한해서 소스 조건 충족)

가스 온도 `T_g∈{50,100,200} K`, 외부 흑체 `T_r=T₀(1+z)`, `z≥0`; `\bar n=[\exp(hν^E/(k_B T_r))-1]^{-1}`. H₂ ortho fraction `f∈[0,1]`이고 인접 J1→0 하향 충돌률 `q₁₀=(1−f)q^p₁₀+fq^o₁₀`; 상향률은 상세평형으로 `q₀₁=(g₁/g₀)q₁₀\exp[-hν^E/(k_BT_g)]`. `C_{ij}=n_{H2}q_{ij}`.


a. 아래/위 복사전이율 `R₁₀=A₁₀(1+\bar n)`, `R₀₁=(g₁/g₀) A₁₀\bar n`.

b. 점유수 정상상태 `p₁=(C₀₁+R₀₁)/(C₀₁+C₁₀+R₀₁+R₁₀)`, `p₀=1-p₁`.

c. **복사에너지 순유출** (양수=냉각, 음수=복사에 의한 순가열):

\[
\frac{\Lambda_{10}}{n_{HD}}=h\nu^E A_{10}\frac{C_{01}(1+\bar n) -(g_1/g_0)\bar n C_{10}}
{C_{01}+C_{10}+A_{10}[1+\bar n +(g_1/g_0)\bar n]}.
\]

따라서 `q_{10}>0`, `nH2>0`일 때 `sgn(Λ₁₀)=sgn(T_g−T_r)`. 이것은 양 온도인 흑체 bath, 상세평형 collision law, 고정된 Einstein A, optically thin steady state 가정 하의 **정확한 2준위 정리**다. `nH₂=0`에서는 두 reservoir가 분리되어 `Λ=0`; `T_g=T_r`에서는 상세평형으로 정확히 `Λ=0`. 이것을 full9 production/no-go 또는 실제 기체 history의 결과로 확대할 수 없다. 초기조건 없음 (정상상태), 벽 경계 없음 (공간균질 optically thin bath).

해석적 임계적색편이 `z_⋆=T_g/T₀−1`: 50K → 17.3453923713, 100K → 35.6907847425, 200K → 72.3815694850. 2021 LAMDA 소스에서 `q^p_{10}=q^o_{10}`은 실제 세 온도에서 같아서 이 2준위 모형의 복사 유출은 정확히 `f`에 독립한다. 이를 full9에 일반화할 수 없다.

## 4. 9준위 마스터 방정식과 에너지 ledger

`Q_{i←j}` 컬럼 generator에 8개 인접 복사 경로 및 9개 원천 H₂ 충돌 경로(J2→0 포함)를 삽입한다. `R_{u→l}=A_{ul}(1+\bar n_{ul})`, `R_{l→u}=(g_u/g_l)A_{ul}\bar n_{ul}`이고 충돌 역전이는 원천 energy-gap에 따른 상세평형. `Qp=0`, `Σ_J p_J=1`, 각 `Q` 컬럼 합은 0. 수치적으로 `mpmath` 80자리 LU를 사용, source field 변환을 명시하여 높은 J의 작은 점유수를 보존.

복사 유출 `Λ_rad/nHD=Σ_{u>l}hν^E_{ul}[p_uR_{ul}−p_lR_{lu}]`, 충돌 유입 `Λ_col/nHD=Σ_{u>l}hν^E_{ul}[p_lC_{lu}−p_uC_{ul}]`. `Qp=0`와 동일한 준위 gap을 양쪽에 쓰므로 `Λ_rad=Λ_col`은 **구현 내부 에너지 balance**이다. 원래 LAMDA `ν^P`의 35Hz source gate가 일곱 전이에서 실패한다는 문제와 구분. 9준위 수치는 새 모델의 물리적 탐색이지만 **owner 입력 승격과 생산 가동에 사용할 수 없음**.

## 5. 실제 계산값과 분광 관측량

다음 결과는 모두 `n_H2 = 10⁴ cm⁻³`, ortho fraction 0.5에서 나온 **조건부 물리 예측**이고 항성/우주 실제 관측 데이터가 아니다. 부호는 복사 순유출을 가리킨다.

| 가스 T (K) | z | CMB T (K) | J1 source-gated Λ/nHD (W/HD) | full9 diagnostic Λ/nHD (W/HD) |
|---:|---:|---:|---:|---:|
| 50 | 0 | 2.72548 | +1.50257305e−29 | +1.61768845e−29 |
| 50 | 30 | 84.48988 | −3.00005673e−29 | −4.29636558e−29 |
| 100 | 0 | 2.72548 | +3.94349294e−29 | +8.20244125e−29 |
| 100 | 50 | 138.99948 | −2.24868004e−29 | −8.02848237e−29 |
| 200 | 50 | 138.99948 | +2.00947187e−29 | +1.64314810e−28 |

144개 2준위 source-gated CMB 정상상태, 144개 full9 diagnostic, 1,152개 9준위 전이별 emitted/absorbed/net photon energy rows를 실제로 생성했다. Sung Table 4의 네 **기존 실제 실측** ν₀를 FRW 관계 `ν_obs=ν_source/(1+z)`에 적용한 16개 조건부 **예상 관측 주파수/파장**도 별도로 생성했다. 이 16개는 새 실험으로 간주하지 않음. PR #165의 296 K line-shape 도표를 이 50–200 K 충돌 모델에 임의의 온도의존 선폭 없이 합치지 않음.

## 6. 실제 검증 및 한계

- 저장된 출처 전사 SHA256 고정, 소스 변형 시 일반 및 Python `-O` 환경에서 읽기 거부.
- `python -m unittest discover -s tests -v`: **19/19 PASS**, `python -O -m unittest discover -s tests -v`: **19/19 PASS**, compileall PASS.
- **Wolfram**: 정확 2준위 유도식 차이가 항등적으로 0, `T_g=T_r` 부호식 0, 순방향 충돌률 0일 때 복사 순전달 0 확인.
- 독립 구현 NumPy float64에서 12개 사례의 전체 순복사 유출을 80자리 mpmath 경로와 비교하여 최대 상대차 **4.8395×10⁻¹⁴**. 매우 작은 high-J에서 float64 점유수가 `−3.09×10⁻¹⁸`까지 표시되는 것은 반올림/소거오차이지 물리적 음수 점유수가 아니다. 본 생산 코드의 80자리 검증과 혼동하지 않음.
- 새 2026 Neufeld Zenodo 소스 본문은 확인했지만 해당 원본 `.dat/.fits` **다운로드 실패**. 실제 Neufeld benchmark, 실제 JWST fitting, 원본 CDMS covariance, Sung 공동 calibration 오차 복원 모두 **NOT_RUN/INPUT_MISSING**.
- 독립된 사람/모델의 native subagent R6/C9는 **NOT_RUN**. 내부 Wolfram CAS와 별도 NumPy 방법을 ‘다른 저자 검증’이라고 바꾸어 부르지 않음.

## 7. DAG 및 다음 연구 의무

| Ledger | 이번 실행 이후 |
|---|---|
| Canonical | **28/88** (증가 0) |
| REC physical | **0/313** (증가 0) |
| REC-EXP-SPECTRAL | **PARTIAL**, 실험 edge=9, rank=6, cycles=3 |
| 상속된 보조 source model | **1/2**, 변경 없음 |
| 새 연구 단위 | **1/1 scoped J1 CMB**, canonical 또는 owner node 아님 |
| 35Hz 원본 | **FAIL7/8**, 허용오차 변경 없음 |
| CDMS 원본 .fit/.par/.lin/카탈로그 및 covariance | **NOT_ACQUIRED** |
| LAMDA 원본 hd.dat 바이트 | **NOT_REACQUIRED** |
| H5 epsilon / H6 / H7 | **NULL / OPEN / OPEN** |
| L4 / REI activation / production | **false / false / HOLD** |
| R6/C9 different-author | **NOT_RUN / NOT_RUN** |

새 J1 CMB 보조 결과는 연구용 **완료 가능한 물리 결과**다. 기존 canonical physical completion을 덮어쓰지 않는다. 다음에 Neufeld 2026 `hd_lamda.dat`와 `hd_population_grids.fits` 원본을 byte-authenticate하여 Neufeld grid에서 나오는 9준위 population을 독립 검산하고, CDMS v2 원본 파일·fit covariance 및 Sung 주파수 calibration 자료를 확보해야 한다. 재현성 없는 임의 sigma/chi-square, 2019/2026 v3 대체, 강제 merge 및 다음 노드 자동 착수는 금지한다.
