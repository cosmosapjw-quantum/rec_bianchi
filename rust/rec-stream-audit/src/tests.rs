// SPDX-License-Identifier: MIT
// Copyright (c) 2026 cosmosapjw-quantum
use super::*;

struct Handle(*mut c_void);

impl Handle {
    fn new(threads: usize) -> Self {
        let handle = rec_prefix_new(threads);
        assert!(!handle.is_null());
        Self(handle)
    }
}

impl Drop for Handle {
    fn drop(&mut self) {
        // SAFETY: tests keep a single owning Handle until all synchronous calls end.
        unsafe { rec_prefix_free(self.0) };
    }
}

struct Fixture {
    start: usize,
    columns: usize,
    lines: Vec<String>,
    py: Vec<f64>,
    tr: Vec<f64>,
    energies: Vec<f64>,
}

impl Fixture {
    fn new(start: usize, columns: usize) -> Self {
        let mut lines = Vec::new();
        let mut py = Vec::new();
        for col in 0..columns {
            for bin in 0..ROWS_PER_COLUMN {
                let value = match bin % 7 {
                    0 => 0.0,
                    1 => -0.0,
                    2 => -((col * ROWS_PER_COLUMN + bin) as f64 + 0.25) / 1000.0,
                    _ => ((col * ROWS_PER_COLUMN + bin) as f64 + 0.25) / 1000.0,
                };
                let (tag, b) = if bin < 311 { ("PV", bin) } else { ("PL", bin - 311) };
                lines.push(format!("{tag},{},{b},{value:.17e}", start + col));
                py.push(value);
            }
        }
        Self {
            start, columns, lines, py,
            tr: (0..columns).map(|c| 0.23 + c as f64 * 0.0001).collect(),
            energies: (0..ROWS_PER_COLUMN).map(|b| 0.5 + b as f64 * 0.001).collect(),
        }
    }

    fn text(&self) -> Vec<u8> {
        (self.lines.join("\n") + "\n").into_bytes()
    }

    fn args(&self, handle: &Handle, text: &[u8], output: &mut [f64]) -> AuditArgs {
        AuditArgs {
            handle: handle.0, text: text.as_ptr(), text_len: text.len(),
            start_col: self.start, columns: self.columns,
            py: self.py.as_ptr(), py_len: self.py.len(),
            tr: self.tr.as_ptr(), tr_len: self.tr.len(),
            energies: self.energies.as_ptr(), energies_len: self.energies.len(),
            native: output.as_mut_ptr(), native_len: output.len(),
        }
    }

    fn run_text(&self, handle: &Handle, text: &[u8]) -> (RecStatus, Vec<f64>) {
        let mut output = vec![-777.0; self.py.len()];
        let args = self.args(handle, text, &mut output);
        let mut status = RecStatus::panic();
        let code = call(args, &mut status);
        assert_eq!(code, status.code);
        (status, output)
    }

    fn run(&self, threads: usize) -> (RecStatus, Vec<f64>) {
        self.run_text(&Handle::new(threads), &self.text())
    }
}

fn call(args: AuditArgs, status: &mut RecStatus) -> i32 {
    // SAFETY: fixtures own all extents. Deliberately bad metadata in guard tests
    // is rejected before any data pointer is read; it is never dereferenced.
    unsafe {
        rec_prefix_audit(
            args.handle, args.text, args.text_len, args.start_col, args.columns,
            args.py, args.py_len, args.tr, args.tr_len,
            args.energies, args.energies_len, args.native, args.native_len, status,
        )
    }
}

fn assert_error(f: &Fixture, code: i32, row: usize, detail: i32) {
    for threads in [1, 2, 4] {
        let (status, _) = f.run(threads);
        assert_eq!((status.code, status.row, status.detail), (code, row, detail));
    }
}

