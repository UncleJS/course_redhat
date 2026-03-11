# Glossary
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Key terms used throughout this guide, ordered alphabetically.

---
<a name="toc"></a>

## Table of contents

- [A](#a)
- [B](#b)
- [C](#c)
- [D](#d)
- [E](#e)
- [F](#f)
- [G](#g)
- [I](#i)
- [J](#j)
- [L](#l)
- [M](#m)
- [N](#n)
- [P](#p)
- [Q](#q)
- [R](#r)
- [S](#s)
- [T](#t)
- [U](#u)
- [V](#v)
- [X](#x)
- [Z](#z)


## A

**ACL (Access Control List)**
An extended permission mechanism that allows fine-grained access control beyond the standard owner/group/other model. Managed with `getfacl` and `setfacl`. See [ACLs](../02-foundations/06-acls.md).

**Ansible**
An agentless IT automation engine that uses SSH to execute declarative playbooks (YAML) on managed nodes. The RHCE exam (EX294) tests Ansible on RHEL 10. See [Ansible Setup and Inventory](../04-rhce/03-ansible-setup-inventory.md).

**Ansible Galaxy**
The upstream community hub for sharing Ansible roles and collections. Accessed via `ansible-galaxy`.

**Ansible Vault**
An Ansible feature for encrypting sensitive data (passwords, API keys) within playbook variables and files.

**AVC (Access Vector Cache)**
The SELinux kernel subsystem that caches policy decisions for performance. AVC denials appear in `/var/log/audit/audit.log` and `journalctl -k`. See [SELinux AVC Basics](../03-rhcsa/14-selinux-avc-basics.md).


[↑ Back to TOC](#toc)

---

## B

**Boolean (SELinux)**
A runtime switch that toggles a subset of SELinux policy rules without recompiling the policy. Managed with `getsebool` and `setsebool`. See [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md).

**Boot target**
A systemd unit of type `target` (e.g., `multi-user.target`, `graphical.target`) that groups dependencies for a system state. Replaces SysVinit runlevels.


[↑ Back to TOC](#toc)

---

## C

**cgroup (Control Group)**
A Linux kernel feature that limits, accounts for, and isolates resource usage (CPU, memory, I/O, network) for collections of processes. Systemd and Podman both use cgroups. RHEL 10 uses cgroup v2 exclusively.

**Condition (systemd)**
A unit file directive (`ConditionPathExists=`, `ConditionVirtualization=`, etc.) that prevents a unit from starting if the condition is not met, without reporting a failure.

**Container**
An isolated process (or group of processes) sharing the host kernel but with separate namespaces (PID, network, mount, user, IPC, UTS). On RHEL 10 this means Podman. See [Podman Fundamentals](../05-rhca/containers/01-podman-fundamentals.md).

**Context (SELinux)**
A label attached to every file, process, and socket of the form `user:role:type:level`. The type field (e.g., `httpd_sys_content_t`) is what most policy rules check. See [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md).


[↑ Back to TOC](#toc)

---

## D

**DAC (Discretionary Access Control)**
The traditional Unix permission model (owner/group/other + rwx). Called "discretionary" because owners can grant access to others at their discretion. Contrasts with MAC.

**DBus**
An IPC mechanism used by systemd for inter-process communication. Required for `systemctl --user` in rootless Podman / Quadlet contexts.

**dnf**
The package manager for RHEL 10 (Dandified YUM). Handles installation, updates, removal, and dependency resolution of RPM packages. See [Packages and DNF](../03-rhcsa/01-packages-dnf.md).

**Drop-in (systemd)**
An override file placed in `/etc/systemd/system/<unit>.d/*.conf` that supplements (rather than replaces) the original unit definition. Created via `systemctl edit <unit>`.


[↑ Back to TOC](#toc)

---

## E

**ens3**
The default virtio network interface name used in KVM/QEMU VMs throughout this guide. May differ in other hypervisors or physical hardware (e.g., `ens192`, `eth0`).

**ext4**
A widely-used Linux journaling filesystem. On RHEL 10, XFS is the default for data partitions; ext4 is used for `/boot` in some configurations.


[↑ Back to TOC](#toc)

---

## F

**fcontext**
An SELinux file context mapping — a rule that defines what SELinux label a file path should have. Managed with `semanage fcontext`. Must be followed by `restorecon` to apply to existing files.

**firewalld**
The RHEL 10 firewall manager, using `nftables` as its backend. Manages zones, services, ports, and rich rules. See [firewalld](../03-rhcsa/11-firewalld.md).

**fstab**
`/etc/fstab` — the filesystem table. Defines which filesystems and network mounts are mounted at boot. See [Filesystems and fstab](../03-rhcsa/03-filesystems-fstab.md).


[↑ Back to TOC](#toc)

---

## G

**GRUB2**
The GRand Unified Bootloader version 2. The bootloader used on RHEL 10. Configuration is managed via `grubby`. The bootloader menu allows kernel selection and parameter editing at boot.

**grubby**
A command-line tool for managing GRUB2 boot entries. Used to set the default kernel, add/remove kernel parameters.


[↑ Back to TOC](#toc)

---

## I

**inode**
A data structure in a filesystem that stores metadata about a file (permissions, timestamps, ownership, data block pointers) but not the filename. Inode exhaustion (not disk space exhaustion) is a common cause of "disk full" errors on `/var/log`.

**I/O wait**
The percentage of CPU time spent waiting for I/O operations to complete (the `wa` column in `vmstat`). High I/O wait indicates a disk or NFS bottleneck, not a CPU bottleneck.


[↑ Back to TOC](#toc)

---

## J

**journald**
The systemd journal daemon (`systemd-journald`). Collects log data from the kernel, services, and applications into a structured binary format queryable with `journalctl`. See [Logging and journald](../03-rhcsa/06-logging-journald.md).

**journalctl**
The command-line interface for reading the systemd journal. Supports filtering by service (`-u`), priority (`-p`), time (`--since`/`--until`), and kernel (`-k`).


[↑ Back to TOC](#toc)

---

## L

**Linger (systemd)**
A per-user setting (`loginctl enable-linger`) that keeps a user's systemd user instance and services running after the user logs out. Required for rootless Podman Quadlet services.

**load average**
A Unix metric representing the average number of processes in the run queue (running or waiting to run) over the last 1, 5, and 15 minutes. Compare to CPU count to assess system load.

**LVM (Logical Volume Manager)**
A storage abstraction layer that allows flexible resizing and management of logical volumes spanning one or more physical disks. See [LVM](../03-rhcsa/04-lvm.md).


[↑ Back to TOC](#toc)

---

## M

**MAC (Mandatory Access Control)**
A security model where access decisions are made by policy, not by the resource owner. SELinux implements MAC on RHEL. Contrast with DAC.

**MLS (Multi-Level Security)**
The sensitivity/clearance component of a full SELinux context (the `s0:cX,cY` part). Most RHEL deployments use `s0` (the default sensitivity level) and only use the category fields for container isolation.


[↑ Back to TOC](#toc)

---

## N

**NetworkManager**
The RHEL 10 network configuration service. Manages connections via `nmcli` (CLI), `nmtui` (TUI), or connection files in `/etc/NetworkManager/system-connections/`. See [NetworkManager and nmcli](../03-rhcsa/09-networkmanager-nmcli.md).

**nmcli**
The command-line interface for NetworkManager. Used to create, modify, activate, and inspect network connections.


[↑ Back to TOC](#toc)

---

## P

**pasta**
The default network stack for rootless Podman on RHEL 10 (replacing slirp4netns). pasta provides better performance and supports IPv6. See [Rootless Podman](../05-rhca/containers/02-rootless.md).

**PE (Physical Extent)**
The basic allocation unit in LVM. A Physical Volume is divided into fixed-size PEs (default 4 MB). Logical Volumes are allocated in multiples of PEs.

**Playbook (Ansible)**
A YAML file containing one or more plays, each targeting a group of hosts and defining a list of tasks to execute. The central Ansible artifact.

**Podman**
A daemonless container engine for OCI containers on RHEL 10. Supports both root and rootless operation. See [Podman Fundamentals](../05-rhca/containers/01-podman-fundamentals.md).

**Podman secret**
An encrypted blob stored by Podman and injected into containers at `/run/secrets/<name>` as a read-only tmpfs file. Never exposed in environment variables or process arguments. See [Secrets](../05-rhca/containers/04-secrets.md).

**PV (Physical Volume)**
A disk or partition initialized for use by LVM with `pvcreate`.


[↑ Back to TOC](#toc)

---

## Q

**Quadlet**
A systemd generator shipped with Podman on RHEL 10 that converts `.container`, `.volume`, `.network`, and `.pod` files into systemd unit files at runtime. The preferred way to run containers under systemd. See [systemd Integration](../05-rhca/containers/05-systemd-integration.md).


[↑ Back to TOC](#toc)

---

## R

**RHCA (Red Hat Certified Architect)**
The highest Red Hat certification tier. Earned by achieving five or more Red Hat Certified Specialist credentials. This guide targets the RHEL infrastructure concentration.

**RHCE (Red Hat Certified Engineer)**
The second-tier Red Hat certification (EX294). Tests Ansible automation skills on RHEL. Prerequisite: RHCSA.

**RHCSA (Red Hat Certified System Administrator)**
The entry-level Red Hat certification (EX200). Tests core RHEL administration skills. See [Exam Objective Map](01-objective-map.md).

**restorecon**
A SELinux tool that relabels files to their default context based on the fcontext database. Must be run after `semanage fcontext` to apply new rules to existing files. See [semanage](../05-rhca/selinux/02-semanage.md).

**Role (Ansible)**
A structured way to organize playbooks, tasks, variables, templates, and handlers into a reusable unit. Roles follow a standard directory layout. See [Ansible Roles](../04-rhce/06-ansible-roles.md).

**RPM**
The underlying package format for RHEL. `rpm` provides low-level package management; `dnf` adds dependency resolution and repository management on top.


[↑ Back to TOC](#toc)

---

## S

**SELinux (Security-Enhanced Linux)**
A Linux Security Module implementing Mandatory Access Control. Enforces type enforcement policy on every file access, network connection, and process action. See [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md).

**semanage**
A SELinux policy management tool for persistent changes to fcontext mappings, port labels, and booleans. Part of the `policycoreutils-python-utils` package. See [semanage](../05-rhca/selinux/02-semanage.md).

**slirp4netns**
The previous user-space network stack for rootless Podman (pre-RHEL 10). Replaced by pasta on RHEL 10.

**socket activation**
A systemd feature where a service is started on-demand when a connection arrives on its socket, rather than at boot. Improves startup time and resource usage.

**subscription-manager**
The RHEL tool for registering systems with Red Hat Subscription Management (RHSM) and entitling them to content repositories.

**sudo**
A program that allows a permitted user to execute commands as another user (typically root) after authentication. RHEL configures sudo via `/etc/sudoers` and `/etc/sudoers.d/`. See [sudo and Updates](../01-getting-started/03-sudo-updates.md).

**swap**
Disk space used to extend virtual memory when physical RAM is exhausted. Chronic swapping (high `si`/`so` in `vmstat`) indicates insufficient RAM for the workload.


[↑ Back to TOC](#toc)

---

## T

**target (systemd)**
A unit type that groups other units for synchronization and ordering. Acts as milestones in the boot process (e.g., `network-online.target`, `multi-user.target`).

**tcpdump**
A command-line network packet analyzer. Used for network troubleshooting and protocol analysis. See [tcpdump](../05-rhca/networking/03-tcpdump.md).

**THP (Transparent Huge Pages)**
A kernel feature that automatically uses 2 MB huge memory pages instead of 4 KB standard pages. Improves throughput for some workloads (databases may prefer it disabled). Managed via `tuned` profiles.

**tuned**
A systemd service on RHEL 10 that applies kernel parameter and device setting profiles optimized for specific workloads. See [tuned](../05-rhca/perf/02-tuned.md).


[↑ Back to TOC](#toc)

---

## U

**Unit (systemd)**
The basic configuration object in systemd. Types include `.service`, `.socket`, `.timer`, `.target`, `.mount`, `.path`, `.slice`, and `.scope`.

**userns (User Namespace)**
A Linux kernel feature that maps a range of host UIDs to a different range inside the namespace. Used by rootless Podman to give containers apparent root access without actual root privileges on the host.


[↑ Back to TOC](#toc)

---

## V

**VG (Volume Group)**
A pool of storage in LVM created from one or more Physical Volumes. Logical Volumes are allocated from VGs.

**virsh**
The command-line interface for libvirt/KVM VM management. Used for VM lifecycle, snapshot management, and network configuration.

**virt-install**
A command-line tool for creating and provisioning KVM virtual machines.


[↑ Back to TOC](#toc)

---

## X

**XFS**
The default filesystem for RHEL 10 data partitions. High-performance, scalable journaling filesystem. Can be grown online but **cannot be shrunk**. See [Filesystems and fstab](../03-rhcsa/03-filesystems-fstab.md).


[↑ Back to TOC](#toc)

---

## Z

**:z / :Z (Podman volume mount flags)**
SELinux relabeling options for Podman volume mounts. `:z` (lowercase) = shared label (multiple containers can read). `:Z` (uppercase) = private label (only this container can read). See [Volumes](../05-rhca/containers/03-volumes.md).


[↑ Back to TOC](#toc)

---

## Next step

→ [Command Cheatsheets](03-cheatsheets.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
