"""Independent original-HyRec h/4 primordial start, bounded to 1--8 FULL steps.

The h/2 module supplies only clock-free scalar formulas and its cosmology
parameters. Its globals, functions, defaults and histories are never modified.
HeIII/HeII histories, the photon prefix and both predictor memories are evolved
on this module's own h/4 grid. No reference trajectory or checkpoint is input.

Public temperatures: K; H: s^-1; nH: m^-3; abundances: per H nucleus;
RHS: d/d ln(a); photon distortions: dimensionless occupation numbers.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory import primordial_2012_refined_start as _h2
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, complete_original_full_atomic,
    populate_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K

DLNA = 8.49e-5 / 4
SOURCE_DLNA = DLNA
SOURCE_INDEX_START = 72892
MAX_ACCEPTED = 8
PINNED_ZIP_SHA256 = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
HISTORY_SCHEMA = "rec.r3o.h4-independent-start.v1"

# These formulas have no time-step globals and retain the reviewed source order.
saha_heii_iii = _h2.saha_heii_iii
saha_heii = _h2.saha_heii
saha_xH1s = _h2.saha_xH1s
helium_rhs = _h2.helium_rhs
tm_steady_K = _h2.tm_steady_K


class QuarterStartCosmology(_h2.HyRec2012Cosmology):
    """Original frozen cosmology, with only the independent quarter-step clock."""

    def __post_init__(self):
        super().__post_init__()
        original = _h2.HyRec2012Cosmology()
        if any(getattr(self, k) != getattr(original, k)
               for k in self.__dataclass_fields__):
            raise ValueError("h4 start requires the frozen original cosmology")

    @property
    def izH0(self) -> int:
        return math.floor(1.0 + math.log(
            (_h2.KB_EV_K * self.T0_K / self.fsR**2 / self.meR)
            * 8001.0 / _h2.TR_MAX_EV) / DLNA)

    def redshift(self, iz: int) -> float:
        if not isinstance(iz, (int, np.integer)) or isinstance(iz, (bool, np.bool_)) or iz < 0:
            raise ValueError("nonnegative integer source index required")
        return 8001.0 * math.exp(-DLNA * int(iz)) - 1.0


@dataclass(frozen=True)
class QuarterHeliumHistory(_h2.HeliumStageHistory):
    """Independent h4 source history, including every primordial row."""

    dlna: float = DLNA
    source_zip_sha256: str = PINNED_ZIP_SHA256

    def __post_init__(self):
        super().__post_init__()
        if (self.dlna != DLNA or self.source_zip_sha256 != PINNED_ZIP_SHA256
                or self.source_sha256 != _h2.SOURCE_HELIUM_SHA256
                or self.iz != tuple(range(SOURCE_INDEX_START + 1))):
            raise ValueError("independent h4 helium grid/source identity mismatch")
        c = QuarterStartCosmology()
        if self.z[0] != 8000.0 or self.z[-1] != c.redshift(SOURCE_INDEX_START):
            raise ValueError("h4 helium source clock endpoints mismatch")


def integrate_helium_stages(
    c: QuarterStartCosmology | None = None, *, check_budget: Callable | None = None,
) -> QuarterHeliumHistory:
    """Original history.c HeIII Saha and HeII post-Saha/predictor stages.

    Source row i stores the derivative evaluated at i-1. The endpoint used
    inside post-Saha is (1+z_in)*exp(-h4)-1, followed by the source's absolute
    grid expression for the accepted output. Neither clock is substituted.
    """
    c = QuarterStartCosmology() if c is None else c
    if type(c) is not QuarterStartCosmology or c.izH0 != SOURCE_INDEX_START:
        raise ValueError("independent h4 cosmology required")
    zs = []; xeout = []; tms = []; xhe = []; rhsout = []
    stages = []; methods = []; psflags = []
    iz = 0; delta = c.fHe
    while iz < c.izH0 and delta > 1.e-8:
        if check_budget is not None and iz % 512 == 0:
            check_budget()
        z = c.redshift(iz)
        xe, delta = saha_heii_iii(c, z)
        zs.append(z); xeout.append(xe); tms.append(c.T0_K * (1 + z))
        rhsout.append(0.0); xhe.append(math.nan)
        stages.append("HeIII_SAHA"); methods.append("SAHA_ALGEBRAIC")
        psflags.append(False); iz += 1
    if iz < 4 or delta > 1.e-8:
        raise ArithmeticError("HeIII stage did not leave valid independent derivative seeds")
    # Literal history.c source finite-difference order.
    dprev2 = (xeout[iz-2] - xeout[iz-4]) / 2. / DLNA
    dprev = (xeout[iz-1] - xeout[iz-3]) / 2. / DLNA
    xh = saha_heii(c, c.redshift(iz-1)); post = True
    while iz <= c.izH0:
        if check_budget is not None and iz % 512 == 0:
            check_budget()
        zin = c.redshift(iz-1)
        H = c.hubble_s(zin)
        rhs = helium_rhs(c, saha_xH1s(c, xh, zin), xh, H, zin)
        method = "POST_SAHA" if post else "SOURCE_PREDICTOR"
        if post:
            zout = (1.0 + zin) * math.exp(-DLNA) - 1.0
            Hout = c.hubble_s(zout)
            saha = saha_heii(c, zout)
            dsaha = (1 + zout) * (saha_heii(c, zout-0.5) - saha_heii(c, zout+0.5))
            dxe = 0.01 * (c.fHe - saha)
            if not (dxe > 0 and saha-dxe >= 0 and saha+dxe <= c.fHe):
                raise ArithmeticError("invalid original He post-Saha perturbation")
            hp = saha_xH1s(c, saha+dxe, zout)
            hm = saha_xH1s(c, saha-dxe, zout)
            jac = (helium_rhs(c, hp, saha+dxe, Hout, zout)
                   - helium_rhs(c, hm, saha-dxe, Hout, zout)) / (2*dxe)
            if jac == 0 or not math.isfinite(jac):
                raise ArithmeticError("singular original He post-Saha Jacobian")
            xh = saha + dsaha / jac
            if abs(xh-saha) > _h2.DXHEII_MAX:
                post = False
        else:
            xh += DLNA * (1.25*rhs - 0.25*dprev2)
        dprev2, dprev = dprev, rhs
        z = c.redshift(iz)
        xhii = 1 - saha_xH1s(c, xh, z)
        xe = xhii + xh
        tm = tm_steady_K(c, xe, z, c.hubble_s(z))
        if not (all(math.isfinite(q) for q in (xh, xhii, xe, tm, rhs))
                and 0 <= xh <= c.fHe and 0 <= xhii <= 1 and tm > 0):
            raise ArithmeticError(f"invalid original h4 helium state at {iz}")
        zs.append(z); xeout.append(xe); tms.append(tm); xhe.append(xh)
        rhsout.append(rhs); stages.append("HeII_RECOMBINATION")
        methods.append(method); psflags.append(post); iz += 1
    xhei = []; xheii = []; xheiii = []; xhii = []
    for i, stage in enumerate(stages):
        if stage == "HeIII_SAHA":
            q = xeout[i] - (1 + c.fHe)
            xheiii.append(q); xheii.append(c.fHe-q)
            xhei.append(0.0); xhii.append(1.0)
        else:
            xheiii.append(0.0); xheii.append(xhe[i])
            xhei.append(c.fHe-xhe[i]); xhii.append(xeout[i]-xhe[i])
    return QuarterHeliumHistory(
        tuple(range(len(zs))), tuple(zs), tuple(xeout), tuple(xhii),
        tuple(xhei), tuple(xheii), tuple(xheiii), tuple(tms), tuple(rhsout),
        tuple(stages), tuple(methods), tuple(psflags),
    )


def source_native_derivative_seeds(helium: QuarterHeliumHistory) -> np.ndarray:
    """Rows [He,H], columns [prev2,prev], consumed at izH0.

    The two columns own input indices izH0-2 and izH0-1, respectively;
    helium output row i stores f_He(i-1). Hydrogen uses original central
    differences of the independently produced h4 electron abundance.
    """
    if type(helium) is not QuarterHeliumHistory or helium.dlna != DLNA:
        raise ValueError("independent h4 helium history required; no h2 checkpoint")
    i = SOURCE_INDEX_START
    he2 = float(helium.helium_rhs_dln_a[i-1])
    he = float(helium.helium_rhs_dln_a[i])
    h2 = (float(helium.xe[i-1]) - float(helium.xe[i-3])) / 2. / DLNA - he2
    h = (float(helium.xe[i]) - float(helium.xe[i-2])) / 2. / DLNA - he
    result = np.array([[he2, he], [h2, h]], dtype=float)
    if not np.all(np.isfinite(result)):
        raise ValueError("nonfinite h4 source-native predictor seeds")
    return result


@dataclass(frozen=True)
class QuarterFullStartHistory:
    iz: np.ndarray
    z: np.ndarray
    xH1s: np.ndarray
    xHII: np.ndarray
    xHeII: np.ndarray
    xe: np.ndarray
    Tm_K: np.ndarray
    helium_rhs_dln_a: np.ndarray
    hydrogen_rhs_dln_a: np.ndarray
    post_saha: np.ndarray
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    matrix_residual: np.ndarray
    initial_predictor: np.ndarray
    final_predictor: np.ndarray
    full_evaluations: int
    dlna: float = DLNA
    source_mode: str = "INDEPENDENT_PYTHON_HYREC2012_H4_BOUNDED_FULL_HHE_START"

    def __post_init__(self):
        n = len(self.iz)-1
        if not 1 <= n <= MAX_ACCEPTED or self.dlna != DLNA:
            raise ValueError("h4 FULL start is bounded to 1..8 accepted steps")
        for name, shape in (
            *((k, (n+1,)) for k in ("iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "post_saha")),
            *((k, (n,)) for k in ("helium_rhs_dln_a", "hydrogen_rhs_dln_a", "matrix_residual")),
            ("virtual_out", (NVIRT, n)), ("average_virtual", (NVIRT, n)),
            ("lyman_out", (3, n)), ("initial_predictor", (2, 2)),
            ("final_predictor", (2, 2)),
        ):
            a = np.asarray(getattr(self, name))
            if a.shape != shape or not np.all(np.isfinite(a)):
                raise ValueError(f"invalid h4 {name}")
            a = np.array(a, copy=True); a.setflags(write=False)
            object.__setattr__(self, name, a)
        if not np.array_equal(self.iz, np.arange(SOURCE_INDEX_START, SOURCE_INDEX_START+n+1)):
            raise ValueError("h4 FULL state ownership indices mismatch")
        if not n <= self.full_evaluations <= 4*n:
            raise ValueError("h4 FULL evaluation count outside source bound")


def make_hmla_source(c, rate_table):
    """Reuse unchanged, clock-free original atomic/thermal source adapter."""
    if type(c) is not QuarterStartCosmology:
        raise ValueError("independent h4 cosmology required")
    return _h2.make_hmla_source(c, rate_table)


def integrate_full_start(
    helium: QuarterHeliumHistory, c: QuarterStartCosmology, source,
    *, accepted_steps: int = 8, common_input_oracle: Callable | None = None,
    check_budget: Callable | None = None,
) -> QuarterFullStartHistory:
    """Build an independent photon prefix and predictor memories from h4 He.

    The original C post-Saha endpoint uses the multiplicative input clock;
    the stored accepted node uses the absolute grid clock. All trial outgoing
    spectra are discarded. C outputs may be compared by a callback, but none
    is used to advance a Python state, derivative memory or photon column.
    """
    if (type(accepted_steps) is not int or not 1 <= accepted_steps <= MAX_ACCEPTED):
        raise ValueError("accepted_steps must be an integer in [1,8]")
    if type(c) is not QuarterStartCosmology or c.izH0 != SOURCE_INDEX_START:
        raise ValueError("independent h4 cosmology required")
    seed = source_native_derivative_seeds(helium)
    i = SOURCE_INDEX_START
    if helium.stage[i] != "HeII_RECOMBINATION" or helium.xHeII[i] <= _h2.XHEII_MIN:
        raise ValueError("h4 source requires joint H+He at the FULL boundary")
    expected_source = make_hmla_source(c, source.table)
    if any(getattr(source, k) != getattr(expected_source, k) for k in (
            "h", "omega_cb", "omega_r_h2", "omega_de_h2", "omega_b_h2",
            "y_he_mass", "tcmb0_K")):
        raise ValueError("h4 atomic source cosmology does not match the original start")
    table = _canonical_twophoton_table(source.table.archive_path)
    n = accepted_steps
    iz = np.arange(i, i+n+1, dtype=np.int64)
    z = np.array([c.redshift(int(k)) for k in iz])
    x1 = np.empty(n+1); xh = np.empty(n+1); xhe = np.empty(n+1)
    xe = np.empty(n+1); tm = np.empty(n+1); post = np.empty(n+1, dtype=bool)
    fhe = np.empty(n); fh = np.empty(n); residual = np.empty(n)
    vout = np.full((NVIRT, n), np.nan); avg = np.full((NVIRT, n), np.nan)
    lyout = np.full((3, n), np.nan)
    xhe[0] = helium.xHeII[i]; x1[0] = saha_xH1s(c, float(xhe[0]), float(z[0]))
    xh[0] = 1.-x1[0]; xe[0] = xh[0]+xhe[0]; tm[0] = helium.Tm_K[i]
    post[0] = True
    dHe2, dHe = map(float, seed[0]); dH2, dH = map(float, seed[1])
    evaluations = 0

    def full_rhs(j, zeval, hion, heion, matter):
        nonlocal evaluations
        if check_budget is not None:
            check_budget()
        if evaluations >= 4*n or not 0 <= j <= n:
            raise RuntimeError("H4_BOUNDED_FULL_EVALUATION_CAP")
        if j < 2:
            fv, fl = np.zeros(NVIRT), np.zeros(2)
        else:
            incoming = causal_incoming_from_accepted_histories(
                energies_eV=table.energy_eV, virtual_history=vout[:, :j],
                lyman_history=lyout[:, :j], z_start=float(z[0]), iz=j,
                z_face=float(zeval), dlna=DLNA, shear_q=0.,
            )
            fv, fl = incoming.virtual_distortion[0], incoming.lya_lyb_incoming_distortion[0]
        # Same inclusive binary64 Tm=Tr boundary treatment as reviewed h2.
        # Original physical post-Saha closure remains Tm=Tr; no fitted rate.
        if matter == c.T0_K*(1.+zeval):
            matter = math.nextafter(float(matter), 0.)
        snapshot = populate_original_full_atomic(
            source, z=float(zeval), xHII=float(hion), xe=float(hion+heion),
            Tm_K=float(matter), incoming_virtual=fv, incoming_lyman=fl,
        )
        out = complete_original_full_atomic(snapshot); evaluations += 1
        if common_input_oracle is not None:
            # A diagnostic callback receives detached, read-only past columns.
            # It has no write path into the evolving Python history.
            vpast = np.array(vout[:, :j], copy=True); vpast.setflags(write=False)
            lpast = np.array(lyout[:, :j], copy=True); lpast.setflags(write=False)
            expected = common_input_oracle(
                j, float(zeval), float(hion), float(heion), float(matter),
                vpast, lpast,
            )
            ratio = _h2.checked_common_input_rhs_ratio(out.dxHII_dln_a, float(expected["rhs"]), j)
            if ratio > 2.e-10:
                raise ArithmeticError(f"H4_COMMON_INPUT_RHS:{j}:{ratio:.17g}")
            tr = KB_NATIVE_EV_K*c.T0_K*(1.+zeval)
            fbbv = 1./np.expm1(table.energy_eV/tr)
            fbbl = 1./np.expm1(np.array((10.198714553953742, 12.087365397278509, 12.748393192442178))/tr)
            metrics = expected.get("metrics")
            if metrics is not None:
                metrics["evaluations"] += 1
                metrics["max_rhs_scaled"] = max(metrics["max_rhs_scaled"], ratio)
            for name, values, background in (
                ("virtual", out.outgoing_virtual, fbbv),
                ("average", out.average_virtual, fbbv),
                ("lyman", out.outgoing_lyman, fbbl),
            ):
                other = np.asarray(expected[name], dtype=float)
                if other.shape != values.shape:
                    raise ValueError(f"H4_COMMON_INPUT_SPECTRUM_SHAPE:{name}")
                ratios = _h2.checked_common_input_spectrum_ratio(values, other, background, j)
                if np.any(ratios > 1.):
                    raise ArithmeticError(f"H4_COMMON_INPUT_PHOTON:{j}:{name}:{np.max(ratios):.17g}")
                if metrics is not None:
                    key = f"max_{name}_tolerance_ratio"
                    metrics[key] = max(metrics[key], float(np.max(ratios)))
        return out

    for j in range(n):
        zin = float(z[j])
        if xhe[j] <= _h2.XHEII_MIN:
            raise RuntimeError("h4 bounded start left original joint H+He stage")
        fhe[j] = helium_rhs(c, float(x1[j]), float(xhe[j]), c.hubble_s(zin), zin)
        xhe[j+1] = xhe[j] + DLNA*(1.25*fhe[j] - .25*dHe2)
        current = full_rhs(j, zin, float(xh[j]), float(xhe[j]), float(tm[j]))
        # Sole commit path: one photon column from the current accepted state.
        vout[:, j] = current.outgoing_virtual; avg[:, j] = current.average_virtual
        lyout[:, j] = current.outgoing_lyman; fh[j] = current.dxHII_dln_a
        residual[j] = current.normalized_matrix_residual
        if not math.isfinite(residual[j]) or residual[j] > 2.e-10:
            raise ArithmeticError(f"h4 matrix residual at column {j}")
        if post[j]:
            zp = (1.+zin)*math.exp(-DLNA)-1.
            heout = float(xhe[j+1])
            q = saha_xH1s(c, heout, zp)
            qp = (1.+zp)*(saha_xH1s(c, heout, zp-.5) - saha_xH1s(c, heout, zp+.5))
            delta_he = .01*(c.fHe-heout)
            if not math.isfinite(delta_he) or delta_he <= 0:
                raise ArithmeticError("invalid original h4 He post-Saha probe")
            qp += ((saha_xH1s(c, heout+delta_he, zp) - saha_xH1s(c, heout-delta_he, zp))
                   / 2. / delta_he * helium_rhs(c, q, heout, c.hubble_s(zp), zp))
            X = 1.-q; Tr = c.T0_K*(1.+zp); delta = .01*q
            if not (delta > 0 and delta < X and X+delta < 1):
                raise ArithmeticError("invalid original h4 hydrogen post-Saha probe")
            f0 = full_rhs(j+1, zp, X, heout, Tr).dxHII_dln_a
            fp = full_rhs(j+1, zp, X+delta, heout, Tr).dxHII_dln_a
            fm = full_rhs(j+1, zp, X-delta, heout, Tr).dxHII_dln_a
            jac = (fp-fm) / 2. / delta
            if jac == 0 or not math.isfinite(jac):
                raise ArithmeticError("singular original h4 H post-Saha Jacobian")
            x1[j+1] = q+(qp+f0)/jac
            xh[j+1] = 1.-x1[j+1]
            post[j+1] = abs(x1[j+1]-q) <= _h2.DXHII_MAX
        else:
            # history.c evolves neutral H by -= h*(1.25 fH-.25 prev2).
            x1[j+1] = x1[j]-DLNA*(1.25*fh[j]-.25*dH2)
            xh[j+1] = 1.-x1[j+1]; post[j+1] = False
        xe[j+1] = xh[j+1]+xhe[j+1]
        tm[j+1] = tm_steady_K(c, float(xe[j+1]), float(z[j+1]), c.hubble_s(float(z[j+1])))
        if not (0 <= xhe[j+1] <= c.fHe and 0 <= xh[j+1] <= 1 and tm[j+1] > 0
                and math.isfinite(xe[j+1]) and math.isfinite(tm[j+1])):
            raise ArithmeticError(f"nonphysical h4 accepted FULL state {j+1}")
        dHe2, dHe = dHe, float(fhe[j]); dH2, dH = dH, float(fh[j])
    return QuarterFullStartHistory(
        iz, z, x1, xh, xhe, xe, tm, fhe, fh, post, vout, avg, lyout,
        residual, seed, np.array([[dHe2, dHe], [dH2, dH]]), evaluations,
    )
