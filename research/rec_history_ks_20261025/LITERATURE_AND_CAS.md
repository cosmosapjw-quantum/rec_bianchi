# Literature and symbolic-tool record
Exa and SciSpace were actually queried in this turn. Search scope:
HyRec source/radiative-transfer context and rigorous inverse-residual bounds.
SciSpace returned10paper records; most were not sufficiently specific to
be premises of this finite certificate. No search hit supplies a calibrated
physical history uncertainty for this input.

Selected primary references:
- Y.Ali-Haimoud and C.M.Hirata,Phys.Rev.D83,043513(2011),
  https://arxiv.org/abs/1011.3758 and https://doi.org/10.1103/PhysRevD.83.043513.
  Used as source-model context; current source mapping comes from retained code.
- S.M.Rump,Verification methods,Acta Numerica19(2010),287-449,
  https://www.tuhh.de/ti3/paper/rump/Ru10.pdf.
  The introduction/principles and interval-method context were read.
  The complete certificate argument used here is directly given in THEORY.md;
  it does not rely on an unread theorem or this paper's entire contents.
- SciSpace surfaced DOI10.1007/BF02253185 for exact residual/a-posteriori
  linear-system bounds. Bibliographic lead only,not a premise.

A single Wolfram Language call,timeConstraint10s,checked generic residual
identity,partial incoming derivative and combined chain rule. All three
returned True. Undefined-symbol warnings from the tool are retained in
evidence/WOLFRAM_SYMBOLIC.json. No user numeric arrays were submitted.
Remote CPU was not measured and is not zero. Independent source review and
exact Fraction manufactured cases separately support the result.
Raw article extracts are not needed to reproduce the locally proved result.