#[test]
fn valid_maximum_block_has_exact_native_bits_and_reuses_local_pool() {
    let f = Fixture::new(137, MAX_COLUMNS);
    let text = f.text();
    for threads in [1, 2, 4] {
        let handle = Handle::new(threads);
        // SAFETY: Handle owns a live instance, accessed immutably between calls.
        let auditor = unsafe { &*handle.0.cast::<Auditor>() };
        assert_eq!(auditor.pool.as_ref().map(ThreadPool::current_num_threads),
                   if threads == 1 { None } else { Some(threads) });
        for _ in 0..2 {
            let (status, output) = f.run_text(&handle, &text);
            assert_eq!(status, RecStatus::ok(MAX_ROWS));
            assert!(output.iter().zip(&f.py).all(|(a, b)| a.to_bits() == b.to_bits()));
        }
    }
}

#[test]
fn whitespace_crlf_and_final_unterminated_line() {
    let mut f = Fixture::new(9, 1);
    f.py[0] = 0.001;
    f.lines[0] = "PV, +009 ,\t00 , \t1.000e-3 \u{2003}".into();
    let text = f.lines.join("\r\n").into_bytes();
    let (status, output) = f.run_text(&Handle::new(2), &text);
    assert_eq!(status, RecStatus::ok(314));
    assert_eq!(output[0].to_bits(), 0.001f64.to_bits());
}

#[test]
fn exact_four_fields_and_native_grammar() {
    for (line, code, detail) in [
        ("PV,3,5", REC_ERR_FIELDS, 0),
        ("PV,3,5,0,", REC_ERR_FIELDS, 0),
        ("PV,3,5,", REC_ERR_FLOAT, 4),
        ("PV,3,5,1_0", REC_ERR_FLOAT, 4),
        ("PV,3,5,1\0", REC_ERR_FLOAT, 4),
        ("PV,3,5,NaN", REC_ERR_NATIVE_NONFINITE, 4),
        ("PV,3,5,inf", REC_ERR_NATIVE_NONFINITE, 4),
        ("PV,3,5,-inf", REC_ERR_NATIVE_NONFINITE, 4),
        ("PV,3,5,1e999", REC_ERR_NATIVE_NONFINITE, 4),
        (" PV,3,5,0", REC_ERR_ORDER, 1),
        ("X,3,5,0", REC_ERR_ORDER, 1),
        ("PV,4,5,0", REC_ERR_ORDER, 2),
        ("PV,3,6,0", REC_ERR_ORDER, 3),
    ] {
        let mut f = Fixture::new(3, 1);
        f.lines[5] = line.into();
        assert_error(&f, code, 5, detail);
    }
}

#[test]
fn pv_pl_transition_and_lyman_bin_order_are_checked() {
    for (row, line, detail) in [
        (310, "PL,17,0,0", 1),
        (311, "PV,17,311,0", 1),
        (311, "PL,17,311,0", 3),
        (313, "PL,17,1,0", 3),
    ] {
        let mut f = Fixture::new(17, 1);
        f.lines[row] = line.into();
        assert_error(&f, REC_ERR_ORDER, row, detail);
    }
}

#[test]
fn integer_grammar_and_overflow_are_explicit() {
    for bad in ["", "+", "-0", "-1", "1.0", "1e0", "1_0", "0x1", "\u{ff11}"] {
        assert_eq!(parse_index(bad), None, "{bad:?}");
        let mut f = Fixture::new(0, 1);
        f.lines[2] = format!("PV,{bad},2,0");
        assert_error(&f, REC_ERR_INTEGER, 2, 2);
    }
    let overflow = format!("{}0", usize::MAX);
    assert_eq!(parse_index(&overflow), None);
    assert_eq!(parse_index(&usize::MAX.to_string()), Some(usize::MAX));
    assert_eq!(parse_index("  +00012\t"), Some(12));
    let mut f = Fixture::new(0, 1);
    f.lines[2] = format!("PV,0,{overflow},0");
    assert_error(&f, REC_ERR_INTEGER, 2, 3);
    // Last representable global column is valid for a one-column block.
    assert_eq!(Fixture::new(usize::MAX, 1).run(1).0, RecStatus::ok(314));
}

