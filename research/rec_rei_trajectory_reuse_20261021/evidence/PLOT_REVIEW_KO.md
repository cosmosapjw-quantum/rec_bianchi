# z20→2 저장 궤적 그림 검토

## 판정과 범위

**PASS_SCOPED_STORED_DATA_FIGURES.** 2026-10-21 UTC에 최종 reducer 산출물
`results/TRAJECTORY_ANALYSIS.npz`를 직접 읽어 PNG 4개와 PDF 4개를 생성했다.
PNG 4개를 모두 직접 열었고, 마지막 cancellation 그림의 범례 위치를 수정한 뒤
그 최종 PNG도 다시 직접 확인했다. 부모 reviewer의 확인 뒤, 두 곡선이 겹친다는 안내를 추가하고 최종 그림을 다시 확인했다. 이 기록은 그림 작성 agent
`/root/rei_latest_survey`의 실제 그림 검토이며 독립적인 자기 코드 감사로 표시하지 않는다.
별도의 reducer 독립 코드 검토 및 물리 판정과 혼합하지 않는다.

입력 SHA256:

```text
239595a3313a68e0125ec7b333b8d515c3fd5d6d8ec115fbef2496d3b18428b9
```

그림 코드 `code/plot_trajectories.py` SHA256:

```text
f7eec503f73c6a74be9b15a09704273eebfef2432e6638946077e6b128c93ad7
```

최종 코드의 기본 경로는 현재 delivery 구조인 `results/`와 `figures/`이다.
최종 rendering에 쓴 명시적 명령은 다음과 같다.

```bash
MPLCONFIGDIR=/tmp/rec_trajectory_mplconfig python code/plot_trajectories.py \
  --input results/TRAJECTORY_ANALYSIS.npz --output-dir figures
```

최종 렌더링 전 임시 preview는 같은 immutable intake의 실제 자료로 만들었으며,
배포 그림은 모두 위의 최종 reducer NPZ에서 다시 만들었다. 가상 자료는 사용하지 않았다.
PDF는 같은 Matplotlib Figure에서 함께 저장했다. 직접 시각 검토 대상은 PNG다.

## 확인한 데이터와 표기

- 175개 고유 nominal triple, 63개 축 support, 112개 mixed 비교 대상, 공통 153개 epoch를 확인했다.
- nominal 좌표로 사례를 선택한다. 실현된 작은 초기 floating-point stress를 0으로 덮어쓰지 않는다.
- signed full-Frobenius 세 채널을 사용한다. shear는 `sqrt(6)*s/H`이며 저장된 shear norm을 signed 값으로 오인하지 않는다.
- redshift 축은 실제 저장된 `z`를 사용하며 20에서 2로 감소한다. `z=4` continuation join을 표시한다.
- 모든 그림은 collisionless fixed-L8 유한 모형과 preliminary 범위를 명시한다. 공통 redshift와 case별 서로 다른 proper time을 구분한다.
- residual의 quantile은 각 epoch에서 112개 mixed case에 대한 유한 표본 요약이다. 신뢰구간이나 ODE 오차 인증이 아니다.
- residual 세로축은 `symlog(linthresh=1e-18)`이다. 0부터 1e-18까지 선형이며 그 이상은 로그다. 수치값을 floor, clip 또는 대체하지 않는다.
- 곡선은 저장된 점들을 직선으로 연결한다. parameter 또는 time 재보간, surface 추정, fitting은 하지 않는다.
- 글자/범례/축/footnote의 겹침을 수정했고, 잘린 caption이나 색상표 없이 최종 PNG 4개를 확인했다.

## 그림별 판단

