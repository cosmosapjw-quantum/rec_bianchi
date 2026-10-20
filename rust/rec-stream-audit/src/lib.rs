// SPDX-License-Identifier: MIT
// Copyright (c) 2026 cosmosapjw-quantum
//! Bounded PV/PL audit; the physical integrator and scalar Tr remain in Python.
//! See include/rec_stream_audit.h and README.md for the C caller contract.

#![deny(unsafe_op_in_unsafe_fn)]

#[cfg(panic = "abort")]
compile_error!("rec-stream-audit requires panic=unwind to contain FFI panics");

use rayon::prelude::*;
use rayon::{ThreadPool, ThreadPoolBuilder};
use std::ffi::{c_int, c_void};
use std::mem::{align_of, size_of, MaybeUninit};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::{ptr, slice, str};

pub const ROWS_PER_COLUMN: usize = 314;
pub const MAX_COLUMNS: usize = 64;
pub const MAX_ROWS: usize = ROWS_PER_COLUMN * MAX_COLUMNS;
pub const MAX_TEXT_BYTES: usize = 4 * 1024 * 1024;
const WORKER_STACK_BYTES: usize = 256 * 1024;
pub const NO_ROW: usize = usize::MAX;

pub const REC_OK: i32 = 0;
pub const REC_ERR_NULL: i32 = 1;
pub const REC_ERR_LENGTH: i32 = 2;
pub const REC_ERR_LIMIT: i32 = 3;
pub const REC_ERR_ALIGNMENT: i32 = 4;
pub const REC_ERR_OVERLAP: i32 = 5;
pub const REC_ERR_FIELDS: i32 = 10;
pub const REC_ERR_INTEGER: i32 = 11;
pub const REC_ERR_ORDER: i32 = 12;
pub const REC_ERR_FLOAT: i32 = 13;
pub const REC_ERR_NATIVE_NONFINITE: i32 = 14;
pub const REC_ERR_PY_NONFINITE: i32 = 15;
pub const REC_ERR_TR: i32 = 16;
pub const REC_ERR_ENERGY: i32 = 17;
pub const REC_ERR_TOLERANCE: i32 = 18;
pub const REC_ERR_PARITY: i32 = 19;
pub const REC_ERR_ROWS: i32 = 20;
pub const REC_ERR_UTF8: i32 = 21;
pub const REC_ERR_BLACKBODY: i32 = 22;
pub const REC_ERR_FBB: i32 = 30;
pub const REC_ERR_RATIO: i32 = 31;
pub const REC_ERR_PANIC: i32 = 90;

const ARG_HANDLE: i32 = 1;
const ARG_TEXT: i32 = 2;
const ARG_COLUMNS: i32 = 3;
const ARG_START_COL: i32 = 4;
const ARG_PY: i32 = 5;
const ARG_TR: i32 = 6;
const ARG_ENERGIES: i32 = 7;
const ARG_NATIVE: i32 = 8;
const ARG_STATUS: i32 = 9;
const ARG_FBB: i32 = 11;
const ARG_C: i32 = 12;
const ARG_RATIO_OUT: i32 = 13;

#[repr(C)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct RecStatus {
    pub code: i32,
    pub row: usize,
    pub detail: i32,
    pub processed_rows: usize,
}

impl RecStatus {
    fn ok(processed_rows: usize) -> Self {
        Self { code: REC_OK, row: NO_ROW, detail: 0, processed_rows }
    }

    fn error(code: i32, row: usize, detail: i32) -> Self {
        Self { code, row, detail, processed_rows: 0 }
    }

    fn argument(code: i32, argument: i32) -> Self {
        Self::error(code, NO_ROW, argument)
    }

    fn panic() -> Self {
        Self { code: REC_ERR_PANIC, row: NO_ROW, detail: 0, processed_rows: NO_ROW }
    }
}

struct Auditor {
    pool: Option<ThreadPool>,
}

// Link the platform libm, as used by Python math.expm1 on Linux. This is not a
// Rust approximation, a vector transcendental, or the physical C code.
#[cfg_attr(target_os = "linux", link(name = "m"))]
extern "C" {
    #[link_name = "expm1"]
    fn system_expm1(value: f64) -> f64;
}

fn contained<T>(fallback: T, body: impl FnOnce() -> T) -> T {
    match catch_unwind(AssertUnwindSafe(body)) {
        Ok(value) => value,
        Err(payload) => {
            // A user-supplied panic payload may itself panic in Drop. Do not
            // let a second unwind escape an extern "C" boundary.
            std::mem::forget(payload);
            fallback
        }
    }
}

