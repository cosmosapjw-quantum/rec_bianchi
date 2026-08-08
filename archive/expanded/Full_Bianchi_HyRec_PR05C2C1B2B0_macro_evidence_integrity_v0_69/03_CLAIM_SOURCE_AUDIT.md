# Claim/source audit

The endpoint bytes and recorded timesteps are source locked.  The expensive worker source and accepted parent states are absent.  Backward Euler nevertheless fixes a unique implied parent, so positivity is auditable without reconstructing the missing worker.
