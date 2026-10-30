"""Conservative approximate covariance from 2011 CDMS v2 HD.fit PRINTED values.

This is NOT the full precision SPFIT .var output (not acquired). Correlations
and uncertainty digits printed in HD.fit have limited precision. No automatic
2011-to-2026 spectroscopy catalogue or production source substitution.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

PARAMETERS=('E1','Y01','Y02','Y03','Y11/2','Y12/2')
SIGMA_MHZ=np.array([36.,2.73,0.073,0.000314,2.73,0.07])
PAIR_CORRELATIONS={
 (0,1):.776846,(0,2):-.596308,(0,3):-.017900,(0,4):-.776658,(0,5):.625612,
 (1,2):-.893152,(1,3):-.032644,(1,4):-.999867,(1,5):.938576,
 (2,3):-.258060,(2,4):.888308,(2,5):-.954808,
 (3,4):.047571,(3,5):-.028563,(4,5):-.938366,
}
def approximate_covariance():
    corr=np.eye(6)
    for (i,j),x in PAIR_CORRELATIONS.items():
        corr[i,j]=corr[j,i]=x
    cov=SIGMA_MHZ[:,None]*corr*SIGMA_MHZ[None,:]
    eig=np.linalg.eigvalsh(corr)
    if not np.all(eig>0):raise ArithmeticError('Printed correlation matrix is not SPD')
    return {'parameters':PARAMETERS,'sigma_mhz':SIGMA_MHZ.tolist(),
            'rounded_correlation_matrix':corr.tolist(),'approx_covariance_mhz2':cov.tolist(),
            'corr_min_eigenvalue':float(eig[0]),'corr_condition_number':float(eig[-1]/eig[0]),
            'interpretation':'PRINTED_PARAMETER_COVARIANCE_ONLY_NOT_FULL_PRECISION_SPFIT_COVARIANCE'}
if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'evidence/CDMS_2011_PRINTED_APPROX_COVARIANCE.json'
    p.write_text(json.dumps(approximate_covariance(),indent=2)+'\n')
    print('wrote',p)
