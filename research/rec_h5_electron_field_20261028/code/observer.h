#ifndef ELECTRON_FIELD_OBSERVER_H
#define ELECTRON_FIELD_OBSERVER_H
#define EF_EVENT_CAP 472
typedef struct {
    int events, zero, nonfinite, overflow;
    double min_abs, schur, values[EF_EVENT_CAP];
    int kinds[EF_EVENT_CAP], indices[EF_EVENT_CAP];
} EFDiagnostics;
extern _Thread_local EFDiagnostics *ef_active_diagnostics;
void ef_observe(int kind, int index, double value);
#endif
