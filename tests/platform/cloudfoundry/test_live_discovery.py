import glob
import os
import shlex
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

    created = False
    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} to {repo_path}")
        subprocess.run(
            ["git", "clone", repo_url, repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        created = True
        print(f"Successfully cloned repository to {repo_path}")
    else:
        print(f"Repository already exists at {repo_path}, skipping clone")

    yield repo_path
    if created and os.path.exists(repo_path):
        shutil.rmtree(repo_path)

@pytest.fixture(scope="function")
def scp_cf_config_file():
    cf_files_path = os.getenv(constants.CLOUDFOUNDRY_FILES_PATH)
    cf_host = os.getenv(constants.CF_HOST)
    cf_user = os.getenv(constants.CF_USER)
    cf_remote_config_path = os.getenv(constants.CF_REMOTE_CONFIG_PATH)

    if not all([cf_files_path, cf_host, cf_user, cf_remote_config_path]):
        missing = []
        if not cf_files_path:
            missing.append("CLOUDFOUNDRY_FILES_PATH")
        if not cf_host:
            missing.append("CF_HOST")
        if not cf_user:
            missing.append("CF_USER")
        if not cf_remote_config_path:
            missing.append("CF_REMOTE_CONFIG_PATH")
        raise Exception(f"Required environment variables not set: {', '.join(missing)}")

    cf_private_key_file = os.path.join(cf_files_path, 'private_key')
    cf_local_config_path = os.path.join(cf_files_path, '.cf', 'config.json')
    if not os.path.exists(cf_private_key_file):
        raise Exception(f"Private key file not found: {cf_private_key_file}")

    ssh = None
    scp = None
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(
            hostname=cf_host,
            username=cf_user,
            pkey=RSAKey.from_private_key_file(cf_private_key_file),
        )

        scp = SCPClient(ssh.get_transport())
        scp.get(cf_remote_config_path, cf_files_path, recursive=True)

        if not os.path.exists(cf_local_config_path):
            raise Exception(f"Failed to scp Cloud Foundry config file to {cf_local_config_path}")

    finally:
        if scp:
            scp.close()
        if ssh:
            ssh.close()

    yield cf_local_config_path

    cf_config_dir = os.path.join(cf_files_path, '.cf')
    if os.path.exists(cf_config_dir):
        shutil.rmtree(cf_config_dir)

@pytest.mark.usefixtures("scp_cf_config_file", "clone_helm_chart_repo")
def test_cf_asset_generation_from_live_discovery():
    """
      Test end-to-end workflow: live discovery of CF application and asset generation.
      1. Downloads CF config via SCP
      2. Discovers CF application manifests
      3. Generates Helm charts from discovered manifests
      """
    repo_path = os.path.join(os.getenv(constants.CLOUDFOUNDRY_FILES_PATH), 'cf-k8s-helm-chart')
    discovery_output_dir = os.path.join(os.getenv(constants.CLOUDFOUNDRY_FILES_PATH), 'discovery')
    asset_dir = os.path.join(os.getenv(constants.CLOUDFOUNDRY_FILES_PATH), 'assets')

    discovery_command = build_platform_discovery_command(
        organizations=['org'],
        config=os.getenv(constants.CLOUDFOUNDRY_FILES_PATH),
        app_name='hello-spring-cloud',
        output_dir=discovery_output_dir
    )

    # Perform live discovery of Cloud Foundry(CF) application manifest
    # Input: CF application manifest, Output: Discovery manifest
    print(f"Running discovery command: '{discovery_command}'")
    discovery_output = subprocess.run(shlex.split(discovery_command), check=True, stdout=subprocess.PIPE,
        text=True).stdout
    assert 'Writing content to file' in discovery_output, "Discovery command failed"

    dir_path = Path(discovery_output_dir)
    assert dir_path.exists() and dir_path.is_dir(), f"Output directory '{dir_path}' was not created"

    yaml_files = glob.glob(f'{discovery_output_dir}/*.yaml')
    assert yaml_files, f"Discovery manifest was not generated in {discovery_output_dir}"
    print(f"Found {len(yaml_files)} discovery manifest(s)")

    # Generate assets after discovering CF application
    # Use the first generated YAML file as input
    input_manifest = yaml_files[0]
    chart_dir = os.path.join(repo_path, 'java-backend')
    print(f"Generating assets from {input_manifest}")
    asset_command = build_asset_generation_command(input_file=input_manifest, chart_dir=chart_dir, output_dir=asset_dir)

    print(f"Running asset generation command: '{asset_command}'")
    subprocess.run(shlex.split(asset_command), check=True, stdout=subprocess.PIPE, text=True)
    asset_files = glob.glob(f'{asset_dir}/*.yaml')
    assert asset_files, f"Assets were not generated in {asset_dir}"


