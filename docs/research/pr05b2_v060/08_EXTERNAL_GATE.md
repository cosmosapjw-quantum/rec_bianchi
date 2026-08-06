# External gate

A future adaptive solver must append history only in the successful-step callback. Event rollback must not commit a candidate, and a discontinuous source/stencil change must restart multistep or FSAL methods. These callback semantics are locked for PR-05C.
