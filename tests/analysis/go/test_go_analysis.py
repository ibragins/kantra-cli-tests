import os

from utils.command import build_analysis_command, run_command_stream_output
from utils.common import get_project_path, verify_triggered_rules
from utils.report import assert_story_points_from_report_file, get_json_from_report_output_js_file


# Polarion TC MTA-533, MTA-544
def test_go_provider_analysis_with_app(golang_analysis_data):
    application_data = golang_analysis_data['golang_app']
    custom_rules_path = os.path.join(get_project_path(), 'data', 'yaml', 'golang-dep-rules.yaml')

    command = build_analysis_command(
        application_data['file_name'],
        application_data['sources'],
        application_data['targets'],
        **{'provider': "go",
            'rules': custom_rules_path,
           # "--run-local=false": None
           }
    )

    output = run_command_stream_output(command)

    assert 'Analysis complete!' in output
    assert_story_points_from_report_file()

    report_data = get_json_from_report_output_js_file()
    verify_triggered_rules(report_data, ['file-001'], expected_unmatched_rules=True)

