import os
import subprocess
import time
from pathlib import Path
from utils import constants

def get_squid_logs(container_name='squid-proxy'):
    """Fetch logs from squid proxy container"""
    result = subprocess.run(
        ['podman', 'logs', container_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8'
    )
    return result.stdout


def start_squid_container(container_name='squid-proxy'):
    """Start squid proxy container"""
    project_root = Path(os.getenv(constants.PROJECT_PATH))
    config_path = project_root / 'squid' / 'squid.conf'

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    stop_squid_container(container_name)

    cmd = [
        'podman', 'run', '-d',
        '--name', container_name,
        '-p', '3128:3128',
        '-v', f'{config_path}:/etc/squid/squid.conf:Z',
        'ubuntu/squid'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Container started ID: {result.stdout.strip()}")

    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e.stderr}")
        raise


def stop_squid_container(container_name='squid-proxy'):
    """Stop squid proxy container"""
    subprocess.run(['podman', 'rm', '-f', container_name],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def clear_squid_logs(container_name='squid-proxy'):
    """Restart squid container to clear logs before test"""
    subprocess.run(['podman', 'restart', container_name], check=True)
    time.sleep(2)  # Wait for squid to start