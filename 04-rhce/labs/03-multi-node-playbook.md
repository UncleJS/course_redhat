# Lab: Multi-Node Ansible Playbook
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCE
**Estimated time:** 45 minutes
**Topology:** Multi-VM (controller + node1 + node2) — see [Multi-VM Labs](../../90-labs/03-multi-vm.md)

---
<a name="toc"></a>

## Table of contents

- [Prerequisites](#prerequisites)
- [Background](#background)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Inventory for two managed nodes](#1--inventory-for-two-managed-nodes)
  - [2 — Ad-hoc ping](#2--ad-hoc-ping)
  - [3 — Playbook across both nodes](#3--playbook-across-both-nodes)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Why this matters in production](#why-this-matters-in-production)
- [Extension tasks](#extension-tasks)
- [Next step](#next-step)


## Prerequisites

- Completed [Ansible Playbooks](../04-ansible-playbooks.md) and prior RHCE labs
- Multi-VM lab up: SSH as `student` to `node1` and `node2` from controller
- `ansible-core` on the controller


[↑ Back to TOC](#toc)

---

## Background

Run the same playbook on two managed nodes to prove inventory + SSH +
idempotence across the fleet — not just localhost.


[↑ Back to TOC](#toc)

---

## Success criteria

- [ ] `ansible all -m ping` succeeds for both nodes
- [ ] Playbook installs `tree` (or similar) on both; second run reports `ok` not `changed` for the package task
- [ ] You used `ansible_user=student`


[↑ Back to TOC](#toc)

---

## Steps

### 1 — Inventory for two managed nodes

On the controller:

```bash
mkdir -p ~/ansible-multi && cd ~/ansible-multi
cat > inventory.ini <<'EOF'
[web]
node1 ansible_host=192.168.122.11
node2 ansible_host=192.168.122.12

[web:vars]
ansible_user=student
ansible_become=true
EOF
```

Adjust IPs to match your Multi-VM setup.

### 2 — Ad-hoc ping

```bash
ansible all -i inventory.ini -m ping
```

### 3 — Playbook across both nodes

```bash
cat > site.yml <<'EOF'
---
- name: Ensure tree is installed
  hosts: web
  become: true
  tasks:
    - name: Install tree
      ansible.builtin.dnf:
        name: tree
        state: present
EOF

ansible-playbook -i inventory.ini site.yml
ansible-playbook -i inventory.ini site.yml   # second run: no package change
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
ansible all -i inventory.ini -m ansible.builtin.dnf -a "name=tree state=absent" --become
```


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Fix |
|---|---|
| UNREACHABLE | `ssh student@node1`; fix keys / `ansible_host` |
| Missing sudo | Ensure `student` is in `wheel` on managed nodes |


[↑ Back to TOC](#toc)

---

## Why this matters in production

EX294 and real ops assume a control node driving many hosts — inventory and
SSH scale are the point of Ansible.


[↑ Back to TOC](#toc)

---

## Extension tasks

- Add `serial: 1` and a handler restarting a service on only one node at a time
- Use a group_vars file for a package list


[↑ Back to TOC](#toc)

---

## Next step

→ [Advanced Infrastructure — RHCA Track](../../05-rhca/01-troubleshooting-playbook.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
