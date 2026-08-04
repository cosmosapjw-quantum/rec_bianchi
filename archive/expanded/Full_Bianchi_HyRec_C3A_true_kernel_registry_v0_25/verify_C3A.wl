ClearAll["Global`*"];
planckOcc[nu_] := 1/(Exp[beta h nu]-1);
planckN[nu_] := 2 nu^2/c^2 planckOcc[nu];
thermFactor[nu_] := (nu0/nu)^2 Exp[beta h (nu-nu0)]
 (1+planckOcc[nu0])/(1+planckOcc[nu]);

levi[i_,j_,k_] := If[DuplicateFreeQ[{i,j,k}],Signature[{i,j,k}],0];
avec={aa,0,0}; nmat=DiagonalMatrix[{0,n2,n3}];
sc[o_,i_,j_] := Sum[levi[i,j,d] nmat[[d,o]],{d,1,3}]
 +avec[[i]] KroneckerDelta[o,j]-avec[[j]] KroneckerDelta[o,i];
jac[d_,a_,b_,cc_] := FullSimplify[Sum[
 sc[e,b,cc] sc[d,a,e]+sc[e,cc,a] sc[d,b,e]+sc[e,a,b] sc[d,cc,e],
 {e,1,3}]];
conn[g_,b_,a_] := 1/2(sc[g,a,b]-sc[a,b,g]+sc[b,g,a]);
dirV[g_] := -Sum[conn[g,b,a] xx[a] xx[b],{a,1,3},{b,1,3}];

<|
 "ThermodynamicResidual"->FullSimplify[
  thermFactor[nu]planckN[nu]-planckN[nu0],
  Assumptions->{beta>0,h>0,c>0,nu>0,nu0>0}
 ],
 "BosonicCompletionResidual"->FullSimplify[
  eta(1+n)-(eta+B)n-(eta-B n)
 ],
 "JacobiDistinct"->Table[jac[d,1,2,3],{d,1,3}],
 "MetricCompatibilityNonzeroCount"->Count[
  Table[FullSimplify[conn[g,b,a]+conn[b,g,a]],{g,1,3},{b,1,3},{a,1,3}],
  _?(#=!=0&),Infinity
 ],
 "DirectionNormResidual"->FullSimplify[Sum[xx[g]dirV[g],{g,1,3}]]
|>
