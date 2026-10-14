Needs["xAct`xTensor`"];
DefManifold[M9,4,{ia,ib,ic,id,ie,iff}];
DefMetric[-1,g9[-ia,-ib],CD,{";","D"}];
DefTensor[k[ia],M9];
DefTensor[xi[-ia],M9];
DefTensor[fn[],M9];
DefTensor[jj[],M9];
DefTensor[chi[],M9];
DefTensor[HH[],M9];
DefTensor[Xg[],M9];
killingSplit=ToCanonical[ContractMetric[
 k[ia]k[ib]CD[-ia][xi[-ib]] -
 (1/2) k[ia]k[ib](CD[-ia][xi[-ib]]+CD[-ib][xi[-ia]])
]];
rSource=ToCanonical[ContractMetric[Expand[
 k[ia] CD[-ia][jj[]-chi[] fn[]]
 -k[ia] CD[-ia][jj[]]
 +chi[] k[ia] CD[-ia][fn[]]
 +fn[] k[ia] CD[-ia][chi[]]
]]];
rRate=ToCanonical[ContractMetric[Expand[
 k[ia] CD[-ia][HH[]fn[]]
 -fn[] k[ia]CD[-ia][HH[]]
 -HH[]k[ia]CD[-ia][fn[]]
]]];
rs={killingSplit,rSource,rRate};
out=<|"WolframVersion"->System`$Version,
"xTensorVersion"->ToString[xAct`xTensor`$Version,InputForm],
"signature"->"-+++",
"identities"->{"Killing_vector_symmetric_split_algebra",
"transport_source_product_rule","positive_rate_occupation_current_rule"},
"residuals"->(ToString[#,InputForm]&/@rs),
"all_exact_zero"->And@@(TrueQ[#===0]&/@rs),
"assumptions"->"The Killing conservation conclusion additionally assumes geodesic k^b nabla_b k^a=0 and Killing xi satisfying nabla_(a xi_b)=0; not proved by the zero residual alone."|>;
Print[ExportString[out,"RawJSON"]];
Export["/home/cosmosapjw/Dropbox/bianchi/rec_bianchi/research/rec_c9_optim_20261015/XACT_RESULT.json",out,"RawJSON"];
If[!out["all_exact_zero"],Exit[2]];
