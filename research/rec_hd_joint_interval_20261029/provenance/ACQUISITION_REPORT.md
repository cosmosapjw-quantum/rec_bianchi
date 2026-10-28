# HD source acquisition — 2026-10-29 KST

Result: **PARTIAL_LAMDA_RESTORED_CDMS_BYTES_BLOCKED**. rec_bianchi PR153 HEAD `67d8baa092f18b7c1bbf8dfe9e255f8b43b45998` is the starting identity. Canonical DAG remains 28/88; physical coverage remains 0/313; original 35 Hz FAIL7/8 and production HOLD are preserved.

The current-turn Python HTTP request retrieved the official LAMDA `hd.dat` with HTTP200. Its 2,289 bytes have SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`, matching the previously pinned source. The response gives `Last-Modified: Mon, 07 Jun 2021 07:42:30 GMT` and ETag `"8f1-5c4282f08d068"`. This restores the original source for reproducible work on this host; it does not add new physical coverage.

Seven official CDMS HTTP requests (directory plus c003501.cat, c003501.egy, HD.par, HD.fit, HD.lin, c003501i.cat) each returned HTTP503. Independent Exa raw-file extraction returned CRAWL_UNKNOWN_ERROR for six files; web-open fallback reported inaccessible for .lit/.egy/.fit. No CDMS original file bytes were obtained and no version authenticity is inferred from extracted text.

Exa successfully extracted the official archived directory and the official LAMDA HD page. The directory lists 2011-12-07 for HD.fit/.par/.lin/.egy/c003501i.cat and 2019-02-25 for c003501.cat. These dates preserve the ambiguity of the current .cat. The LAMDA page attributes spectroscopy to CDMS version 2 of December 2011 and collision data to Flower (1999), including DeltaJ1 and J2-0. The actual conversion recipe is still unresolved.

SciSpace search was executed with a complete question on HD version-2 spectroscopy and LAMDA lineage. Results are retained as discovery metadata. None authenticates the missing original files or supplies an adopted conversion script. Exa search returned five results; search/fetch response text is retained separately from raw HTTP source bytes.

An additional source-description discrepancy is retained without physical adoption: the official HD webpage describes coverage "up to v=1 (~3100 cm^-1)", while the actual nine-row file labels levels J=0..8 and lists energies up to 3089.576092837 cm^-1. The page wording alone must not supply an extra vibrational manifold to the solver.

The minimum next step is to acquire the listed CDMS v2 originals in a working official HTTP environment, keep response headers and hashes, map quantum-number rows and measured/predicted tags by version, then recover or reconstruct the exact LAMDA conversion lineage from those bytes. Do not substitute the updated 2026 v3 fit, relax 35 Hz, change rates, or run historical native/IVP campaigns to address this input-access failure.

Files: `HTTP_ATTEMPTS.json`, `hd.dat`, optional `LAMDA_HD.html`, `SEARCH_TOOL_RESPONSES.txt`, `EXA_RAWFILE_ATTEMPT.json`, `WEB_FALLBACK.json`, and `ACQUISITION_REPORT.json`. The JSON records precise URLs and failure classes. No repository or provider mutation was performed.

A bounded official-source alternate-host search returned only the cdms.astro.uni-koeln.de archive and current v3 directory. No exact alternate-host archive URL was observed, so no guessed alias was fetched. Conversion attribution is confirmed; generator script, conversion author and field-level derivation remain unresolved.
