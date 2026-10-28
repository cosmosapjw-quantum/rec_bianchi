"""Generate observation-only copies of locked native source; never build/run it."""
import difflib
import json
from pathlib import Path
import re
import shutil
from common import UNIT,REPO,verify_locks,sha,dump,check

def function(text,name,transform):
    match=re.search(r'^(?:void|double)\s+'+re.escape(name)+r'\s*\([^;]*?\)\s*\{',text,re.M)
    check(match is not None,'SOURCE_FUNCTION_NOT_FOUND:'+name)
    begin=match.start();brace=text.index('{',match.start());depth=1;end=brace+1
    while depth:
        if text[end]=='{':depth+=1
        elif text[end]=='}':depth-=1
        end+=1
    old=text[begin:end];new=transform(old)
    return text[:begin]+new+text[end:]

def one(s,old,new):
    check(s.count(old)==1,'SOURCE_INSERTION_CARDINALITY:'+old[:100])
    return s.replace(old,new,1)

def declarations(s,decl):
    pos=s.index('{')+1
    return s[:pos]+'\n'+decl+'\n'+s[pos:]

def hooks_history(text):
    text=one(text,'#include "history.h"','#include "history.h"\n#include "capture_support.h"')
    def post(s):
        # Wrappers remain operands of the original subtraction expression.
        s=one(s,'rec_dxHIIdlna(MODEL, xHIISaha + xHeII_out','cap_dispatch("post_saha_base", MODEL, xHIISaha + xHeII_out')
        s=one(s,'rec_dxHIIdlna(MODEL, xHIISaha+Dxe + xHeII_out','cap_dispatch("post_saha_plus", MODEL, xHIISaha+Dxe + xHeII_out')
        return one(s,'rec_dxHIIdlna(MODEL, xHIISaha-Dxe + xHeII_out','cap_dispatch("post_saha_minus", MODEL, xHIISaha-Dxe + xHeII_out')
    text=function(text,'rec_xH1s_postSaha',post)
    def helium(s):
        s=declarations(s,'    double cap_x=*xHeII,cap_p=*dxHeIIdlna_prev,cap_p2=*dxHeIIdlna_prev2;\n    int cap_integrated=(*post_saha==0);')
        return s[:-1]+'\n    cap_recur("xHeII",cap_global_in(),cap_x,*xHeII,dxHeIIdlna,cap_p,cap_p2,*dxHeIIdlna_prev,*dxHeIIdlna_prev2,1,cap_integrated,0);\n}'
    text=function(text,'rec_get_xe_next1_He',helium)
    def hhe(s):
        s=declarations(s,'    double cap_hp=*dxHIIdlna_prev,cap_hp2=*dxHIIdlna_prev2,cap_hep=*dxHeIIdlna_prev,cap_hep2=*dxHeIIdlna_prev2;\n    int cap_integrated=(*post_saha==0);unsigned long cap_rhs_id;')
        s=one(s,'rec_dxHIIdlna(MODEL, xe_in','cap_dispatch("h_he_input", MODEL, xe_in')
        end='iz_in-param->izH0, z_in, param->fsR, param->meR);'
        s=one(s,end,end+'\n       cap_rhs_id=cap_last_call();')
        return s[:-1]+'''\n    cap_recur("xHeII",iz_in,xHeII_in,*xHeII,dxHeIIdlna,cap_hep,cap_hep2,*dxHeIIdlna_prev,*dxHeIIdlna_prev2,1,1,0);
    cap_recur("xH1s",iz_in,xH1s_in,*xH1s,dxHIIdlna,cap_hp,cap_hp2,*dxHIIdlna_prev,*dxHIIdlna_prev2,-1,cap_integrated,cap_rhs_id);
}'''
    text=function(text,'get_rec_next2_HHe',hhe)
    def hydrogen(s):
        s=declarations(s,'    double cap_p=*dxedlna_prev,cap_p2=*dxedlna_prev2;\n    int cap_integrated=(*post_saha==0);unsigned long cap_rhs_id;')
        s=one(s,'rec_dxHIIdlna(model, xe_in','cap_dispatch("h_steady_input", model, xe_in')
        end='iz-param->izH0, z_in, param->fsR, param->meR);'
        s=one(s,end,end+'\n    cap_rhs_id=cap_last_call();')
        return s[:-1]+'\n    cap_recur("xe",iz,xe_in,*xe_out,dxedlna,cap_p,cap_p2,*dxedlna_prev,*dxedlna_prev2,1,cap_integrated,cap_rhs_id);\n}'
    text=function(text,'rec_get_xe_next1_H',hydrogen)
    def thermal(s):
        s=declarations(s,'    double cap_p=*dxedlna_prev,cap_p2=*dxedlna_prev2,cap_tp=*dTmdlna_prev,cap_tp2=*dTmdlna_prev2;\n    unsigned long cap_rhs_id;')
        s=one(s,'rec_dxHIIdlna(model, xe_in','cap_dispatch("h_tm_input", model, xe_in')
        end='iz-param->izH0, z_in, param->fsR, param->meR);'
        s=one(s,end,end+'\n    cap_rhs_id=cap_last_call();')
        return s[:-1]+'''\n    cap_recur("xe",iz,xe_in,*xe_out,dxedlna,cap_p,cap_p2,*dxedlna_prev,*dxedlna_prev2,1,1,cap_rhs_id);
    cap_recur("Tm_K",iz,Tm_in,*Tm_out,dTmdlna,cap_tp,cap_tp2,*dTmdlna_prev,*dTmdlna_prev2,1,1,cap_rhs_id);
}'''
    text=function(text,'rec_get_xe_next2_HTm',thermal)
    def driver(s):
        s=one(s,'Dfminus_hist = create_2D_array',
            'cap_init(param->izH0,param->nz,param->nzrt,param->zH0,param->T0,param->nH0,param->fHe,param->obh2,param->omh2,param->okh2,param->odeh2,param->w0,param->wa,param->Y,param->Nnueff);\n   Dfminus_hist = create_2D_array')
        s=one(s,'Tm_output[iz] = param->T0 * (1.+z);',
              'Tm_output[iz] = param->T0 * (1.+z);\n       cap_phase("HEIII_SAHA",iz);cap_node(iz,z,xe_output[iz],Tm_output[iz],0,0.,0.,0);')
        s=one(s,'rec_get_xe_next1_He(param, z,','cap_phase("HE_ONLY",iz-1);\n        rec_get_xe_next1_He(param, z,')
        s=one(s,'get_rec_next2_HHe(param, iz-1,','cap_phase("H_HE",iz-1);\n      get_rec_next2_HHe(param, iz-1,')
        s=one(s,'rec_get_xe_next1_H(param, z,','cap_phase("H_STEADY",iz-1);\n        rec_get_xe_next1_H(param, z,')
        s=one(s,'rec_get_xe_next2_HTm(MODEL,','cap_phase("H_TM",iz-1);\n         rec_get_xe_next2_HTm(MODEL,')
        s=one(s,'rec_get_xe_next2_HTm(PEEBLES,','cap_phase("LOW_PEEBLES",iz-1);\n        rec_get_xe_next2_HTm(PEEBLES,')
        # Three steady-temperature assignments share an expression; preserve
        # exact text and append the appropriate committed-node observer.
        expr='Tm_output[iz] = rec_Tmss(xe_output[iz], param->T0*(1.+z), rec_HubbleConstant(param, z), param->fHe, param->fsR, param->meR);'
        check(s.count(expr)==3,'STEADY_NODE_CARDINALITY')
        replacements=[expr+'\n        cap_node(iz,z,xe_output[iz],Tm_output[iz],1,xH1s,xHeII,0);',
                      expr+'\n      cap_node(iz,z,xe_output[iz],Tm_output[iz],1,xH1s,xHeII,0);',
                      expr+'\n        cap_node(iz,z,xe_output[iz],Tm_output[iz],0,0.,0.,1);']
        pieces=s.split(expr);s=pieces[0]+''.join(rep+tail for rep,tail in zip(replacements,pieces[1:]))
        # The two differential-temperature loops finish by assigning z.
        for native,phase in [('MODEL','H_TM'),('PEEBLES','LOW_PEEBLES')]:
            marker='cap_phase("'+phase+'",iz-1);'
            pos=s.index(marker);end=s.index('z = (1.+ZSTART)*exp(-DLNA*iz) - 1.;',pos)
            end+=len('z = (1.+ZSTART)*exp(-DLNA*iz) - 1.;')
            s=s[:end]+'\n         cap_node(iz,z,xe_output[iz],Tm_output[iz],0,0.,0.,1);'+s[end:]
        for component,prev,p2,arr,sub1,sub2 in [
            ('xHeII','dxHeIIdlna_prev','dxHeIIdlna_prev2','xe_output','0.','0.'),
            ('xHII','dxHIIdlna_prev','dxHIIdlna_prev2','xe_output','dxHeIIdlna_prev','dxHeIIdlna_prev2'),
            ('Tm_K','dTmdlna_prev','dTmdlna_prev2','Tm_output','0.','0.')]:
            # Insert after the assignment of the first previous memory.
            pattern=r'('+re.escape(prev)+r'\s*=\s*\('+re.escape(arr)+r'\[iz-1\][^;]+;)'
            found=list(re.finditer(pattern,s));check(len(found)==1,'SEED_CARDINALITY:'+component)
            m=found[0];hook=f'\n   cap_seed("{component}",iz,{prev},{p2},{arr}[iz-1],{arr}[iz-2],{arr}[iz-3],{arr}[iz-4],{sub1},{sub2});'
            s=s[:m.end()]+hook+s[m.end():]
        s=one(s,'free_2D_array(Dfminus_hist, NVIRT);','cap_final(Dfminus_hist,Dfminus_Ly_hist,Dfnu_hist,twog_params->Eb_tab);\n     free_2D_array(Dfminus_hist, NVIRT);')
        return s
    return function(text,'rec_build_history',driver)

