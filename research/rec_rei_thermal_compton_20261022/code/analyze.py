"""Data-only THERM02 physical contrasts; never import or execute a solver.

Read exactly eight completed new-case NPZs and two retained THERM01 baselines.
Signed observables and source owners remain separate. Observed refinement
changes are finite sensitivity comparisons, not physical/global error bounds.
"""
from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CASES = ("t02_split_mao_off", "t02_split_mao_hot", "t02_split_mao_planck",
         "t02_split_derivative_planck", "t02_iso_mao_planck",
         "t02_split_mao_hot_tight34", "t02_split_mao_planck_tight34",
         "t02_split_mao_planck_oracle63")
OFF, HOT, PLANCK, DERIVATIVE, ISO, HOT_TIGHT, PLANCK_TIGHT, ORACLE = CASES
BASELINES = ("thermal_split60", "thermal_iso60")
SIGNED_NAMES = ("shear", "matter", "radiation", "total", "gamma", "nu")
LEDGER_NAMES = ("absorption", "escape", "adiabatic_work", "CMB_or_reference", "UV_Compton")
UNIT_OWNER = "vendor/therm01/vendor/rei_pr220/vendor/rec_hheli/code/atomic_network.py"
PAIRS = (
    ("hot_minus_off", HOT, OFF),
    ("planck_minus_off", PLANCK, OFF),
    ("planck_minus_hot", PLANCK, HOT),
    ("derivative_planck_minus_mao_planck", DERIVATIVE, PLANCK),
    ("iso_planck_minus_split_planck", ISO, PLANCK),
    ("mao_off_minus_old_split_derivative_off", OFF, BASELINES[0]),
    ("iso_planck_minus_old_iso_derivative_off", ISO, BASELINES[1]),
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    os.replace(temporary, path)


def eV_joule(root):
    """Read the numeric unit constant from its retained owner without import."""
    manifest = json.loads((root / "provenance/REUSED_FILES.json").read_text())
    row = next(record for record in manifest["files"] if record["path"] == UNIT_OWNER)
    source = root / UNIT_OWNER
    if sha(source) != row["sha256"]:
        raise ValueError("retained unit owner changed")
    for node in ast.parse(source.read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "EV_J" for target in node.targets):
            value = ast.literal_eval(node.value)
            if not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
                raise ValueError("invalid retained EV_J constant")
            return float(value)
    raise ValueError("retained EV_J constant not found")


def read_history(root, name, baseline=False):
    directory = root / ("baseline" if baseline else "data") / name
    raw_path = directory / "trajectory.npz"
    result_path = directory / "RESULT.json"
    receipt = json.loads(result_path.read_text())
    if receipt.get("status") != "PASS":
        raise ValueError("completed PASS result required:" + name)
    raw_sha = sha(raw_path)
    if receipt.get("raw_sha256") != raw_sha:
        raise ValueError("trajectory SHA-256 differs from result:" + name)
    with np.load(raw_path, allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    required = ("x", "z", "diagnostic_names", "diagnostics", "Y", "q",
                "species_names", "scaled_populations", "signed_observables",
                "ledger_GL16", "ledger_normalized_residual", "ledger_GL_difference")
    if any(key not in arrays for key in required):
        raise ValueError("missing physical analysis arrays:" + name)
    x, z = arrays["x"], arrays["z"]
    if x.shape != (193,) or z.shape != (193,) or not np.all(np.diff(x) > 0):
        raise ValueError("193 strictly ordered saved nodes required:" + name)
    names = [str(key) for key in arrays["diagnostic_names"]]
    if len(set(names)) != len(names) or arrays["diagnostics"].shape != (193, len(names)):
        raise ValueError("diagnostic dimensions/names differ:" + name)
    diagnostics = {key: arrays["diagnostics"][:, i] for i, key in enumerate(names)}
    for key in ("T_K", "tau_T", "ne_m3", "nb_m3", "epsilon_total_J"):
        if key not in diagnostics or not np.isfinite(diagnostics[key]).all():
            raise ValueError("missing/nonfinite " + key + ":" + name)
    if np.any(diagnostics["nb_m3"] <= 0) or np.any(diagnostics["T_K"] <= 0):
        raise ValueError("positive number density and temperature required:" + name)
    if arrays["scaled_populations"].shape != (193, 21) or arrays["signed_observables"].shape != (193, 6):
        raise ValueError("wrong population/stress dimensions:" + name)
    ledger_width = 3 if baseline else 5
    if arrays["ledger_GL16"].shape != (193, ledger_width):
        raise ValueError("wrong ledger width:" + name)
    for key in ("scaled_populations", "signed_observables", "ledger_GL16", "Y"):
        if not np.isfinite(arrays[key]).all():
            raise ValueError("nonfinite " + key + ":" + name)
    return dict(name=name, baseline=baseline, arrays=arrays, D=diagnostics, receipt=receipt,
                paths={str(raw_path.relative_to(root)): dict(bytes=raw_path.stat().st_size, sha256=raw_sha),
                       str(result_path.relative_to(root)): dict(bytes=result_path.stat().st_size, sha256=sha(result_path))})


def extremum(values, x, z, names=None):
    """Retain the sign and coordinate of the largest absolute difference."""
    values = np.asarray(values)
    index = np.unravel_index(int(np.argmax(abs(values))), values.shape)
    result = dict(max_absolute=float(abs(values[index])), signed_value=float(values[index]),
                  sample_index=int(index[0]), x=float(x[index[0]]), z=float(z[index[0]]))
    if len(index) == 2:
        result["component_index"] = int(index[1])
        if names is not None:
            result["component_name"] = str(names[index[1]])
    return result


def exchange_summary(history):
    arrays, D = history["arrays"], history["D"]
    if history["baseline"]:
        return dict(status="NOT_APPLICABLE_PRIOR_COMPTON_OFF", sampled_peaks=None,
                    saved_and_GL_peaks=None, integrals_GL16=None, integrals_GL8=None)
    columns = ("compton_over_HUgamma", "compton_over_HUref")
    out = dict(status="MEASURED", owners={columns[0]: "current actual photon density",
                                         columns[1]: "independent external Planck bath; zero when inactive"},
               sampled_peaks={}, saved_and_GL_peaks={},
               integrals_GL16={}, integrals_GL8={},
               denser_peak_scope="193 saved nodes and persisted GL8/GL16 nodes; accepted solver nodes excluded",
               interpretation="measured exchange scale, not a backreaction error bound")
    for j, name in enumerate(columns):
        out["sampled_peaks"][name] = extremum(D[name], arrays["x"], arrays["z"])
        xx = np.concatenate((arrays["x"], arrays["dense_GL8_x"], arrays["dense_GL16_x"]))
        vv = np.concatenate((D[name], arrays["dense_GL8_exchange_ratios"][:, j], arrays["dense_GL16_exchange_ratios"][:, j]))
        out["saved_and_GL_peaks"][name] = extremum(vv, xx, 21*np.exp(-xx)-1)
        out["integrals_GL16"][name] = float(arrays["exchange_ratio_integrals_GL16"][-1, j])
        out["integrals_GL8"][name] = float(arrays["exchange_ratio_integrals_GL8"][-1, j])
    return out


def case_summary(history, conversion):
    arrays, D, receipt = history["arrays"], history["D"], history["receipt"]
    energy = arrays["ledger_GL16"][-1] / conversion
    ledger = dict(zip(LEDGER_NAMES, energy.tolist()))
    if history["baseline"]:
        ledger.update(CMB_or_reference=0., UV_Compton=0.)
    total = D["epsilon_total_J"]
    predicted = ledger["absorption"]-ledger["escape"]-ledger["adiabatic_work"]+ledger["CMB_or_reference"]+ledger["UV_Compton"]
    residual_peak = extremum(arrays["ledger_normalized_residual"], arrays["x"], arrays["z"])
    temperature = D["T_K"]
    minimum_index, maximum_index = int(np.argmin(temperature)), int(np.argmax(temperature))
    xe = D["ne_m3"] / D["nb_m3"]
    source = receipt["identity"]["config"]
    summary = dict(id=history["name"], cohort="THERM01_RETAINED" if history["baseline"] else "THERM02_NEW",
        rr_closure=source.get("rr_closure", "rate_derivative"), cmb_branch=source.get("cmb_branch", "off"),
        final_T_K=float(temperature[-1]), final_tau=float(D["tau_T"][-1]), final_xe_per_baryon=float(xe[-1]),
        minimum_T_K=float(temperature[minimum_index]), minimum_T_z=float(arrays["z"][minimum_index]),
        maximum_T_K=float(temperature[maximum_index]), maximum_T_z=float(arrays["z"][maximum_index]),
        minimum_sampled_scaled_population=float(arrays["scaled_populations"].min()),
        accepted_BDF_node_count=None if history["baseline"] else int(receipt["accepted_nodes"]),
        saved_node_count=len(arrays["x"]), solver_nfev=receipt.get("nfev"), wall_seconds=receipt.get("wall_seconds"),
        final_signed_observables=dict(zip(SIGNED_NAMES, arrays["signed_observables"][-1].tolist())),
        ledger_GL16_final_eV_per_baryon=ledger,
        gas_energy_change_eV_per_baryon=float((total[-1]-total[0])/conversion),
        ledger_predicted_energy_change_eV_per_baryon=float(predicted),
        endpoint_energy_residual_eV_per_baryon=float((total[-1]-total[0])/conversion-predicted),
        energy_residual_peak=residual_peak,
        energy_residual_gate=3e-6, energy_gate_margin_fraction=float(1-residual_peak["max_absolute"]/3e-6),
        maximum_GL8_GL16_difference=float(arrays["ledger_GL_difference"].max()),
        exchange=exchange_summary(history),
        accepted_node_note="not separately persisted in THERM01 t_eval return" if history["baseline"] else "actual BDF nodes persisted separately from saved193")
    if not history["baseline"]:
        summary["final_absolute_throughput_eV_per_baryon"] = float(arrays["ledger_abs_GL16"][-1].sum()/conversion)
        summary["physical_scope_counts"] = {name: int(row["metrics"]["sample_count"])
                                             for name, row in receipt["physical_scopes"].items()}
    return summary


def pair_arrays(left, right):
    a, b = left["arrays"], right["arrays"]
    if not np.array_equal(a["x"], b["x"]) or not np.array_equal(a["z"], b["z"]):
        raise ValueError("contrasts require identical saved grids")
    if not np.array_equal(a["species_names"], b["species_names"]):
        raise ValueError("species ordering changed across contrast")
    da, db = left["D"], right["D"]
    out = dict(T_K=da["T_K"]-db["T_K"],
               relative_T=(da["T_K"]-db["T_K"])/np.maximum(abs(da["T_K"]), abs(db["T_K"])),
               xe_per_baryon=da["ne_m3"]/da["nb_m3"]-db["ne_m3"]/db["nb_m3"],
               tau_T=da["tau_T"]-db["tau_T"],
               scaled_charge_fraction=a["scaled_populations"]-b["scaled_populations"])
    for j, name in enumerate(SIGNED_NAMES):
        out[name] = a["signed_observables"][:, j]-b["signed_observables"][:, j]
    return out


def pair_summary(left, right):
    differences = pair_arrays(left, right)
    arrays = left["arrays"]
    peaks = {name: extremum(value, arrays["x"], arrays["z"], arrays["species_names"] if name == "scaled_charge_fraction" else None)
             for name, value in differences.items()}
    return dict(left=left["name"], right=right["name"], subtraction="left minus right",
        relative_T_denominator="pointwise max(abs(T_left), abs(T_right))",
        maximum_relative_T=peaks["relative_T"]["max_absolute"],
        maximum_absolute_T_K=peaks["T_K"]["max_absolute"],
        maximum_absolute_T_z=peaks["T_K"]["z"],
        maximum_scaled_charge_fraction_change=peaks["scaled_charge_fraction"],
        delta_final_T_K=float(differences["T_K"][-1]), delta_final_tau=float(differences["tau_T"][-1]),
        delta_final_xe_per_baryon=float(differences["xe_per_baryon"][-1]),
        maximum_absolute_tau=peaks["tau_T"]["max_absolute"],
        maximum_absolute_signed6={name: peaks[name]["max_absolute"] for name in SIGNED_NAMES},
        delta_final_signed6={name: float(differences[name][-1]) for name in SIGNED_NAMES},
        observable_peaks=peaks, evidence_kind="OBSERVED_MODEL_OR_SOURCE_CHANGE",
        physical_accuracy="NOT_INFERRED", global_error_bound="NOT_ESTABLISHED")


def finite_branch_sensitivity(histories):
    """Compare branch differences with both observed nominal/tight changes."""
    pairs = {"branch_difference": pair_arrays(histories[PLANCK], histories[HOT]),
             "hot_refinement": pair_arrays(histories[HOT_TIGHT], histories[HOT]),
             "planck_refinement": pair_arrays(histories[PLANCK_TIGHT], histories[PLANCK])}
    observables = ("T_K", "relative_T", "xe_per_baryon", "tau_T", "scaled_charge_fraction") + SIGNED_NAMES
    out = dict(label="FINITE_OBSERVED_SENSITIVITY_NOT_GLOBAL_ERROR_BOUND",
               branch_comparison="planck_reference minus actual_hot",
               criterion="branch peak exceeds each observed nominal-tight peak separately",
               normalization="absolute physical differences; relative_T additionally uses each pair's symmetric temperature denominator",
               observations={})
    for name in observables:
        branch = float(np.max(abs(pairs["branch_difference"][name])))
        hot = float(np.max(abs(pairs["hot_refinement"][name])))
        planck = float(np.max(abs(pairs["planck_refinement"][name])))
        maximum, total = max(hot, planck), hot+planck
        out["observations"][name] = dict(branch_peak_absolute=branch,
            hot_nominal_tight_peak_absolute=hot, planck_nominal_tight_peak_absolute=planck,
            ratio_to_maximum_observed_refinement=branch/maximum if maximum > 0 else None,
            ratio_to_sum_observed_refinements=branch/total if total > 0 else None,
            exceeds_each_observed_refinement=bool(branch > hot and branch > planck),
            exceeds_sum_observed_refinements=bool(branch > total),
            zero_refinement_denominator=bool(total == 0))
    return out


def write_table(path, summaries):
    base = ("id", "cohort", "rr_closure", "cmb_branch", "final_T_K", "final_tau", "final_xe_per_baryon",
            "minimum_T_K", "minimum_T_z", "maximum_T_K", "maximum_T_z",
            "minimum_sampled_scaled_population", "accepted_BDF_node_count", "saved_node_count",
            "solver_nfev", "wall_seconds", "energy_gate_margin_fraction", "maximum_GL8_GL16_difference",
            "gas_energy_change_eV_per_baryon", "endpoint_energy_residual_eV_per_baryon")
    fields = list(base) + ["final_signed_"+name for name in SIGNED_NAMES] + ["ledger_"+name+"_eV_per_baryon" for name in LEDGER_NAMES]
    fields += ["maximum_normalized_energy_residual", "actual_exchange_peak_saved_GL", "reference_exchange_peak_saved_GL",
               "actual_exchange_integral_GL16", "reference_exchange_integral_GL16"]
    temporary = path.with_name(path.name+".writing")
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for summary in summaries:
            row = {name: summary.get(name) for name in base}
            row.update({"final_signed_"+name: value for name, value in summary["final_signed_observables"].items()})
            row.update({"ledger_"+name+"_eV_per_baryon": value for name, value in summary["ledger_GL16_final_eV_per_baryon"].items()})
            row["maximum_normalized_energy_residual"] = summary["energy_residual_peak"]["max_absolute"]
            exchange = summary["exchange"]
            if exchange["status"] == "MEASURED":
                for name, column in (("actual", "compton_over_HUgamma"), ("reference", "compton_over_HUref")):
                    row[name+"_exchange_peak_saved_GL"] = exchange["saved_and_GL_peaks"][column]["max_absolute"]
                    row[name+"_exchange_integral_GL16"] = exchange["integrals_GL16"][column]
            writer.writerow({key: format(value, ".17g") if isinstance(value, float) else value for key, value in row.items()})
    os.replace(temporary, path)


def write_draft(path, report):
    cases, comparisons = report["cases"], report["contrasts"]
    branches = report["planck_hot_finite_sensitivity"]["observations"]
    rows = ["# THERM02 물리 해석 초안", "", "저장된 완료 자료만으로 계산한 해석 초안이다. 새 ODE와 과거 suite 실행은 0회다.", "",
            "## 주요 측정", "", "| 사례 | 최종 T [K] | 최종 tau_T | 최종 n_e/n_b | CMB/reference 순교환 [eV/baryon] |", "|---|---:|---:|---:|---:|"]
    for name in (OFF, HOT, PLANCK, DERIVATIVE, ISO):
        row = cases[name]
        rows.append(f"| {name} | {row['final_T_K']:.9g} | {row['final_tau']:.9g} | {row['final_xe_per_baryon']:.9g} | {row['ledger_GL16_final_eV_per_baryon']['CMB_or_reference']:.9g} |")
    rows.extend(["", "## 비교의 물리적 의미", "",
        f"Mao hybrid에서 actual_hot을 활성화한 off 대비 최종 온도 변화는 {comparisons['hot_minus_off']['delta_final_T_K']:.9g} K이며, 전체 저장 구간의 최대 상대 온도 변화는 {comparisons['hot_minus_off']['maximum_relative_T']:.9g}이다.",
        f"독립 Planck reference와 actual_hot의 최종 온도 차이는 {comparisons['planck_minus_hot']['delta_final_T_K']:.9g} K이다. 이 차이는 실제 복사장을 Planck 분포로 복원한 오차가 아니라 서로 다른 source owner의 조건부 모델 차이다.",
        f"Planck branch에서 derivative RR moment와 Mao hybrid의 최종 온도 차이는 {comparisons['derivative_planck_minus_mao_planck']['delta_final_T_K']:.9g} K이다. 이는 RR cooling closure 민감도이며 어느 closure의 독립적 물리 정확도도 정하지 않는다.",
        f"동일 Planck branch의 isotropic−split 최종 온도 차이는 {comparisons['iso_planck_minus_split_planck']['delta_final_T_K']:.9g} K이다. 물질과 복사 anisotropic stress는 각각의 signed 관측량으로 보존했다.", "",
        "## 두 branch의 유한 정밀도 비교", "",
        "Planck−hot에만 두 branch의 nominal/tight 결과가 함께 있다. 아래 비교는 관찰된 유한 정밀도 변화이며 전역 오차 한계나 통계적 신뢰도를 뜻하지 않는다.", "",
        "| 관측량 | branch peak | hot refinement peak | Planck refinement peak | 최대 refinement 대비 비 |", "|---|---:|---:|---:|---:|"])
    for name in ("T_K", "xe_per_baryon", "tau_T", "scaled_charge_fraction", "matter", "radiation", "shear"):
        row = branches[name]
        ratio = row["ratio_to_maximum_observed_refinement"]
        rows.append(f"| {name} | {row['branch_peak_absolute']:.8g} | {row['hot_nominal_tight_peak_absolute']:.8g} | {row['planck_nominal_tight_peak_absolute']:.8g} | {ratio:.8g} |" if ratio is not None else f"| {name} | {row['branch_peak_absolute']:.8g} | {row['hot_nominal_tight_peak_absolute']:.8g} | {row['planck_nominal_tight_peak_absolute']:.8g} | 분모 0 |")
    max_energy = max(row["energy_residual_peak"]["max_absolute"] for row in cases.values())
    rows.extend(["", "## 에너지 및 범위", "",
        f"8개 새 사례의 최대 정규화 에너지 잔차는 {max_energy:.12g}; 고정 수용치 3e-6에 대한 여유 비율은 {1-max_energy/3e-6:.9g}이다. GL16 ledger의 absorption/escape/work/CMB/UV를 부호와 owner에 따라 보존했다.",
        "실제 photon density와 외부 reference density로 나눈 교환 척도는 별도로 기록했다. 해당 비율과 그 적분은 생략된 spectral/Einstein backreaction 오차를 제한하지 않는다.",
        "결과는 prescribed UV, 공통 전자온도, 21population 원자망 및 test-fluid 열 모델 아래에서 유효하다. Li 공명 final yield와 전체 spectral 에너지 closure는 열린 의무다.", "",
        "Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.", ""])
    Path(path).write_text("\n".join(rows))


def make_analysis(root=None, draft_path=None):
    root = Path(root) if root is not None else ROOT
    histories = {name: read_history(root, name) for name in CASES}
    histories.update({name: read_history(root, name, baseline=True) for name in BASELINES})
    conversion = eV_joule(root)
    summaries = {name: case_summary(history, conversion) for name, history in histories.items()}
    contrasts = {name: pair_summary(histories[left], histories[right]) for name, left, right in PAIRS}
    contrasts["planck_minus_hot"]["evidence_kind"] = "MODEL_BRANCH_CHANGE_WITH_TWO_FINITE_REFINEMENTS"
    provenance = {}
    for history in histories.values():
        provenance.update(history["paths"])
    for name in ("code/analyze.py", UNIT_OWNER, "FROZEN_CONTRACT.md", "provenance/REUSED_FILES.json"):
        path = root / name
        provenance[name] = dict(bytes=path.stat().st_size, sha256=sha(path))
    report = dict(schema="therm02.data_only_physics_comparisons.v1", status="COMPLETE_DATA_REDUCTION",
        created_UTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        new_cosmological_IVPs=0, old_suite_runs=0, read_new_case_count=8, read_retained_baseline_count=2,
        energy_unit=dict(eV_J=conversion, source=UNIT_OWNER, evaluation="literal constant read via AST; module not imported"),
        cases={name: summaries[name] for name in CASES},
        retained_baselines={name: summaries[name] for name in BASELINES},
        contrasts=contrasts, planck_hot_finite_sensitivity=finite_branch_sensitivity(histories),
        provenance=provenance,
        interpretation_scope=["conditional 21population atomic/thermal test-fluid model",
            "Mao-factor hybrid retains donor number rates", "actual_hot and external Planck reference have different source owners",
            "other closure/seed changes remain observed changes without two-sided refinement resolution claims",
            "no independent physical cooling accuracy, nuclear completion, or global numerical error bound inferred"],
        statuses=dict(Physical="HOLD", REC_U5="HOLD_9_FAIL/HOLD_8_FAIL", closure="CLOSED_HOLD_NOT_RESET",
                      global_convergence="NOT_RUN", production="NOT_APPROVED", REI_activation=False))
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    table = results / "PHYSICS_TABLE.csv"
    write_table(table, [summaries[name] for name in CASES+BASELINES])
    report["table"] = dict(path=str(table.relative_to(root)), bytes=table.stat().st_size, sha256=sha(table),
                           rows=10, baseline_rows_explicitly_labelled=True)
    dump(results / "PHYSICS_COMPARISONS.json", report)
    if draft_path is not None:
        write_draft(draft_path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--draft", type=Path, help="optional external Korean interpretation draft")
    args = parser.parse_args()
    report = make_analysis(args.root, args.draft)
    print("THERM02_DATA_ANALYSIS: COMPLETE; 8 new histories + 2 retained baselines; 0 new IVPs; 0 old suites")
    print("PHYSICS_COMPARISONS.json and PHYSICS_TABLE.csv written with exact input SHA-256 provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
