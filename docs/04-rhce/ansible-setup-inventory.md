# Ansible Setup and Inventory

Ansible is an agentless automation tool that connects to managed nodes over
SSH (or WinRM for Windows) and runs tasks. No agent is installed on target hosts.

---

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

---

## Install Ansible on RHEL 10

```bash
# Enable the Ansible module stream
sudo dnf install -y ansible-core

# Verify
ansible --version
```

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

---

## Next step

→ [Ansible Playbooks](ansible-playbooks.md)
