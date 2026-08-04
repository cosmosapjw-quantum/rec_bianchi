ClearAll["Global`*"];

nuOut=nuIn/(1+h nuIn(1-mu)/(M c^2));

massShellResidual=FullSimplify[
 -2 M h(nuIn-nuOut)
 +2 h^2 nuIn nuOut(1-mu)/c^2,
 Assumptions->{M>0,c>0,h>0,nuIn>0,-1<=mu<=1}
];

covariantScale=(PiDotKi)/(PiDotQ+KiDotQ);
covariantResidual=FullSimplify[
 2 PiDotKi
 -2 covariantScale PiDotQ
 -2 covariantScale KiDotQ
];

reverseIncoming=FullSimplify[
 PfDotKf-PiDotKi
 /. PfDotKf->PiDotKf+KiDotKf
 /. PiDotKi->PiDotKf+KiDotKf
];

reverseOutgoing=FullSimplify[
 PfDotKi-PiDotKf
 /. PfDotKi->PiDotKi-KiDotKf
 /. PiDotKi->PiDotKf+KiDotKf
];

<|
 "MassShellToComptonResidual"->massShellResidual,
 "CovariantOutgoingScaleResidual"->covariantResidual,
 "ReverseIncomingEnergyInvariant"->reverseIncoming,
 "ReverseOutgoingEnergyInvariant"->reverseOutgoing,
 "SameEventTransferResidual"->
  FullSimplify[{d0,d1,d2,d3}+{-d0,-d1,-d2,-d3}]
|>
