# REC-DONOR-03 — 물리 deposition 입력 권위 계약 초안

상태: `DRAFT_FOR_OWNER_REVIEW`

유지하는 제한: `NO_PASS_REC_PHYSICAL_SPLIT`

## 1. 목적과 변경 범위

PR #63의 수치 어댑터는 완료된 선행 작업이다. 이 문서는 그 구현이나 검증을 다시 열지 않고, 원본 HyRec의 어느 양이 어댑터 입력 `R_sa`, `B_is`, `mu_i`에 해당하는지 추적한다. 원본에서 정해지는 사실, REC의 변환, 추가적인 물리·수치 선택을 분리한다. 새 생산 코드, 실행기, 테스트, map, provider는 만들지 않는다.

검토 기준은 `cosmosapjw-quantum/rec_bianchi`의 commit `aeb01d369436f2d0eda2c946e9c650e54ae06fca`, tree `afa41c177aa27d73ef772a7d20522d3ef2ef7835`이다. 정확한 파일 경로·blob·관련 기호는 같은 폴더의 `SOURCE_TRACE.json`에 기록한다. 현재 초안이 이전 계약이나 소스의 의미를 자동으로 교체하지는 않는다.

이번에 읽은 것은 이 기준에서의 실제 Python 소스, 보존된 C/header 발췌, 기존 출처 기록과 Git 파일 메타데이터다. 원본 ZIP을 이번 실행환경에서 새로 압축 해제하거나 재해시하지 못했다. 따라서 아래의 원본 C 관련 주장은 보존된 발췌가 보여주는 범위로 제한한다. 원본 archive의 프로젝트 내 정본 지위는 이미 수락된 책임자 확인을 유지하며, 내부 날짜 차이를 이유로 다시 문제 삼지 않는다.

## 2. 원본과 현재 코드의 대응

| 원본 또는 현재 객체 | 확인한 의미 | 허용되는 사용 | 금지되는 등치 |
|---|---|---|---|
| `HyRec_Oct2012.zip` | 책임자가 지정한 October-2012 정본, 등록 SHA-256과 Git blob 존재 | 원본 C와 표의 기준 입력 | 이번 턴에 ZIP 바이트를 새로 검증했다는 주장 |
| `Eb_tab[b]` | 가상준위 중심 에너지, eV | 채널 에너지·임계 구간 추적 | 유한 셀 경계 또는 폭 |
| `A1s_tab[b]` | `3*A2p1s*phi(E)*DE` | 원본 확산·가상준위 계산의 계수 | 독립적인 1광자 생성률 또는 물리 셀 전이율 |
| `A2s_tab[b]` | 임계 아래 `dLambda_2s/dE * DeltaE`, 위 Raman 계수의 구간 적분 | 해당 원본 구간·정규화에서 계수 사용 | 추가 `DeltaE` 곱셈, 근거 없는 추가 광자 수 2 |
| `A3s3d_tab[b]` | `(dLambda_3s/dE + 5*dLambda_3d/dE)*DeltaE`, 지정 구간에서 Raman 성분 | 합쳐진 계수로서 추적 | 5를 다시 곱함; 독립 3s·3d 개체수 채널로 임의 분리 |
| `A4s4d_tab[b]` | `(dLambda_4s/dE + 5*dLambda_4d/dE)*DeltaE` | 원본과 같은 합산·구간 조건 | 별도 하위준위 정보 없이 분해 |
| `Tvr`, `Trv`, `Trr` | 실준위·가상준위 결합 행렬, 열적 인자·축퇴도와 부호 포함 | 원본 대수계의 계수 | 행렬 원소 자체를 양의 photon packet rate로 사용 |
| `PhysicalTwoPhotonRamanBin` | REC가 별도로 정의한 스칼라 추적 광자 전후방 쌍 source | 입력 계수·개체수·동반 광자의 출처가 지정된 경우 식 검토 | 원본 C가 이 객체를 직접 저장하거나 출력한다는 주장 |
| `OriginalHyRecVirtualSpikeSource` | signed `Delta_f`에 대한 가상 spike 통과 갱신 | 원본 순서·기준장·특성선 범위에서 사용 | `s^-1` 연속 packet source 또는 비음수 total `f`와 직접 합성 |
| `IsotropicEinsteinLineSource` | 위상공간 인자까지 적용한 occupation-rate 계수 | 이미 변환된 local occupation action | 다시 `n_H/mu` deposition 적용 |
| `transport_edge_flux_per_H_s` | 원본 snapshot의 순 경계 광자 flux, per H per second | 집계된 경계 flux의 추적·비교 | 서로 배타적인 미시 채널별 전이율 |
| `COMSourceDepositionPlan` | 호출자가 실제 물리 measure와 보존 map을 제공하는 계산기 | 고정 map의 action/JVP | 원본 가상준위에서 map·measure를 스스로 결정하는 권위 |

