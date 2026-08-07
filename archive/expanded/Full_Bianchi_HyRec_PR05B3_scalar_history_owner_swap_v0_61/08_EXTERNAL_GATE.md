# External gate

PETSc integration must create candidates during an attempt, commit in the successful-step callback exactly once, discard on rejection, restore exact parent bytes after event rollback, and restart at stencil/coefficient discontinuities. Adaptive integration is deferred to PR-05C.
