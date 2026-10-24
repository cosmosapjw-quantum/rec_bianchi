# 첨부 자료 읽기 전용 intake

## 범위와 현재 상태

지정된 01·04·05·07·08 txt와 03·09 sh의 전체 텍스트를 읽었다. 셸은 source/실행하지 않았다. root에서 `git status --short --branch`는 `not a git repository`를 반환했다. 따라서 이 workspace snapshot을 현재 branch/HEAD/clean checkout이라고 표현하지 않는다. `WORKSPACE_FILES.txt`는 현재 일반 파일 경로 목록이다. root가 Git 원본과 대조한 중앙 copy `central_admission_work/AGENTS.md`를 읽고 별도 metadata/hash를 남겼다. 이번 intake는 source inventory이며 구현/과학적 검증 판정이 아니다.

## 자료별 역할과 현재 요청의 우선순위

| 자료 | 실제 내용 | 이번 작업에서의 취급 |
|---|---|---|
| 01 | htt/bass low-ell solver 전체 감사 템플릿, 8개 역할, geometry/transport/hierarchy/statistics/optimization readiness | 범용·이전 scope 참고. 현재 built-in 1.0 요청의 범위를 넓히거나 8-agent 실행을 강제하는 권한이 아님 |
| 04 | contract와 code path를 먼저 복원하고 제한된 가설·최소 patch·dual audit·plot adversarial 검토 | 연구 설계 참고. 자동 patch/실험 실행 또는 모든 baseline 재실행 허가는 아님 |
| 05 | DAG 상태 복원, 다음 단계 한 개 선택, dual audit와 plot 검토를 포함한 CMB 범용 executor | 현재 root가 다음 유한 unit을 고정하기 위한 참고. 과거 stage 전체 replay나 새 process gate를 추가하지 않음 |
| 07 | 잔여 figure overlap/legibility 미세 수정 | 향후 실제 figure 검토에 한정해 참고 |
| 08 | figure semantic consistency·축소 가독성·첫 repair 검토 | 향후 figure claim 해석에 참고. intake에서 plot 생성 의무로 취급하지 않음 |
| 03 | `/mnt/data/rust-1.94.1-prefix`를 PATH/LD_LIBRARY_PATH에 추가 | 과거 환경용 source script. 현재 설치가 있다는 증거가 아니며 실행하지 않음 |
| 09 | pip 설치, marker 생성, cargo test/maturin build/wheel install, import와 광범위 pytest | 과거 복구 script. 과거 520/44 counts는 현재 PASS가 아님. 실행/설치하지 않음 |

현재 명시된 요청은 broad survey 후 built-in 1.0 범위의 full research/coding loop와 stage backup이며, 이 executor에게 부여된 작업은 그중 유한 read-only intake뿐이다. 전체 사용자 constraint 원문이 이 하위 agent에게 전달된 것은 아니므로 built-in 1.0 세부 물리 convention/tolerance는 추정하지 않았다. 다음 unit의 물리·수치 판단과 허용 실행량은 root Astra가 고정한다.

현재 중앙 AGENTS는 개인 단일 연구자 trust model, 과학적 identity·재현성·회복을 위한 비례적인 controls, byte identity와 scientific validity의 구분, 유한 review/repair, Astra framing 및 독립 판단과 mechanical executor의 분리를 요구한다. 첨부 안의 일반 workflow가 이보다 오래된 보안·fingerprint·전이 승인·전체 replay 관행을 담더라도 현 명시 scope의 추가 blocker로 승격시키지 않는다.

## REC 관련 exact source 후보

archive `14-bianchireview87.tar-1-.gz`의 member 이름은 다음과 같다. 파일을 설치하거나 코드를 import/실행하지 않았으며 작은 선택 member는 archive reader로 source text만 읽었다. 원문과 hash는 `SELECTED_MEMBER_TEXT.json`, `SELECTED_MEMBER_METADATA.json`에 있다.

