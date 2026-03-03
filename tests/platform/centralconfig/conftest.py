"""Create hub entities before central config tests; cleanup when the run is completed."""
import os
import subprocess
import pytest


def _project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, "..", "..", ".."))


@pytest.fixture(scope="session", autouse=True)
def ensure_hub_entities():
    """Run create-entities.sh once before any central config test in this directory."""
    project_root = _project_root()
    script_path = os.path.join(project_root, "scripts", "create-entities.sh")
    if not os.path.isfile(script_path):
        pytest.skip(f"create-entities.sh not found at {script_path}")
    result = subprocess.run(
        [script_path],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        pytest.fail(
            f"create-entities.sh failed (exit {result.returncode})\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


@pytest.fixture(scope="session", autouse=True)
def cleanup_hub_entities_after_run():
    """Run cleanup-hub-entities.sh when central config test run is completed."""
    yield
    project_root = _project_root()
    script_path = os.path.join(project_root, "scripts", "cleanup-hub-entities.sh")
    if not os.path.isfile(script_path):
        return
    subprocess.run(
        [script_path],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
