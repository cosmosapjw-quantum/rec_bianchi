"""Exact scientific-input binding for native-reference split restart records.

This binds inputs, not a scientific-equivalence test on numerical outputs.
All dataclass fields (including arrays and future fields) participate. Array
layout/endianness are canonical content details; scalar float bits, shapes,
field types and values are retained. No arbitrary repr or object identity.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import copy
import hashlib
import json
import math
from typing import Any
import numpy as np

SCHEMA = 'rec-split-domain-restart/v2'
CONTEXT_SCHEMA = 'rec-split-scientific-context/v1'
REPRESENTATION = 'NATIVE_PROXY_ALGEBRA_ONLY_NOT_PHYSICAL_COM'


def _encode(value: Any) -> Any:
    if value is None or type(value) in (str, bool):
        return value
    if isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_)):
        return {'integer': str(int(value))}
    if isinstance(value, (float, np.floating)):
        if np.asarray(value).dtype.itemsize > 8:
            raise TypeError('extended-precision scalar requires an explicit encoding')
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('scientific context must be finite')
        return {'binary64_hex': number.hex()}
    if isinstance(value, np.ndarray):
        if value.dtype.kind not in 'biufc' or value.dtype.hasobject:
            raise TypeError('scientific arrays must have a numeric dtype')
        if not np.isfinite(value).all():
            raise ValueError('scientific arrays must be finite')
        canonical = np.ascontiguousarray(value.astype(value.dtype.newbyteorder('<'), copy=False))
        return {'array_dtype': canonical.dtype.str,
                'shape': list(canonical.shape),
                'data_sha256': hashlib.sha256(canonical.tobytes(order='C')).hexdigest()}
    if is_dataclass(value) and not isinstance(value, type):
        return {'dataclass': type(value).__module__ + '.' + type(value).__qualname__,
                'fields': {field.name: _encode(getattr(value, field.name)) for field in fields(value)}}
    if isinstance(value, Mapping):
        if not all(type(key) is str for key in value):
            raise TypeError('scientific mapping keys must be strings')
        return {'mapping': {key: _encode(value[key]) for key in sorted(value)}}
    if isinstance(value, (tuple, list)):
        return {type(value).__name__: [_encode(item) for item in value]}
    raise TypeError('unsupported scientific context type: ' + type(value).__qualname__)


def _digest(payload: Mapping[str, Any]) -> str:
    try:
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=True, allow_nan=False).encode('ascii')
    except (TypeError, ValueError) as exc:
        raise ValueError('invalid scientific context serialization') from exc
    return hashlib.sha256(raw).hexdigest()


def scientific_context(replacement: Any, constants: Mapping[str, Any]) -> dict[str, Any]:
    """Exhaustively bind a dataclass replacement, its snapshot and constants."""
    if not is_dataclass(replacement) or isinstance(replacement, type):
        raise TypeError('replacement must be a dataclass instance')
    if not isinstance(constants, Mapping):
        raise TypeError('constants must be an explicit mapping')
    return {
        'schema': CONTEXT_SCHEMA,
        'replacement': _encode(replacement),
        'constants': _encode(constants),
        'conventions': {
            'metric': '-+++',
            'frame': 'hydrogen_orthonormal_tetrad',
            'frequency': 'ordinary_Hz',
            'occupation': 'dimensionless',
            'representation': REPRESENTATION,
        },
    }


def bind_restart_context(record: Mapping[str, Any], context: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping) or record.get('schema') != 'rec-split-domain-restart/v1':
        raise ValueError('binding requires a newly generated native v1 record')
    if not isinstance(context, Mapping) or context.get('schema') != CONTEXT_SCHEMA:
        raise ValueError('invalid scientific context schema')
    result = copy.deepcopy(dict(record))
    result['schema'] = SCHEMA
    result['representation'] = REPRESENTATION
    result['scientific_context'] = copy.deepcopy(dict(context))
    result['scientific_context_sha256'] = _digest(context)
    return result


def require_restart_context(record: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    """Reject before restoring state or solving. Legacy records need no migration."""
    if not isinstance(record, Mapping) or record.get('schema') != SCHEMA:
        raise ValueError('unsupported split-domain restart schema; legacy unbound record rejected')
    supplied = record.get('scientific_context')
    if not isinstance(supplied, Mapping) or supplied.get('schema') != CONTEXT_SCHEMA:
        raise ValueError('missing scientific context')
    if record.get('scientific_context_sha256') != _digest(supplied):
        raise ValueError('scientific context digest mismatch')
    if record.get('representation') != REPRESENTATION or _digest(supplied) != _digest(expected):
        raise ValueError('restart scientific context differs from current inputs')
