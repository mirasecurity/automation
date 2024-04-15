# Ansible Playbooks

## install_kvm

`install_kvm.yml` is an Ansible playbook designed to install a specified virtual machine (VM) KVM image on a remote host. This playbook provides the following functionality:

- **Installation from URL or Local File:** Supports installation from either a URL or a file present on the local system.

- **Image Extraction and Naming:** Automatically extracts the image and renames it to the domain name provided for the VM.

- **Automatic Link Creation:** Automatically creates links for the machine, ensuring seamless integration and accessibility.

### Usage

Ensure you have Ansible installed and configured properly before running this playbook.

Run the playbook using the following command:

```bash
ansible-playbook playbooks/install_kvm.yml --extra-vars \
    "hypervisor_hostname=<hypervisor_hostname> \
     hypervisor_vm_image_loc=<hypervisor_vm_image_loc> \
     hypervisor_dest_directory=<hypervisor_dest_directory> \
     vm_qcow_name=<vm_qcow_name> \
     vm_vcpus=<vm_vcpus> \
     vm_memory=<vm_memory> \
     vm_os_variant=<os_variant> \
     vm_boot=<vm_boot> \
     vm_cpu=<vm_cpu> \
     vm_source=<vm_source> \
     vm_model=<vm_model> \
     vm_source_mode=<vm_source_mode> \
     vm_network_net_a=<vm_network_net_a> \
     vm_network_net_b=<vm_network_net_b> \
     vm_network_app_a=<vm_network_app_a> \
     vm_network_app_b=<vm_network_app_b> \
     vm_network_mir_a=<vm_network_mir_a> \
     vm_network_mir_b=<vm_network_mir_b> \
     vm_username=<vm_username> \
     vm_hashed_password=<vm_hashed_password> \
     vm_hostname=<vm_hostname> \
     vm_static_ip_address=<vm_static_ip_address> \
     vm_ip_gateway=<vm_ip_gateway> \
     vm_ip_netmask=<vm_ip_netmask> \
     vm_dns_server_1=<vm_dns_server_1> \
     vm_dns_server_2=<vm_dns_server_2>"
```

Replace the placeholders with appropriate values for your environment.

### Variables

- **hypervisor_hostname** (Required): The hostname of the hypervisor.
   Example: `hypervisor_hostname: "192.168.1.100"`

- **hypervisor_username** (Required): Username for accessing the hypervisor.
   Example: `hypervisor_username: "admin"`

- **hypervisor_password** (Required): Password for accessing the hypervisor.
   Example: `hypervisor_password: "password123"`

- **hypervisor_vm_image_loc** (Required): Location of the image on the machine or URL.
   Example: `hypervisor_vm_image_loc: "/path/to/image.qcow2"`

- **hypervisor_dest_directory** (Required): Destination location for storing the image.
   Example: `hypervisor_dest_directory: "/var/lib/libvirt/images"`

- **vm_qcow_name** (Required): Name of the QCOW image.
   Example: `vm_qcow_name: "myimage"`

- **vm_vcpus** (Optional): Number of virtual CPUs. (Default: 8)
   Example: `vm_vcpus: 4`

- **vm_memory** (Optional): Amount of vm_memory in MB. (Default: 16384)
   Example: `vm_memory: 8192`

- **vm_os_variant** (Optional): OS variant (Default: centos7.0).
   Example: `vm_os_variant: "centos7.0"`

- **vm_boot** (Optional): Boot options (Default: hd,cdrom).
    Example: `vm_boot: "cdrom,hd"`

- **vm_cpu** (Optional): CPU model (Default: host).
    Example: `cpu: "host"`

- **vm_source** (Optional): Network vm_source (Default: eno0).
    Example: `vm_source: "eth0"`

- **vm_model** (Optional): Network model (Default: virtio).
    Example: `model: "virtio"`

- **vm_source_mode** (Optional): Source mode (Default: bridge).
    Example: `vm_source_mode: "nat"`

- **vm_network_net_a** (Required): Network configuration for net-a.
    Example: `vm_network_net_a: "net-a"`

- **vm_network_net_b** (Required): Network configuration for net-b.
    Example: `vm_network_net_b: "net-b"`

- **vm_network_app_a** (Required): Network configuration for app-a.
    Example: `vm_network_app_a: "app-a"`

- **vm_network_app_b** (Required): Network configuration for app-b.
    Example: `vm_network_app_b: "app-b"`

- **vm_network_mir_a** (Required): Network configuration for mir-a.
    Example: `vm_network_mir_a: "mir-a"`

- **vm_network_mir_b** (Required): Network configuration for mir-b.
    Example: `vm_network_mir_b: "mir-b"`

- **vm_username** (Required): Username for accessing the virtual machine.
    Example: `vm_username: "user"`

- **vm_password** (Required): Password for accessing the virtual machine.
    Example: `vm_password: "vmPassword123"`

- **vm_old_password** (Required): Old password for the virtual machine (if applicable).
    Example: `vm_old_password: "oldPassword456"`

- **vm_hostname** (Required): Hostname of the virtual machine.
    Example: `vm_hostname: "myvm"`

- **vm_static_ip_address** (Optional): Static IP address for the virtual machine.
    Example: `vm_static_ip_address: "192.168.1.50"`

- **vm_ip_netmask** (Optional): Subnet mask for the virtual machine's IP address.
    Example: `vm_ip_netmask: "255.255.255.0"`

- **vm_ip_gateway** (Optional): Gateway IP address for the virtual machine.
    Example: `vm_ip_gateway: "192.168.1.1"`

