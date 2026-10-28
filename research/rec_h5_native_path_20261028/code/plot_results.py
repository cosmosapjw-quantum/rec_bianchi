"""Render saved finite-record diagnostics only; never import the native producer."""
from collections import Counter
from fractions import Fraction
import json
import math
import os
from pathlib import Path

import common as C

OUTPUT_NAMES=('NATIVE_COMMITTED_AND_WRITER.png','H5_AFFINE_AND_RECURRENCE.png',
              'NATIVE_PATH_FIGURES.pdf','FIGURE_RECEIPT.json')


def display_number(value):
    """Display-only conversion; exact saved rational records remain authoritative."""
    if value is None:
        return math.nan
    if isinstance(value,str):
        number=float.fromhex(value) if '0x' in value.lower() else float(Fraction(value))
    else:
        number=float(value)
    if not math.isfinite(number):
        raise ValueError('NONFINITE_SAVED_PLOT_VALUE')
    return number


def run(output:Path):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if any((output/name).exists() for name in OUTPUT_NAMES):
        raise FileExistsError('PLOT_OUTPUT_ALREADY_EXISTS')
    source=C.UNIT/'results/analysis001/PLOT_DATA.json'
    data=json.loads(source.read_text())
    nodes=data['nodes'];queries=data['queries'];recurrences=data['recurrences']
    C.check(len(queries)==313 and [q['incoming_index'] for q in queries]==list(range(313)),
            'WRONG_SAVED_QUERY_ORDER')
    C.check(data['physical_coverage']=='0/313','CHANGED_PHYSICAL_PLOT_SCOPE')
    C.check(bool(nodes),'MISSING_SAVED_NODES')
    for key,unit in {'Tm_ratio':'dimensionless','writer_xe_delta':'dimensionless',
                     'writer_Tm_delta':'K','normalized':'abs(rho)/gross'}.items():
        C.check(data['units'][key]==unit,'CHANGED_SAVED_PLOT_UNIT:'+key)
    os.environ.setdefault('MPLCONFIGDIR',str(output/'mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    plt.rcParams.update({'font.size':8,'axes.titlesize':9,'axes.labelsize':8,
                         'figure.dpi':100,'savefig.dpi':130})
    figures=[]
    try:
        fig,axes=plt.subplots(3,2,figsize=(11.7,8.3),constrained_layout=True)
        figures.append(fig)
        x=[r['local'] for r in nodes]
        for ax,key,title,unit in [
                (axes[0,0],'xe','Committed electron fraction','dimensionless'),
                (axes[0,1],'Tm_ratio','Committed Tm / [T0 (1 + z)]','dimensionless'),
                (axes[1,0],'writer_xe_delta','Final writer xe minus committed xe','dimensionless'),
                (axes[1,1],'writer_Tm_delta','Final writer TM/kN minus committed Tm','K; diagnostic conversion')]:
            ax.plot(x,[display_number(r.get(key)) for r in nodes],lw=.8)
            ax.set(title=title,xlabel='Integer local slot',ylabel=unit)
            ax.grid(alpha=.2)
        phases=['HEIII_SAHA','HE_ONLY','H_HE','H_STEADY','H_TM','LOW_PEEBLES']
        for r in nodes:
            C.validate_phase(r['phase'])
        axes[2,0].step(x,[phases.index(r['phase']) for r in nodes],where='post',lw=.8)
        axes[2,0].set(yticks=range(len(phases)),yticklabels=phases,
                      xlabel='Integer local slot',title='Recorded native phase')
        writer_ids=[r.get('writer_id') for r in nodes]
        available=sum(v is not None for v in writer_ids)
        if available:
            axes[2,1].plot(x,[display_number(v) for v in writer_ids],lw=.8)
            axes[2,1].set(ylabel='Actual dispatcher call ID')
        else:
            axes[2,1].text(.5,.5,'Writer call IDs absent in saved plot packet',
                           transform=axes[2,1].transAxes,ha='center',va='center',wrap=True)
        axes[2,1].set(xlabel='Integer local slot',title='Final FULL writer ownership')
        fig.suptitle('Native committed state and final writer diagnostics\n'
                     'Distinct saved views; physical bound coverage 0/313',fontsize=12)

        fig2,axes2=plt.subplots(4,2,figsize=(11.7,11.7),constrained_layout=True)
        figures.append(fig2)
        qx=[q['incoming_index'] for q in queries]
        fields=[('writer','xe','dimensionless'),('writer','TM_eV','eV'),
                ('writer','H_s_inv','s^-1'),('writer','nH_cm3','cm^-3'),
                ('committed','xe','dimensionless'),('committed','Tm_K','K')]
        for ax,(view,key,unit) in zip(axes2.flat,fields):
            records=[q['fields'][view][key] for q in queries]
            slope=[display_number(r['slope']) for r in records]
            low=[display_number(r['min']) for r in records]
            high=[display_number(r['max']) for r in records]
            ax.plot(qx,slope,color='tab:blue',lw=.7,label='Saved exact affine slope')
            ax.set(title=view+' '+key,xlabel='H5 incoming query index',
                   ylabel=unit+' per eta (slope)')
            ax.tick_params(axis='y',labelcolor='tab:blue')
            twin=ax.twinx()
            twin.fill_between(qx,low,high,color='tab:orange',alpha=.25,
                              label='Saved endpoint range')
            twin.set_ylabel(unit+' (endpoint range)',color='tab:orange')
            twin.tick_params(axis='y',labelcolor='tab:orange')
            ax.grid(alpha=.15)
        components=sorted({r['component'] for r in recurrences})
        positive_count=0;zero_counts=Counter();nonzero_counts=Counter()
        ax=axes2[3,0]
        for component in components:
            selected=[r for r in recurrences if r['component']==component]
            positive=[]
            for row in selected:
                norm=Fraction(row['normalized']);rho=Fraction(row['rho'])
                C.check(norm>=0,'NEGATIVE_SAVED_NORMALIZED_RESIDUAL')
                if rho==0:
                    zero_counts[component]+=1
                else:
                    nonzero_counts[component]+=1
                if norm>0:
                    positive.append((row['local_in'],float(norm)))
            if positive:
                positive_count+=len(positive)
                ax.scatter([p[0] for p in positive],[p[1] for p in positive],
                           s=3,label=component)
        ax.axhline(float(Fraction(64,2**52)),color='black',ls='--',lw=.8,
                   label='Frozen 64 * 2^-52 arithmetic criterion')
        ax.set_yscale('log')
        ax.set(title='Discrete recurrence arithmetic residuals',
               xlabel='Recorded local input slot',ylabel='abs(rho) / gross; positive values only')
        ax.legend(fontsize=6,loc='best')
        ax.grid(alpha=.15)
        ax=axes2[3,1];locations=list(range(len(components)))
        ax.bar([i-.18 for i in locations],[zero_counts[c] for c in components],
               width=.36,label='Exact zero rho')
        ax.bar([i+.18 for i in locations],[nonzero_counts[c] for c in components],
               width=.36,label='Nonzero rho')
        ax.set(xticks=locations,xticklabels=components,ylabel='Saved integrated records',
               title='Exact zeros counted separately; no log floor')
        ax.legend(fontsize=7)
        fig2.suptitle('Actual 313 saved affine cells and discrete recurrence diagnostics\n'
                      'Endpoint ranges are representation ranges; rho is not a physical defect',fontsize=11)
        fig.savefig(output/OUTPUT_NAMES[0])
        fig2.savefig(output/OUTPUT_NAMES[1])
        with PdfPages(output/OUTPUT_NAMES[2]) as pdf:
            pdf.savefig(fig);pdf.savefig(fig2)
        receipt={'status':'RENDERED_SAVED_DATA_ONLY','input_path':str(source.relative_to(C.REPO)),
                 'input_sha256':C.sha(source),'query_count':len(queries),'node_count':len(nodes),
                 'recurrence_count':len(recurrences),'writer_id_count':available,
                 'positive_normalized_residuals_plotted':positive_count,
                 'exact_zero_rho_by_component':dict(zero_counts),
                 'nonzero_rho_by_component':dict(nonzero_counts),'pdf_pages':2,
                 'outputs':[{ 'name':name,'bytes':(output/name).stat().st_size,
                              'sha256':C.sha(output/name)} for name in OUTPUT_NAMES[:3]],
                 'source_or_RHS_calls':0,'native_runs':0,
                 'rational_to_float_scope':'display only; saved exact packet authoritative',
                 'QSS_semantics':'Native real/virtual QSS vectors are departures xi - xi(eq with 1s); no positivity check.',
                 'physical':dict(C.PHYSICAL),'physical_coverage':'0/313',
                 'H6':'OPEN','H7':'OPEN','L4_ready':False,'REI_activation':False}
        C.dump(output/'FIGURE_RECEIPT.json',receipt)
        return receipt
    finally:
        for figure in figures:
            plt.close(figure)
