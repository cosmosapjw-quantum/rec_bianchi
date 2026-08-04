ClearAll["Global`*"];

nu = nuAbs + x dNu;
Ax1 = (nu R - nuAbsDot)/dNu - x dLogDNu;
Ax2 = (nuAbs R - nuAbsDot)/dNu + x(R-dLogDNu);

redFlux = Max[-aR,0] nIR - Max[aR,0] nOR;
blueFlux = Max[aB,0] nIB - Max[-aB,0] nOB;

dNI = -redFlux-blueFlux-lRsc-lBsc+sI;
dNR = redFlux+lRsc+sR-farR;
dNB = blueFlux+lBsc+sB-farB;

<|
 "EquivalentCoordinateSpeedResidual" -> FullSimplify[Ax1-Ax2],
 "RedOutflow" -> FullSimplify[
   redFlux /. {aR->-u,nOR->0},
   Assumptions->{u>0}
 ],
 "RedInflow" -> FullSimplify[
   redFlux /. {aR->u,nIR->0},
   Assumptions->{u>0}
 ],
 "BlueOutflow" -> FullSimplify[
   blueFlux /. {aB->u,nOB->0},
   Assumptions->{u>0}
 ],
 "BlueInflow" -> FullSimplify[
   blueFlux /. {aB->-u,nIB->0},
   Assumptions->{u>0}
 ],
 "PhotonNumberResidual" -> FullSimplify[
   dNI+dNR+dNB-(sI+sR+sB-farR-farB)
 ],
 "ScatteringFourMomentumResidual" ->
   FullSimplify[-J pI+J pO+J(pI-pO)],
 "LiouvilleFourMomentumResidual" ->
   FullSimplify[-L pB+L pB],
 "TruePartitionResidual" ->
   FullSimplify[
     chiI eta+chiR eta+(1-chiI-chiR)eta-eta
   ]
|>