#[derive(Clone, Copy)]
struct Span {
    begin: usize,
    end: usize,
}

impl Span {
    fn overlaps(self, other: Self) -> bool {
        self.begin < other.end && other.begin < self.end
            && self.begin != self.end && other.begin != other.end
    }
}

// Metadata only: no pointer is read or turned into a reference here. A valid
// address range is still a caller obligation; addresses cannot prove ownership.
fn span<T>(pointer: *const T, len: usize, argument: i32) -> Result<Span, RecStatus> {
    if pointer.is_null() {
        return Err(RecStatus::argument(REC_ERR_NULL, argument));
    }
    let begin = pointer as usize;
    if begin % align_of::<T>() != 0 {
        return Err(RecStatus::argument(REC_ERR_ALIGNMENT, argument));
    }
    let bytes = len.checked_mul(size_of::<T>())
        .filter(|&bytes| bytes <= isize::MAX as usize)
        .ok_or_else(|| RecStatus::argument(REC_ERR_LENGTH, argument))?;
    let end = begin.checked_add(bytes)
        .ok_or_else(|| RecStatus::argument(REC_ERR_LENGTH, argument))?;
    Ok(Span { begin, end })
}

/// Construct a handle with 1..4 threads. Returns NULL on invalid count or failure.
#[no_mangle]
pub extern "C" fn rec_prefix_new(threads: usize) -> *mut c_void {
    contained(ptr::null_mut(), || {
        if !(1..=4).contains(&threads) {
            return ptr::null_mut();
        }
        let pool = if threads == 1 {
            None
        } else {
            match ThreadPoolBuilder::new()
                .num_threads(threads)
                .stack_size(WORKER_STACK_BYTES)
                .thread_name(|i| format!("rec-prefix-{i}"))
                .build()
            {
                Ok(pool) => Some(pool),
                Err(_) => return ptr::null_mut(),
            }
        };
        Box::into_raw(Box::new(Auditor { pool })).cast()
    })
}

/// Free a handle; NULL is a no-op.
///
/// # Safety
/// A non-NULL handle must come from this library's rec_prefix_new, be live,
/// and be exclusively owned, with no concurrent calls. Free it exactly once.
#[no_mangle]
pub unsafe extern "C" fn rec_prefix_free(handle: *mut c_void) {
    contained((), || {
        if !handle.is_null() {
            // SAFETY: required live, exclusive Box ownership from the caller.
            unsafe { drop(Box::from_raw(handle.cast::<Auditor>())) };
        }
    });
}

#[derive(Clone, Copy)]
struct AuditArgs {
    handle: *mut c_void,
    text: *const u8,
    text_len: usize,
    start_col: usize,
    columns: usize,
    py: *const f64,
    py_len: usize,
    tr: *const f64,
    tr_len: usize,
    energies: *const f64,
    energies_len: usize,
    native: *mut f64,
    native_len: usize,
}

impl AuditArgs {
    fn validate(self, status_span: Span) -> Result<(), RecStatus> {
        if !(1..=MAX_COLUMNS).contains(&self.columns) {
            return Err(RecStatus::argument(REC_ERR_LIMIT, ARG_COLUMNS));
        }
        if self.text_len > MAX_TEXT_BYTES {
            return Err(RecStatus::argument(REC_ERR_LIMIT, ARG_TEXT));
        }
        if self.start_col.checked_add(self.columns - 1).is_none() {
            return Err(RecStatus::argument(REC_ERR_LIMIT, ARG_START_COL));
        }
        let rows = self.columns * ROWS_PER_COLUMN;
        for (actual, expected, argument) in [
            (self.py_len, rows, ARG_PY),
            (self.tr_len, self.columns, ARG_TR),
            (self.energies_len, ROWS_PER_COLUMN, ARG_ENERGIES),
            (self.native_len, rows, ARG_NATIVE),
        ] {
            if actual != expected {
                return Err(RecStatus::argument(REC_ERR_LENGTH, argument));
            }
        }
        let handle = span(self.handle.cast::<Auditor>(), 1, ARG_HANDLE)?;
        let inputs = [
            span(self.text, self.text_len, ARG_TEXT)?,
            span(self.py, self.py_len, ARG_PY)?,
            span(self.tr, self.tr_len, ARG_TR)?,
            span(self.energies, self.energies_len, ARG_ENERGIES)?,
        ];
        let output = span(self.native, self.native_len, ARG_NATIVE)?;
        for other in inputs.into_iter().chain([handle, output]) {
            if status_span.overlaps(other) {
                return Err(RecStatus::argument(REC_ERR_OVERLAP, ARG_STATUS));
            }
        }
        for other in inputs.into_iter().chain([handle]) {
            if output.overlaps(other) {
                return Err(RecStatus::argument(REC_ERR_OVERLAP, ARG_NATIVE));
            }
        }
        for other in inputs {
            if handle.overlaps(other) {
                return Err(RecStatus::argument(REC_ERR_OVERLAP, ARG_HANDLE));
            }
        }
        Ok(())
    }

