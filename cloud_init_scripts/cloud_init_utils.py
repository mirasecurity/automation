import argparse
import os
import subprocess


def generate_cloud_init_files(user, hashed_user_password, cloud_init_user_data_directory, cloud_init_meta_data_directory, vm_hostname, vm_static_ip_address=None, vm_ip_gateway=None, vm_ip_netmask=None, vm_dns_server_1=None, vm_dns_server_2=None):
    """
    Generate cloud-init scripts for configuring a virtual machine.

    Parameters
    ----------
    user : str
        The username for the virtual machine.
    hashed_user_password : str
        The hashed password for the virtual machine user.
    cloud_init_user_data_directory : str
        The path to the output file for cloud-init user data.
    cloud_init_meta_data_directory : str
        The path to the output file for cloud-init metadata.
    vm_hostname : str
        The hostname for the virtual machine.
    vm_static_ip_address : str, optional
        The static IP address for the virtual machine (default is None).
    vm_ip_gateway : str, optional
        The IP gateway for the virtual machine (default is None).
    vm_ip_netmask : str, optional
        The IP netmask for the virtual machine (default is None).
    vm_dns_server_1 : str, optional
        The primary DNS server for the virtual machine (default is None).
    vm_dns_server_2 : str, optional
        The secondary DNS server for the virtual machine (default is None).

    Returns
    -------
    None

    Notes
    -----
    This function generates cloud-init scripts for configuring a virtual machine. It creates a cloud-init
    user data template based on the provided parameters, including the user, password, hostname, and networking
    settings. The generated user data template is written to the specified `cloud_init_user_data_directory` file,
    while the metadata template containing only the hostname is written to the `cloud_init_meta_data_directory` file.
    """
    cloud_init_user_data_template = '''#cloud-config
user: {}
password: "{}"
chpasswd: {{expire: False}}
ssh_pwauth: True
runcmd:
- hostnamectl set-hostname {}
'''.format(user, hashed_user_password, vm_hostname)

    if vm_static_ip_address:
        cloud_init_user_data_template += "- set -x; sed -i -e 's/BOOTPROTO=\"dhcp\"/BOOTPROTO=\"static\"/g' /etc/sysconfig/network-scripts/ifcfg-eth0\n"

    if vm_static_ip_address:
        cloud_init_user_data_template += f"- set -x; echo 'IPADDR={vm_static_ip_address}' >> /etc/sysconfig/network-scripts/ifcfg-eth0\n"

    if vm_ip_gateway:
        cloud_init_user_data_template += f"- set -x; echo 'GATEWAY={vm_ip_gateway}' >> /etc/sysconfig/network-scripts/ifcfg-eth0\n"

    if vm_ip_netmask:
        cloud_init_user_data_template += f"- set -x; echo 'NETMASK={vm_ip_netmask}' >> /etc/sysconfig/network-scripts/ifcfg-eth0\n"

    if vm_dns_server_1:
        cloud_init_user_data_template += (
            f"- set -x; if ! grep -q '^DNS1=' /etc/sysconfig/network-scripts/ifcfg-eth0; then echo 'DNS1={vm_dns_server_1}' >> /etc/sysconfig/network-scripts/ifcfg-eth0; else sed -i 's/^DNS1=.*/DNS1={vm_dns_server_1}/' /etc/sysconfig/network-scripts/ifcfg-eth0; fi\n"
        )

    if vm_dns_server_2:
        cloud_init_user_data_template += (
            f"- set -x; if ! grep -q '^DNS2=' /etc/sysconfig/network-scripts/ifcfg-eth0; then echo 'DNS2={vm_dns_server_2}' >> /etc/sysconfig/network-scripts/ifcfg-eth0; else sed -i 's/^DNS2=.*/DNS2={vm_dns_server_2}/' /etc/sysconfig/network-scripts/ifcfg-eth0; fi\n"
        )

    # Restart the network to apply the changes
    cloud_init_user_data_template += '- set -x; systemctl restart network\n'

    # Write the cloud_init_user_data_template to the specified output file
    with open(cloud_init_user_data_directory, 'w') as output_file:
        output_file.write(cloud_init_user_data_template)

    cloud_init_meta_data_template = f'hostname: {vm_hostname}'

    # Write the cloud_init_meta_data_template to the specified output file
    with open(cloud_init_meta_data_directory, 'w') as output_file:
        output_file.write(cloud_init_meta_data_template)


def generate_cloud_init_iso(cloud_init_iso_name, user_data_directory, meta_data_directory):
    """
    Generate a cloud-init ISO image.

    Parameters
    ----------
    cloud_init_iso_name : str
        The name of the cloud-init ISO image to generate.
    user_data_directory : str
        The directory containing the user data file.
    meta_data_directory : str
        The directory containing the metadata file.

    Returns
    -------
    None

    Notes
    -----
    This function generates a cloud-init ISO image using the `genisoimage` command-line tool.
    It combines the user data and metadata files from the specified directories into the ISO image.
    The generated ISO image is saved with the provided `cloud_init_iso_name`.
    """
    command = [
        'genisoimage', '-output', cloud_init_iso_name, '-volid',
        'cidata', '-joliet', '-rock', user_data_directory, meta_data_directory,
    ]
    subprocess.run(command, capture_output=True, text=True)


def setup_arg_parser():
    parser = argparse.ArgumentParser(
        description='Generate cloud-init scripts and ISO image',
    )

    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Sub-parser for generating cloud-init scripts
    parser_generate_cloud_init_iso = subparsers.add_parser(
        'generate_cloud_init_iso', help='Generate cloud-init scripts',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--user', required=True, help='Username for the virtual machine',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--hashed_user_password', required=True, help='Hashed password for the virtual machine user',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--cloud_init_user_data_directory', required=False, default='.', help='Directory the user-data file will be created',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--cloud_init_meta_data_directory', required=False, default='.', help='Directory the meta-data file will be created',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--vm_hostname', required=True, help='Hostname for the virtual machine',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--vm_static_ip_address', help='Static IP address for the virtual machine',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--vm_ip_gateway', help='IP gateway for the virtual machine',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--vm_ip_netmask', help='IP netmask for the virtual machine',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--vm_dns_server_1', help='Primary DNS server for the virtual machine',
    )
    parser_generate_cloud_init_iso.add_argument(
        '--vm_dns_server_2', help='Secondary DNS server for the virtual machine',
    )

    parser_generate_cloud_init_iso.add_argument(
        '--cloud_init_iso_name', required=True, help='Name of the cloud-init ISO image to generate',
    )

    return parser


if __name__ == '__main__':

    parser = setup_arg_parser()
    args = parser.parse_args()

    if args.command == 'generate_cloud_init_iso':
        user_data_directory = os.path.join(
            args.cloud_init_user_data_directory, 'user-data',
        )
        meta_data_directory = os.path.join(
            args.cloud_init_meta_data_directory, 'meta-data',
        )

        generate_cloud_init_files(
            args.user, args.hashed_user_password,
            user_data_directory,
            meta_data_directory,
            args.vm_hostname,
            args.vm_static_ip_address, args.vm_ip_gateway, args.vm_ip_netmask,
            args.vm_dns_server_1, args.vm_dns_server_2,
        )
        generate_cloud_init_iso(
            args.cloud_init_iso_name, user_data_directory, meta_data_directory,
        )
    else:
        print('Invalid command')
