#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'state/PROJECT_STATE.json').read_text())
print(json.dumps(state,indent=2))
try:
    print('
Git status:')
    print(subprocess.check_output(['git','status','--short','--branch'],cwd=ROOT,text=True))
except Exception as exc:
    print(f'git status unavailable: {exc}')
