
[↑ Back to TOC](#toc)

# Lab: Write Your First Playbook
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCE
**Estimated time:** 40 minutes
**Topology:** Single VM (using localhost as managed node)

---
<a name="toc"></a>

## Table of contents

- [Background](#background)
- [Prerequisites](#prerequisites)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Create the project directory](#1-create-the-project-directory)
  - [2 — Create the inventory](#2-create-the-inventory)
  - [3 — Create the playbook](#3-create-the-playbook)
  - [4 — Create the template](#4-create-the-template)
  - [5 — Run in check mode first](#5-run-in-check-mode-first)
  - [6 — Apply the playbook](#6-apply-the-playbook)
  - [7 — Run again to confirm idempotence](#7-run-again-to-confirm-idempotence)
  - [8 — Trigger the handler](#8-trigger-the-handler)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)


## Background

In production environments, a single service deployment typically involves
installing packages, creating service accounts, setting up directory trees
with correct ownership and permissions, deploying configuration from templates,
and starting the service — all in a specific order, all idempotently. A
manual runbook for this sequence is a liability: steps get missed, executed
out of order, or skipped when time pressure is high during incidents.

The playbook pattern you build in this lab is the direct solution. Once it
exists, any engineer runs it with a single command and gets the same result
every time. When the configuration changes, the template is updated in Git,
the playbook is re-run, and only the diff is applied. When a new server needs
to be provisioned, the same playbook runs on it — no manual steps, no
tribal knowledge required.

This four-part pattern (install → user/dir → config from template → handler)
is the atomic unit of Ansible. Everything you do in later labs and in the
RHCE exam is a combination and extension of exactly this structure.

---

## Prerequisites

- Completed [Ansible Setup and Inventory](../03-ansible-setup-inventory.md) and [Ansible Playbooks](../04-ansible-playbooks.md)
- `ansible-core` installed: `sudo dnf install -y ansible-core`
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Success criteria

- A local inventory targeting `localhost` is working
- A playbook installs packages, creates a user, deploys a config file
- The playbook is idempotent (run twice, second run shows no changes)
- A handler triggers correctly when config changes

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Create the project directory

```bash
mkdir ~/ansible-lab && cd ~/ansible-lab
```

> **Hint:** All subsequent commands assume you are inside `~/ansible-lab`.
> Ansible looks for `ansible.cfg` and the `templates/` directory relative
> to the directory you run `ansible-playbook` from.

### 2 — Create the inventory

```bash
cat > inventory.ini << 'EOF'
[local]
localhost ansible_connection=local
EOF
```

> **✅ Verify**
> ```bash
> ansible -i inventory.ini local -m ansible.builtin.ping
> ```
> Expected: `localhost | SUCCESS`
>

> **Hint:** `ansible_connection=local` bypasses SSH entirely. Ansible runs
> the task directly on the control node using Python. This is the standard
> approach when your control node is also your only test target.


[↑ Back to TOC](#toc)

---

### 3 — Create the playbook

```bash
vim site.yml
```

```yaml
---
- name: Configure local system
  hosts: local
  become: true

  vars:
    app_user: labuser
    app_dir: /srv/labapp
    app_port: 8080

  tasks:
    - name: Install required packages
      ansible.builtin.dnf:
        name:
          - vim
          - curl
          - git
        state: present

    - name: Create application group
      ansible.builtin.group:
        name: appteam
        state: present

    - name: Create application user
      ansible.builtin.user:
        name: "{{ app_user }}"
        groups: appteam
        shell: /bin/bash
        create_home: true
        comment: "Lab Application User"
        state: present

    - name: Create application directory
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        group: appteam
        mode: '0775'

    - name: Deploy application config
      ansible.builtin.template:
        src: templates/app.conf.j2
        dest: "{{ app_dir }}/app.conf"
        owner: "{{ app_user }}"
        group: appteam
        mode: '0640'
      notify: Show config deployed

  handlers:
    - name: Show config deployed
      ansible.builtin.debug:
        msg: "Config deployed to {{ app_dir }}/app.conf"
```

> **Hint:** Note the FQCN module names (`ansible.builtin.dnf` not just `dnf`).
> These are required in modern playbooks and expected in the RHCE exam.

---

### 4 — Create the template

```bash
mkdir -p templates
cat > templates/app.conf.j2 << 'EOF'
# Application configuration
# Managed by Ansible — do not edit by hand
# Generated: {{ ansible_date_time.iso8601 }}

[server]
port = {{ app_port }}
user = {{ app_user }}
dir  = {{ app_dir }}

[host]
hostname = {{ inventory_hostname }}
os       = {{ ansible_distribution }} {{ ansible_distribution_version }}
EOF
```

> **Hint:** `inventory_hostname` is a magic variable — it is the name of the
> current host in the inventory (here: `localhost`). `ansible_distribution`
> and `ansible_distribution_version` are facts gathered automatically.


[↑ Back to TOC](#toc)

---

### 5 — Run in check mode first

```bash
ansible-playbook -i inventory.ini site.yml --check
```

Review what would change. No changes are applied.

> **Hint:** Check mode on a `template` task requires the template source file
> to exist and the Jinja2 variables to be defined, but it does not write the
> rendered file to the target host. If the template references a variable that
> doesn't exist, the check will fail here — which is useful early feedback.


[↑ Back to TOC](#toc)

---

### 6 — Apply the playbook

```bash
ansible-playbook -i inventory.ini site.yml
```

Note the tasks that show `changed` vs `ok`.

> **✅ Verify**
> ```bash
> cat /srv/labapp/app.conf
> id labuser
> ```
> Config file present; user created.
>

> **Hint:** The `become: true` at the play level means all tasks run with
> sudo. If you see `Permission denied` errors, confirm your user can run
> `sudo` without a password, or run `ansible-playbook` with `--ask-become-pass`.


[↑ Back to TOC](#toc)

---

### 7 — Run again to confirm idempotence

```bash
ansible-playbook -i inventory.ini site.yml
```

Expected: all tasks show `ok` — no changes. This confirms idempotence.

> **Hint:** If any task shows `changed` on the second run, that task is not
> idempotent. The most common cause is a `command` or `shell` task that
> always runs. Check for missing `creates:`, `changed_when:`, or
> `when:` guards.


[↑ Back to TOC](#toc)

---

### 8 — Trigger the handler

Change the port in the playbook:

```yaml
    app_port: 9090
```

```bash
ansible-playbook -i inventory.ini site.yml
```

Look for: `Deploy application config` shows `changed` and the handler runs.

```bash
grep port /srv/labapp/app.conf
```

Expected: `port = 9090`

> **Hint:** Handlers only run when the notifying task reports `changed`. If
> you run the playbook again without changing anything, `Deploy application
> config` shows `ok` and the handler does NOT run. This is correct —
> the service doesn't need to be restarted if the config didn't change.


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
cd ~
sudo userdel -r labuser
sudo groupdel appteam
sudo rm -rf /srv/labapp
rm -rf ~/ansible-lab
```

---


[↑ Back to TOC](#toc)

## Troubleshooting guide

| Symptom | Likely cause | Diagnostic command | Fix |
|---|---|---|---|
| `localhost \| UNREACHABLE` on `ping` | `ansible-core` not installed or inventory syntax wrong | `ansible --version` | `sudo dnf install -y ansible-core`; check `inventory.ini` for typos |
| `Permission denied` on any task | `become: true` missing or sudo requires a password | `sudo -l` to check sudo rules | Add `become: true` to the play; add `--ask-become-pass` to the command |
| `Handler didn't run` | Task showed `ok` not `changed` | Re-read task output carefully | Handler only runs when the notifying task reports `changed` |
| `Template not found` | Wrong path in `src:` | `ls templates/` | Confirm `src: templates/app.conf.j2` matches the actual file path |
| `AnsibleUndefinedVariable` in template | Variable used in template is not defined | `ansible -m setup localhost` | Add the variable to `vars:` or check for typos in the variable name |
| `ERROR! Syntax Error while loading YAML` | YAML indentation error in playbook | `ansible-playbook site.yml --syntax-check` | Fix indentation — use spaces not tabs; all task properties must be indented 6 spaces under `tasks:` |
| `FAILED! => {"msg": "Missing sudo password"}` | Running as non-root user without passwordless sudo | `sudo visudo` | Add `yourusername ALL=(ALL) NOPASSWD: ALL` to sudoers for lab use only |
| Package install fails with `No package found` | DNF repo not configured or no network | `dnf repolist` | Ensure subscription or repo is configured: `sudo subscription-manager repos --list` |

[↑ Back to TOC](#toc)

---

## Extension tasks

### Extension 1 — Add a second group and per-host variables

1. Add a second host to the inventory using `localhost` again with a different
   alias and a different `app_port` value:

   ```ini
   [local]
   localhost  ansible_connection=local app_port=8080
   localhost2 ansible_connection=local app_port=9090
   ```

2. Re-run the playbook. Confirm each host gets its own config with the correct
   port in `/srv/labapp/app.conf`.

   > **Hint:** `localhost2` is a fake alias. Ansible will run tasks on
   > `localhost` twice — once as `localhost` and once as `localhost2`. This
   > simulates a multi-host run without needing multiple VMs.

### Extension 2 — Add a `vars_file` and encrypt it with Ansible Vault

1. Move the `app_port` and `app_user` variables out of the playbook `vars:`
   block and into a file `vars/app.yml`.

2. Encrypt the file:

   ```bash
   ansible-vault encrypt vars/app.yml
   ```

3. Update the playbook to use `vars_files: [vars/app.yml]` and run:

   ```bash
   ansible-playbook -i inventory.ini site.yml --ask-vault-pass
   ```

4. Confirm the playbook still works and the vars file is now encrypted in the
   filesystem (`cat vars/app.yml` should show `$ANSIBLE_VAULT;1.1;AES256...`).

### Extension 3 — Add a `block` with `rescue` for robust error handling

1. Wrap the package install and user creation tasks in a `block:`.

2. Add a `rescue:` section that logs a message and creates a failure marker
   file at `/tmp/ansible-lab-failed` if the block fails.

3. Deliberately break the playbook (use a package name that doesn't exist),
   run it, and confirm the rescue handler creates the file.

4. Fix the playbook, clean up the marker file, and re-run to confirm success.

[↑ Back to TOC](#toc)

---


[↑ Back to TOC](#toc)

## Why this matters in production

This four-part pattern — install packages, manage users/dirs, deploy config
from template, notify handler — covers 80% of real-world service deployment
tasks. The moment you have this working repeatably, you have a foundation to
build every other role on.

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab — Role-Based Web Service Deploy](02-role-web-deploy.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
