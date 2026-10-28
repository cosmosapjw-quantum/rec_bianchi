# C1 — 실제 입력 baseline과 source identity

C1 mechanical preparation 완료. Root의 단계 게시·capsule·Drive/Dropbox 최종 ACK와 size readback은 별도이며 이 문서는 이를 예측하지 않는다. R1–R10의 실제 완료는 controller가 보고했다. Adapter 구현은 C5까지 대기한다.

## 소유 범위와 관측 provenance

- Owner: cosmosapjw-quantum/rec_bianchi.
- Branch: research/rec-h5-electron-field-20261028.
- Owned subtree: research/rec_h5_electron_field_20261028/.
- Native parent: 29e8427fa02ae089b004bce13c3d29ef663c89b4.
- Controller가 전달한 현 PR146 HEAD: 7a4fe54d97357e687e854aa2659601523ee2e1fe. 이 worker는 원격 ref를 다시 읽거나 쓰지 않았다.
- 실제 HEAD/AGENTS readback은 root가 보존한 coding/C1_HEAD_SNAPSHOT.json을 따른다. Root가 확인한 최신 중앙은66ef9a0147a0573b77e74e151dc280ba2bd4b64c / DAGblobac459abd24d5e6f9b8813d84d2a6fd1afe2a5f87이며 병렬 HE-TANGENT13 변경과 기존 native backlink를 포함한다. 이 worker는 그 snapshot을 덮어쓰지 않았다.
- 요청 executor gpt-6.1-sol; 실제 runtime model-id는 NOT_OBSERVED.

## 복원과 불변 입력

원 native SOURCE ZIP110654069bytes/SHA25694b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c의 앞선 실제 복원·whole-SHA receipt를 재사용했다. 이번 단계는 그 ZIP의 전체 hash를 다시 계산하거나 ZIP을 재포장하지 않았다. 지정한8개 original source/header/table와 capture002의7개 기록·metadata를 원 member에서 byte 그대로 추출했다.8개 native 파일은 기존 INPUT_LOCKS의 byte/SHA와 각각 일치한다.

이미 복원된 thermal_source/inputs/native_path.json을 byte-identical하게 inputs/native_path.json으로 복사했다. 이 파일의 query/geometric endpoint/exact alpha 내용은 C1에서 재계산하거나 source writer와 binding하지 않았다.

inputs/SOURCE_MANIFEST.json은16개 실제 파일의 bytes/SHA256/원 ZIP member 또는 기존 로컬 source 경로를 기록한다.

| 입력 파일 | Bytes | SHA256 |
|---|---:|---|
| inputs/original/HyRec/hydrogen.c | 37471 | 421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b |
| inputs/original/HyRec/hydrogen.h | 7837 | e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba |
| inputs/original/HyRec/hyrectools.c | 6001 | beb97b6cee3b80cf74d58264da7087301865881d266de1c17dd472a08665bb79 |
| inputs/original/HyRec/hyrectools.h | 972 | 537de0362b930d6059725ab51cfb1d0078398ad0a02eb02aae93bef9751d7be6 |
| inputs/original/HyRec/hyrec_params.h | 3764 | cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2 |
| inputs/original/HyRec/Alpha_inf.dat | 132000 | c543c755d99ba8e999450dd5cb486a3ad88d26378da0ccc8363b10418e4832bd |
| inputs/original/HyRec/R_inf.dat | 1700 | ce914f4b552ba55ba00f7916f36b0986f19adfdb638e5aefae91f7b2d05a8112 |
| inputs/original/HyRec/two_photon_tables.dat | 25191 | 93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9 |
| inputs/capture002/CALLS.jsonl | 3899725 | fadd9fc669167a83e7b94f19eaffcd0f8361bb71c3a5593469e249965a78e3e5 |
| inputs/capture002/QSS_WRITES.jsonl | 3970311 | 4f3c0c61f4cf76ac1667cc51f007549e01737f567a2b80feef60667c44499ec8 |
| inputs/capture002/LAST_WRITERS.json | 37680 | ace33861745d20661ef1d83913fdf724d30b1443488c35b760146d3d93428cea |
| inputs/capture002/PARAMETERS.json | 529 | 29fe96ec9c647bbb7311ed4fd8f56a0343b2ac77c15c47e2094e85586a8fe434 |
| inputs/capture002/VARIABLE_SEMANTICS.json | 378 | 8d2c0cfa43312518b0ef6a472b4cbb8e9d3b115e4a9c2201f9d5a06cff9ee03c |
| inputs/capture002/SELECTED_SLOTS.txt | 660 | 2634f5ca294480676a2980688c571bf8629d28aee047e14cbb5a33f7b9562e27 |
| inputs/native_path.json | 2200624 | c76b6794ed9ac028206da113f260e303cc821655a2a68b7e98a5309e5f280bf5 |
| inputs/capture002/WRITES.jsonl | 1149615 | 6de4bc263b0a78fe09cd4cddfdb7fc8fb23792fdab314ea71e7a9d0667203a2a |

