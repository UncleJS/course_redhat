# Ansible Setup and Inventory
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Ansible is an agentless automation tool that connects to managed nodes over
SSH (or WinRM for Windows) and runs tasks. No agent is installed on target hosts.

---
<a name="toc"></a>

## Table of contents

- [Architecture](#architecture)
- [Install Ansible on RHEL 10](#install-ansible-on-rhel-10)
- [SSH key setup (required)](#ssh-key-setup-required)
- [Inventory file](#inventory-file)
  - [INI format](#ini-format)
  - [YAML format (modern)](#yaml-format-modern)
- [ansible.cfg](#ansiblecfg)
- [Ad-hoc commands](#ad-hoc-commands)
- [Ansible modules (essential)](#ansible-modules-essential)


## Architecture

```
Control node (your workstation or jump host)
    │
    │  SSH
    │
    ├── managed node: web01
    ├── managed node: web02
    └── managed node: db01
```

| Term | Meaning |
|---|---|
| **Control node** | Where Ansible is installed and run from |
| **Managed node** | Host that Ansible configures |
| **Inventory** | List of managed nodes (hosts and groups) |
| **Playbook** | YAML file describing what to do |
| **Module** | A built-in task type (e.g., `dnf`, `copy`, `service`) |
| **Role** | A reusable, structured collection of tasks |


[↑ Back to TOC](#toc)

---

## Install Ansible on RHEL 10

```bash
# Enable the Ansible module stream
sudo dnf install -y ansible-core

# Verify
ansible --version
```


[↑ Back to TOC](#toc)

---

## SSH key setup (required)

Ansible connects via SSH. Copy your SSH key to managed nodes first:

```bash
# Generate key if needed
ssh-keygen -t ed25519 -C "ansible-control"

# Copy to managed nodes
ssh-copy-id rhel@192.168.1.101
ssh-copy-id rhel@192.168.1.102
```


[↑ Back to TOC](#toc)

---

## Inventory file

The inventory lists your managed nodes. Default location: `/etc/ansible/hosts`.
For learning, create a local `inventory.ini` file.

### INI format

```ini
# inventory.ini

[webservers]
web01 ansible_host=192.168.1.101
web02 ansible_host=192.168.1.102

[dbservers]
db01 ansible_host=192.168.1.103

[all:vars]
ansible_user=rhel
ansible_become=true
ansible_become_method=sudo
```

### YAML format (modern)

```yaml
# inventory.yaml
all:
  vars:
    ansible_user: rhel
    ansible_become: true
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.168.1.101
        web02:
          ansible_host: 192.168.1.102
    dbservers:
      hosts:
        db01:
          ansible_host: 192.168.1.103
```


[↑ Back to TOC](#toc)

---

## ansible.cfg

Project-level configuration (takes priority over global `/etc/ansible/ansible.cfg`):

```ini
# ansible.cfg  (in your project directory)
[defaults]
inventory = inventory.ini
remote_user = rhel
host_key_checking = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
become_user = root
```


[↑ Back to TOC](#toc)

---

## Ad-hoc commands

Ad-hoc commands run a single module without a playbook:

```bash
# Ping all hosts
ansible all -m ping

# Ping a specific group
ansible webservers -m ping

# Run a command on all hosts
ansible all -m command -a "uptime"

# Install a package
ansible webservers -m dnf -a "name=vim state=present"

# Gather facts about a host
ansible web01 -m setup

# Copy a file
ansible all -m copy -a "src=/etc/hosts dest=/tmp/hosts_copy"
```


[↑ Back to TOC](#toc)

---

## Ansible modules (essential)

| Module | What it does |
|---|---|
| `ping` | Test connectivity |
| `command` | Run a command (no shell features) |
| `shell` | Run a command with shell features |
| `dnf` | Manage packages |
| `service` | Manage systemd services |
| `copy` | Copy files to managed nodes |
| `template` | Render Jinja2 templates |
| `file` | Manage file/dir attributes |
| `user` | Manage users |
| `group` | Manage groups |
| `firewalld` | Manage firewalld rules |
| `selinux` | Manage SELinux mode |
| `seboolean` | Manage SELinux booleans |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Ansible — How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/index.html) | Static and dynamic inventory reference |
| [`ansible.cfg` reference](https://docs.ansible.com/ansible/latest/reference_appendices/config.html) | All configuration file options |
| [Ansible — Connection methods](https://docs.ansible.com/ansible/latest/plugins/connection.html) | SSH, local, and other connection plugins |

---

## Next step

→ [Ansible Playbooks](04-ansible-playbooks.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
