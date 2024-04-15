import argparse
import datetime
import json
import logging as log
import os
import re

from utils.ansible import ansible_add_to_inventory_executor
from utils.ansible import ansible_log_writer_analyzer
from utils.ansible import ansible_run_check
from utils.utils import setup_logging

docker_name = 'ansible_automation'


def cleanup_func(config_opts, cleanup_log_name, log_level, use_docker=True):
    log_check_bool = []

    for conf in config_opts:
        hypervisor_hostname = conf.get('hypervisor_hostname')
        hypervisor_username = conf.get('hypervisor_username')
        hypervisor_password = conf.get('hypervisor_password')

        vm_qcow_name = conf.get('vm_qcow_name')

        vm_network_net_a = conf.get('vm_network_net_a')
        vm_network_net_b = conf.get('vm_network_net_b')

        vm_network_app_a = conf.get('vm_network_app_a')
        vm_network_app_b = conf.get('vm_network_app_b')

        vm_network_mir_a = conf.get('vm_network_mir_a')
        vm_network_mir_b = conf.get('vm_network_mir_b')

        # Check if it was not successfully added to the inventory
        if not ansible_add_to_inventory_executor(
            hostname=hypervisor_hostname,
            username=hypervisor_username,
            password=hypervisor_password,
            use_docker=use_docker,
            docker_name=docker_name,
            install_log_name=cleanup_log_name,
            log_level=log_level,
        ):
            raise Exception(
                f'Something went wrong when adding {hypervisor_hostname} to the inventory',
            )

        log.info('Step 1: Add the SSH keys')
        # Step 1: Add the SSH keys
        log_check_bool.append(
            ansible_log_writer_analyzer(
                cleanup_log_name, 'echo Adding SSH Keys',
            ),
        )
        make_sure_ssh_available = f'ansible-playbook playbooks/ssh_setup_individual.yml --extra-vars "hypervisor_username={conf["hypervisor_username"]} hypervisor_password={conf["hypervisor_password"]} hypervisor_hostname={conf["hypervisor_hostname"]}"'
        ssh_docker_command = f'docker exec -t {docker_name} {make_sure_ssh_available}'
        log_check_bool.append(
            ansible_log_writer_analyzer(
                cleanup_log_name, ssh_docker_command,
            ),
        )

        ansible_cleanup_command = f'ansible-playbook playbooks/cleanup.yml --extra-vars\
            "hypervisor_hostname={conf["hypervisor_hostname"]}\
            hypervisor_dest_directory={conf["hypervisor_dest_directory"]}\
            vm_qcow_name={vm_qcow_name}\
            vm_network_net_a={vm_network_net_a}\
            vm_network_net_b={vm_network_net_b}\
            vm_network_app_a={vm_network_app_a}\
            vm_network_app_b={vm_network_app_b}\
            vm_network_mir_a={vm_network_mir_a}\
            vm_network_mir_b={vm_network_mir_b}"'
        docker_cleanup_command = f'docker exec -t {docker_name} {ansible_cleanup_command}'
        log_check_bool.append(
            ansible_log_writer_analyzer(
                cleanup_log_name, docker_cleanup_command,
            ),
        )

    if ansible_run_check(log_check_bool):
        log.error(hypervisor_hostname + ' Cleanup Failed\n')
        return False
    else:
        log.info(hypervisor_hostname + ' Cleanup Succeeded\n')
        return True


def parse_cleanup_arguments():
    """
    Parse command-line arguments for cleanup configuration.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.

    Example
    -------
    Example usage:
        python deploy.py --config /path/to/config.json

    Notes
    -----
    This function parses command-line arguments for cleanup configuration. It returns
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
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_cleanup_arguments()

    # Setup Logging
    log_dir = args.log_dir
    if log_dir is not None:
        log_file_path = os.path.join(log_dir, 'cleanup-')
    else:
        log_file_path = 'logs/cleanup-'
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

    config_file_path = args.config
    with open(config_file_path) as json_file:
        conf_arr = json.load(json_file)

    use_docker = True

    cleanup_func(conf_arr, log_file_path, log_level, use_docker)
