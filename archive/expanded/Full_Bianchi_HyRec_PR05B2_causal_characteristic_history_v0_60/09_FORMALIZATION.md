# Formalization

For each query, `eta_q=-ln[(1+z)E_source/E_target]` and `y_q=(1-lambda)y_L+lambda y_R`. At fixed stencil the exact JVP is `(1-lambda)dy_L+lambda dy_R+(y_R-y_L)deta_q/DLNA`. A stencil switch is an event, not a differentiable branch.