| Exact member | 확인한 interface / 다음 source intake에 유용한 지점 |
|---|---|
| `./bianchi/thermo/history_api.py` | `IonizationHistory`, `TabulatedHistory`, `SahaHistory`, `BuiltinPeeblesHistory`, `validate_history`, `n_H_cm3`, `thomson_rate`, `optical_depth`; n_e/n_H와 redshift domain, matter temperature, history injection interface |
| `./bianchi/thermo/recombination.py` | `saha_xe`, `peebles_xe`, `optical_depth_and_visibility`, `saha_all_species`, `helium_ionization`, `xe_with_helium`, `peebles_rate_regime`; `scipy.integrate.solve_ivp` 사용 source 확인만 함 |
| `./bianchi/thermo/temperature.py` | `temperature_of_ell`, `temperature_redshift_isotropic`, entropy/neutrino-temperature helpers |
| `./tests/test_b2b_history_api.py` | built-in injection equivalence, tabulation/range guard, single source Thomson rate의 기존 test definitions |
| `./tests/test_q19_history_wiring.py` | time-dependent rate wiring, optical-depth relation, model/lcdm H, range/clamp rejection, event/fast/reference path와 baryon velocity forwarding의 기존 test definitions |
| `./tests/test_m9_recomb.py` | Saha/Peebles/visibility/drag/helium/radiation-H/escape-rate saturation의 기존 test definitions |

이들은 attached older solver의 source 후보이며 현재 REC native outgoing history adapter와 동일 구현·물리 admission이라고 간주하지 않는다. 내장 Peebles와 external history protocol은 대체 가능한 interface를 갖는다는 source 구조이지, HyRec/CosmoRec급 정확도를 확보했다는 증거가 아니다. 여기서 시험을 재실행하거나 결과를 새로 주장하지 않았다.

추가 index 후보: `./scripts/codegen_thermo_tables.py`, `./bianchi/thermo/dof.py`, `./bianchi/thermo/relics.py`, `./_rustcore/src/thermo/{fd.rs,dof.rs,mod.rs,dof_table.rs}`. Rust offline bundle 17에도 `src/thermo/`가 있다. vendor의 Windows FileHistory는 recombination history가 아닌 검색 false positive다.

## 첨부 안 AGENTS와 적용 경계

실제 workspace에서 일반 경로로 확인된 AGENTS는 중앙 copy다. archive 11의 root `AGENTS.md`는 전 patch metadata/version 갱신·광범위 cargo/maturin/unittest gates를 요구하는 과거 lowell automation kit 규칙이다. archive 12의 `BASS_v1_BACKGROUND_HIGHL_HARNESS_PROJECT_SOURCE_BUNDLE_20260803/01_CANONICAL_HARNESS/BASS_v1_background_highl_harness/AGENTS.md`는 homogeneous background/finite angular hierarchy scope와 여러 전이 lock·fresh fingerprint 규칙을 담는다. 둘은 archive member text이며 현재 작업 디렉터리에 펼쳐져 적용되는 AGENTS가 아니다. archive 17의 `vendor/zerocopy/AGENTS.md`는 제삼자 vendor-local 파일이며 이번 REC unit 정책이 아니다. inherited security/process demands 및 일괄 replay를 실행하지 않았다.

## Archive와 참고문헌

8개 관련 zip/tar의 full member index를 `*.members.txt`로 저장했다. Rust toolchain 06은 192,287,020 bytes, generic cargo vendor 15는 112,967,859 bytes이며 full hash와 설치/대규모 추출을 하지 않았다. xAct 13은 15,613,945 bytes로 파일 metadata만 기록했다. 선택되지 않은 archive body/source는 읽지 않았다.

18에는 Ellis Relativistic Cosmology, Kinetic Theory, Kolb–Turner The Early Universe, cosmology lecture notes, relativistic fluid/kinetic texts가 있다. 19에는 `1501.04288v1.pdf`, `mnras0380-1387.pdf`, `1-s2.0-S0370157308000884-main.pdf`, `A_1001921711071.pdf`, `PhysRevD.62.043004.pdf`, `9904408v2.pdf`, `9804316v3.pdf`, `1810.06293v1.pdf`가 있다. 이름만 index했으며 논문 title/결론은 추정하지 않았다. 다음 root source intake가 필요한 exact 문헌을 고르면 그때 관련 내용만 읽을 수 있다.

## 종료

새 code implementation, scientific run, solver import, probe, plot, bootstrap, dependency installation, clone/worktree, large archive extraction, external mutation은 모두 0. 생성물은 지정 survey 경로의 읽기 전용 intake 기록뿐이다. 다음 scientific unit과 stage backup 경로·시점은 root가 정한다.
