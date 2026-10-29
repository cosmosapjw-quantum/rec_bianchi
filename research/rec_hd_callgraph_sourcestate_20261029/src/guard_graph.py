"""Read-only, source-pinned, *scoped* HD guard/callsite audit.

This is a research analyser, not a production/source-policy switcher. It does not
read, replicate or replace LAMDA/CDMS private input, and cannot certify dynamic
callers or an entire multi-repository native control-flow graph.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from hashlib import sha1, sha256
from pathlib import Path
from typing import Any


class SourceMismatch(ValueError):
    """The target source file is not the locked Git blob."""


class UnsupportedControlFlow(ValueError):
    """The static intraprocedural proof cannot discharge a control-flow obligation."""


def git_blob_id(data: bytes) -> str:
    return sha1(f"blob {len(data)}\0".encode('ascii') + data).hexdigest()


def read_pinned_py(path: str | Path, expected_blob: str) -> ast.Module:
    raw = Path(path).read_bytes()
    got = git_blob_id(raw)
    if got != expected_blob:
        raise SourceMismatch(f"blob mismatch for {Path(path).name}: {got}")
    return ast.parse(raw.decode('utf-8'), filename=str(path))


def call_target(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return call_target(node.value) + '.' + node.attr
    return '<dynamic>'


def calls(node: ast.AST) -> tuple[str, ...]:
    return tuple(call_target(v.func) for v in ast.walk(node) if isinstance(v, ast.Call))


def body_for(mod: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    matches = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    if len(matches) != 1:
        raise ValueError(f"expected one module-level function {name!r}, found {len(matches)}")
    return matches[0]


@dataclass(frozen=True)
class StaticOrder:
    entry: str
    required_call: str
    consumer_call: str
    order: str
    guard_line: int | None
    consumer_line: int | None
    strength: str


def ordered_straightline_calls(function: ast.FunctionDef | ast.AsyncFunctionDef,
                               guard: str, consumer: str) -> StaticOrder:
    """Conservative source-level ordering for a *straight-line* function body.

    Static proof is intentionally refused if a function contains branching,
    exception handling, loops, with-contexts, awaits/yields, returns ahead of
    the consumer, or nested calls that obscure sequence ordering. The oracle
    checks *necessary entry ordering*, not success of any callee's scientific gate.
    """
    paths: list[tuple[int,str]] = []
    early_return = False
    for s in function.body:
        if isinstance(s, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try,
                          ast.With, ast.AsyncWith, ast.Match, ast.TryStar)):
            raise UnsupportedControlFlow(f"{function.name}: non-linear statement on line {s.lineno}")
        if isinstance(s, (ast.Return, ast.Raise)):
            if not paths or not any(name == consumer for _, name in paths):
                early_return = True
        if isinstance(s, (ast.Assign, ast.AnnAssign, ast.Expr, ast.Return, ast.Raise)):
            cs = calls(s)
            if len(cs) > 1 and (guard in cs or consumer in cs):
                raise UnsupportedControlFlow(f"{function.name}: nested same-statement calls on line {s.lineno}")
            paths.extend((s.lineno, c) for c in cs)
        else:
            raise UnsupportedControlFlow(f"{function.name}: unsupported statement {type(s).__name__}")
    gs = [line for line,name in paths if name == guard]
    cs = [line for line,name in paths if name == consumer]
    if not cs:
        return StaticOrder(function.name,guard,consumer,'NO_CONSUMER',min(gs) if gs else None,None,'STATIC_SCOPED')
    if early_return:
        raise UnsupportedControlFlow(f"{function.name}: return/raise before consumer")
    if len(gs) == 1 and len(cs) == 1 and gs[0] < cs[0]:
        return StaticOrder(function.name,guard,consumer,'GUARD_PRECEDES_CONSUMER',gs[0],cs[0],'STATIC_ORDER_ONLY')
    if not gs:
        return StaticOrder(function.name,guard,consumer,'DIRECT_NO_GUARD_IN_FUNCTION',None,min(cs),'STATIC_SCOPED')
    return StaticOrder(function.name,guard,consumer,'NOT_PROVEN',min(gs),min(cs),'STATIC_SCOPED')


def stage_guard_evidence(mod: ast.Module) -> dict[str, Any]:
    """Extract *actual pinned firewall file* call order, never imply universal coverage."""
    wrapped = body_for(mod,'guarded_line_coefficients')
    order = ordered_straightline_calls(wrapped,'strict_bridge','module.line_coefficients')
    strict = body_for(mod,'strict_bridge')
    core = body_for(mod,'_strict_bridge_core')
    source_call = 'validate_pinned_raw_bytes' in calls(strict)
    core_call = '_strict_bridge_core' in calls(strict)
    owner_gate = 'module.require_energy_frequency_bridge' in calls(core)
    q_call = 'module.transition_qualification' in calls(core)
    return {'wrapper_order':order.__dict__,
            'strict_bridge_calls_source_validator':source_call,
            'strict_bridge_calls_core':core_call,
            'core_calls_owner_energy_gate':owner_gate,
            'core_calls_owner_transition_qualification':q_call,
            'guarded_research_entry_static_sequence':bool(order.order=='GUARD_PRECEDES_CONSUMER' and
                                                           source_call and core_call and owner_gate and q_call),
            'runtime_owner_private_source': 'NOT_RUN',
            'other_callers_covered':False}


def reachable_without_cuts(graph: dict[str, tuple[str,...]],
                           roots: set[str], consumers: set[str], cuts: set[str]) -> list[list[str]]:
    """Enumerate shortest rooted unguarded witnesses in finite graph.

    A non-empty result CERTIFIES a bypass path in *this declared graph*.
    An empty result does not certify unmodelled dynamic/FFI callers.
    """
    from collections import deque
    witnesses=[]
    for root in sorted(roots):
        if root in cuts:
            continue
        q=deque([(root, (root,))])
        seen={root}
        while q:
            u,path=q.popleft()
            if u in consumers:
                witnesses.append(list(path))
                break
            for v in graph.get(u,()):
                if v not in seen and v not in cuts:
                    seen.add(v)
                    q.append((v,path+(v,)))
    return witnesses


def all_observed_paths_guarded(graph:dict[str,tuple[str,...]],
                               roots:set[str],consumers:set[str],cuts:set[str]) -> bool:
    return not reachable_without_cuts(graph,roots,consumers,cuts)


def validate_source_state(module: Any, data: Any, *, expected_module_blob: str,
                          expected_source_sha256: str, expected_source_bytes: int) -> dict[str, Any]:
    """Opt-in scientific strengthening: bind parsed object to exact pinned raw bytes.

    A SHA label plus even authenticated source_roundtrip() is *not enough* to
    guarantee parsed field values if a frozen dataclass is later reconstructed.
    Reparse authenticated raw bytes with the owner's pinned parser, compare all
    dataclass fields, and fail closed. This is not a live production interface.
    No write or mutation of the owner object is performed.
    """
    p=Path(getattr(module,'__file__',''))
    if not p.is_file() or git_blob_id(p.read_bytes()) != expected_module_blob:
        raise SourceMismatch('pinned owner module blob is unavailable or changed')
    if type(data) is not getattr(module,'HDDataset',None):
        raise SourceMismatch('dataset must be the exact owner HDDataset class')
    if not hasattr(data,'source_roundtrip'):
        raise SourceMismatch('source_roundtrip unavailable')
    raw=data.source_roundtrip()
    if (type(raw) is not bytes or len(raw)!=expected_source_bytes or
            sha256(raw).hexdigest()!=expected_source_sha256):
        raise SourceMismatch('real raw source bytes do not match pin')
    if (getattr(data,'source_sha256',None)!=expected_source_sha256 or
            getattr(data,'source_bytes',None)!=expected_source_bytes):
        raise SourceMismatch('dataset identity metadata mismatch')
    canonical=module.parse_hd(raw)
    if type(canonical) is not type(data) or canonical != data:
        raise SourceMismatch('parsed dataset differs from immutable raw-source canonical parse')
    return {'status':'PASS_SOURCE_STATE_CLOSURE',
            'raw_bytes':len(raw),'source_sha256':expected_source_sha256,
            'owner_blob_sha1':expected_module_blob,
            'scope':'SOURCE_STATE_ONLY_NOT_PHYSICAL_ADMISSION'}
