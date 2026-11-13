# Canonical research source

This release-support package was generated outside the user's Windows development machine, so it does not invent replacements for canonical experiment files that exist only in the local project.

Before the final GitHub push, run `tools/package_existing_project.py` **from the canonical EvoNIDS project root**. The script copies the real `research/` implementation, tests and result directories into the clean submission folder while excluding caches and machine-specific files.

Expected canonical modules include:

- `research/src/run_fair_budget_suite.py`
- `research/src/run_nsga2_suite.py`
- `research/src/run_full_feature_baselines.py`
- `research/src/analyse_final_results.py`
- `research/src/statistical_analysis.py`
- `research/src/build_final_report_tables.py`
- `research/src/evaluate_feature_subset.py`
- `research/src/models/`
- `research/src/utils/`
- `research/tests/`

The final GitHub repository should contain those actual files, not reconstructed approximations.
