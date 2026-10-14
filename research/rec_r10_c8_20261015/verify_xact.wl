Needs["xAct`xTensor`"];
DefManifold[MC8,4,{aa,bb,cc,dd,ee,ff}];
DefMetric[-1,gg[-aa,-bb],CD,{";","D"}];
DefTensor[UU[aa],MC8];
DefTensor[nB[],MC8];
DefTensor[Xe[],MC8];
DefTensor[ff[],MC8];
DefTensor[fhat[],MC8];
DefTensor[rJ[],MC8];
DefTensor[rChi[],MC8];
DefTensor[FD[],MC8];
DefTensor[dFD[],MC8];
DefTensor[dJ[],MC8];
DefTensor[dChi[],MC8];
r1=ToCanonical[ContractMetric[Expand[
CD[-aa][nB[] UU[aa]]-nB[]CD[-aa][UU[aa]]-UU[aa]CD[-aa][nB[]]
]]];
r2=ToCanonical[ContractMetric[Expand[
CD[-aa][nB[] Xe[] UU[aa]]-Xe[] CD[-aa][nB[] UU[aa]]-nB[] UU[aa] CD[-aa][Xe[]]
]]];
r3=ToCanonical[ContractMetric[Expand[
UU[aa] CD[-aa][rJ[]-rChi[] ff[]]-UU[aa] CD[-aa][rJ[]]
+rChi[] UU[aa] CD[-aa][ff[]]+ff[]UU[aa]CD[-aa][rChi[]]
]]];
expr=(FD[]+dFD[])(rJ[]+dJ[]-(rChi[]+dChi[])fhat[])-FD[](rJ[]-rChi[]ff[]);
decomp=-FD[]rChi[](fhat[]-ff[])+dFD[](rJ[]+dJ[]-(rChi[]+dChi[])fhat[])+FD[](dJ[]-dChi[]fhat[]);
r4=ToCanonical[ContractMetric[Expand[expr-decomp]]];
vals={r1,r2,r3,r4};
out=<|"WolframVersion"->System`$Version,
"xTensorVersion"->ToString[xAct`xTensor`$Version,InputForm],
"signature"->"-+++",
"identities"->{"baryon_current_divergence_product",
"ionization_current_divergence_product","emission_absorption_convective_product",
"nonlinear_scalar_rate_source_difference_decomposition"},
"residuals"->(ToString[#,InputForm]&/@vals),
"all_exact_zero"->And@@(TrueQ[#===0]&/@vals),
"claim_scope"->"Pure covariant current algebra plus exact scalar rate-source decomposition, no Einstein, stiff or HyRec source certificate."|>;
Export["/home/cosmosapjw/rec_theory_runs/REC_R10_C8_20261015/XACT_RESULT.json",out,"RawJSON"];
Print[ExportString[out,"RawJSON"]];
If[!out["all_exact_zero"],Exit[2]];
