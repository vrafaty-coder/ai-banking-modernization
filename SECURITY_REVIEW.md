# Pre-publication security review (static scan)

This is a limited heuristic scan, not a guarantee of no secrets or licensing issues.

{
  "file_count": 200,
  "collisions": [],
  "excluded": [],
  "secret_pattern_hits": [],
  "shell_checks": [
    {
      "file": "scripts/verify_java.sh",
      "ok": true,
      "error": ""
    },
    {
      "file": "scripts/verify_cobol.sh",
      "ok": true,
      "error": ""
    },
    {
      "file": "cobol/programs/run-tx02-tests.sh",
      "ok": true,
      "error": ""
    },
    {
      "file": "cobol/programs/run-tx01-tests.sh",
      "ok": true,
      "error": ""
    }
  ],
  "python_count": 36,
  "python_failures": [],
  "runner_has_temp_data_directory": true,
  "sensitive_or_out_of_scope_names": [],
  "zip_sources": [
    "1(1).zip",
    "2(1).zip"
  ]
}
