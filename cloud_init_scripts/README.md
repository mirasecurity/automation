# Cloud-Init ISO Generator

This Python script provides functionality to generate cloud-init scripts for configuring virtual machines and to create a cloud-init ISO image.

## Usage

### Prerequisites

- Python 3.x
- `genisoimage` command-line tool

### Installation

No installation is required. Simply clone or download the script file.

### Generating Cloud-Init Scripts

To generate cloud-init scripts, run the following command:

```bash
python cloud_init_utils.py generate_cloud_init_iso \
    --vm_username <vm_username> \
    --vm_hashed_password '<vm_hashed_password>' \
    --vm_hostname <vm_hostname> \
    --cloud_init_iso_name <cloud_init_iso_name> \
    [--cloud_init_meta_data_directory <cloud_init_meta_data_directory>] \
    [--cloud_init_user_data_directory <cloud_init_user_data_directory>] \
    [--vm_static_ip_address <static_ip_address>] \
    [--vm_ip_gateway <ip_gateway>] \
    [--vm_ip_netmask <ip_netmask>] \
    [--vm_dns_server_1 <dns_server_1>] \
    [--vm_dns_server_2 <dns_server_2>]

```
To generate a hash of your password use the following command:

    mkpasswd -m sha-512

Please note that the vm_hashed_password must be placed in inverted commas(' ') otherwise special characters like `$` and `\` are escaped and won't be added correctly to the user-data file.

e.g. Generate your password using:

    mkpasswd -m sha-512 Str0ngP@ssw0rd!
    >> $6$lch7PslmofEYJlt5$ff.8KzFMi.lT/m4Ot/A.kAsTtRmbxDYJGY6TOuIujT6JSnSo9XRjiJpztvsi8y6hYNlEiII9WU9pjP1iQ/41g0

```bash
python cloud_init_utils.py generate_cloud_init_iso \
    --vm_username mira \
    --vm_hashed_password '$6$lch7PslmofEYJlt5$ff.8KzFMi.lT/m4Ot/A.kAsTtRmbxDYJGY6TOuIujT6JSnSo9XRjiJpztvsi8y6hYNlEiII9WU9pjP1iQ/41g0' \
    --vm_hostname host-machine \
    --cloud_init_iso_name cloud_init.iso
```

To use the cloud-init iso image with the mira kvm use the following command:

```bash
virt-install --name=<kvm_domain_name> \
--vcpus=<num_cpus> \
--memory=<vm_memory> \
--os-variant=<vm_os_variant> \
--disk <vm_qcow_name>.qcow2 \
--cdrom <cloud_init_name>.iso \
--boot hd,cdrom \
--cpu host \
--network type=direct,source=<main_interface_name>,model=virtio,source_mode=bridge \
--network bridge=<br_net_a>,model=virtio  \
--network bridge=<br_net_b>,model=virtio  \
--network bridge=<br_app_a>,model=virtio  \
--network bridge=<br_app_b>,model=virtio  \
--network bridge=<br_mir_a>,model=virtio  \
--network bridge=<br_mir_b>,model=virtio  \
--noautoconsole \
--import
```

The ISO may also be loaded into a new ESXi VM on it's first import.

### References

- https://cloudinit.readthedocs.io/en/latest/howto/run_cloud_init_locally.html
