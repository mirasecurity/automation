# VM Deployment Automation

This repository provides helper functions for deploying a variable number of virtual machines. The included examples requires an ETO that is using v2.1 software or later for the initial installation, as older builds do not have cloud-init support.

The Ansible scripts generate necessary configurations for Netplan (Ubuntu) or Network Manager (RHEL) on the system. However, these configurations are basic examples and may need further customization. Refer to the VM GSG documentation for detailed instructions on creating more tailored configurations.

## Getting Started

The deployment code provided is designed to run on any machine that meets the prerequisite of having Python and Docker installed. The Python script orchestrates the deployment process by executing commands through a Docker container. This container is pre-configured with all the necessary requirements, including Ansible. The Python script passes a configuration JSON file to the Docker container, which then utilizes it for the deployment process.

### Prerequisites

Ensure that you have installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Python3](https://www.python.org/downloads/)

### Installation

1. Generate a secure SSH key in the local folder `ssh-keys/ansible`, not in the root .ssh as to not interfere with other SSH keys:

```bash
ssh-keygen -t rsa -b 4096 -f ssh-keys/ansible
```

Note: If the user does not add this, the deploy.py script will automatically create it.

2. Then startup the ansible docker container using

```bash
docker compose up -d --build
```
If you encounter permission-related issues, you might want to try running the command with sudo, like this:
```bash
sudo docker compose up -d --build
```

## Usage

1. Set up your deployment configuration using `build_config.template.json` as a template to build your own configuration file. Please look at the [Template Fields](/ansible_automation/README.md#template-fields) for a description of the required fields and what each field represents.

2. Once your configuration json file is ready, then run the deployment script:

```bash
python3 deploy.py --config <config>.json
```
Or with optional parameters:

```bash
sudo python3 deploy.py --config  <config>.json --log-dir logs/ --log-level INFO --allow-enrollment True
```

## Description
The deployment script performs the following tasks:

1. Parses deployment arguments.
2. Checks if Docker is running; if so, starts the ansible_automation container; if not, prompts the user to start Docker and exits.
3. Sets up logging, creating a log file path based on the current timestamp and specified log directory.
Creates the log directory if it doesn't exist.
4. Reads configuration data from a JSON file specified in the arguments.
5. Initiates deployment, displaying progress and storing logs in the specified log file.
6. Outputs messages indicating the start and end of deployment.

The deployment works as follows:

[Flow Diagram](https://github.com/mirasecurity/automation/blob/master/ansible_automation/flow-chart.jpg?raw=true)


## Template for Virtual Machine Deployment KVM

When filling out the `build_config.template.json` template to deploy virtual machines, follow the guidelines below.

### Template Fields

1. **hypervisor_hostname** (Required): The hostname of the hypervisor.
2. **hypervisor_username** (Required): Username for accessing the hypervisor.
3. **hypervisor_password** (Required): Password for accessing the hypervisor.
4. **hypervisor_vm_image_loc** (Required): Location of the image on the machine or URL.
5. **hypervisor_dest_directory** (Required): Destination location for storing the image.
6. **vm_qcow_name** (Required): Name of the QCOW image.
7. **vm_vcpus** (Optional): Number of virtual CPUs. (Default: 8)
8. **vm_memory** (Optional): Amount of memory in MB. (Default: 16384)
9. **vm_os_variant** (Optional): OS variant (Default: centos7.0).
10. **vm_boot** (Optional): Boot options (Default: hd,cdrom).
11. **vm_cpu** (Optional): CPU model (Default: host).
12. **vm_source** (Optional): Network source (Default: eno0).
13. **vm_model** (Optional): Network model (Default: virtio).
14. **vm_source_mode** (Optional): Source mode (Default: bridge).
15. **vm_network_net_a** (Required): Network bridge name to be created for for net-a.
16. **vm_network_net_b** (Required): Network bridge name to be created for for net-b.
17. **vm_network_app_a** (Required): Network bridge name to be created for for app-a.
18. **vm_network_app_b** (Required): Network bridge name to be created for for app-b.
19. **vm_network_mir_a** (Required): Network bridge name to be created for for mir-a.
20. **vm_network_mir_b** (Required): Network bridge name to be created for for mir-b.
21. **vm_username** (Required): Username for accessing the virtual machine.
22. **vm_api_username** (Optional): API username for the virtual machine (Default: mira).
23. **vm_password** (Required): Password for accessing the virtual machine.
24. **vm_old_password** (Required): Old/Default password for the virtual machine (if applicable).
25. **vm_hostname** (Required): New hostname of the virtual machine.
26. **vm_static_ip_address** (Optional): Static IP address for the virtual machine.
27. **vm_ip_netmask** (Optional): Subnet mask for the virtual machine's IP address.
28. **vm_ip_gateway** (Optional): Gateway IP address for the virtual machine.
29. **vm_dns_server_1** (Optional): Primary DNS server for the virtual machine.
30. **vm_dns_server_2** (Optional): Secondary DNS server for the virtual machine.
31. **vm_allow_enrollment** (Optional): Boolean to allow the ETO to change it's enrollment state.

Note: Fields marked as (Optional) are not mandatory for deployment but may be required depending on your specific setup.


## ETO Setup via API

"The `deploy.py` file also changes the default password for the 'admin' user for the ETO API. Additionally, the `setup_eto.py` file is responsible for modifying default settings and can be utilized independently. If `vm_static_ip_address` is specified in the `<config>.json` file, along with `vm_ip_netmask`, `vm_ip_gateway`, and `vm_allow_enrollment`, then the enrollment state for the ETO can be altered. Otherwise, the default API settings will remain unchanged.

The script can be executed independently with the following command:

```bash
python3 setup_eto.py --ip=<vm_static_ip_address> --username=<vm_api_username> --old_password=<vm_old_password> --password=<vm_password> --allow-enrollment=<vm_allow_enrollment>
```

This command will update the default password for the ETO and adjust the enrollment state accordingly.


## Cleanup

Should something go wrong, or the user wishes to remove the VM from the system the `cleanup.py` is is made available. It requires the same configuration used for the `deploy.py` file. It's purpose is to remove and delete the VM and associated files from it, along with the network configurations setup by Netplan (Ubuntu) or NetworkManager (RedHat). None of the system packages are modified by this play.

The python file can be run with the following command:

```bash
python3 cleanup.py --config  <config>.json --log-dir logs/ --log-level INFO
```
