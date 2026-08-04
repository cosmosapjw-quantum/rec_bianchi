ClearAll["Global`*"];
trMin=SetPrecision[0.004,50]; trMax=SetPrecision[0.4,50];
ntr=100; tr=SetPrecision[3000*8.617343e-05,50];
dlog=(Log[trMax]-Log[trMin])/(ntr-1);
u=(Log[tr]-Log[trMin])/dlog; idx=Floor[u]; frac=u-idx;
ww={frac(frac-1)(2-frac)/6,
(1+frac)(1-frac)(2-frac)/2,
(1+frac)frac(2-frac)/2,
(1+frac)frac(frac-1)/6};
a2s=SetPrecision[{2.1986885e-13, 2.1379089e-13, 2.0779901e-13, 2.0188858e-13},40];
a2p=SetPrecision[{5.8667669e-13, 5.654425e-13, 5.4488824e-13, 5.2499279e-13},40];
rsp=SetPrecision[{348.38577, 572.25626, 919.3205, 1445.6878},40];
alpha2s=Exp[Log[a2s].ww]; alpha2p=Exp[Log[a2p].ww];
rr=Exp[Log[rsp].ww];
saha=SetPrecision[3.016103031869581e+21,50];
ei=SetPrecision[13.598286071938324,50];
beta2s=alpha2s saha tr Sqrt[tr] Exp[-ei/(4 tr)];
beta2p=alpha2p saha tr Sqrt[tr] Exp[-ei/(4 tr)]/3;
<|
"Index"->idx,
"Fraction"->N[frac,20],
"WeightSumResidual"->N[Total[ww]-1,30],
"Alpha2s"->N[alpha2s,20],
"Alpha2p"->N[alpha2p,20],
"Beta2s"->N[beta2s,20],
"Beta2p"->N[beta2p,20],
"R2p2s"->N[rr,20],
"DetailedBalance2sResidual"->N[
 beta2s-alpha2s saha tr Sqrt[tr] Exp[-ei/(4 tr)],30],
"DetailedBalance2pResidual"->N[
 beta2p-alpha2p saha tr Sqrt[tr] Exp[-ei/(4 tr)]/3,30]
|>
