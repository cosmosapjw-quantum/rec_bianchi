# R2 — 근거와 재사용 대응

결과: 현재 질문에 필요한 원본 함수, 저장된 dispatcher 입력, radiation incoming, 이미 닫힌 background/native 결과를 분리하여 다음 유도의 입력으로 고정했다. 신규 field 실행은 아직 없다. 중앙 DAG28/88(+0), 단위 내용2/20.

## 직접 확보한 원본

원본 native SOURCE ZIP은110654069bytes, SHA25694b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c이다. 두 원격 part를 byte concatenation하여 원 ZIP을 복원하고 전체 SHA를 실제 확인했다. 원 ZIP은 변경하지 않았다. original/HyRec/hydrogen.c의 실제 SHA256은421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b이다. history.c는8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976이다.

hydrogen.c의 populateTS_2photon, solveTXeqB, solve_real_virt, FULL prelude와 scalar 식을 직접 읽었다. original read_rates/read_twog_params로 tables를 초기화한다. read_twog_params는 sub-Lyα A2s를 정규화한 뒤 feature switch를 적용하므로 raw table hash뿐 아니라 초기화 함수·매크로도 identity에 포함한다. original calloc의 초기0을 보존한다.

capture002의 LAST_WRITERS, CALLS, QSS_WRITES를 함께 사용한다. 선택 slot132개는 메타데이터로 확인했고, 과학 입력 조립과132점 새 실행은 C단계에서 수행한다. native path313 query,626 endpoint references,89 geometric cells,132 unique native times를 그대로 연결한다. CALLS는 dispatcher temperature, WRITES는 coefficient temperature를 담으므로 서로 대체하지 않는다.

## 재사용 결과와 남은 의존성

| 자료 | 실제 확보 범위 | 현재 사용 |
|---|---|---|
| BGJET PR143 HEAD0cb5c5ee16f5be57e71ea6694a8fd93af0394467 | 원 kernel 및 saved endpoint supplement fresh R6/C9 PASS_SCOPED,19/20 | 배경과 geometric query provenance 재사용; 이전 계산0회 반복 |
| Native PR144 HEAD29e8427fa02ae089b004bce13c3d29ef663c89b4 |20/20 scoped delivery, actual native states/radiation captures | 새 point API의 고정 입력과 saved comparison |
| Thermal PR145 HEAD7d3db873dacac29bab40cb5576d1c14b629afa87 |18/20, fresh R6/C9 미완료; 기존 affine thermal residual | 의존성 조사 결과로 보존; 이번 판정에 포함하지 않음 |
| QSS03 PR142 HEAD5438f2a082f7ed204603e441866ca63d1e0bf9de |12/20,C3; coefficient-box certificate NOT_RUN | box-wide inverse gain은 분리된 미완료 의무 |
| REI thermal/caloric/chemical branches | 각 대표 조건에서 별도 부분 결과 | REC full-state/error/tube의 대체 근거로 사용하지 않음 |

## 문헌과 source version

SciSpace에서 HyRec와 coupled recombination을 실제 검색하고 Exa에서 원전을 찾아 확인했다. Ali-Haïmoud & Hirata, arXiv:1011.3758v2(2011), DOI10.1103/PhysRevD.83.043513의 V절은 real/virtual level과 radiation의 결합된 이산 구조를 설명한다. 원전 URL: https://arxiv.org/html/1011.3758v2 . 검색 서비스가 제시한 일부 연도/자동 HTML 날짜는 원문 버전 날짜와 구별했다.

논문은 모델의 물리적 배경을 제공한다. 본 구현의 세부 연산·2012 수정·signed departure·rescaling은 실제 보존된 source bytes로 결정한다. 논문 전체나 모든 branch의 과학 내용을 읽었다고 주장하지 않는다.

## 조사 coverage

51개 owner 저장소 metadata 중 관련17개 repo의1823 branch와1100 open PR 목록을 끝까지 pagination했다. 최근64PR와 관련 comment 자료를 묶어 검토했다. Dropbox 일부 큰 subtree와 Drive/Library 검색에 잔여 cursor가 있고 실제 rate limit이 관찰되었다. 다른 대화는 검색 결과로 접근했으며 모든 원문 transcript 열람 기능은 제공되지 않았다. 원격 목록 전수성과 모든 과학 내용의 검증은 다른 범위이다. 자세한 조사 범위는 SURVEY_SYNTHESIS_KO.md를 따른다.

다음 의무는 source block을 정확한 변수와 가정으로 쓰고, incoming 고정/변화에 따른 선형 구조를 유도하는 것이다.
