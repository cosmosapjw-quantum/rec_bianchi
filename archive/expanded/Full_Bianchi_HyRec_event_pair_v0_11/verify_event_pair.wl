ClearAll["Global`*"];

energyRule = EHf -> EHi + EgI - EgF;

FullSimplify[
 Exp[-beta EHi]/Exp[-beta EHf] -
 Exp[-beta(EgF-EgI)] /. energyRule
]

be[E_] := 1/(Exp[beta(E-mu)]-1);

FullSimplify[
 Exp[-beta EHi] be[EgI](1+be[EgF]) -
 Exp[-beta EHf] be[EgF](1+be[EgI]) /. energyRule
]

psiA = Log[fa/(1+fa)] + beta Ea;
psiB = Log[fb/(1+fb)] + beta Eb;

flux = Sab(1+fa)(1+fb)(Exp[psiB]-Exp[psiA]);

FullSimplify[
 (psiA-psiB) flux +
 Sab(1+fa)(1+fb)(psiA-psiB)(Exp[psiA]-Exp[psiB])
]
