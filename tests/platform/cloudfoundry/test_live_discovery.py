import glob
import os
import subprocess
import pytest
import shutil
from pathlib import Path
from paramiko import SSHClient, RSAKey
from scp import SCPClient

from utils import constants
from utils.command import build_platform_discovery_command, build_asset_generation_command

@pytest.fixture(scope="session")
def clone_helm_chart_repo():
    """
    Clone the cf-k8s-helm-chart repository to the location specified by CLOUDFOUNDRY_FILES_PATH.
    If the repository already exists, it will be skipped.
    """
    cf_files_path = os.getenv(constants.CLOUDFOUNDRY_FILES_PATH)
    if not cf_files_path:
        raise Exception("CLOUDFOUNDRY_FILES_PATH environment variable is not set")

    repo_url = "https://github.com/konveyor/cf-k8s-helm-chart"
    repo_name = "cf-k8s-helm-chart"
    repo_path = os.path.join(cf_files_path, repo_name)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} to {repo_path}")
        subprocess.run(
            ["git", "clone", repo_url, repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Successfully cloned repository to {repo_path}")
    else:
        print(f"Repository already exists at {repo_path}, skipping clone")

    yield repo_path
    if os.path.exists(repo_path):
       shutil.rmtree(repo_path)

@pytest.fixture(scope="function")
def scp_cf_config_file():
    # TO DO: Remove hard coded values
    private_key_file = os.path.join(os.getenv(
        constants.CLOUDFOUNDRY_FILES_PATH), 'private_key')
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(
        hostname="11.22.33.44",
        username="fedora",
        pkey=RSAKey.from_private_key_file(private_key_file),
    )

    scp = SCPClient(ssh.get_transport())
    scp.get("/home/fedora/.cf/config.json", Path(os.getenv(constants.CLOUDFOUNDRY_FILES_PATH)))

    scp.close()
    ssh.close()

def test_cf_asset_generation_from_live_discovery(scp_cf_config_file, clone_helm_chart_repo):
    output_dir = os.getenv(constants.CLOUDFOUNDRY_FILES_PATH)
    asset_dir = os.path.join(os.getenv(constants.CLOUDFOUNDRY_FILES_PATH), 'assets')

    command = build_platform_discovery_command(
        organizations=['org'],
        spaces=['space'],
        app_name='hello-spring-cloud',
        output_dir=output_dir
    )

    # Perform live discovery of Cloud Foundry(CF) application manifest
    # Input: CF application manifest, Output: Discovery manifest
    output = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
        encoding='utf-8').stdout
    assert 'Writing content to file' in output, f"Discovery command failed"

    dir_path = Path(output_dir)
    assert dir_path.exists() and dir_path.is_dir(), f"Output directory '{dir_path}' was not created"

    yaml_files = glob.glob(f'{output_dir}/*.yaml')
    assert yaml_files, f"Discovery manifest was not generated in {output_dir}"

    # Generate assets after discovering CF application
    # Use the first generated YAML file as input
    input_manifest = yaml_files[0]
    asset_command = build_asset_generation_command(input_file=input_manifest)

    asset_output = subprocess.run(asset_command, shell=True, check=True, stdout=subprocess.PIPE,
        encoding='utf-8').stdout
    asset_files = glob.glob(f'{asset_dir}/*.yaml')
    assert yaml_files, f"Assets were not generated in {asset_dir}"


