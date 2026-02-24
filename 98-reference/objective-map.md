# Exam Objective Map

This page maps each chapter and lab to the official Red Hat exam objectives for RHCSA (EX200), RHCE (EX294), and the RHCA infrastructure concentration exams.

> **Disclaimer:** Exam objectives change. Always cross-reference with the current Red Hat exam page at [access.redhat.com/training/exam-objectives](https://access.redhat.com/training/exam-objectives).

---

## RHCSA (EX200) — RHEL 10

### Understand and use essential tools

| Objective | Chapter | Lab |
|---|---|---|
| Access a shell prompt and issue commands with correct syntax | [Shell Basics](../02-foundations/shell-basics.md) | — |
| Use input-output redirection | [Pipes and Redirection](../02-foundations/pipes-redirection.md) | — |
| Use grep and regular expressions to analyze text | [Files and Text](../02-foundations/files-and-text.md) | — |
| Access remote systems using SSH | [SSH](../03-rhcsa/ssh.md) | [Static IP & DNS](../03-rhcsa/labs/static-ip-dns.md) |
| Log in and switch users in multiuser targets | [Shell Basics](../02-foundations/shell-basics.md) | — |
| Archive, compress, unpack, and uncompress files | [Files and Text](../02-foundations/files-and-text.md) | — |
| Create and edit text files | [Editors](../02-foundations/editors.md) | — |
| Create, delete, copy, and move files and directories | [Files and Text](../02-foundations/files-and-text.md) | — |
| Create hard and soft links | [Files and Text](../02-foundations/files-and-text.md) | — |
| List, set, and change standard file permissions | [Permissions](../02-foundations/permissions.md) | — |
| Locate, read, and use system documentation | [Help System](../01-getting-started/help-system.md) | — |

### Create simple shell scripts

| Objective | Chapter | Lab |
|---|---|---|
| Conditionals, loops | [Bash Fundamentals](../04-rhce/bash-fundamentals.md) | — |
| Process exit codes, test command | [Bash Fundamentals](../04-rhce/bash-fundamentals.md) | — |

### Operate running systems

| Objective | Chapter | Lab |
|---|---|---|
| Boot, reboot, shut down | [systemd Basics](../03-rhcsa/systemd-basics.md) | — |
| Interrupt the boot process to gain access to a system | [Recovery Patterns](../05-rhca/perf/recovery-patterns.md) | — |
| Identify CPU/memory intensive processes and kill | [Resource Triage](../05-rhca/perf/resource-triage.md) | — |
| Adjust process scheduling | [Resource Triage](../05-rhca/perf/resource-triage.md) | — |
| Manage tuning profiles | [tuned](../05-rhca/perf/tuned.md) | — |
| Locate and interpret system log files and journals | [Logging and journald](../03-rhcsa/logging-journald.md) | — |
| Preserve system journals across reboots | [journald Retention](../05-rhca/journald-retention.md) | — |
| Start, stop, and check status of services | [systemd Basics](../03-rhcsa/systemd-basics.md) | [Systemd Service](../03-rhcsa/labs/systemd-service.md) |
| Securely transfer files | [SSH](../03-rhcsa/ssh.md) | — |

### Configure local storage

| Objective | Chapter | Lab |
|---|---|---|
| List, create, delete partitions | [Storage Overview](../03-rhcsa/storage-overview.md) | — |
| Create and remove physical volumes, VGs, LVs | [LVM](../03-rhcsa/lvm.md) | [LVM XFS Grow](../03-rhcsa/labs/lvm-xfs-grow.md) |
| Configure systems to mount file systems at boot | [Filesystems and fstab](../03-rhcsa/filesystems-fstab.md) | — |
| Create and use swap space | [Storage Overview](../03-rhcsa/storage-overview.md) | — |
| Create and manage POSIX ACLs | [ACLs](../02-foundations/acls.md) | [Shared Team Dir](../02-foundations/labs/shared-team-dir.md) |

### Create and configure file systems

| Objective | Chapter | Lab |
|---|---|---|
| Create, mount, unmount, and use vfat, ext4, xfs file systems | [Filesystems and fstab](../03-rhcsa/filesystems-fstab.md) | — |
| Mount and unmount network file systems using NFS | [Filesystems and fstab](../03-rhcsa/filesystems-fstab.md) | — |
| Configure automount | [Filesystems and fstab](../03-rhcsa/filesystems-fstab.md) | — |
| Extend existing LVs | [LVM](../03-rhcsa/lvm.md) | [LVM XFS Grow](../03-rhcsa/labs/lvm-xfs-grow.md) |
| Create and configure set-GID directories for collaboration | [Permissions](../02-foundations/permissions.md) | [Shared Team Dir](../02-foundations/labs/shared-team-dir.md) |

### Deploy, configure, and maintain systems

| Objective | Chapter | Lab |
|---|---|---|
| Schedule tasks using at and cron | [Scheduling](../03-rhcsa/scheduling.md) | — |
| Start and stop services, configure services to start automatically | [systemd Basics](../03-rhcsa/systemd-basics.md) | [Systemd Service](../03-rhcsa/labs/systemd-service.md) |
| Configure systems to boot into a specific target | [systemd Advanced](../05-rhca/systemd-advanced.md) | — |
| Configure time service clients | [Networking Basics](../03-rhcsa/networking-basics.md) | — |
| Install and update software packages from a repository | [Packages and DNF](../03-rhcsa/packages-dnf.md) | — |
| Modify the system bootloader | [Recovery Patterns](../05-rhca/perf/recovery-patterns.md) | — |

### Manage basic networking

| Objective | Chapter | Lab |
|---|---|---|
| Configure IPv4 and IPv6 addresses | [NetworkManager and nmcli](../03-rhcsa/networkmanager-nmcli.md) | [Static IP & DNS](../03-rhcsa/labs/static-ip-dns.md) |
| Configure hostname resolution | [DNS Resolution](../03-rhcsa/dns-resolution.md) | — |
| Configure network services to start automatically | [NetworkManager and nmcli](../03-rhcsa/networkmanager-nmcli.md) | — |
| Restrict network access using firewall-cmd | [firewalld](../03-rhcsa/firewalld.md) | — |

### Manage users and groups

| Objective | Chapter | Lab |
|---|---|---|
| Create, delete, and modify local user accounts | [Shell Basics](../02-foundations/shell-basics.md) | — |
| Change passwords and adjust password aging | [Shell Basics](../02-foundations/shell-basics.md) | — |
| Create, delete, and modify local groups | [Permissions](../02-foundations/permissions.md) | — |
| Configure superuser access | [sudo and Updates](../01-getting-started/sudo-updates.md) | — |

### Manage security

| Objective | Chapter | Lab |
|---|---|---|
| Configure firewall settings using firewall-cmd | [firewalld](../03-rhcsa/firewalld.md) | — |
| Manage default file permissions | [Permissions](../02-foundations/permissions.md) | — |
| Configure key-based authentication for SSH | [SSH](../03-rhcsa/ssh.md) | — |
| Set enforcing and permissive modes for SELinux | [SELinux Fundamentals](../03-rhcsa/selinux-fundamentals.md) | — |
| List and identify SELinux file and process context | [SELinux Fundamentals](../03-rhcsa/selinux-fundamentals.md) | — |
| Restore default file contexts | [SELinux AVC Basics](../03-rhcsa/selinux-avc-basics.md) | [SELinux Label Fix](../03-rhcsa/labs/selinux-label-fix.md) |
| Manage SELinux port labels | [semanage](../05-rhca/selinux/semanage.md) | [Non-default Port](../05-rhca/selinux/labs/nondefault-port.md) |
| Use Boolean settings to modify system SELinux settings | [SELinux Fundamentals](../03-rhcsa/selinux-fundamentals.md) | — |
| Diagnose and address routine SELinux policy violations | [SELinux AVC Basics](../03-rhcsa/selinux-avc-basics.md) | [SELinux Label Fix](../03-rhcsa/labs/selinux-label-fix.md) |

---

## RHCE (EX294) — Ansible on RHEL 10

| Objective | Chapter | Lab |
|---|---|---|
| Install and configure Ansible on a control node | [Ansible Setup and Inventory](../04-rhce/ansible-setup-inventory.md) | — |
| Create and use static inventories | [Ansible Setup and Inventory](../04-rhce/ansible-setup-inventory.md) | [First Playbook](../04-rhce/labs/first-playbook.md) |
| Create and use playbooks | [Ansible Playbooks](../04-rhce/ansible-playbooks.md) | [First Playbook](../04-rhce/labs/first-playbook.md) |
| Create and use variables, facts, and templates | [Ansible Vars and Templates](../04-rhce/ansible-vars-templates.md) | — |
| Create and use roles | [Ansible Roles](../04-rhce/ansible-roles.md) | [Role Web Deploy](../04-rhce/labs/role-web-deploy.md) |
| Create and use logic in playbooks | [Ansible Playbooks](../04-rhce/ansible-playbooks.md) | — |
| Use Ansible to configure target machines | [Ansible Service Deploy](../04-rhce/ansible-service-deploy.md) | — |
| Download and use roles from Ansible Galaxy | [Ansible Roles](../04-rhce/ansible-roles.md) | — |
| Use Ansible Vault for secrets | [Ansible Vars and Templates](../04-rhce/ansible-vars-templates.md) | — |
| Manage content with collections | [Ansible Roles](../04-rhce/ansible-roles.md) | — |
| Automate patching and updates | [Ansible Patching](../04-rhce/ansible-patching.md) | — |

---

## RHCA Infrastructure Concentration (indicative topics)

| Topic | Chapter |
|---|---|
| Advanced systemd unit configuration and hardening | [systemd Advanced](../05-rhca/systemd-advanced.md), [systemd Hardening](../05-rhca/systemd-hardening.md) |
| SELinux audit workflow and policy development | [SELinux Audit Workflow](../05-rhca/selinux/audit-workflow.md), [semanage](../05-rhca/selinux/semanage.md) |
| Advanced networking — multiple profiles, routing | [nmcli Profiles](../05-rhca/networking/nmcli-profiles.md), [Routing Method](../05-rhca/networking/routing-method.md) |
| Network diagnostics — tcpdump | [tcpdump](../05-rhca/networking/tcpdump.md) |
| Rootless Podman and container lifecycle | [Rootless](../05-rhca/containers/rootless.md), [Volumes](../05-rhca/containers/volumes.md) |
| Container secrets management and rotation | [Secrets](../05-rhca/containers/secrets.md), [Lab - Secrets Rotate](../05-rhca/containers/labs/secrets-rotate.md) |
| Quadlet / systemd container integration | [systemd Integration](../05-rhca/containers/systemd-integration.md), [Lab - Rootless Web](../05-rhca/containers/labs/rootless-web.md) |
| SELinux for containers | [SELinux Containers](../05-rhca/containers/selinux-containers.md) |
| Performance triage | [Resource Triage](../05-rhca/perf/resource-triage.md) |
| tuned profile management | [tuned](../05-rhca/perf/tuned.md) |
| System recovery procedures | [Recovery Patterns](../05-rhca/perf/recovery-patterns.md) |
| journald retention and forwarding | [journald Retention](../05-rhca/journald-retention.md) |
| Structured troubleshooting methodology | [Troubleshooting Playbook](../05-rhca/troubleshooting-playbook.md) |

---

## Next step

→ [Glossary](glossary.md)
