# Deploy a Service with Ansible — Firewall + SELinux

A complete real-world playbook that installs nginx, configures firewalld, and
handles SELinux correctly — the three pillars of RHEL service deployment.

---

## Project structure

```
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

---

## `inventory.ini`

```ini
[webservers]
web01 ansible_host=192.168.1.101

[webservers:vars]
nginx_port=80
```

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

```nginx
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

---

## `roles/nginx/files/index.html`

```html
<!DOCTYPE html>
<html>
<head><title>RHEL Lab</title></head>
<body><h1>Deployed by Ansible</h1></body>
</html>
```

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
# Dry run first
ansible-playbook site.yml --check

# Apply
ansible-playbook site.yml

# Apply with verbose output
ansible-playbook site.yml -v
```

---

## Verify

```bash
# From control node
curl http://192.168.1.101/
```

Expected: `Deployed by Ansible`

---

## Further reading

| Resource | Notes |
|---|---|
| [`ansible.builtin.service` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) | Start, stop, enable services idempotently |
| [`ansible.posix.firewalld` module](https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html) | Manage firewalld zones and services from Ansible |
| [`community.general.sefcontext` module](https://docs.ansible.com/ansible/latest/collections/community/general/sefcontext_module.html) | Manage SELinux file contexts from Ansible |
| [RHEL System Roles — httpd](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/automating_system_administration_by_using_rhel_system_roles/index) | Red Hat-supported role for web server deployment |

---

## Next step

→ [Patch Workflow + Reporting](ansible-patching.md)
