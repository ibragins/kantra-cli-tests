import os

from utils import constants
from utils.command import build_analysis_command, run_command_stream_output
from utils.common import verify_triggered_yaml_rules
from utils.report import assert_story_points_from_report_file, get_dict_from_output_yaml_file

# Polarion TC MTA-536, 543
def test_java_provider_analysis(analysis_data):

    application_data = analysis_data['tackle-testapp-project']

    custom_rules_path = os.path.join(os.getenv(constants.PROJECT_PATH), 'data/yaml', '01-javax-package-custom-target.windup.yaml')
    command = build_analysis_command(
            application_data['file_name'],
            application_data['sources'],
            application_data['targets'],
            **{'provider': "java",
               'rules': custom_rules_path}
        )

    output = run_command_stream_output(command)

    assert 'analysis complete' in output.lower(), "Expected 'Analysis complete!' in Kantra output"
    
    assert_story_points_from_report_file()

    report_data = get_dict_from_output_yaml_file()

    verify_triggered_yaml_rules(report_data, ['javax-package-custom-target-00001'], True)

