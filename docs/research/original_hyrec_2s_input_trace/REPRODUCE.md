# Read-only numerical-census verification

Run from the repository root with the dependencies already available. This
procedure prints a result without rewriting any source, old evidence or channel
data. It invokes the existing loader and validates the exported values. It does
not compile C, reconstruct original integration regions, or choose `B` or `mu`.

The first extraction used Python 3.12.13 and NumPy 2.3.5. Decimal strings and
hexadecimal binary64 values have different identity roles. A recomputation on a
different arithmetic/runtime lane must not silently overwrite the saved trace.

```bash
PYTHONPATH=src python -B - <<'PY'
import csv
from decimal import Decimal, localcontext
import hashlib
from io import BytesIO, StringIO
import json
from pathlib import Path
import subprocess
import zipfile
import numpy as np
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
    OriginalHyRecTwoPhotonRamanTable, TWO_PHOTON_MEMBER,
    TWO_PHOTON_TABLE_SHA256, A2S_THRESHOLD_EV, L2S_1S_S_INV, NSUBLYA,
)
from full_bianchi_hyrec.recoil.original_hyrec_native import (
    ORIGINAL_HYREC_ARCHIVE_SHA256,
)

root = Path.cwd()
d = root / 'docs/research/original_hyrec_2s_input_trace'
pin = json.loads((d / 'PROVENANCE.json').read_text())
parent = pin['parent_commit']
assert subprocess.check_output(
    ['git', 'rev-parse', parent + '^{tree}'], text=True
).strip() == pin['parent_tree']
subprocess.run(['git', 'merge-base', '--is-ancestor', parent, 'HEAD'], check=True)
for path, identity in pin['repository_files'].items():
    data = (root / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == identity['sha256'], path
    assert subprocess.check_output(
        ['git', 'rev-parse', parent + ':' + path], text=True
    ).strip() == identity['git_blob'], path

archive = root / 'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == ORIGINAL_HYREC_ARCHIVE_SHA256
with zipfile.ZipFile(archive) as z:
    data = z.read(TWO_PHOTON_MEMBER)
    for name, identity in pin['archive_members'].items():
        assert hashlib.sha256(z.read(name)).hexdigest() == identity['sha256']
assert hashlib.sha256(data).hexdigest() == TWO_PHOTON_TABLE_SHA256
lines = data.decode('ascii').splitlines()
raw = np.loadtxt(StringIO(data.decode('ascii')))
table = OriginalHyRecTwoPhotonRamanTable.from_archive(archive)
assert raw.shape == (311, 5) and len(lines) == 311
factor = L2S_1S_S_INV / float(np.sum(raw[:NSUBLYA, 2]))
with localcontext() as ctx:
    ctx.prec = 70
    decimal_sum = sum(Decimal(line.split()[2]) for line in lines[:NSUBLYA])
    decimal_factor = Decimal('8.2206') / decimal_sum
    reference = [Decimal(line.split()[2]) * decimal_factor for line in lines[:NSUBLYA]]
with (d / 'bins_2s.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 140
max_ulp = 0.0
for b, row in enumerate(rows):
    tokens = lines[b].split()
    assert int(row['b']) == b
    assert int(row['source_row_1based']) == int(row['source_line_1based']) == b + 1
    assert row['energy_eV_lexeme'] == tokens[0]
    assert row['raw_A2s_s_inv_lexeme'] == tokens[2]
    assert float(row['energy_eV']) == table.energy_eV[b] == raw[b, 0]
    assert float(row['raw_A2s_s_inv']) == raw[b, 2]
    assert row['normalization_id'] == 'NORM_READ_TWOG_287_290'
    assert float(row['normalization_factor']) == factor
    assert float(row['normalized_A2s_s_inv']) == table.A2s_s_inv[b]
    assert float(row['normalized_A2s_s_inv']).hex() == row['normalized_A2s_binary64_hex']
    ec = Decimal(str(A2S_THRESHOLD_EV)) - Decimal(tokens[0])
    assert Decimal(row['companion_energy_eV_from_decimal_tokens']) == ec
    assert float(row['companion_energy_eV_binary64']) == A2S_THRESHOLD_EV - table.energy_eV[b]
    assert A2S_THRESHOLD_EV / 2 < table.energy_eV[b] < A2S_THRESHOLD_EV
    assert row['original_bin_integral_lower_eV'] == row['original_bin_integral_upper_eV'] == ''
    assert row['extra_multiplicity_applied'] == 'NONE'
    assert row['B_status'] == row['mu_status'] == 'UNRESOLVED'
    max_ulp = max(max_ulp, abs(float(table.A2s_s_inv[b]) - float(reference[b])) /
                  abs(float(np.spacing(float(reference[b])))))
assert np.array_equal(table.integrated_rates_s_inv[[0, 2, 3]], raw[:, [1, 3, 4]].T)
assert np.array_equal(table.A2s_s_inv[140:], raw[140:, 2])

hist = root / 'archive/bundles/Full_Bianchi_HyRec_PR05C2C1B2A_two_photon_raman_source_v0_68.zip'
with zipfile.ZipFile(hist) as z:
    entries = z.read('SHA256SUMS.txt').decode().splitlines()
    for line in entries:
        digest, name = line.split(None, 1)
        assert hashlib.sha256(z.read(name.lstrip('*'))).hexdigest() == digest
    with np.load(BytesIO(z.read('pr05c2c1b2a_two_photon_raman_source_v068.npz')),
                 allow_pickle=False) as a:
        assert np.array_equal(table.energy_eV, a['energy_eV'])
        assert np.array_equal(table.integrated_rates_s_inv, a['integrated_rates_s_inv'])

contract = json.loads((d / 'OWNER_REVIEW_CONTRACT.json').read_text())
for field in ['B', 'mu_m_inv3', 'target_cell_boundaries', 'target_cell_energies_J',
              'angular_rule', 'packet_rate_values', 'n_H_m_inv3', 'map_authority',
              'measure_authority']:
    assert contract['deposition_inputs'][field] is None, field
assert not contract['deposition_inputs']['executed']
assert not contract['deposition_inputs']['jvp_executed']
assert all(o['status'] == 'UNRESOLVED' for o in contract['required_owner_decisions'])
assert contract['review_acceptance']['claim'] == 'NO_PASS_REC_PHYSICAL_SPLIT'
print(json.dumps({'status': 'TRACE_VALUES_AND_IDENTITY_VERIFIED_ONLY',
                  'rows': len(rows), 'raw_sum_decimal': str(decimal_sum),
                  'normalization_binary64': factor,
                  'normalized_sum': float(np.sum(table.A2s_s_inv[:140])),
                  'decimal_reference_max_ulps': max_ulp,
                  'historical_manifest_entries': len(entries),
                  'native_C_executed': False, 'B_mu_selected': False}, indent=2))
PY
```

The existing smallest test cone is:

```bash
PYTHONPATH=src python -B -m pytest -p no:cacheprovider -q \
  tests/trajectory/test_hyrec_two_photon_raman.py::test_canonical_table_is_byte_locked_normalized_and_process_classified
```

The recorded run used the existing external venv named in `TARGETED_TEST.log`
because the default runtime lacked pytest. This is one fresh table test. The
v0.68 C comparison and the REC-DONOR-02C manufactured adapter results remain
historical evidence, even though their stored hashes are freshly checked.
