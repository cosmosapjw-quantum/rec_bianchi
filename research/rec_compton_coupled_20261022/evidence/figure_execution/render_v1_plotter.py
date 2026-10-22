"""Create-only scientific figures from the completed Compton saved arrays.

No runtime model, driver, solver or source evaluator is imported. New modeled
transfers are distinguished from omitted CI/CE diagnostics on those new paths.
The arrays behind every curve/bar/marker are retained in NPZ and CSV files.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
from scipy.integrate import simpson
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

UNIT = Path(__file__).resolve().parents[1]
SEEDS = ("s03_m03_r03", "s04_m04_r04")
BRANCHES = ("actual_hot", "planck_reference")
EV_J = 1.602176634e-19  # exact SI electronvolt, same value as the source owner
HOT, PLANCK, BASE = "#D55E00", "#0072B2", "#333333"
GAIN, LOSS, PURPLE, GREEN = "#B66A00", "#0072B2", "#882255", "#228833"
METRICS = ("lnT", "conditional_fraction", "tau", "signed_stress_only")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_bytes(path, payload):
    with Path(path).open("xb") as stream:
        stream.write(payload)
    if Path(path).read_bytes() != payload:
        raise IOError("OUTPUT_READBACK_MISMATCH:" + str(path))


def save_json(path, value):
    save_bytes(path, (json.dumps(value, indent=2, allow_nan=False)+"\n").encode())


def save_csv(path, rows):
    if not rows:
        raise ValueError("EMPTY_FIGURE_TABLE")
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
    save_bytes(path, stream.getvalue().encode())


def read_npz(path):
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key].copy() for key in data.files}


def diagnostics(arrays):
    names=arrays["diagnostic_names"].tolist()
    if len(names) != len(set(names)):
        raise ValueError("DUPLICATE_DIAGNOSTIC_NAME")
    return {name: arrays["diagnostics"][:, j] for j,name in enumerate(names)}


def label(seed, branch, refined=True):
    return seed+"_"+branch+("_refined" if refined else "_nominal")


def verified_receipt(folder, expected_runtime=None):
    receipt=json.loads((folder/"RESULT.json").read_text())
    if receipt.get("status") != "COMPLETE":
        raise ValueError("INPUT_NOT_COMPLETE:"+str(folder))
    if expected_runtime is not None and receipt.get("source_identity") != expected_runtime:
        raise ValueError("RUNTIME_IDENTITY_MISMATCH:"+str(folder))
    if not receipt.get("outputs"):
        raise ValueError("EMPTY_OUTPUT_BINDINGS:"+str(folder))
    for relative, record in receipt["outputs"].items():
        path=folder/relative
        if path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
            raise ValueError("INPUT_HASH_MISMATCH:"+str(path))
    return receipt


def load_inputs(analysis, campaign):
    receipt=verified_receipt(analysis)
    summary=json.loads((analysis/"SUMMARY.json").read_text())
    runtime=receipt["runtime_identity"]
    if summary["runtime_identity"] != runtime or summary["refinement"]["status"] != "PASS":
        raise ValueError("ANALYSIS_IDENTITY_OR_REFINEMENT_NOT_ADMITTED")
    data, inputs={}, {}
    for seed in SEEDS:
        for branch in BRANCHES:
            for refined in (False, True):
                key=label(seed,branch,refined)
                case=campaign/key
                rec=verified_receipt(case,runtime)
                a=read_npz(analysis/key/"comparison_and_source_data.npz")
                raw=read_npz(case/"trajectory.npz")
                if not np.array_equal(a["x"],raw["x"]) or not np.array_equal(a["T_K"],raw["T_K"]):
                    raise ValueError("ANALYZED_PATH_MISMATCH:"+key)
                data[key]=dict(analysis=a,raw=raw,receipt=rec,summary=summary["cases"][key])
                used=[analysis/key/"comparison_and_source_data.npz",case/"RESULT.json",case/"trajectory.npz"]
                if branch=="actual_hot" and refined:
                    data[key]["dense"]={n:read_npz(case/f"dense_{n}.npz") for n in (513,1025)}
                    data[key]["collisions"]=read_npz(analysis/key/"collisions/collisions_dense_1025.npz")
                    used += [case/"dense_513.npz",case/"dense_1025.npz",
                             analysis/key/"collisions/collisions_dense_1025.npz"]
                for path in used:
                    inputs[str(path)]=dict(bytes=path.stat().st_size,sha256=sha(path))
    for name in ("RESULT.json","SUMMARY.json","INPUTS.json","BRANCH_COMPARISONS.json"):
        path=analysis/name; inputs[str(path)]=dict(bytes=path.stat().st_size,sha256=sha(path))
    return data,summary,receipt,inputs


def style():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
        "axes.titlesize":12,"axes.labelsize":10.5,"legend.fontsize":9,
        "legend.frameon":False,"axes.spines.top":False,"axes.spines.right":False,
        "axes.axisbelow":True,"axes.linewidth":.8,"xtick.direction":"out",
        "ytick.direction":"out","figure.dpi":140,"savefig.dpi":190,
        "pdf.fonttype":42,"ps.fonttype":42,"lines.linewidth":1.8})


def redshift_axis(ax,z):
    ax.set_xlim(float(z[0]),float(z[-1]))
    ax.set_xticks([v for v in (8,7,6,5,4,3,2) if z[-1]-1e-9<=v<=z[0]+1e-9])
    ax.set_xlabel("Redshift z  (time increases to the right)")
    ax.grid(alpha=.18)


def save_figure(fig,output,name):
    records={}
    for ext in ("png","pdf"):
        buffer=io.BytesIO()
        metadata={"Title":name,"Creator":"rec_bianchi plot_compton.py"} if ext=="pdf" else None
        fig.savefig(buffer,format=ext,bbox_inches="tight",facecolor="white",metadata=metadata)
        payload=buffer.getvalue()
        if ext=="png":
            with Image.open(io.BytesIO(payload)) as check:
                check.verify()
            with Image.open(io.BytesIO(payload)) as check:
                check.load(); dimensions=list(check.size)
        else:
            if len(payload)<1000 or not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-1024:]:
                raise ValueError("INVALID_PDF_BUFFER:"+name)
            dimensions=None
        path=output/(name+"."+ext)
        save_bytes(path,payload)
        records[path.name]=dict(bytes=len(payload),sha256=sha(path),pixel_size=dimensions)
    plt.close(fig)
    return records


def temperature_figure(data,output,arrays):
    fig,axes=plt.subplots(2,2,figsize=(13.6,8.4),sharex="col",sharey="row",
                          gridspec_kw={"height_ratios":[1.45,1]})
    rows=[]
    for col,seed in enumerate(SEEDS):
        hot=data[label(seed,"actual_hot")]["analysis"]
        ref=data[label(seed,"planck_reference")]["analysis"]
        if not np.array_equal(hot["x"],ref["x"]) or not np.array_equal(hot["baseline_T_K"],ref["baseline_T_K"]):
            raise ValueError("TEMPERATURE_COMPARISON_GRID_CHANGED:"+seed)
        z,x=hot["z"],hot["x"]
        old,T_hot,T_ref=hot["baseline_T_K"],hot["T_K"],ref["T_K"]
        frac_hot,frac_ref=100*(T_hot/old-1),100*(T_ref/old-1)
        for values,color,ls,name in ((old,BASE,"-","Existing no-Compton"),
                                    (T_hot,HOT,"-","Actual hot-electron term"),
                                    (T_ref,PLANCK,"--","Separate Planck reference")):
            axes[0,col].plot(z,values/1000,color=color,ls=ls,label=name)
        axes[1,col].plot(z,frac_hot,color=HOT)
        axes[1,col].plot(z,frac_ref,color=PLANCK,ls="--")
        axes[1,col].axhline(0,color=".5",lw=.8)
        axes[0,col].set_title(f"({'ab'[col]}) {seed}",loc="left")
        axes[1,col].set_title(f"({'cd'[col]}) Relative to its existing baseline",loc="left",fontsize=11)
        for ax in axes[:,col]: redshift_axis(ax,z)
        axes[0,col].set_xlabel("")
        for name,values in (("x",x),("z",z),("baseline_T_K",old),("actual_hot_T_K",T_hot),
                            ("planck_reference_T_K",T_ref),("actual_hot_delta_percent",frac_hot),
                            ("planck_reference_delta_percent",frac_ref)):
            arrays["temperature_"+seed+"_"+name]=values
        rows += [dict(seed=seed,x=float(x[j]),z=float(z[j]),baseline_T_K=float(old[j]),
                      actual_hot_T_K=float(T_hot[j]),planck_reference_T_K=float(T_ref[j]),
                      actual_hot_delta_percent=float(frac_hot[j]),planck_reference_delta_percent=float(frac_ref[j]))
                 for j in range(len(x))]
    axes[0,0].set_ylabel("Gas temperature [kK]")
    axes[1,0].set_ylabel("100 (T / T₀ − 1) [%]")
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=3,loc="upper center",bbox_to_anchor=(.5,.945),fontsize=10)
    fig.suptitle("Compton coupling changes the evolved gas temperature",fontsize=16,y=.995)
    fig.subplots_adjust(left=.085,right=.975,top=.84,bottom=.115,wspace=.17,hspace=.25)
    fig.text(.5,.025,"Refined solutions on the same 109 saved comparison points. Both Compton branches include the same UV term.\n"
             "T₀ is the matching existing Mao no-Compton trajectory; the Planck bath is an independent reference, not a reconstructed spectrum.",
             ha="center",va="bottom",fontsize=9)
    save_csv(output/"01_temperature_curves.csv",rows)
    return save_figure(fig,output,"01_temperature_response")


def signed_bars(ax,values,names,title,linthresh=1e-6):
    yy=np.arange(len(values))
    ax.barh(yy,values,color=[GAIN if v>=0 else LOSS for v in values],height=.65)
    ax.set_yticks(yy,names); ax.invert_yaxis()
    ax.set_xscale("symlog",linthresh=linthresh,linscale=.7)
    extent=max(float(np.max(abs(values)))*2,linthresh*10)
    ax.set_xlim(-extent,extent); ax.axvline(0,color=".45",lw=.75)
    ax.grid(axis="x",alpha=.18); ax.set_title(title,loc="left")
    ax.set_xlabel("Signed energy input [eV / baryon]; symlog")
    for j,value in enumerate(values):
        ax.text(1.015,j,f"{value:+.4g}",transform=ax.get_yaxis_transform(),
                ha="left",va="center",fontsize=9)


def energy_figure(data,output,arrays):
    fig,axes=plt.subplots(3,2,figsize=(15.2,13.0),gridspec_kw={"height_ratios":[1.12,.95,1]})
    budget_rows,balance_rows,endpoint_rows=[],[],[]
    modeled=("photo_primary","rr_kinetic","dr_kinetic","compton_selected","compton_uv","expansion_work")
    modeled_names=("Photoelectron heat","RR kinetic loss","DR kinetic loss","Compton: actual hot","UV Compton","Expansion work")
    omitted=("ci_kinetic","ci_binding","ce_HI","ce_HeII")
    omitted_names=("CI: kinetic transfer","CI: binding transfer","H I excitation","He II excitation")
    for col,seed in enumerate(SEEDS):
        case=data[label(seed,"actual_hot")]
        summary=case["summary"]; c=case["collisions"]
        values=np.array([summary["energy_eV_per_baryon"][name] for name in modeled])
        signed_bars(axes[0,col],values,modeled_names,f"({'ab'[col]}) {seed}: modeled terms")
        arrays["energy_"+seed+"_modeled_names"]=np.array(modeled)
        arrays["energy_"+seed+"_modeled_Simpson1025_eV_baryon"]=values
        for name,value in zip(modeled,values):
            budget_rows.append(dict(seed=seed,owner="included in actual_hot RHS",process=name,
                                    component="total",rule="Simpson1025",energy_eV_baryon=float(value)))
        support=np.array([summary["collisions"]["energy_eV_per_baryon"][n]["supported_interval_contribution"] for n in omitted])
        continuation=np.array([summary["collisions"]["energy_eV_per_baryon"][n]["continuation_or_boundary_contribution"] for n in omitted])
        total=support+continuation
        # These processes each have a definite sign, so interval partitions
        # stack without cancelling supported and unsupported contributions.
        if np.any(support*continuation < 0):
            raise ValueError("OPPOSING_SUPPORT_PARTITION_SIGNS:"+seed)
        ax=axes[1,col]; yy=np.arange(len(omitted));colors=[PURPLE,PURPLE,GREEN,GREEN]
        ax.barh(yy,support,color=colors,height=.65)
        ax.barh(yy,continuation,left=support,color="white",edgecolor=colors,hatch="////",height=.65)
        ax.set_yticks(yy,omitted_names); ax.invert_yaxis()
        ax.set_xscale("symlog",linthresh=1e-7,linscale=.7)
        extent=max(float(np.max(abs(total)))*2,1e-6)
        ax.set_xlim(-extent,extent);ax.axvline(0,color=".45",lw=.75);ax.grid(axis="x",alpha=.18)
        ax.set_title(f"({'cd'[col]}) Omitted CI/CE: new-path diagnostics",loc="left")
        ax.set_xlabel("Signed transfer [eV / baryon]; symlog")
        for j,value in enumerate(total):
            ax.text(1.015,j,f"{value:+.4g}",transform=ax.get_yaxis_transform(),ha="left",va="center",fontsize=9)
        for name,values2 in (("names",np.array(omitted)),("supported",support),("continuation",continuation),("total",total)):
            arrays["collision_"+seed+"_"+name]=values2
        arrays["collision_"+seed+"_support_mask"]=c["in_published_accuracy_domain"]
        arrays["collision_"+seed+"_coefficient_names"]=c["coefficient_names"]
        for j,name in enumerate(omitted):
            for component,values2 in (("supported_intervals",support),("continuation_or_boundary",continuation)):
                budget_rows.append(dict(seed=seed,owner="omitted diagnostic; not actual CI/CE exchange",process=name,
                                        component=component,rule="positive-weight trapezoid1025",energy_eV_baryon=float(values2[j])))
        ax=axes[2,col]
        for n,color,ls in ((513,".55","--"),(1025,PLANCK,"-")):
            d=case["dense"][n]; diag=diagnostics(d)
            names=d["integrand_names"].tolist()
            net=names.index("gas_source_minus_work");through=names.index("absolute_throughput")
            energy=diag["gas_energy_J_per_baryon"]-diag["gas_energy_J_per_baryon"][0]
            cum=d["cumulative_trapezoid_J_per_baryon"][:,net]
            integrals=simpson(d["integrands_J_per_baryon_per_x"],x=d["x"],axis=0)
            normalization=float(integrals[through])
            residual=(energy-cum)/normalization
            endpoint=float((energy[-1]-integrals[net])/normalization)
            declared=case["receipt"]["energy_integrals"][f"dense_{n}"]["residual_scaled"]
            if not np.isclose(abs(endpoint),declared,rtol=2e-12,atol=2e-16):
                raise ValueError("GAS_ENDPOINT_ARITHMETIC_MISMATCH:"+seed)
            ax.plot(d["z"],residual,color=color,ls=ls,label=f"Cumulative trapezoid, {n} nodes")
            ax.plot(d["z"][-1],endpoint,marker="o" if n==1025 else "s",color=color,
                    markersize=5,clip_on=False,label=f"Simpson endpoint, {n} nodes")
            for name,values2 in (("x",d["x"]),("z",d["z"]),("delta_energy_eV_baryon",energy/EV_J),
                                 ("cumulative_net_eV_baryon",cum/EV_J),("residual_scaled",residual),
                                 ("endpoint_Simpson_residual_scaled",np.array(endpoint))):
                arrays[f"balance_{seed}_{n}_"+name]=values2
            endpoint_rows.append(dict(seed=seed,nodes=n,normalization="Simpson absolute throughput on same grid",
                                      signed_Simpson_residual_scaled=endpoint,absolute_Simpson_residual_scaled=abs(endpoint),
                                      endpoint_delta_energy_eV_baryon=float(energy[-1]/EV_J),
                                      endpoint_net_input_Simpson_eV_baryon=float(integrals[net]/EV_J),
                                      absolute_throughput_Simpson_eV_baryon=normalization/EV_J))
            balance_rows += [dict(seed=seed,nodes=n,x=float(d["x"][j]),z=float(d["z"][j]),
                                  delta_energy_eV_baryon=float(energy[j]/EV_J),
                                  cumulative_net_trapezoid_eV_baryon=float(cum[j]/EV_J),
                                  signed_residual_over_final_throughput=float(residual[j])) for j in range(len(energy))]
        ax.axhline(0,color=".4",lw=.7);redshift_axis(ax,d["z"])
        ax.ticklabel_format(axis="y",style="sci",scilimits=(-2,2))
        ax.set_ylabel("Signed gas balance / final throughput")
        ax.set_title(f"({'ef'[col]}) Total gas energy audit",loc="left")
        ax.legend(fontsize=8,loc="best")
        ax.text(.03,.97,f"1025-node endpoint |residual| = {abs(endpoint):.3g}",
                transform=ax.transAxes,va="top",fontsize=8.5,
                bbox=dict(facecolor="white",edgecolor="none",alpha=.85,pad=2))
    fig.suptitle("Energy transfers on the newly evolved actual_hot paths",fontsize=16,y=.995)
    fig.subplots_adjust(left=.135,right=.90,top=.945,bottom=.12,wspace=.70,hspace=.55)
    fig.text(.5,.023,"Refined paths; positive = gain. Modeled energy bars use dense1025 Simpson. Gas audit includes binding energy and expansion work.\n"
             "CI/CE bars are omitted-process diagnostics, not exchanges applied by the ODE. CI kinetic and binding transfers cancel in total gas.\n"
             "Solid CI/CE bars: both interval endpoints in fit range. Hatched: continuation / boundary, without a published accuracy claim. Li CI/CE and He I CE remain unavailable.",
             ha="center",va="bottom",fontsize=9)
    save_csv(output/"02_energy_budget.csv",budget_rows)
    save_csv(output/"02_gas_balance_curves.csv",balance_rows)
    save_csv(output/"02_gas_balance_endpoints.csv",endpoint_rows)
    return save_figure(fig,output,"02_energy_transfers_and_audit")


def metric_values(first,second):
    raw=first["raw_state"]-second["raw_state"]
    stress=first["signed_observables"][:,1:]-second["signed_observables"][:,1:]
    return np.array([np.max(abs(raw[:,62])),np.max(abs(raw[:,40:61])),
                     np.max(abs(raw[:,61])),np.max(abs(stress))],dtype=float)


def refinement_figure(data,summary,output,arrays):
    values=np.zeros((len(SEEDS),len(METRICS),4))
    rows=[]
    for j,seed in enumerate(SEEDS):
        hn=data[label(seed,"actual_hot",False)]["raw"];hr=data[label(seed,"actual_hot")]["raw"]
        pn=data[label(seed,"planck_reference",False)]["raw"];pr=data[label(seed,"planck_reference")]["raw"]
        for candidate in (hn,hr,pn):
            if not np.array_equal(candidate["x"],pr["x"]):
                raise ValueError("REFINEMENT_GRID_MISMATCH:"+seed)
        values[j,:,0]=metric_values(hr,pr)
        values[j,:,1]=metric_values(hn,hr)
        values[j,:,2]=metric_values(pn,pr)
        values[j,:,3]=values[j,:,1]+values[j,:,2]
        for k,metric in enumerate(METRICS):
            declared=summary["branch_comparisons"][seed]["resolution"][metric]
            if not np.allclose(values[j,k,[0,3]],
                               [declared["branch_difference"],declared["sum_of_observed_refinement_changes"]],rtol=3e-14,atol=0):
                raise ValueError("BRANCH_SUMMARY_MISMATCH:"+seed+":"+metric)
            rows.append(dict(seed=seed,metric=metric,refined_branch_difference=float(values[j,k,0]),
                             actual_hot_nominal_refined_change=float(values[j,k,1]),
                             planck_nominal_refined_change=float(values[j,k,2]),
                             sum_of_observed_refinement_changes=float(values[j,k,3]),
                             branch_exceeds_sum=bool(values[j,k,0]>values[j,k,3]),
                             scope="maxima on 109 saved comparison nodes; finite observed changes, not rigorous error bounds"))
    arrays["comparison_seeds"]=np.array(SEEDS);arrays["comparison_metrics"]=np.array(METRICS)
    arrays["comparison_series"]=np.array(["refined_branch_difference","actual_hot_refinement","planck_reference_refinement","sum_refinements"])
    arrays["comparison_maxima"]=values
    fig,axes=plt.subplots(2,2,figsize=(13.7,9.0))
    titles=("(a) Gas temperature","(b) Conditional ionic fractions","(c) Accumulated Thomson depth","(d) Signed stresses, excluding shear")
    ylabels=("max |Δ ln T|","max |Δ(Yᵢ / isotope scale)|","max |Δτ|","max |ΔP| over five stress entries")
    series=("Branch difference, refined","Actual-hot refinement change","Planck refinement change","Sum of observed refinement changes")
    colors=(PURPLE,HOT,PLANCK,".6")
    xpos=np.arange(len(SEEDS));width=.18
    for k,ax in enumerate(axes.flat):
        positive=values[:,k,:][values[:,k,:]>0]
        if not positive.size:
            raise ValueError("NO_POSITIVE_COMPARISON_FOR_LOG_PLOT:"+METRICS[k])
        ymin,ymax=float(positive.min())/4,float(positive.max())*12
        for j,(name,color) in enumerate(zip(series,colors)):
            offset=(j-1.5)*width;v=values[:,k,j]
            ax.bar(xpos+offset,np.where(v>0,v,np.nan),width*.9,color=color,label=name,
                   hatch="////" if j==3 else None,edgecolor=".4" if j==3 else "none",linewidth=.5)
            for x,value in zip(xpos+offset,v):
                if value==0:
                    ax.text(x,ymin*1.2,"0",ha="center",va="bottom",fontsize=9)
        ax.set_yscale("log");ax.set_ylim(ymin,ymax)
        ax.set_xticks(xpos,SEEDS);ax.set_ylabel(ylabels[k]);ax.set_title(titles[k],loc="left")
        ax.grid(axis="y",alpha=.18)
        for j,seed in enumerate(SEEDS):
            ratio=values[j,k,0]/values[j,k,3] if values[j,k,3]>0 else None
            text=f"D / (Rₕ + Rₚ) = {ratio:.3g}" if ratio is not None else "Rₕ + Rₚ = 0"
            ax.text((j+.5)/2,.96,text,transform=ax.transAxes,ha="center",va="top",fontsize=9)
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=2,loc="upper center",bbox_to_anchor=(.5,.952),fontsize=9.5)
    fig.suptitle("Branch differences compared with observed refinement changes",fontsize=15,y=.995)
    fig.subplots_adjust(left=.09,right=.975,top=.82,bottom=.125,wspace=.29,hspace=.34)
    fig.text(.5,.026,"D is the actual_hot − Planck_reference difference on refined solutions. Rₕ and Rₚ are each branch's nominal − refined change.\n"
             "All bars show maximum absolute differences on 109 saved nodes. These are empirical finite-resolution comparisons, not rigorous or global error bounds.\n"
             "Stress panel uses columns 1–5 of the signed six-vector; its shear coordinate is excluded. Exact zeros are labeled 0, not assigned a log-scale floor.",
             ha="center",va="bottom",fontsize=9)
    save_csv(output/"03_branch_vs_refinement.csv",rows)
    return save_figure(fig,output,"03_branch_vs_refinement")


def run(analysis,campaign,output):
    analysis,campaign,output=Path(analysis).resolve(),Path(campaign).resolve(),Path(output).resolve()
    start=time.perf_counter()
    data,summary,receipt,inputs=load_inputs(analysis,campaign)
    # Input validation is complete before starting a create-only render set.
    output.mkdir(parents=True,exist_ok=False)
    save_json(output/"STARTED.json",dict(started_utc=datetime.now(timezone.utc).isoformat(),
              command=sys.argv,plotter_sha256=sha(__file__),input_analysis_sha256=sha(analysis/"RESULT.json"),
              new_ODE_integrations=0,old_IVP_reruns=0))
    try:
        style();arrays={};figures={}
        figures.update(temperature_figure(data,output,arrays))
        figures.update(energy_figure(data,output,arrays))
        figures.update(refinement_figure(data,summary,output,arrays))
        buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
        save_bytes(output/"plot_data.npz",buffer.getvalue())
        with np.load(output/"plot_data.npz",allow_pickle=False) as check:
            for key,value in arrays.items():
                if not np.array_equal(check[key],value):
                    raise ValueError("PLOTTED_ARRAY_READBACK_MISMATCH:"+key)
        for path,record in inputs.items():
            if sha(path)!=record["sha256"]:
                raise ValueError("INPUT_CHANGED_DURING_RENDER:"+path)
        manifest=dict(status="RENDERED_AWAITING_INDEPENDENT_VISUAL_REVIEW",figures=figures,
             inputs=inputs,source_identity=receipt["source_identity"],runtime_identity=receipt["runtime_identity"],
             plotter_sha256=sha(__file__),new_ODE_integrations=0,old_IVP_reruns=0,
             environment=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__),
             plotted_data=dict(npz="plot_data.npz",array_count=len(arrays),
                 csv_files=sorted(p.name for p in output.glob("*.csv"))),
             conventions=dict(temperature="refined existing and new paths; 109 comparison points",
                 energy="refined actual_hot paths; dense1025 modeled Simpson integrals",
                 collisions="omitted-process diagnostics; positive-weight trapezoid support partition; no actual CI/CE exchange claim",
                 balance="signed cumulative trapezoid residual; separately marked signed Simpson endpoints",
                 comparison="refined branch difference vs both observed nominal/refined changes; stress-only excludes shear",
                 clock="any supplied elapsed_Myr is cumulative since donor z20, not reset at restart"),
             limitations=["No actual-grey-spectrum reconstruction or Compton photon-energy backreaction",
                          "Below-support CI/CE contributions are analytic continuations; unavailable channels are not zero rates",
                          "Sampled differences are not rigorous or global numerical error bounds",
                          "PNG CRC/decompression and PDF buffer structure checked; independent visual review pending"],
             physical_status="HOLD",production="NOT_APPROVED",global_convergence="NOT_RUN",REI_activation=False,
             wall_seconds=time.perf_counter()-start,
             outputs={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(output.iterdir()) if p.is_file()})
        save_json(output/"FIGURE_MANIFEST.json",manifest)
        print(json.dumps(dict(status=manifest["status"],output=str(output),figure_pairs=3,
                              arrays=len(arrays),wall_seconds=manifest["wall_seconds"]),indent=2))
        return manifest
    except Exception as exc:
        save_json(output/"FAILED.json",dict(status="FAILED",error=repr(exc),traceback=traceback.format_exc(),
                  wall_seconds=time.perf_counter()-start,retained_files=sorted(p.name for p in output.iterdir()),
                  new_ODE_integrations=0,old_IVP_reruns=0))
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--analysis",type=Path,default=UNIT/"results/analysis_v1")
    parser.add_argument("--campaign",type=Path,default=UNIT/"results/compton8")
    parser.add_argument("--output",type=Path,default=UNIT/"figures/v1")
    args=parser.parse_args()
    run(args.analysis,args.campaign,args.output)