    unsafe fn run(self) -> RecStatus {
        // SAFETY: validate ran before any pointer read. Caller guarantees live
        // storage, initialized immutable inputs, and a valid handle. Writable
        // output does not overlap an input. MaybeUninit supports C/NumPy buffers
        // whose initial elements need not have defined values.
        let (auditor, text, py, tr, energies, native) = unsafe {
            (
                &*self.handle.cast::<Auditor>(),
                slice::from_raw_parts(self.text, self.text_len),
                slice::from_raw_parts(self.py, self.py_len),
                slice::from_raw_parts(self.tr, self.tr_len),
                slice::from_raw_parts(self.energies, self.energies_len),
                slice::from_raw_parts_mut(self.native.cast::<MaybeUninit<f64>>(), self.native_len),
            )
        };
        audit_block(auditor, text, self.start_col, py, tr, energies, native)
    }
}

/// Audit a bounded block. See the C header for lengths, codes and row semantics.
///
/// # Safety
/// All pointer extents must be valid; inputs initialized and immutable; native
/// and status writable and disjoint from all other buffers and the live handle.
/// The handle cannot be freed while this call is in flight. See README.md.
#[no_mangle]
#[allow(clippy::too_many_arguments)]
pub unsafe extern "C" fn rec_prefix_audit(
    handle: *mut c_void,
    text: *const u8, text_len: usize,
    start_col: usize, columns: usize,
    py_values: *const f64, py_len: usize,
    tr: *const f64, tr_len: usize,
    energies: *const f64, energies_len: usize,
    native_values: *mut f64, native_len: usize,
    out: *mut RecStatus,
) -> c_int {
    let status_span = match span(out, 1, ARG_STATUS) {
        Ok(value) => value,
        Err(error) => return error.code,
    };
    let args = AuditArgs {
        handle, text, text_len, start_col, columns,
        py: py_values, py_len, tr, tr_len, energies, energies_len,
        native: native_values, native_len,
    };
    let status = contained(RecStatus::panic(), || {
        if let Err(error) = args.validate(status_span) {
            return error;
        }
        // SAFETY: metadata validated, remaining obligations documented above.
        unsafe { args.run() }
    });
    if status.code != REC_ERR_OVERLAP {
        // SAFETY: status pointer is checked and caller promises writable storage.
        unsafe { ptr::write(out, status) };
    }
    status.code
}

fn parse_index(field: &str) -> Option<usize> {
    let trimmed = field.trim();
    let digits = trimmed.strip_prefix('+').unwrap_or(trimmed);
    if digits.is_empty() {
        return None;
    }
    digits.bytes().try_fold(0usize, |value, digit| {
        if digit.is_ascii_digit() {
            value.checked_mul(10)?.checked_add((digit - b'0') as usize)
        } else {
            None
        }
    })
}

fn parse_record(bytes: &[u8], column: usize, bin: usize) -> Result<f64, (i32, i32)> {
    let line = str::from_utf8(bytes).map_err(|_| (REC_ERR_UTF8, 0))?;
    let mut fields = line.split(',');
    let tag = fields.next().ok_or((REC_ERR_FIELDS, 0))?;
    let column_field = fields.next().ok_or((REC_ERR_FIELDS, 0))?;
    let bin_field = fields.next().ok_or((REC_ERR_FIELDS, 0))?;
    let value_field = fields.next().ok_or((REC_ERR_FIELDS, 0))?;
    if fields.next().is_some() {
        return Err((REC_ERR_FIELDS, 0));
    }
    let actual_column = parse_index(column_field).ok_or((REC_ERR_INTEGER, 2))?;
    let actual_bin = parse_index(bin_field).ok_or((REC_ERR_INTEGER, 3))?;
    let (expected_tag, expected_bin) = if bin < 311 { ("PV", bin) } else { ("PL", bin - 311) };
    if tag != expected_tag {
        return Err((REC_ERR_ORDER, 1));
    }
    if actual_column != column {
        return Err((REC_ERR_ORDER, 2));
    }
    if actual_bin != expected_bin {
        return Err((REC_ERR_ORDER, 3));
    }
    let value = value_field.trim().parse::<f64>().map_err(|_| (REC_ERR_FLOAT, 4))?;
    if !value.is_finite() {
        return Err((REC_ERR_NATIVE_NONFINITE, 4));
    }
    Ok(value)
}

