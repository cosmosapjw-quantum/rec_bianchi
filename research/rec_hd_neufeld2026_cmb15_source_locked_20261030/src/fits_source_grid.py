"""Read only the original Neufeld 2026 FITS structure, preserving IEEE NaNs.

A small documented FITS reader for primary header, BINTABLE T/density and LOGPOP
NAXIS=(15,111,161). No guessing of orientation or reliance on imports that turn
NaNs into zero. Immutable source digest and original HDU header checks required.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, math, re
import numpy as np

STANDARD_SHA256 = '0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1'
ALTERNATE_SHA256 = '1fc3588b32e1423a5c56c68df43ee0385f38f62424615971857b403bf02d45de'
FITS_SIZE=2174400
FITS_BLOCK=2880


def _card_value(line:bytes):
    if line[8:10]!=b'= ':return None
    raw=line[10:80].decode('ascii').split(' / ')[0].strip()
    if not raw:return None
    if raw.startswith("'"):
        return raw[1:].split("'",1)[0].rstrip()
    if raw in ('T','F'):return raw=='T'
    try:return int(raw)
    except ValueError:
        try:return float(raw.replace('D','E'))
        except ValueError:return raw


def load_fits(path:Path, *, source_kind:str):
    data=Path(path).read_bytes()
    if len(data)!=FITS_SIZE:raise ValueError('Original FITS size wrong')
    sha=hashlib.sha256(data).hexdigest()
    want={'standard':STANDARD_SHA256,'alternate':ALTERNATE_SHA256}[source_kind]
    if sha!=want:raise ValueError('Original FITS SHA256 wrong')
    blocks=[];off=0
    while off<len(data):
        cards=[];start=off
        while True:
            chunk=data[off:off+FITS_BLOCK];off+=FITS_BLOCK
            if len(chunk)!=FITS_BLOCK:raise ValueError('Truncated FITS header')
            lines=[chunk[i:i+80] for i in range(0,FITS_BLOCK,80)]
            cards.extend(lines)
            if any(line.startswith(b'END ') for line in lines):break
        meta={line[:8].decode('ascii').strip():_card_value(line) for line in cards if line[8:10]==b'= '}
        naxis=int(meta.get('NAXIS',0));dims=[int(meta['NAXIS'+str(i)]) for i in range(1,naxis+1)]
        if meta.get('XTENSION')=='BINTABLE':
            size=int(meta['NAXIS1'])*int(meta['NAXIS2'])+int(meta.get('PCOUNT',0))
        else:
            size=(abs(int(meta['BITPIX']))//8)*math.prod(dims) if naxis else 0
        content=data[off:off+size]
        if len(content)!=size:raise ValueError('Truncated FITS data')
        off+=((size+FITS_BLOCK-1)//FITS_BLOCK)*FITS_BLOCK
        blocks.append((meta,content,start))
    if len(blocks)!=6:raise ValueError('Unexpected Neufeld FITS HDU count')
    # Published table axes: two BINTABLEs, each one double/row.
    tmeta,tbytes,_=blocks[1];nmeta,nbytes,_=blocks[2]
    if not (tmeta.get('EXTNAME')=='TEMPERATURE' and tmeta.get('TFORM1')=='D' and
            nmeta.get('EXTNAME')=='DENSITY' and nmeta.get('TFORM1')=='D'):
        raise ValueError('Temperature/density column definitions mismatch')
    temperature=np.frombuffer(tbytes,dtype='>f8').astype('float64')
    density=np.frombuffer(nbytes,dtype='>f8').astype('float64')
    image_meta, image_bytes,_=blocks[5]
    if image_meta.get('EXTNAME')!='LOGPOP' or [image_meta.get('NAXIS'+str(i)) for i in (1,2,3)]!=[15,111,161]:
        raise ValueError('Unrecognized Neufeld logpop FITS image axis')
    logp=np.frombuffer(image_bytes,dtype='>f8').reshape((161,111,15)).astype('float64')
    if temperature.shape!=(161,) or density.shape!=(111,):raise ValueError('Unexpected grid dimensions')
    if not np.isfinite(temperature).all() or not np.isfinite(density).all():raise ValueError('Invalid T/n grid')
    if not np.isnan(logp).any():raise ValueError('FITS NaNs unexpectedly erased')
    g=1+2*np.arange(15)
    p=np.where(np.isfinite(logp), g[None,None,:]*np.power(10, np.where(np.isfinite(logp),logp,-1000)), np.nan)
    known=np.nansum(p,axis=2)
    return {'source_sha256':sha,'source_kind':source_kind,'temperatures_K':temperature,
            'densities_cm3':density,'logpop':logp,'populations':p,'known_mass':known,
            'nan_count':int(np.isnan(logp).sum()),'nan_by_cell':np.isnan(logp).sum(axis=2),
            'metadata_nan_count':image_meta.get('NANCOUNT'),
            'meta':image_meta,'HDU_count':len(blocks)}

if __name__=='__main__':
 import sys
 for s,f in zip(('standard','alternate'),sys.argv[1:]):
  v=load_fits(Path(f),source_kind=s)
  print(s, v['source_sha256'], v['populations'].shape, 'nan',v['nan_count'],'meta_nan',v['metadata_nan_count'],
        'nonmissing sum range',v['known_mass'].min(),v['known_mass'].max())
