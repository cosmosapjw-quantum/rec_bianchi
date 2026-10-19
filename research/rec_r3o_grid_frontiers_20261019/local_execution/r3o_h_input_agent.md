# R3O original-h 입력 어댑터와 predictor 그림 인계

## 완료 결과

`prepare_r3o_h_history.py`의 비어 있던 파일을 구현했다. 원본 h `8.49e-5`의
105,859개 상태를 R3N `load_history` 형식으로 저장했고, 두 상태 배열의 바이트가
원본과 동일함을 확인했다. 실제 입력 세 파일, 고정 생산자
`6c6c385f69f73ad477a3131d637b25fe7faca5ac`, 원본 source ZIP, R3I 계약을 검사했다.
출력 디렉터리는 원자적 생성으로 예약하고 파일은 exclusive 생성한다.
입력 읽기 이후 mutation을 실제로 유도한 음성 검사를 포함해 **12개 검사 PASS**였다.
R3N과 기존 cosmology 모듈의 해시는 유지됐다.

원본 h와 저장된 R3M h2를 함께 읽은 결과는 **INSUFFICIENT_LEVELS**, 누락 level `[2]`다.
`xe`, `Tm_K`의 nodewise C parity는 **UNKNOWN**이며 배열을 만들지 않았다.
정수 z 8,001점의 기존 C 최대 오차는 별도 기록으로만 보존했다. binary64
상태의 추가 출력 quantization만 0으로 표시했다. 물리 계약 SHA는
`aca3d76043802e93260ae590f92984453f191e55c31bb8290a24350e198777ef`로 h2와 같다.

구간은 입력 인덱스 기준 `UNKNOWN:0..29194`, `EMLA:29195..72465`,
`PEEBLES:72466..105858`이다. 두 경계는 입력 29195와 72466에 놓았다.
원본 마지막 source node는 ln(a)=2.2387149876124113e-05로 0을 조금
넘지만 z=0 cubic stencil에 필요해 보존했다. R3N의 물리적 boundary coverage는
`[X0+29195*h, 0]`이며 이전 고적색편이 경계가 알려진 것으로 채우지 않았다.
7개 z 앵커의 Python source-grid→기존 Python 출력 대응 차이는 두 필드 모두 0이었다.

## 작은 프로브와 그림

실제 실행은 manufactured affine scalar `y'=-200*y+100`, `y0=1`,
`h=4.245e-5`, 각 12회 갱신의 baseline 및 세 기억 변경이다.
실제 HyRec 생산 궤적의 추가 실행 수는 0이다. baseline의 과거 RHS는 해석해로 만든다.

`e0=0`, `delta2=delta F_(-2)`, `delta1=delta F_(-1)`,
`alpha=1+5*h*lambda/4`라 하면 차분은

- `e1=-h*delta2/4`,
- `e2=alpha*e1-h*delta1/4`,
- `e_(k+1)=alpha*e_k-h*lambda*e_(k-2)/4` (`k>=2`).

이 식을 exact rational arithmetic으로 계산해 실제 float 상태 차이와 비교했다.
세 경우 모두 PASS, 최대 차이는 `1.8763473847577261e-16`이다.
prev2에 1을 더하면 첫 상태 차이의 기대값은 `-1.06125e-5`이며,
prev에만 1을 더하면 첫 차이는 0이고 둘째 단계에 같은 직접 항이 들어온다.
이 결과는 두 predictor 기억의 소유 인덱스를 유지해야 하는 이유를 보인다.

최종 선택 PNG:
`research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/plot_revision_002/predictor_memory_seed_response.png`

원래 아래 패널의 범례를 오른쪽 위로 옮긴 PNG를 실제 view_image로 확인했다.
코드 변경은 범례 위치 한 줄이다. 해당 줄을 되돌린 소스의 SHA가 검사 실행 당시
소스와 일치함을 확인했다. 수치 코드는 재실행하지 않았다.

