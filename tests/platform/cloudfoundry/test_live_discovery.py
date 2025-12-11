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

@pytest.fixture(scope="function")
def cleanup_output_directory():
    # Teardown: Delete the directory and its contents
    yield
    dir_path = Path(os.getenv(constants.ASSET_GENERATION_OUTPUT))
    print("DIR PATH", dir_path)
    if dir_path.exists():
        shutil.rmtree(dir_path)


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

def test_cf_asset_generation_from_live_discovery(scp_cf_config_file):
    output_dir = os.getenv(constants.ASSET_GENERATION_OUTPUT)

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

    # Run the asset generation command
    asset_output = subprocess.run(asset_command, shell=True, check=True, stdout=subprocess.PIPE,
        encoding='utf-8').stdout
    print(f"Asset generation output: {asset_output}")
    

