# REC-to-REI AXIS153: 완료된 물질/복사 분리 pilot의 응답 재사용

원 owner/적분기를 바꾸지 않는 사후 분석이다. REI PR213의 실제729-case warm C15 결과를 재사용한다. 새 ODE/NCP/benchmark 실행은0이며, 현재 완성된729개를 새 대기열로 돌리지 않는다.

## 정확한 역할

- REC base: df95a074730ea0d13d609cf88d448f01f4a47ef1
- 새 reducer/test/results 게시: d2c0fbb5fa06dfc37db57876bb130ef8a4fa8a5d
- 실제 실행 reducer SHA256: 453eee672e2a6d78bf0f76aa42f5453e68c1066cc561f5fe547be9e30e01e457
- REI 결과: c8e9f67aa031ffb33a9b0347bdea61dbb01fb746
- REI 최종 배송: d32cd99fa19c65aa1ca63dbc8aab8741834270e8
- C15 물리 owner: rei_bianchi@80825585f9fe31d2ee0d5af545ada3fa1f52be72
- CSV: 1778657bytes,729행149열, SHA256 c322453eed4c4c236ff19501ea6eca50353d6ebecc604a6cab9647b3a090255c

## 물리·수학 계약

(-,+,+,+), proper time s, H와전단성분s의 단위s^-1. LRS에서 sigma=diag(-s,-s,2s), pi_A=diag(-D_A/3,-D_A/3,2D_A/3). A=m,r. half-contraction convention에서 S=sqrt(3)s/H, P_A=(8piG/c^2)D_A/(sqrt(3)H^2), Sigma=|S|, Pi_A=|P_A|. Pi_total은 |P_m+P_r|이며 |P_m|+|P_r|가 아니다. Frobenius norm은sqrt(2)배다.

물질은 massive nonbaryonic Vlasov이고, 등방H/He와잔여cold matter의 anisotropic stress는이closure에서0이다. 복사는gamma+massless neutrino+UV. warm a=.1999→.2, 초기gas12000K의 조건부 LRS다. 전체coldEoR/일반비축대칭Bianchi I와동일하지 않다.

Fhat(S,m,r)=F(S,m,0)+F(S,0,r)-F(S,0,0).
153개축support만 예측에사용하고576개mixed끝점은비교에만 사용했다. 새fit계수0. F가C2이면 F-Fhat=integral_0^m integral_0^r partial_m partial_r F dv du. 따라서 |R|<=|mr|sup|F_mr|이나 그연속sup상한은확보하지 않았다. 문헌상anchored decomposition 개념(doi10.1137/17M1161890, 공식초록)을 참고했고 이항등식은직접유도·CAS검산했다.

이는사전등록blind검증이아닌 retrospective 저장자료비교다. 대수적분해나작은끝점잔차를물리결합의소실로해석하지 않는다.

## 실제새결과

최대끝점차이: signedS1.5612511283791264e-17, P_m2.2970232486929643e-14, P_r1.6540805183873353e-14, total3.9510982640131203e-14, Tgas1.0913936421275139e-11K. 비영상쇄72개를포함한다. inherited3e-13은display/orientation floor일뿐solver tolerance가아니다.

12개실제unit검사PASS. 별도Fraction정확반례1개도검산했다: g=mr(m²-1)(r²-1)(m+r)는153축+90sentinel 모두0이나 g(1/2,1/4)=135/2048. 따라서243개control통과만으로나머지486개를인증할수없다. 현재576개실제비교와미래설계의가정을구분한다.

GNU time: user1.12s/system.12s/wall.84s/maxRSS113260KiB. 내부mainCPU.124043779s는다른범위이므로합산하지않는다. 물리적speedup·parallel scaling·RSS감소는NOT_MEASURED.

## 재현과보존

전체보존ZIP에는intake/원CSV,work/code,실제로그,전체비교CSV,PNG/SVG그림과manifest가있다. Git에는compact source/evidence를게시한다. stage1은40payload를Drive전체readback으로대조했다. Dropbox는완료ACK/크기확인과whole readback NOT_RUN을구별한다. 최종보존은PR116의마지막receipt를읽는다.

```bash
cd work/code
python -m unittest -v test_axis_reuse
python sentinel_counterexample.py
python axis_reuse.py --csv ../../intake/REI_SPLIT729_CASES.csv --out ../results/new_readonly_check
python plot_axis_reuse.py --results ../results/new_readonly_check --out ../figures/new_readonly_check
```

그림은실제81점response,576점withheld잔차,8점zero-shear상쇄끝점에서생성했다. 비균일축의실제좌표를쓰고입력범위밖은표시하지않는다. 독립agent는노출되지않아새독립감사는NOT_RUN이다. 실제검토는직렬self-review+CAS+표적반례다. Physical validity HOLD, production NOT_APPROVED. 상세한한국어보고서는전체archive의work/REPORT_KO.md.
