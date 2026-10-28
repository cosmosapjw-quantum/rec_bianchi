#ifndef ELECTRON_FIELD_H
#define ELECTRON_FIELD_H
#include <stddef.h>
#include "observer.h"
#define EF_N 311
typedef struct EFContext EFContext;
typedef struct {
    int status, kernel_calls;
    EFDiagnostics diagnostics;
    double FH, coefficient_TM_eV, coefficient_TR_eV, s, x1, Delta, H, nH;
    double xr[2], xv[EF_N], A[2][2], B[2][EF_N], C[2][EF_N], V[3][EF_N];
    double sr[2], sv[EF_N], Dtau[EF_N], Alpha[2], DAlpha[2], Beta[2];
} EFOutput;
EFContext *ef_context_new(void);
void ef_context_free(EFContext *context);
size_t ef_tables_count(void);
int ef_tables_copy(const EFContext *context, double *destination, size_t count);
int ef_evaluate(EFContext *context, const double *P, size_t P_count,
                const double *incoming, size_t incoming_count,
                const double *lyman, size_t lyman_count, int model,
                const char *phase, int helium_neutral, const char *units,
                const char *temperature_origin, const char *source_sha256,
                EFOutput *output);
#endif