전체 입력 payload: 16files / 11474458bytes. Native8개, capture7개, native_path copy1개.

## Phase 및 metadata 단서

CALLS의 저장 phase vocabulary는 H_HE, H_STEADY다. 이는 vocabulary 읽기이며132 final writer의 phase/membership 판정이 아니다. 실제 selected slot metadata는132개/중복0, fsR=meR=1, izH0=18234, nzrt=10961, retained_rows7489, 저장순서channel_then_local_time이다. VARIABLES는 signed departures 허용을 명시한다.

후속 C2/C3/C6/C7는 LAST_WRITERS[slot]과 CALLS/QSS_WRITES의(id,slot)을 결속해야 한다. 이번 C1에서 그 join·132-point input selection·313 query/626 endpoint binding·field 평가는 실행하지 않았다. H_STEADY/He-neutral/xe=xHII/FULL은 frozen primary acceptance 조건으로 남고 C1 metadata가 그것을 대신 검증하지 않는다.

## C3 선택 및 실행 경계

Controller가 선택한 C3는 outside231diag entry prepass + original solve diag0/denom240개 + Schur det1개, point당472 value events다. Extra solve0, point-scoped TLS save/restore, immutable original 보존이다. 아직 observer나 adapter code를 작성하지 않았다.

Required acceptance는 FH512 eps64 S_F와 independent normalized residual4096 eps64이며 bitwise equality는 실제 count만 별도 보고한다. C1은 이 numerical gate를 실행하지 않았다.

Adapter code0, compiler0, table initialization0, new point calls0, scientific binding0, native/full-history/old campaign0, remote mutations0, source ZIP repackaging0. Extraction/hash/metadata의 현재 process CPU는 manifest에 별도 기록하며 science charge로 둔갑시키지 않는다. Parent/tool/unmeasured costs는 UNKNOWN_NOT_ZERO이고 기존 예산·실패는 unchanged다.

Canonical28/88+0, separateREI33/88, reference313/313, physical0/313; physical query/K/M2/defect/L/tube/e0/epsilon/outgoing null; H6/H7OPEN,L4false,REIactivationfalse,AUTO_NEXT_NODE=OFF_AFTER_THIS_SELECTED_UNIT.

## C1 온도 provenance locator 정정

실제 coefficient temperature record는 QSS_WRITES가 아니라 runtime/results/capture002/raw/WRITES.jsonl이다. 이1149615byte 파일을 inputs/capture002/WRITES.jsonl로 byte 그대로 추가했다. Keys는 id,slot,coefficient_TM_eV,coefficient_TR_eV다. QSS_WRITES는 real/virtual/incoming/outgoing 배열 record이며 coefficient temperature를 포함하지 않는다. 기존 native_path.json의 final_writer_coefficient_temperatures와 이 WRITES를 후속단계에서(id,slot)로 결속할 수 있지만 C1에서는 그 binding을 실행하지 않았다. 이는 locator 정정이며 R5 수식·허용오차·예산·원본 ZIP을 변경하지 않는다.
