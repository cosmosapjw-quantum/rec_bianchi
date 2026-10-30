"""Source-locked HD spectroscopy graph and structurally correlated error model.

All published measurements are actual PR164 inherited observations. The program
DOES NOT construct an experimental covariance, chi-square, sigma or p-value.
One 2-parameter calibration experiment is explicitly COUNTERFACTUAL.
Linear algebra uses exact rational arithmetic so result identity is not a
floating-point coincidence. No dependency on the 2019/2026 CDMS catalog.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json, hashlib

C_LIGHT_METRES_PER_SECOND = 299792458
CM_INV_TO_MHZ = F(299792458, 10000)  # c * 100 / 10^6 = 29979.2458 MHz/(cm^-1)
EDGES = ((2,0),(3,1),(4,3),(6,5),(7,6),(1,0),(2,1),(3,2),(4,3))
C = ((1,0,0,0,0,-1,-1,0,0),
     (0,1,0,0,0,0,-1,-1,0),
     (0,0,1,0,0,0,0,0,-1))
EXPECTED_SOURCE_SHA256 = '2d781a67a312a7f124955d3ad9c83fe739fa8fb0925390b5139df7d954e92dd8'
EXPECTED_INPUT_SHA256 = 'e568752432b1dc45e2b5ca37f8b767dad0ced0cea2c289fa29dc77ccdbf8da32'


def dot(a,b):
    return sum((x*y for x,y in zip(a,b)),F(0))


def matmul(a,b):
    bt = list(zip(*b))
    return [[dot(row,col) for col in bt] for row in a]


def rank(matrix):
    a = [[F(v) for v in row] for row in matrix]
    rows,cols=len(a),len(a[0]); r=0
    for j in range(cols):
        piv = next((k for k in range(r,rows) if a[k][j]),None)
        if piv is None: continue
        a[r],a[piv]=a[piv],a[r]
        fac=a[r][j]
        a[r]=[v/fac for v in a[r]]
        for k in range(rows):
            if k!=r and a[k][j]:
                fac=a[k][j]
                a[k]=[v-fac*w for v,w in zip(a[k],a[r])]
        r+=1
        if r==rows: break
    return r


def incidence():
    d=[]
    for upper,lower in EDGES:
        row=[0]*9
        row[upper],row[lower] = 1,-1
        d.append(row)
    return d


def read_source(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_INPUT_SHA256:
        raise ValueError('immutable original source input bytes changed')
    a=json.loads(raw.decode('utf-8'))
    if a['schema']!='REC_HD_SUNG_2022_MULTISPECTRAL_LAB_MEASURED_V1':
        raise ValueError('LAB_INPUT source schema changed')
    protect=a['protection']
    if (protect['parent_PR']!=163 or
        protect['parent_head']!='65c5c4c9105c9957418ff014d34e007e53a63b3b' or
        protect['canonical_DAG']!='28/88' or protect['REC_physical_DAG']!='0/313' or
        protect['original_35Hz']!='FAIL7/8' or protect['production']!='HOLD'):
        raise ValueError('protected original science contract modified')
    if a['primary_source']['joint_covariance'] is not None or protect['CDMS_2011_v2_covariance'] is not None:
        raise ValueError('covariance no longer missing; re-evaluate source and model')
    if protect['CDMS_2011_v2_original_raw']!='NOT_ACQUIRED':
        raise ValueError('cannot silently promote original raw acquisition')
    if len(a['inherited_measurements'])!=5 or len(a['line_parameters'])!=4:
        raise ValueError('measured rows count incorrect')
    if tuple((r['upper_J'],r['lower_J']) for r in a['inherited_measurements']+a['line_parameters'])!=EDGES:
        raise ValueError('measured row ordering changed')
    if a['primary_source']['doi']!='10.1016/j.jqsrt.2022.108412':
        raise ValueError('wrong paper')
    return a


def measurements_mhz(a):
    old=a['inherited_measurements']
    new=a['line_parameters']
    result=[]
    for item in old:
        if 'nominal_Hz' in item:
            result.append(F(item['nominal_Hz'])/1000000)
        else:
            result.append(F(item['nominal_cm_minus1'])*CM_INV_TO_MHZ)
    result.extend(F(item['nu0_cm_minus1'])*CM_INV_TO_MHZ for item in new)
    return result


def two_parameter_sung_calibration(x):
    """Exploratory nominal correction δf_j=u+v*x_j, x in cm^-1, f in MHz.

    No claim that this describes actual calibration errors. Independent fits,
    pressure-shift uncertainty and other error terms remain unmodeled.
    """
    if len(x)!=4: raise ValueError('four measured Sung centers required')
    b = [[F(0),F(0)] for _ in range(9)]
    for j in range(4): b[5+j]=[F(1),F(x[j])]
    return b


def calculate(path):
    a=read_source(path)
    y=measurements_mhz(a)
    D=incidence()
    if rank(D)!=6 or rank(C)!=3 or matmul(C,D)!=[[F(0)]*9 for _ in range(3)]:
        raise ValueError('incidence/cycle rank closure mismatch')
    r=[dot(row,y) for row in C]
    x=[F(t['nu0_cm_minus1']) for t in a['line_parameters']]
    B=two_parameter_sung_calibration(x)
    CB=matmul(C,B)
    # The printed cycle residual is old minus Sung. Inserting a common
    # Sung shift changes cycles through CB, whose entries are negative.
    M=[[-v for v in row] for row in CB]
    if M!=[[2,x[0]+x[1]],[2,x[1]+x[2]],[1,x[3]]]:
        raise ValueError('Sung common-calibration basis mismatch')
    if rank(M)!=2:
        raise ValueError('common calibration projection rank changed')
    # Unique left null direction normalized to l[2] = 1.
    l0 = ((x[1]+x[2])/2 - x[3])/(x[0]-x[2])
    ell=[l0,-F(1,2)-l0,F(1)]
    if [dot(ell,list(col)) for col in zip(*M)]!=[0,0]:
        raise ValueError('left-null invariant failed')
    invariant=dot(ell,r)
    # Fit first two exact nominal cycles with the hypothetical u,v.
    v=(r[0]-r[1])/(x[0]-x[2])
    u=(r[0]-v*(x[0]+x[1]))/2
    fitted=[dot(row,[u,v]) for row in M]
    if fitted[0]!=r[0] or fitted[1]!=r[1]:
        raise ValueError('first-two calibration witness failed')
    remainder=r[2]-fitted[2]
    if remainder!=invariant:
        raise ValueError('invariant exact arithmetic failed')
    # Status claims: "measured rows" are 9, but graph rank is only 6.
    return {
        'schema':'REC_HD_SOURCE_COVARIANCE_RECONSTRUCTION_V1',
        'data_identity': {'parent_source_archive_sha256':EXPECTED_SOURCE_SHA256,
                          'source_record':'PR164 data/LAB_INPUT.json',
                          'source_lab_input_sha256':EXPECTED_INPUT_SHA256,
                          'primary_sung_doi':'10.1016/j.jqsrt.2022.108412'},
        'measured_edges':len(EDGES), 'levels':9, 'incidence_rank':rank(D),
        'connected_components':[[0,1,2,3,4],[5,6,7],[8]],
        'measured_cycle_count':3, 'cycle_residuals_nominal_MHz':[format_decimal(z) for z in r],
        'conditional_calibration_model': {
            'status':'COUNTERFACTUAL_SOURCE_NUISANCE_BASIS_NOT_EMPIRICALLY_FITTED',
            'model':'Sung center corrections δ_j=u+v*x_j; x_j cm^-1; δ_j MHz',
            'C_times_source_design':[ [format_decimal(t) for t in row] for row in CB],
            'projection_rank':rank(CB), 'cycle_invariant_count':3-rank(CB),
            'left_null_normalized':[format_decimal(z) for z in ell],
            'calibration_invariant_nominal_cycle_MHz':format_decimal(invariant),
            'calibration_invariant_exact_rational_MHz':str(invariant),
            'illustrative_exact_fit_first_two_u_MHz':format_decimal(u),
            'illustrative_exact_fit_first_two_v_MHz_per_cm_inverse':format_decimal(v),
            'illustrative_remaining_third_nominal_MHz':format_decimal(remainder),
            'claim':'Nominal cycles cannot all vanish under only a shared u+v*x correction; this is NOT empirical exclusion of calibration or data.'
        },
        'covariance': {'actual_full_9x9':None, 'actual_cycle_3x3':None,
             'model':'Cov(y)=Σ_fit+Σ_exp_systematic+BΩB^T+Σ_cross (not numerically identified)',
             'cycle_propagation':'Cov(Cy)=C Cov(y) C^T',
             'full_rank_gls_identity':'min_E (y-D E)^T V^-1 (y-D E)=(Cy)^T(CVC^T)^-1(Cy) if V positive-definite',
             'statistical_sigma':None, 'chi_square':None, 'p_value':None,
             'fit_reported_errors_not_total':True,
             'Sung_Table7_scope':'Line-shape parameter correlations (width/shift/temperature), NOT established inter-line-center covariance'},
        'CDMS_2011_v2_source_status':'OFFICIAL_ARCHIVE_DISCOVERED_BYTES_NOT_ACQUIRED',
        'protection': {'original_35Hz':'FAIL7/8', 'canonical_DAG':'28/88',
                       'REC_physical_DAG':'0/313', 'REC_EXP_SPECTRAL':'PARTIAL',
                       'H5_epsilon':None,'H6':'OPEN','H7':'OPEN',
                       'L4_ready':False,'REI_activation':False,
                       'production':'HOLD','auto_next_node':False},
        'different_author_R6_C9':'NOT_RUN', 'native_subagent':'NOT_RUN'
    }


def format_decimal(x):
    from decimal import Decimal,localcontext
    with localcontext() as ctx:
        ctx.prec=42
        return format(Decimal(x.numerator)/Decimal(x.denominator),'.12f')


def project_covariance(V):
    """Pure structural map C V C^T. Caller supplies trustworthy source V.

    No default/synthetic V is provided by this module, and this function
    makes no claim that a passed matrix is a physical experimental covariance.
    """
    if len(V)!=9 or any(len(row)!=9 for row in V):
        raise ValueError('Expected original nine-row experimental covariance')
    A=[[F(v) for v in row] for row in V]
    if A!=[list(row) for row in zip(*A)]:
        raise ValueError('Covariance not symmetric')
    # This checks nonnegative diagonal entries, not that V is PD/PSD.
    if any(A[i][i]<0 for i in range(9)):
        raise ValueError('Negative marginal variance')
    return matmul(matmul(C,A), list(zip(*C)))


def save(path_in,path_out):
    result=calculate(path_in)
    Path(path_out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--input', default=str(Path(__file__).resolve().parents[1]/'input/LAB_INPUT_PR164_IMMUTABLE.json'))
    p.add_argument('--output', default=str(Path(__file__).resolve().parents[1]/'evidence/RESULTS.json'))
    args=p.parse_args()
    save(args.input,args.output)
