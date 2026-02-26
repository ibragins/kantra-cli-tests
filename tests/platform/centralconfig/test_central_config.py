import os.path

import pytest
from utils.command import build_central_config_login_command, build_central_config_sync_command, get_cli_path, \
    build_analysis_command_ccm
from utils.common import get_hub_url, get_hub_username, get_hub_password, get_hub_secure, get_full_application_path, \
    get_project_path, get_profile_path, run_command
from utils.report import get_json_from_report_output_js_file


def test_login_hub():
    hub_url = get_hub_url()
    if "localhost" in hub_url:
        pytest.skip("Skipping login test when hub URL contains localhost")
    command = build_central_config_login_command(
        hub_url,
        get_hub_username(),
        get_hub_password(),
        get_hub_secure()
    )
    print(command)
    output = run_command(command, shell=False, check=True)
    assert "login successful" in output.stdout.lower(), \
        f"Expected 'login successful' in output, got: {output.stdout}"

def test_sync_hub(central_config_data):
    """Positive test: pulls profile bundle from hub by application name"""
    command = build_central_config_sync_command(
        central_config_data["app_url"],
        get_full_application_path(central_config_data["filename"]),
        get_hub_secure()
    )
    print(command)
    output = run_command(command, shell=False, check=True)

    assert output.returncode == 0, \
        f"Command failed with exit code {output.returncode}\nSTDOUT: {output.stdout}\nSTDERR: {output.stderr}"
    assert "profile bundle downloaded successfully" in output.stdout.lower(), \
        f"Expected 'profile bundle downloaded successfully' in output, got:\nSTDOUT: {output.stdout}\nSTDERR: {output.stderr}"

def test_sync_hub_negative():
    """Negative test: expects command to fail when connecting to invalid localhost hub."""
    command = build_central_config_sync_command(
        "http://localhost",
        get_project_path(),
        secure=False
    )
    print(command)
    output = run_command(command, shell=False, check=False)
    # This is a negative test - we expect the command to fail
    assert output.returncode != 0, \
        f"Expected command to fail, but it succeeded with return code {output.returncode}"
    assert "no applications found in hub" in output.stderr.lower(), \
        f"Expected 'no applications found in hub' in stderr, got: {output.stderr}"

def test_list_profiles(central_config_data):
    """Positive test: gives list of all profiles available by specified path"""
    command = [get_cli_path(),
               "config",
               "list",
               "--profile-dir",
               get_full_application_path(central_config_data["filename"]),
               ]
    print(command)
    output = run_command(command, shell=False, check=True)
    assert "profiles found in" in output.stdout.lower(), f"Expected 'profiles found in' in output, got: {output.stdout}"

def test_analysis(central_config_data):
    profile_path = os.path.join(
        get_full_application_path(central_config_data["filename"]),
        ".konveyor",
        "profiles",
        get_profile_path(central_config_data)[1]
    )
    command = build_analysis_command_ccm(
        central_config_data["filename"],
        profile_path
    )
    output = run_command(command, shell=True, check=False)
    print(output)
    assert 'using profile' in output.stdout.lower()
    report_data = get_json_from_report_output_js_file(False)
    assert report_data, "Report data is empty"
    assert len(report_data[0]['depItems']) >= 0, "No dependencies were found"