#[test]
fn python_values_tr_and_energies_must_be_finite_and_positive_where_required() {
    for bad in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        let mut f = Fixture::new(0, 2);
        f.py[315] = bad;
        assert_error(&f, REC_ERR_PY_NONFINITE, 315, 0);
    }
    for bad in [0.0, -0.0, -1.0, f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        let mut f = Fixture::new(0, 2);
        f.tr[1] = bad;
        assert_error(&f, REC_ERR_TR, 314, 0);
        let mut f = Fixture::new(0, 2);
        f.energies[23] = bad;
        assert_error(&f, REC_ERR_ENERGY, 23, 0);
    }
}

#[test]
fn earliest_failure_and_attempt_count_are_identical_with_one_two_four_threads() {
    let mut f = Fixture::new(41, 4);
    f.py[83] = 12345.0;
    f.lines[314 + 11] = "PV,999,11,0".into();
    f.tr[2] = f64::NAN;
    let text = f.text();
    let mut expected = RecStatus::error(REC_ERR_PARITY, 83, 0);
    expected.processed_rows = 84 + 12 + 1 + 314;
    for threads in [1, 2, 4] {
        let handle = Handle::new(threads);
        for _ in 0..8 {
            let (status, output) = f.run_text(&handle, &text);
            assert_eq!(status, expected);
            assert_eq!(output[83].to_bits(),
                       f.lines[83].split(',').nth(3).unwrap().parse::<f64>().unwrap().to_bits());
            assert_eq!(output[84], -777.0); // Its column stops at the error.
            assert_eq!(output[3 * 314 + 20].to_bits(), f.py[3 * 314 + 20].to_bits());
        }
    }
}

#[test]
fn later_invalid_utf8_or_missing_rows_do_not_mask_an_earlier_record_error() {
    let mut f = Fixture::new(0, 2);
    f.py[13] = 900.0;
    let mut text = f.text();
    let later = text.iter().enumerate().filter(|(_, b)| **b == b'\n')
        .nth(399).unwrap().0 + 1;
    text[later] = 0xff;
    for threads in [1, 2, 4] {
        let status = f.run_text(&Handle::new(threads), &text).0;
        assert_eq!((status.code, status.row), (REC_ERR_PARITY, 13));
    }
    f.py[13] = f.lines[13].split(',').nth(3).unwrap().parse().unwrap();
    let status = f.run_text(&Handle::new(4), &text).0;
    assert_eq!((status.code, status.row), (REC_ERR_UTF8, 400));
    f.lines.truncate(450);
    f.lines[17] = "bad".into();
    assert_error(&f, REC_ERR_FIELDS, 17, 0);
}

#[test]
fn row_counts_blank_records_and_extra_records_are_ordered() {
    let f = Fixture::new(0, 2);
    for threads in [1, 2, 4] {
        let handle = Handle::new(threads);
        let empty = f.run_text(&handle, b"").0;
        assert_eq!((empty.code, empty.row, empty.detail, empty.processed_rows),
                   (REC_ERR_ROWS, 0, -1, 0));
        let short = f.lines[..450].join("\n");
        let status = f.run_text(&handle, short.as_bytes()).0;
        assert_eq!((status.code, status.row, status.detail, status.processed_rows),
                   (REC_ERR_ROWS, 450, -1, 450));
        let mut extra = f.text();
        extra.extend_from_slice(b"extra\nmore\n");
        let status = f.run_text(&handle, &extra).0;
        assert_eq!((status.code, status.row, status.detail, status.processed_rows),
                   (REC_ERR_ROWS, 628, 1, 628));
    }
    let mut blank = Fixture::new(0, 1);
    blank.lines[2].clear();
    assert_error(&blank, REC_ERR_FIELDS, 2, 0);
    let mut earlier = Fixture::new(0, 1);
    earlier.lines[4] = "bad".into();
    earlier.lines.push("extra".into());
    assert_error(&earlier, REC_ERR_FIELDS, 4, 0);
}

