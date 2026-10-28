cpuStart=TimeUsed[];wallStart=AbsoluteTime[];memoryStart=MemoryInUse[];
result=MemoryConstrained[TimeConstrained[
 Module[{aa,bb,cc,vv,sr,sv,schur,rhs,detq,xr,xv,mat,src,sol,fh,scalarZero,blockZero,affineZero,hessianZero,toy,wrongToy,wrongResidual},
 aa={{a11,a12},{a21,a22}};bb={b1,b2};cc={c1,c2};vv=v0;
 sr={r1+g1*u1,r2+g2*u2};sv=g3*u3;
 schur=aa-Outer[Times,bb,cc]/vv;rhs=sr-bb*sv/vv;
 detq=schur[[1,1]]*schur[[2,2]]-schur[[1,2]]*schur[[2,1]];
 xr={(schur[[2,2]]*rhs[[1]]-schur[[1,2]]*rhs[[2]])/detq,
     (schur[[1,1]]*rhs[[2]]-schur[[2,1]]*rhs[[1]])/detq};
 xv=(sv-cc.xr)/vv;
 mat={{a11,a12,b1},{a21,a22,b2},{c1,c2,vv}};
 src=Append[sr,sv];sol=Append[xr,xv];
 scalarZero=Expand[nH*(s*x1*(alpha-alphaEq)+alpha*(xe*p-s*x1))-nH*(alpha*xe*p-alphaEq*s*x1)];
 blockZero=Together /@ (mat.sol-src);
 fh=(-cTotal+{beta1,beta2}.xr)/hubble;
 affineZero=Together[(fh/.{u1->(1-t)*u1+t*w1,u2->(1-t)*u2+t*w2,u3->(1-t)*u3+t*w3})-(1-t)*fh-t*(fh/.{u1->w1,u2->w2,u3->w3})];
 hessianZero=Table[Together[D[fh,ui,uj]],{ui,{u1,u2,u3}},{uj,{u1,u2,u3}}];
 toy=Inverse[{{3,-1},{-2,4}}].{1,2};
 wrongToy=Inverse[{{3,-2},{-1,4}}].{1,2};
 wrongResidual={{3,-1},{-2,4}}.wrongToy-{1,2};
 <|"scalar_identity"->scalarZero,"block_residual_identity"->blockZero,
 "affine_identity"->affineZero,"incoming_hessian"->hessianZero,
 "exact_toy_solution"->toy,"swapped_block_toy_residual"->wrongResidual,
 "conditions"->"v0 != 0 and det(Schur) != 0; real algebra, fixed coefficients; no numeric source calls"|>
 ],8,$TimedOut],512*1024^2,$MemoryLimit];
<|"result"->result,"kernel_cpu_seconds"->(TimeUsed[]-cpuStart),"wall_seconds"->(AbsoluteTime[]-wallStart),
 "memory_start_bytes"->memoryStart,"memory_end_bytes"->MemoryInUse[],
 "kernel_max_memory_bytes"->MaxMemoryUsed[],"platform"->$SystemID,"version"->$Version|>
