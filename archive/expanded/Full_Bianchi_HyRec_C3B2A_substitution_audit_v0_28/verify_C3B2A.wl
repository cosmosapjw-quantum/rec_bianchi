ClearAll["Global`*"];

w={w1,w2,w3};
one={1,1,1};
A=KroneckerProduct[IdentityMatrix[2],{w}];
J=KroneckerProduct[IdentityMatrix[2],Transpose[{one}]];

trv={{a11,a12},{a21,a22}};
tvr={{b11,b12},{b21,b22}};

liftIdentities=Assuming[w1+w2+w3==1,
 FullSimplify /@ {
  A.J-IdentityMatrix[2],
  KroneckerProduct[trv,{w}].J-trv,
  A.KroneckerProduct[tvr,Transpose[{one}]]-tvr
 }
];

p[tau_]:=1-(1-Exp[-tau])/tau;
f[gam_]:=gam/(1-p[c gam]);

nonadditive=FullSimplify[
 f[g1+g2]-f[g1]-f[g2],
 Assumptions->{c>0,g1>0,g2>0}
];

smallTau=FullSimplify@Normal@Series[
 f[g1+g2]-f[g1]-f[g2],
 {c,0,3}
];

<|
 "LiftIdentities"->liftIdentities,
 "OpticalClosureNonAdditive"->nonadditive,
 "SmallOpticalDepthSeries"->smallTau
|>
