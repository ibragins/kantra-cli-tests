import os

from utils import constants
from utils.command import build_analysis_command, run_command_stream_output


# Polarion TC MTA-542
def test_nodejs_provider_analysis(nodejs_analysis_data):
    application_data = nodejs_analysis_data['nodejs_app_project']
    # TODO: replace with a nodejs rule when available and validate them
    custom_rules_path = os.path.join(os.getenv(constants.PROJECT_PATH), 'data/yaml', 'python_rules.yaml')
    command = build_analysis_command(
        application_data['file_name'],
        application_data['sources'],
        application_data['targets'],
        **{'rules': custom_rules_path,
           'provider': "nodejs"}
    )

    output = run_command_stream_output(command)

    assert 'Analysis complete!' in output
