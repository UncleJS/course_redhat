
[↑ Back to TOC](#toc)

# Lab: Role-Based Web Service Deploy
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCE
**Estimated time:** 60 minutes
**Topology:** Single VM (localhost) or two VMs if available

---
<a name="toc"></a>

## Table of contents

- [Background](#background)
- [Prerequisites](#prerequisites)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Install required collections](#1-install-required-collections)
  - [2 — Create project structure](#2-create-project-structure)
  - [3 — Create ansible.cfg and inventory](#3-create-ansiblecfg-and-inventory)
  - [4 — Define role defaults](#4-define-role-defaults)
  - [5 — Write role tasks](#5-write-role-tasks)
  - [6 — Write role handler](#6-write-role-handler)
  - [7 — Write nginx config template](#7-write-nginx-config-template)
  - [8 — Write site.yml](#8-write-siteyml)
  - [9 — Run check mode then apply](#9-run-check-mode-then-apply)
  - [10 — Confirm idempotence](#10-confirm-idempotence)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)


## Background

A single-file playbook that deploys a web server works in a single project.
The moment a second project needs the same web server, you face a choice:
copy-paste the playbook (and then maintain two diverging copies) or extract
the logic into a role that both projects share.

Roles are the unit of reuse in production Ansible. A well-written nginx role
that handles firewalld and SELinux correctly is a security baseline — every
project that uses it automatically gets the same hardening. When a new
SELinux policy requirement appears, you update the role once and re-run
every project's playbook.

This lab mirrors exactly the kind of task you face in the RHCE exam:
structure a role from scratch, wire it into a playbook, verify that the
service is accessible and that firewalld/SELinux are correctly configured.
The three-part check (curl response, semanage port, firewall-cmd) is the
exam verification pattern.

---

## Prerequisites

- Completed [Roles and Collections](../06-ansible-roles.md) and [Deploy a Service with Ansible](../07-ansible-service-deploy.md)
- `ansible-core` and `ansible.posix` collection installed
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Success criteria

- An `nginx` role deploys nginx with a custom port (8080)
- firewalld is configured via Ansible
- SELinux context is set correctly via Ansible
- Playbook is idempotent
- Curl confirms the service is accessible

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Install required collections

```bash
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.general
```

> **Hint:** Verify the collections installed successfully:
> ```bash
> ansible-galaxy collection list | grep -E 'ansible.posix|community.general'
> ```
> Both should appear with a version number.

### 2 — Create project structure

```bash
mkdir ~/role-lab && cd ~/role-lab
ansible-galaxy role init roles/nginx
```

> **Hint:** `ansible-galaxy role init` creates the full skeleton:
> `defaults/`, `tasks/`, `handlers/`, `templates/`, `files/`, `vars/`,
> `meta/`. You only need to populate the ones you use — leave the others
> with their empty `main.yml` stubs.

### 3 — Create ansible.cfg and inventory

```bash
cat > ansible.cfg << 'EOF'
[defaults]
inventory = inventory.ini
remote_user = rhel
host_key_checking = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
EOF

cat > inventory.ini << 'EOF'
[webservers]
localhost ansible_connection=local nginx_port=8080
EOF
```

> **Hint:** `nginx_port=8080` is a host variable set directly in the
> inventory line. It overrides the role's default of `80`. This is the
> correct mechanism for per-host customisation.

### 4 — Define role defaults

```bash
cat > roles/nginx/defaults/main.yml << 'EOF'
---
nginx_port: 80
nginx_root: /var/www/html
nginx_user: nginx
EOF
```

> **Hint:** Values in `defaults/main.yml` have the lowest priority of any
> variable source. They are intentionally overridable. Never put secrets
> or environment-specific values here.

### 5 — Write role tasks

```bash
cat > roles/nginx/tasks/main.yml << 'EOF'
---
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
    state: present

- name: Create web root
  ansible.builtin.file:
    path: "{{ nginx_root }}"
    state: directory
    owner: "{{ nginx_user }}"
    group: "{{ nginx_user }}"
    mode: '0755'
    setype: httpd_sys_content_t

- name: Deploy index.html
  ansible.builtin.copy:
    content: "<h1>Deployed by Ansible Role</h1>\n"
    dest: "{{ nginx_root }}/index.html"
    setype: httpd_sys_content_t

- name: Deploy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
  notify: Reload nginx

- name: Allow nginx non-standard port in SELinux
  community.general.seport:
    ports: "{{ nginx_port }}"
    proto: tcp
    setype: http_port_t
    state: present
  when: nginx_port not in [80, 443]

- name: Open custom port in firewalld
  ansible.posix.firewalld:
    port: "{{ nginx_port }}/tcp"
    state: enabled
    permanent: true
    immediate: true
  when: nginx_port not in [80, 443]

- name: Open http in firewalld
  ansible.posix.firewalld:
    service: http
    state: enabled
    permanent: true
    immediate: true
  when: nginx_port == 80

- name: Start and enable nginx
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
EOF
```

> **Hint:** The `when: nginx_port not in [80, 443]` condition ensures
> SELinux port labelling and the custom firewalld port rule only run when
> the port is non-standard. SELinux already knows about ports 80 and 443
> — adding them again is a no-op but clutters the audit log.

### 6 — Write role handler

```bash
cat > roles/nginx/handlers/main.yml << 'EOF'
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
EOF
```

### 7 — Write nginx config template

```bash
cat > roles/nginx/templates/nginx.conf.j2 << 'EOF'
user {{ nginx_user }};
worker_processes auto;
error_log /var/log/nginx/error.log;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    sendfile      on;

    server {
        listen      {{ nginx_port }};
        server_name {{ inventory_hostname }};
        root        {{ nginx_root }};
        index       index.html;
    }
}
EOF
```

> **Hint:** `inventory_hostname` is the name of the current host as it
> appears in the inventory — here it will be `localhost`. In a production
> inventory with real hostnames this becomes the actual server name.

### 8 — Write site.yml

```bash
cat > site.yml << 'EOF'
---
- name: Deploy nginx web server
  hosts: webservers
  become: true
  roles:
    - nginx
EOF
```

### 9 — Run check mode then apply

```bash
ansible-playbook site.yml --check
ansible-playbook site.yml
```

> **✅ Verify**
> ```bash
> curl http://localhost:8080/
> ```
> Expected: `Deployed by Ansible Role`
>
> ```bash
> sudo semanage port -l | grep http_port
> ```
> Look for: `8080` listed under `http_port_t`
>
> ```bash
> sudo firewall-cmd --list-all | grep 8080
> ```
> Look for: `8080/tcp` in the ports list

> **Hint:** If `curl` returns `connection refused`, check the nginx service
> first: `systemctl status nginx`. If it failed to start, check the config:
> `nginx -t`. If `curl` returns a response but not the expected content,
> check the web root: `ls -lZ /var/www/html/`.

### 10 — Confirm idempotence

```bash
ansible-playbook site.yml
```

All tasks: `ok`. No changes.

> **Hint:** If the SELinux `seport` task always shows `changed`, confirm
> that `community.general` is version 7.0.0 or later. Older versions had
> idempotency bugs in `seport`.


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
cd ~
ansible-playbook -i role-lab/inventory.ini role-lab/site.yml \
  -e "nginx_port=8080" --tags never ||:
sudo systemctl disable --now nginx
sudo dnf remove -y nginx
sudo semanage port -d -t http_port_t -p tcp 8080 2>/dev/null || true
sudo firewall-cmd --permanent --remove-port=8080/tcp 2>/dev/null || true
sudo firewall-cmd --reload
rm -rf ~/role-lab
```

---


[↑ Back to TOC](#toc)

## Troubleshooting guide

| Symptom | Likely cause | Diagnostic command | Fix |
|---|---|---|---|
| `UNREACHABLE! Authentication failed` | SSH key not set up or wrong user | `ssh rhel@<host>` manually | `ssh-copy-id rhel@<host>`; confirm `remote_user` in `ansible.cfg` |
| `ERROR! couldn't resolve module/action 'ansible.posix.firewalld'` | `ansible.posix` collection not installed | `ansible-galaxy collection list` | `ansible-galaxy collection install ansible.posix` |
| `ERROR! couldn't resolve module/action 'community.general.seport'` | `community.general` collection not installed | `ansible-galaxy collection list` | `ansible-galaxy collection install community.general` |
| `curl: (7) Failed to connect to localhost port 8080` | nginx not running, or wrong port, or firewall blocking | `systemctl status nginx` then `nginx -t` | Fix config error and restart nginx; verify `firewall-cmd --list-all` |
| nginx starts but serves 403 Forbidden | SELinux wrong context on web root | `ls -lZ /var/www/html/` | Run `restorecon -Rv /var/www/html/`; verify `setype: httpd_sys_content_t` in tasks |
| SELinux AVC denial in audit log | Process type not allowed | `ausearch -m AVC -ts recent` | Identify the denial and fix with `seboolean` or `sefcontext` |
| `seport` task fails with "Port already defined" | Port 8080 already has a conflicting SELinux label | `semanage port -l \| grep 8080` | Remove the conflicting label: `sudo semanage port -d -t <type> -p tcp 8080` then re-run |
| Handler not running after config change | Task showing `ok` not `changed` | Check playbook output carefully | Confirm the template actually changed (use `--diff`); handlers only run on `changed` |

[↑ Back to TOC](#toc)

---

## Extension tasks

### Extension 1 — Parameterise the role for HTTPS

1. Add TLS-related defaults to `roles/nginx/defaults/main.yml`:

   ```yaml
   nginx_tls_enabled: false
   nginx_tls_port: 443
   nginx_tls_cert: /etc/nginx/ssl/server.crt
   nginx_tls_key:  /etc/nginx/ssl/server.key
   ```

2. Add a task to generate a self-signed certificate when `nginx_tls_enabled`
   is `true`:

   ```yaml
   - name: Create SSL directory
     ansible.builtin.file:
       path: /etc/nginx/ssl
       state: directory
       mode: '0700'
     when: nginx_tls_enabled | bool

   - name: Generate self-signed certificate
     ansible.builtin.command:
       cmd: >
         openssl req -x509 -nodes -days 365 -newkey rsa:2048
         -keyout {{ nginx_tls_key }} -out {{ nginx_tls_cert }}
         -subj "/CN={{ inventory_hostname }}"
       creates: "{{ nginx_tls_cert }}"
     when: nginx_tls_enabled | bool
   ```

3. Update the template to add an SSL server block when `nginx_tls_enabled`
   is `true`.

4. Update `site.yml` to pass `nginx_tls_enabled: true` and run the playbook.
   Verify with `curl -k https://localhost/`.

### Extension 2 — Add a second role: `hardening`

1. Create a `hardening` role with `ansible-galaxy role init roles/hardening`.

2. Add tasks to:
   - Set `PermitRootLogin no` in `/etc/ssh/sshd_config` (use `lineinfile`)
   - Notify a handler that restarts `sshd`
   - Set `LoginGraceTime 30` in `/etc/ssh/sshd_config`
   - Enable the `firewalld` service

3. Update `site.yml` to apply both `nginx` and `hardening` roles.

4. Verify that `sshd` is running and the config changes are applied.

### Extension 3 — Use `group_vars` for environment differentiation

1. Create two inventory groups: `dev` and `production`.

2. Create `group_vars/dev.yml` with `nginx_port: 8080`.

3. Create `group_vars/production.yml` with `nginx_port: 80`.

4. Run the playbook against each group and confirm the correct port is used
   in each environment's nginx config.

   > **Hint:** Use `ansible-inventory --graph` to visualise the group
   > structure and `ansible-inventory --host localhost` to see which
   > variables are resolved for a given host.

[↑ Back to TOC](#toc)

---


[↑ Back to TOC](#toc)

## Why this matters in production

Roles are the unit of reuse in Ansible. An `nginx` role can be dropped into
any project and parameterised for dev (port 8080) vs prod (port 443). The
SELinux and firewalld steps inside the role mean the service is correctly
hardened by default — the role encapsulates all three: software, firewall,
and MAC policy.

---


[↑ Back to TOC](#toc)

## Next step

→ [Advanced Infrastructure — RHCA Track](../../05-rhca/01-troubleshooting-playbook.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
