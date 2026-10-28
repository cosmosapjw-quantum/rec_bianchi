# REC-HD 원자료 분광 lineage / Kirchhoff 교차에너지 국소 진단

**결론: PASS_SCOPED_DIAGNOSTIC; 원래 REC-HD source-choice gate는 HOLD 유지.** `REC_HD_PRIMARY_SPECTROSCOPY_RECONCILIATION_NEXT`에 대해 준비된 2021-06-07 LAMDA HD 원본(2,289 bytes, SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`)을 actual Git blob에서 그대로 복원·해시 검증했다. original 35Hz 7/8 FAIL과 line1 PASS를 보존하고, source version2 `.cat/.egy/.par` 및 전환 레시피는 검색/현재 접근에서 얻지 못했다.

## 실제 동시 체크에서 얻은 새 과학적 크기

이전에 서로 독립적으로 검사하던 Maxwellian level-energy detailed balance와 photon-frequency Einstein relation을 **같은 LTE population**에 묶으면, `R=(j_nu/alpha_nu)/B_nu(T)=expm1(h nu/k_BT)/expm1(h c100 (w_u-w_l)/k_BT)`가 된다. 이는 *소스 열 교차 해석의 조건부 값*이다. source-printed 50,100,200 K에서 8×3=24개 계산 모두 유한하며, 최대 |R-1| = **1.7541951787469943×10^-6** (line6 J6→5, 50 K). 원래 35Hz 문제의 원인이나 실제 기체 가열 오차를 잰 값이 아니다.

| line/J_upper | signed gap minus nu [Hz] | R-1 at 50K | at 100K | at 200K | CDMS v2 HTML fit-input lead |
|---|---:|---:|---:|---:|---|
|1 / J1| -8.2410162 |+8.5674e-12|+5.4702e-12|+4.1746e-12|Drouin (2011) J''0|
|2 / J2| -947678.840324 |+9.1511e-7|+4.9297e-7|+3.1506e-7|Ulivi (1991) J''1|
|3 / J3| +1084318.7429164 |-1.0413e-6|-5.3210e-7|-3.0552e-7|Ulivi (1991) J''2|
|4 / J4| -47627.4090914 |+4.5717e-8|+2.3005e-8|+1.2424e-8|Ulivi (1991) J''3|
|5 / J5| +1245461.910729 |-1.1955e-6|-5.9889e-7|-3.1262e-7|not individually named|
|6 / J6| -1827572.5607572 |+1.7542e-6|+8.7763e-7|+4.4964e-7|not individually named|
|7 / J7| +1411205.4502552 |-1.3545e-6|-6.7741e-7|-3.4350e-7|Essenwanger & Gush (1984) J''6|
|8 / J8| +6864.9896228 |-6.5894e-9|-3.2949e-9|-1.6612e-9|not individually named|

CDMS v2 HTML의 'reported fit inputs'를 LAMDA 저장된 각각의 주파수가 실험값임을 확정하는 증거로 승격하지 않았다. 모델 예측·측정선·준위 fitting 원문이 없다. 표의 시각화는 `figures/HD_SOURCE_CROSS_ENERGY.png`이며 source 8점 이외를 연결하지 않았다. 최초 그림 아래 캡션/축 겹침은 원본 유지 + 저장데이터만 사용한 1회 배치 수정으로 해결했다.

## 실제 코드 검산 / 예산

source 원본 SHA와 9 levels/8 lines/1-based J 연속성이 검증됐고, Decimal80와 mpmath120 비교 최댓값 **3.1069285e-79**, 허용 1e-65. 물리 부호 음성검사, 원래 7 failure 유지, 오염원문 해시거부, 임의 교정 ladder의 비승격을 확인했다. 독립 외부 소스 모델 검토는 NOT_RUN, same-context numerical cross-method check에 한정한다. C9/정식 독립 심사는 미충족이다.

새 누적 실행 예산 12 child CPU s /80 wall s, 1 thread, 512 MiB address, new IVP 0, native C 0, old adapter full campaign replay 0. 실제 process CPU 합은 실행기록을 참조하며, 원격 source retrieval/model/provider 비용은 UNKNOWN_NOT_ZERO다.

## CDMS / LAMDA 출처

- Original CDMS Version2 Dec 2011 HTML: https://cdms.astro.uni-koeln.de/cgi-bin/cdmsinfo?file=e003501.cat (retrieval showed version2 historical HTML; versionless URL may serve version3 elsewhere, no raw byte snapshot).
- LAMDA June7 2021 HD metadata: https://home.strw.leidenuniv.nl/~moldata/HD.html
- Source formatting: https://home.strw.leidenuniv.nl/~moldata/molformat.html (line frequency an informational field).
- CDMS current 2026 v3 entry: https://cdms.astro.uni-koeln.de/cgi-bin/cdmsinfo?file=e003501.cat (a separate 2026 source identity; no version transfer).
- Previous signed source defect and literal adapter: rec_bianchi research/program_expansion_20261025/hd_adapter/SOURCE_DISCREPANCY.md and `lamda_hd.py` at immutable 6ab99170; do not rerun or relabel original tests.

## H–Li and canonical statuses

이 결과는 neutral ¹H²H 로터의 finite source 진단이지 신규 26 ground·5 nuclear-level·102 formal charge request가 active species/rate로 공급된 것이 아니다. 새 음이온/준안정 상태 level source는 isotope/state-qualified 별도 의무. 기존 `ElementalElectronicEquality`, REC 20 atomic slots+n=21, REI ON_refined17, VigilODE6/30/33을 변경하지 않았다. Canonical **28/88 delta0**, physical 0/313, full HD bridge HOLD, H5 epsilon null, H6/H7 OPEN, L4=false, REI activation=false, production HOLD. No central DAG/main mutation.

**다음 필요한 단일 입력:** version2 archived `.cat/.egy/.par` and LAMDA source-conversion provenance with numerical row IDs and quoted uncertainties. 이것이 없으면 주파수 열/준위 에너지 중 무엇을 채택할지 선택하지 않는다. 새로운 2026 v3도 별도 source-qualified proposal과 기존 영향을 받는 검사 없이 덮어쓰지 않는다.
