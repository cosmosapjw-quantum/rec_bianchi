"""Numerical/schema mutation checks for new components, not full COM physics."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/trajectory/pr05c2c1b2b1e1c_repair'
TEST='tests/trajectory/test_split_context_and_deposition.py'
CASES=[
 ('omit_doppler_width','split_scientific_context.py',
  'for field in fields(value)}}',
  "for field in fields(value) if field.name != 'doppler_width_eV'}}",
  'test_every_scientific_change_invalidates_restart[doppler_width_eV]'),
 ('drop_photon_measure','com_source_deposition.py',
  'result = numerator/self.mode_measure_m3[:,None]',
  'result = numerator/np.ones_like(self.mode_measure_m3)[:,None]',
  'test_number_energy_and_four_moments_use_physical_measure'),
 ('drop_density_jvp','com_source_deposition.py',
  'nH*dr+float(nH_tangent_m3)*rates', 'nH*dr',
  'test_fixed_map_jvp_includes_density_derivative'),
 ('accept_wrong_source_energy','com_source_deposition.py',
  'if not np.isfinite(energy).all() or np.any(np.abs(energy-Es)>g*((np.abs(E)@np.abs(B))+np.abs(Es))):',
  'if False:', 'test_invalid_deposition_is_rejected_before_action[energy]'),
]
results=[]
for label,filename,old,new,selector in CASES:
    with tempfile.TemporaryDirectory(prefix='rec-pr34-component-mutant-') as td:
        root=Path(td)
        for rel in [TEST,'src/full_bianchi_hyrec/trajectory/split_scientific_context.py',
                    'src/full_bianchi_hyrec/trajectory/com_source_deposition.py']:
            target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
        target=root/'src/full_bianchi_hyrec/trajectory'/filename
        text=target.read_text();assert text.count(old)==1,(label,text.count(old))
        target.write_text(text.replace(old,new))
        xml=root/'report.xml'
        run=subprocess.run([sys.executable,'-m','pytest','-q',str(root/TEST)+'::'+selector,
                            '--tb=short','--junitxml='+str(xml)],cwd=root,
                           capture_output=True,text=True,timeout=40,
                           env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
        log=run.stdout+run.stderr;(OUT/f'MUTANT_{label}.log').write_text(log)
        suites=list(ET.parse(xml).getroot().iter('testsuite'))
        errors=sum(int(s.attrib.get('errors',0)) for s in suites)
        failures=sum(int(s.attrib.get('failures',0)) for s in suites)
        assert run.returncode==1 and errors==0 and failures==1,(label,log)
        results.append({'id':label,'selector':selector,'failures':failures,'errors':errors,
                        'scope':'COMPONENT_SOURCE_MUTANT_NOT_FULL_COUPLED_PROOF'})
(OUT/'MUTATIONS.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
