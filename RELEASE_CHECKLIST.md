# Pre-publication checklist (updated 2026-11-14)

- [x] Canonical Java dependencies grouped by package (previous staging review).
- [x] Historical generated source and human adjudication preserved.
- [x] GnuCOBOL TX01 T01–T07: user-reported PASS on Windows with GnuCOBOL 3.2.0.
- [x] GnuCOBOL TX02 T01–T07: user-reported PASS on Windows with GnuCOBOL 3.2.0.
- [x] Isolated runner creates a disposable `data` directory.
- [x] Static heuristic scan for common credential patterns (see SECURITY_REVIEW.md).
- [ ] Manually review all data, prompts, licenses, and commit history before public push.
- [ ] Verify regression programs exit nonzero on assertion failure; PASS output alone is insufficient.
- [x] Java Validation Gates rerun on V4 staging tree: TX01 60 PASS + 4 NOT_EVALUABLE; TX02 64 PASS.
- [ ] Re-run COBOL tests on the exact V4 tree and capture logs (previous user run was on V2).
- [ ] Freeze Python dependencies and confirm optional API-free reproduction instructions.
- [ ] Choose a license; confirm repository release URL, tag, commit and version; update CITATION.cff and paper.
