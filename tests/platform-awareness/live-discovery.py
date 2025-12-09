import glob
import os
import subprocess
import pytest
import shutil
from pathlib import Path

from utils import constants
from utils.command import build_platform_discovery_command

@pytest.fixture(scope="function")
def cleanup_output_directory():
    # Teardown: Delete the directory and its contents
    yield
    dir_path = Path(os.getenv(constants.ASSET_GENERATION_OUTPUT))
    print("DIR PATH", dir_path)
    if dir_path.exists():
        shutil.rmtree(dir_path)

# Polarion TC MTA-617
def test_cf_asset_generation_from_live_discovery(cleanup_output_directory):
    input_yaml = os.path.join(os.getenv(
        constants.PROJECT_PATH), 'data', 'yaml', 'asset_generation')
    output_dir = os.getenv(constants.ASSET_GENERATION_OUTPUT)

    command = build_platform_discovery_command(input_yaml,
        **{'output-dir': output_dir}
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
