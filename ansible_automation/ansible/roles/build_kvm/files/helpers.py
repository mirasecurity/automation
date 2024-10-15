import os
import subprocess
import tarfile
from pathlib import Path
from urllib.parse import urlparse
from ipaddress import IPv4Network

import requests


def create_directory(path):
    os.makedirs(path, exist_ok=True)


def download_or_retrieve_file(url_or_file):
    """
    Download a file from a URL or file path.

    Parameters
    ----------
    url_or_file : str
        The URL of the file to download or the local file path.

    Returns
    -------
    str
        The absolute file path where the downloaded file is saved.

    Notes
    -----
    This function supports downloading files from HTTP, as well as handling local file paths. The function prints
    the file path and the source (URL or local file) for logging purposes.
    """
    parsed_url = urlparse(url_or_file)
    if parsed_url.scheme == 'http' or parsed_url.scheme == 'https':
        # HTTP(S) handling
        response = requests.get(url_or_file)
        file_name = os.path.basename(parsed_url.path)
        with open(file_name, 'wb') as file:
            file.write(response.content)
        file_path = os.path.abspath(file_name)
        print('file_path:', file_path, 'from URL')
    else:
        # Local file
        file_path = os.path.abspath(url_or_file)
        print('file_path:', file_path, 'local file')

    return file_path


def download_extract_and_rename_qcow2(url_or_file, extract_path, new_qcow_file=None, loc_dir=None):
    """
    Download, extract, and optionally rename a qcow2 file.

    Parameters
    ----------
    url_or_file : str
        The URL or file path of the qcow2 file.
    extract_path : str
        The path to extract the contents of the qcow2 file.
    new_qcow_file : str, optional
        The new name for the qcow2 file (default is None).
    loc_dir : str, optional
        The directory within the extracted path where the qcow2 file will be placed (default is None).

    Returns
    -------
    Tuple[str, Path, str]
        A tuple containing the path of the qcow2 file, the extraction path, and the file path of the downloaded file.

    Notes
    -----
    This function downloads a qcow2 file from a URL or uses a file path if provided. It extracts the contents of the qcow2
    file to the specified extraction path. If a new name is specified, it renames the qcow2 file accordingly. The function
    returns a tuple containing the path of the qcow2 file, the extraction path, and the file path of the downloaded file.
    """

    # Example usage:
    # url_or_file = "http://example.com/sample.txt"
    file_path = download_or_retrieve_file(url_or_file)

    # extract the file to the extract_path
    with tarfile.open(file_path, 'r:gz') as tar:
        for member in tar.getmembers():
            print('member', member)
            # Ensures there is not a race condition on the machine
            extract_path = extract_path + '/' + loc_dir
            create_directory(extract_path)
            tar.extractall(path=extract_path, members=[member])
    print('extract_path: ', extract_path)

    qcow2_file = os.path.join(extract_path, member.name)
    print('qcow2_file: ', qcow2_file)

    if new_qcow_file:
        new_qcow_file = new_qcow_file + '.qcow2'

    # rename the qcow2 file if a new name is specified
    if qcow2_file is not None and new_qcow_file is not None:
        new_qcow2_file = os.path.join(
            os.path.dirname(qcow2_file), new_qcow_file,
        )
        os.rename(qcow2_file, new_qcow2_file)
        qcow2_file = new_qcow2_file
        print('qcow2_file new name: ', qcow2_file)

    # return the directory of the qcow2 file
    return (qcow2_file if qcow2_file is not None else None, Path(extract_path), file_path)


