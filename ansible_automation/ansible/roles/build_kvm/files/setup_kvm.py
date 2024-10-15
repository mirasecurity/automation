import argparse
import os
import subprocess
from pathlib import Path

from helpers import clean_up_sensitive_info
from helpers import download_extract_and_rename_qcow2
from helpers import generate_cloud_init_files
from helpers import generate_cloud_init_iso


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create bridges and launch a virtual machine from a downloaded image',
    )

    # add arguments for launching the virtual machine
    parser.add_argument(
        '--hypervisor_vm_image_loc', required=True,
        help='The url/file directory where to download the tar file to be extracted on the hypervisor',
    )
    parser.add_argument(
        '--hypervisor_dest_directory', default='/var/lib/libvirt/images/',
        help='The file directory where to place the qcow image on the hypervisor',
    )
    parser.add_argument('--vm-image-name', help='Rename the VM image')
    parser.add_argument(
        '--vm_qcow_name', required=True,
        help='name of the virtual machine qcow image',
    )
    parser.add_argument(
        '--vm_vcpus', type=int, default=8,
        help='number of virtual CPUs',
    )
    parser.add_argument(
        '--vm_memory', type=int, default=16384,
        help='amount of memory in MB assigned to the VM',
    )
    parser.add_argument(
        '--vm_os_variant', default='centos7.0',
        help='operating system variant of the VM',
    )
    parser.add_argument(
        '--vm_boot', default='hd,cdrom',
        help='vm_boot order (hd,cdrom)',
    )
    parser.add_argument('--vm_cpu', default='host', help='CPU model')
    parser.add_argument('--vm_type', default='direct', help='network type')
    parser.add_argument(
        '--vm_source', required=True,
        help='main network interface',
    )
    parser.add_argument('--vm_model', default='virtio', help='network model')
    parser.add_argument(
        '--vm_source_mode', default='bridge',
        help='network vm_source mode',
    )
    parser.add_argument(
        '--vm_network_net_a', required=True,
        help='network net a interface',
    )
    parser.add_argument(
        '--vm_network_net_b', required=True,
        help='network net b interface',
    )
    parser.add_argument(
        '--vm_network_app_a', required=True,
        help='network appliance a interfaces',
    )
    parser.add_argument(
        '--vm_network_app_b', required=True,
        help='network appliance b interfaces',
    )
    parser.add_argument(
        '--vm_network_mir_a', required=True,
        help='network mirror a interfaces',
    )
    parser.add_argument(
        '--vm_network_mir_b', required=True,
        help='network mirror b interfaces',
    )
    parser.add_argument(
        '--vm_username', required=True,
        help='user for the vm',
    )
    parser.add_argument(
        '--vm_hashed_password', required=True,
        help='Hashed vm password',
    )
    parser.add_argument(
        '--vm_hostname', required=True,
        help='Hostname for the vm',
    )
    # Additional and not required
    parser.add_argument(
        '--vm_static_ip_address', required=False,
        default=None, help='Static IP Address for the VM',
    )
    parser.add_argument(
        '--vm_ip_gateway', required=False,
        default=None, help='IP Gateway for the VM',
    )
    parser.add_argument(
        '--vm_ip_netmask', required=False,
        default=None, help='IP Netmask for the VM. Supports dotted-decimal (eg. "255.255.255.255") and CIDR (eg. "/32") notations',
    )
    parser.add_argument(
        '--vm_dns_server_1', required=False,
        default=None, help='DNS server 1 for the VM',
    )
    parser.add_argument(
        '--vm_dns_server_2', required=False,
        default=None, help='DNS server 2 for the VM',
    )
    parser.add_argument(
        '--vm_nameserver', required=False,
        default=None, help='Nameserver for the the VM. Multiple can be specified comma-seperated.',
    )

    args = parser.parse_args()

    # VM Network Config
    if args.vm_static_ip_address is not None:
        # If --vm_static_ip_address is provided, make --vm_ip_gateway and --vm_ip_netmask required
        if args.vm_ip_gateway is None:
            parser.error(
                'When specifying a static IP address, --vm_ip_gateway is required.',
            )
        if args.vm_ip_netmask is None:
            parser.error(
                'When specifying a static IP address, --vm_ip_netmask is required.',
            )

    return args


