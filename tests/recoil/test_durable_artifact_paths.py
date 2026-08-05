from pathlib import Path

from full_bianchi_hyrec.recoil import recoil_bridge


def test_recoil_bridge_defaults_are_repository_relative_and_present():
    module_path = Path(recoil_bridge.__file__).resolve()
    repository_root = module_path.parents[3]

    for path in (recoil_bridge._DEFAULT_V032, recoil_bridge._DEFAULT_V033):
        assert path.is_file()
        relative = path.relative_to(repository_root)
        assert relative.parts[:2] == ("archive", "expanded")

    source = module_path.read_text(encoding="utf-8")
    assert '"/mnt/data/Full_Bianchi_HyRec_' not in source
