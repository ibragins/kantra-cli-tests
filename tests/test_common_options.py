import os
import subprocess

from utils import constants


# Polarion TC MTA-372
def test_list_targets():
    kantra_path = os.getenv(constants.KANTRA_CLI_PATH)
    command = kantra_path + ' analyze --list-targets'

    output = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout

    for i in ['hibernate-search5', 'eap', 'cloud-readiness', 'camel4', 'openjdk11', 'java-ee7', 'quarkus']:
        assert i in output, f"Target '{i}' not found in output."


# Polarion TC MTA-472
def test_list_targets_duplicates():
    kantra_path = os.getenv(constants.KANTRA_CLI_PATH)
    command = kantra_path + ' analyze --list-targets'

    output = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout

    targets = str.split(output, "\n")
    assert len(targets) == len(set(targets))


# Polarion TC MTA-372
def test_list_sources():
    kantra_path = os.getenv(constants.KANTRA_CLI_PATH)
    command = kantra_path + ' analyze --list-sources'

    output = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout

    for i in ['log4j', 'eap', 'springboot', 'openjdk11', 'java-ee', 'javaee', 'oraclejdk']:
        assert i in output, f"Source '{i}' not found in output."


# Polarion TC MTA-488
def test_list_sources_duplicates():
    kantra_path = os.getenv(constants.KANTRA_CLI_PATH)
    command = kantra_path + ' analyze --list-sources'

    output = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout

    sources = str.split(output, "\n")
    assert len(sources) == len(set(sources))


# Polarion TC MTA-596
def test_list_providers():
    kantra_path = os.getenv(constants.KANTRA_CLI_PATH)
    command = kantra_path + ' analyze --list-providers'

    output = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout

    for i in ['java', 'python', 'go', 'dotnet', 'nodejs']:
        assert i in output, f"Provider '{i}' not found in output."
