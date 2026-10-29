# REC-HD-CONSUMER-CALLSITE01 | 실제 소비자 코드·에너지 장부 연구보고서

**2026-10-29 KST** · `cosmosapjw-quantum/rec_bianchi` · parent PR #155 HEAD `861b7f8b3e52d580437a1b4ad448d9669b0d2706` · 새 작업 브랜치 `research/rec-hd-consumer-callsite-20261029`.

## 연구 결과

원본 HD `hd.dat` 2289바이트의 SHA-256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`와 실제 PR151/155 Python 코드 Git blob을 확인했다. 공식 LAMDA의 optional FREQ 의미론은 소비자별로 다르며, PR151 `generate(...,source_consistent=False)`는 **인쇄된 광자 주파수**를 복사 전이의 Bose 점유수/광자 에너지에 쓰는 동시에 **준위 에너지 차이**를 충돌 상세균형에 쓰는 `MIXED` 진단 코드임을 확인했다. PR155 `frequency_comparison`은 두 정책을 비교하는 연구 도구이지 production solver가 아니다.

REC의 실제 `hyrec_source_adapter.one_photon_planck_null_residual`은 같은 `frequency_Hz`로 upper Boltzmann population과 Planck occupation을 동시에 만들므로 입력 주파수가 무엇이든 상세균형 잔차가 항등적으로 0이 된다. 따라서 이 null helper만으로 **독립된 LAMDA 준위차와 인쇄 주파수의 일치 여부를 검사할 수 없다.** REC `frequency_liouville.from_network`는 hydrogen Ly-alpha 고정 COM grid `nu_abs_Hz + x Doppler_width_Hz`와 mode measure를 사용하며, HD LAMDA loader가 확인된 것은 아니다. BASS의 검사된 Saha/Peebles·Thomson/BGK 모듈과 REI의 검사된 HI/HeI/HeII continuum 모듈도 HD 회전선의 실제 소비자로 확인되지 않았다. **이는 선택한 9개 파일/함수에 대한 코드 감사 결과이지 전체 repo/branch에 대한 부재 증명이 아니다.** `CALLSITE_MATRIX.json`에 각 repo/commit/blob/function/line을 보존했다.

국소 정지 프레임에서 상준위→하준위의 순방출 이벤트 밀도를 `R_j=n_u W_down-n_l W_up` (m^-3 s^-1)로 정의하면, 물질 준위에너지 `h nu_E,j`, 광자 에너지 `h nu_P,j`를 사용하는 두 부문의 국소 소스 합은

\[
\boxed{\mathcal Q_{m+\gamma}=h\sum_{j=1}^8(\nu_{P,j}-\nu_{E,j})R_j.}
\]

이 식은 실제 열생성률이 아니라 **원본 데이터 두 필드를 동시에 사용하는 모델의 조건부 에너지 장부**다. 외부 reservoir, line-shape transport, frame boost, cosmological work가 있는 경우 별도의 물리적 식이 필요하다. 임의의 독립 R_j에 대해 채널별로 장부가 0이려면 각 `nu_P,j=nu_E,j`여야 하지만, 특정 R_j에서는 부호가 상쇄될 수 있다.

정확한 source-decimal 계산에서 가장 큰 주파수 불일치는 **J=6→5**, `nu_E-nu_P=-1,827,572.5607572 Hz`이며, 순방출 이벤트 한 건당 총 국소 소스 계수는 **+1.210962399179234431758×10^-27 J/event**다. 이것은 광자/준위 소스 표현 차이의 계수이지 물리적 에너지 생성이나 관측 오차가 아니다. 여덟 전이의 부호와 값은 `results/RESULT.json`과 `results/LOCAL_LEDGER.png`에 보존했다.

## 실제 코딩·검산

- 기존 PR151 `multichannel.py` Git blob `029255494bf0a63b93bf8b2715327a8585afb5f3`와 PR155 `field_semantics.py` Git blob `21517960f912efbd2dc9df8b94fd577e03ca2e27`을 **실제로 import**하여 원본 source로 `generate`를 실행했다. 과거 9×9 정상상태·native·IVP는 실행하지 않았다.
- 인쇄 주파수 J2의 메모리 내 값을 +0.001 GHz 바꾼 결과, **복사 edge 1개만 변경**, 다른 7개 복사 edge와 18개 충돌 edge는 동일. 원본 2289바이트는 변경하지 않았다.
- T=50,100,200 K × 임의 진단 충돌밀도 1000,1000000 cm^-3의 **6/6 preflight PASS**. 단일 하준위 밀도 `n_l=1 m^-3`를 둔 합성 Boltzmann/Planck 장부를 mpmath95 직접 rate와 별도 `expm1` oracle로 대조했다.
- Python `unittest` **24/24 PASS**, `compileall` PASS. 원본 SHA 변조, 부모 코드 blob 변조, 비유한 입력, 음수 주파수, energy gauge shift, 불변 collision edge, 원래 35Hz `FAIL7/8` 보존을 검사했다. 별도 Decimal90 구현으로 8개 per-event 에너지 계수를 Fraction 결과와 **정확히** 대조했다.
- Wolfram Language에서 상기 `R`와 `Q`의 기호식을 확인했고, 동일 주파수에서 구성한 null helper가 정확히 0이라는 항등식 및 8개 source-decimal 최대값을 대조했다.
- 첫 번째 직접-rate oracle에 잘못된 `exp(-x_E)` 인자가 있어 초기 실행이 실패했으나 수학적으로 교정한 뒤 통합 재검증했다. 초기 matrix test의 임의 이름 규칙 오류도 교정했다. 원 실패는 `CODING.md`에 보존했다.
- 90 mm 단폭 그림을 열어 확인했고, J1/J8의 아주 작은 비영 값을 footnote로 표시했다. 그래프는 실제 물리적 source energy 생산률이 아니라 **이산 8전이 per-event signed coefficient**다.

## 다른 저장소·CI 상태

BASS 최신 CE1-F 관련 PR #241, REI UVB PR #261, WU088_HH HD reactive PR #156 및 관련 REC PR #151–155를 조사했으나, 이들의 다른 물리적 공급자·검증 상태를 REC에 수입하지 않았다. WU의 H+ + HD → D+ + H2 반응율은 HD 중성 복사선 CDMS 주파수 자료가 아니다. REC parent PR155의 `verify-durable-backup` CI는 실패이며, 로그에서 과거 `research/rec_source_synthesis_20261027`의 CSV 후행 공백 등이 검출됐다. 해당 저장소 수준의 검증 실패는 이번 source-only 23개 테스트 PASS와 분리해 기록했다.

## 판정과 남은 문제

**`PASS_SCOPED_CONSUMER_MAPPING_AND_LOCAL_LEDGER`**. 새 수학적 항등식과 실제 PR151/155 consumer의 metadata-only mutation은 직접 검증했다. 그러나 **다른 저자의 독립 심사 R6/C9는 NOT_RUN**, BASS/REI 전체 native/generated code 및 모든 최신 비공개 브랜치의 HD 호출 부재를 증명하지 않았으며, CDMS 2011 v2 원바이트·LAMDA 변환 lineage는 여전히 확보하지 못했다. 따라서 중앙 **28/88(+0)**, REC 물리 **0/313(+0)**, H5 epsilon `null`, H6/H7 `OPEN`, L4/REI false, production `HOLD`, 원 35Hz **FAIL7/8** 유지.

다음 물리적 진척의 필수 입력은 CDMS v2 원본 파일과 QN/TAG/uncertainty 및 LAMDA 변환 계보다. 독립적인 코드 후속 과제는 BASS/REI/REC의 native C/Rust 및 전체 호출 그래프를 **실제 로컬 checkout**에서 스캔해 이 9개 파일 감사 범위를 넓히는 것이다. 둘 다 기존 승인 없이 source replacement나 물리 gate 승격으로 이어지지 않는다.

### PR156 CI SVG 자체 결함 수정

최초 PR156 CI 실패에는 기존 CSV/SVG 공백 외에도 **이번 신규 `LOCAL_LEDGER.svg`의 후행 공백 801줄**이 포함됐다. 이를 신규 구현 결함으로 정확히 분류하고, 기존 SVG를 보존한 뒤 공백만 제거해 XML 구조·path token 의미가 같음을 확인했다. `plot_ledger.py`의 이후 출력도 정규화하도록 수정하고 회귀 테스트를 추가했다. **최종 targeted unittest 24/24 PASS**. 기존 repo-wide 검증은 역사적 파일 공백 때문에 계속 FAIL이며 CI 전체 PASS를 주장하지 않는다. 수정 전 SOURCE ZIP과 stage snapshots는 역사적 증거로 유지하고, 수정 후 별도 SOURCE ZIP을 최종 재현본으로 제공한다.
