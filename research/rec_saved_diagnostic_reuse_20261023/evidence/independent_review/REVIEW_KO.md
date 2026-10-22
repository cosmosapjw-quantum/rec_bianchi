# C2 독립 검토

**검토 판정: confirmed. 현재 C2 산출물에서 수정이 필요한 finding을 발견하지 않았다.** 이 판정은 지정된 저장 상태의 수식·코드 대응, baseline 증거와 표현에 대한 것이다. 단계 수용·게시·백업·전역 과학 판정은 부모 작업의 권한과 범위에 남는다.

## 범위와 독립성

검토자는 `/root/diagnostic_c2_review`의 새 native context다. 구현·수식 매핑을 작성하지 않았고, 기대 판정을 전달받지 않은 상태에서 실제 소스·증거를 읽었다. 작성 경로는 `evidence/independent_review/`에 한정했다. 과학 driver를 import하지 않았고 새 IVP, 기존 IVP 재실행, 전체 기존 test suite, 후보 구현, 재귀적 검토를 수행하지 않았다.

`skill_context_used`: physmath-research-loop **1.3.0**의 `SKILL.md`, `STAGE_SELECTION.md`, `CODING_LOOP.md` C2, `POLICY_INTEGRATION.md`, `SUBAGENT_MODE.md`, `EVIDENCE_AND_HANDOFF.md`와 skillquiver `execute-durably`를 실제로 읽고 적용했다. 외부 durable state의 objective·criteria를 읽고 C2만 확인했으며, byte identity·numerical equality·scientific claim을 분리했다.

## 확인한 결과

1. **원본과 입력:** local commit `40f7cf12b509377350e9a16da461e8ef97cdcb62`, whole tree `a136dea6c4ade8c6be442843800d0eb1458caa5f`를 확인했다. 기존 tracked source diff는 검사 전후 비어 있었다. 40개 원래 NPZ의 바이트 해시·크기·raw-state shape·유한성·증가하는 x를 확인하고, 8개 collision reference와 inherited source lock을 대조했다. runtime 및 collision identity를 파일 해시와 canonical payload로 독립 재구성했다.

2. **선택과 exact 비교:** endpoints, 온도 peak, 네 residual/backreaction 최대점, fit/underflow 경계 양옆, 최대거리 채움과 작은 index tie-break를 독립 구현으로 재구성했다. 모든 선택 index·reason·raw-state/x hash가 일치했다. 사례당 gather 16개 배열과 collision 58개 점별 배열·정적 metadata가 원래 제품과 dtype/shape 및 C-order 바이트까지 일치했다. 58개는 원본 harness의 34개 점별 배열에 정적 이름·단위·availability 등의 검사를 추가한 수다. 전체 격자 누적값을 부분집합 누적값과 비교하지 않았다.

3. **물리 소유권과 장부:** 실제/Planck branch의 독점 선택, UV power, particle/electron owner, gas-energy와 work, 단위 환산, CE charge-state target 및 CI particle forcing을 독립 산술로 확인했다. 두 gas source는 각각 kinetic+ion과 absorbed−escape+Compton의 정의로 정확히 복원되었다. 512점 중 **491점**에서 두 합계가 반올림 수준으로 다르며, 최대 네 저장소 잔차는 **3.8820046920465465e-16**다. 한 합계를 다른 합계로 복사한 source 경로는 발견하지 않았다. opposite bath가 photon/Einstein RHS에 적용되지 않는 한계도 보고서에 유지되어 있다.

4. **mask와 부분격자:** unavailable과 continuation/underflow의 구분 및 source domain을 대조했다. 사례당 13개 energy와 6개 forcing의 구간 mask를 endpoint AND로 재구성하고 trapezoid 적분·누적값을 부분격자 자체에서 확인했다. 이는 retained endpoints에 대한 검사이며 구간 내부나 전체 1025점 결과의 인증이 아니다.

5. **프로파일:** 사례당 18개 실제 호출 수 assertion이 매핑과 일치했다. geometry 7회, number network 3회, thermal source 2회, prepared moments 7회, Mao factor 26회/점이며 collision provider 1회/점과 retained integral 19회/격자다. 각 프로파일의 self-time 합과 raw caller graph를 독립 대조했다. 세 비용 영역은 서로의 descendant가 아니므로 이 경우에 한해 cumulative time의 합산이 정당하다. 총 profiler self time **5.399687069 s**와 열원 **38.9614%**, geometry **24.2282%**, 원자망 **19.9326%**, 나머지 **16.8778%**가 재현되었다. 중첩된 나머지 함수들의 cumulative time을 전부 합산하지 않았다.

