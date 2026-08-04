# Full Bianchi–HyRec COM pole/background action audit v0.9

This bounded audit adds the center-of-mass pole denominators and the
v0.8 bound+continuum scalar background to the exact event kinematics.

It is **not** yet the event-deposited production conductance.

## Frequency-anchor firewall

For internal transition energy fraction e0 = DeltaE/(M c^2),

    e_abs = 1 - sqrt(1-2 e0)
    e_em  = -1 + sqrt(1+2 e0).

At first order,

    x_abs = +g/2
    x_em  = -g/2,

where g = e0/b is the total recoil in Doppler widths.

The audit therefore compares

    baseline at x
    COM model at x + x_abs.

At line centre:

- baseline mean jump: -4.394289635901e-04
- COM-pole mean jump: -4.394289691764e-04
- difference: -5.586253465015e-12
- full-background increment: -2.064215343935e-08

The apparent factor-of-two recoil change seen when both models were
evaluated at the internal-energy frequency was an anchor mismatch.

## Wing result

For |x| <= 4, the genuine COM-pole action difference reaches

    5.571375e-04

Doppler widths, while the smooth bound+continuum background adds at most

    7.317673e-05.

These differences must now be tested at the finite-volume operator-action
level rather than inferred from individual event means.

## Files

- COM_action_table.csv
- COM_action_ledger.json
- verify_anchor_and_width.wl
- MANIFEST_SHA256.txt