def generate_cloud_init_files(
        vm_username,
        vm_hashed_password,
        cloud_init_user_data_output,
        cloud_init_meta_data_output,
        vm_hostname,
        vm_static_ip_address=None,
        vm_ip_gateway=None,
        vm_ip_netmask=None,
        vm_dns_server_1=None,
        vm_dns_server_2=None,
        vm_nameserver=None,
    ):
    """
    Generate cloud-init scripts for configuring a virtual machine.

    Parameters
    ----------
    vm_username : str
        The username for the virtual machine.
    vm_hashed_password : str
        The hashed password for the virtual machine user.
    cloud_init_user_data_output : str
        The path to the output file for cloud-init user data.
    cloud_init_meta_data_output : str
        The path to the output file for cloud-init metadata.
    vm_hostname : str
        The hostname for the virtual machine.
    vm_static_ip_address : str, optional
        The static IP address for the virtual machine (default is None).
    vm_ip_gateway : str, optional
        The IP gateway for the virtual machine (default is None).
    vm_ip_netmask : str, optional
        The IP netmask for the virtual machine (default is None).
        Supports dotted-decimal (eg. '255.255.255.255') and CIDR (eg. '/32') notations.
    vm_dns_server_1 : str, optional
        The primary DNS server for the virtual machine (default is None).
    vm_dns_server_2 : str, optional
        The secondary DNS server for the virtual machine (default is None).
    vm_nameserver: str, optional
        The nameserver for the virtual machine (default is None).
        Multiple can be specified comma-seperated.

    Returns
    -------
    None

    Notes
    -----
    This function generates cloud-init scripts for configuring a virtual machine. It creates a cloud-init
    user data template based on the provided parameters, including the user, password, hostname, and networking
    settings. The generated user data template is written to the specified `cloud_init_user_data_output` file,
    while the metadata template containing only the hostname is written to the `cloud_init_meta_data_output` file.
    """
    # Convert netmask to CIDR notation for nmcli
    if vm_ip_netmask is not None:
        netmask_len = len(vm_ip_netmask.split('.'))
        if netmask_len == 1 and len(vm_ip_netmask.split('/')) == 1:
            vm_ip_netmask = f"/{vm_ip_netmask}"
        if netmask_len == 4:
            vm_ip_netmask = "/" + str(IPv4Network(f'0.0.0.0/{vm_ip_netmask}').prefixlen)
    else:
        vm_ip_netmask = ""

    cloud_init_user_data_template = '''#cloud-config
user: {}
password: "{}"
chpasswd: {{expire: False}}
ssh_pwauth: True
runcmd:
- hostnamectl set-hostname {}
'''.format(vm_username, vm_hashed_password, vm_hostname)

    if vm_static_ip_address:
        cloud_init_user_data_template += f"- set -x; nmcli connection modify eth0 ipv4.method manual ipv4.addresses '{vm_static_ip_address}{vm_ip_netmask}'\n"

    if vm_ip_gateway:
        cloud_init_user_data_template += f"- set -x; nmcli connection modify eth0 ipv4.gateway '{vm_ip_gateway}'\n"

    if vm_dns_server_1:
        cloud_init_user_data_template += (
            f"- set -x; nmcli connection modify eth0 ipv4.dns '{vm_dns_server_1}'\n"
        )

    if vm_dns_server_2:
        cloud_init_user_data_template += (
            f"- set -x; nmcli connection modify eth0 +ipv4.dns '{vm_dns_server_2}'\n"
        )

    if vm_nameserver:
            cloud_init_user_data_template += (
                f"- set -x; nmcli connection modify eth0 ipv4.dns-search '{vm_nameserver}'\n"
            )

    # Restart the network to apply the changes
    cloud_init_user_data_template += (
        f"- set -x; if uname -a | grep el7; then systemctl restart network; else systemctl restart NetworkManager ; fi\n"
    )

    # Write the cloud_init_user_data_template to the specified output file
    with open(cloud_init_user_data_output, 'w') as output_file:
        output_file.write(cloud_init_user_data_template)

    cloud_init_meta_data_template = f'hostname: {vm_hostname}'

    # Write the cloud_init_meta_data_template to the specified output file
    with open(cloud_init_meta_data_output, 'w') as output_file:
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
    subprocess.run(command)


def clean_up_sensitive_info(files_to_delete: list):
    """
    Delete sensitive files from the system.

    Parameters
    ----------
    files_to_delete : list
        A list of file paths to delete.

    Returns
    -------
    None

    Notes
    -----
    This function iterates through the list of file paths provided in `files_to_delete`
    and attempts to delete each file using the `os.remove` function. If deletion is successful,
    a message is printed indicating the file was deleted. If deletion fails due to an OSError,
    an error message is printed.
    """
    for file_name in files_to_delete:
        try:
            os.remove(file_name)
            print(f'Deleted: {file_name}')
        except OSError as e:
            print(f'Error deleting {file_name}: {e}')
