/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 cosmosapjw-quantum
 * Linux x86-64 C ABI smoke test against the built cdylib.
 */
#include "rec_stream_audit.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

_Static_assert(sizeof(RecStatus) == 32, "RecStatus size");
_Static_assert(_Alignof(RecStatus) == 8, "RecStatus alignment");
_Static_assert(offsetof(RecStatus, code) == 0, "code offset");
_Static_assert(offsetof(RecStatus, row) == 8, "row offset");
_Static_assert(offsetof(RecStatus, detail) == 16, "detail offset");
_Static_assert(offsetof(RecStatus, processed_rows) == 24, "work offset");

int main(void) {
    char text[65536];
    double py[628], native[628], tr[2] = {1.0, 1.0}, energies[314];
    size_t bytes = 0;
    for (size_t bin = 0; bin < 314; ++bin) energies[bin] = 1.0;
    for (size_t row = 0; row < 628; ++row) {
        const size_t slot = row % 314;
        py[row] = (double)row * 1.0e-12;
        const int n = snprintf(text + bytes, sizeof(text) - bytes,
            "%s,%zu,%zu,%.17g\n", slot < 311 ? "PV" : "PL",
            100 + row / 314, slot < 311 ? slot : slot - 311, py[row]);
        assert(n > 0 && (size_t)n < sizeof(text) - bytes);
        bytes += (size_t)n;
    }
    assert(rec_prefix_new(0) == NULL);
    assert(rec_prefix_new(5) == NULL);
    rec_prefix_free(NULL);
    for (size_t threads = 1; threads <= 4; threads *= 2) {
        void *handle = rec_prefix_new(threads);
        assert(handle != NULL);
        RecStatus status;
        assert(rec_prefix_audit(handle, (const uint8_t *)text, bytes, 100, 2,
            py, 628, tr, 2, energies, 314, native, 628, &status) == REC_OK);
        assert(status.code == REC_OK && status.row == SIZE_MAX);
        assert(status.detail == 0 && status.processed_rows == 628);
        assert(memcmp(py, native, sizeof(py)) == 0);
        const double saved = py[2];
        py[2] = 1.0;
        assert(rec_prefix_audit(handle, (const uint8_t *)text, bytes, 100, 2,
            py, 628, tr, 2, energies, 314, native, 628, &status) == REC_ERR_PARITY);
        assert(status.code == REC_ERR_PARITY && status.row == 2);
        assert(status.processed_rows == 3 + 314);
        py[2] = saved;
        rec_prefix_free(handle);
    }
    const double p[3] = {0.0, 1.0, 2.0};
    const double c[3] = {0.0, 1.00001, 2.0};
    const double fbb[3] = {1.0, 0.5, 0.0};
    double ratios[3];
    assert(rec_ratio_batch(3, p, c, fbb, ratios) == REC_OK);
    for (size_t i = 0; i < 3; ++i) {
        const double tol = 1.0e-7 * fmax(fabs(p[i]), fabs(c[i])) + 1.0e-10 * fbb[i];
        assert(ratios[i] == fabs(p[i] - c[i]) / tol);
    }
    assert(ratios[1] > 1.0);
    assert(rec_ratio_batch(0, NULL, NULL, NULL, NULL) == REC_OK);
    puts("C ABI smoke PASS: layout, parsed bits, parity/work count at 1/2/4 threads, batch ratios");
    return 0;
}
