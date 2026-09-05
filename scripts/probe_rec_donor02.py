"""Exact dyadic oracle, hostile formula mutants, hashes and SVG evidence.

These manufactured probes do not integrate a trajectory or admit source data.
The SVG is generated with the Python standard library. Rendered visual review
is separate from its numerical-coordinate audit and is not asserted here.
"""
from __future__ import annotations
import csv
from fractions import Fraction as Q
import hashlib
from html import escape
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("donor02_probe_fixture",
    ROOT / "tests/trajectory/test_rec_donor01_typed_physical_source_red.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
case = fixture.TestRecDonor01TypedPhysicalSourceRed()
m = case._module()


def hashes():
    source = case._source(m)
    return {"source": source.semantic_sha256,
            "restart_mutant": case._source(m, trajectory=case._trajectory(m, "7" * 64)).semantic_sha256,
            "payload_mutant": case._source(m, provenance=case._provenance(m, "9" * 64)).semantic_sha256}


def plot_svg(path, title, x_label, y_label, series, xlim, ylim):
    """Simple monochrome plot: labels and distinct dash patterns, no fitted data."""
    def xp(x):
        return 92 + 608 * (x-xlim[0])/(xlim[1]-xlim[0])
    def yp(y):
        return 360 - 268 * (y-ylim[0])/(ylim[1]-ylim[0])
    items = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 455" role="img">',
             '<title>' + escape(title) + '</title>',
             '<desc>Manufactured local-source diagnostic, not a cosmological evolution.</desc>',
             '<g font-family="sans-serif" font-size="16">',
             '<text x="380" y="27" text-anchor="middle">' + escape(title) + '</text>',
             '<path d="M92 92 V360 H700" fill="none" stroke="currentColor"/>']
    for i in range(5):
        x = xlim[0]+i*(xlim[1]-xlim[0])/4
        y = ylim[0]+i*(ylim[1]-ylim[0])/4
        items.extend([f'<text x="{xp(x):.3f}" y="389" text-anchor="middle">{x:g}</text>',
                      f'<text x="80" y="{yp(y)+5:.3f}" text-anchor="end">{y:g}</text>'])
    items.extend(['<text x="390" y="432" text-anchor="middle">'+escape(x_label)+'</text>',
                  '<text transform="translate(22 226) rotate(-90)" text-anchor="middle">'+escape(y_label)+'</text>'])
    for i, (name, pairs) in enumerate(series):
        dash = ('none', '8 5', '2 5')[i]
        coords = ' '.join(f'{xp(x):.6f},{yp(y):.6f}' for x,y in pairs)
        lx = 94 + i*211
        items.extend([f'<polyline points="{coords}" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="{dash}"/>',
                      f'<path d="M{lx} 63 h35" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="{dash}"/>',
                      f'<text x="{lx+43}" y="68">'+escape(name)+'</text>'])
    items.append('</g></svg>')
    path.write_text('\n'.join(items)+'\n', encoding='utf-8')