#[test]
fn exact_boundary_matches_independent_python_math_reference() {
    // Python 3.12.14 / Linux math.expm1: greatest native value passing when
    // py=0, energy=tr=1. Its tolerance is exactly this value in binary64.
    // The immediately following representable native value fails.
    let boundary = f64::from_bits(0x3dcf_fe98_461a_10da);
    assert_eq!(check_value(0.0, boundary, 1.0, 1.0), Ok(()));
    assert_eq!(check_value(0.0, f64::from_bits(boundary.to_bits() + 1), 1.0, 1.0),
               Err((REC_ERR_PARITY, 0)));
    for (native, expected_code) in [(boundary, REC_OK),
                                   (f64::from_bits(boundary.to_bits() + 1), REC_ERR_PARITY)] {
        let mut f = Fixture::new(0, 1);
        f.tr[0] = 1.0;
        f.energies[0] = 1.0;
        f.lines[0] = format!("PV,0,0,{native:.17e}");
        assert_eq!(f.run(1).0.code, expected_code);
    }
}

#[test]
fn scalar_association_matches_python_vectors_that_differ_under_fma() {
    // Independent Python binary64 products+sum, compared to libc fma during
    // fixture derivation. Every expected result differs by one ULP from FMA.
    for (p, f, expected) in [
        (0x3f17_3319_dfa5_8020, 0x3e69_85e9_b383_9a75, 0x3da3_7614_ed94_3052),
        (0x3fe5_b6ec_805e_091c, 0x3e46_2f14_8b6f_8a7f, 0x3e72_3729_cda8_f6a9),
        (0x4077_2267_b481_082c, 0x4006_d4ed_63a2_76f6, 0x3f03_681c_9ddc_682d),
    ] {
        assert_eq!(tolerance(f64::from_bits(p), 0.0, f64::from_bits(f)).to_bits(), expected);
    }
}

#[test]
fn zero_tolerance_nonfinite_tolerance_and_blackbody_boundary_semantics() {
    assert_eq!(check_value(0.0, -0.0, 1.0, 1.0), Ok(()));
    // Infinite quotient itself is legal in Python math.expm1: fbb=0, tol=0.
    assert_eq!(check_value(0.0, 0.0, f64::MIN_POSITIVE, f64::MAX), Ok(()));
    assert_eq!(check_value(0.0, f64::from_bits(1), f64::MIN_POSITIVE, f64::MAX),
               Err((REC_ERR_PARITY, 0)));
    // Finite expm1 overflow and reciprocal of an underflowed zero match Python
    // exceptions. An infinite tolerance is explicitly rejected by this ABI.
    assert_eq!(check_value(0.0, 0.0, 1.0, 1000.0), Err((REC_ERR_BLACKBODY, 1)));
    assert_eq!(check_value(0.0, 0.0, f64::MAX, f64::from_bits(1)),
               Err((REC_ERR_BLACKBODY, 2)));
    assert_eq!(check_value(0.0, 0.0, 1.0, f64::from_bits(1)),
               Err((REC_ERR_TOLERANCE, 0)));
    assert_eq!(check_value(f64::MAX, -f64::MAX, 1.0, 1.0), Err((REC_ERR_PARITY, 0)));
    assert_eq!(check_value(f64::MAX, f64::MAX, 1.0, 1.0), Ok(()));
}

#[test]
fn invalid_handle_thread_counts_and_null_free() {
    for threads in [0, 5, usize::MAX] { assert!(rec_prefix_new(threads).is_null()); }
    // SAFETY: NULL is expressly accepted.
    unsafe { rec_prefix_free(ptr::null_mut()) };
}