**수정본 PDF는 CPU 제한으로 미완료**다. 0-byte 파일을 `.pdf.partial`로
보존했고 원래 PDF도 보존했다. 완성된 최종 PNG가 본 작업의 그림 산출물이다.
부모 게시 패키지는 `.pdf.partial`을 완성 PDF로 표시해서는 안 된다.

## 실행과 비용

장소는 ChatGPT sandbox, Python 3.12.14 / NumPy 2.3.5다.

| 실행 | 실제 CPU 초 | 결과 |
|---|---:|---|
| 입력 구조 확인 | 0.824565 | 실제 NPZ/receipt 읽음 |
| 초기 identity 해시 | 0.037554 | 원본 세 파일 MATCH |
| 어댑터 subprocess | 1.367438 | 105,859 상태 준비 |
| 12개 unittest subprocess | 1.892971 | 12 PASS |
| 프로브+첫 PNG/PDF subprocess | 4.196377 | 3 유리수 대조 PASS |
| 저장된 프로브의 범례 수정 | 1.436889 | PNG 완료, PDF CPU-stop |

wrapper CPU와 최종 해시 기록을 포함한 측정 합계는 스냅샷 시점
**9.895912 CPU초**로 10초 작업 한도 안에 있다.
그 이후 추가 수치·그림 실행은 하지 않는다. inner CLI CPU는 subprocess CPU와
중복 가산하지 않았다. 상세 영수증은 `r3o_h_input_implementation.json`과
`r3o_h_input_*_001.execution.json`에 있다.

## 재사용·실패·부모 작업

원본 full tar 309,819,364 bytes, SHA256
`d302fc3680bbaafe39f1f5c840365cc04c9d6718d3e0a3221929a40c4c7d3012`의
Dropbox 전체 readback MATCH는 부모 intake의 완료 근거를 재사용했다.
이 어댑터는 새 원격 readback을 수행하지 않았다.

처음 관측한 0-byte 코드 파일은 부모가 보고한 disk-full write 실패에 대응한다.
복구 후 어댑터/검사의 실제 실행은 성공했다. 수정본 PDF의 CPU-stop은 자원 제한
분류다. 고정 입력·producer·같은-h 허용오차를 바꿔 성공으로 만들지 않았다.

부모가 THEORY/DAG/독립 검토/게시/백업을 처리한다. 이번 작업은 GitHub 및
원격 백업을 수정하지 않았다. 기존 h2 full low-z 153,327-step은 NOT_RUN,
h4의 이미 수행된 8단계 start는 부모 검토 상태를 따른다.
U5 h HOLD_9_FAIL, h2 HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI=false를 유지했다.
글로벌 h/h2/h4 수렴 및 Bianchi/REI/CMB 과학 승인은 없다.

## 재실행 인터페이스

이미 준비된 h trace와 producer_inputs를 재사용할 수 있다. 새 산출 경로를 지정한다.
아래는 부모/Codex용 명령이며 사용자에게 수동 실행을 요청하지 않는다.

```bash
python3 scripts/prepare_r3o_h_history.py --raw-dir research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/producer_inputs --evidence-dir /tmp/r3o_h_adapter_new
OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s tests/trajectory -p test_r3o_h_inputs.py -v
OPENBLAS_NUM_THREADS=1 python3 scripts/plot_r3o_frontiers.py --evidence-dir /tmp/r3o_frontier_probe_new
```

## 정확한 변경·산출 파일

아래 경로는 `/workspace/scratch/afe554957b2e/rec_work` 기준이다.
이 목록 밖의 기존 repo 파일은 수정하지 않았다. 인계 노트, 구현 JSON,
개별 실행 로그·CPU 영수증은 `rec_recovery/r3o_h_input*`에 별도로 보존했다.