def main():
    if sys.argv[1:] == ["--hash-only"]:
        print(json.dumps(hashes(), sort_keys=True))
        return
    out = Path(sys.argv[1]).resolve()
    if out == ROOT or ROOT in out.parents:
        raise RuntimeError("OUTPUT_MUST_BE_OUTSIDE_WORKTREE")
    out.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "STOP_INVALID", "scientific_claim": "NO_PASS_REC_PHYSICAL_SPLIT",
               "rendered_visual_review": "NOT_PERFORMED", "physical_deposition_executed": False}
    try:
        head = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'], text=True).strip()
        records = []
        jerrors = []
        pairs = [(Q(1,4),Q(3,4)), (Q(3,4),Q(1,4)), (Q(1,2),Q(1,2)), (Q(0),Q(0))]
        directions = [(Q(1,8),Q(1,2),Q(-1,4)), (Q(-1,4),Q(0),Q(1,2)), (Q(0),Q(-1,2),Q(1,4))]
        for eta,kappa in pairs:
            source = case._source(m, float(eta), float(kappa))
            for i in range(9):
                f = Q(i,4)
                exact = eta*(1+f)-kappa*f
                actual = source.action(energy_j=2.25e-18, occupation=float(f))
                records.append(dict(emission_s_inv=float(eta),absorption_s_inv=float(kappa),
                                    occupation=float(f), actual_s_inv=actual, exact_s_inv=float(exact),
                                    residual_s_inv=actual-float(exact)))
                if actual != float(exact):
                    raise AssertionError("AFFINE_DYADIC_ORACLE_MISMATCH")
                for df,de,da in directions:
                    j = source.jvp(energy_j=2.25e-18, occupation=float(f),
                          d_occupation=float(df),d_emission_s_inv=float(de),d_absorption_s_inv=float(da))
                    ref = (1+f)*de-f*da-(kappa-eta)*df
                    jerrors.append(j-float(ref))
                    if j != float(ref):
                        raise AssertionError("JVP_DYADIC_ORACLE_MISMATCH")
        with (out/'affine_oracle.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
        source = case._source(m)
        energies = (math.nextafter(2e-18,0.0),2e-18,2.25e-18,
                    math.nextafter(2.5e-18,0.0),2.5e-18,math.nextafter(2.5e-18,math.inf))
        thresholds = [{"energy_j": e, "source_s_inv": source.action(energy_j=e,occupation=2.0)} for e in energies]
        if [r['source_s_inv'] for r in thresholds] != [0.0,-0.75,-0.75,-0.75,0.0,0.0]:
            raise AssertionError("ENDPOINT_POLICY_MISMATCH")
        h1 = subprocess.check_output([sys.executable,'-B',__file__,'--hash-only'],text=True).strip()
        h2 = subprocess.check_output([sys.executable,'-B',__file__,'--hash-only'],text=True).strip()
        if h1 != h2 or len(set(json.loads(h1).values())) != 3:
            raise AssertionError("SEMANTIC_HASH_PROBE_MISMATCH")
        # Fixed test fixture: keep the primal/JVP independently exact.
        mutant_rows = []
        for i in range(9):
            f = Q(i,4)
            eta,kappa,df,de,da = Q(1,4),Q(3,4),Q(1,8),Q(1,2),Q(-1,4)
            C = eta*(1+f)-kappa*f
            J = (1+f)*de-f*da-(kappa-eta)*df
            mutant_rows.append({"occupation":float(f),
                "drop_stimulated_C_residual":float((eta-kappa*f)-C),
                "flip_absorption_J_residual":float(((1+f)*de+f*da-(kappa-eta)*df)-J),
                "drop_state_J_residual":float(((1+f)*de-f*da)-J)})
        if not all(any(row[k] != 0 for row in mutant_rows) for k in tuple(mutant_rows[0])[1:]):
            raise AssertionError("HOSTILE_MUTANT_NOT_DETECTED")
        with (out/'mutant_residuals.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(mutant_rows[0]))
            writer.writeheader(); writer.writerows(mutant_rows)
        xs = [i/4 for i in range(9)]
        series = []
        for name,(eta,kappa) in zip(('damping','amplification','equal rates'),pairs[:3]):
            obj = case._source(m,float(eta),float(kappa))
            series.append((name,[(f,obj.action(energy_j=2.25e-18,occupation=f)) for f in xs]))
        plot_svg(out/'affine_source.svg', 'Local affine source: manufactured coefficients',
                 'Occupation f (dimensionless)', 'C[f] (s^-1)', series, (0,2), (-1,2))
        keys = tuple(mutant_rows[0])[1:]
        plot_svg(out/'mutant_residuals.svg', 'Formula mutations against exact rational oracles',
                 'Occupation f (dimensionless)', 'Signed residual (s^-1)',
                 [(name,[(r['occupation'],r[k]) for r in mutant_rows])
                  for name,k in zip(('drop stimulated','flip J sign','drop state J'),keys)],
                 (0,2),(-1,0.25))
        receipt.update(status='PASS_BOUNDED_MANUFACTURED_ORACLES_NOT_SOURCE_ADMISSION',
            head=head, action_cases=len(records), jvp_cases=len(jerrors),
            max_action_residual=max(abs(r['residual_s_inv']) for r in records),
            max_jvp_residual=max(abs(v) for v in jerrors),
            threshold_records=thresholds, fresh_process_hashes=json.loads(h1),
            hashes_identical_in_two_fresh_processes=True, detected_mutants=list(keys),
            figure_files=['affine_source.svg','mutant_residuals.svg'],
            source_blob=subprocess.check_output(['git','-C',str(ROOT),'rev-parse',
                        'HEAD:src/full_bianchi_hyrec/physical_source_authority.py'],text=True).strip(),
            probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    finally:
        (out/'NUMERICAL_PROBE.json').write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        (out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
            for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS'),encoding='utf-8')
        print(json.dumps(receipt,sort_keys=True,allow_nan=False))

if __name__ == '__main__':
    main()
