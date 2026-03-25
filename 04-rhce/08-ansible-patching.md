
[↑ Back to TOC](#toc)

# Patch Workflow + Reporting
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

A repeatable, auditable patch process is one of the most valuable things you
can automate with Ansible.

Manual patching at scale is untenable. Running `dnf update -y` interactively
across 200 hosts takes hours, produces no structured audit trail, offers no
consistent pre/post health checks, and depends entirely on the operator
remembering to follow the correct procedure at 2 AM during a maintenance
window. One missed step — forgetting to check for failed systemd units, or
not rebooting after a kernel update — can leave a host in an inconsistent
state that manifests as an incident weeks later.

Ansible's patch playbook turns the procedure into code. The same checks run
every time, on every host, in the same order. The `serial` keyword controls
the blast radius: instead of updating all 200 hosts simultaneously (risky),
you can patch one host at a time, verify it, and proceed. If a host fails
post-patch checks, the playbook stops before the problem propagates to the
rest of the fleet.

The `pre_tasks` / `post_tasks` structure is the key architectural pattern
here. Pre-tasks establish baseline state and pre-conditions. The main tasks
do the actual patching. Post-tasks verify that the host is healthy after
patching. Ansible's `fail` module turns a policy check into an automated
gate: if a post-patch health check fails, the playbook aborts with a clear
error message instead of silently continuing to the next host.

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
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## The patch workflow

```text
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
ansible all -m ansible.builtin.command -a "dnf check-update" --become
```

Or use the `dnf` module:

```bash
ansible all -m ansible.builtin.dnf -a "list=updates" --become
```

Check which packages have security advisories:

```bash
ansible all -m ansible.builtin.command \
  -a "dnf updateinfo list security" --become
```


[↑ Back to TOC](#toc)

---

## Patch playbook

```yaml
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

> **Exam tip:** The `serial` keyword controls how many hosts are patched at
> once. `serial: 1` is safest for critical services — it patches one host,
> verifies it, then moves to the next. Use `serial: "20%"` to patch 20% of
> the fleet at a time.

---

## Run the patch playbook

```bash
# Patch all hosts (no auto-reboot)
ansible-playbook -i inventory.ini patch.yml

# Patch only webservers
ansible-playbook -i inventory.ini patch.yml -e "target_hosts=webservers"

# Patch with auto-reboot enabled
ansible-playbook -i inventory.ini patch.yml -e "allow_reboot=true"

# Patch a single host
ansible-playbook -i inventory.ini patch.yml --limit web01
```


[↑ Back to TOC](#toc)

---

## Check mode — preview without applying

```bash
ansible-playbook -i inventory.ini patch.yml --check
```

In check mode, the `dnf` module will report which packages would be updated
without downloading or installing them.


[↑ Back to TOC](#toc)

---

## Reporting: view the patch log

```bash
ansible all -m ansible.builtin.command \
  -a "tail -20 /var/log/ansible-patching.log" --become
```

Fetch the log files back to the control node:

```bash
ansible all -m ansible.builtin.fetch \
  -a "src=/var/log/ansible-patching.log dest=patch-logs/ flat=no" --become
```

This creates `patch-logs/<hostname>/var/log/ansible-patching.log` for each host.


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

Apply patches for a specific CVE:

```yaml
- name: Patch for specific CVE
  ansible.builtin.dnf:
    name: "*"
    bugfix: true
    state: latest
  # Note: use cves parameter when targeting a specific CVE
```

List available security advisories before patching:

```bash
ansible all -m ansible.builtin.command \
  -a "dnf updateinfo list security" --become
```


[↑ Back to TOC](#toc)

---

## Worked example

### Safe rolling patch workflow with pre/post health checks

This example extends the basic patch playbook with a realistic pre/post check
suite appropriate for a fleet of web application servers. It checks service
health before patching, patches one host at a time, and performs structured
post-patch verification before moving on.

```yaml
---
# rolling-patch.yml
- name: Rolling patch — web application fleet
  hosts: "{{ target_hosts | default('webservers') }}"
  become: true
  serial: 1              # one host at a time
  max_fail_percentage: 0 # abort entire play if any host fails

  vars:
    patch_log: /var/log/ansible-patching.log
    critical_services:
      - nginx
      - firewalld

  pre_tasks:
    - name: "[PRE] Verify all critical services are running before patching"
      ansible.builtin.service_facts:

    - name: "[PRE] Assert critical services are active"
      ansible.builtin.assert:
        that: >
          ansible_facts.services[item + '.service'] is defined
          and ansible_facts.services[item + '.service'].state == 'running'
        fail_msg: "{{ item }} is NOT running on {{ inventory_hostname }} — aborting patch"
      loop: "{{ critical_services }}"

    - name: "[PRE] Check for failed systemd units before patching"
      ansible.builtin.command: systemctl --failed --no-legend
      register: pre_failed_units
      changed_when: false

    - name: "[PRE] Abort if units were already failed before patching"
      ansible.builtin.fail:
        msg: >
          Host {{ inventory_hostname }} has failed units BEFORE patching:
          {{ pre_failed_units.stdout }}
          Fix these before running the patch playbook.
      when: pre_failed_units.stdout | length > 0

    - name: "[PRE] Record disk usage before patching"
      ansible.builtin.command: df -h /
      register: pre_disk
      changed_when: false

    - name: "[PRE] Log patch start"
      ansible.builtin.lineinfile:
        path: "{{ patch_log }}"
        line: >-
          {{ ansible_date_time.iso8601 }} BEGIN {{ inventory_hostname }}
          kernel={{ ansible_kernel }}
        create: true
        mode: '0640'

  tasks:
    - name: "[PATCH] Update package cache"
      ansible.builtin.dnf:
        update_cache: true
      changed_when: false

    - name: "[PATCH] Apply all available updates"
      ansible.builtin.dnf:
        name: "*"
        state: latest
      register: dnf_result

    - name: "[PATCH] Log updated packages"
      ansible.builtin.lineinfile:
        path: "{{ patch_log }}"
        line: >-
          {{ ansible_date_time.iso8601}} PACKAGES {{ inventory_hostname }}
          changed={{ dnf_result.changed }}
          packages={{ dnf_result.results | default([]) | length }}
      when: dnf_result.changed

  post_tasks:
    - name: "[POST] Gather new kernel version"
      ansible.builtin.command: uname -r
      register: new_kernel
      changed_when: false

    - name: "[POST] Check for failed systemd units after patching"
      ansible.builtin.command: systemctl --failed --no-legend
      register: post_failed_units
      changed_when: false

    - name: "[POST] Fail if new units failed after patching"
      ansible.builtin.fail:
        msg: >
          Patch introduced service failures on {{ inventory_hostname }}:
          {{ post_failed_units.stdout }}
      when: post_failed_units.stdout | length > 0

    - name: "[POST] Verify critical services still running after patch"
      ansible.builtin.service_facts:

    - name: "[POST] Assert critical services active post-patch"
      ansible.builtin.assert:
        that: >
          ansible_facts.services[item + '.service'] is defined
          and ansible_facts.services[item + '.service'].state == 'running'
        fail_msg: "{{ item }} is NOT running after patching {{ inventory_hostname }}"
      loop: "{{ critical_services }}"

    - name: "[POST] Check if reboot required (new kernel)"
      ansible.builtin.command: needs-restarting -r
      register: reboot_check
      changed_when: false
      failed_when: false
      # needs-restarting exits 1 if reboot is needed (not an error for us)

    - name: "[POST] Reboot if new kernel installed and allow_reboot is true"
      ansible.builtin.reboot:
        reboot_timeout: 600
        post_reboot_delay: 30
        msg: "Rebooting {{ inventory_hostname }} after kernel update"
      when:
        - reboot_check.rc == 1
        - allow_reboot | default(false) | bool

    - name: "[POST] Re-verify services after reboot"
      ansible.builtin.service_facts:
      when:
        - reboot_check.rc == 1
        - allow_reboot | default(false) | bool

    - name: "[POST] Final assertion after reboot"
      ansible.builtin.assert:
        that: >
          ansible_facts.services[item + '.service'] is defined
          and ansible_facts.services[item + '.service'].state == 'running'
        fail_msg: "{{ item }} did not come back after reboot on {{ inventory_hostname }}"
      loop: "{{ critical_services }}"
      when:
        - reboot_check.rc == 1
        - allow_reboot | default(false) | bool

    - name: "[POST] Log patch completion"
      ansible.builtin.lineinfile:
        path: "{{ patch_log }}"
        line: >-
          {{ ansible_date_time.iso8601 }} END {{ inventory_hostname }}
          new_kernel={{ new_kernel.stdout }}
          status=OK
```

Run the rolling patch:

```bash
# Preview
ansible-playbook -i inventory.ini rolling-patch.yml --check

# Apply with reboot enabled
ansible-playbook -i inventory.ini rolling-patch.yml -e "allow_reboot=true"

# Collect all patch logs
ansible-playbook -i inventory.ini rolling-patch.yml
ansible all -m ansible.builtin.fetch \
  -a "src=/var/log/ansible-patching.log dest=reports/ flat=no"
```

[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| No `serial:` keyword | All hosts patched simultaneously; one failure aborts all | Always use `serial: 1` or `serial: "10%"` for production patch playbooks |
| `failed_when` not set on `dnf check-update` | Exit code 100 (updates available) treated as failure; playbook aborts before patching | Set `failed_when: dnf_check.rc not in [0, 100]` |
| No pre-patch health checks | Patch playbook masks pre-existing failures, making root cause unclear | Add `pre_tasks` that assert service health before patching begins |
| `reboot` task without `reboot_timeout` | Slow hosts appear unreachable after reboot; playbook fails with UNREACHABLE | Set `reboot_timeout: 600` for hosts with slow startup |
| Patching without VM snapshot | No rollback path if patch breaks the system | Take snapshots before patching via your virtualisation API; consider making this a pre-task |
| `max_fail_percentage` not set | One host failure doesn't stop remaining hosts from being patched | Set `max_fail_percentage: 0` to stop the play if any host fails post-patch checks |

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
