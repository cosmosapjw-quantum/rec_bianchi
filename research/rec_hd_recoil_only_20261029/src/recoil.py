"""Exact two-body recoil control for source-pinned *public* REC HD line literals.

A restricted rest-frame single-photon kinematic diagnostic, NOT a source
correction, heat term, physical CDMS v2 authentication, or production adapter.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path

H = Fraction(662607015, 10**42)  # 6.62607015e-34 J*s exact SI
C = Fraction(299792458, 1)  # m/s exactly
U = Fraction(166053906660, 10**38)  # 1.66053906660e-27 kg, fixed value (measured, not exact physically)
MIN_MASS = 2 * U
REFERENCE_MASS = 3 * U
ORIGINAL_GATE_HZ = Fraction(35)
PUBLIC_RESULT_BLOB = "5a99c9e31604347cf756abb4ab3ea1a134238e0d"
LAMDA_RAW_SHA_FROM_PREDECESSOR = "0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb"
FROZEN_PAIRS = (
 ("13374930469958794919/5000000", "2674986094000/1", "-41205081/5000000"),
 ("1332890250930289919/250000", "5331561951400/1", "-236919710081/250000"),
 ("19879323162796857291/2500000", "7951728180800/1", "2710796857291/2500000"),
 ("52591535167862954543/5000000", "10518307081200/1", "-238137045457/5000000"),
 ("13015354732561910729/1000000", "13015353487100/1", "1245461910729/1000000"),
 ("38571409466318598107/2500000", "15428565614100/1", "-4568931401893/2500000"),
 ("22182121643381812819/1250000", "17745695903500/1", "1764006812819/1250000"),
 ("49892404686912474057/2500000", "19956961867900/1", "17162474057/2500000"),
)

class SourceIdentityError(ValueError): pass
class DomainError(ValueError): pass


def json_fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frac(value: str | int | Fraction) -> Fraction:
    if isinstance(value, bool): raise DomainError("bool is not a rational number")
    return Fraction(value)


def emission_photon_energy(delta_E: Fraction, M_upper: Fraction) -> Fraction:
    """Exact free emission, upper molecule initially at rest."""
    if delta_E <= 0 or M_upper <= 0 or delta_E >= M_upper*C*C:
        raise DomainError("positive gap and M_u c^2 > gap required")
    return delta_E * (1 - delta_E/(2*M_upper*C*C))


def absorption_photon_energy(delta_E: Fraction, M_lower: Fraction) -> Fraction:
    """Exact free absorption, lower molecule initially at rest."""
    if delta_E <= 0 or M_lower <= 0:
        raise DomainError("positive gap and lower mass required")
    return delta_E * (1 + delta_E/(2*M_lower*C*C))


def recoil_shift_hz(nu_energy: Fraction, rest_mass: Fraction) -> Fraction:
    if nu_energy <= 0 or rest_mass <= 0 or H*nu_energy >= rest_mass*C*C:
        raise DomainError("rest-frame mass gap outside physical two-body branch")
    return H * nu_energy**2 / (2*rest_mass*C*C)


def mass_required_for_shift(nu_energy: Fraction, discrepancy_hz: Fraction) -> Fraction:
    if nu_energy <= 0 or discrepancy_hz == 0: raise DomainError("positive frequency and nonzero discrepancy required")
    return H*nu_energy**2 / (2*C*C*abs(discrepancy_hz))


def decimal_string(x: Fraction, precision: int=45) -> str:
    with localcontext() as ctx:
        ctx.prec=precision
        return format(Decimal(x.numerator)/Decimal(x.denominator), "f")


def load_transcript(raw: bytes) -> dict:
    try: data=json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e: raise SourceIdentityError("invalid public transcript") from e
    if data.get("source_blob_sha")!=PUBLIC_RESULT_BLOB or data.get("LAMDA_original_sha256_from_prior_source")!=LAMDA_RAW_SHA_FROM_PREDECESSOR:
        raise SourceIdentityError("frozen source provenance mismatch")
    rows=data.get("rows")
    if not isinstance(rows,list) or len(rows)!=8: raise SourceIdentityError("expected eight exact source rows")
    for j,row in enumerate(rows,1):
        if row.get("upper")!=j: raise SourceIdentityError("line ID mismatch")
        triple=(row.get("nu_E_Hz"),row.get("nu_P_Hz"),row.get("nu_E_minus_nu_P_Hz"))
        if triple!=FROZEN_PAIRS[j-1]: raise SourceIdentityError(f"public selected-field transcription mismatch J={j}")
        a,b,d=(frac(x) for x in triple)
        if a<=0 or b<=0 or a-b!=d: raise SourceIdentityError("nonpositive or inconsistent line frequencies")
    return data


def compute(raw: bytes, minimum_mass: Fraction=MIN_MASS, reference_mass: Fraction=REFERENCE_MASS) -> dict:
    if minimum_mass<=0 or reference_mass<minimum_mass: raise DomainError("declared mass bounds inconsistent")
    z=load_transcript(raw)
    out=[]
    for j,(nu_txt,p_txt,d_txt) in enumerate(FROZEN_PAIRS,1):
        nu,phot,detuning=(frac(x) for x in (nu_txt,p_txt,d_txt))
        recoil_upper=recoil_shift_hz(nu,minimum_mass)
        recoil_nominal=recoil_shift_hz(nu,reference_mass)
        required=mass_required_for_shift(nu,detuning)
        resid=max(Fraction(0),abs(detuning)-recoil_upper)
        out.append({
            "J_upper":j, "J_lower":j-1,
            "nu_E_Hz":nu_txt,"nu_P_Hz":p_txt,
            "nu_E_minus_nu_P_Hz_exact":str(detuning),
            "nu_E_minus_nu_P_Hz_decimal":decimal_string(detuning),
            "recoil_2u_upper_Hz":decimal_string(recoil_upper),
            "recoil_3u_reference_Hz":decimal_string(recoil_nominal),
            "ratio_abs_defect_to_2u_recoil":decimal_string(abs(detuning)/recoil_upper),
            "min_abs_residual_after_recoil_2u_Hz":decimal_string(resid),
            "implied_mass_u_if_recoil_only":decimal_string(required/U),
            "emission_sign_compatible":detuning>=0,
            "rest_frame_recoil_magnitude_can_cover":abs(detuning)<=recoil_upper,
            "original_35_Hz_pass":abs(detuning)<=ORIGINAL_GATE_HZ,
            "original_35_Hz_repaired":False
        })
    return {
      "schema":"REC_HD_RECOIL_ONLY_COVARIANT_ENERGY_CONTROL_V1",
      "selected_source_blob":PUBLIC_RESULT_BLOB,
      "transcript_sha256":json_fingerprint(raw),
      "source_authenticity":"PUBLIC_GIT_SELECTED_FIELDS_ONLY; NOT original LAMDA/CDMS byte re-acquisition",
      "kinematic_assumptions":"free single photon, initial emitter/absorber at rest, fixed molecule mass >= 2 u; recoil-only, no thermal Doppler/pressure/environment/other reservoir",
      "constants":{"c_m_per_s":str(C),"h_Js":"6.62607015e-34","u_kg_used":"1.66053906660e-27", "minimum_mass_u":"2","reference_mass_u":"3"},
      "proof":"E_gamma,em=DeltaE(1-DeltaE/(2M_u c^2)); E_gamma,abs=DeltaE(1+DeltaE/(2M_l c^2)); |Delta_nu|_recoil <= h nu_E^2/(2 M_min c^2)",
      "rows":out,
      "count_original_35_Hz_fail":sum(not x["original_35_Hz_pass"] for x in out),
      "count_defect_exceeds_2u_recoil":sum(not x["rest_frame_recoil_magnitude_can_cover"] for x in out),
      "count_J2_to_J8_defect_exceeds_2u_recoil":sum(not x["rest_frame_recoil_magnitude_can_cover"] for x in out[1:]),
      "physical_source_choice":"HOLD", "production":"HOLD", "canonical_DAG":"28/88", "REC_physical_DAG":"0/313",
      "interpretation":"recoil-only model discrimination, not universal no-go, measured spectroscopic uncertainty, restored source, or physical heating"
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--transcript",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    data=compute(args.transcript.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as out:
        json.dump(data,out,indent=2,ensure_ascii=False)
        out.write("\n")
    print(f"recoil-only: {data['count_J2_to_J8_defect_exceeds_2u_recoil']}/7 high-J magnitude excluded; 35Hz gate fails {data['count_original_35_Hz_fail']}/8; production HOLD")
    return 0

if __name__=="__main__": raise SystemExit(main())
