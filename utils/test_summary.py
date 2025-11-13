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

USE_COLOR = sys.stdout.isatty() and os.environ.get("TERM") != "dumb"

def color(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text

green = lambda text: color(text, "32")
red = lambda text: color(text, "31")
bold = lambda text: color(text, "1")


def print_summary(json_file="test-results/report.json"):
    """Load pytest JSON report and print summarized test results per spec."""
    # --- Load JSON report ---
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as e:
        print(f"Error reading report file: {e}")
        sys.exit(1)

    tests = data.get("tests", [])
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
            green(stats["passed"]) if stats["passed"] else "0",
            red(stats["failed"]) if stats["failed"] else "0",
            stats["skipped"],
            stats["other"],
        ])

    # --- Add final summary row ---
    if total_failed == 0:
        summary_icon = green("✓")
        summary_text = bold(green(f"{total_passed}/{total_tests} tests passed"))
    else:
        summary_icon = red("✗")
        summary_text = bold(red(f"{total_failed}/{total_tests} tests failed"))

    table_rows.append([
        f"{summary_icon} {summary_text}",
        total_tests,
        green(total_passed),
        red(total_failed),
        total_skipped,
        total_other,
    ])

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
    report = sys.argv[1] if len(sys.argv) > 1 else "test-results/report.json"
    print_summary(report)