# REC-DONOR-02 bounded source implementation

Parent: 2dfd464efe91b319993e6c6759d380d53d0f3fde.
Parent tree: 0fdb8bf0904df05ef5b495f3f0b19e5c4444a886.
The operator independently fetched that exact parent. The previous response's
998-addition count was wrong: the Git object and operator both report 1781.

## Plan frozen before implementation

1. Execute the inherited 16 tests and the new 11 safety tests on this test-only
   child. Require 27 tests, 22 assertion failures, five controls, no errors/skips.
2. Add only src/full_bianchi_hyrec/physical_source_authority.py in production.
   Use the standard library, immutable metadata, factory-created sources,
   internally computed semantic hashes and explicit non-admission flags.
3. Migrate only the old absence control and the invalid threshold fixture.
   Preserve all other inherited assertions, including the disputed deposition
   success assertion. Do not mark that assertion xfail or catch its error.
4. Run the same exact-head suite; no broad tests, backend provisioning or
   physical trajectory. The anticipated bounded result is 26 passes and one
   DepositionAuthorityError from the inherited metadata-only success demand.
5. Preserve the non-GREEN result and stop. Never advertise 27/27 or donor GREEN.

## Reproduced mathematical contract defects

P1 threshold fixture: eta=1/4, kappa=3/4, f=1/2 gives C=0 even inside support.
Its assertNotEqual(C,0) cannot test support admission. Use f=2 at every tested
energy and exact expected interior C=-3/4, not a wider tolerance. The source
law and the half-open energy interval remain unchanged. An independent
Fraction control records both the null fixture and its non-equilibrium repair.

P1 deposition: the old binding supplies n_H, one scalar measure and two hashes,
not the matrix B, packet channel basis, target layout or an authenticated
resolver. The advertised calculation n_H/mu_i sum_s B_is R_s cannot be executed
from that binding. application_count=1 is a caller declaration, not evidence
that any operation ran. The implementation must reject unresolved deposition;
its inherited success test must remain non-green rather than return a sham
receipt. A separate safety test asserts that rejection.

## Claim boundaries

The local affine law is an executable manufactured protocol, not an admitted
HyRec data source. A linear companion-weighted packet probe is only a
MANUFACTURED_LINEAR_PACKET_PROBE; the label TWO_PHOTON or RAMAN does not turn
it into the corresponding nonlinear physical kernel. SourceProvenance records
DECLARED_NOT_AUTHENTICATED. Moment-map and angular bindings do not execute
projection, certify a basis or supply a closure. No source admission, deposition
execution, physical face, BASS/REI wiring, provider export, merge or ready state.
No change to inherited immutable evidence, harness policy or historical manifests.

## Runtime and review

Native ChatGPT container.exec and python both returned ClientError before
execution. Connected WolframContext and WolframLanguageEvaluator each returned
HTTP 502 before a kernel result. They are unavailable axes, not mathematical
failures. GitHub-hosted exact-source execution is the planned execution lane.
The PHYS-MATH and PHYS-MATH-CODE readings are separate checks by the same
assistant, not independent reviewers. Independent final review remains withheld.

## Literature role

SciSpace retrieved Ali-Haimoud & Hirata, PRD 83, 043513 (2011),
arXiv:1011.3758v2, and Hirata, PRD 78, 023001 (2008), arXiv:0803.0808v2.
Primary abstract readbacks confirm joint radiation/population evolution and
radiative-transfer treatment of two-photon/Raman processes. They do not certify
this proposed Python protocol or supply its deposition matrix. Authority effect:
NONE_METHOD_AND_SCOPE_ONLY. Attached TEFF Papers I and II remain static
coarse-graining diagnostics, not recombination closures.

## Completion accounting

Do not infer physical-provider completion from tests or metadata node counts.
Report the local-source implementation, raw suite outcome, unresolved
operator, and absent integrated run separately. Previous project-wide
40-45% and 10-15% estimates lacked a frozen weighted denominator and are withdrawn.

## Next action after the bounded implementation

REC-DONOR-02B_RESOLVED_PACKET_DEPOSITION_CONTRACT:
resolve an actual repository-owned B[target,packet] payload and target measure,
bind it to kernel/channel/state identities, and test its numerical action
against an independent two-channel oracle. Until that contract exists,
UNRESOLVED_DEPOSITION_OPERATOR is the correct runtime refusal.
