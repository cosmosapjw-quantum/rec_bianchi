"""Canonical point pair for one shared radiation/atomic energy event."""
import numpy as np

def canonicalize_shared_event(independent):
    value=np.asarray(independent,dtype=np.float64)
    if value.shape!=(5,) or not np.all(np.isfinite(value)):
        raise ValueError('SHARED_EVENT_VECTOR_SHAPE_OR_NONFINITE')
    paired=value.copy()
    paired[4]=-paired[3]
    return paired
