from __future__ import annotations

from pathlib import Path
import importlib.util
import os

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/scientific_test_runner.py"


def load_module():
    spec = importlib.util.spec_from_file_location("scientific_test_runner", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_slow_collection_is_deduplicated_by_file_without_losing_nodes() -> None:
    module = load_module()
    text = "\n".join(
        [
            "tests/a.py::test_one",
            "tests/a.py::test_two",
            "tests/b.py::test_three[param]",
            "3/9 tests collected (6 deselected)",
        ]
    )
    files, nodes = module.parse_slow_collection(text)
    assert nodes == [
        "tests/a.py::test_one",
        "tests/a.py::test_two",
        "tests/b.py::test_three[param]",
    ]
    assert files == ["tests/a.py", "tests/b.py"]


def test_scientific_environment_disables_external_pytest_plugins_and_blas_threads() -> None:
    module = load_module()
    env = module.scientific_environment({"PATH": os.environ.get("PATH", "")})
    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    for name in (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "BLIS_NUM_THREADS",
    ):
        assert env[name] == "1"


def test_scientific_fingerprint_tracks_computational_inputs_not_receipts(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "src").mkdir()
    (tmp_path / "src/model.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "tests/recoil").mkdir(parents=True)
    (tmp_path / "tests/recoil/test_model.py").write_text(
        "def test_value(): assert True\n", encoding="utf-8"
    )
    (tmp_path / "state/scientific_test_receipts").mkdir(parents=True)
    receipt = tmp_path / "state/scientific_test_receipts/example.json"
    receipt.write_text('{"status":"PASS"}\n', encoding="utf-8")

    before = module.scientific_input_fingerprint(tmp_path)
    receipt.write_text('{"status":"CHANGED"}\n', encoding="utf-8")
    assert module.scientific_input_fingerprint(tmp_path) == before

    (tmp_path / "src/model.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert module.scientific_input_fingerprint(tmp_path) != before


def test_scientific_receipt_is_valid_only_for_matching_fingerprint_and_nodes(
    tmp_path: Path,
) -> None:
    module = load_module()
    test_file = "tests/recoil/test_model.py"
    nodes = [f"{test_file}::test_one", f"{test_file}::test_two"]
    module.write_scientific_receipt(
        root=tmp_path,
        test_file=test_file,
        nodes=nodes,
        fingerprint="fingerprint-A",
        elapsed_seconds=1.25,
    )
    assert module.valid_scientific_receipt(
        root=tmp_path,
        test_file=test_file,
        nodes=nodes,
        fingerprint="fingerprint-A",
    )
    assert not module.valid_scientific_receipt(
        root=tmp_path,
        test_file=test_file,
        nodes=nodes,
        fingerprint="fingerprint-B",
    )
    assert not module.valid_scientific_receipt(
        root=tmp_path,
        test_file=test_file,
        nodes=nodes + [f"{test_file}::test_three"],
        fingerprint="fingerprint-A",
    )


def test_scientific_receipts_are_runtime_cache_not_tracked_state(tmp_path: Path) -> None:
    module = load_module()
    test_file = "tests/recoil/test_model.py"
    path = module.write_scientific_receipt(
        root=tmp_path,
        test_file=test_file,
        nodes=[f"{test_file}::test_one"],
        fingerprint="fingerprint-A",
        elapsed_seconds=0.1,
        output="1 passed\n",
    )
    assert path.is_relative_to(tmp_path / ".cache/scientific_test_receipts")
    assert not (tmp_path / "state/scientific_test_receipts").exists()


def test_scientific_fingerprint_tracks_the_runner_contract(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "src").mkdir()
    (tmp_path / "src/model.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    runner = tmp_path / "scripts/scientific_test_runner.py"
    runner.write_text("POLICY = 1\n", encoding="utf-8")
    before = module.scientific_input_fingerprint(tmp_path)
    runner.write_text("POLICY = 2\n", encoding="utf-8")
    assert module.scientific_input_fingerprint(tmp_path) != before