def generate():
    locks=verify_locks();source=UNIT/'build/source';source.mkdir(parents=True,exist_ok=False)
    originals=UNIT/'inputs/original/HyRec'
    for p in originals.iterdir():
        if p.is_file():shutil.copyfile(p,source/p.name)
    diff=[]
    for name in ('history.c','hydrogen.c','hyrec.c'):
        old=(source/name).read_bytes().decode('utf-8');normalized=old.replace('\r\n','\n')
        if name=='history.c':new=hooks_history(normalized)
        elif name=='hydrogen.c':
            new=one(normalized,'#include "hydrogen.h"','#include "hydrogen.h"\n#include "capture_support.h"')
            statement='for (b = 0; b < NVIRT; b++) Dfnu_hist[b][iz] = xv[b]/x1s;'
            new=one(new,statement,statement+'\n   cap_full_write(iz,xr,xv,Dfminus_hist,Dfminus_Ly_hist,Dfnu_hist,Dfplus,Dfplus_Ly,TM,TR);')
        else:
            new=one(normalized,'#include "hyrec_params.h"','#include "hyrec_params.h"\n#include "capture_support.h"')
            new=one(new,'free(xe_output);','cap_finish();\n    free(xe_output);')
        # Restore the original line convention for the observation copy.
        if '\r\n' in old:new=new.replace('\n','\r\n')
        (source/name).write_bytes(new.encode())
        diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='canonical/'+name,tofile='instrumented/'+name))
    for name in ('capture_support.c','capture_support.h'):shutil.copyfile(UNIT/'code'/name,source/name)
    (UNIT/'build/INSTRUMENTATION.diff').write_text(''.join(diff))
    dump(UNIT/'build/SOURCE_GENERATION.json',{'status':'PREPARED_SOURCE_ONLY_NOT_BUILT','original_locks':locks,
        'instrumented_files':{p.name:sha(p) for p in source.iterdir() if p.suffix in ('.c','.h')},
        'diff_sha256':sha(UNIT/'build/INSTRUMENTATION.diff')})
    return source

if __name__=='__main__':generate()
