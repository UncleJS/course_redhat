
[↑ Back to TOC](#toc)

# Automation Mindset — Idempotence
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Before writing a single line of Bash or Ansible, you need to think differently
about how you manage systems.

Manual server administration does not scale. When you SSH into a machine and
run commands by hand, you produce a unique snowflake — a server whose state
exists only in your memory, a stale wiki page, or a colleague's tribal
knowledge. The moment you manage a second server, divergence begins. By server
ten, no two machines are identical and nobody can explain why.

Automation solves this by making the *description of desired state* the
primary artifact, not the sequence of commands that achieves it. A playbook,
role, or script becomes the single source of truth. Any engineer can read it,
reproduce it, test it, and apply it to one host or one thousand without
variation.

The mental model has three pillars. **Idempotency** means running the same
automation ten times produces the same result as running it once — the system
converges to the desired state and stays there. **Desired state** means you
declare what you want (`nginx is installed and running`) rather than scripting
steps (`apt-get install nginx; systemctl start nginx`). **Push vs pull** is
the architectural choice: Ansible pushes configuration from a control node
outward over SSH; tools like Puppet and Chef use agents that pull from a
central server. RHCE focuses on the push model.

This chapter is the conceptual foundation for everything that follows. Before
you write your first playbook or Bash function, internalise these patterns.
They determine whether your automation is safe to re-run on a live production
host at 3 AM or whether it makes things worse.

---
<a name="toc"></a>

## Table of contents

- [The manual administration trap](#the-manual-administration-trap)
- [Automation thinking](#automation-thinking)
  - [Imperative vs Declarative](#imperative-vs-declarative)
- [Idempotence](#idempotence)
- [Why idempotence matters](#why-idempotence-matters)
- [The "set -euo pipefail" habit for Bash](#the-set-euo-pipefail-habit-for-bash)
- [Infrastructure as Code (IaC) principles](#infrastructure-as-code-iac-principles)
- [The 4-stage automation workflow](#the-4-stage-automation-workflow)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## The manual administration trap

When you configure a server by hand:

- Steps are only in your head or a runbook
- You can't repeat the exact steps reliably
- Drift occurs (the server changes over time, documentation doesn't)
- Scaling to 10, 100, or 1000 servers is impossible


[↑ Back to TOC](#toc)

---

## Automation thinking

Automation means describing **the desired state**, not the steps to get there.

### Imperative vs Declarative

| Approach | Style | Example |
|---|---|---|
| Imperative | "Do these steps" | `mkdir /etc/myapp; cp config /etc/myapp/; chmod 640` |
| Declarative | "Ensure this state" | "Directory `/etc/myapp` exists, file present, mode 640" |

Ansible (and most modern config management) is declarative: you describe what
you want, the tool figures out how to get there.


[↑ Back to TOC](#toc)

---

## Idempotence

> An operation is **idempotent** if running it multiple times produces the
> same result as running it once.

```bash
# Not idempotent — appends a line every time you run it
echo "server = db01" >> /etc/myapp.conf

# Idempotent — only adds the line if it's not already there
grep -qxF "server = db01" /etc/myapp.conf || echo "server = db01" >> /etc/myapp.conf
```

Ansible tasks are idempotent by design. The same playbook run ten times
produces the same final state.


[↑ Back to TOC](#toc)

---

## Why idempotence matters

- **Safe to re-run**: apply the playbook on a new server OR re-apply it on an
  existing server to bring it into compliance.
- **Self-documenting**: the playbook is the source of truth for system state.
- **Auditable**: run the playbook in check mode to see what would change.
- **Drift detection**: if a playbook reports changes on a server that should
  be stable, something changed outside of automation.


[↑ Back to TOC](#toc)

---

## The "set -euo pipefail" habit for Bash

Even in scripts, think idempotently and fail safely:

```bash
#!/usr/bin/env bash
set -euo pipefail

# -e  exit on any error
# -u  treat unset variables as errors
# -o pipefail  fail if any command in a pipe fails
```

Without `set -e`, a script silently continues after errors and can cause
hard-to-debug problems.


[↑ Back to TOC](#toc)

---

## Infrastructure as Code (IaC) principles

1. **Version control everything**: store playbooks, roles, and configs in Git.
2. **Review before apply**: treat automation changes like code changes — PR/review.
3. **Test in a lab first**: never run untested automation on production.
4. **Minimal privilege**: automation accounts should have only the access they need.
5. **No secrets in code**: use Ansible Vault, environment variables, or a secrets manager.


[↑ Back to TOC](#toc)

---

## The 4-stage automation workflow

```text
Write → Test (lab) → Review → Apply (prod)
   ↑                                    |
   └────────────────────────────────────┘
              (iterate)
```

> **Exam tip:** The RHCE practical exam gives you a control node and several
> managed nodes. Spend the first five minutes verifying SSH connectivity and
> confirming `ansible all -m ping` succeeds. An unreachable host costs you
> every task that targets it.

> **Exam tip:** Always run `ansible-playbook --syntax-check` before applying
> any playbook. YAML indentation errors are the most common reason tasks fail
> silently or not at all.

[↑ Back to TOC](#toc)

---

## Worked example

### Converting a 20-step manual SOP to an Ansible playbook

A typical enterprise server build SOP might look like this (abbreviated):

```text
1.  dnf install -y httpd mod_ssl
2.  systemctl enable --now httpd
3.  firewall-cmd --permanent --add-service=http --add-service=https
4.  firewall-cmd --reload
5.  setsebool -P httpd_can_network_connect 1
6.  mkdir -p /var/www/myapp
7.  chown apache:apache /var/www/myapp
8.  chmod 0755 /var/www/myapp
9.  cp /tmp/myapp.conf /etc/httpd/conf.d/myapp.conf
10. chmod 0644 /etc/httpd/conf.d/myapp.conf
11. restorecon -Rv /var/www/myapp
12. useradd -r -s /sbin/nologin myapp
13. ...and so on for 20 steps
```

Problems: step 3 runs again on a re-provision and fails if the rule already
exists. Step 9 overwrites a locally modified file with no diff. Steps have no
error handling.

The same outcome, expressed as an idempotent playbook:

```yaml
---
- name: Build application web server
  hosts: webservers
  become: true

  vars:
    app_user: myapp
    app_dir: /var/www/myapp

  tasks:
    - name: Install httpd and mod_ssl
      ansible.builtin.dnf:
        name:
          - httpd
          - mod_ssl
        state: present

    - name: Enable httpd SELinux boolean
      ansible.posix.seboolean:
        name: httpd_can_network_connect
        state: true
        persistent: true

    - name: Create application directory
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'
        setype: httpd_sys_content_t

    - name: Create application service account
      ansible.builtin.user:
        name: "{{ app_user }}"
        system: true
        shell: /sbin/nologin
        state: present

    - name: Deploy application vhost config
      ansible.builtin.template:
        src: templates/myapp.conf.j2
        dest: /etc/httpd/conf.d/myapp.conf
        owner: root
        group: root
        mode: '0644'
      notify: Reload httpd

    - name: Open firewall for http and https
      ansible.posix.firewalld:
        service: "{{ item }}"
        state: enabled
        permanent: true
        immediate: true
      loop:
        - http
        - https

    - name: Start and enable httpd
      ansible.builtin.service:
        name: httpd
        state: started
        enabled: true

  handlers:
    - name: Reload httpd
      ansible.builtin.service:
        name: httpd
        state: reloaded
```

Run this on a fresh host: it installs everything. Run it on an existing host:
it checks each resource, changes only what drifted, and leaves everything else
untouched. The SOP is now executable, reviewable, and version-controlled.

Key differences from the manual SOP:

| Manual SOP | Ansible playbook |
|---|---|
| Fails if re-run (duplicate firewall rule) | Idempotent — checks before acting |
| No error handling between steps | Stops at first failure by default |
| State lives on the server | State declared in code (Git) |
| One engineer's tribal knowledge | Any engineer can read and run it |
| Audit trail: none | Audit trail: Git history + Ansible output |


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Using `command` or `shell` for package/service tasks | Playbook not idempotent; always shows `changed` | Use `ansible.builtin.dnf`, `ansible.builtin.service` — these track state |
| Storing secrets in plaintext vars files | Credentials visible in Git history | Encrypt with `ansible-vault encrypt vars/secrets.yml` |
| No `set -euo pipefail` in Bash scripts | Script silently continues after a failed command | Always include the three flags in the shebang block |
| Skipping `--check` before production runs | Unexpected changes applied to live hosts | Make `--check` a mandatory step in your change workflow |
| Not version-controlling playbooks | Can't roll back a broken change | `git init` the project directory before writing the first file |
| Running automation as root directly | Violates least-privilege; audit trail lost | Create a dedicated `ansible` service account with passwordless sudo |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [The Twelve-Factor App](https://12factor.net/) | Software methodology that embeds idempotent, reproducible thinking |
| [Ansible — Getting started](https://docs.ansible.com/ansible/latest/getting_started/index.html) | Official intro to the Ansible automation philosophy |
| [Infrastructure as Code (Martin Fowler)](https://martinfowler.com/bliki/InfrastructureAsCode.html) | Conceptual overview of IaC and idempotence |

---


[↑ Back to TOC](#toc)

## Next step

→ [Bash Scripting Fundamentals](02-bash-fundamentals.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
