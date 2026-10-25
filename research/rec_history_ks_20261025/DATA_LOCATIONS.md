# Data and reproduction locations
The Git projection contains source code,contracts,reviews,JSON diagnostics,
source identities,stage/DAG reports and selected PNGs. Complete raw NPZ arrays,
all13endpoint snapshots,actual35MBhistory and immutable THERMO01 S2 ZIP are
delivered in the full S2 backup. Final provider IDs,size,SHA256 and restore
order are in delivery/S2_ACTUAL_RECEIPT.json and PUBLICATION_STATE.json.
Do not substitute a partial Git checkout for the full raw backup input set.
After restoring the full S2 ZIP,follow RESTORE_ORDER_KS01.md; the retained
THERMO01 ZIP must expand at inputs/thermo_s2. CLI arguments in code/README.md
make all retained paths explicit. No rerun is needed to inspect saved results.
Science S2 is immutable18/20; final S3 and compact companion record actual20/20.
No archive contains its own provider ACK; this avoids recursive re-archiving.

