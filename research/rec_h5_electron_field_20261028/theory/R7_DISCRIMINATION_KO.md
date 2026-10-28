# R7 — 실제 symbolic 판별 검증

중앙 DAG28/88(+0), 단위 내용7/20. 새 native point 호출0, 이전 과학 캠페인 재실행0.

## 입력과 방법

R5의 stable scalar source 변형, 일반2-real/1-virtual Schur elimination, incoming affine성 및 잘못된 block 방향을 구별하는 작은 예를 Wolfram Language kernel에서 실제 실행했다. 정확한 명령은 R7_WOLFRAM_INPUT.wl, 실제 도구 응답은 R7_WOLFRAM_RAW.json이다.

실수 유리식 검산은 V와 Schur determinant가0이 아닌 영역을 대상으로 한다. R5의 임의311-virtual 차원 증명은 block 역대입으로 이미 수행되었고, 이 CAS는 그 대수적 전이를 작은 일반 기호 block에서 판별하는 보조 검산이다. 원본 native313차원 matrix의 실제 point nonsingularity나 coefficient-box regularity를 CAS로 확인했다고 주장하지 않는다.

## 실제 출력

- Stable scalar 변형:0.
- Schur 해를 원 block에 역대입한3개 잔차:{0,0,0}.
- 고정 coefficient의 incoming affine identity:0.
- 세 incoming에 대한 Hessian:3x3 모두0.
- R4 toy의 u=1 정확한 해:{3/5,4/5}.
- B/C 위치를 뒤바꾼 toy 해를 원 식에 넣은 잔차:{7/10,-4/5}. 따라서 잘못된 block 방향은 이 판별 예에서 구별된다.

이 결과는 R5의 원본 유도와 일치한다. 소스의 binary64 affine성을 요구하는 검사가 아니며, 다른 모델의 독립 승인으로 세지 않는다. Fresh nonauthor R6는 별도 검토로 이미 기록했다.

## 실제 자원과 한계

Wolfram kernel version15.0.1 for Linux x86(64-bit), platformLinux-x86-64.
Kernel-reported CPU delta0.062269999999999825s, internal wall0.062582s.
MemoryInUse 시작371700976bytes, 종료372249384bytes, kernel MaxMemoryUsed399417112bytes.

요청에는 timeConstraint10s와 내부 TimeConstrained8s,MemoryConstrained512MiB를 적용했다. Wolfram의 memory 수치는 kernel 관리 메모리 지표이며 OS RSS readback은 제공되지 않았다. Remote execution의 thread count 및 OS-level memory ceiling은 직접 관측하지 못했다. 이것을 local RLIMIT_AS 증거로 대체하지 않는다. 이 도구의 실제 관측 한계를 그대로 보존한다.

Kernel CPU 보고값0.06227s를 새60CPU 연구 예산에 먼저 계상한다. 뒤의 local scientific child는 남은59.93773CPU 내에서 per-child30wall/512MiB/single-thread로 실행한다. Remote tool/network/model의 관측하지 못한 비용은0으로 쓰지 않는다. 이 resource 계상은 전체 세션 비용 측정이 아니다.

## 판정

판별 검증 PASS_SCOPED. 선택한 source expression과 block 방향을 유지한다. C단계는 원본 입력 결속, 실제 내부 divisor,source parity,독립 residual,nonmutation을 확인한다. Physical0/313과 physical certificate null은 변하지 않는다.
