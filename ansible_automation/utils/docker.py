import subprocess


def is_docker_running():
    """
    Check if Docker daemon is running.

    Returns
    -------
    bool
        True if Docker daemon is running, False otherwise.
    """
    try:
        subprocess.run(
            ['docker', 'info'], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def is_container_running(container_name):
    """
    Check if a Docker container is running.

    Parameters
    ----------
    container_name : str
        Name of the Docker container.

    Returns
    -------
    bool
        True if the container is running, False otherwise.
    """
    try:
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Running}}', container_name], capture_output=True, text=True, check=True,
        )
        return result.stdout.strip() == 'true'
    except subprocess.CalledProcessError:
        return False


def start_container(container_name, compose_file, build=True):
    """
    Start a Docker container using docker compose.

    Parameters
    ----------
    container_name : str
        Name of the Docker container to start.
    compose_file : str
        Path to the docker compose file.

    Returns
    -------
    None
    """
    command = f'docker compose -f {compose_file} up -d' + \
        (' --build' if build else '')
    try:
        subprocess.run(command, shell=True, check=True)
        print(f'The container {container_name} has been started.')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while starting the container: {e}')


def stop_container(container_name, compose_file):
    """
    Stop a Docker container using docker compose.

    Parameters
    ----------
    container_name : str
        Name of the Docker container to stop.
    compose_file : str
        Path to the docker compose file.

    Returns
    -------
    None
    """
    command = f'docker compose -f {compose_file} down'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f'The container {container_name} has been started.')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while starting the container: {e}')


def ensure_container_running(container_name, compose_file, build=True):
    """
    Ensure that a Docker container is running. If not, start it.

    Parameters
    ----------
    container_name : str
        Name of the Docker container.
    compose_file : str
        Path to the docker compose file.

    Returns
    -------
    None
    """
    if not is_container_running(container_name):
        start_container(container_name, compose_file, build)
    else:
        print(f'The container {container_name} is already running.')