#[inline]
fn tolerance(py: f64, native: f64, fbb: f64) -> f64 {
    let py_abs = py.abs();
    let native_abs = native.abs();
    let largest = if py_abs >= native_abs { py_abs } else { native_abs };
    let relative = 1.0e-7 * largest;
    let floor = 1.0e-10 * fbb;
    relative + floor
}

fn check_value(py: f64, native: f64, tr: f64, energy: f64) -> Result<(), (i32, i32)> {
    if !py.is_finite() {
        return Err((REC_ERR_PY_NONFINITE, 0));
    }
    if !tr.is_finite() || tr <= 0.0 {
        return Err((REC_ERR_TR, 0));
    }
    if !energy.is_finite() || energy <= 0.0 {
        return Err((REC_ERR_ENERGY, 0));
    }
    let argument = energy / tr;
    // SAFETY: system expm1 has no pointer arguments or shared physics state.
    let denominator = unsafe { system_expm1(argument) };
    // Python math.expm1 raises on finite-argument overflow, and 1./0. raises.
    // An infinite argument itself is allowed: expm1(+inf)=+inf, fbb=0.
    if argument.is_finite() && denominator.is_infinite() {
        return Err((REC_ERR_BLACKBODY, 1));
    }
    if denominator == 0.0 {
        return Err((REC_ERR_BLACKBODY, 2));
    }
    let fbb = 1.0 / denominator;
    let tol = tolerance(py, native, fbb);
    if !tol.is_finite() {
        return Err((REC_ERR_TOLERANCE, 0));
    }
    // No ratio is substituted here: equality at a zero or positive tolerance
    // passes, and overflow in the difference still fails the original gate.
    if (py - native).abs() > tol {
        return Err((REC_ERR_PARITY, 0));
    }
    Ok(())
}

#[derive(Clone, Copy)]
struct ColumnOutcome {
    error: Option<RecStatus>,
    attempted: usize,
}

fn audit_column(
    records: &[Option<&[u8]>],
    py: &[f64],
    native: &mut [MaybeUninit<f64>],
    tr: f64,
    energies: &[f64],
    column: usize,
    first_row: usize,
) -> ColumnOutcome {
    let mut attempted = 0;
    for (bin, record) in records.iter().enumerate() {
        let row = first_row + bin;
        let Some(bytes) = record else {
            return ColumnOutcome {
                error: Some(RecStatus::error(REC_ERR_ROWS, row, -1)), attempted,
            };
        };
        attempted += 1;
        let result = parse_record(bytes, column, bin).and_then(|value| {
            native[bin].write(value);
            check_value(py[bin], value, tr, energies[bin])
        });
        if let Err((code, detail)) = result {
            return ColumnOutcome {
                error: Some(RecStatus::error(code, row, detail)), attempted,
            };
        }
    }
    ColumnOutcome { error: None, attempted }
}

