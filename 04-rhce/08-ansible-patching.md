
[↑ Back to TOC](#toc)

# Patch Workflow + Reporting
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

A repeatable, auditable patch process is one of the most valuable things you
can automate with Ansible.

---
<a name="toc"></a>

## Table of contents

- [The patch workflow](#the-patch-workflow)
- [Check available updates (ad-hoc)](#check-available-updates-ad-hoc)
- [Patch playbook](#patch-playbook)
- [Run the patch playbook](#run-the-patch-playbook)
- [Check mode — preview without applying](#check-mode-preview-without-applying)
- [Reporting: view the patch log](#reporting-view-the-patch-log)
- [Security patches only](#security-patches-only)


## The patch workflow

```
1. Check → what updates are available?
2. Snapshot/backup → take a VM snapshot before patching
3. Apply → run the updates
4. Verify → services still running, no failed units
5. Report → log what changed, when, on which hosts
6. Reboot → if kernel was updated (optional, per policy)
```


[↑ Back to TOC](#toc)

---

## Check available updates (ad-hoc)

```bash
ansible all -m command -a "dnf check-update" --become
```

Or use the `dnf` module:

```bash
ansible all -m dnf -a "list=updates" --become
```


[↑ Back to TOC](#toc)

---

## Patch playbook

```yaml

[↑ Back to TOC](#toc)

---
# patch.yml
- name: Patch RHEL hosts
  hosts: "{{ target_hosts | default('all') }}"
  become: true
  serial: 1                   # patch one host at a time (safe for production)

  pre_tasks:
    - name: Record pre-patch time
      ansible.builtin.set_fact:
        patch_start: "{{ ansible_date_time.iso8601 }}"

    - name: Check for available updates
      ansible.builtin.command: dnf check-update
      register: dnf_check
      changed_when: false
      failed_when: dnf_check.rc not in [0, 100]
      # rc 100 = updates available (not an error)

    - name: Log that patching is starting
      ansible.builtin.lineinfile:
        path: /var/log/ansible-patching.log
        line: "{{ ansible_date_time.iso8601 }} - Patching started on {{ inventory_hostname }}"
        create: true

  tasks:
    - name: Apply all updates
      ansible.builtin.dnf:
        name: "*"
        state: latest
        update_cache: true
      register: dnf_result

    - name: Log packages updated
      ansible.builtin.lineinfile:
        path: /var/log/ansible-patching.log
        line: "{{ ansible_date_time.iso8601 }} - Updated on {{ inventory_hostname }}: {{ dnf_result.changes | default('none') }}"
      when: dnf_result.changed

  post_tasks:
    - name: Check for failed systemd units
      ansible.builtin.command: systemctl --failed --no-legend
      register: failed_units
      changed_when: false

    - name: Fail if any units failed
      ansible.builtin.fail:
        msg: "Failed units detected after patching: {{ failed_units.stdout }}"
      when: failed_units.stdout | length > 0

    - name: Check if reboot is required
      ansible.builtin.stat:
        path: /run/reboot-required
      register: reboot_required

    - name: Report reboot needed
      ansible.builtin.debug:
        msg: "Reboot required on {{ inventory_hostname }}"
      when: reboot_required.stat.exists

    - name: Reboot if required (optional — enable per environment)
      ansible.builtin.reboot:
        reboot_timeout: 300
        msg: "Rebooting for kernel update"
      when:
        - reboot_required.stat.exists
        - allow_reboot | default(false) | bool
```

---

## Run the patch playbook

```bash
# Patch all hosts (no auto-reboot)
ansible-playbook -i inventory.ini patch.yml

# Patch only webservers
ansible-playbook -i inventory.ini patch.yml -e "target_hosts=webservers"

# Patch with auto-reboot enabled
ansible-playbook -i inventory.ini patch.yml -e "allow_reboot=true"
```


[↑ Back to TOC](#toc)

---

## Check mode — preview without applying

```bash
ansible-playbook -i inventory.ini patch.yml --check
```


[↑ Back to TOC](#toc)

---

## Reporting: view the patch log

```bash
ansible all -m command -a "tail -20 /var/log/ansible-patching.log" --become
```


[↑ Back to TOC](#toc)

---

## Security patches only

```yaml
- name: Apply security updates only
  ansible.builtin.dnf:
    name: "*"
    security: true
    state: latest
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`ansible.builtin.dnf` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/dnf_module.html) | Full options for package and update management |
| [RHEL System Roles — patch](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/automating_system_administration_by_using_rhel_system_roles/index) | Red Hat-supported patching role |
| [Red Hat Security Advisories API](https://access.redhat.com/labs/securitydataapi/) | Programmatic access to CVE and errata data |

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab: Write Your First Playbook](labs/01-first-playbook.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
