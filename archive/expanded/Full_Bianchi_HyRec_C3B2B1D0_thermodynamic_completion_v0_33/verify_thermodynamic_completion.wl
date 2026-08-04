ClearAll["Global`*"];

Kab=Bab Sqrt[PiA/PiB];
Kba=Bab Sqrt[PiB/PiA];

psiA=Log[fa/(1+fa)]-Log[za];
psiB=Log[fb/(1+fb)]-Log[zb];

Sab=Bab Sqrt[PiA PiB];
Jab=Sab(1+fa)(1+fb)(Exp[psiB]-Exp[psiA]);

beRule={
 fa->q za/(1-q za),
 fb->q zb/(1-q zb)
};

b=Sqrt[2 k T/M]/c;
g=h nu0/(M c^2 b);
alpha=beta h nu0 b;

fpCurrent=a1[x] pi[x]-1/2 D[a2[x]pi[x],x];
fpRule=a1[x]->1/2 D[a2[x],x]
 +1/2 a2[x]D[Log[pi[x]],x];

<|
 "PairDetailedBalanceResidual"->FullSimplify[
  Kab PiB-Kba PiA,
  Assumptions->{Bab>=0,PiA>0,PiB>0}
 ],
 "BoseEinsteinEdgeResidual"->FullSimplify[
  Jab/.beRule,
  Assumptions->{
   Bab>=0,PiA>0,PiB>0,
   0<q za<1,0<q zb<1
  }
 ],
 "EntropyIdentityResidual"->FullSimplify[
  (psiA-psiB)Jab
  +Sab(1+fa)(1+fb)
   (psiA-psiB)(Exp[psiA]-Exp[psiB])
 ],
 "ThermalSlopeAlphaMinus2g"->FullSimplify[
  alpha-2g,
  Assumptions->{
   beta==1/(k T),k>0,T>0,M>0,
   c>0,h>0,nu0>0
  }
 ],
 "FokkerPlanckZeroCurrentResidual"->
  FullSimplify[fpCurrent/.fpRule]
|>
