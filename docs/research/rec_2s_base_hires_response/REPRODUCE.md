# Restore exact executed sources

The ZIP contains a self-contained Git bundle with all ancestors, including the pinned input ZIP.
The bundle needs no network or prerequisite repository. SHA256SUMS excludes itself.

```bash
sha256sum -c SHA256SUMS
git clone -b research/rec-2s-base-hires-response-20260905 rec_2s_response.bundle restored
cd restored
git checkout --detach e6506c2434a9063d4e4a0a6a26c06aef7832ce52
```

Numerical replay (optional recipient action; not repeated during packaging): choose a new output
path outside the clone. Use the recorded existing environment; no installer is part of this delivery.

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/rec-response-mpl OPENBLAS_NUM_THREADS=1 /home/cosmosapjw/cosmo_lab/.venv/bin/python docs/research/rec_2s_base_hires_response/check_response.py --output /tmp/rec-response-new-output
```

The exact original argv, external cache directories and exit codes are in execution/COMMANDS.jsonl.
The repaired Wolfram script belongs to commit 27cccfc94196583363a956ddf37bafce57873639.
The Python checker/CASES/test blobs are unchanged in that child. Its actual invocation is separately
recorded; do not label that child as a second numerical run. The final result commit/tree are in
RETURN_IDENTITY.json outside the bundle to avoid circular self-identification.
