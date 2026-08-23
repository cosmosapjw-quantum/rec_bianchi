from __future__ import annotations

import ast
import json
from pathlib import Path
import re


ROOT = Path("/home/cosmosapjw/Dropbox/bianchi/rec_bianchi")
SEED = Path("/tmp/rec_bianchi_independent_numerical_research.md")
src_files = sorted((ROOT / "src/full_bianchi_hyrec").rglob("*.py"))
test_files = sorted((ROOT / "tests").rglob("*.py"))
definition_terms = re.compile(
    r"(solve|solver|residual|event|history|restart|commit|accept|step|jvp|jacob|state|result|context)",
    re.I,
)
call_terms = re.compile(r"(solve|gmres|root|commit|accept|append|lstsq|inv$)", re.I)
test_terms = re.compile(
    r"(nonfinite|nan|inf|residual|invariant|conserv|restart|rollback|reject|event|fail|raise|jvp|jacob)",
    re.I,
)

definitions = []
classes = []
calls = []
for path in src_files:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rel = str(path.relative_to(ROOT))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and definition_terms.search(node.name):
            definitions.append((rel, node.lineno, node.name))
        elif isinstance(node, ast.ClassDef) and definition_terms.search(node.name):
            classes.append((rel, node.lineno, node.name))
        elif isinstance(node, ast.Call):
            target = node.func
            name = target.id if isinstance(target, ast.Name) else target.attr if isinstance(target, ast.Attribute) else ""
            if call_terms.search(name):
                calls.append((rel, node.lineno, name))

test_hits = []
for path in test_files:
    rel = str(path.relative_to(ROOT))
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if test_terms.search(line):
            test_hits.append((rel, line_no))

seed_text = SEED.read_text(encoding="utf-8")
remedies = sorted(set(re.findall(r"(?m)^\| (R\d{2}) \|", seed_text)))
hypotheses = sorted(set(re.findall(r"(?m)^- (N\d) ", seed_text)))

print(json.dumps({
    "source_python_files": len(src_files),
    "test_python_files": len(test_files),
    "relevant_definitions": len(definitions),
    "relevant_classes": len(classes),
    "numeric_or_commit_calls": len(calls),
    "test_term_hits": len(test_hits),
    "seed_remedies": remedies,
    "seed_remedy_count": len(remedies),
    "seed_hypotheses": hypotheses,
    "seed_hypothesis_count": len(hypotheses),
}, sort_keys=True))
