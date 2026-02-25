# Exam Objective Map

This page maps each chapter and lab to the official Red Hat exam objectives for RHCSA (EX200), RHCE (EX294), and the RHCA infrastructure concentration exams.

> **Disclaimer:** Exam objectives change. Always cross-reference with the current Red Hat exam page at [access.redhat.com/training/exam-objectives](https://access.redhat.com/training/exam-objectives).

---
<a name="toc"></a>

## Table of contents

- [RHCSA (EX200) — RHEL 10](#rhcsa-ex200-rhel-10)
  - [Understand and use essential tools](#understand-and-use-essential-tools)
  - [Create simple shell scripts](#create-simple-shell-scripts)
  - [Operate running systems](#operate-running-systems)
  - [Configure local storage](#configure-local-storage)
  - [Create and configure file systems](#create-and-configure-file-systems)
  - [Deploy, configure, and maintain systems](#deploy-configure-and-maintain-systems)
  - [Manage basic networking](#manage-basic-networking)
  - [Manage users and groups](#manage-users-and-groups)
  - [Manage security](#manage-security)
- [RHCE (EX294) — Ansible on RHEL 10](#rhce-ex294-ansible-on-rhel-10)
- [RHCA Infrastructure Concentration (indicative topics)](#rhca-infrastructure-concentration-indicative-topics)


## RHCSA (EX200) — RHEL 10

### Understand and use essential tools

| Objective | Chapter | Lab |
|---|---|---|
| Access a shell prompt and issue commands with correct syntax | [Shell Basics](../02-foundations/01-shell-basics.md) | — |
| Use input-output redirection | [Pipes and Redirection](../02-foundations/03-pipes-redirection.md) | — |
| Use grep and regular expressions to analyze text | [Files and Text](../02-foundations/02-files-and-text.md) | — |
| Access remote systems using SSH | [SSH](../03-rhcsa/12-ssh.md) | [Static IP & DNS](../03-rhcsa/labs/01-static-ip-dns.md) |
| Log in and switch users in multiuser targets | [Shell Basics](../02-foundations/01-shell-basics.md) | — |
| Archive, compress, unpack, and uncompress files | [Files and Text](../02-foundations/02-files-and-text.md) | — |
| Create and edit text files | [Editors](../02-foundations/04-editors.md) | — |
| Create, delete, copy, and move files and directories | [Files and Text](../02-foundations/02-files-and-text.md) | — |
| Create hard and soft links | [Files and Text](../02-foundations/02-files-and-text.md) | — |
| List, set, and change standard file permissions | [Permissions](../02-foundations/05-permissions.md) | — |
| Locate, read, and use system documentation | [Help System](../01-getting-started/04-help-system.md) | — |

### Create simple shell scripts

| Objective | Chapter | Lab |
|---|---|---|
| Conditionals, loops | [Bash Fundamentals](../04-rhce/02-bash-fundamentals.md) | — |
| Process exit codes, test command | [Bash Fundamentals](../04-rhce/02-bash-fundamentals.md) | — |

### Operate running systems

| Objective | Chapter | Lab |
|---|---|---|
| Boot, reboot, shut down | [systemd Basics](../03-rhcsa/05-systemd-basics.md) | — |
| Interrupt the boot process to gain access to a system | [Recovery Patterns](../05-rhca/perf/03-recovery-patterns.md) | — |
| Identify CPU/memory intensive processes and kill | [Resource Triage](../05-rhca/perf/01-resource-triage.md) | — |
| Adjust process scheduling | [Resource Triage](../05-rhca/perf/01-resource-triage.md) | — |
| Manage tuning profiles | [tuned](../05-rhca/perf/02-tuned.md) | — |
| Locate and interpret system log files and journals | [Logging and journald](../03-rhcsa/06-logging-journald.md) | — |
| Preserve system journals across reboots | [journald Retention](../05-rhca/04-journald-retention.md) | — |
| Start, stop, and check status of services | [systemd Basics](../03-rhcsa/05-systemd-basics.md) | [Systemd Service](../03-rhcsa/labs/02-systemd-service.md) |
| Securely transfer files | [SSH](../03-rhcsa/12-ssh.md) | — |

### Configure local storage

| Objective | Chapter | Lab |
|---|---|---|
| List, create, delete partitions | [Storage Overview](../03-rhcsa/02-storage-overview.md) | — |
| Create and remove physical volumes, VGs, LVs | [LVM](../03-rhcsa/04-lvm.md) | [LVM XFS Grow](../03-rhcsa/labs/03-lvm-xfs-grow.md) |
| Configure systems to mount file systems at boot | [Filesystems and fstab](../03-rhcsa/03-filesystems-fstab.md) | — |
| Create and use swap space | [Storage Overview](../03-rhcsa/02-storage-overview.md) | — |
| Create and manage POSIX ACLs | [ACLs](../02-foundations/06-acls.md) | [Shared Team Dir](../02-foundations/labs/01-shared-team-dir.md) |

### Create and configure file systems

| Objective | Chapter | Lab |
|---|---|---|
| Create, mount, unmount, and use vfat, ext4, xfs file systems | [Filesystems and fstab](../03-rhcsa/03-filesystems-fstab.md) | — |
| Mount and unmount network file systems using NFS | [Filesystems and fstab](../03-rhcsa/03-filesystems-fstab.md) | — |
| Configure automount | [Filesystems and fstab](../03-rhcsa/03-filesystems-fstab.md) | — |
| Extend existing LVs | [LVM](../03-rhcsa/04-lvm.md) | [LVM XFS Grow](../03-rhcsa/labs/03-lvm-xfs-grow.md) |
| Create and configure set-GID directories for collaboration | [Permissions](../02-foundations/05-permissions.md) | [Shared Team Dir](../02-foundations/labs/01-shared-team-dir.md) |

### Deploy, configure, and maintain systems

| Objective | Chapter | Lab |
|---|---|---|
| Schedule tasks using at and cron | [Scheduling](../03-rhcsa/07-scheduling.md) | — |
| Start and stop services, configure services to start automatically | [systemd Basics](../03-rhcsa/05-systemd-basics.md) | [Systemd Service](../03-rhcsa/labs/02-systemd-service.md) |
| Configure systems to boot into a specific target | [systemd Advanced](../05-rhca/02-systemd-advanced.md) | — |
| Configure time service clients | [Networking Basics](../03-rhcsa/08-networking-basics.md) | — |
| Install and update software packages from a repository | [Packages and DNF](../03-rhcsa/01-packages-dnf.md) | — |
| Modify the system bootloader | [Recovery Patterns](../05-rhca/perf/03-recovery-patterns.md) | — |

### Manage basic networking

| Objective | Chapter | Lab |
|---|---|---|
| Configure IPv4 and IPv6 addresses | [NetworkManager and nmcli](../03-rhcsa/09-networkmanager-nmcli.md) | [Static IP & DNS](../03-rhcsa/labs/01-static-ip-dns.md) |
| Configure hostname resolution | [DNS Resolution](../03-rhcsa/10-dns-resolution.md) | — |
| Configure network services to start automatically | [NetworkManager and nmcli](../03-rhcsa/09-networkmanager-nmcli.md) | — |
| Restrict network access using firewall-cmd | [firewalld](../03-rhcsa/11-firewalld.md) | — |

### Manage users and groups

| Objective | Chapter | Lab |
|---|---|---|
| Create, delete, and modify local user accounts | [Accounts, sudo, and Updates](../01-getting-started/03-sudo-updates.md) | — |
| Change passwords and adjust password aging | [Accounts, sudo, and Updates](../01-getting-started/03-sudo-updates.md) | — |
| Create, delete, and modify local groups | [Users, Groups, Permissions](../02-foundations/05-permissions.md) | — |
| Configure superuser access | [Accounts, sudo, and Updates](../01-getting-started/03-sudo-updates.md) | — |

### Manage security

| Objective | Chapter | Lab |
|---|---|---|
| Configure firewall settings using firewall-cmd | [firewalld](../03-rhcsa/11-firewalld.md) | — |
| Manage default file permissions | [Permissions](../02-foundations/05-permissions.md) | — |
| Configure key-based authentication for SSH | [SSH](../03-rhcsa/12-ssh.md) | — |
| Set enforcing and permissive modes for SELinux | [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md) | — |
| List and identify SELinux file and process context | [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md) | — |
| Restore default file contexts | [SELinux AVC Basics](../03-rhcsa/14-selinux-avc-basics.md) | [SELinux Label Fix](../03-rhcsa/labs/04-selinux-label-fix.md) |
| Manage SELinux port labels | [semanage](../05-rhca/selinux/02-semanage.md) | [Non-default Port](../05-rhca/selinux/labs/01-nondefault-port.md) |
| Use Boolean settings to modify system SELinux settings | [SELinux Fundamentals](../03-rhcsa/13-selinux-fundamentals.md) | — |
| Diagnose and address routine SELinux policy violations | [SELinux AVC Basics](../03-rhcsa/14-selinux-avc-basics.md) | [SELinux Label Fix](../03-rhcsa/labs/04-selinux-label-fix.md) |


[↑ Back to TOC](#toc)

---

## RHCE (EX294) — Ansible on RHEL 10

| Objective | Chapter | Lab |
|---|---|---|
| Install and configure Ansible on a control node | [Ansible Setup and Inventory](../04-rhce/03-ansible-setup-inventory.md) | — |
| Create and use static inventories | [Ansible Setup and Inventory](../04-rhce/03-ansible-setup-inventory.md) | [First Playbook](../04-rhce/labs/01-first-playbook.md) |
| Create and use playbooks | [Ansible Playbooks](../04-rhce/04-ansible-playbooks.md) | [First Playbook](../04-rhce/labs/01-first-playbook.md) |
| Create and use variables, facts, and templates | [Ansible Vars and Templates](../04-rhce/05-ansible-vars-templates.md) | — |
| Create and use roles | [Ansible Roles](../04-rhce/06-ansible-roles.md) | [Role Web Deploy](../04-rhce/labs/02-role-web-deploy.md) |
| Create and use logic in playbooks | [Ansible Playbooks](../04-rhce/04-ansible-playbooks.md) | — |
| Use Ansible to configure target machines | [Ansible Service Deploy](../04-rhce/07-ansible-service-deploy.md) | — |
| Download and use roles from Ansible Galaxy | [Ansible Roles](../04-rhce/06-ansible-roles.md) | — |
| Use Ansible Vault for secrets | [Ansible Vars and Templates](../04-rhce/05-ansible-vars-templates.md) | — |
| Manage content with collections | [Ansible Roles](../04-rhce/06-ansible-roles.md) | — |
| Automate patching and updates | [Ansible Patching](../04-rhce/08-ansible-patching.md) | — |


[↑ Back to TOC](#toc)

---

## RHCA Infrastructure Concentration (indicative topics)

| Topic | Chapter |
|---|---|
| Advanced systemd unit configuration and hardening | [systemd Advanced](../05-rhca/02-systemd-advanced.md), [systemd Hardening](../05-rhca/03-systemd-hardening.md) |
| SELinux audit workflow and policy development | [SELinux Audit Workflow](../05-rhca/selinux/03-audit-workflow.md), [semanage](../05-rhca/selinux/02-semanage.md) |
| Advanced networking — multiple profiles, routing | [nmcli Profiles](../05-rhca/networking/01-nmcli-profiles.md), [Routing Method](../05-rhca/networking/02-routing-method.md) |
| Network diagnostics — tcpdump | [tcpdump](../05-rhca/networking/03-tcpdump.md) |
| Rootless Podman and container lifecycle | [Rootless](../05-rhca/containers/02-rootless.md), [Volumes](../05-rhca/containers/03-volumes.md) |
| Container secrets management and rotation | [Secrets](../05-rhca/containers/04-secrets.md), [Lab - Secrets Rotate](../05-rhca/containers/labs/02-secrets-rotate.md) |
| Quadlet / systemd container integration | [systemd Integration](../05-rhca/containers/05-systemd-integration.md), [Lab - Rootless Web](../05-rhca/containers/labs/01-rootless-web.md) |
| SELinux for containers | [SELinux Containers](../05-rhca/containers/06-selinux-containers.md) |
| Performance triage | [Resource Triage](../05-rhca/perf/01-resource-triage.md) |
| tuned profile management | [tuned](../05-rhca/perf/02-tuned.md) |
| System recovery procedures | [Recovery Patterns](../05-rhca/perf/03-recovery-patterns.md) |
| journald retention and forwarding | [journald Retention](../05-rhca/04-journald-retention.md) |
| Structured troubleshooting methodology | [Troubleshooting Playbook](../05-rhca/01-troubleshooting-playbook.md) |


[↑ Back to TOC](#toc)

---

## Next step

→ [Glossary](02-glossary.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
