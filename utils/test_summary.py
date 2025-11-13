"""
Test Summary Utility (Spec-Level)
Groups pytest JSON report results by spec (test file) and prints
a clean summary table.
"""

import json
import sys
from collections import defaultdict
from tabulate import tabulate

# ANSI color codes
def color(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

GREEN = "92"
RED = "91"

def print_summary(json_file='test-results/report.json'):
    # Load pytest JSON report
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading report file: {e}")
        sys.exit(1)

    tests = data.get("tests", [])
    if not tests:
        print("No test data found in JSON report.")
        sys.exit(0)

    # Group results by spec (file path)
    grouped = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})
    for t in tests:
        nodeid = t.get("nodeid", "")
        spec_name = nodeid.split("::")[0]
        outcome = t.get("outcome", "").lower()

        grouped[spec_name]["total"] += 1
        if outcome == "passed":
            grouped[spec_name]["passed"] += 1
        elif outcome == "failed":
            grouped[spec_name]["failed"] += 1

    # Prepare table rows
    table_rows = []
    total_tests = total_passed = total_failed = 0

    for spec, stats in sorted(grouped.items()):
        total_tests += stats["total"]
        total_passed += stats["passed"]
        total_failed += stats["failed"]

        row = [
            spec,
            stats["total"],
            color(str(stats["passed"]), GREEN) if stats["passed"] else "0",
            color(str(stats["failed"]), RED) if stats["failed"] else "0",
        ]
        table_rows.append(row)

    # Prepare summary row
    if total_failed == 0:
        summary_icon = color("✓", GREEN)
        summary_text = f"{total_passed}/{total_tests} tests passed"
    else:
        summary_icon = color("✗", RED)
        summary_text = f"{total_failed}/{total_tests} tests failed"

    summary_row = [
        f"{summary_icon} {summary_text}",
        total_tests,
        color(str(total_passed), GREEN),
        color(str(total_failed), RED),
    ]
    table_rows.append(summary_row)

    # Generate the table as text
    table_str = tabulate(
        table_rows,
        headers=["Spec", "Tests", "Passing", "Failing"],
        tablefmt="fancy_grid"
    )

    table_lines = table_str.splitlines()
    enhanced_lines = []

    data_rows = table_rows[:-1]  # all rows except summary
    line_idx = 0

    for row_idx, _ in enumerate(data_rows):
        while line_idx < len(table_lines):
            enhanced_lines.append(table_lines[line_idx])
            if "├" in table_lines[line_idx] and "┼" in table_lines[line_idx]:
                if row_idx < len(data_rows) - 1:
                    enhanced_lines.append(table_lines[line_idx])
                line_idx += 1
                break
            line_idx += 1

    # Append remaining lines (summary row + bottom border)
    while line_idx < len(table_lines):
        enhanced_lines.append(table_lines[line_idx])
        line_idx += 1

    # Print final table
    print("\n" + "=" * 80)
    print("TEST SUMMARY BY SPEC")
    print("=" * 80 + "\n")
    print("\n".join(enhanced_lines))

    # Exit with proper code
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    report = sys.argv[1] if len(sys.argv) > 1 else "test-results/report.json"
    print_summary(report)