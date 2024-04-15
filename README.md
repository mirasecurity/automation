# Automation Suite for Mira Products

This repository contains tools used to speed up workflows when deploying Mira Products.

## ansible_automation

This is used to completely automate the deployment for the vETOs. The documentation regarding its usage is available [here](https://mirasecurity.github.io/automation/).

The included examples require a vETO that is using v2.1 software or later for the initial installation, as older builds do not have cloud-init support.

## cloud_init_scripts

The cloud-init scripts section of the repo is helper functions used to generate cloud-init configurations and iso images which can be used to change the default credentials of vETO. [Cloud-init Scripts README](/cloud_init_scripts/README.md#cloud-init-iso-generator) contains more information regarding its application.
