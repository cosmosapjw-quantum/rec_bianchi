ClearAll["Global`*"];

sigmaT=8 Pi re^2/3;
GammaA=8 Pi^2 re f nu0^2/(3 c);
gammaNu=GammaA/(4 Pi);

sigmaL[nu_]:=
 sigmaT (f^2 nu0^2/4)/
 ((nu-nu0)^2+gammaNu^2);

integrated=Assuming[
 {re>0,f>0,nu0>0,c>0},
 FullSimplify[
  Integrate[sigmaL[nu],{nu,-Infinity,Infinity}]
 ]
];

phaseNorm=Integrate[
 (3/4)(1+mu^2)/2,
 {mu,-1,1}
];

zonalNorm=Assuming[
 kappa>0,
 FullSimplify[
  Integrate[
   (3/4)(1+mu^2)Exp[kappa mu]/2,
   {mu,-1,1}
  ]
 ]
];

<|
 "IntegratedKHWLorentzian"->integrated,
 "OscillatorStrengthIntegral"->Pi re c f,
 "NormalizationResidual"->
  FullSimplify[integrated-Pi re c f],
 "RayleighPhaseNormalizedSphereAverage"->phaseNorm,
 "ExpZonalNormalization"->zonalNorm
|>
