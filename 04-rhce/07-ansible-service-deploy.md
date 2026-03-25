
[↑ Back to TOC](#toc)

# Deploy a Service with Ansible — Firewall + SELinux
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

A complete real-world playbook that installs nginx, configures firewalld, and
handles SELinux correctly — the three pillars of RHEL service deployment.

Service deployment on RHEL is never just "install the package and start the
service". Two security subsystems gate every service before it can accept
network connections: **firewalld** controls network access at the packet level,
and **SELinux** enforces mandatory access control at the process and file level.
Both must be configured correctly, or the service silently fails — the port
is open but traffic is blocked by the firewall, or the service starts but
cannot read its configuration because the file context is wrong.

The patterns in this chapter are the direct answer to the most common RHCE
practical exam failures: services that the candidate installed and configured
correctly, but which never became reachable because firewalld or SELinux was
not handled. Ansible makes this reliable by encoding all three concerns —
software, firewall, MAC — in the same role. Deploy once, get everything.

Every section of this chapter references the project in chapter 07. Work
through the lab in `labs/02-role-web-deploy.md` after reading this chapter.

---
<a name="toc"></a>

## Table of contents

- [Project structure](#project-structure)
- [`ansible.cfg`](#ansiblecfg)
- [`inventory.ini`](#inventoryini)
- [`roles/nginx/defaults/main.yml`](#rolesnginxdefaultsmainyml)
- [`roles/nginx/tasks/main.yml`](#rolesnginxtasksmainyml)
- [`roles/nginx/handlers/main.yml`](#rolesnginxhandlersmainyml)
- [`roles/nginx/templates/nginx.conf.j2`](#rolesnginxtemplatesnginxconfj2)
- [`roles/nginx/files/index.html`](#rolesnginxfilesindexhtml)
- [`site.yml`](#siteyml)
- [Run it](#run-it)
- [Verify](#verify)
- [SELinux and firewalld reference](#selinux-and-firewalld-reference)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Project structure

```text
web-deploy/
  ansible.cfg
  inventory.ini
  site.yml
  roles/
    nginx/
      defaults/main.yml
      tasks/main.yml
      handlers/main.yml
      templates/nginx.conf.j2
      files/index.html
```


[↑ Back to TOC](#toc)

---

## `ansible.cfg`

```ini
[defaults]
inventory = inventory.ini
remote_user = rhel
host_key_checking = False
stdout_callback = yaml

[privilege_escalation]
become = True
become_method = sudo
```


[↑ Back to TOC](#toc)

---

## `inventory.ini`

```ini
[webservers]
web01 ansible_host=192.168.1.101

[webservers:vars]
nginx_port=80
```


[↑ Back to TOC](#toc)

---

## `roles/nginx/defaults/main.yml`

```yaml
---
nginx_port: 80
nginx_root: /var/www/html
nginx_user: nginx
```

---

## `roles/nginx/tasks/main.yml`

```yaml
---
- name: Install nginx
  ansible.builtin.dnf:
    name: nginx
    state: present
  tags: packages

- name: Create web root
  ansible.builtin.file:
    path: "{{ nginx_root }}"
    state: directory
    owner: "{{ nginx_user }}"
    group: "{{ nginx_user }}"
    mode: '0755'
    setype: httpd_sys_content_t     # SELinux type — correct for web content

- name: Deploy index.html
  ansible.builtin.copy:
    src: index.html
    dest: "{{ nginx_root }}/index.html"
    owner: "{{ nginx_user }}"
    group: "{{ nginx_user }}"
    mode: '0644'
    setype: httpd_sys_content_t     # ensure correct SELinux context

- name: Deploy nginx config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: nginx -t -c %s       # validate config before applying
  notify: Reload nginx

- name: Allow nginx port in SELinux (if non-standard)
  community.general.seport:
    ports: "{{ nginx_port }}"
    proto: tcp
    setype: http_port_t
    state: present
  when: nginx_port != 80 and nginx_port != 443

- name: Allow http through firewalld
  ansible.posix.firewalld:
    service: http
    state: enabled
    permanent: true
    immediate: true
  when: nginx_port == 80

- name: Allow custom port through firewalld
  ansible.posix.firewalld:
    port: "{{ nginx_port }}/tcp"
    state: enabled
    permanent: true
    immediate: true
  when: nginx_port != 80

- name: Ensure nginx is started and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true
  tags: service
```

---

## `roles/nginx/handlers/main.yml`

```yaml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded

- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

---

## `roles/nginx/templates/nginx.conf.j2`

```jinja2
user {{ nginx_user }};
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    sendfile            on;
    keepalive_timeout   65;

    server {
        listen       {{ nginx_port }};
        server_name  {{ inventory_hostname }};
        root         {{ nginx_root }};
        index        index.html;

        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
    }
}
```


[↑ Back to TOC](#toc)

---

## `roles/nginx/files/index.html`

```html
<!DOCTYPE html>
<html>
<head><title>RHEL Lab</title></head>
<body><h1>Deployed by Ansible</h1></body>
</html>
```


[↑ Back to TOC](#toc)

---

## `site.yml`

```yaml
---
- name: Deploy nginx web server
  hosts: webservers
  become: true

  roles:
    - nginx
```

---

## Run it

```bash
# Validate YAML syntax before anything else
ansible-playbook site.yml --syntax-check

# Dry run first
ansible-playbook site.yml --check --diff

# Apply
ansible-playbook site.yml

# Apply with verbose output
ansible-playbook site.yml -v
```


[↑ Back to TOC](#toc)

---

## Verify

```bash
# HTTP response from control node
curl http://192.168.1.101/
```

Expected: `Deployed by Ansible`

```bash
# Confirm firewalld rule is active
ansible webservers -m ansible.builtin.command -a "firewall-cmd --list-all"

# Confirm SELinux context on web root
ansible webservers -m ansible.builtin.command -a "ls -lZ /var/www/html/"

# Confirm nginx is running and enabled
ansible webservers -m ansible.builtin.service_facts
```


[↑ Back to TOC](#toc)

---

## SELinux and firewalld reference

### SELinux contexts for web services

| Directory / file | Correct SELinux type | Purpose |
|---|---|---|
| `/var/www/html` | `httpd_sys_content_t` | Standard web content — read-only for httpd |
| `/var/www/html/uploads` | `httpd_sys_rw_content_t` | Content httpd can write |
| `/etc/nginx/nginx.conf` | `httpd_config_t` | Service configuration |
| `/var/log/nginx/` | `httpd_log_t` | Service log files |

Use `setype:` in `ansible.builtin.file` and `ansible.builtin.copy` tasks to
set context inline. For directories that already exist, use
`community.general.sefcontext` plus `ansible.builtin.command: restorecon -Rv`:

```yaml
- name: Set SELinux context on custom web root
  community.general.sefcontext:
    target: '/srv/webapp(/.*)?'
    setype: httpd_sys_content_t
    state: present

- name: Apply SELinux context
  ansible.builtin.command: restorecon -Rv /srv/webapp
  changed_when: false
```

### SELinux booleans for common services

| Boolean | Effect |
|---|---|
| `httpd_can_network_connect` | Allow nginx/httpd to make outbound network connections |
| `httpd_can_network_connect_db` | Allow httpd to connect to a database |
| `httpd_use_nfs` | Allow httpd to serve content from NFS mounts |

```yaml
- name: Allow nginx to connect to upstream
  ansible.posix.seboolean:
    name: httpd_can_network_connect
    state: true
    persistent: true
```

### firewalld zones

| Zone | Default trust | Use for |
|---|---|---|
| `public` | Untrusted | Internet-facing interfaces |
| `internal` | Trusted | Internal network interfaces |
| `dmz` | Partial trust | DMZ hosts |

Always specify the zone in playbooks to avoid relying on the default:

```yaml
- name: Allow https in the public zone
  ansible.posix.firewalld:
    service: https
    zone: public
    state: enabled
    permanent: true
    immediate: true
```

> **Exam tip:** If a service is installed and running but not reachable, check
> firewalld first (`firewall-cmd --list-all`), then SELinux (`ausearch -m
> AVC -ts recent`). These two are responsible for the majority of "service
> works locally but not remotely" failures.

[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| `firewalld` rule added without `immediate: true` | Rule is permanent but not active until next reboot | Always set both `permanent: true` and `immediate: true` |
| Wrong SELinux type on custom web root | nginx starts, serves 403 Forbidden | Set `setype: httpd_sys_content_t`; run `restorecon -Rv /custom/path` |
| Non-standard port not registered in SELinux | nginx fails to start; audit log shows AVC denial | Use `community.general.seport` to add the port to `http_port_t` |
| `validate:` path incorrect in template task | Task fails with "command not found" | Use the full path: `validate: /usr/sbin/nginx -t -c %s` |
| SELinux in Permissive mode masking real problems | Playbook runs fine in lab, fails in production (Enforcing) | Never test with `setenforce 0`; test in Enforcing mode from the start |
| `ansible.posix` collection not installed | `ERROR! couldn't resolve module/action 'ansible.posix.firewalld'` | `ansible-galaxy collection install ansible.posix` |

[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`ansible.builtin.service` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) | Start, stop, enable services idempotently |
| [`ansible.posix.firewalld` module](https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html) | Manage firewalld zones and services from Ansible |
| [`community.general.sefcontext` module](https://docs.ansible.com/ansible/latest/collections/community/general/sefcontext_module.html) | Manage SELinux file contexts from Ansible |
| [RHEL System Roles — httpd](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/automating_system_administration_by_using_rhel_system_roles/index) | Red Hat-supported role for web server deployment |

---


[↑ Back to TOC](#toc)

## Next step

→ [Patch Workflow + Reporting](08-ansible-patching.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
