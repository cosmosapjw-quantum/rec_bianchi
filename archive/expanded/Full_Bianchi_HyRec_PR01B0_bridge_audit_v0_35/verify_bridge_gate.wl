ClearAll["Global`*"];

p[mu_] := (3/8)(1+mu^2);
shift[mu_] := -g(1-mu)/(1+g b(1-mu));

moments = <|
 "Normalization" -> Integrate[p[mu],{mu,-1,1}],
 "MeanOneMinusMu" -> Integrate[(1-mu)p[mu],{mu,-1,1}],
 "SecondOneMinusMu" -> Integrate[(1-mu)^2 p[mu],{mu,-1,1}],
 "ThirdOneMinusMu" -> Integrate[(1-mu)^3 p[mu],{mu,-1,1}]
|>;

exactMean = Assuming[{g>0,b>0},
 FullSimplify[Integrate[p[mu] shift[mu],{mu,-1,1}]]
];

seriesMean = Assuming[{g>0,b>0},
 FullSimplify[Normal@Series[exactMean,{b,0,2}]]
];

d=q delta;
gaussianRatio=FullSimplify[
 Exp[-(d+g q)^2/(2q)]/
 Exp[-(-d+g q)^2/(2q)],
 Assumptions->{q>0,g>0,delta∈Reals}
];

frequencyFactorRatio=(nuI/nuJ)^2;

<|
 "RayleighMoments"->moments,
 "ExactMeanRecoil"->exactMean,
 "MeanRecoilSeries"->seriesMean,
 "ShiftedGaussianForwardReverseRatio"->gaussianRatio,
 "KHWFrequencyFactorRatio"->frequencyFactorRatio,
 "CombinedAffinity"->FullSimplify[
  gaussianRatio frequencyFactorRatio,
  Assumptions->{q>0,g>0,nuI>0,nuJ>0,delta∈Reals}
 ]
|>
