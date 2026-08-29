"""Explicit context-bound API for PR34's retained native-proxy reference algebra.

The original split_domain_replacement module remains unchanged.
This fixes restart-input attribution only; it does NOT turn eight eliminated
native proxies into physical COM occupation or bless the reference ledger.
"""
from __future__ import annotations

from collections.abc import Mapping
from scipy.constants import c, h
from full_bianchi_hyrec.recoil import original_hyrec_native as _native
from full_bianchi_hyrec.recoil import original_hyrec_physical_flux as _physical
from . import split_domain_replacement as _reference
from .split_domain_replacement import (
    LOCKED_INTERIOR_NATIVE_INDICES, LOCKED_CROSS_EDGES, LOCKED_INTERFACE_ABS_X,
    SplitDomainContext, SplitDomainOwnershipAudit, SplitDomainRegistry,
    SplitDomainSolution, SplitDomainRestartState, SplitDomainInterfaceEntry,
    SplitDomainLedger,
)
from .split_scientific_context import (
    scientific_context, bind_restart_context, require_restart_context,
)


class ContextBoundSplitDomainReplacement(_reference.SplitDomainReplacement):
    """Native algebra with a v2 scientific-context restart; not physical COM."""

    def _restart_scientific_context(self):
        return scientific_context(self, {
            'native_reference_blob': '4e448557d1f3d6ff535a445c2d892588eb3adf37',
            'electron_volt_J': _reference.electron_volt,
            'lyman_alpha_energy_eV': _reference.LYMAN_ALPHA_ENERGY_EV,
            'H_PLANCK_EV_S': _native.H_PLANCK_EV_S,
            'SOURCE_HPC_EV_CM': _physical.SOURCE_HPC_EV_CM,
            'h_J_s': h,
            'c_m_s': c,
        })

    def restart_record(self):
        return bind_restart_context(super().restart_record(), self._restart_scientific_context())

    def state_from_restart_record(self, record: Mapping[str, object]):
        # This check precedes all old source/history checks and the reference solve.
        require_restart_context(record, self._restart_scientific_context())
        reference_record = dict(record)
        reference_record['schema'] = 'rec-split-domain-restart/v1'
        return super().state_from_restart_record(reference_record)


__all__ = ['ContextBoundSplitDomainReplacement']