#[test]
fn metadata_caps_lengths_nulls_alignment_and_ranges_are_checked_before_reads() {
    let f = Fixture::new(0, 2);
    let handle = Handle::new(1);
    let text = f.text();
    let mut output = vec![0.0; f.py.len()];
    let good = f.args(&handle, &text, &mut output);
    let mut variants = Vec::new();
    for columns in [0, 65, usize::MAX] {
        let mut a = good; a.columns = columns; a.handle = ptr::dangling_mut::<Auditor>().cast();
        variants.push((a, REC_ERR_LIMIT, ARG_COLUMNS));
    }
    let mut a = good; a.text_len = MAX_TEXT_BYTES + 1; a.text = ptr::dangling();
    variants.push((a, REC_ERR_LIMIT, ARG_TEXT));
    let mut a = good; a.start_col = usize::MAX;
    variants.push((a, REC_ERR_LIMIT, ARG_START_COL));
    for (argument, change) in [
        (ARG_PY, 0), (ARG_TR, 1), (ARG_ENERGIES, 2), (ARG_NATIVE, 3),
    ] {
        let mut a = good;
        match change {
            0 => a.py_len = usize::MAX,
            1 => a.tr_len += 1,
            2 => a.energies_len -= 1,
            _ => a.native_len -= 1,
        }
        variants.push((a, REC_ERR_LENGTH, argument));
    }
    for argument in [ARG_HANDLE, ARG_TEXT, ARG_PY, ARG_TR, ARG_ENERGIES, ARG_NATIVE] {
        let mut a = good;
        match argument {
            ARG_HANDLE => a.handle = ptr::null_mut(),
            ARG_TEXT => a.text = ptr::null(),
            ARG_PY => a.py = ptr::null(),
            ARG_TR => a.tr = ptr::null(),
            ARG_ENERGIES => a.energies = ptr::null(),
            _ => a.native = ptr::null_mut(),
        }
        variants.push((a, REC_ERR_NULL, argument));
    }
    let mut a = good; a.py = 1usize as *const f64;
    variants.push((a, REC_ERR_ALIGNMENT, ARG_PY));
    let mut a = good; a.text = (usize::MAX - 5) as *const u8;
    variants.push((a, REC_ERR_LENGTH, ARG_TEXT));
    for (args, code, detail) in variants {
        let mut status = RecStatus::panic();
        assert_eq!(call(args, &mut status), code);
        assert_eq!(status, RecStatus::argument(code, detail));
    }
    assert!(output.iter().all(|&x| x == 0.0));
}

#[test]
fn overlapping_buffers_and_unwritable_status_metadata_are_rejected() {
    let mut f = Fixture::new(0, 1);
    let handle = Handle::new(1);
    let text = f.text();
    let mut output = vec![0.0; f.py.len()];
    let mut args = f.args(&handle, &text, &mut output);
    args.native = f.py.as_mut_ptr();
    let mut status = RecStatus::panic();
    let before = status;
    assert_eq!(call(args, &mut status), REC_ERR_OVERLAP);
    assert_eq!(status, before); // No writes on any overlap.
    let args = f.args(&handle, &text, &mut output);
    // SAFETY: invalid status metadata is rejected without a read/write.
    unsafe {
        for (out, expected) in [(ptr::null_mut(), REC_ERR_NULL),
                                (1usize as *mut RecStatus, REC_ERR_ALIGNMENT),
                                (f.py.as_mut_ptr().cast::<RecStatus>(), REC_ERR_OVERLAP)] {
            assert_eq!(rec_prefix_audit(args.handle, args.text, args.text_len,
                       args.start_col, args.columns, args.py, args.py_len,
                       args.tr, args.tr_len, args.energies, args.energies_len,
                       args.native, args.native_len, out), expected);
        }
    }
    assert_eq!(f.py[0].to_bits(), 0.0f64.to_bits());
}

