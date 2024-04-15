KVM Setup
=================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

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
