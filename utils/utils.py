import subprocess


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
    subprocess.run(
        [f'podman run -d --name {container_name} -p 3128:3128 -v $(pwd)/squid.conf:/etc/squid/squid.conf:Z ubuntu/squid'],
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')


def clear_squid_logs(container_name='squid-proxy'):
    """Restart squid container to clear logs before test"""
    subprocess.run(['podman', 'restart', container_name], check=True)
    time.sleep(2)  # Wait for squid to start