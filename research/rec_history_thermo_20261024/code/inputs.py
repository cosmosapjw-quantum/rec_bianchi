"""Standalone immutable input loading; no project package/native imports."""
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np


def verify_inputs(unit):
    manifest = json.loads((unit/'inputs/INPUT_IDENTITIES.json').read_text())
    for item in manifest['files']:
        b = (unit/item['path']).read_bytes()
        if len(b) != item['bytes'] or hashlib.sha256(b).hexdigest() != item['sha256']:
            raise ValueError('IMMUTABLE_INPUT_IDENTITY:'+item['path'])
    return manifest


def load(unit):
    verify_inputs(unit)
    meta = {}
    virtual = np.full((311,13), np.nan)
    rr = np.zeros((2,2)); rv = np.zeros((2,311)); vr = np.zeros((2,311)); vv = np.zeros((3,311))
    real_rows = np.full((2,5), np.nan)
    seen = set()
    with (unit/'inputs/target_native_snapshot.csv').open(newline='') as f:
        for row in csv.reader(f):
            kind = row[0]
            if kind == 'META':
                meta[row[1]] = float(row[2])
            elif kind == 'VIRTUAL':
                i = int(row[1])
                if i in seen or not 0 <= i < 311 or len(row) != 15:
                    raise ValueError('SNAPSHOT_VIRTUAL_ROWS')
                virtual[i] = list(map(float,row[2:])); seen.add(i)
            elif kind == 'REAL':
                real_rows[int(row[1])] = list(map(float,row[2:]))
            elif kind in ('TRR','TRV','TVR','TVV'):
                {'TRR':rr,'TRV':rv,'TVR':vr,'TVV':vv}[kind][int(row[1]),int(row[2])] = float(row[3])
    if len(seen) != 311 or not np.all(np.isfinite(virtual)) or not np.all(np.isfinite(real_rows)):
        raise ValueError('SNAPSHOT_MISSING_OR_NONFINITE')
    with np.load(unit/'inputs/PREPARED_BLOCKS.npz',allow_pickle=False) as f:
        prepared = {k:f[k].copy() for k in f.files}
    alpha = np.loadtxt(unit/'inputs/Alpha_inf.dat').reshape(100,40,2)
    rrates = np.loadtxt(unit/'inputs/R_inf.dat')
    two = np.loadtxt(unit/'inputs/two_photon_tables.dat')
    if alpha.shape != (100,40,2) or rrates.shape != (100,) or two.shape != (311,5):
        raise ValueError('SOURCE_TABLE_SHAPE')
    if not np.all(np.isfinite(alpha)) or not np.all(alpha > 0) or not np.all(np.isfinite(rrates)) or not np.all(rrates > 0):
        raise ValueError('SOURCE_TABLE_RATE_DOMAIN')
    if not np.all(np.isfinite(two)) or not np.all(np.diff(two[:,0]) > 0) or np.any(two[:,1:] < 0):
        raise ValueError('SOURCE_TABLE_VIRTUAL_DOMAIN')
    # Scalar libm log and source-order normalization preserve the table reader.
    la = np.array([math.log(x) for x in alpha.flat]).reshape(100,40,2).transpose(2,1,0)
    lr = np.array([math.log(x) for x in rrates])
    rates = two[:,1:].T.copy()
    norm = 8.2206/sum(float(x) for x in rates[1,:140])
    rates[1,:140] *= norm
    theta = np.array([meta['xe'],meta['xHII'],meta['TR_eV_rescaled'],meta['TM_eV_rescaled'],meta['nH_cm3'],meta['H_sInv']])
    incoming = np.r_[virtual[:,1], meta['Dfplus_Lya'],meta['Dfplus_Lyb']]
    return {'meta':meta,'virtual':virtual,'real_rows':real_rows,'Trr':rr,'Trv':rv,'Tvr':vr,'Tvv':vv,
            'prepared':prepared,'log_alpha':la,'log_R':lr,'energy':two[:,0],'rates':rates,
            'theta':theta,'incoming':incoming,'normalization_A2s':norm}
