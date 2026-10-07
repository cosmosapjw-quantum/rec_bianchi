# REC pure-H Peebles pointwise 구현 — 2026-10-04

선택한 `rec_bianchi` branch `forward/rust-he-sources-20260922`, commit `5694a5c7ef487adc969f38ae9112b796396216ca`의 정확한 `rust/rec_microphysics` crate에 `hydrogen_peebles` 모듈을 추가했다. 기존 He/frame/screen API는 수정하지 않았다. 실제 게시 시 `coding/rec_microphysics`의 소스 변경을 저장소의 `rust/rec_microphysics`로 이식한다. `target/`은 게시·백업 대상이 아니다.

## 구현 범위

- 순수 H, proper SI 수밀도 `n_H [m^-3]`, `alpha_B [m^3/s]`, 시간률 `[s^-1]`.
- `x_e=x_p`, `x_1=1-x_p-x_2`; `x_2s=x_2/4`, `x_2p=3x_2/4`.
- 임의 명시적 입력률의 retained-shell 연속·바닥상태 flux, 질량보존 RHS.
- `beta_shell=beta_P/4`, `D=(Lambda+3R_alpha)/4`와 안정적인 scaled `C=D/(D+beta_shell)`.
- 실제 ground abundance를 입력한 순간 QSS target, **고정 R_alpha 모형에 한정된** finite-population QSS.
- 정확한 pointwise closure defect와 redshift 부호 변환.
- exact source profile `HYREC2_TLA_2020_PEEBLES_FUDGE1`: upstream commit `09e8243d0e08edd3603a94dfbc445ae06cafe139`의 PPB formula와 반올림 상수 identity를 보존한 독립 수식 구현. upstream 원문 C 소스는 복제하지 않는다.
- 별도 `PhysicalConstantsSI` 입력 경로. SI 상수를 재계산한 profile을 HYREC의 반올림 상수 profile과 혼합하지 않는다.

native source adapter는 `T_m=T_r`만 받는다. theory 문서에 있는 two-temperature 일반화는 이 함수의 실행 증거가 아니다. `H>0`, `x_1>0` 조건 밖에서는 optically thick expanding-Sobolev adapter가 오류를 반환한다. optically thick 조건 자체를 모든 입력에서 입증한 것은 아니며 물리적 적용 시 외부 admission이 필요하다.

## 중요한 비교 의미

`peebles_rhs`는 supplied rates를 고정하고 thermal inverse의 `x_1`을 `1-x_p`로 놓는다. 완전한 standard Sobolev Peebles와 비교할 때는 source assembler에도 `RetainedState { xp, x2: 0.0 }`을 주어야 한다. `x_2>0`의 retained source를 조립하면 `R_alpha∝1/x_1`가 달라진다. `closure_defect`는 양쪽에 같은 순간 `C`를 사용하여

`retained dxp − collapsed-inverse RHS = −(1−C) dx2 − C beta_P exp(−E21/kT) x2`

를 검증한다. 전체 collapsed model에서 C까지 재계산한 차이는 별도의 `C(actual ground) − C(collapsed ground)` 항을 더해야 한다. 이 함수를 self-consistent finite-shell Sobolev QSS root solver라고 부르지 않는다.

finite retained thermal equilibrium는 `x_p²/(1−x_p)=S_rate/(1+4B)`이며 `S_rate=beta_P B/(n_H alpha_B)`, `B=exp(−E21/kT)`다. 일반적인 collapsed Saha는 `x_2`를 무시할 때의 근사다. synthetic `B=0.2` 시험으로 둘의 차이를 검출했다.

continuum flux와 ground flux는 별도다. `chi1 dxp + E21 dx2`의 binding-energy bookkeeping을 시험했지만 이를 가스 가열률 또는 광자 에너지 spectrum으로 제공하지 않는다. 외부 prescribed thermal bath와의 에너지 교환을 실제 열·광자 소비자가 이어받아야 한다.

## 실행

Rust 1.94.1, edition 2024, 외부 dependency 없음. 저장소 root에서:

```sh
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --offline --locked --test hydrogen_peebles
cargo test --manifest-path rust/rec_microphysics/Cargo.toml --offline --locked
cargo build --manifest-path rust/rec_microphysics/Cargo.toml --offline --locked --example peebles_probe
printf '3000,250000000,5e-14,0.1,0\n' | rust/rec_microphysics/target/debug/examples/peebles_probe source
```

