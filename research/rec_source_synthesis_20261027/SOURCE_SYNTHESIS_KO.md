# 최신 자료 종합 — R2

## 현재 위치

2026-10-27 KST 조사에서 관련 10개 저장소의 1,380개 branch ref와 여섯 과학 저장소의 열린 PR 844개를 전수 열거했다. 최신성과 관련성이 있는 고정 원문을 읽고 19개 선택 원문의 Git blob을 대조했다. 모든 과거 브랜치의 raw payload를 다시 읽었다는 뜻은 아니다. 목록, 선택 근거와 읽기 범위는 `survey/repositories/`에 있다.

최신 작업 원 DAG는 **32/88**, shared 중앙 권위본은 **27/88**이다. 검토된 27개 기준 집합에 HE-EXP-SPECIES, REC-EXP-SPECIES, REC-EXP-EXTERNAL, REC-EXP-SPECTRAL, REC-FIELD가 추가됐다. REC-COUPLED는 부분 성과다. 정확한 ID와 여섯 판정 규칙은 `survey/repositories/DAG_COUNT_RECONCILIATION.json`에 있다. 이 합성에서 새로운 완료 노드는 0개다.

## 새 자료가 바꾼 결정

1. **GEO01 전달 복구.** Git에서 빠져 있던 REC-HISTORY-GEO01의 S2/S3를 Dropbox에서 직접 복구했다. S2의 230개와 S3의 30개 manifest 항목이 일치한다. 검토된 게시 payload 111개는 110개 UTF8 소스와 이미 존재하는 원 history blob 한 개다. 제어된 shear의 17,528 ordinary roots, 96 Decimal roots, 다섯 matvec와 독립 검토를 재사용한다. 당시 미완료 Git·Drive 전달을 이번 합성에서 완료한다.
2. **HD 조사 재사용.** 최신 REI의 source-resolution, successor-precision, repair-finding 세 기록은 원 35 Hz gate를 보존한다. 기본 CDMS .cat/.egy 출력 정밀도만으로 이 gate를 보증할 수 없다. 같은 fit의 충분한 정밀도와 state/centroid 대응이 필요하다. 공식 CDMS v2 archive 경로를 새로 찾았지만 일곱 payload는 HTTP503으로 회수되지 않았다. 같은 요청을 반복하지 않고 고정 자료의 joint thermal inconsistency를 정량화한다.
3. **H5 실제 입력 범위.** GEO01은 원 source의 고정 chart 전파를 제공한다. REI 최신 순간 source는 z=2.479이며 원 H5 z≈1100 source와 다르다. VIGILODE V6도 point binding까지이고 whole-tube certificate는 열려 있다. 읽은 신규 자료에는 실제 H5 proof packet이 없어 coverage 0/313과 physical epsilon null을 유지한다. 다음 실행은 원 native 선형 history의 knot-crossing remainder를 정확히 구성한다.
4. **중앙 관찰 합성.** 최신 REI 작업 SHA ee94bef8에는 다섯 완료 노드와 REC-COUPLED 부분 성과가 있으나, 별도 PR232의 HD/H5 구현 관찰은 빠져 있다. 최종 중앙 draft에는 새 작업 결과와 이 관찰을 함께 적용하고 모든 기존 88개 contract·다른 owner 결과를 보존한다.

## 백업과 대화 조사 범위

Dropbox REC 날짜 폴더 180개, REI 연구 백업 181개, BASS dossier 3,428개는 terminal pagination까지 열거했다. 관련 작은 인계·receipt를 먼저 읽고 여섯 필요한 archive를 실제 복구했다. GEO01 S2와 HD/H5 portable의 각 payload SHA/size까지 확인했다. Drive는 REC 31개와 REI 연구 백업 225개 등을 열거했으나 BASS dossier 조회는 1,000개 API 한도와 cursor 부재로 부분 조사다.

다른 대화 검색은 실제 `personal_context_search`가 현재 대화에서 이용 불가라고 반환했다. 따라서 대화 전체나 미노출 Drive 파일에 대한 전수 열람을 주장하지 않는다. 사용자의 재업로드를 요구하지 않고 접근 가능한 Git·백업·인계 원문을 직접 종합했다. 자세한 범위·오류는 `survey/backup_context/ACCESS_AND_COVERAGE_LIMITS.json`에 있다.

## 원전과 도구

SciSpace의 자연어 문헌 검색, Exa의 공식 출처 검색·읽기, 원 제공자의 LAMDA 다운로드를 수행했다. LAMDA는 원 2,289 bytes/hash와 일치한다. 공식 형식 문서는 level energy와 부가 frequency의 역할을 구별한다. CDMS의 실험 주파수 병합 설명은 가능한 메커니즘이지만 실제 HD row-level 자료를 확보하지 못했으므로 일곱 실패의 확정 원인으로 채택하지 않는다.

H5 관련 Neumaier의 residual/tube theorem과 reconstruction 원전을 읽었다. 실제 native `hydrogen.c::interp_Dfnu`는 두 점의 선형 보간이고 strict causal endpoint를 요구한다. 다음 수학 작업은 이 실제 표현의 기울기 점프를 포함하는 Peano identity다. 문헌과 새 유도는 원 source의 물리 defect·tube·initial-error 수치를 대신하지 않는다.

완료 계산, 원 실패, 기존 예산과 미측정 비용을 모두 재사용한다. Source read, 수학적 유도, 구현 검사, 물리 승인, 외부 전달은 각각의 근거로 판정한다.