### 2.1 원본 표에서 이미 적용된 연산

보존된 `HyRec/hydrogen.c` 발췌의 270, 278–283행은 표 읽기를, 287–290행은 `A2s_tab[0:NSUBLYA]`의 합을 `L2s1s`로 맞추는 연산을 보여준다. 현재 reader는 `NVIRT=311`, `NSUBLYA=140`, `L2s1s=8.2206 s^-1`를 사용한다. 원본 header 발췌의 96–100행은 중심 에너지와 네 표 열의 의미를 구분한다.

따라서 원본의 구간 적분 계수에 새 구간 폭을 다시 곱하거나, 이미 합쳐진 d-state 가중치 5를 다시 적용하면 안 된다. 반대로 이 정보만으로 전체 주파수 영역의 교환 대칭 계수, 한 쌍당 두 광자의 집계 방식까지 확정할 수는 없다. 특히 sub-Lyman-alpha 합이 8.2206이라는 사실만으로 임의의 모든 입력에 추가 factor 2를 정당화할 수 없다.

### 2.2 원본 결합 행렬과 독립 packet source의 차이

보존 C 발췌 470–477행에서 `Tvr[0,b]`는 `A2s_tab[b]`에 `abs(exp((E_b-E21)/TR)-1)`의 역수와 원자 상수 재척도를 적용한 음의 비대각 계수이다. `Trv[0,b]`에는 다시 `exp((E_b-E21)/TR)`가 곱해진다. 두 번째 실준위 행은 3s/3d와 4s/4d 성분을 각각 `exp(-E32/TR)/3`, `exp(-E42/TR)/3`와 함께 합치며, 역방향에는 추가 3이 나타난다.

현재 `evaluate_canonical_coupling()`은 이 경로를 재구성하며 `fsR**8 * meR`를 사용한다. 이 원본 대응 계수에는 동반 방사장의 열적 감소 인자가 이미 들어 있다. 이를 독립적인 bare packet 계수라고 다시 명명하고 `PhysicalTwoPhotonRamanBin`의 동반 occupation 인자를 곱하는 합성은 별도 유도 없이 허용하지 않는다.

`primitive_rates.py`의 `Alpha`, `Beta`, `R_2p2s`도 원자 개체수 계통의 계수다. `DAlpha`는 `Alpha(Tm,Tr)-Alpha(Tr,Tr)`이며 미분 기호가 아니다. SI 변환에서 재결합 계수 `cm^3/s`는 `m^3/s`로 변환되지만, 보통 전이율 `s^-1`에 같은 인자를 적용하지 않는다.

## 3. 추적 광자와 원자 사건을 분리하는 계약

### 3.1 이미 코드에 존재하는 추적 광자 식

현재 `PhysicalTwoPhotonRamanBin`은 상위·바닥준위 개체수를 `x_u`, `x_g`, 축퇴도 비를 `g`, 동반·추적 occupation을 `f_c`, `f_t`로 받아 다음을 계산한다.

두 광자 과정:

\[
R_t^{2\gamma}=\Lambda\left[x_u(1+f_c)(1+f_t)-g x_g f_c f_t\right],
\qquad E_t+E_c=\Delta E_{ug}.
\]

Raman 과정:

\[
R_t^{\mathrm R}=K\left[x_u f_c(1+f_t)-g x_g(1+f_c)f_t\right],
\qquad E_t-E_c=\Delta E_{ug}.
\]

반환값은 추적된 광자의 순 생성률이다. 이는 실제 물리 입력의 인증이나 원본 채널 집계의 완결을 의미하지 않는다. 코드에 이 paired 식이 이미 있다는 사실과, 최근 `physical_source_authority.py`의 manufactured 비국소 probe만 존재한다는 사실은 구분해야 한다. 기존 식을 새로 구현하지 않는다.

직접 대수 점검: `X=exp(E_c/(k_B T))`, `Y=exp(E_t/(k_B T))`일 때 `f_c=1/(X-1)`, `f_t=1/(Y-1)`를 대입한다. 두 광자 과정은 `x_u=g*x_g/(X*Y)`, Raman은 `x_u=g*x_g*X/Y`에서 전후방 항이 상쇄된다. 이는 고정된 쌍의 열평형 항등식일 뿐, 전체 스펙트럼·공명·다중도·시간 진화의 검증이 아니다. 이번 환경에서 새 CAS 실행은 없었다.

### 3.2 사건을 한 번 세는 경우의 조건부 광자 장부

다음 `q`는 원본 배열명이나 검증된 원본 출력이 아니라, 원자 사건을 한 번만 세는 순사건률의 새 표기다. 실제 원본 표가 이 `q`와 같은지 아직 가정하지 않는다.

