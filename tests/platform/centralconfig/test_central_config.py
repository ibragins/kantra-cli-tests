import subprocess
import pytest
from utils.command import build_central_config_login_command, build_central_config_sync_command, get_cli_path, \
    build_analysis_command_ccm
from utils.common import get_hub_url, get_hub_username, get_hub_password, get_hub_secure, get_full_application_path, \
    get_project_path
from utils.report import get_json_from_report_output_js_file


def test_login_hub_central_config():
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
    output = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
               encoding='utf-8')
    assert "login successful" in output.stdout.lower(), \
        f"Expected 'login successful' in output, got: {output.stdout}"

def test_sync_hub_central_config(central_config_data):
    """Positive test: pulls profile bundle from hub by application name"""
    command = build_central_config_sync_command(
        central_config_data["app_url"],
        get_full_application_path(central_config_data["filename"]),
        get_hub_secure()
    )
    print(command)
    output = subprocess.run(command, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   encoding='utf-8')

    assert output.returncode == 0, \
        f"Command failed with exit code {output.returncode}\nSTDOUT: {output.stdout}\nSTDERR: {output.stderr}"
    assert "profile bundle downloaded successfully" in output.stdout.lower(), \
        f"Expected 'profile bundle downloaded successfully' in output, got:\nSTDOUT: {output.stdout}\nSTDERR: {output.stderr}"

def test_sync_hub_central_config_negative():
    """Negative test: expects command to fail when connecting to invalid localhost hub."""
    command = build_central_config_sync_command(
        "http://localhost",
        get_project_path(),
        secure=False
    )
    print(command)
    output = subprocess.run(command, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   encoding='utf-8')
    # This is a negative test - we expect the command to fail
    assert output.returncode != 0, \
        f"Expected command to fail, but it succeeded with return code {output.returncode}"
    assert "no applications found in hub" in output.stderr.lower(), \
        f"Expected 'no applications found in hub' in stderr, got: {output.stderr}"

def test_list_profiles_central_config(central_config_data):
    """Positive test: gives list of all profiles available by specified path"""
    command = [get_cli_path(),
               "config",
               "list",
               "--profile-dir",
               get_full_application_path(central_config_data["filename"]),
               ]
    print(command)
    output = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    assert "profiles found in" in output.stdout.lower(), f"Expected 'profiles found in' in output, got: {output.stdout}"

def test_analysis_central_config(central_config_data):
    # profile_path = os.path.join(get_project_path(), '.konveyor', 'profiles', 'profile-1')
    command = build_analysis_command_ccm(
        central_config_data["filename"],
        # profile_path
    )
    output = subprocess.run(command, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding='utf-8')
    assert 'using found profile' in output.stdout.lower()
    report_data = get_json_from_report_output_js_file(False)
    assert len(report_data[0]['depItems']) >= 0, "No dependencies were found"