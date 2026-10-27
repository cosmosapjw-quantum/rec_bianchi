#!/usr/bin/env python3
"""Build the authorized private portable source/input ZIP; never run science.

The source commit is an explicit parent-supplied identifier. This helper performs
no Git or cloud operation and does not infer authority from the local checkout.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import sys
import time
import zipfile

HERE=Path(__file__).resolve().parent
UNIT=HERE.parent
REPO=UNIT.parents[1]
WORKSPACE=REPO.parent
UNIT_REL=UNIT.relative_to(REPO)
DEFAULT_OUTPUT=WORKSPACE/'deliverables/REC_SYNTHESIS_20261027_SOURCE.zip'
MAX_ZIP_BYTES=95*1024*1024
FIXED_TIMESTAMP=(2026,10,27,0,0,0)
ARCHIVE_SUFFIXES=('.zip','.tar','.gz','.tgz','.bz2','.xz','.7z','.rar')
EXCLUDED_DIRS={'.git','.cache','__pycache__','mplconfig','fontcache','.fontcache',
               '.pytest_cache','.mypy_cache','.ruff_cache','.venv','venv','node_modules',
               '.aws','.ssh','.gnupg','.credentials','credentials','credential','secrets',
               'tempfixture','tempfixtures','tmp_fixture','temporary_fixture'}
EXCLUDED_FILES={'.env','.netrc','credentials','credentials.json','token.json','tokens.json',
                'id_rsa','id_ed25519'}
SNAPSHOTS=('central_DAG_12f6007a.json','central_DAG_5abe0d19.json',
           'central_DAG_ee94bef8.json','central_DAG_e18b4349.json')
CONTEXT_FILES=SNAPSHOTS+('RESTORE_RECEIPT.json','LATEST_REFS_RECOVERY.json',
    'CENTRAL_DIRECT_REFERENCE_INTAKE.json','CENTRAL_DIRECT_SOURCE_RECOVERY.json',
    'CENTRAL_INTEGRATION_SOURCE_ANALYSIS.json','PARALLEL_DELTA_5abe0d19.json',
    'CR_HEIII_GROUND_RR_20261027.json','AGENTS_central_5abe0d19.md',
    'AGENTS_central_ee94bef8.md','restore_fixed_central.py')
LOCKS=(
 ('rec_bianchi/research/rec_history_geometry_response_20261026/inputs/history.npz',35239470,
  'd4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1'),
 ('rec_bianchi/research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json',220122,
  '5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8'),
 ('rec_bianchi/research/rec_history_thermo_20261024/vendor/hydrogen.c',37471,
  '421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b'),
 ('survey_literature/lamda_hd_live.dat',2289,
  '0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'))


def canonical(value):
    return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exclusion(path):
    if any(part.lower() in EXCLUDED_DIRS for part in path.parts):
        return 'CACHE_TEMP_OR_CREDENTIAL_DIRECTORY'
    if path.name.lower() in EXCLUDED_FILES:
        return 'CREDENTIAL_FILE'
    if path.name.lower().endswith(ARCHIVE_SUFFIXES):
        return 'RECURSIVE_ARCHIVE'
    if path.suffix.lower() in ('.pyc','.pyo'):
        return 'PYTHON_CACHE'
    if path.is_symlink():
        return 'SYMLINK_NOT_DEREFERENCED'
    return None


def collect():
    members={};excluded=[]
    def add(path,arcname):
        reason=exclusion(path)
        if reason:
            excluded.append(dict(path=arcname,reason=reason));return
        if not path.is_file():
            raise ValueError('REQUIRED_FILE_MISSING:'+str(path))
        if arcname in members:
            raise ValueError('DUPLICATE_MEMBER:'+arcname)
        members[arcname]=path
    for relative in (UNIT_REL,Path('research/rec_history_geometry_response_20261026'),
                     Path('research/program_expansion_20261025')):
        root=REPO/relative
        if not root.is_dir():
            raise ValueError('REQUIRED_TREE_MISSING:'+str(root))
        for directory,dirs,files in os.walk(root,followlinks=False):
            directory=Path(directory)
            for name in sorted(dirs[:]):
                child=directory/name
                reason=exclusion(child)
                if reason:
                    dirs.remove(name)
                    excluded.append(dict(path='rec_bianchi/'+child.relative_to(REPO).as_posix(),reason=reason))
            for name in sorted(files):
                path=directory/name
                add(path,'rec_bianchi/'+path.relative_to(REPO).as_posix())
    for relative in ('research/rec_history_thermo_20261024/vendor/hydrogen.c',
                     'README.md','LICENSE','pyproject.toml','requirements.txt','requirements-dev.txt'):
        add(REPO/relative,'rec_bianchi/'+relative)
    add(WORKSPACE/'survey_literature/lamda_hd_live.dat','survey_literature/lamda_hd_live.dat')
    for name in CONTEXT_FILES:
        path=WORKSPACE/'survey_repo'/name
        if path.exists() or name in SNAPSHOTS:
            add(path,'source_context/survey_repo/'+name)
    return members,sorted(excluded,key=lambda x:x['path'])


def restore_readme(source_head):
    return f'''# REC source synthesis: 휴대용 소스·입력 복원

이 ZIP은 부모가 명시한 C10 소스 커밋 `{source_head}`에 대응하는 작업 자료입니다.
이 문자열은 부모가 제공한 출처 식별자이며, helper는 로컬 HEAD를 추론하거나 Git
원격 상태를 검증하지 않았습니다. SOURCE_MANIFEST.json은 실제 포장한 파일의
바이트 수와 SHA256을 기록합니다. Git 미러나 원격 커밋 객체를 대신하지 않습니다.

## 복원 구조

빈 디렉터리에 ZIP을 풀면 `rec_bianchi/`, `survey_literature/`,
`source_context/`가 같은 위치에 생깁니다. `rec_bianchi/` 아래의 상대경로는
원래 저장소 경로를 보존합니다. new unit 전체, GEO01 전체와 원본 history.npz,
program_expansion_20261025 전체의 과거 HD/H5 소스·결과·예산·실패·수리 이력,
native hydrogen.c를 포함합니다. source_context는 명시적으로 고른 중앙 DAG와
복원·병렬 변경 자료입니다. 무관한 저장소나 개인 계정 목록은 수집하지 않습니다.

`survey_literature/lamda_hd_live.dat`는 2289바이트 원본이며 private backup에만
포함했습니다. 이를 공개 Git에 새 원시 데이터 미러로 업로드하지 마십시오.
재귀 ZIP/tar/gz, Git 메타데이터, 캐시, 임시 fixture, 자격증명 경로는 제외합니다.
NPZ 과학 입력은 제외하지 않습니다. 구체적인 제외 목록은 manifest에 있습니다.

## 무계산 검증과 실행 경계

우선 ZIP CRC 및 manifest의 모든 payload 바이트 수·SHA256을 검증하십시오.
manifest 자신의 SHA256은 ZIP 바깥 packaging receipt에 있습니다. 모든 ZIP 멤버는
작성 후 다시 읽어 CRC/바이트 수/SHA256을 검사했습니다. receipt는 ZIP 바깥에
저장되며 자기 자신이나 나중의 cloud ACK를 ZIP에 재귀적으로 포함하지 않습니다.

이미 저장된 `results/`, `figures/`, `review/`, `stages/`와 receipt를 먼저 읽으십시오.
이 포장은 과학 계산을 실행하지 않았고 기존 결과를 재인증하지 않습니다.
과거의 실패·부분 비용·수리 기록을 보존했습니다. 물리 epsilon은 null,
H5 물리 증명 coverage는 0/313이며 원래 물리 admission 기준은 그대로입니다.

과거 frozen command에는 `/workspace/scratch/6104ad84b826/...`의 절대경로와
특정 Python 인터프리터가 남아 있습니다. 다른 컴퓨터에서는 새 복원 경로와
현지 Python으로 경로를 명시적으로 재결합해야 합니다. 원래 freeze/receipt를
덮어쓰지 말고 새 실행 기록에 원래 경로와 새 경로, 동일 입력 SHA256,
변경한 실행 환경을 함께 기록하십시오. 경로 재결합은 과학식·입력·허용오차·
물리 claim을 바꾸는 허가가 아닙니다. 이미 성공한 suite를 포장 확인 목적으로
재실행하지 마십시오. 새 과학 실행에는 부모가 정한 별도 범위와 자원 승인이 필요합니다.

기본 Python 요구사항은 `rec_bianchi/pyproject.toml`과 requirements 파일을 참고하고,
실제 검증 당시 버전·1 thread·2 GiB 제한·CPU/wall 비용은 각 freeze와 receipt를
확인하십시오. 이 helper는 패키지 설치, native 빌드, IVP/RHS/과거 primary 실행을
하지 않습니다. 아직 측정되지 않은 I/O 비용은 UNKNOWN_NOT_ZERO입니다.
'''.encode()


def zipinfo(name):
    item=zipfile.ZipInfo(name,FIXED_TIMESTAMP)
    item.create_system=3
    item.external_attr=0o100644<<16
    item.compress_type=zipfile.ZIP_DEFLATED
    return item


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-head',required=True,help='Exact 40-hex final C10 source commit supplied by parent')
    parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    if not re.fullmatch('[0-9a-fA-F]{40}',args.source_head):
        parser.error('--source-head must be an exact 40-hex commit identifier')
    head=args.source_head.lower();output=args.output.resolve()
    if not re.fullmatch('[A-Za-z0-9_.-]+',output.name) or output.suffix.lower()!='.zip':
        parser.error('--output must have a Markdown-safe .zip filename')
    output.parent.mkdir(parents=True,exist_ok=True)
    receipt_path=output.with_suffix('.packaging.receipt.json')
    partial=output.with_name(output.stem+'.building.zip')
    if output.exists() or partial.exists() or receipt_path.exists():
        parser.error('Output/partial/receipt already exists; preserve earlier attempt and choose a new filename')
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    wall=time.monotonic();usage=resource.getrusage(resource.RUSAGE_SELF)
    receipt=dict(schema='REC_PORTABLE_SOURCE_PACKAGING_V1',source_head=head,
                 source_head_origin='EXPLICIT_PARENT_ARGUMENT_NOT_LOCAL_HEAD',
                 command=[sys.executable,str(Path(__file__).resolve()),*sys.argv[1:]],
                 start_utc=start,output=str(output),status='ERROR',scientific_execution=False,
                 premeasurement_and_postmeasurement_io_cost='UNKNOWN_NOT_ZERO')
    try:
        members,excluded=collect()
        expected_stages={'rec_bianchi/'+(UNIT_REL/'stages'/f'{track}{number}.json').as_posix()
                         for track in ('R','C') for number in range(1,11)}
        missing=sorted(expected_stages-members.keys())
        if missing:
            raise ValueError('FINAL_TWENTY_STAGE_FILES_MISSING:'+','.join(missing))
        for name in ('ROOT_DECISION.json','review/CODE_DECISION.json','review/THEORY_DECISION.json'):
            member='rec_bianchi/'+(UNIT_REL/name).as_posix()
            if member not in members:
                raise ValueError('FINAL_ADMISSION_ARTIFACT_MISSING:'+member)
        metadata={}
        for name,path in sorted(members.items()):
            data=path.read_bytes();metadata[name]=dict(bytes=len(data),sha256=sha(data))
        for name,size,digest in LOCKS:
            if metadata.get(name)!={'bytes':size,'sha256':digest}:
                raise ValueError('IMMUTABLE_SCIENTIFIC_INPUT_MISMATCH:'+name)
        generated={'RESTORE_README_KO.md':restore_readme(head)}
        for name,data in generated.items():
            metadata[name]=dict(bytes=len(data),sha256=sha(data))
        manifest=dict(schema='REC_PORTABLE_SOURCE_MANIFEST_V1',source_head=head,
            source_head_origin='EXPLICIT_PARENT_ARGUMENT_NOT_LOCAL_HEAD',
            source_head_verification='40_HEX_SYNTAX_ONLY; actual payload identities below',
            scientific_execution=False,zip_timestamp=list(FIXED_TIMESTAMP),
            scope=['complete current new unit','complete reused GEO01 unit',
                   'complete program_expansion_20261025','native hydrogen.c',
                   'private original LAMDA input','curated central source context','repository metadata'],
            members=metadata,excluded=excluded,
            manifest_self_identity='SHA256 and bytes recorded in external packaging receipt; self-hash excluded to avoid recursion',
            member_count_excluding_manifest=len(metadata),physical_epsilon=None,
            physical_bound_coverage='0/313',historical_costs_and_repairs='PRESERVED')
        manifest_data=canonical(manifest);generated['SOURCE_MANIFEST.json']=manifest_data
        expected=dict(metadata)
        expected['SOURCE_MANIFEST.json']=dict(bytes=len(manifest_data),sha256=sha(manifest_data))
        with zipfile.ZipFile(partial,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
            for name in sorted(expected):
                data=generated[name] if name in generated else members[name].read_bytes()
                if len(data)!=expected[name]['bytes'] or sha(data)!=expected[name]['sha256']:
                    raise ValueError('SOURCE_CHANGED_DURING_PACKAGING:'+name)
                archive.writestr(zipinfo(name),data,compresslevel=6)
        actual_size=partial.stat().st_size
        receipt.update(zip_bytes=actual_size,size_cap_bytes=MAX_ZIP_BYTES,member_count=len(expected),
                       uncompressed_bytes=sum(item['bytes'] for item in expected.values()),
                       manifest_identity=expected['SOURCE_MANIFEST.json'])
        if actual_size>=MAX_ZIP_BYTES:
            receipt['options']=['Ask parent to authorize larger transport','Ask parent for explicit split-volume packaging preserving every input']
            raise ValueError('ZIP_NOT_BELOW_95_MIB; no input omitted; complete partial archive preserved')
        with zipfile.ZipFile(partial) as archive:
            names=archive.namelist()
            if len(names)!=len(set(names)) or sorted(names)!=sorted(expected):
                raise ValueError('ZIP_MEMBER_SET_MISMATCH')
            for name in names:
                data=archive.read(name)  # zipfile checks each member CRC while reading.
                if len(data)!=expected[name]['bytes'] or sha(data)!=expected[name]['sha256']:
                    raise ValueError('ZIP_READBACK_BYTE_IDENTITY_FAILURE:'+name)
        receipt.update(all_members_crc_readback='PASS',all_members_byte_identity='PASS',
                       zip_sha256=sha(partial.read_bytes()))
        partial.rename(output)
        receipt['status']='PASS'
    except Exception as exc:
        receipt.update(error=repr(exc),partial_archive=str(partial) if partial.exists() else None)
    finally:
        end_usage=resource.getrusage(resource.RUSAGE_SELF)
        receipt.update(end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       wall_s=time.monotonic()-wall,
                       packaging_cpu_s=(end_usage.ru_utime+end_usage.ru_stime)-(usage.ru_utime+usage.ru_stime),
                       packaging_max_rss_kib=end_usage.ru_maxrss)
        receipt_path.write_bytes(canonical(receipt))
        print(json.dumps(receipt,sort_keys=True))
    if receipt['status']!='PASS':
        raise SystemExit(1)


if __name__=='__main__':
    main()
