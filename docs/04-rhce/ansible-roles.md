# Roles and Collections

Roles make playbooks reusable and shareable by organising tasks, variables,
templates, and files into a standard directory structure.

---

## Role directory structure

```
roles/
  webserver/
    defaults/
      main.yml        # Default variable values (lowest priority)
    vars/
      main.yml        # Role variables (higher priority than defaults)
    tasks/
      main.yml        # Main list of tasks
    handlers/
      main.yml        # Handlers used by this role
    templates/
      nginx.conf.j2   # Jinja2 templates
    files/
      index.html      # Static files to copy
    meta/
      main.yml        # Role metadata and dependencies
    README.md
```

---

## Create a role scaffold

```bash
ansible-galaxy role init roles/webserver
```

---

## Example role: webserver

**`roles/webserver/defaults/main.yml`**

```yaml
---
webserver_port: 80
webserver_root: /var/www/html
webserver_user: root
```

**`roles/webserver/tasks/main.yml`**

```yaml
---
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
    state: present

- name: Create web root
  ansible.builtin.file:
    path: "{{ webserver_root }}"
    state: directory
    mode: '0755'

- name: Deploy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
  notify: Reload nginx

- name: Open firewall for http
  ansible.posix.firewalld:
    service: http
    state: enabled
    permanent: true
    immediate: true

- name: Ensure nginx is started and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
```

**`roles/webserver/handlers/main.yml`**

```yaml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

---

## Use a role in a playbook

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: true
  roles:
    - webserver

- name: Configure web servers with custom port
  hosts: webservers
  become: true
  roles:
    - role: webserver
      vars:
        webserver_port: 8080
```

---

## Ansible Collections

Collections bundle modules, roles, plugins, and playbooks. The key built-in
collections for RHEL:

| Collection | Provides |
|---|---|
| `ansible.builtin` | Core modules (dnf, service, file, copy, etc.) |
| `ansible.posix` | firewalld, sysctl, at, cron |
| `community.general` | Wide variety of extras |
| `redhat.rhel_system_roles` | RHEL System Roles (timesync, selinux, etc.) |

### Install a collection

```bash
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install redhat.rhel_system_roles
```

### RHEL System Roles

RHEL ships pre-certified roles for common administration tasks:

```bash
sudo dnf install -y rhel-system-roles
```

Available roles:

| Role | Task |
|---|---|
| `timesync` | Configure chrony/NTP |
| `selinux` | Configure SELinux mode and booleans |
| `network` | Configure networking |
| `firewall` | Configure firewalld |
| `storage` | Configure LVM and filesystems |
| `certificate` | Manage TLS certificates |

Example usage:

```yaml
---
- name: Sync time with NTP
  hosts: all
  become: true
  vars:
    timesync_ntp_servers:
      - hostname: pool.ntp.org
        iburst: true

  roles:
    - redhat.rhel_system_roles.timesync
```

---

## `requirements.yml` — declare dependencies

```yaml
# requirements.yml
collections:
  - name: ansible.posix
  - name: community.general

roles:
  - name: geerlingguy.nginx
    src: https://github.com/geerlingguy/ansible-role-nginx
```

Install all at once:

```bash
ansible-galaxy install -r requirements.yml
ansible-galaxy collection install -r requirements.yml
```

---

## Next step

→ [Deploy a Service with Ansible](ansible-service-deploy.md)
