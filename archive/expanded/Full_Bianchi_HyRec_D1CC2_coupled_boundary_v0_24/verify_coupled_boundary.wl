ClearAll["Global`*"];
beta={bx,by,bz}; edir={ex,ey,ez};
bdot={dbx,dby,dbz}; edot={dex,dey,dez};
gamma=1/Sqrt[1-beta.beta];
Dop=gamma(1-beta.edir);
vars=Join[beta,edir]; vels=Join[bdot,edot];
dlogDirect=FullSimplify[
 Grad[Log[Dop],vars].vels,
 Assumptions->{beta.beta<1,1-beta.edir>0}
];
dlogTarget=gamma^2 beta.bdot
 -(bdot.edir+beta.edot)/(1-beta.edir);
xexpr=(nuH-nuAbs)/dNu;
dxDirect=Grad[xexpr,{nuH,nuAbs,dNu}].
 {RH nuH,nuAbsDot,dLogDNu dNu};
<|
 "TiltDerivativeResidual"->FullSimplify[
  dlogDirect-dlogTarget,
  Assumptions->{beta.beta<1,1-beta.edir>0}
 ],
 "FrameFrequencyResidual"->FullSimplify[
  (RN+dlogDirect)-(RN+dlogTarget),
  Assumptions->{beta.beta<1,1-beta.edir>0}
 ],
 "DopplerCoordinateResidual"->FullSimplify[
  dxDirect-((nuH RH-nuAbsDot)/dNu-xexpr dLogDNu)
 ],
 "TruePartitionResidual"->FullSimplify[
  chiI eta+chiR eta+chiB eta-eta,
  Assumptions->chiI+chiR+chiB==1
 ],
 "TrueFourMomentumResidual"->FullSimplify[-J p+J p]
|>
