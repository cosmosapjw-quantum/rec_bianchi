#!/usr/bin/env python3
"""REC H5: source-locked xe column and common nH/H scaling identity.

This program does NOT supply the five missing independent thermodynamic
columns, the full Bianchi/thermal-history Jacobian, or any physical epsilon.
It uses the exact represented source block inherited from RESPONSE01.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
from decimal import Decimal, localcontext

SRC_SHA = 'f94fc8df8b8c523177183a2e56c09adac2d93284f5439b9304ef4ae14229e0f6'
PARENT_CODE_SHA = 'ce47a2bc204c58c29cc0962aa78c2130e7381279953a78198d6de3fb693649ac'
PR135_REPORTED_DXE_F = Decimal('-49.2760921201')
ZERO = Decimal(0)
ONE = Decimal(1)


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def get_inputs(z: zipfile.ZipFile):
    import fnmatch
    names = z.namelist()
    pat = 'electron_response/inputs/execution/C7_attempt001/PRIMARY_*.jsonl'
    paths = sorted(n for n in names if fnmatch.fnmatch(n, pat))
    assert len(paths) == 4, f'expected four raw primary shards, found {len(paths)}'
    records = [json.loads(line) for p in paths for line in z.read(p).decode().splitlines() if line]
    assert len(records) == 132 and sorted(r['index'] for r in records) == list(range(132))
    pat2 = 'electron_response/execution/C7_attempt001/RESPONSE_*.jsonl'
    paths2 = sorted(n for n in names if fnmatch.fnmatch(n, pat2))
    assert len(paths2) == 7
    responses = [json.loads(line) for p in paths2 for line in z.read(p).decode().splitlines() if line]
    assert sorted(r['index'] for r in responses) == list(range(132))
    return sorted(records,key=lambda r:r['index']),{r['index']:r for r in responses}


def dot2(a, b):
    return sum((x*y for x,y in zip(a[:2], b[:2])), ZERO)


def row(p, adj, prec):
    from incoming_response import SOURCE_SHA256, parse_record, source_constant, scalar_constant, scalar_row, prefix_coefficients, SOURCE_ROWS, solve_block, residual
    p = parse_record(p)
    with localcontext() as ctx:
        ctx.prec=prec
        xe, xp = p.P[0],p.P[1]
        # s(theta,u) at fixed xHII, T, nH, H, incoming, table and M.
        s=list(source_constant(p,prec))
        for r,g,u in zip(SOURCE_ROWS,prefix_coefficients(p,prec),p.incoming):
            s[r] += g*u
        s=tuple(s)
        x,diag=solve_block(p,s,precision=prec)
        q=scalar_row(p,prec)
        d=scalar_constant(p,prec)
        F=d+dot2(q,x)
        # exact derivative wrt independent ambient xe:
        # dM/dxe=0, dG/dxe=0, dq/dxe=0,
        # ds_real,i/dxe=nH*alpha_i*xHII, dd/dxe=-(sum ds_i)/H.
        a=(p.nH * p.alpha[0]*xp,p.nH * p.alpha[1]*xp)
        v=a+(ZERO,)*311
        dx,_=solve_block(p,v,precision=prec)
        Dxe=dot2(q,dx)-(a[0]+a[1])/p.H
        adjrow=adj[p.index]
        assert adjrow['index']==p.index and adjrow['call_id']==p.call_id and adjrow['slot']==p.slot
        assert adjrow['source_sha256']==SOURCE_SHA256
        lam=[Decimal(y) for y in adjrow['lambda313']]
        adjxe=dot2(lam,v)-(a[0]+a[1])/p.H
        adjerr=abs(Dxe-adjxe)
        expected_scaling=xe*Dxe-F
        # Two independent finite-change constructions (fixed M & G).
        epsi=Decimal('0.000001')
        s_x=list(s);s_x[0]+=epsi*a[0];s_x[1]+=epsi*a[1]
        X_e,_=solve_block(p,tuple(s_x),precision=prec)
        F_e=d-epsi*(a[0]+a[1])/p.H+dot2(q,X_e)
        e_err=abs((F_e-F)/epsi-Dxe)
        t=Decimal('0.001')
        scale=t.exp()
        s_t=list(s)
        for i in range(2):s_t[i]+=(scale-ONE)*xe*a[i]
        X_t,_=solve_block(p,tuple(s_t),precision=prec)
        q_t=tuple(y/scale for y in q[:2])
        d_t=(d-((scale-ONE)*xe*(a[0]+a[1])/p.H))/scale
        F_t=d_t+dot2(q_t,X_t)
        # independent algebraic identity for all common density/H rescalings
        F_pred=(F+(scale-ONE)*xe*Dxe)/scale
        scaleerr=abs(F_t-F_pred)
        scale_backward=residual(p,dx,v,precision=prec)['maximum']
        return {
            'index':p.index,'call_id':p.call_id,'slot':p.slot,
            'z':str(p.z),'xe':str(xe),'H_s_inv':str(p.H),'nH_cm3':str(p.nH),
            'F0_prefix_real':str(F),'F_saved_native':str(p.saved_FH),
            'dF_dxe_fixed_xHII':str(Dxe),
            'dF_dln_nH_plus_dln_H':str(expected_scaling),
            'adjoint_vs_primal_error':str(adjerr),
            'direct_fd_derivative_error':str(e_err),
            'common_scaling_exact_identity_error':str(scaleerr),
            'primal_tangent_componentwise_backward_error':str(scale_backward),
            'Schur_det':str(diag['schur_determinant']),
        }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--module',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--precision',type=int,default=80)
    args=ap.parse_args()
    assert args.precision in (80,120)
    assert _hash(args.source)==SRC_SHA,'IMMUTABLE_SOURCE_HASH_MISMATCH'
    assert _hash(args.module)==PARENT_CODE_SHA,'PARENT_CODE_HASH_MISMATCH'
    sys.path.insert(0,str(args.module.parent))
    from incoming_response import SOURCE_SHA256
    from incoming_response import parse_record
    with zipfile.ZipFile(args.source) as z:
        assert z.testzip() is None,'SOURCE_ZIP_CRC_FAILURE'
        recs,adj = get_inputs(z)
    rows=[]
    for rec in recs:
        rows.append(row(rec, adj, args.precision))
    maximum=lambda key:max(Decimal(r[key]) for r in rows)
    point=rows[131]
    match=abs(Decimal(point['dF_dxe_fixed_xHII'])-PR135_REPORTED_DXE_F)
    tol={'adjoint':'1e-60','finite':'1e-60','scaling':'1e-60','backward':'1e-60'}
    checks={
        'all_132_points_bound_to_source':len(rows)==132,
        'source_immutable_SHA':_hash(args.source)==SRC_SHA,
        'parent_immutable_code_SHA':_hash(args.module)==PARENT_CODE_SHA,
        'primal_vs_preexisting_adjoint':maximum('adjoint_vs_primal_error')<Decimal(tol['adjoint']),
        'finite_xe_delta_matches_local_affine':maximum('direct_fd_derivative_error')<Decimal(tol['finite']),
        'density_H_finite_scaling_identity':maximum('common_scaling_exact_identity_error')<Decimal(tol['scaling']),
        'tangent_residual':maximum('primal_tangent_componentwise_backward_error')<Decimal(tol['backward']),
        'PR135_same_point_xe_column':match < Decimal('3e-9'),
        'adversarial_reversed_sign_detected':abs(-Decimal(point['dF_dxe_fixed_xHII'])-PR135_REPORTED_DXE_F)>Decimal('1'),
    }
    report={
        'schema':'REC_H5_THERMO_BRIDGE01_XE_SCOPED_V1','mode':'frozen-prefix real affine local extension',
        'source_SHA256':SRC_SHA,'code_SHA256':_hash(args.module),
        'scope':'ambient xe column at fixed xHII plus common ln nH+ln H identity; not six independent columns',
        'precision':args.precision,'records':len(rows),
        'max_abs_adjoint_vs_primal':str(maximum('adjoint_vs_primal_error')),
        'max_abs_finite_xe_derivative_error':str(maximum('direct_fd_derivative_error')),
        'max_abs_common_scaling_exact_identity_error':str(maximum('common_scaling_exact_identity_error')),
        'max_componentwise_tangent_backward':str(maximum('primal_tangent_componentwise_backward_error')),
        'index131_PR135_dF_dxe':str(PR135_REPORTED_DXE_F),
        'index131_current_dF_dxe':point['dF_dxe_fixed_xHII'],
        'index131_agreement_abs':str(match),
        'checks':checks,'verdict':'PASS_SCOPED_XE_AND_COMMON_SCALING' if all(checks.values()) else 'FAIL_SCOPED',
        'not_certified':['remaining xHII,lnTR,lnTM,lnnH,lnH separate columns','continuous tube Lipschitz bound','native binary64 derivative','full-P source coefficient JVP','H5 physical epsilon or e0','H6/H7 full dynamics'],
        'no_new_native_or_old_history_calls':True,
    }
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'POINTS.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    (args.out/'SUMMARY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='not_certified'},indent=2))
    if not all(checks.values()):sys.exit(2)

if __name__=='__main__':main()
