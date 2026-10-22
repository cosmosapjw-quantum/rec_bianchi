# C2 그림의 의미와 판독 기준

최종 그림은 `figures/v2/`다. 원본 첫 렌더는 `figures/`에 보존했다.
모든 그림은 폭 90 mm에서 8–9.5 pt 글꼴로 작성했다. Double-column에서는
동일 vector PDF를 확대할 수 있다.

## Figure 1 — Baseline latency

8개 저장 경로에서 결정적으로 선택한 64개 상태씩을 기존 진단 함수로
평가한 시간이다. 파란색은 `gather_set`, 주황색은 CI/CE `_evaluate_grid`다.
각 점은 profiler를 사용하지 않은 한 번의 반복, 세로 표시는 세 반복의
중앙값, 가로선은 관측된 최소–최대 범위다. 신뢰구간이나 오차 추정이 아니다.
가로축은 상태당 wall time(ms)의 로그 축이다. 03/04는 seed, hot/ref는
`actual_hot`/`planck_reference`, N/R은 nominal/refined를 뜻한다.

이 값은 64점 부분 격자에 대한 point diagnostics와 해당 부분 격자의
assembly/quadrature를 포함하며 파일 I/O와 초기화는 제외한다. 전체 16,170개
저장 행의 생산 시간으로 외삽할 수 없다. 마지막 사례의 큰 분산은 제거하지
않았다. 별도 순서 검사에서도 큰 변동이 다른 사례로 옮겨 나타났으므로
물리 branch 또는 refinement 자체가 느리다는 근거로 읽으면 안 된다.

첫 렌더에서 마지막 행의 데이터와 범례가 겹쳤다(P1). V2는 범례를 axes
밖으로 옮겼으며 측정 배열은 byte-identical하다.

## Figure 2 — Baseline cost attribution

한 번의 cProfile 평가에서 얻은 512개 상태의 진단 비용을 서로 중첩되지 않는
세 호출 하위 경로와 나머지로 분해했다. `ThermalSources.evaluate`에는 이미
계산된 network를 전달하므로 이 경로에서 `AtomicNetwork.evaluate`를 다시
호출하지 않는다. `Geometry.fields`도 이 두 경로 안에 중첩되지 않는다.
따라서 이 세 함수의 cumulative time을 여기서는 합산할 수 있다. 다른
중첩 함수들의 cumulative time 전체를 합산해서는 안 된다.

분모는 `gather_set`의 합산 profiler self time 5.399687069 s다. 열원 38.9614%,
geometry 24.2282%, 원자망 19.9326%, 나머지 16.8778%다. 이는 계측 중 관측한
비용 분포이며 unprofiled wall time의 정밀한 분해나 개선 후 가속비가 아니다.
단일 함수의 self time으로는 prepared massive moment가 가장 크지만, 그
사실을 전체 geometry 경로가 가장 크다는 뜻으로 읽으면 안 된다.

## 실제 육안 확인 질문

- 점·범례·축 제목이 서로 겹치거나 잘리지 않는가?
- Figure 1의 가로선이 통계적 신뢰구간으로 오해될 여지가 캡션에서 해소되는가?
- Figure 2가 모든 nested cumulative time을 합산한 그림처럼 보이지 않는가?
- 90 mm에서 사례 약어·단위·로그 축·중앙값 표시를 구별할 수 있는가?
- 그림이 후보 구현의 speedup이나 완전한 물리 검증을 암시하지 않는가?