- **vm_dns_server_1** (Optional): Primary DNS server for the virtual machine.
    Example: `vm_dns_server_1: "8.8.8.8"`

- **vm_dns_server_2** (Optional): Secondary DNS server for the virtual machine.
    Example: `vm_dns_server_2: "8.8.4.4"`

- **vm_api_username** (Optional): API username for the virtual machine.
    Example: `vm_api_username: "api_user"`


### Note

Ensure that all required variables are correctly specified for successful execution of the playbook.


## Install Requirements Playbook

This Ansible playbook is designed to install required packages on a remote system, *provided that the hypervisor has access to the internet and is not just accessible via SSH*. It simplifies the process of setting up necessary dependencies for various tasks.

### Usage

Ensure you have Ansible installed and configured properly before running this playbook.

Run the playbook using the following command:

```bash
ansible-playbook playbooks/setup.yml --extra-vars \
    "hypervisor_hostname=<hostname> /
     vm_network_net_a=<vm_network_net_a> /
     vm_network_net_b=<vm_network_net_b> /
     vm_network_app_a=<vm_network_app_a> /
     vm_network_app_b=<vm_network_app_b> /
     vm_network_mir_a=<vm_network_mir_a> /
     vm_network_mir_b=<vm_network_mir_b> /
     vm_qcow_name=<vm_qcow_name>"
```

Replace `<hostname>` with the hostname or IP address of the hypervisor where you want to install the required packages needed to run the KVM.

### Playbook Structure

The playbook consists of the following structure:

```yaml
- hosts: "{{ hypervisor_hostname }}"
  roles:
    - setup_hypervisor
```

- `hosts`: Specifies the hypervisor_hostname machine(s) where the playbook will be executed.
- `roles`: Defines the roles to be applied to the hypervisor_hostname machine(s). The role works for both Red Hat and Debian-based systems.

### Note

Ensure that the hypervisor_hostname machine(s) are accessible and properly configured to run Ansible playbooks. Additionally, ensure that the necessary roles (`setup_hypervisor`) are available and correctly configured for the playbook execution.

The ansible scripts creates temporary linux bridges using the ip link command as a backup. Netplan (Ubuntu) or Network Manager (RHEL) is used to setup the network bridges, more complex setups can be made, but a basic implementation is available in the playbooks.

## ssh_setup_individual

This Ansible playbook facilitates the installation of SSH keys on a remote machine, enabling seamless authentication without the need for password input. It allows you to force the SSH key copy to any machine, even if the machine is not in your inventory.

### Usage

Ensure you have Ansible installed and configured properly before running this playbook.

Run the playbook using the following command:

```bash
ansible-playbook playbooks/ssh_setup_individual.yml --extra-vars "hypervisor_username=<hypervisor_username> hypervisor_hostname=<hypervisor_hostname> hypervisor_password=<hypervisor_password>"
```

Replace `<hypervisor_username>`, `<hypervisor_hostname>`, and `<hypervisor_password>` with appropriate values:

- `hypervisor_username`: The user of the remote machine (e.g., root).
- `hypervisor_hostname`: The hostname or IP address of the remote machine.
- `hypervisor_password`: The password of the remote machine itself.

### Playbook Structure

The playbook consists of the following structure:

```yaml
- name: "Install ssh keys on remote machine"
  hosts: localhost
  connection: local
  roles:
    - ssh_remote_setup_individual
```

- `name`: Descriptive name for the playbook task.
- `hosts`: Specifies the hypervisor_hostname hosts where the playbook will be executed. In this case, it's set to `localhost` since the SSH key setup is performed locally.
- `connection`: Specifies the connection type. Here, it's set to `local` to ensure the SSH key setup is performed locally.
- `roles`: Defines the roles to be applied. The `ssh_remote_setup_individual` role is responsible for setting up SSH keys on the remote machine.

### Note

Ensure that the necessary SSH keys are available and properly configured for successful execution of the playbook. Additionally, ensure that the hypervisor_hostname machine is accessible and correctly configured to accept SSH connections.

## cleanup_hypervisor

This Ansible playbook has the task of removing the deployed vETO based on the configuration used in install_kvm playbook. The playbook also removes the network bridges that were setup via Network Manager(Redhat) or Netplan(Ubuntu).

### Usage

Ensure you have Ansible installed and configured properly before running this playbook.

Run the playbook using the following command:

```bash
ansible-playbook playbooks/cleanup.yml --extra-vars "\
    hypervisor_hostname=<hypervisor_hostname> \
    hypervisor_dest_directory=<hypervisor_dest_directory> \
    vm_qcow_name=<vm_qcow_name> \
    vm_network_net_a=<vm_network_net_a> \
    vm_network_net_b=<vm_network_net_b> \
    vm_network_app_a=<vm_network_app_a> \
    vm_network_app_b=<vm_network_app_b> \
    vm_network_mir_a=<vm_network_mir_a> \
    vm_network_mir_b=<vm_network_mir_b> \
    "
```

### Playbook Structure

The playbook consists of the following structure:

```yaml
- name: "Remove the vETO and associated files and clean network configs"
  hosts: "{{ hypervisor_hostname }}"
  roles:
    - cleanup_hypervisor
```

- `name`: Descriptive name for the playbook task.
- `hosts`: Specifies the hypervisor_hostname machine(s) where the playbook will be executed.
- `roles`: Defines the roles to be applied. The `cleanup_hypervisor` role is responsible for stopping and deleting the virtual machine, along with its associated networking setup.

### Note

Ensure that the hypervisor_hostname machine(s) are accessible and properly configured to run Ansible playbooks.
