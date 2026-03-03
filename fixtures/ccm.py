import json
import pytest


@pytest.fixture(scope="session")
def central_config_data():
    with open('data/ccm.json', 'r') as file:
        json_list = json.load(file)
    return json_list