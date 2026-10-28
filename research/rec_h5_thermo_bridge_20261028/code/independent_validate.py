#!/usr/bin/env python3
"""Bounded independent sparse solve and Decimal precision comparison, 3 rows."""
import argparse,sys,json,zipfile,hashlib
from pathlib import Path
from decimal import Decimal,localcontext
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


def sparse_matrix(p):
    rr=[];cc=[];vv=[]
    def setv(i,j,v):rr.append(i);cc.append(j);vv.append(float(v))
    for i in range(2):
        for j in range(2):setv(i,j,p.A[i][j])
        for b in range(311):setv(i,b+2,p.B[i][b]);setv(b+2,i,p.C_storage[i][b])
    for b in range(311):
        setv(2+b,2+b,p.V[0][b])
        if b>0:setv(2+b,1+b,p.V[1][b])
        if b<310:setv(2+b,3+b,p.V[2][b])
    return coo_matrix((vv,(rr,cc)),shape=(313,313)).tocsc()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--points',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    sys.path.insert(0,str(args.module.parent))
    from incoming_response import parse_record,solve_block,residual
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from thermo_bridge import get_inputs,row,SRC_SHA,PARENT_CODE_SHA
    assert hashlib.sha256(args.source.read_bytes()).hexdigest()==SRC_SHA
    assert hashlib.sha256(args.module.read_bytes()).hexdigest()==PARENT_CODE_SHA
    with zipfile.ZipFile(args.source) as z:records, adj=get_inputs(z)
    r80={r['index']:r for r in map(json.loads,args.points.read_text().splitlines())}
    summary=[]
    for i in (0,65,131):
        p=parse_record(records[i]); v=np.zeros(313)
        a=[p.nH*p.alpha[j]*p.P[1] for j in range(2)]
        v[:2]=[float(z) for z in a]
        dx=spsolve(sparse_matrix(p),v)
        F_scipy=(float(p.beta[0])*dx[0]+float(p.beta[1])*dx[1]-(v[0]+v[1]))/float(p.H)
        F_80=float(Decimal(r80[i]['dF_dxe_fixed_xHII']))
        rel_scipy=abs(F_scipy-F_80)/max(abs(F_80),1e-300)
        r120=row(records[i],adj,120)
        dec120=Decimal(r120['dF_dxe_fixed_xHII'])
        dec80=Decimal(r80[i]['dF_dxe_fixed_xHII'])
        dec_gap=abs(dec120-dec80)
        assert rel_scipy<1e-9, (i,rel_scipy)
        assert dec_gap<Decimal('1e-65'),(i,dec_gap)
        assert Decimal(r120['adjoint_vs_primal_error'])<Decimal('1e-70')  # inherited 80-digit adjoint; not a 120-digit oracle
        summary.append(dict(index=i,z=str(p.z),float_scipy_F=F_scipy,decimal80_F=str(dec80),
            decimal120_F=str(dec120),scipy_relative_error=rel_scipy,
            decimal80_vs120_absolute=str(dec_gap)))
    # Adversarial counterexample: independent xHII direction would alter M and
    # x1, so calling the fixed-xHII xe column a pure-H tangent is invalid.
    res={'schema':'REC_H5_THERMO_BRIDGE01_INDEPENDENT_VALIDATION_V1','results':summary,
         'scipy_relative_gate':1e-9,'decimal80_vs120_abs_gate':'1e-65',
         'verdict':'PASS_SCOPED','sampled_points':3,
         'not_checked':'full six-primitive Jacobian or native rounding derivative'}
    args.out.write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps(res,indent=2))
if __name__=='__main__':main()
