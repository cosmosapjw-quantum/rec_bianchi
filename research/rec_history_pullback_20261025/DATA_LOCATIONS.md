# Data locations and restore order — PB01

공개 Git projection은 owned source,논증,판정,그림과 selected result JSON을 담는다.
원history·전체NPZ·case별 exact Fraction·private survey/conversation 응답은
scienceS2 full raw archive에 보존한다. Actual provider IDs와 SHA는
 delivery/PUBLICATION_STATE.json, S2_RECEIPT.json, FINAL_COMPANION_RECEIPT.json을 따른다.

S0R=동결문서·조사·runtime recovery, S1=preexec code/review,
S1F=최초실패 raw, scienceS2=18/20 과학전체,
compact companion=과학S2 후 실제 중앙게시·전달 근거다. 각 ZIP의 ownACK는
그ZIP 안에재귀삽입하지않는다. 다음 receipt 또는finalGit가실제ACK를기록한다.

## Full restore

1. scienceS2의 PAYLOAD_MANIFEST.json으로 archive member identity를 확인해
   rec_history_followup_20261025 아래로 복원한다.
2. delivery/recovery001/KS01_S2_RECOVERED.zip은54196274bytes,
   SHA2563a67f3e1e40d39f8833bf9481e483593929ab9fc2c38451dae8e9ed4a7042301다.
   이를 sibling rec_history_next_20261025 아래로 복원하면206payload를 얻는다.
3. 위 sibling의 inputs/THERMO01_S2.zip은5842521bytes,
   SHA256f17aa795966c9af1805b9194db42dae99f6daa266205b0293ead3bff4f2090d1다.
   inputs/thermo_s2 아래로 복원하면485manifest payload를 얻는다.
4. original35MBhistory와 KS01 K/event/witness inputs는
   inputs/PATH_MANIFEST.json과 actual19-entry EXECUTION_IDENTITIES에 연결된다.
   경로는상황에맞게binding할수있지만원bytes/물리inputidentity를바꾸지않는다.

현재세션에서 위 두원archive의 size/SHA/CRC/각payload와 실제복원bytes를
확인했다. 이는 workspace 소실복구 I/O였고 기존과학재실행은0이다.
Runtime recovery 및 정확히복원/재구성한 파일의구분은 delivery와 survey에있다.

## Actual execution record

- Executed first primary: sourcebc63fd1868710548f27381a6bbaea8d6b445357436a5fdc009e8997c03a66b26;
  old18manifest34140f9a776162b13f19b39be0a1353952c1918a5d5fc250a0fdb3dd3c7dc0e0;
  results/primary001은exit2 원상태보존.
- Accepted shared-event repair: repairs/event_pair001의32vectors;
  원381raw불변,새matvec0.
- Current primary: ac69a3578ff45c0363fcc194ef694135543217f342eb861c06712c5eb6590ebb;
  current19manifest879c8543c679b296a155a6b3202aa900d68657731a423da0e51035756b1c0cd3;
  전체primary재실행0.
- Accepted images: results/figures001/cell_margins_query_gains.png,
  results/figures002/remainder_adjoint_consistency.png. 최초실패layout도그대로보존.

일반재개는결과/receipt재사용으로시작한다. 이복구설명은새IVP/native/기존campaign
실행지시가아니다.
