# Method note

For a symmetric equilibrium conductance \(S_{ab}=S_{ba}\) and positive
cell equilibrium weights \(\Pi_a\),

\[
K_{a\leftarrow b}=S_{ab}/\Pi_b,
\qquad
G_{bb}=-\sum_{a\ne b}K_{a\leftarrow b}.
\]

Then

\[
\mathbf 1^T G=0,\qquad G\Pi=0,
\]

and, with \(q_a=N_a/\Pi_a\),

\[
q^TGN=-\sum_{a<b}S_{ab}(q_a-q_b)^2\le0.
\]

The raw one-sided COM conductance in this artifact is not symmetric:
the converged defect is approximately \(1.43\times10^{-5}\).  The
stored paired table is \((S+S^T)/2\) and is used only to measure the
operator-level size of the missing reciprocal phase-space terms.
