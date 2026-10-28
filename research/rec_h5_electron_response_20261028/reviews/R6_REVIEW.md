# REC-H5-ELECTRON-RESPONSE01 — independent R6 theory review

Reviewer: `/root/incoming_theory_review`. Workflow: physmath-research-loop 1.0.0, R6.

## Decision and reviewed scope

**PASS_SCOPED.** The final `CONTRACT.md` and `THEORY.md` agree with an independent derivation from the pinned HyRec source. The admitted mathematical result is the incoming derivative of the explicitly defined fixed represented-coefficient real model, conditional on exact-real M being invertible. The chosen structured factorization additionally requires invertible V and nonzero exact elimination pivots. This review does not certify any numerical execution, exact nonsingularity, inverse gain, coefficient neighborhood, or physical tube.

The reviewer did not author the implementation or edit the root theory/contract. The reviewer read the original assembly and solve before reviewing the new documents, derived the block equations and residual identity independently, reported two missing clarifications, and reread the root's corrected documents. The only files written by this reviewer are this report and `R6_RECEIPT.json`. No native call, source-field evaluation, scientific numerical calculation, compiler invocation, or remote mutation was performed. JSON parsing and file hashing were read-only evidence operations.

Reviewed final identities:

| Document | Bytes | SHA-256 |
|---|---:|---|
| CONTRACT.md | 7292 | 4b77633b0b5001542cf52d0f904ea9bfaedfb8acf6b5010877d56db2d99408c1 |
| THEORY.md | 5879 | 6608c8c4e5bed4988169fed65cb57eef2eb53460bf488d74f8252adbf225dcd1 |

## Independent source mapping

The original `populateTS_2photon` reads incoming radiation only in two real source entries and the virtual source entry. At fixed scalar point and initialized tables it does not read incoming radiation in A, B, C or V. Stored C is 2 by 311; the mathematical lower-left block is its transpose.

For u=(virtual0,...,virtual310,Ly0,Ly1), the only nonzero entries are

    G[2+b,b] = V[b,b]*x1*pi(tau[b]),
    G[1,311] = 3*kL*H/nH,
    G[0,312] = 3*kL*H/nH*kBeta.

Ly0 enters the real 2p row; Ly1 enters the real 2s row. The source values of kL and kBeta and the optical-depth threshold are lifted from their binary64 literals, as required by the contract. The large-tau exponential expression and the small-tau polynomial are explicitly reconstructed real functions. The original native omega and RLya intermediary bits were not saved; the documentation correctly does not claim their recovery or differentiation of the stepwise binary64 rounding map.

M and G have units s^-1, X and u are dimensionless, q=Beta/H is dimensionless, lambda has units s, and J=G^T lambda is dimensionless. FH is the rate of ionization fraction change with respect to eta=ln(a). Signed incoming and population departures remain allowed by the algebraic model.

## Adjoint and factorization

From M X=a+G u and F=d+q^T X at fixed coefficients, M dX=G du. If M^T lambda=q, then dF=lambda^T G du and J=G^T lambda. Fixed coefficients make this an exact finite-increment identity in the defined real model, with zero incoming Hessian. The statement is conditional on exact-real invertibility and does not turn numerical pivot observations into an invertibility proof.

Writing mathematical C=Cstored^T, block elimination gives

    Z=V^-T B^T,
    Q^T=A^T-C^T Z,
    Q^T lambda_r=q_r,
    lambda_v=-Z lambda_r.

For a general right-hand side the documented y=V^-T r_v, real Schur solve and lambda_v=y-Z lambda_r follow by substitution. The transpose band convention is correctly shifted: lowerT[b]=upper[b-1], upperT[b]=lower[b+1], with zero boundaries. Same-index band swapping represents a different matrix. The exact pivot recurrence is transpose-invariant because its products are lower[i]*upper[i-1]; no row diagonal dominance of V^T is assumed.

## Difference decomposition and validation interpretation

