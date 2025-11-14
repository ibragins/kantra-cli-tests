"""
    Test Summary Utility
    Reads pytest JSON report and displays test results in a tabular format.
    Designed for both local runs and CI/CD systems like Jenkins.

    Usage:
        python utils/test_summary.py [json_report_file]

    Example:
        python utils/test_summary.py test-results/report.json
"""

import json
import sys
import os
from collections import defaultdict
from tabulate import tabulate

def debug(msg):
    """Print debug message and flush stdout (important for Windows Jenkins)."""
    print(f"[DEBUG] {msg}")
    sys.stdout.flush()

def print_summary(json_file="test-results/report.json"):
    """Load pytest JSON report and print summarized test results per spec."""
    debug(f"Starting summary. JSON file path: {json_file}")
    debug(f"Current working directory: {os.getcwd()}")
    debug(f"Python executable: {sys.executable}")
    # --- Load JSON report ---
    try:
        debug("Attempting to open JSON report file...")
        with open(json_file, "r") as f:
            data = json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"Error reading report file: {e}")
        sys.exit(1)

    tests = data.get("tests", [])
    debug(f"Total test entries in JSON: {len(tests)}")
    if not tests:
        print("No test data found in JSON report.")
        sys.exit(0)

    # --- Group results by spec file ---
    grouped = defaultdict(lambda: {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "other": 0
    })

    for t in tests:
        nodeid = t.get("nodeid", "")
        spec_name = nodeid.split("::")[0]
        outcome = t.get("outcome", "").lower()

        grouped[spec_name]["total"] += 1

        if outcome == "passed":
            grouped[spec_name]["passed"] += 1
        elif outcome in {"failed", "error"}:
            grouped[spec_name]["failed"] += 1
        elif outcome == "skipped":
            grouped[spec_name]["skipped"] += 1
        else:
            grouped[spec_name]["other"] += 1

    # --- Prepare rows for the table ---
    table_rows = []
    total_tests = total_passed = total_failed = total_skipped = total_other = 0

    for spec, stats in sorted(grouped.items()):
        total_tests += stats["total"]
        total_passed += stats["passed"]
        total_failed += stats["failed"]
        total_skipped += stats["skipped"]
        total_other += stats["other"]

        table_rows.append([
            spec,
            stats["total"],
            stats["passed"],
            stats["failed"],
            stats["skipped"],
            stats["other"],
        ])

    # --- Add final summary row ---
    if total_failed == 0:
        summary_label = "✓ ALL PASSED"
        summary_status = f"{total_passed}/{total_tests} tests passed"
    else:
        summary_label = "✗"
        summary_status = f"{total_failed}/{total_tests} tests failed"

    table_rows.append([
        f"{summary_label} {summary_status}",
        total_tests,
        total_passed,
        total_failed,
        total_skipped,
        total_other,
    ])
    debug(f"Total tests: {total_tests}, Passed: {total_passed}, Failed: {total_failed}, Skipped: {total_skipped}, Other: {total_other}")
    # --- Print formatted summary ---
    print("\n" + "=" * 80)
    print("TEST SUMMARY BY SPEC")
    print("=" * 80 + "\n")

    table_str = tabulate(
        table_rows,
        headers=["Spec", "Tests", "Passing", "Failing", "Skipped", "Other"],
        tablefmt="fancy_grid"
    )
    print(table_str)

    # --- Exit with failure code if any test failed or errored ---
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    debug("test_summary.py invoked directly.")
    report = sys.argv[1] if len(sys.argv) > 1 else "test-results/report.json"
    print_summary(report)