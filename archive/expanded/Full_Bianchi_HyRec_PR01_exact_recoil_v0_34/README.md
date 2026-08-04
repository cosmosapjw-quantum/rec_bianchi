# Full Bianchi–HyRec PR-01A exact recoil v0.34

This artifact closes the exact elastic photon–hydrogen event kinematics.

## Hard results

- pytest: [32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                                                [100%][0m
[33m=============================== warnings summary ===============================[0m
../../../../opt/pyvenv/lib/python3.13/site-packages/_pytest/cacheprovider.py:475
  /opt/pyvenv/lib/python3.13/site-packages/_pytest/cacheprovider.py:475: PytestCacheWarning: cache could not write path /mnt/data/Full_Bianchi_HyRec_PR01_exact_recoil_v0_34/workspace/.pytest_cache/v/cache/nodeids: [Errno 13] Permission denied: '/mnt/data/Full_Bianchi_HyRec_PR01_exact_recoil_v0_34/workspace/.pytest_cache/v/cache/nodeids'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
[33m[32m9 passed[0m, [33m[1m1 warning[0m[33m in 0.12s[0m[0m
- random moving-atom events: 2000
- maximum forward four-momentum residual:
  4.786346e-17
- maximum final mass-shell residual:
  9.954561e-16
- maximum reverse-photon residual:
  1.177980e-15
- same-event photon+atom transfer residual:
  0.000000e+00

## Status

- PR-01A exact kinematics: PASS
- PR-01B v0.33 small-recoil bridge: OPEN
- PR-01 complete: OPEN

The workspace contains the TDD tests and minimal implementation.
