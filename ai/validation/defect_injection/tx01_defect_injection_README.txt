TX01 Controlled Defect Injection — Experimental Run

Run: python run_tx01_defect_injection.py
Requires Java JDK 17+ and Python 3.
Input Java files and Tx01ValidationGateV3.java must be in the same directory as the Python runner.

This experiment tests whether V3 detects FIVE deliberately introduced defects, each in a temporary compiled copy. The original generated Java is never edited.
Detection is defined as the targeted scenario receiving FAIL in at least one V3 dimension.
Results are source-oracle based; no executable COBOL reference was run.
The BUSINESS_RULE dimension in V3 is a composite, not independent evidence.
NOT_EVALUABLE scenarios are excluded from detection counts.
The test suite may have additional blind spots; these five mutants do not prove comprehensive mutation adequacy.