if __name__ == '__main__':
    """
    This code orchestrates the setup and launch of a vETO(virtual Encrypted Traffic Orchestrator) on a hypervisor.

    Steps:
    1. Parse command-line arguments to extract parameters necessary for VM setup and launch.
    2. Download, extract, and rename the QCOW2 image file required for the VM.
    3. Generate paths for cloud-init user data and metadata files, which contain VM configuration details.
    4. Generate cloud-init scripts using the provided parameters for user data, metadata, hostname, etc.
    5. Specify the path for the cloud-init ISO file, which initializes the VM.
    6. Check if the disk (QCOW2 image file) exists; if not, raise an exception.
    7. Construct the command to launch the VM using the `virt-install` command-line tool.
    8. Prepare network bridges for the VM by creating bridge interfaces and bringing them up.
    9. Execute shell commands to set up network bridges and launch the VM using the `virt-install` command.
    10. Print the constructed `virt-install` command for debugging purposes.
    11. Clean up sensitive information by removing temporary files or directories related to the VM setup process.
    """
    args = parse_args()

    # Download or find the image and rename it to the hostname
    disk, extract_path, tar_file_path = download_extract_and_rename_qcow2(
        url_or_file=args.hypervisor_vm_image_loc,
        extract_path=args.hypervisor_dest_directory,
        new_qcow_file=args.vm_qcow_name,
        loc_dir=args.vm_qcow_name,
    )

    cloud_init_user_data_output = str(
        Path(os.path.join(extract_path, 'user-data')),
    )
    cloud_init_meta_data_output = str(
        Path(os.path.join(extract_path, 'meta-data')),
    )

    # Generate cloud-init scripts
    generate_cloud_init_files(
        vm_username=args.vm_username,
        vm_hashed_password=args.vm_hashed_password,
        cloud_init_user_data_output=cloud_init_user_data_output,
        cloud_init_meta_data_output=cloud_init_meta_data_output,
        vm_hostname=args.vm_hostname,
        vm_static_ip_address=args.vm_static_ip_address,
        vm_ip_gateway=args.vm_ip_gateway,
        vm_ip_netmask=args.vm_ip_netmask,
        vm_dns_server_1=args.vm_dns_server_1,
        vm_dns_server_2=args.vm_dns_server_2,
        vm_nameserver=args.vm_nameserver,
    )

    cloud_init_iso_output = str(
        Path(os.path.join(extract_path, 'cloud-init.iso')),
    )

    # Generate the actual iso used
    generate_cloud_init_iso(
        cloud_init_iso_name=cloud_init_iso_output,
        user_data_directory=cloud_init_user_data_output,
        meta_data_directory=cloud_init_meta_data_output,
    )

    if disk is None:
        raise Exception(f'No such file exists: {disk}')

    # Build the command to launch the virtual machine
    virt_install_command = [
        'virt-install',
        f'--name={args.vm_qcow_name}',
        f'--vcpus={args.vm_vcpus}',
        f'--memory={args.vm_memory}',
        f'--os-variant={args.vm_os_variant}',
        f'--disk={disk}',
        f'--disk={cloud_init_iso_output},device=cdrom',
        f'--boot={args.vm_boot}',
        f'--cpu={args.vm_cpu}',
    ]

    virt_install_command.append(
        f'--network type={args.vm_type},source={args.vm_source},model={args.vm_model},source_mode={args.vm_source_mode}',
    )

    # Setup up the interfaces
    link_setup = []
    for net in (args.vm_network_net_a, args.vm_network_net_b, args.vm_network_app_a, args.vm_network_app_b, args.vm_network_mir_a, args.vm_network_mir_b):
        # Add the network interface to the command
        virt_install_command.append(
            f'--network bridge={net},model={args.vm_model}',
        )
        link_setup.append(
            f'ip link add name {net} type bridge; ip link set dev {net} up',
        )

    virt_install_command.append('--noautoconsole')
    virt_install_command.append('--import')
    virt_install_command.append('--autostart')

    # Creating the links required
    # for link_command in link_setup:
    #     link_startup = subprocess.run(link_command, shell=True, stdout=True)

    # Execute the command to launch the virtual machine
    virsh_build = subprocess.run(
        ' '.join(virt_install_command), shell=True, stdout=True,
    )

    print('virt_install_command', virt_install_command)
    clean_up_sensitive_info([
        tar_file_path,
    ])
