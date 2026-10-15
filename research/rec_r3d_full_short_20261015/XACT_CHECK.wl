(* Exact Bianchi-I Killing-momentum and xAct metric-identity checks.
   Signature (-+++), coordinate time t, q=db/d ln a.
   Independently checks the formulas used by REC causal transport. *)
$HistoryLength = 0;
AppendTo[$Path, "/home/cosmosapjw/rec_theory_runs/REC_R3D_HFULL_STEP_20261015/xact_runtime"];
Print["XACT_FILE=", FindFile["xAct`xTensor`"]];
Needs["xAct`xTensor`"];
DefManifold[RecM,4,{a,b,c,d,e,f}];
DefMetric[-1, gRec[-a,-b], DRec, {";", "∇"}];
compat = ToCanonical[DRec[-a][gRec[-b,-c]]];
r[d_,q_,mu_] := Exp[d] Sqrt[(1-mu^2) Exp[-2 q d]+mu^2 Exp[4 q d]];
rate = FullSimplify[(D[r[d,q,mu],d]/r[d,q,mu]/.d->0) -
          (1 + q(3 mu^2-1)), Assumptions->Element[{mu,q},Reals]&&-1<mu<1];
metric = DiagonalMatrix[{-1,aa[t]^2 Exp[-2 beta[t]],
                                aa[t]^2 Exp[-2 beta[t]],
                                aa[t]^2 Exp[4 beta[t]]}];
volume = FullSimplify[Sqrt[-Det[metric]],Assumptions->aa[t]>0];
densityJac = FullSimplify[Det[DiagonalMatrix[{Exp[-q d],Exp[-q d],Exp[2 q d]}]]];
scalarQzero = FullSimplify[r[d,0,mu]-Exp[d],Assumptions->d>0&&-1<mu<1];
checks = <|"xAct_metric_compatibility_zero" -> SameQ[compat,0],
     "directional_energy_rate_zero" -> SameQ[rate,0],
     "spatial_volume_is_a3" -> SameQ[volume,aa[t]^3],
     "Killing_anisotropic_jacobian_one" -> SameQ[densityJac,1],
     "FLRW_limit_zero" -> SameQ[scalarQzero,0]|>;
Print["REC_XACT_RESULTS=", InputForm[checks]];
If[!And@@Values[checks], Exit[5]];
Exit[0];