| 과정 | 추적 광자 다리 | 동반 광자 다리 | 전체 광자 수 변화 | 광자 에너지 변화 |
|---|---:|---:|---:|---:|
| 두 광자 방출의 순사건 | `+q` | `+q` | `2q` | `(E_t+E_c)q` |
| Raman의 순사건 | `+q` | `-q` | `0` | `(E_t-E_c)q` |

이 표는 주어진 에너지 관계와 사건 정의에서 직접 유도한 bookkeeping이다. 원본 적분 영역이 교환된 광자 쌍을 이미 세고 있는지, 별도 대칭 인자를 포함하는지는 원본 바이트와 정의를 따라 확인해야 한다. 그 답을 책임자의 임의 선택으로 대체하지 않는다.

COM에 한 광자 다리씩 전달한다면 각 열의 `source_energy_J`는 그 다리의 광자 에너지이고, 두 광자 원자 전이의 총 에너지를 두 열에 반복해서 넣지 않는다. Raman의 흡수 다리는 부호 있는 `R`로 표현한다. 현재 비음수 `B`에 사건의 음의 화학양론 부호를 섞지 않는다. 이 문서에서 그러한 열 또는 map을 실제 생성하지는 않는다.

동반 광자를 고정된 열적 저장소로 처리하는 범위를 택할 수는 있으나, 그 경우 계산되는 것은 추적 광자 부분계다. 빠진 다리의 에너지 교환을 숨긴 채 전체 방사장 보존을 주장하지 않는다. 두 다리의 각도 관계도 원본 등방 스칼라 계수에서 자동으로 주어지지 않는다.

## 4. 물리 measure와 map의 출처

### 4.1 서로 다른 세 물체

`x_b=x_1s*f_b` 또는 그 departure는 원본 가상준위 변수이며 유한 셀 광자 수가 아니다. 현재 `physical_log_mode_factor_per_H()`의 `A_b=8*pi*nu_b^3/(c^3*n_H)`는 수소 원자당 로그 주파수 구간의 계수다. `COMSourceDepositionPlan.mode_measure_m3`의 `mu_i`는 실제 target occupation에 대응하는 물리 measure다. 이 세 물체는 서로 교체할 수 없다.

기존 `PR05B1_SOURCE_IDENTIFIABLE_DAE_FORMALISM.md`는 원본이 중심과 적분 rate만 주고 유한 spike 폭·셀 edge·shape를 주지 않는다는 식별 불가능성 결과를 보존한다. 중심이 같고 폭만 두 배인 두 양의 support는 같은 영폭 극한을 가지면서 다른 유한 measure를 만든다. 이는 이번에 새로 실행한 반례가 아니라 기존 연구 근거의 재사용이다. 따라서 이 초안은 native 중심의 중간값 등으로 물리 셀 경계를 임의 생성하지 않는다.

### 4.2 명시된 유한 셀 표현에서만 성립하는 조건부 식

두 편광에 같은 스칼라 occupation을 사용하고, 각도 평균 가중치의 합이 1이며, 주파수 셀 내부에서 occupation을 상수로 표현한다고 별도로 선언한 경우에 한해:

\[
\mu_i=\frac{8\pi}{c^3}\int_{\nu_{i-1/2}}^{\nu_{i+1/2}}\nu^2\,d\nu
=\frac{8\pi}{3h_P^3c^3}\left(E_{i+1/2}^3-E_{i-1/2}^3\right),
\qquad h_P=2\pi\hbar.
\]

단위는 `m^-3`이다. 이 식은 위 표현 가정에서 직접 유도한 조건부 measure이며, 현재 target grid를 선택하거나 원본 HyRec가 그 셀을 공급한다고 주장하지 않는다. 총 Stokes intensity와 편광별 occupation, `dOmega`와 `dOmega/(4*pi)`를 섞으면 계수가 달라질 수 있으므로 기존 target 정의를 먼저 확인해야 한다.

`sum_i B_is=1`, `sum_i E_i B_is=E_s`는 주어진 photon map의 number·energy 일관성 조건이다. PR #61/#63의 두 보존 map이 다른 출력으로 이어지는 기존 결과가 보여주듯, 이 두 식은 map의 유일성이나 물리 인증을 보장하지 않는다. 실제 map에는 생성 절차, target reconstruction, support, 경계 밖 처리와 원본 물리 채널의 연결이 필요하다. map을 고정한 JVP만 기존 구현 범위이며 moving-map 항을 여기서 추가하지 않는다.

### 4.3 단위 및 집계 경계