- `scripts/prepare_r3o_h_history.py` — 12268 bytes; SHA256 `c5a938c0b37cae5ff8b1ec05099bb420fd2da9a17e719ef047c9192c52224cad`
- `scripts/plot_r3o_frontiers.py` — 8883 bytes; SHA256 `e952d0ca8f290d66ca61a645979a43bbdda1db085c72e2b3bacd2337b6c1b500`
- `tests/trajectory/test_r3o_h_inputs.py` — 7517 bytes; SHA256 `74004e931a004f313353fb92ee345519f9d358aab1b75c9363644dd2d6ca176d`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/FIGURE_REVIEW_KO.md` — 2372 bytes; SHA256 `f83b30a979ec62b5c7ccfcd1ad15c9fff14683a93712d03f2069d608b4a64502`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/FINAL_PLOT_SELECTION.json` — 581 bytes; SHA256 `208ab5c89d07509f4d2e511d2c6213faeb417d992a776bad2a9971d55aed3adc`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/execution.json` — 1174 bytes; SHA256 `6db3adbb09e21b6ebc74803acb7c9f67da3dd5335c6c9848507bc243f602d3fa`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/h_h2_coverage.json` — 4598 bytes; SHA256 `2a52e5ca58a92a41f7ae00fe1486cea75e27d814995a16525d5fe1f5beadc45c`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/plot_revision_002/predictor_memory_seed_response.pdf.partial` — 0 bytes; SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/plot_revision_002/predictor_memory_seed_response.png` — 109830 bytes; SHA256 `519794aec35f4327ced762169865d4fd104be54d679f6bf2f9341f26aed5eb35`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/plot_revision_002/render_execution.json` — 647 bytes; SHA256 `b67928f83bfb62cc6052c457eaaad4c380a27e67256e1ce8de2fca0b342a979d`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/predictor_memory_seed_response.pdf` — 18724 bytes; SHA256 `949c1fb6a18d7ca673b6e7b2a49d24c7bb5e0dcd75ceff79dd370038f83a8655`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/predictor_memory_seed_response.png` — 109923 bytes; SHA256 `143f0da3eab9ccb27c0ed6973e80d75578fbdf3c2d55a7eee146f3aa88bd79c3`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/probe.json` — 5900 bytes; SHA256 `fc565a1c646cfcd9045f11670807c034389adbdb5635130d2d20c16d9f8e9816`
- `research/rec_r3o_grid_frontiers_20261019/frontier_probes_001/result.json` — 1118 bytes; SHA256 `d457cc8dc961a5ef53e5a0581944174f39039c728d5912207b93afb7b32d4e47`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/execution.json` — 1570 bytes; SHA256 `a2b6ab4493303ce79fcda6a66931ce66f1bb80c17724f057d6c5d9e2c28112b9`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/h_state_trace.json` — 2465 bytes; SHA256 `bb9d69284d75f357aaf2a786f573099c888af76e29551653cc557d8239a18d40`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/h_state_trace.npz` — 2262562 bytes; SHA256 `d46fb7eaeb6cc8792c5d929f28953d48684cf1e4f3305f33f6ba4f3393999fd3`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/producer_inputs/independent_integer_z_history.csv` — 497670 bytes; SHA256 `c7c113af50fd49e7937a3bfef15ac2e295fe51cc161e83196bc921e0f02c98ce`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/producer_inputs/independent_source_grid.npz` — 1382904 bytes; SHA256 `12818562014c3f7563d4396d3b499ae9666feef3d8824db8232717325cc0bf15`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/producer_inputs/verification.json` — 5837 bytes; SHA256 `43ccacd3bce28512ee5223ec9d5ff9979c435227d63da5f78e7572a89de478fa`
- `research/rec_r3o_grid_frontiers_20261019/reused_h_trace_001/result.json` — 1749 bytes; SHA256 `46cb4bc4b69e9f8bf774288231faa3ad1daf7208e98ee658329de2e277ebed5d`