6. **집계·보고서·그림:** 원시 반복에서 48개 plotted latency, 281개 CSV profile 행, median과 probe 범위를 재구성했다. nominal probe는 **3.6650065–19.1017393 ms/상태**, refined는 **3.8125854–5.2155692 ms/상태**다. 보고서는 지연 원인을 확정하지 않으며 physical branch/refinement 또는 후보 speedup으로 확대하지 않는다. V1/V2 plot data는 바이트가 같고 최종 V2 PNG 두 장을 `view_image`로 실제 확인했다. 범례, 단위, 로그 축, 8개 사례, 세 반복과 범위가 겹침·잘림 없이 읽힌다. 가로선이 신뢰구간이 아니라는 설명도 적절하다.

## 실제 실행 증거

| 검사 | 실제 명령 | exit | 내부 wall s | 외부 tool wall s |
|---|---|---:|---:|---:|
| 저장 배열·물리·호출 수 | `python research/rec_saved_diagnostic_reuse_20261023/evidence/independent_review/check_saved_arrays.py` | 0 | 9.449968626 | 9.878932106 |
| raw profile→CSV→plot binding | `python research/rec_saved_diagnostic_reuse_20261023/evidence/independent_review/check_final_artifacts.py` | 0 | 0.535527490 | 1.238703881 |

실제 명령과 verbatim 출력은 `COMMAND_001.json`, `COMMAND_002.json`, 세부 결과와 전체 확인 해시는 `SAVED_ARRAY_CHECK.json`, `FINAL_ARTIFACT_CHECK.json`에 있다.

초기 schema 탐색에서 검토자가 `collision__energy_power_names`라는 존재하지 않는 이름을 요청해 exit 1이 한 번 발생했다. 실제 이름 `collision__process_names`를 읽은 수정 명령은 exit 0이었다. 이는 검토자 discovery typo이며 대상 오류나 red/green repair가 아니다. 해당 실패는 어떤 criterion에도 통과 증거로 사용하지 않았고 `REVIEW.json`에 분리해 보존했다. canonical check와 이 ancillary 숫자 탐색들의 외부 wall 합은 **22.533737390 s**다. target repair/recheck는 필요하지 않았다.

## 최종 확인한 핵심 파일 해시

| 파일 | SHA256 |
|---|---|
| `C2_SCOPE.md` | `b56e037456278b1b10979cbb94bee1a57db435f5dbb188eb405b36b50fa3e0a3` |
| `FORMULA_CODE_MAP_KO.md` | `c7a35e82ba1a77d26debd7b53baa4f231b45894cd1052639d224895fcff28330` |
| `REPORT_KO.md` | `058b524cfb907169efee7786a5e5908c152f2043306405552e7973b92a82c577` |
| `NEXT_STAGE_C3.md` | `37fe366dbb610a006d663a98d5dcde1117a88ca94ae94348f0b63580a1fbfa80` |
| `FIGURE_CAPTIONS_KO.md` | `4320c0069f0101d0adf1e4528189821a939a585d093cd70928256a4ed5df37df` |
| `code/profile_saved_diagnostics.py` | `ca8d4f164def4a6cc2814a7de133cccb3f9c465f8265ec7744806b0152374570` |
| `code/probe_timing_variation.py` | `6a68acdc14523c19858547786242954cffeac4b088b6020295a09116d8c1971f` |
| `code/summarize_profile.py` | `6936ffe9c869d03dda3822312a47ba3771090c33d9c21b1a076be29583a4cc9e` |
| `code/render_latency_v2.py` | `fdbe8b71a6f5546b062c9bfce371b2b6ecda31b84f9326640817d52e8f89c516` |
| `figures/v2/baseline_latency.png` | `675884a40d8362883ded02c498762ecdf0da77283546fd10fc01e0eb18e8cc09` |
| `figures/v2/baseline_cost_attribution.png` | `3def07bb53ffbeacc02c405e773785aa06bfdfa66cf065cc4b86b6e2800408ca` |

## 남은 경계

C3 설계, 후보 구현, 모든 16,170 diagnostic 행과 13,176 collision 행의 동등성, paired speedup은 실행하지 않은 상태로 남는다. physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, REI false, U5 CLOSED가 유지된다. 게시·백업·delivery criterion은 이 검토가 새로 확인하지 않았다. 부모는 현재 confirmed 결과를 C2의 지정된 evidence criteria에 적용하고 별도의 실제 delivery receipt로 마무리하면 된다.
