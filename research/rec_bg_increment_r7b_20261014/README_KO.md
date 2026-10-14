# REC R7B positive background increments

Read THEORY_KO.md, CODEX_HANDOFF_KO.md, RESULT_SUMMARY.json and SUPPLIER_DAG.json.

This is an independent theory/prototype supplier. Ideal relative integral error is uniformly <3.080731e-10/1.921401e-11 at1024/2048cells in the stated positive-density background.21tests and804interval comparisons passed. Computed roundoff/trajectory bounds and native adoption remain separate. No production solver or canonical STATE/source mutation.

Core code uses Python3.10+ standard library. Run `python3 -m unittest discover -s code -p 'test_increment.py' -v`. Optional `python3 code/validate_numeric.py` uses mpmath1.3.0 and writes new results; use a separate copy.

Existing stable primitive increments had already passed the previous component gate. This adds a rate-first uniform interpolation bound and one shared clock/shear surrogate, not a claim to have first fixed stable subtraction. Exact-cache work remains under its own unchanged contract. Full signed-family/half-amplitude/refinement analyses are not completed here.
