# Git 게시 identity와 복원

일반 Git push는 이 실행환경의 Git 자격증명 부재로 exit128이었다.

    fatal: could not read Username for 'https://github.com': terminal prompts disabled

동일 요청을 재시도하지 않고 이미 연결된 GitHub의 Git-data 경로로 별도
branch에 게시했다. 소스/증거 tree를 먼저 재구성하여 원래 Git tree SHA와
정확히 일치함을 확인했다. GitHub가 만든 commit의 metadata는 로컬 commit과
다르므로 두 commit SHA를 같은 것으로 쓰지 않는다.

| 역할 | 실제 로컬 commit | GitHub 게시 mirror | 동일한 tree |
|---|---|---|---|
| 실행 소스 | 7eb64cb8d65c1fa22f49c019f3c8ce4fb1d22bdc | 7a3bbc1fbdb2cf53810225ae6fd5ffb41a829b36 | 09a39358a7da53f467fb4d889157174d1d40eaa8 |
| 검토·증거 | 33f0178705eb9aaaf49d24587ce5f89970896211 | ed5ad886ca66858909739ffecac779bdf9af2f62 | cfa76a168b5d41fdc7da9cf4b12c832b22a17ae9 |

원래 직접 부모는 양쪽 모두 PR77의
`4125f7f39b29b710ad6ca673520ae46a426b564f`다. 증거 commit은 각각 해당
실행 소스 commit을 부모로 가진다. 게시 metadata 차이는 새 과학 실행이
아니며, 어느 GitHub mirror에서도 시험을 다시 실행했다고 주장하지 않는다.

마지막 게시 자식은 이 설명·publication receipt·원래 로컬 chain bundle과
갱신된 이 디렉터리 manifest만 추가한다. 그 자식의 tree를 위의 실행 tree나
증거 tree와 혼동하지 않는다.

원래 두 commit은 [ORIGINAL_CHAIN.bundle](evidence/ORIGINAL_CHAIN.bundle)에
원래 metadata와 함께 보존했다. 131091 bytes, SHA-256:

    59c6560f311781cbe32adf22a3b1be6ed89a1fe931494213b9753b2e2d0f8c99

bundle은 PR77 commit을 prerequisite로 갖는 incremental bundle이고
최종 ref는 로컬 증거 commit을 가리키는 HEAD다. 기존 REC 저장소에서
`git bundle verify`로 확인했으며 exit0이었다. 원래 source를 복원해야
할 때는 prerequisite가 있는 저장소에서 이 bundle을 fetch하면 된다.
평소에는 위 GitHub mirror의 고정 파일 링크만 읽으면 된다. 사용자에게
bundle 다운로드·재업로드를 요구하는 전달 방식이 아니다.

모든 원래 source·test·CI·BASS/REC component와 과거 evidence는 불변이다.
독립 검토는 두 축에 P0=0/P1=0이었다. 실제 실행 결과와 게시 성공을
구별하며 NO_PASS_REC_PHYSICAL_SPLIT 및 Draft·미병합 경계를 유지한다.
