# Further Reading
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Curated resources to deepen your understanding beyond this guide. All Red Hat documentation is freely accessible with a free Red Hat Developer account.

---
<a name="toc"></a>

## Table of contents

- [Official Red Hat Documentation](#official-red-hat-documentation)
- [Red Hat Exam Prep](#red-hat-exam-prep)
- [Ansible](#ansible)
- [systemd](#systemd)
- [SELinux](#selinux)
- [Containers and Podman](#containers-and-podman)
- [Performance and Observability](#performance-and-observability)
- [Linux Fundamentals](#linux-fundamentals)
- [Networking](#networking)
- [Practice Environments](#practice-environments)
- [Community](#community)


## Official Red Hat Documentation

| Resource | URL | When to Use |
|---|---|---|
| RHEL 10 Product Documentation | [access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10) | Authoritative reference for everything |
| Configuring and managing networking | [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | nmcli deep dive, bonding, bridges, VLANs |
| SELinux User's and Administrator's Guide | [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/using_selinux/index) | Policy deep-dive, confined services, troubleshooting |
| Managing file systems | [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_file_systems/index) | XFS, ext4, LVM, VDO |
| Configuring basic system settings | [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_basic_system_settings/index) | tuned, performance co-pilot, cgroups |
| Building, running, and managing containers | [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/building_running_and_managing_containers/index) | Podman, Buildah, Quadlet, rootless |
| Automating system administration with Ansible | [link](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/automating_system_administration_by_using_rhel_system_roles/index) | RHEL System Roles |


[↑ Back to TOC](#toc)

---

## Red Hat Exam Prep

| Resource | Notes |
|---|---|
| [RHCSA EX200 Exam Objectives](https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam) | Official, always check before exam |
| [RHCE EX294 Exam Objectives](https://www.redhat.com/en/services/training/ex294-red-hat-certified-engineer-rhce-exam-red-hat-enterprise-linux-9) | Ansible exam objectives |
| [RHCA Infrastructure concentration](https://www.redhat.com/en/services/certification/rhca) | Overview of specialist credentials |
| [Red Hat Learning Subscription](https://www.redhat.com/en/services/training/learning-subscription) | Video courses, hands-on labs in the cloud |


[↑ Back to TOC](#toc)

---

## Ansible

| Resource | Notes |
|---|---|
| [Ansible Documentation](https://docs.ansible.com/) | Module reference, playbook language reference |
| [Ansible Galaxy](https://galaxy.ansible.com/) | Community roles and collections |
| [Red Hat Ansible Automation Platform Docs](https://access.redhat.com/documentation/en-us/red_hat_ansible_automation_platform/) | AAP-specific; useful background for EX294 |
| *Ansible: Up and Running* (O'Reilly) | Book — excellent Ansible fundamentals |


[↑ Back to TOC](#toc)

---

## systemd

| Resource | Notes |
|---|---|
| `man systemd.unit` | The definitive reference — read it |
| `man systemd.service` | Service-specific directives |
| `man systemd.exec` | Sandboxing directives (`PrivateTmp`, `NoNewPrivileges`, etc.) |
| [systemd.io](https://systemd.io/) | Upstream documentation and blog |
| *How Linux Works* by Brian Ward | Book — excellent systemd and boot process coverage |


[↑ Back to TOC](#toc)

---

## SELinux

| Resource | Notes |
|---|---|
| [SELinux Project Wiki](https://selinuxproject.org/page/Main_Page) | Policy reference, upstream docs |
| `man semanage-fcontext` | fcontext management |
| `man audit2allow` | Policy module generation |
| `man sepolicy` | Introspect SELinux policy |
| *SELinux System Administration* (Packt) | Book — comprehensive guide |


[↑ Back to TOC](#toc)

---

## Containers and Podman

| Resource | Notes |
|---|---|
| [Podman Documentation](https://docs.podman.io/) | Official Podman reference |
| [Quadlet documentation](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) | Full `.container` file directive reference |
| [OCI Image Specification](https://github.com/opencontainers/image-spec) | What a container image actually is |
| [Red Hat Container Catalog](https://catalog.redhat.com/software/containers/explore) | Certified base images for RHEL |


[↑ Back to TOC](#toc)

---

## Performance and Observability

| Resource | Notes |
|---|---|
| `man iostat`, `man vmstat`, `man mpstat` | sysstat tools reference |
| [Brendan Gregg's Linux Performance](https://www.brendangregg.com/linuxperf.html) | The definitive performance resource |
| [bpftrace](https://github.com/iovisor/bpftrace) | Dynamic tracing for deep performance analysis |
| *Systems Performance* by Brendan Gregg | Book — essential for RHCA-level performance work |
| [Red Hat Performance Co-Pilot (PCP)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/monitoring_and_managing_system_status_and_performance/index) | RHEL's observability framework |


[↑ Back to TOC](#toc)

---

## Linux Fundamentals

| Resource | Notes |
|---|---|
| `man hier` | The filesystem hierarchy standard — read once |
| [The Linux Command Line](https://linuxcommand.org/tlcl.php) | Free book — excellent for Track A learners |
| *UNIX and Linux System Administration Handbook* (Evi Nemeth et al.) | The essential sysadmin reference; 5th ed. covers Linux well |
| [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/) | Authoritative but dense; useful for proc/sys tuning |


[↑ Back to TOC](#toc)

---

## Networking

| Resource | Notes |
|---|---|
| `man ip`, `man ip-route`, `man ip-address` | iproute2 reference |
| [NetworkManager documentation](https://networkmanager.dev/docs/) | nmcli and connection file formats |
| *TCP/IP Illustrated, Vol. 1* by W. Richard Stevens | Classic — fundamental TCP/IP knowledge for tcpdump work |
| [tcpdump.org](https://www.tcpdump.org/manpages/tcpdump.1.html) | Filter syntax reference |


[↑ Back to TOC](#toc)

---

## Practice Environments

| Resource | Notes |
|---|---|
| [Red Hat Developer Sandbox](https://developers.redhat.com/developer-sandbox) | Free OpenShift/cloud environment (not RHEL, but useful) |
| [KVM/QEMU on Fedora](https://developer.fedoraproject.org/tools/virtualization/about.html) | Best local environment for RHEL labs |
| [Vagrant + libvirt](https://vagrant-libvirt.github.io/vagrant-libvirt/) | Scriptable multi-VM environments |
| [learn.redhat.com](https://learn.redhat.com/) | Red Hat's official learning platform |


[↑ Back to TOC](#toc)

---

## Community

| Resource | Notes |
|---|---|
| [r/redhat](https://www.reddit.com/r/redhat/) | Community discussion |
| [r/linuxadmin](https://www.reddit.com/r/linuxadmin/) | Broader sysadmin community |
| [Red Hat Discussion Forums](https://discuss.redhat.com/) | Official community forums |
| [RHCSA/RHCE Study Group (r/redhat)](https://www.reddit.com/r/redhat/wiki/index) | Community study resources and experience reports |


[↑ Back to TOC](#toc)

---

## Next step

→ [Back to Contents](../README.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
