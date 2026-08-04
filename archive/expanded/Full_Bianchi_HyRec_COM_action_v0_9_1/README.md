# Full Bianchi–HyRec COM action audit v0.9.1

**Use this bundle, not v0.9.**  The first v0.9 bundle contained stale
smooth-background opacity columns.  v0.9.1 recomputes every pole and
full-amplitude weight.

## Line-anchor result

Equal physical detuning means comparing the standard baseline at x with
the COM model at x + x_abs, where

    x_abs = 2.314599800955e-04
    x_em  = -2.314599800955e-04

Doppler widths.

At line centre:

- baseline M1 = -4.394289635901e-04
- COM-pole M1 = -4.394289691764e-04
- difference  = -5.586253465015e-12
- smooth-background increment = -2.064215343935e-08

Thus the apparent half-recoil discrepancy was a line-anchor mismatch.

## Genuine wing action

For |x| <= 4:

- max COM-pole M1 change:
  5.571375458353e-04
- max smooth-background M1 increment:
  7.317672717821e-05
- max COM-pole opacity change:
  1.759504200034e-03
- max smooth-background opacity change relative to pole:
  1.576837613871e-04

The background opacity correction is now O(10^-4), consistent with the
independent v0.6 KHW audit.

## Files

- COM_action_table.csv
- COM_action_ledger.json
- MANIFEST_SHA256.txt
