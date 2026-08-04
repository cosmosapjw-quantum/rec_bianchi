ClearAll["Global`*"];

mu=1-2 s^2;
ct=Sqrt[1-s^2];
x=u+v;
xp=u-v;

jac=Abs[Det[D[{x,xp},{{u,v}}]]];

transformed=FullSimplify[
 1/(Pi Sqrt[1-mu^2])
 Exp[-(x-xp)^2/(2(1-mu))]
 jac,
 Assumptions->{0<s<1,u∈Reals,v∈Reals}
];

vint=Assuming[
 {0<s<1,vL<vU,vL∈Reals,vU∈Reals},
 FullSimplify[
  Integrate[transformed,{v,vL,vU}]
 ]
];

angularMeasure=FullSimplify[
 (1/2)Abs[D[mu,s]],
 Assumptions->{0<s<1}
];

moments=Table[
 FullSimplify[
  1/2 Integrate[
   (3/4)(1+z^2)LegendreP[l,z],
   {z,-1,1}
  ]
 ],
 {l,0,6}
];

<|
 "Jacobian"->jac,
 "TransformedGaussianFactor"->transformed,
 "IntegratedVFactor"->vint,
 "HalfDmuMeasure"->angularMeasure,
 "RayleighLegendreMoments"->moments
|>
