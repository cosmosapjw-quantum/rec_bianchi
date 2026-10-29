# REC HD source-bound Voigt opacity 연구 보고서 · 2026-10-30

**신규 실험 측정값 수:** 0 (PR164 원본 Sung Table 4의 4개 재사용). **신규 조건부 분광 물리 사례:** 36, 파수별 프로파일 7,236행. 신규 그림 3개. 실제 4개 실측 line-center의 LAMDA 원본 대체, 새 real telescope observation, 원본 2011 catalog fit 또는 astrophysical cooling history는 생성하지 않았다.

## 물리 목적과 원 근거

원본 보존 기준은 REC PR164 immutable HEAD `e050b97b7d5c6c0929062fafd7333e0164112399`. Sung et al., JQSRT 295, 108412 (2023), DOI `10.1016/j.jqsrt.2022.108412`, 원논문 Table 4에서 얻은 네 전이 R(0)–R(3)의 `nu0, S_296, H2 HWHM slope, H2 center shift`를 부모 ZIP에서 정확히 상속하였다. HITRAN 공식 문서 `https://hitran.org/docs/definitions-and-units/`에 따라 S가 **자연 동위원소 존재비 가중 선강도**라는 convention을 보존한다. 이 강도에 HD-only molecule column을 곱하는 것은 원칙적으로 잘못이므로, N_ref는 동일 convention에 대응하는 가상 reference-column으로 정의한다.

이론은 `THEORY_KO.md`, 계산식과 결과 입력 잠금은 `CODING_KO.md`, `data/LAB_INPUT_PARENT_PR164.json` 및 `SOURCE_IDENTITY.json`을 참조. 296 K, 순수 H2 충돌 기여만 고려한 pressure shift/HWHM과 Maxwell-Doppler Gaussian의 Voigt convolution을 사용했다. 이것은 원 실험의 hard-collision Rautian profile을 동일하게 재현하지 않는다.

## 생성 물리 결과

파수별 `tau=N_ref*S*Voigt`, `T=exp(-tau)`를 4 lines × 3 H2 partial pressures (0.01, 0.1, 0.5 atm) × 3 reference columns (1e22, 1e23, 1e24 cm^-2)로 계산했다. 36개 조합의 중심 위치/폭/광학깊이/투과율/등가폭, 총 7,236 profile points가 CSV에 저장되었다. 세 부류의 그림은 중심 광학깊이, 세 압력별 R(2) 투과율 곡선, 등가폭-컬럼 관계다.

p(H2)=0.1 atm, N_ref=1e24 cm^-2의 직접 코드 출력:

| 회전선 | 조건부 중심 파수 cm^-1 | Doppler σ cm^-1 | Lorentz γ cm^-1 | τ_peak | center transmission | finite-window W cm^-1 |
|---|---:|---:|---:|---:|---:|---:|
| R(0) | 89.227937000 | 0.000268596921 | 0.0012 | 0.1410209370 | 0.8684711283 | 0.0005332242241 |
| R(1) | 177.841551000 | 0.000535344264 | 0.00114 | 0.5739503180 | 0.5632958401 | 0.002066842202 |
| R(2) | 265.240656000 | 0.000798436129 | 0.00104 | 0.6491315372 | 0.5224993511 | 0.002420237946 |
| R(3) | 350.853902000 | 0.00105615268 | 0.00097 | 0.3141417570 | 0.7304154793 | 0.001384431364 |


**그림의 진술 범위:** 모든 선형상은 사용자가 지정한 모델 입력에 대한 예측이다. Sung 원 실험 스펙트럼의 복원 또는 새 실측 데이터가 아니다. 더 낮은 0.01 atm는 실험 fitting 범위 외삽 가능성이 있고 self-broadening/나란한 다른 선들은 제외한다. N_ref와 H2 pressure는 실제 기하학·혼합비로 연결되어 있지 않다. 광학깊이 정확도는 원논문 296 K fit systematics와 covariance가 부재하여 통계적으로 보증하지 못한다.

## 물리/구현 검증

Python unittest `15/15` normal, `15/15` with `-O`, `compileall` PASS. Source 4개 measured 숫자의 단일 값 변조 차단은 `assert`가 아니라 `ValueError`로 구현하여 -O에서도 보존한다. Positivity, normalization, Gaussian/Lorentz 극한, 0<T≤1, column-scaling, 이상적인 line area 및 finite-window eq-width 불등식 검증. Wolfram 독립 도구로 R(0), p=.1 atm, N_ref=1e23 cm^-2의 Doppler σ=0.0002685969210133116 cm^-1, peak_tau=0.014102093702663755, transmission=0.9859968750523141을 확인했다. 3개 실제 PNG 시각검수. native distinct-author reviewer 및 full Rautian observational validation NOT_RUN.

외부 기존 GitHub Action `verify-durable-backup`의 PR164 실행은 FAIL(로그에서 많은 historical CSV trailing whitespace), 이 기존 CI 실패는 이번 신규 물리 코드 테스트 PASS나 cloud 백업 인증으로 대체할 수 없다. 원 프로젝트 전체 파일 자동 whitespace 정리는 원본보호 범위를 벗어나므로 수행하지 않았다.

## 보존, DAG, 다음 연구

부모 PR164 full ZIP은 sha256 `{source['parent_zip']['sha256']}`, {source['parent_zip']['bytes']} bytes로 정확히 재복사되고 ZIP CRC 통과. 새 전체 ZIP 및 원격 경로는 별도 `delivery/FINAL_DELIVERY_ACK.json`이 확정한다. 대화나 GitHub의 말만으로 백업 `UPLOAD_VERIFIED` 또는 `RESTORE_VERIFIED`를 주장하지 않는다.

연구 완료 판정: **조건부 과학 모델 데이터 생성**, 새로운 관측값 없음. `REC-EXP-SPECTRAL` 여전히 PARTIAL, canonical **28/88**, REC physical **0/313** (+0). 신규 scoped **18/20**, R6·C9 별개 저자 독립 검사 NOT_RUN, original **35Hz FAIL7/8**, H5 epsilon null, H6/H7 OPEN, L4/REI=false, production HOLD. 2011 original CDMS `.fit`/`.par`/`.lin`/`.cat` raw와 joint fit covariance, Sung 원 PDF/원 스펙트럼 및 systematic covariance 확보가 원본-수준 실험 해석의 다음 단계다. 현행 CDMS v3로 대체하지 않는다.
