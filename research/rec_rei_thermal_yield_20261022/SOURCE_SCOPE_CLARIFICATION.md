# Source-scope clarification — retained continuum versus omitted resonances

Recorded during the same independent review on 2026-10-22. This note supersedes
the sentence “Core excitation is zero for this support” in the historical frozen
contract. The original contract bytes are retained because they are part of the
executed scientific identity. No source coefficient, spectrum, equation, case,
tolerance, acceptance gate, or completed trajectory is changed.

**Correct statement:** For this source support, the retained direct Li I
1s-photoionization branch and its direct-core-hole energy term vanish. Resonant
core excitation and its decay are excluded model processes; some resonances lie
inside 50–60 eV, and no zero omission error is asserted.

The published primary source Müller, Kheifets, Bray & Fursa, *Physical Review A*
113, 033105 (2026), DOI [10.1103/l4xt-3sxy](https://doi.org/10.1103/l4xt-3sxy),
describes Li core-excitation/autoionizing resonances in the 50–70 eV range in its
introduction. The source memo already excluded resonant atomic excitation and
excited-level kinetics. Thus the overly broad frozen-contract sentence is a
wording defect; the implemented smoothed ground-state continuum and its declared
exclusions are unchanged. The finite energy ledger validates retained processes
only. It does not bound heating/yield errors from excluded resonances.

The exact-zero unit gate refers to the retained direct-core contribution, not
to a measurement or a claim that all physical core excitations vanish. Unit final
electron yield applies to the admitted adjacent-charge ground-state channels.
THERM01 is not a complete physical ionic-yield closure even for all processes in
the 5–60 eV band, nor a full 5–200 eV model.

The next source/data work must account for in-band resonant channels as well as
the 60–200 eV correlated single/double-ionization and excitation partitions.
No new IVP is needed to correct this scope statement. Physical HOLD, REC U5
HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN,
production NOT_APPROVED, and REI_activation=false remain unchanged.
