# 보존된 메타데이터 snapshot

기존 조사에서 반환된 GitHub, Dropbox, Drive, Library 메타데이터를 허용된 필드만 남겨 ID별 중복 제거했다. JSONL 파일은 각각 4 MiB 미만이며 출처 collection을 기록한다. 범위·페이지 완결성·중복·실제 행 수와 각 파일 SHA-256은 SUMMARY.json을 따른다. 관측은 서로 다른 시점의 snapshot이다.

이 목록은 모든 과학 내용이나 archive bytes를 읽거나 검증했다는 뜻이 아니다. Drive 폴더 목록 응답에는 완결 신호가 없고 파일의 경로·크기·수정시간 등 일부 필드는 원 응답에서 제공되지 않았다. signed URL, 커서, 토큰, 본문, 계정과 공유 정보는 포함하지 않았다. 과학 실행, 원 ZIP 수정, 원격 쓰기 없음.
