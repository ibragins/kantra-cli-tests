import subprocess
from utils.command import build_central_config_login_command, build_central_config_sync_command


def test_login_hub_central_config(central_config_data):
    command = build_central_config_login_command(
        central_config_data["hub_url"],
        central_config_data["hub_username"],
        central_config_data["hub_password"],
        central_config_data["secure"]
    )
    print(command)
    output = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   encoding='utf-8')
    print(output.stdout)

    assert "login successful" in output.stdout.lower(), \
        f"Expected 'login successful' in output, got: {output.stdout}"

def test_sync_hub_central_config(central_config_data):
    command = build_central_config_sync_command(central_config_data["app_url"], central_config_data["secure"])
    print(f"Running command: {command}")
    output = subprocess.run(command, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   encoding='utf-8')
    print(f"Return code: {output.returncode}")
    print(f"STDERR: {output.stderr}")

    assert output.returncode == 0, \
        f"Command failed with exit code {output.returncode}\nSTDOUT: {output.stdout}\nSTDERR: {output.stderr}"
    assert "profile bundle downloaded successfully" in output.stdout.lower(), \
        f"Expected 'profile bundle downloaded successfully' in output, got:\nSTDOUT: {output.stdout}\nSTDERR: {output.stderr}"

def test_sync_hub_central_config_negative():
    """Negative test: expects command to fail when connecting to invalid localhost hub."""
    command = build_central_config_sync_command("http://localhost", secure=False)
    print(f"Running command: {command}")
    output = subprocess.run(command, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   encoding='utf-8')
    print(f"Return code: {output.returncode}")
    print(f"STDOUT: {output.stdout}")
    print(f"STDERR: {output.stderr}")

    # This is a negative test - we expect the command to fail
    assert output.returncode != 0, \
        f"Expected command to fail, but it succeeded with return code {output.returncode}"
    assert "no applications found in hub" in output.stderr.lower(), \
        f"Expected 'no applications found in hub' in stderr, got: {output.stderr}"