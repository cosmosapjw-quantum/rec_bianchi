# REC HD Recoil-Only Bound (Research / HOLD)

Subunit of `cosmosapjw-quantum/rec_bianchi` after Draft PR157. Derives exact one-photon molecular rest recoil and compares its maximum magnitude with the **public source-pinned PR156 selected-field differences**. Does not claim original CDMS v2 source restoration, thermochemical heat, physical population solver or production. Runs under Python standard library plus optional C++20 and matplotlib. No original molecular data bytes embedded.

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python src/recoil.py --transcript data/PR156_SELECTED_FREQUENCIES.json --output /tmp/rec_recoil_test.json
g++ -std=c++20 -O2 -Wall -Wextra -pedantic src/recoil_crosscheck.cpp -o /tmp/recoil_cpp
/tmp/recoil_cpp
python src/plot_results.py
```

`THEORY_KO.md`, `CODING_KO.md` and `REPORT_KO.md` give assumptions and current source/production gates. `STAGE_LEDGER.json` and `stages/` contain retrospectively captured stage-specific checkpoints and real backup receipts are separate. See `NEXT_NODE_CONTRACT.json` and `HANDOFF_NEXT_THREAD_KO.md` for the one next source-qualification task.
