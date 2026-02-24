# Lab: Role-Based Web Service Deploy

**Track:** RHCE
**Estimated time:** 60 minutes
**Topology:** Single VM (localhost) or two VMs if available

---

## Prerequisites

- Completed [Roles and Collections](../ansible-roles.md) and [Deploy a Service with Ansible](../ansible-service-deploy.md)
- `ansible-core` and `ansible.posix` collection installed
- VM snapshot taken

---

## Success criteria

- An `nginx` role deploys nginx with a custom port (8080)
- firewalld is configured via Ansible
- SELinux context is set correctly via Ansible
- Playbook is idempotent
- Curl confirms the service is accessible

---

## Steps

### 1 — Install required collections

```bash
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.general
```

### 2 — Create project structure

```bash
mkdir ~/role-lab && cd ~/role-lab
ansible-galaxy role init roles/nginx
```

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

### 4 — Define role defaults

```bash
cat > roles/nginx/defaults/main.yml << 'EOF'
---
nginx_port: 80
nginx_root: /var/www/html
nginx_user: nginx
EOF
```

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

### 10 — Confirm idempotence

```bash
ansible-playbook site.yml
```

All tasks: `ok`. No changes.

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

## Why this matters in production

Roles are the unit of reuse in Ansible. An `nginx` role can be dropped into
any project and parameterised for dev (port 8080) vs prod (port 443). The
SELinux and firewalld steps inside the role mean the service is correctly
hardened by default — the role encapsulates all three: software, firewall,
and MAC policy.

---

## Next step

→ [Advanced Infrastructure — RHCA Track](../../05-rhca/troubleshooting-playbook.md)
