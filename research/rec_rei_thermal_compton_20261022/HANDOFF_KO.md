# THERM02 재개 계약

## 현재 연구 단위

REC Draft [PR125](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/125),
branch `research/rec-rei-thermal-compton-20261022`. PR120 위에 쌓은 독립 단위다.
과학 계약·코드·8개 새 IVP·3개 유한 비교·그림·독립 검토가 완료되었다.
최종 Git/backup identity는 `delivery/`의 실제 receipt와 PR 최신 반환을 읽는다.
이 문서가 자신의 commit hash를 미리 지정하지는 않는다.

과학 결과 commit은 `407a280aff51abefc10374cb6e21c4224140328c`다. Stage C의
닫힌 ZIP은 28,138,141 bytes, 181 payload이며 SHA-256은
`b4ebbc130c4626973f3b6ed1bef372a299678756bac708107dc92c7a3842d649`다.
Dropbox whole-GET/전체 SHA-256/ZIP CRC/181 payload 검증 PASS,
Drive upload ACK 및 metadata size 일치 PASS이다. Drive whole-byte는 NOT_RUN이다.
이 ZIP 이후의 delivery receipt와 최종 DAG는 metadata commit으로 별도 게시한다.
ZIP 내부 manifest에는 업로드 후 생성되는 자신의 provider ACK를 소급 삽입하지 않는다.

`FROZEN_CONTRACT.md` SHA-256:
`076a97a621d2bdc55eb24859bd122792ac47c32d320458e7d97ff0836d2f4169`.
Scientific kernel SHA-256:
`599be84fabe9bdc904fdcda46e685f2fcaffa5985ba72dcabcd1fa5cb97a51db`.
Runner SHA-256:
`a7fd5f599b05dcec3f0c1b1a78a3de144f7d40ebf9a1db25a60b4c5b13402e4d`.

## 실행과 결과

5 nominal compact34 + 2 tight34 + 1 full63 oracle = 정확히 8개.
z20→2, 193 saved nodes, T0=1000 K, 5–60 eV GL4 continuum.
`python -u code/run.py --run` exit 0; new8, cached0, old-ODE0.
누적 실행·진단·저장 시간 92.951497908 s. No additional science execution is needed.

Split Mao off/hot/Planck의 z=2 T는 6573.376838/5609.584328/5610.699960 K.
Planck−hot의 최대 |ΔT|=7.194733 K. 최대 normalized energy residual
3.7671763347e-7 < 3e-6. hot/tight, Planck/tight, Planck/full63 모두 PASS.
이 유한 비교에서 Planck−hot shear/matter/neutrino stress 차이는 분해되지 않는다.
Photon/radiation/total, T, xe, fractions, tau의 차이는 두 관측 refinement를 넘는다.
Global error bound나 완전한 물리 closure를 뜻하지 않는다.

독립 검토: `PASS_SCOPED_THERM02_WITH_VISUAL_REPAIR`.
원자료 계산 1회, 과학 module/RHS/ODE/old suite 0회. 3개 최종 PDF 직접 시각 확인.
11 plotting CSV는 실제 raw와 정확히 대응하며 표시 수정 전후 값이 같다.

## 그대로 재사용할 완료 근거

REC119 `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`: 125main+1control=126.
REI220 `8be7533cc97b3302bf42608699d6e8313ed6af8a`: 127main+2oracle=129, 62→33.
이 둘의 cohort·행·계수·실행 수를 합치지 않는다. 원래 REI 첫 실패 raw는
역사적으로 local-only였다. 새 백업으로 그 과거 범위를 소급 변경하지 않는다.

REC126/REI129/warm729, THERM01(PR120)8, PR121 restart8, PR124 Compton restart8,
THERM02(PR125)8 및 다른 완료 계산을 다시 실행하지 않는다. PR124의 5–200 eV,
z7.963732801243163→2, 109-node, full63/logT cohort와 이번 5–60 eV compact34
cohort를 분리한다. 동일 입력 성능 비교가 없으므로 speedup을 주장하지 않는다.

## 가장 이른 열린 물리 단계

`NEXT_DAG.json`의 N1/N2 source-provider contract를 0-ODE로 먼저 구성한다.

- N1: Li final charge/state/energy partition. 정확한 resonance/continuum source,
  energy grid, channel cross sections, branching, secondary/Auger electrons,
  escaped photons, ionic potential 및 단위와 threshold를 고정한다.
  Total cross section을 final ionic yield로 대체하지 않는다. 현재 필요한
  정확한 table은 `MISSING_EXACT_INPUT`이다.
- N2: 실제 grey field의 recoil/induced spectrum 및 일치하는 radiation collision/
  Einstein backreaction. External Planck reference와 passive bath debit은 이
  실제-field closure의 대체 입력이 아니다.

먼저 source가 지지하는 식과 number/charge/energy owner를 정하고 유한 수용
기준을 고정한다. 그 다음 영향받는 adapter/kernel만 구현한다. 새 코드 검증이나
작은 계산이 필요하면 해당 새 의존성에만 배정하며 완료 cohort 반복을 요청하지 않는다.

## 유지할 전역 상태

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.

현재 계산은 21-population conditional atomic/thermal test-fluid 모델이다.
이번 단위에서는 T를 진화시키고 UV는 prescribed다. 과거 REC/REI의 prescribed
T/UV 결과를 바꾸지 않았다. 전체 핵반응망·완전한 열역학적 폐쇄로 표현하지 않는다.
