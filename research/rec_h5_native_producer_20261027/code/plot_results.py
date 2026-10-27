"""Display enclosures from the saved reference packet; floats used only for plots."""
from pathlib import Path

def plot_packet(packet, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = packet['reference_bounds']
    x = [r['binding']['incoming_index'] for r in rows]
    def midpoint(key):
        return [(float(r['reference_bounds'][key]['lo'])+float(r['reference_bounds'][key]['hi']))/2 for r in rows]
    fig, axes=plt.subplots(2,1,figsize=(10,7),layout='constrained',sharex=True)
    for key,label in [('M1_ref',r'$M_{1,ref}$'),('M2_ref',r'$M_{2,ref}$')]:
        axes[0].semilogy(x,midpoint(key),label=label,linewidth=1.5)
    axes[0].set_ylabel('Whole stored-cell reference bound')
    axes[0].legend(); axes[0].grid(alpha=.2)
    for key,label in [('J_ref','Actual reference chord'),('chord_bound','Curvature chord upper bound')]:
        axes[1].semilogy(x,midpoint(key),label=label,linewidth=1)
    axes[1].set_ylabel('Dimensionless reference chord')
    axes[1].set_xlabel('Actual incoming channel index')
    axes[1].legend(); axes[1].grid(alpha=.2)
    fig.suptitle('Native Wien reference: actual 313 bindings\nPhysical coverage remains 0/313')
    figures=Path(output)/'figures'; figures.mkdir(exist_ok=False)
    fig.savefig(figures/'reference_envelopes_and_bridges.png',dpi=160)
    fig.savefig(figures/'reference_envelopes_and_bridges.pdf')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    for key,label in [('B_char','Characteristic bridge magnitude'),('B_TR','Temperature bridge magnitude'),
                      ('old_anchor_radius','Preserved anchor radius'),('R_bridge','Direct chord bridge radius'),
                      ('R_bridge_curvature','Curvature chord bridge radius')]:
        ax.semilogy(x,[abs(v) for v in midpoint(key)],label=label,linewidth=1.2)
    ax.set(xlabel='Actual incoming channel index',ylabel='Dimensionless representation radius',
           title='Native-to-absolute-interpolant representation bounds')
    ax.legend(); ax.grid(alpha=.2)
    fig.savefig(figures/'representation_radii.png',dpi=160)
    plt.close(fig)