fn audit_block(
    auditor: &Auditor,
    text: &[u8],
    start_col: usize,
    py: &[f64],
    tr: &[f64],
    energies: &[f64],
    native: &mut [MaybeUninit<f64>],
) -> RecStatus {
    let rows = py.len();
    // Borrow each line. Slots are bounded by the declared block size, even on
    // malformed input. Do not validate all UTF-8 or values ahead of earlier rows.
    let mut records = vec![None; rows];
    let mut remaining = text;
    let mut count = 0;
    while !remaining.is_empty() && count < rows {
        if let Some(end) = remaining.iter().position(|&byte| byte == b'\n') {
            records[count] = Some(&remaining[..end]);
            remaining = &remaining[end + 1..];
        } else {
            records[count] = Some(remaining);
            remaining = &[];
        }
        count += 1;
    }
    let extra = !remaining.is_empty();
    // All jobs finish. Indexed zip/map/collect preserves column positions;
    // neither scheduling nor short-circuit parallel reduction chooses an error.
    let outcomes: Vec<ColumnOutcome> = if let Some(pool) = &auditor.pool {
        pool.install(|| {
            records.par_chunks(ROWS_PER_COLUMN)
                .zip(py.par_chunks(ROWS_PER_COLUMN))
                .zip(native.par_chunks_mut(ROWS_PER_COLUMN))
                .enumerate()
                .map(|(col, ((lines, py), native))| {
                    audit_column(lines, py, native, tr[col], energies,
                                 start_col + col, col * ROWS_PER_COLUMN)
                })
                .collect()
        })
    } else {
        records.chunks(ROWS_PER_COLUMN)
            .zip(py.chunks(ROWS_PER_COLUMN))
            .zip(native.chunks_mut(ROWS_PER_COLUMN))
            .enumerate()
            .map(|(col, ((lines, py), native))| {
                audit_column(lines, py, native, tr[col], energies,
                             start_col + col, col * ROWS_PER_COLUMN)
            })
            .collect()
    };
    let mut status = RecStatus::ok(0);
    let mut attempted = 0;
    for outcome in outcomes {
        attempted += outcome.attempted;
        if status.code == REC_OK {
            if let Some(error) = outcome.error {
                status = error;
            }
        }
    }
    if status.code == REC_OK && extra {
        status = RecStatus::error(REC_ERR_ROWS, rows, 1);
    }
    status.processed_rows = attempted;
    status
}

// A separate pure per-lane loop gives LLVM an opportunity to auto-vectorize.
// Input validation and the output finiteness scan do not change its arithmetic.
// Keep a distinct symbol for compiler IR/assembly inspection by the parent.
#[inline(never)]
fn ratio_kernel(py: &[f64], native: &[f64], fbb: &[f64], out: &mut [MaybeUninit<f64>]) {
    for (((&py, &native), &fbb), dst) in py.iter().zip(native).zip(fbb).zip(out) {
        dst.write((py - native).abs() / tolerance(py, native, fbb));
    }
}

unsafe fn ratio_batch(n: usize, py: *const f64, native: *const f64,
                      fbb: *const f64, out: *mut f64) -> i32 {
    if n > MAX_ROWS {
        return REC_ERR_LIMIT;
    }
    if n == 0 {
        return REC_OK;
    }
    let validate = || -> Result<(), RecStatus> {
        let inputs = [span(py, n, ARG_PY)?, span(native, n, ARG_C)?, span(fbb, n, ARG_FBB)?];
        let output = span(out, n, ARG_RATIO_OUT)?;
        if inputs.into_iter().any(|input| output.overlaps(input)) {
            return Err(RecStatus::argument(REC_ERR_OVERLAP, ARG_RATIO_OUT));
        }
        Ok(())
    };
    if let Err(error) = validate() {
        return error.code;
    }
    // SAFETY: all metadata was checked without reading pointers; caller provides
    // initialized input extents and a separate writable output extent.
    let (py, native, fbb, out) = unsafe {
        (slice::from_raw_parts(py, n), slice::from_raw_parts(native, n),
         slice::from_raw_parts(fbb, n),
         slice::from_raw_parts_mut(out.cast::<MaybeUninit<f64>>(), n))
    };
    for ((&py, &native), &fbb) in py.iter().zip(native).zip(fbb) {
        if !py.is_finite() { return REC_ERR_PY_NONFINITE; }
        if !native.is_finite() { return REC_ERR_NATIVE_NONFINITE; }
        if !fbb.is_finite() || fbb < 0.0 { return REC_ERR_FBB; }
        if !tolerance(py, native, fbb).is_finite() { return REC_ERR_TOLERANCE; }
    }
    ratio_kernel(py, native, fbb, out);
    for value in out {
        // SAFETY: ratio_kernel writes every element before this scan starts.
        if !unsafe { value.assume_init() }.is_finite() {
            return REC_ERR_RATIO;
        }
    }
    REC_OK
}

/// Compute finite independent lane ratios. Finite ratios above one are allowed.
///
/// # Safety
/// For n>0, all arrays have n valid elements; inputs initialized and immutable,
/// output writable and not overlapping inputs. For n==0 NULL is accepted.
#[no_mangle]
pub unsafe extern "C" fn rec_ratio_batch(
    n: usize, py: *const f64, c: *const f64, fbb: *const f64, out: *mut f64,
) -> c_int {
    contained(REC_ERR_PANIC, || {
        // SAFETY: forwarding the public caller contract to metadata validation.
        unsafe { ratio_batch(n, py, c, fbb, out) }
    })
}

#[cfg(test)]
mod tests;