#[test]
fn batch_matches_independent_scalar_formula_bit_for_bit_and_accepts_ratios_above_one() {
    let n = MAX_ROWS;
    let py: Vec<f64> = (0..n).map(|i| ((i as f64 + 0.5) / 97.0) - 100.0).collect();
    let c: Vec<f64> = py.iter().enumerate().map(|(i, &p)| p + (i % 11) as f64 * 1.0e-5).collect();
    let fbb: Vec<f64> = (0..n).map(|i| (i % 13) as f64 * 0.01).collect();
    let mut out = vec![MaybeUninit::<f64>::uninit(); n];
    // SAFETY: distinct, valid extents; output is intentionally uninitialized.
    let code = unsafe { rec_ratio_batch(n, py.as_ptr(), c.as_ptr(), fbb.as_ptr(), out.as_mut_ptr().cast()) };
    assert_eq!(code, REC_OK);
    let mut above_one = false;
    for i in 0..n {
        let reference = (py[i] - c[i]).abs() /
            (1.0e-7 * py[i].abs().max(c[i].abs()) + 1.0e-10 * fbb[i]);
        // SAFETY: successful batch writes every output lane.
        let actual = unsafe { out[i].assume_init() };
        assert_eq!(actual.to_bits(), reference.to_bits());
        above_one |= actual > 1.0;
    }
    assert!(above_one);
}

#[test]
fn batch_checks_nonfinite_inputs_zero_denominator_overflow_and_pointer_contract() {
    let run = |py: f64, c: f64, fbb: f64| {
        let mut out = 99.0;
        // SAFETY: distinct initialized inputs and writable output.
        let code = unsafe { rec_ratio_batch(1, &py, &c, &fbb, &mut out) };
        (code, out)
    };
    assert_eq!(run(0.0, -0.0, 1.0), (REC_OK, 0.0));
    assert_eq!(run(0.0, 0.0, 0.0).0, REC_ERR_RATIO);
    assert_eq!(run(f64::MAX, -f64::MAX, 1.0).0, REC_ERR_RATIO);
    assert_eq!(run(f64::MAX, f64::MAX, 0.0), (REC_OK, 0.0));
    for bad in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
        assert_eq!(run(bad, 0.0, 1.0), (REC_ERR_PY_NONFINITE, 99.0));
        assert_eq!(run(0.0, bad, 1.0), (REC_ERR_NATIVE_NONFINITE, 99.0));
        assert_eq!(run(0.0, 0.0, bad), (REC_ERR_FBB, 99.0));
    }
    assert_eq!(run(0.0, 0.0, -1.0), (REC_ERR_FBB, 99.0));
    // SAFETY: these invalid pointer combinations are rejected before reads.
    unsafe {
        assert_eq!(rec_ratio_batch(0, ptr::null(), ptr::null(), ptr::null(), ptr::null_mut()), REC_OK);
        assert_eq!(rec_ratio_batch(MAX_ROWS + 1, ptr::null(), ptr::null(), ptr::null(), ptr::null_mut()), REC_ERR_LIMIT);
        assert_eq!(rec_ratio_batch(1, ptr::null(), ptr::null(), ptr::null(), ptr::null_mut()), REC_ERR_NULL);
        let mut data = [1.0; 4];
        assert_eq!(rec_ratio_batch(4, data.as_ptr(), data.as_ptr(), data.as_ptr(), data.as_mut_ptr()), REC_ERR_OVERLAP);
        assert_eq!(rec_ratio_batch(1, 1usize as *const f64, data.as_ptr(), data.as_ptr(), data.as_mut_ptr()), REC_ERR_ALIGNMENT);
    }
}

#[test]
fn unwinds_and_panicking_payload_destructors_stay_inside_boundary_helper() {
    assert_eq!(contained(REC_ERR_PANIC, || panic!("synthetic local panic")), REC_ERR_PANIC);
    let pool = ThreadPoolBuilder::new().num_threads(2).build().unwrap();
    assert_eq!(contained(REC_ERR_PANIC, || pool.install(|| panic!("synthetic worker panic"))), REC_ERR_PANIC);
    struct BadDrop;
    impl Drop for BadDrop { fn drop(&mut self) { panic!("payload destructor"); } }
    assert_eq!(contained(REC_ERR_PANIC, || std::panic::panic_any(BadDrop)), REC_ERR_PANIC);
}