The definitions r_i=M X_i-S_i, r_lambda=M^T lambda_hat-q, e_i=FH_i-(d+q^T X_i), and e_G=(S_c-S_b)-G(u_c-u_b) give

    DeltaFH-(G^T lambda_hat)^T du
      = Deltae + lambda_hat^T e_G
        + lambda_hat^T(r_c-r_b) - r_lambda^T DeltaX.

The signs are correct: q^T DeltaX=lambda_hat^T M DeltaX-r_lambda^T DeltaX. The constant affine source a and baseline stored source S_b are distinct in the final notation. The identity holds for arbitrary lambda_hat, so its closure is a consistency check, not an independent validation of G or the adjoint solve. The contract correctly requires separate adjoint residual, precision/direct-solve checks, source reconstruction, and observed-response criteria.

Controls must first share the same point identity and identical stored coefficients. The new 512 eps64 reconstruction criterion is identified separately from the predecessor's source-parity gate. Its worst-row mismatch is retained as a diagnostic. The nine saved native controls span one original incoming direction at each of three points; they are not 313-column independent native Jacobian validation. The final theory now states this explicitly. Full-vector support instead comes from the source mapping and independent equation/solve checks.

No scientific execution result was reviewed for this R6 decision. In particular, the controller's reported C7 result and the open C8 diagnostic are not adopted here as independently checked numerical evidence. Final code and result acceptance remain C9 duties.

## General P differential and physical scope

Implicit differentiation within a differentiable branch/cell gives

    dF=dd+(dq)^T X
       +lambda^T[da+(dG)u-(dM)X]+J^T du.

The documented scalar expansion, including -F*dH/H, is correct. On the current He-neutral xe=p manifold the allowed tangent obeys dxe=dp. Ordinary derivatives also require a fixed table interpolation cell, feature choice and optical-depth branch; interfaces require stated one-sided or piecewise derivatives. The new incoming response does not supply da, dM, dG, dq and dd as a full-state provider or silently discard them in a time derivative.

The exact-model inequality |deltaF|<=||J||_1||du||_infinity is correct. A computed point ||J||_1 without directed error certification is a numerical sensitivity value, not a certified physical or whole-domain Lipschitz bound. QSS03 nonsingularity/coefficient-box/inverse-gain work and the physical defect, model discrepancy, initial error, full-state norm and positive tube remain separate obligations. Canonical 28/88 +0 and physical 0/313 are inherited bookkeeping, not new completions granted by this review.

## Findings and disposition

| ID | Finding | Required correction | Final disposition |
|---|---|---|---|
| R6-F01 | The original structured-solve prose did not separately state the V/pivot assumptions; invertible M alone does not imply them. | Add invertible V and nonzero exact tridiagonal pivots as factorization conditions while retaining invertible M for the abstract theorem. | RESOLVED by root in CONTRACT and THEORY; reread in the hash-bound versions above. |
| R6-F02 | The original final prose omitted the rank interpretation of the nine saved native controls. | State three points with one incoming direction each and separate full-vector equation evidence from these native directions. | RESOLVED by root in THEORY; reread in the hash-bound version above. |

Open blocking theory findings: **0**. The acceptance is scoped to the reviewed mathematics and model definition. No new general adjoint theorem, strong no-go result, exact-real invertibility certificate, or physical admission is claimed.

## Source reads and independence

Read original `inputs/original/HyRec/hydrogen.c` assembly, solver, LYA_FACT and source scalar; `hydrogen.h` and `hyrec_params.h`; predecessor `code/electron_field.c`, `electron_field.h`, `stage_worker.py` and relevant `runtime.py`; predecessor R5/R9 theory; C7/C8 record schemas and the saved C8 summary. The source archive identity was supplied and recovered by the controller; this reviewer did not independently rehash the whole archive. The two new reviewed documents were read and hashed directly by this reviewer.

Actual independence is separate-agent independent derivation followed by document review. Runtime model-family diversity was not observed and is not claimed. CAS/serial review approval credit: 0. Scientific execution by this reviewer: 0.
