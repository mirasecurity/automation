import argparse
import datetime
import json
import logging as log
import os
import re

from utils.ansible import ansible_add_to_inventory_executor
from utils.ansible import ansible_log_writer_analyzer
from utils.ansible import ansible_run_check
from utils.ansible import ansible_ssh_key_exist
from utils.ansible import ansible_ssh_keys_generate
from utils.cloud_init import cloud_init_sha512_crypt
from utils.cloud_init import generate_random_salt
from utils.docker import ensure_container_running
from utils.docker import is_docker_running
from utils.docker import stop_container
from utils.utils import colors
from utils.utils import setup_logging

docker_name = 'ansible_automation'


def builder_func(build_options, install_log_name, log_level, use_docker=True):
    """
    Execute a series of build steps based on provided options.

    Parameters
    ----------
    build_options : list
        A list of dictionaries containing build options.
    install_log_name : str
        The name of the installation log file.
    log_level : str
        The logging level.

    Returns
    -------
    None

    Notes
    -----
    This function executes a series of build steps based on the provided `build_options`.
    For each build option, it performs various tasks such as configuring hypervisors,
    installing required packages, executing build scripts, and setting up virtual machines.
    The function logs each step and checks for failures using the `ansible_log_writer_analyzer`
    and `ansible_run_check` functions. If a failure occurs, the function logs an error message
    and returns False. Otherwise, it returns True upon successful completion.
    """
    log_check_bool = []

    for build in build_options:
        # -- Hypervisor
        hypervisor_hostname = build.get('hypervisor_hostname')
        hypervisor_username = build.get('hypervisor_username')
        hypervisor_password = build.get('hypervisor_password')

        # -- VM Configuration
        hypervisor_vm_image_loc = build.get('hypervisor_vm_image_loc')
        hypervisor_dest_directory = build.get('hypervisor_dest_directory')
        vm_qcow_name = build.get('vm_qcow_name')
        vm_vcpus = build.get('vm_vcpus', 8)
        vm_memory = build.get('vm_memory', 16384)
        vm_os_variant = build.get('vm_os_variant', 'centos7.0')
        vm_boot = build.get('vm_boot', 'hd,cdrom')
        vm_cpu = build.get('vm_cpu', 'host')
        vm_source = build.get('vm_source')
        vm_model = build.get('vm_model')
        vm_source_mode = build.get('vm_source_mode', 'bridge')

        vm_network_net_a = build.get('vm_network_net_a')
        vm_network_net_b = build.get('vm_network_net_b')

        vm_network_app_a = build.get('vm_network_app_a')
        vm_network_app_b = build.get('vm_network_app_b')

        vm_network_mir_a = build.get('vm_network_mir_a')
        vm_network_mir_b = build.get('vm_network_mir_b')

        vm_hostname = build.get('vm_hostname')
        vm_password = build.get('vm_password')
        vm_hashed_password = cloud_init_sha512_crypt(
            vm_password, salt=generate_random_salt(), rounds=5000,
        )
        vm_hashed_password = vm_hashed_password.replace('$', '\\$')

        vm_old_password = build.get('vm_old_password')
        vm_username = build.get('vm_username', 'root')

        # ETO Network configuration
        vm_static_ip_address = build.get('vm_static_ip_address')
        vm_ip_gateway = build.get('vm_ip_gateway')
        vm_ip_netmask = build.get('vm_ip_netmask')
        vm_dns_server_1 = build.get('vm_dns_server_1')
        vm_dns_server_2 = build.get('vm_dns_server_2')

        # ETO API Config
        vm_api_username = build.get('vm_api_username')
        vm_allow_enrollment = build.get('vm_allow_enrollment')

        if vm_static_ip_address is None:
            log.info('Cannot connect to ETO unless a static IP is provided, please note that the default settings for the API will have to be changed manually')

        # Check if it was not successfully added to the inventory
        if not ansible_add_to_inventory_executor(
            hostname=hypervisor_hostname,
            username=hypervisor_username,
            password=hypervisor_password,
            use_docker=use_docker,
            docker_name=docker_name,
            install_log_name=install_log_name,
            log_level=log_level,
        ):
            raise Exception(
                f'Something went wrong when adding {hypervisor_hostname} to the inventory',
            )

        log.info('Step 1: Add the SSH keys')
        # Step 1: Add the SSH keys
        log_check_bool.append(
            ansible_log_writer_analyzer(
                install_log_name, 'echo Adding SSH Keys',
            ),
        )
        make_sure_ssh_available = f'ansible-playbook playbooks/ssh_setup_individual.yml --extra-vars "hypervisor_username={hypervisor_username} hypervisor_password={hypervisor_password} hypervisor_hostname={hypervisor_hostname}"'
        ssh_docker_command = f'docker exec -t {docker_name} {make_sure_ssh_available}'
        log_check_bool.append(
            ansible_log_writer_analyzer(
                install_log_name, ssh_docker_command, log_level,
            ),
        )

        # If failed exit the loop
        if ansible_run_check(log_check_bool):
            log.error('Failed Step 1')
            break

        log.info('Step 2: Install required packages and dependencies')
        log_check_bool.append(
            ansible_log_writer_analyzer(
                install_log_name, 'echo Installing requirements',
            ),
        )
        install_required_packages = f'ansible-playbook playbooks/setup.yml --extra-vars \
            "hypervisor_hostname={hypervisor_hostname}\
             vm_network_net_a={vm_network_net_a}\
             vm_network_net_b={vm_network_net_b}\
             vm_network_app_a={vm_network_app_a}\
             vm_network_app_b={vm_network_app_b}\
             vm_network_mir_a={vm_network_mir_a}\
             vm_network_mir_b={vm_network_mir_b}\
             vm_qcow_name={vm_qcow_name}"'
        install_required_packages_docker_command = f'docker exec -t {docker_name} {install_required_packages}'
        log_check_bool.append(
            ansible_log_writer_analyzer(
                install_log_name, install_required_packages_docker_command,
            ),
        )

        # If failed exit the loop
        if ansible_run_check(log_check_bool):
            log.error('Failed Step 2')
            break

        log.info('Step 3: Run KVM Installation')
        log_check_bool.append(
            ansible_log_writer_analyzer(
                install_log_name, 'echo Running Build',
            ),
        )
        command_name = f'ansible-playbook playbooks/install_kvm.yml --extra-vars \
            "hypervisor_hostname={hypervisor_hostname}\
             hypervisor_vm_image_loc={hypervisor_vm_image_loc}\
             hypervisor_dest_directory={hypervisor_dest_directory}\
             vm_qcow_name={vm_qcow_name}\
             vm_vcpus={vm_vcpus}\
             vm_memory={vm_memory}\
             vm_os_variant={vm_os_variant}\
             vm_boot={vm_boot}\
             vm_cpu={vm_cpu}\
             vm_source={vm_source}\
             vm_model={vm_model}\
             vm_source_mode={vm_source_mode}\
             vm_network_net_a={vm_network_net_a}\
             vm_network_net_b={vm_network_net_b}\
             vm_network_app_a={vm_network_app_a}\
             vm_network_app_b={vm_network_app_b}\
             vm_network_mir_a={vm_network_mir_a}\
             vm_network_mir_b={vm_network_mir_b}\
             vm_username={vm_username}\
             vm_hashed_password={vm_hashed_password}\
             vm_hostname={vm_hostname}\
             vm_static_ip_address={vm_static_ip_address}\
             vm_ip_gateway={vm_ip_gateway}\
             vm_ip_netmask={vm_ip_netmask}\
             vm_dns_server_1={vm_dns_server_1}\
             vm_dns_server_2={vm_dns_server_2}"'
        docker_command = f'docker exec -t {docker_name} {command_name}'
        log_check_bool.append(
            ansible_log_writer_analyzer(
                install_log_name, docker_command,
            ),
        )

        # If failed break out of the loop
        if ansible_run_check(log_check_bool):
            log.error('Failed Step 3')
            break

        if vm_static_ip_address:
            # Setup the VM Instance
            log.info('Step 4: Setup the VM via API')
            log_check_bool.append(
                ansible_log_writer_analyzer(
                    install_log_name, 'echo Setting up the ETO',
                ),
            )
            command_name = f'python3 /deploy/setup_eto.py --ip={vm_static_ip_address} --username={vm_api_username} --old_password={vm_old_password} --password={vm_password} --allow-enrollment={vm_allow_enrollment}'
            docker_command = f'docker exec -t {docker_name} {command_name}'
            log_check_bool.append(
                ansible_log_writer_analyzer(
                    install_log_name, docker_command,
                ),
            )
        else:
            log.warning('Cannot connect to ETO unless a static IP is provided')

    if ansible_run_check(log_check_bool):
        log.error(hypervisor_hostname + ' Installation Failed\n')
        return False
    else:
        log.info(hypervisor_hostname + ' Installation Succeeded\n')
        return True


