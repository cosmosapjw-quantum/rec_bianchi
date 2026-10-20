/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 cosmosapjw-quantum
 */
#ifndef REC_STREAM_AUDIT_H
#define REC_STREAM_AUDIT_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define REC_PREFIX_ROWS_PER_COLUMN ((size_t)314)
#define REC_PREFIX_MAX_COLUMNS ((size_t)64)
#define REC_PREFIX_MAX_ROWS ((size_t)20096)
#define REC_PREFIX_MAX_TEXT_BYTES ((size_t)4194304)
#define REC_PREFIX_NO_ROW SIZE_MAX

enum RecCode {
    REC_OK = 0,
    REC_ERR_NULL = 1,
    REC_ERR_LENGTH = 2,
    REC_ERR_LIMIT = 3,
    REC_ERR_ALIGNMENT = 4,
    REC_ERR_OVERLAP = 5,
    REC_ERR_FIELDS = 10,
    REC_ERR_INTEGER = 11,
    REC_ERR_ORDER = 12,
    REC_ERR_FLOAT = 13,
    REC_ERR_NATIVE_NONFINITE = 14,
    REC_ERR_PY_NONFINITE = 15,
    REC_ERR_TR = 16,
    REC_ERR_ENERGY = 17,
    REC_ERR_TOLERANCE = 18,
    REC_ERR_PARITY = 19,
    REC_ERR_ROWS = 20,
    REC_ERR_UTF8 = 21,
    REC_ERR_BLACKBODY = 22,
    REC_ERR_FBB = 30,
    REC_ERR_RATIO = 31,
    REC_ERR_PANIC = 90
};

/* Argument identifiers used in detail for codes 1..5. */
enum RecArgument {
    REC_ARG_HANDLE = 1,
    REC_ARG_TEXT = 2,
    REC_ARG_COLUMNS = 3,
    REC_ARG_START_COL = 4,
    REC_ARG_PY = 5,
    REC_ARG_TR = 6,
    REC_ARG_ENERGIES = 7,
    REC_ARG_NATIVE = 8,
    REC_ARG_STATUS = 9,
    REC_ARG_N = 10,
    REC_ARG_FBB = 11,
    REC_ARG_C = 12,
    REC_ARG_RATIO_OUT = 13
};

typedef struct RecStatus {
    int32_t code;
    size_t row;             /* Zero-based within this block; SIZE_MAX if none. */
    int32_t detail;         /* See README.md for record-specific details. */
    size_t processed_rows;  /* All attempted present records, including speculation. */
} RecStatus;

/* threads must be 1..4; NULL indicates invalid count, pool failure, or panic.
 * One thread uses a direct serial loop; >1 owns a reusable local Rayon pool.
 */
void *rec_prefix_new(size_t threads);

/* NULL is a no-op. A non-NULL handle must be live, exclusively owned during
 * destruction, and freed exactly once, by this same library instance.
 */
void rec_prefix_free(void *handle);

/* Exact lengths: py_len == native_len == columns*314, tr_len == columns,
 * energies_len == 314; columns is 1..64; text_len <= MAX_TEXT_BYTES.
 * text has exactly columns*314 PV/PL records, with LF or CRLF separators;
 * the final record may omit its LF. No NUL terminator is required/read.
 * py_values and native_values are contiguous row-major [columns][314] blocks:
 * index = local_column*314 + slot.
 * Each column contains PV bins 0..310 followed by PL bins 0..2.
 * tr is precomputed by Python in the original scalar association.
 *
 * All pointers must be non-NULL, correctly aligned, and valid for the given
 * extents (including writable out and native_values). Inputs must be fully
 * initialized and immutable until return. Output arrays may be uninitialized.
 * native_values and out must not overlap any other buffer or the handle;
 * read-only input arrays may overlap each other. Do not free the handle or
 * reuse writable buffers during an in-flight call. See README.md for the
 * required default floating-point environment, panic and allocation limits.
 *
 * Return value equals out->code, except invalid out or any detected overlap
 * returns a code without writing out. Argument errors do not read input data.
 * Record errors return the earliest failing position after joining all jobs;
 * output is partial on error and the caller must discard the failed block.
 * processed_rows counts present expected-position records whose validation
 * started, including a failing record and work in later columns. Missing and
 * extra records are not counted. On panic, processed_rows is SIZE_MAX (unknown).
 */
int rec_prefix_audit(
    void *handle,
    const uint8_t *text, size_t text_len,
    size_t start_col, size_t columns,
    const double *py_values, size_t py_len,
    const double *tr, size_t tr_len,
    const double *energies, size_t energies_len,
    double *native_values, size_t native_len,
    RecStatus *out);

/* Independent per-lane ratios, NOT a parity gate:
 * out[i] = abs(py[i]-c[i]) /
 *          (1.e-7*max(abs(py[i]),abs(c[i])) + 1.e-10*fbb[i]).
 * n <= MAX_ROWS; n==0 succeeds without touching any pointer (NULL allowed).
 * For n>0, all arrays have at least n elements. Inputs are finite, fbb >= 0;
 * tolerance and ratio must be finite. Zero/zero is a ratio error. Finite ratios
 * above one are returned normally. out must not alias an input. On any error
 * discard out; no row/status is returned. Same lifetime/alignment obligations.
 * Plain independent-lane arithmetic is intended for LLVM auto-vectorization;
 * no SIMD or performance guarantee is part of this ABI.
 */
int rec_ratio_batch(size_t n, const double *py, const double *c,
                    const double *fbb, double *out);

#ifdef __cplusplus
}
#endif

#endif
