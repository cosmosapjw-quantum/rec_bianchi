ClearAll["Global`*"];

hyperbolicResidual=FullSimplify[
 Sinh[t]^2 Cosh[t]-(Cosh[3t]-Cosh[t])/4
];
besselResidual=FullSimplify[
 (BesselK[3,z]-BesselK[1,z])/4-BesselK[2,z]/z,
 Assumptions->{z>0},
 TransformationFunctions->{Automatic,FunctionExpand}
];
thermalResidual=FullSimplify[
 Exp[-beta(Ei+wi)]-Exp[-beta(Ef+wf)],
 Assumptions->{beta>0,Ei+wi==Ef+wf}
];
amp[vin_,vout_]:=-(f va/2)(
 1/(va-vin-I gam)+1/(va+vout+I gam)
);
<|
 "HyperbolicIdentityResidual"->hyperbolicResidual,
 "BesselRecurrenceResidual"->besselResidual,
 "MJNormalization"->4 Pi m^3 c^3 BesselK[2,z]/z,
 "ThermalAffinityResidual"->thermalResidual,
 "ReverseIncomingInvariant"->FullSimplify[PfKf-PiKi,Assumptions->{PfKf==PiKi}],
 "ReverseOutgoingInvariant"->FullSimplify[PfKi-PiKf,Assumptions->{PfKi==PiKf}],
 "TwoPAmplitudeResidual"->FullSimplify[amp[vin,vout]-amp[vinR,voutR],Assumptions->{vinR==vin,voutR==vout}]
|>