def parse_deployment_arguments():
    """
    Parse command-line arguments for deployment configuration.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.

    Example
    -------
    Example usage:
        python deploy.py --config /path/to/config.json --log-dir /path/to/logs --log-level DEBUG --allow-enrollment True

    Notes
    -----
    This function parses command-line arguments for deployment configuration. It returns
    an `argparse.Namespace` object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Deployment Config Parser')
    parser.add_argument(
        '--config', required=True, type=str,
        help='Path to deployment configuration file',
    )
    parser.add_argument(
        '--log-dir', type=str, default=None,
        help='Path to deployment logs',
    )
    parser.add_argument(
        '--log-level', type=str, default='INFO', choices=[
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'VERBOSE',
        ], help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL, VERBOSE)',
    )
    parser.add_argument(
        '--allow-enrollment', type=bool, default=False,
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    """This script is designed to handle deployment tasks. When executed directly, it performs the following steps:

    1. Parses deployment arguments.
    2. Checks if Docker is running; if up, starts the ansible_automation container; if not, prompts the user to start Docker and exits.
    3. Sets up logging, creating a log file path based on the current timestamp and specified log directory.
    4. Creates the log directory if it doesn't exist.
    5. Reads configuration data from a JSON file specified in the arguments.
    6. Initiates deployment, displaying progress and storing logs in the specified log file.
    7. Outputs messages indicating the start and end of deployment.
    """

    args = parse_deployment_arguments()

    # Check if the docker container is running
    if is_docker_running():
        # Check the existence of the ssh-keys directory
        if ansible_ssh_key_exist(directory='./ssh-keys', key_name='ansible'):
            print(colors.GREEN + 'SSH keys exist' + colors.GREEN)
            ensure_container_running(
                docker_name, compose_file='docker-compose.yml',
            )
        else:
            print(colors.RED + 'Stopping the docker container' + colors.END)
            stop_container(docker_name, compose_file='docker-compose.yml')
            print(colors.RED + 'Generating the SSH keys' + colors.END)
            ansible_ssh_keys_generate(
                directory='./ssh-keys', key_name='ansible',
            )
            print(
                colors.RED + 'Starting the containers to ensure the volume mounts correctly' + colors.END,
            )
            ensure_container_running(
                docker_name, compose_file='docker-compose.yml', build=False,
            )
    else:
        print(colors.RED + 'Docker is not running, please start it.' + colors.END)
        exit(1)

    # Setup Logging
    log_dir = args.log_dir
    if log_dir is not None:
        log_file_path = os.path.join(log_dir, 'deploy-')
    else:
        log_file_path = 'logs/deploy-'
    log_file_path += str(
        datetime.datetime.now().replace(
            microsecond=0,
        ).isoformat(),
    )
    log_file_path = re.sub(':', '-', log_file_path) + '.log'

    # Create the directory if it doesn't exist
    if not os.path.exists(os.path.dirname(log_file_path)):
        os.makedirs(os.path.dirname(log_file_path))
    log_level = str.upper(args.log_level)
    setup_logging(log_file_path, log_level=log_level)

    # Get the data from the JSON file
    config_file_path = args.config
    with open(config_file_path) as json_file:
        configuration = json.load(json_file)

    # Begin Deployment
    print(colors.GREEN + 'Deployment has begun' + colors.END)
    print(f'Logs are stored in {log_file_path}')
    result = builder_func(
        configuration, log_file_path,
        log_level, use_docker=True,
    )
    print(
        (colors.GREEN if result else colors.RED),
        'Deployment has Ended', colors.END,
    )