- 원본 `nH`의 `cm^-3`에서 SI `m^-3`로의 변환은 `10^6`이다.
- 원본 eV와 SI J, Hz의 대응에는 실제 선택한 상수 집합과 `fsR^2*meR` 에너지 재척도 위치를 기록한다. 원본 수치 재현용 상수를 새 상수로 조용히 교체하지 않는다.
- `TR`가 eV 단위의 재척도된 온도 에너지인지 K인지 구분한다. 원본 `eta=ln(a)` 미분과 물리 초 미분도 구분한다.
- 현재 COM의 각도 가중치는 평균으로 정규화되어 합이 1이다. 등방 `R[S]` 입력과 방향별 `R[S,A]`의 정의에서 추가 `4*pi` 적용 여부를 명시해야 한다.
- `IsotropicEinsteinLineSource`의 `c^3*n_H/(8*pi*nu^2)` 및 profile 인자가 들어간 계수는 이미 occupation rate다. 이를 packet 입력으로 재명명하여 density/measure 변환을 두 번 적용하지 않는다.
- `J_b=H*A_b*(Delta_f_minus-Delta_f_plus)`는 signed 집계 경계 flux다. `Tvr` 개별 채널과 같은 객체가 아니며, 원본의 합산 flux와 별도 paired source를 중복으로 더하지 않는다.

## 5. 미결정 사항과 책임자 검토

다음 세 묶음은 구현을 반복하기 위한 새 하네스가 아니라, 한 번의 책임자 검토에서 정리할 입력 계약 항목이다.

### D1 — 첫 대상과 사건/광자 장부

권장하는 제한된 첫 대상은 `2s` 채널 하나다. 이는 아직 승인된 선택이 아니다. 추적 광자 부분계와 두 광자 전체 장부 중 범위를 결정하고, 원본의 주파수 적분 영역·교환 계수·event 대비 photon normalization을 실제 archive member에서 추적한다. 그 정규화가 원본으로부터 정해지는 부분은 임의 선택 사항이 아니다. 합쳐진 `3s3d`/`4s4d`의 분해는 별도 근거가 생기기 전까지 보류한다.

### D2 — 실제 target와 map 생성 규칙

재사용할 target occupation 정의, measure 생성 코드/입력, 에너지 좌표, 각도 평균, grid와 map의 파일 identity를 지정한다. source 중심을 target 셀 폭으로 해석하지 않는다. 여러 보존 map이 가능하면 보존식 이외의 물리·재구성 조건을 명시하고, 단지 테스트를 통과하는 manufactured map을 승격하지 않는다.

### D3 — 원본 감소 모델과 REC paired 모델의 책임 분리

원본 열적 동반 광자 계수를 소비할 것인지, 독립 paired source로 별도 진화할 것인지 범위를 정한다. 원본 real/virtual 및 escape 계통과 새 source의 중복 집계를 막는 채널별 포함/제외표를 작성한다. `Delta_f`를 total `f`로 바꾸는 경우 기준장과 그 변환을 별도 식별한다. 필요한 개체수·occupation·배경 snapshot이 없다면 미결정으로 남기며, 이번 문서 작성만으로 값을 생성하지 않는다.

## 6. 승인 이후의 최소 수용 조건

실제 입력을 물리적으로 사용하기 전에는 원본 archive/member/표와 사용한 변환의 바이트를 연결하고, 각 channel의 의미와 원자 개체수 정의, rate 단위, photon 다리·다중도, target map/measure를 동일한 기록에서 추적할 수 있어야 한다. 빈 필드를 SHA-shaped 문자열로 채우거나 책임자 승인만으로 미확인 원본 사실을 사실로 만들지 않는다.

이번 문서의 최대 상태는 `DRAFT_FOR_OWNER_REVIEW`다. 아래 값은 유지한다.

```text
physical_source_authenticated = false
provider_admitted = false
NO_PASS_REC_PHYSICAL_SPLIT
```

다음 단일 작업은 D1–D3를 대상으로 한 책임자 검토이며, 그 결과를 기록하기 전에는 새 물리 rate 생성, map 선택, adapter 변경, BASS 연결로 확장하지 않는다.

## 7. 문헌의 역할

SciSpace 검색으로 원본 HyRec와 Hirata의 two-photon 논문을 찾고 다음 원 논문 초록을 읽었다.

- Ali-Haimoud & Hirata, HyRec, arXiv:1011.3758, Phys. Rev. D 83, 043513.
- Hirata, two-photon transitions, arXiv:0803.0808, Phys. Rev. D 78, 023001.

두 논문은 방사장과 원자 개체수의 결합, 고준위 two-photon 공명과 연속 one-photon 과정의 구별이 필요함을 뒷받침한다. 이번에는 본문 전체나 모든 식을 대조하지 않았으며, 초록으로 원본 표의 광자 다중도를 확정하지 않는다. 코드별 수식·상수·부호 주장의 직접 근거는 위 기준 소스와 보존된 발췌다. 문헌 검토가 repository 바이트 인증이나 실행 PASS를 대신하지 않는다.
