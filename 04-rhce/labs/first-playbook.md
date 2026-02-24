# Lab: Write Your First Playbook

**Track:** RHCE
**Estimated time:** 40 minutes
**Topology:** Single VM (using localhost as managed node)

---

## Prerequisites

- Completed [Ansible Setup and Inventory](../ansible-setup-inventory.md) and [Ansible Playbooks](../ansible-playbooks.md)
- `ansible-core` installed: `sudo dnf install -y ansible-core`
- VM snapshot taken

---

## Success criteria

- A local inventory targeting `localhost` is working
- A playbook installs packages, creates a user, deploys a config file
- The playbook is idempotent (run twice, second run shows no changes)
- A handler triggers correctly when config changes

---

## Steps

### 1 — Create the project directory

```bash
mkdir ~/ansible-lab && cd ~/ansible-lab
```

### 2 — Create the inventory

```bash
cat > inventory.ini << 'EOF'
[local]
localhost ansible_connection=local
EOF
```

> **✅ Verify**
> ```bash
> ansible -i inventory.ini local -m ping
> ```
> Expected: `localhost | SUCCESS`
>

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

---

### 5 — Run in check mode first

```bash
ansible-playbook -i inventory.ini site.yml --check
```

Review what would change. No changes are applied.

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

---

### 7 — Run again to confirm idempotence

```bash
ansible-playbook -i inventory.ini site.yml
```

Expected: all tasks show `ok` — no changes. This confirms idempotence.

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

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `ping` fails | `ansible-core` not installed | `sudo dnf install -y ansible-core` |
| Permission denied | `become: true` missing | Add `become: true` to the play |
| Handler didn't run | Task showed `ok` not `changed` | Handler only runs when task reports `changed` |
| Template not found | Wrong path | Check `src: templates/app.conf.j2` matches actual file |

---

## Why this matters in production

This four-part pattern — install packages, manage users/dirs, deploy config
from template, notify handler — covers 80% of real-world service deployment
tasks. The moment you have this working repeatably, you have a foundation to
build every other role on.
