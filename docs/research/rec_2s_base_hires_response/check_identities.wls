(* New fixed-population alpha direction and weak-form identities only. *)
ClearAll[aa, xg, xu, ec, et, q, gc, gt, ut, w];
fc = 1/(ec - 1); ft = 1/(et - 1);
dc = -gc fc (1 + fc); dt = -gt ft (1 + ft);
paired = aa (xu (1 + fc) (1 + ft) - xg fc ft);
chain = aa ((xu (1 + ft) - xg ft) dc + (xu (1 + fc) - xg fc) dt);
stable = aa xg fc ft (q - 1);
stableD = gc ec D[stable, ec] + gt et D[stable, et] + (gc + gt) q D[stable, q];
sub = xu -> xg q/(ec et);
res = <|
  "single_field_stable" -> Together[(paired /. sub) - stable],
  "alpha_chain_both_legs" -> Together[(chain /. sub) - stableD],
  "lte_value" -> Together[stable /. q -> 1],
  "lte_alpha_direction" -> Together[(stableD /. q -> 1) - aa xg fc ft (gc + gt)],
  "weak_alpha" -> Together[w ((chain /. sub) - stableD)],
  "weak_number" -> Expand[(1 + 1) stable - 2 stable],
  "weak_energy" -> Expand[(ut + 1 - ut) stable - stable],
  "weak_quadratic" -> Expand[(ut^2 + (1-ut)^2) stable - (1-2 ut (1-ut)) stable]
|>;
ok = And @@ (TrueQ[# == 0] & /@ Values[res]);
out = <|"version" -> $Version, "installation_directory" -> $InstallationDirectory,
 "command_line" -> $CommandLine, "script_command_line" -> $ScriptCommandLine,
 "residuals" -> Map[ToString[#, InputForm] &, res], "passed" -> ok,
 "scope" -> "new fixed-population alpha direction and weak form; no O1/O2/O3 replay"|>;
Print[ExportString[out, "RawJSON"]];
outputPath = Last[$CommandLine];
exported = Check[Export[outputPath, out, "RawJSON"], $Failed];
exportOK = StringQ[exported] && FileExistsQ[outputPath];
Exit[If[ok && exportOK, 0, 1]];
