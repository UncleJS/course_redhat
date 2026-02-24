# Variables, Templates, and Files

Variables and templates let you write reusable playbooks that work across
different environments (dev, staging, prod) without changing the code.

---

## Defining variables

### In the playbook (inline)

```yaml
---
- name: Deploy web app
  hosts: webservers
  become: true
  vars:
    app_port: 8080
    app_user: webapp
    app_dir: /srv/webapp

  tasks:
    - name: Create app directory
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
```

### In a vars file

```yaml
# vars/main.yml
app_port: 8080
app_user: webapp
app_dir: /srv/webapp
db_host: db01.lab.local
```

```yaml
- name: Deploy web app
  hosts: webservers
  vars_files:
    - vars/main.yml
```

### In the inventory (host/group vars)

```ini
# inventory.ini
[webservers]
web01 ansible_host=192.168.1.101 app_port=8080
web02 ansible_host=192.168.1.102 app_port=8081

[webservers:vars]
app_user=webapp
```

Or as files:

```
inventory/
  group_vars/
    webservers.yml     # applies to all webservers
    all.yml            # applies to all hosts
  host_vars/
    web01.yml          # applies to web01 only
```

---

## Variable precedence (simplified, lowest to highest)

```
role defaults → inventory group_vars → inventory host_vars
  → playbook vars → extra vars (-e flag)
```

Extra vars (`-e`) always win:

```bash
ansible-playbook site.yml -e "app_port=9090"
```

---

## Variable usage in tasks

```yaml
- name: Template a config file
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf

- name: Create a user
  ansible.builtin.user:
    name: "{{ app_user }}"
    home: "{{ app_dir }}"
```

Always quote variables that are the entire YAML value to avoid type coercion:
```yaml
path: "{{ app_dir }}"    # correct
path: {{ app_dir }}      # incorrect — YAML parse error
```

---

## Jinja2 templates

Templates use Jinja2 syntax and are rendered on the managed node.

```
templates/
  nginx.conf.j2
```

```nginx
# templates/nginx.conf.j2
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    server {
        listen {{ app_port }};
        server_name {{ inventory_hostname }};

        root {{ app_dir }};

        access_log /var/log/nginx/{{ inventory_hostname }}_access.log;
    }
}
```

Deploy the template:

```yaml
- name: Deploy nginx config
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
  notify: Reload nginx
```

### Jinja2 basics

```jinja2
{# Comment #}
{{ variable }}
{{ variable | default("fallback") }}
{{ variable | upper }}

{% if app_port == 443 %}
ssl on;
{% endif %}

{% for host in groups['webservers'] %}
server {{ host }};
{% endfor %}
```

---

## The `lineinfile` module

Useful for managing single lines in config files:

```yaml
- name: Set MaxSessions in sshd_config
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?MaxSessions'
    line: 'MaxSessions 10'
    state: present
  notify: Restart sshd
```

---

## The `blockinfile` module

Manage a multi-line block:

```yaml
- name: Add hosts entries
  ansible.builtin.blockinfile:
    path: /etc/hosts
    block: |
      192.168.1.101 web01 web01.lab.local
      192.168.1.102 web02 web02.lab.local
    marker: "# {mark} ANSIBLE MANAGED BLOCK"
```

---

## Ansible Vault (secrets)

Never store passwords in plain-text vars files:

```bash
# Encrypt a vars file
ansible-vault encrypt vars/secrets.yml

# View an encrypted file
ansible-vault view vars/secrets.yml

# Edit an encrypted file
ansible-vault edit vars/secrets.yml

# Run playbook with vault
ansible-playbook site.yml --ask-vault-pass

# Or use a vault password file
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

---

## Next step

→ [Roles and Collections](ansible-roles.md)
