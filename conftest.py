import time
import pytest
from dotenv import load_dotenv

pytest_plugins = [
    "fixtures.analysis",
    "fixtures.transformation",
    "fixtures.ccm",
]


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()

_run_started_at: dict[str, float] = {}


def pytest_runtest_logstart(nodeid, location):
    # Unconditionally skipped tests never run pytest_runtest_setup but still
    # run pytest_runtest_teardown; logstart always runs for each collected item.
    _run_started_at[nodeid] = time.perf_counter()


def pytest_runtest_teardown(item):
    started = _run_started_at.pop(item.nodeid, None)
    if started is not None:
        duration = time.perf_counter() - started
        print(f"\nTest {item.name} took {duration:.4f} seconds")