| 그림 | 직접 확인한 내용 | 해석 범위 |
|---|---|---|
| `01_signed_sector_evolution_z20_z2` | 초기 shear 0에서 baseline, pure matter +3e-4, pure radiation +3e-4, 두 방향의 ±3e-4 상쇄 조합을 세 패널에 표시; 범례 5개 | signed shear/matter/radiation의 실제 저장 이력. 각 좌표의 norm은 절댓값 |
| `02_finite_grid_endpoint_response_z2` | S_i=0,.003,.1에서 각 25개 실제 endpoint; x/y 좌표가 원래 비균일 m/r 격자와 일치; 행별 공통 대칭 색상표 | 첫 행은 같은 S_i의 (m,r)=(0,0) endpoint를 뺀 signed shear response. 나머지는 signed matter/radiation endpoint. 점 사이의 면은 추정하지 않음 |
| `03_mixed_trajectory_absolute_residual` | 112개 mixed case의 median/p95/max를 전 153개 epoch에 표시; signed 3채널; 63 support를 residual 통계에 섞지 않음 | 저장 trajectory와 63축 재구성의 사후 discrepancy. 전역/연속 오차 경계가 아님 |
| `04_signed_cancellation_and_total_norm` | Pm/Pr signed curve, `abs(Pm+Pr)`, `abs(Pm)+abs(Pr)`를 구별하고 실제 total norm 대 재구성 norm의 차이를 별도 패널에 표시 | 성분 합을 만든 뒤 norm을 취하는 순서를 직접 보여 줌. 성분 norm의 합은 total norm의 상계이며 total 자체가 아님 |

Figure 3의 실제 전 저장 이력 최대 residual은 다음과 같다.

| 채널 | 최대 절대 residual |
|---|---:|
| Signed shear | 9.40056251721652e-09 |
| Signed matter | 8.582762394605706e-09 |
| Signed radiation | 1.1057774095034681e-08 |

이 값들은 과거 warm C15 endpoint 차이와 합치거나 직접 동일 조건으로 비교하지 않는다.

Figure 4의 단일 case ID는
`9bad767cd17b0651746fca2bd9c6ad6911a6df067ad58af71ab0872827ccacf9`이다.
실현된 초기 total norm은 1.0842021724855044e-19이다. z=2에서
Pm=5.7965531695747936e-06, Pr=-3.9844807585121206e-05,
total norm=3.4048254415546413e-05이다. 전 저장 이력에서 total norm 최대는
7.418120491212348e-05이며, 이 case의 total norm 재구성 차이 최대는
5.7436124760223755e-09이다. 초기 상쇄가 이후 동일하게 유지된다고 표현하지 않는다.
이 case에서 하단의 norm residual과 성분 residual 합 상계는 그림 해상도에서 거의 겹친다. 그림에 "The two curves coincide at this plotted scale."을 명시했다.

## 최종 산출물 identity

| 파일 | bytes | SHA256 |
|---|---:|---|
| `01_signed_sector_evolution_z20_z2.pdf` | 32591 | `17d8ce23ae1541ab0fed46cf12e96aa0031e6b248546acf1a2b42a7bde5b5524` |
| `01_signed_sector_evolution_z20_z2.png` | 273504 | `6839d3cad3b1d482873a0c77ec16c343316d551386915ae614ffab73ee23803a` |
| `02_finite_grid_endpoint_response_z2.pdf` | 42371 | `2681b731c342b86f332451795d3902033df14ce2a9696f0b6f22352604904a89` |
| `02_finite_grid_endpoint_response_z2.png` | 432980 | `d25d540d687714db603768967a6aa50c5b4ed4687475c73b8fa1696ae4de1bd3` |
| `03_mixed_trajectory_absolute_residual.pdf` | 52485 | `76f5d885ac1a1ea88c1cbc532bec3b106dbc9313c983e63fffc94ecbfefd5a07` |
| `03_mixed_trajectory_absolute_residual.png` | 277746 | `b99c04e3b39078cf20ad6798459617b1356c58be25211ddb286fc8c10690404a` |
| `04_signed_cancellation_and_total_norm.pdf` | 33839 | `49065dca6172b8591c33bd040d336da9b4f664334f2318a2c32e182af4a0063e` |
| `04_signed_cancellation_and_total_norm.png` | 250130 | `f06c5a466d399493b76a178f13e407af27f3458a26aadb7dc5594f9e7cca07f1` |

기계 판독용 provenance와 실제 수치 envelope는 `evidence/PLOT_REVIEW.json`에 보존했다.

## 유지하는 상태

새 ODE 실행 0, benchmark 0. 이 그림 생성은 speedup 또는 병렬 scaling 측정이 아니다.
physical HOLD, global convergence NOT_RUN, production NOT_APPROVED와 원래 REC U5 HOLD를 유지한다.
