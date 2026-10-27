Clear[x, eta, c, a, b, q, et, es, k, t, z, delta, yl, yr, uh, wa, wb, wq, wn, alpha, ff, ww, ffp, wwp];
derivatives = FullSimplify[Table[D[Exp[-c Exp[eta]], {eta,n}], {n,1,3}] /. c -> x Exp[-eta], Assumptions -> x>0];
criticalPolynomial = Factor[Exp[x] D[(x^2-x) Exp[-x],x]];
criticalRoots = Solve[x^2-3x+1==0,x];
characteristic = FullSimplify[es Exp[-Log[(1+z)es/et]]/(k t)-et/(k t(1+z)),Assumptions->{es>0,et>0,k>0,t>0,z>-1}];
bridge = FullSimplify[Exp[-x Exp[delta]]-Exp[-x]-Exp[-x](Exp[-x(Exp[delta]-1)]-1),Assumptions->{x>0,Element[delta,Reals]}];
anchor = Expand[(uh+wn)-((1-alpha)(yl+wa)+alpha(yr+wb))-((uh-((1-alpha)yl+alpha yr))-((1-alpha)wa+alpha wb-wq)-(wq-wn))];
quadraticChord = Factor[((b-q)/(b-a) a^2+(q-a)/(b-a)b^2-q^2)-((q-a)(b-q))];
defect = Expand[(ffp-wwp)-(ff^2+eta-wwp)-(ffp-(ff^2+eta))];
<|"derivatives"->derivatives,"critical_polynomial"->criticalPolynomial,"critical_roots"->criticalRoots,"characteristic_residual"->characteristic,"bridge_residual"->bridge,"anchor_residual"->anchor,"quadratic_chord_residual"->quadraticChord,"toy_defect_residual"->defect|>
