ClearAll["Global`*"];
Tvv={{d1,u1},{l2,d2}}; trv={r1,r2}; tvr={v1,v2}; sv={q1,q2};
inv=Inverse[Tvv]; teff=a-trv.inv.tvr; seff=s-trv.inv.sv;
xx=Together[seff/teff]; yy=Together[inv.(sv-tvr xx)];
res=FullSimplify[Join[{a xx+trv.yy-s},Tvv.yy+tvr xx-sv],
 Assumptions->Det[Tvv]!=0&&teff!=0];
pi0=Exp[-E0/temp]; pi1=Exp[-E1/temp];
R10=Exp[(E1-E0)/temp]R01;
pib=Exp[-Eb/temp]; pi2=3 Exp[-E21/temp];
R2b=Exp[(E21-Eb)/temp]Rb2/3;
<|
"SchurResidual"->res,
"AdjacentDetailedBalanceResidual"->FullSimplify[pi0 R01-pi1 R10,Assumptions->temp>0],
"LineCenterDetailedBalanceResidual"->FullSimplify[pib Rb2-pi2 R2b,Assumptions->temp>0]
|>
