#!/usr/bin/env python3
"""Build the delivery-only, pre-own-ACK companion; no scientific execution."""
from pathlib import Path
import hashlib
import json
import resource
import signal
import subprocess
import time
import zipfile

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
WORKSPACE = REPO.parent
SCIENCE = "683c3f2ac3cdcc62ad6be9fe983ea39fcd74d1de"
CENTRAL = "e18b4349f2a2da3ef7caf5ec73c8787d03894620"
NAME = "REC_HD_H5_DELIVERY_COMPANION_20261025.zip"
ACK = "research/program_expansion_20261025/delivery/COMPANION_BACKUP_RECEIPT.json"
EXCLUDE_NAMES = {"text_entries.json", "COMPANION_ARCHIVE_RECEIPT.json",
                 "COMPANION_BACKUP_RECEIPT.json", NAME}
CENTRAL_INPUTS = ("DAG.current.json", "AGENTS.md", "REC-HD-ADAPTER.json",
                  "REC-H5-DEFECT-BOUND01.json", "SOURCE_RECEIPT.json", "TREE_RECURSIVE.json")
CENTRAL_PUBLICATION = (
    "research/orchestration_expansion_20261025/DAG.json",
    "research/orchestration_expansion_20261025/contracts/REC-HD-ADAPTER.json",
    "research/orchestration_expansion_20261025/contracts/REC-H5-DEFECT-BOUND01.json",
    "research/orchestration_expansion_20261025/observations/REC_HD_H5_20261025.json")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def allowed(path):
    return (path.is_file() and path.name not in EXCLUDE_NAMES
            and "__pycache__" not in path.parts and ".cache" not in path.parts
            and path.suffix not in (".pyc", ".zip") and ".zip.part" not in path.name)


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    signal.alarm(120)
    started = time.perf_counter()
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    if head != SCIENCE:
        raise ValueError("CURRENT_HEAD_DIFFERS_FROM_FROZEN_SCIENCE_S1")
    output = WORKSPACE / "deliverables" / NAME
    receipt_path = output.with_name("COMPANION_ARCHIVE_RECEIPT.json")
    if output.exists() or receipt_path.exists():
        raise FileExistsError("COMPANION_OUTPUT_OR_RECEIPT_ALREADY_EXISTS")
    paths = list(UNIT.glob("*.md")) + list(UNIT.glob("*.json"))
    paths += [p for p in (UNIT / "delivery").rglob("*") if allowed(p)]
    central = WORKSPACE / "central_update_final"
    for relative in CENTRAL_PUBLICATION:
        if not (central / relative).is_file():
            raise FileNotFoundError(relative)
    paths += [p for p in central.rglob("*") if allowed(p)]
    paths += [WORKSPACE / "central_inputs_final" / name for name in CENTRAL_INPUTS]
    payload, sources = {}, {}
    for path in sorted(set(paths)):
        name = path.relative_to(WORKSPACE).as_posix()
        if path.name == "WORK_RECORD_HD_H5.json":
            name = str(Path(name).with_name("WORK_RECORD_HD_H5_PRE_COMPANION_ACK.json"))
        data = path.read_bytes()
        if len(data) > 16 * 1024 * 1024:
            raise ValueError("UNEXPECTED_LARGE_COMPANION_PAYLOAD:" + name)
        payload[name] = data
        sources[name] = path.relative_to(WORKSPACE).as_posix()
    readme = f"""# REC HD/H5 최종 전달 동반 ZIP — 자기 ACK 직전 스냅샷

과학 source S1은 `{SCIENCE}`이며 과학 core·결과·독립 검토는 변경하지 않았다.
이 ZIP은 전달 문서·게시와 기존 백업 영수증·중앙 DAG 산출물·복구 도구를 묶는다.
원 source ZIP, PB01 S2 원 archive, 대형 binary parts는 중복 포함하지 않는다.
과학 실행이나 과학 테스트를 재수행하지 않았으며 원 과학 HOLD를 확대 승인하지 않는다.

중앙 관측은 rei_bianchi PR232, commit `{CENTRAL}`에 게시되어 있다.
이 동반 ZIP은 **자기 백업 ACK 직전**의 고정 스냅샷이다. 최종 ACK는 이후 REC
containing commit의 `{ACK}`에 기록된다. 해당 commit이 최종 전달 identity를
제공한다. 이 ZIP 안에 자기 ACK를 넣기 위한 반복 재포장을 하지 않는다.

`rec_bianchi/research/program_expansion_20261025/WORK_RECORD_HD_H5_PRE_COMPANION_ACK.json`
은 원 WORK_RECORD의 bytes를 보존하고 보관 이름만 바꾼 **pre-own-ACK 기록**이다.
그 기록의 pending 상태는 이 스냅샷 시점에 해당하며 최종 상태는 위 후속 ACK를 따른다.

## 전체 source ZIP 복구

`rec_bianchi/research/program_expansion_20261025/delivery/full_source_restore/`
안에 `restore_source_zip.py`와 `PARTS_MANIFEST.json`이 있다. Drive에서 받은
`REC_HD_H5_FULL_SOURCE_20261025_683c3f2ac3cd.zip.part001`, `.part002`, `.part003`
세 파일을 **이 manifest·스크립트와 같은 폴더**에 놓고 해당 폴더에서 실행한다.
세 파일 모두 원 ZIP basename 뒤에 각각 `.part001`, `.part002`, `.part003`가 붙는다.

```bash
python3 restore_source_zip.py --verify-only
python3 restore_source_zip.py --output REC_HD_H5_FULL_SOURCE_20261025_683c3f2ac3cd.zip
```

Python 표준 라이브러리만 필요하다. 원본은 275,856,297 bytes이며 SHA256은
`71d0f0a44e43b211bdfabd7ac99be71077e1578814947aca09af56c6acb2fb29`이다.
스크립트는 각 part와 결합한 전체의 크기·SHA256을 검사하고 기존 출력은 덮어쓰지 않는다.
단일 ZIP 또는 각 part의 실제 원격 object identity는 `delivery/BACKUP_RECEIPT.json`을 따른다.

## 내용과 검증

`PAYLOAD_MANIFEST.json`은 각 payload의 보관 경로·원 경로·bytes·SHA256을 담는다.
Manifest 자체는 자기 hash 목록에서 제외한다. ZIP의 전체 SHA256·CRC 결과·I/O 계측은
ZIP 밖의 `COMPANION_ARCHIVE_RECEIPT.json`에 기록하며 이 파일도 재귀 포함하지 않는다.
`central_update_final/`은 실제 네 게시 파일, 생성 스크립트와 실행/검증 영수증이고,
`central_inputs_final/`은 그 게시가 사용한 고정 중앙 입력 snapshot이다.
"""
    payload["README_FIRST_KO.md"] = readme.encode()
    sources["README_FIRST_KO.md"] = "generated_by:delivery/build_companion.py"
    manifest = {"schema": "REC_HD_H5_COMPANION_PAYLOAD_MANIFEST_V1",
                "snapshot_stage": "PRE_OWN_COMPANION_ACK", "science_S1": SCIENCE,
                "central_publication_commit": CENTRAL, "future_final_ack": ACK,
                "payload_count_excluding_manifest": len(payload),
                "payloads": [{"path": n, "source_path": sources[n], "bytes": len(b),
                              "sha256": digest(b)} for n, b in sorted(payload.items())],
                "manifest_self_hash_excluded": True,
                "excluded": ["source ZIPs and raw binary parts", "cache directories and .pyc",
                             "text_entries.json duplicated publication content",
                             "own archive/receipt and later own backup ACK"],
                "new_scientific_calculations": 0, "scientific_tests_rerun": 0}
    payload["PAYLOAD_MANIFEST.json"] = encoded(manifest)
    partial = output.with_suffix(".zip.partial")
    with zipfile.ZipFile(partial, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=6)
    with zipfile.ZipFile(partial) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(payload):
            raise ValueError("COMPANION_ZIP_CRC_OR_MEMBER_SET_FAILED")
        for name, data in payload.items():
            if archive.read(name) != data:
                raise ValueError("COMPANION_PAYLOAD_READBACK_FAILED:" + name)
    partial.rename(output)
    archive_bytes = output.read_bytes()
    receipt = {"schema": "REC_HD_H5_COMPANION_ARCHIVE_RECEIPT_V1",
               "archive": {"name": output.name, "path": str(output),
                           "bytes": len(archive_bytes), "sha256": digest(archive_bytes)},
               "science_S1": SCIENCE, "central_publication_commit": CENTRAL,
               "snapshot_stage": "PRE_OWN_COMPANION_ACK", "future_final_ack": ACK,
               "payload_count_excluding_manifest": len(payload) - 1,
               "zip_member_count": len(payload), "payload_manifest_sha256": digest(payload["PAYLOAD_MANIFEST.json"]),
               "verification": "PASS_EACH_PAYLOAD_BYTE_READBACK_AND_ZIP_CRC",
               "resource_cap": {"CPU_seconds": 30, "wall_seconds": 120, "address_space_bytes": 1073741824},
               "io_execution": {"process_CPU_seconds": time.process_time(),
                                "main_wall_seconds": time.perf_counter() - started,
                                "maximum_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
               "outside_measured_cost": "UNKNOWN_NOT_ZERO",
               "new_scientific_calculations": 0, "scientific_tests_rerun": 0,
               "science_core_results_review_changed": False,
               "own_ack_included": False, "own_receipt_included": False}
    receipt_path.write_bytes(encoded(receipt))
    signal.alarm(0)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
