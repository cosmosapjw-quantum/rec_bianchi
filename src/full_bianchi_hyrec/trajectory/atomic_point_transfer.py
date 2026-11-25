"""Bounded positive source-packet map and exact native diffusion ownership split.

No finite width is inferred for native spikes. This module maps a supplied
point EVENT RATE into the COM parent-owned number representation. It does
not solve the coupled occupation/population residual or admit an owner swap.
"""
from __future__ import annotations
import numpy as np
from scipy.constants import h,e,k
from .hyrec_two_photon_raman import OriginalHyRecTwoPhotonRamanTable,PhysicalTwoPhotonRamanBin,A2S_THRESHOLD_EV
from ..recoil.original_hyrec_native import populate_original_hyrec_diffusion,build_native_diffusion_network
from ..recoil.calibrated_source import owner_cells,PCC

def point_partition(energy_eV,bounds,sub):
    """P maps point counts to hat nodes; P.T is the dual point functional."""
    bounds=np.asarray(bounds,float);energy=np.asarray(energy_eV,float)
    if sub<1 or bounds.ndim!=2 or bounds.shape[1]!=2:raise ValueError("invalid point partition")
    x=np.linspace(bounds[:,0],bounds[:,1],sub+1,axis=1)
    det=(energy*e/h-PCC.nu_abs)/PCC.dnu
    idx=np.flatnonzero((det>=bounds.min())&(det<=bounds.max()))
    P=np.zeros((x.size,len(idx)))
    for col,i in enumerate(idx):
        matches=np.flatnonzero((bounds[:,0]<=det[i])&(det[i]<=bounds[:,1]))
        if not len(matches):raise ValueError("uncovered point support")
        parent=int(matches[0]);nodes=x[parent]
        left=int(np.clip(np.searchsorted(nodes,det[i],side="right")-1,0,sub-1))
        t=(det[i]-nodes[left])/(nodes[left+1]-nodes[left])
        P[parent*(sub+1)+left:parent*(sub+1)+left+2,col]=[1-t,t]
    return x.ravel(),idx,P,det[idx]

def audit_source(archive,Tm,Tr,x1s,x2s,sub):
    tab=OriginalHyRecTwoPhotonRamanTable.from_archive(archive)
    x,idx,P,det=point_partition(tab.energy_eV,owner_cells(),sub)
    canonical=tab.evaluate_canonical_coupling(radiation_temperature_eV=k*Tr/e)
    raw=np.column_stack([tab.energy_eV,tab.integrated_rates_s_inv.T])
    # A1s is unchanged by the table's A2s normalization.
    native=build_native_diffusion_network(populate_original_hyrec_diffusion(raw,Tm))
    Q=native.generator_s_inv;parts={name:np.zeros_like(Q) for name in ("inside","cross","outside","centre")}
    counts={name:0 for name in parts};cross=[]
    inside=set(idx.tolist())
    for i in range(len(Q)):
        for j in range(i+1,len(Q)):
            if Q[i,j]==0 and Q[j,i]==0:continue
            a,b=map(int,native.source_indices[[i,j]])
            typ="centre" if -1 in (a,b) else "inside" if a in inside and b in inside else "cross" if (a in inside)!=(b in inside) else "outside"
            counts[typ]+=1
            if typ=="cross":cross.append([a,b])
            parts[typ][i,j]=Q[i,j];parts[typ][j,i]=Q[j,i]
    for M in parts.values():np.fill_diagonal(M,-M.sum(axis=0))
    scale=max(np.max(abs(Q)),1e-300)
    reassembly=float(np.max(abs(sum(parts.values())-Q))/scale)
    pi=native.equilibrium_proxy
    balance=max(float(np.max(abs(M@pi))/(scale*np.max(pi))) for M in parts.values())
    gains=np.zeros(len(idx));losses=gains.copy();thermal=0.;compan=0.;atom=0.;jvp_error=0.;events=0
    trans=A2S_THRESHOLD_EV*e/h
    eq=x1s*np.exp(-h*trans/(k*Tr))
    for j,i in enumerate(idx):
        rate=tab.A2s_s_inv[i]
        if rate==0:continue
        tracked=tab.energy_eV[i]*e/h;comp=abs(trans-tracked);kind=tab.process_kind("2s",i)
        fc=1/np.expm1(h*comp/(k*Tr));ft=1/np.expm1(h*tracked/(k*Tr))
        def event(upper):return PhysicalTwoPhotonRamanBin(kind,rate,trans,comp,tracked,upper,x1s,1.)
        ev=event(x2s);events+=1
        gains[j],losses[j]=ev.paired_rates(companion_occupation=fc,tracked_occupation=ft)
        a,b=event(eq).paired_rates(companion_occupation=fc,tracked_occupation=ft)
        thermal=max(thermal,abs(a-b)/max(a+b,1e-300))
        net=gains[j]-losses[j]
        compan+=h*comp*(1 if kind=="two_photon" else -1)*net
        atom-=h*trans*net
        # Linear-in-tracked-f JVP, independent centered finite difference.
        df=ft*1e-3
        jac=ev.jvp(companion_occupation=fc,tracked_occupation=ft,d_integrated_rate_s_inv=0.,d_upper_population=0.,d_ground_population=0.,d_companion_occupation=0.,d_tracked_occupation=df)
        fd=(ev.net_action(fc,ft+df)-ev.net_action(fc,ft-df))/2
        jvp_error=max(jvp_error,abs(jac-fd)/max(abs(jac),abs(fd),1e-300))
    gross=float(gains.sum()+losses.sum());net=gains-losses;dep=P@net
    packet_e=h*(PCC.nu_abs+PCC.dnu*x);point_e=tab.energy_eV[idx]*e
    energy_scale=max(gross*max(point_e),1e-300)
    return dict(Tm=Tm,Tr=Tr,x1s=x1s,x2s=x2s,subcells=sub,indices=idx.tolist(),detuning=det.tolist(),native_inside=counts["inside"],native_cross=counts["cross"],native_outside=counts["outside"],native_centre=counts["centre"],cross_edges=cross,native_reassembly_relative=reassembly,native_split_equilibrium_relative=balance,canonical_real_to_virtual_inside_fraction=float(canonical.real_to_virtual_s_inv[:,idx].sum()/canonical.real_to_virtual_s_inv.sum()),canonical_virtual_to_real_inside_fraction=float(canonical.virtual_to_real_s_inv[:,idx].sum()/canonical.virtual_to_real_s_inv.sum()),actual_2s_events=events,actual_2s_net_rate_per_H_s=float(net.sum()),source_number_residual=abs(dep.sum()-net.sum())/max(gross,1e-300),source_energy_residual=abs(packet_e@dep-point_e@net)/energy_scale,atom_companion_tracked_energy_residual=abs(packet_e@dep+compan+atom)/energy_scale,thermal_null_relative=thermal,jvp_relative=jvp_error,scope="POINT_PACKET_AND_NATIVE_PROXY_EDGE_SPLIT_ONLY_NO_OWNER_SWAP")
