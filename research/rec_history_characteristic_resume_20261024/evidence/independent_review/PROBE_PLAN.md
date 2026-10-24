# Proposed independent finite probes — not executed

Execution requires explicit root GO after primary and freezing the concrete script/controller. At most six probe rows total; one bounded invocation under 6 CPU/15 execution-wall seconds, one thread, 1 GiB. No old checks, IVP, native recombination or dense RHS. Use source snapshot/controller receipts and save each raw row. Original thresholds remain unchanged.

1. **P1 transformed source-time tangent overflow:** crossing n=[1,0,0], b=[0,0,0], Lambda=1; JVP dLambda=-1e308,deta_t=1e308, other tangents zero. Expected explicit ValueError for nonfinite transformed result after the diagnosed guard correction.
2. **P2 exact-axis finite off-axis tangent:** n=[1,0,0], b=[-.5,.2,.3], Lambda=2; dn=[0,1e-3,0], other tangents zero. Exact Delta=4, dDelta=0, dn_s,y=1e-3 exp(2.8), and other source tangent components zero. Compare JVP at 5e-9 scaled and save absolute error.
3. **P3 negative-axis source/target coefficient distinction:** n=[0,-1,0], b=[.25,-.5,.25], Lambda=.4; db=[-.1,.2,-.1], other tangents zero. Exact Delta=.8, dDelta=-.32, dn_s=0, dqt=.2. Compare with 5e-9 scaled gate.
4. **P4 tiny signed Wien offset:** xt=2, Lambda=.3, Delta=.3+2e-13; dlnxt=.04,dLambda=.07,dDelta=-.02. Compare offset and reference JVP with independent 80-digit exponentials; 8e-12 relative scale max(abs(reference),1e-300) plus 5e-324 absolute floor.
5. **P5 strict prefix and knot behavior:** eta0=0,h=.125,values=[.2,.3,.4],iz=3. Query eta=-.001 must reject before fallback; eta=.125 with deta=0 must retain k=1 and value=.3. These two branches constitute one predeclared domain-behavior row and invocation counts must report both calls.
6. **P6 missing uncertainty remains missing:** error_envelope with e_H=None,K_eta=.03,K_n=.02,eps_F=1e-8,e_arithmetic=1e-13,a_min=.8,a_max=1.2,qt=1,tau=.2,H_t=1e-13 must raise MISSING_ERROR_INPUT. No numerical bound may be substituted.

These are proposed exact cases. Root may approve this plan or narrow it before execution; changes after results require diagnosis and preserved original evidence.