독립 검산용 probe는 stdin CSV를 받고 stdout CSV를 낸다. 빈 줄과 `#` 주석 줄은 무시한다. header 없는 입력을 쓴다. malformed/nonfinite/domain 오류는 stderr와 exit 2를 반환한다.

| 모드 | 입력 열 |
|---|---|
| `source` | `T_K,nH_m3,H_s,xp,x2` |
| `frozen` | `nH_m3,alphaB_m3_s,betaP_s,Lambda_s,Ralpha_s,b_Lya,xp,x2` |

출력은 alpha, Ralpha, betaP, beta_shell, D, B, C, x1, 두 flux, 세 RHS, supplied-rate collapsed Peebles RHS, fixed-ground QSS target, 직접/분해 closure defect다. header가 정확한 열 이름을 제공한다. binary64 점 계산이며 underflow는 0으로 남기고 인위적 floor를 추가하지 않는다. 재결합 계수의 외부 정확도 범위는 이 구현 시험으로 인증하지 않는다.

## 실제 검증 기록

- 원본 crate 사본에서 새 API import가 `E0432`, exit 101로 실패하여 missing implementation을 확인했다. `BASELINE_GAP_LOG.txt`.
- 추가된 20개 targeted tests PASS: factor-4/factor-3 오류 대조, finite-population/Saha 구분, off-shell defect, conservation, source fixture, SI 변환, domain, nonfinite, C 극한, redshift 부호.
- 통합 crate 108 tests PASS: 기존 forward 76 + frame 8 + screen 3 + doctest 1 + 새 H 20. `FULL_CRATE_TEST_LOG.txt`.
- probe build 성공. 외부 mpmath/original-C 대조는 루트 연구 패킷의 별도 검증 결과를 따른다.
- recovered toolchain에는 rustfmt가 없어 formatter 검증은 수행되지 않았다. 과학적/컴파일 검증 실패가 아니다.

실제 REI call-site 연결, matched cosmological history, 온도·광자 방정식, 모든 Bianchi 형식, 엄밀 구간 remainder는 이 구현의 완료 주장이 아니다.

## 외부 원본 C 기준식의 재현

`fetch_upstream_reference.py`는 exact commit의 `hydrogen.c`, `hydrogen.h`, `hyrectools.c`, `hyrectools.h`, `energy_injection.h` 다섯 파일만 외부 cache로 가져온다. SOURCE_LOCK과 UPSTREAM_C_BUILD의 크기·SHA-256을 literal source lock과 교차확인하고, 내려받은 바이트가 모두 맞아야 로컬 probe를 빌드한다. 기존 cache가 다르면 덮어쓰지 않고 실패한다. 공개 열람 가능성과 재배포 허가를 동일시하지 않으므로 upstream 원문은 패킷에 포함하지 않는다.

패킷 root에서 다음과 같이 실행한다.

```sh
python3 coding/fetch_upstream_reference.py --dry-run
python3 coding/fetch_upstream_reference.py --cache /tmp/rec-bianchi-hyrec2-09e8243 --output /tmp/rec-bianchi-hyrec2-09e8243/hyrec_tla_probe --report evidence/UPSTREAM_C_REPLAY_LOCAL.json
```

이미 원문 cache가 있으면 `--offline`을 추가한다. `--source-lock`, `--build-evidence`, `--driver`로 경로를 명시할 수 있다. `--cc`는 compiler 실행 파일 경로다. shell 문자열을 실행하지 않는다. GCC/호환 compiler와 `--gc-sections`를 지원하는 linker가 필요하며 `-std=gnu11`로 upstream `M_PI` 사용을 보존한다.

이번 환경에서는 기존 원문 cache를 사용한 `--offline` 경로의 checksum 검증과 재빌드가 실제 exit 0으로 끝났다(`evidence/UPSTREAM_REPLAY_HELPER_CHECK.json`). HTTP 다운로드 분기는 이번 helper 시험에서 재실행하지 않았다. 이 helper는 원문 identity와 build만 확인하며 수치 parity·과학적 admission은 별도 검증기 책임이다.
