import os

import pytest
from deepdiff import DeepDiff

import utils.common
from fixtures.analysis import ci_data
from utils.command import build_analysis_command, run_command_stream_output
from utils.output import normalize_output
from utils.report import assert_story_points_from_report_file, get_dict_from_output_yaml_file

# Covered by koncur tests/book-server-source and tests/book-server-deps.
_KONCUR_DUPLICATED_CASES = frozenset({"book-server_source", "book-server_deps"})


@pytest.mark.parametrize("application_data", ci_data(),
                         ids=lambda case: f"{case['name']}")
def test_bvp_issue_analyzer_901(application_data):
    if application_data["name"] in _KONCUR_DUPLICATED_CASES:
        pytest.skip(
            "Covered by koncur tests/book-server-source and tests/book-server-deps"
        )

    reference_data_path = os.path.join(
        utils.common.get_project_path(),
        "data", "ci", "shared_tests", application_data['referencesDir']
    )

    command = build_analysis_command(
        application_data['filename'],
        application_data['sources'],
        application_data['targets'],
        with_deps=application_data["withDeps"]
    )

    output = run_command_stream_output(command)

    assert 'analysis complete' in output.lower(), "Expected 'Analysis complete!' in Kantra output"
    assert_story_points_from_report_file()

    # Parsing report and reference
    report_data = normalize_output(
        get_dict_from_output_yaml_file(),
        os.path.join(utils.common.get_project_path(), 'data', 'applications', application_data['filename'])
    )
    reference_data = get_dict_from_output_yaml_file(
        filename="output.yaml",
        report_path=reference_data_path
    )

    reference_data = normalize_output(
        reference_data,
        os.path.join(utils.common.get_project_path(), 'data', 'applications', application_data['filename'])
    )

    diff = DeepDiff(report_data, reference_data, ignore_order=True)
    errors = []
    if len(report_data) != len(reference_data):
        report_names = [item.get('name', f"Unnamed_Index_{i}") for i, item in enumerate(report_data) if
                        isinstance(item, dict)]
        reference_names = [item.get('name', f"Unnamed_Index_{i}") for i, item in enumerate(reference_data) if
                           isinstance(item, dict)]

        errors.append(
            f"Mismatch in reports length:\n"
            f"\nReport length: {len(report_data)}. "
            f"Found technology names:\n{', '.join(report_names) if report_names else 'None'}\n"
            f"\nReference report length: {len(reference_data)}. "
            f"Found technology names:\n{', '.join(reference_names) if reference_names else 'None'}"
        )
    if diff != {}:
        errors.append(f"Mismatch in name/violations:\n{diff.pretty()}")
    if errors:
        error_message = "The following rule validation errors occurred:\n" + "\n".join(errors)
        print(f"Failed assertions: {error_message}")
        raise AssertionError(error_message)