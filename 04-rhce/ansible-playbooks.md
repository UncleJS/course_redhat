# Ansible Playbooks — Tasks and Handlers

A **playbook** is a YAML file that describes the desired state of one or more
managed nodes. It is the core artifact of Ansible automation.

---

## Playbook structure

```yaml
---
- name: Describe what this play does          # Play name
  hosts: webservers                           # Target inventory group
  become: true                                # Use sudo

  tasks:
    - name: Describe what this task does      # Task name
      module_name:                            # Module
        option1: value1
        option2: value2
```

Every task should have a `name`. It appears in output and helps with debugging.

---

## A minimal working playbook

```yaml
---
- name: Ensure vim is installed on all hosts
  hosts: all
  become: true

  tasks:
    - name: Install vim
      ansible.builtin.dnf:
        name: vim
        state: present
```

Run it:

```bash
ansible-playbook -i inventory.ini install-vim.yml
```

---

## Common task patterns

### Package management

```yaml
- name: Install multiple packages
  ansible.builtin.dnf:
    name:
      - vim
      - git
      - curl
    state: present

- name: Remove a package
  ansible.builtin.dnf:
    name: telnet
    state: absent

- name: Update all packages
  ansible.builtin.dnf:
    name: "*"
    state: latest
```

### Service management

```yaml
- name: Ensure httpd is running and enabled
  ansible.builtin.service:
    name: httpd
    state: started
    enabled: true

- name: Restart httpd
  ansible.builtin.service:
    name: httpd
    state: restarted
```

### File management

```yaml
- name: Create a directory
  ansible.builtin.file:
    path: /etc/myapp
    state: directory
    owner: root
    group: root
    mode: '0755'

- name: Copy a file
  ansible.builtin.copy:
    src: files/myapp.conf
    dest: /etc/myapp/myapp.conf
    owner: root
    group: root
    mode: '0644'

- name: Create a symlink
  ansible.builtin.file:
    src: /etc/myapp/myapp.conf
    dest: /etc/myapp.conf
    state: link
```

### User management

```yaml
- name: Create application user
  ansible.builtin.user:
    name: appuser
    groups: wheel
    shell: /bin/bash
    create_home: true
    state: present
```

---

## Handlers

Handlers run **once at the end of the play, only if notified**. They're used
for actions that should only happen when something changes (e.g., restart a
service only if its config was modified).

```yaml
---
- name: Configure sshd
  hosts: all
  become: true

  tasks:
    - name: Set SSH LoginGraceTime
      ansible.builtin.lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^LoginGraceTime'
        line: 'LoginGraceTime 30'
      notify: Restart sshd            # triggers the handler

  handlers:
    - name: Restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted
```

Key points:
- Handlers run **after all tasks** in the play complete
- A handler is only triggered if its notifying task reported `changed`
- Multiple tasks can notify the same handler — it still runs only once

---

## Check mode (dry run)

```bash
ansible-playbook -i inventory.ini site.yml --check
```

Simulates what would change without making any changes.

---

## Verbose output

```bash
ansible-playbook -i inventory.ini site.yml -v    # basic
ansible-playbook -i inventory.ini site.yml -vvv  # very verbose (shows SSH details)
```

---

## Limit to specific hosts

```bash
# Run playbook against one host only
ansible-playbook -i inventory.ini site.yml --limit web01

# Run against a group
ansible-playbook -i inventory.ini site.yml --limit webservers
```

---

## Tags

Tags let you run only specific tasks:

```yaml
- name: Install packages
  ansible.builtin.dnf:
    name: nginx
    state: present
  tags:
    - packages
    - nginx
```

```bash
# Run only tagged tasks
ansible-playbook site.yml --tags packages

# Skip tagged tasks
ansible-playbook site.yml --skip-tags packages
```

---

## Further reading

| Resource | Notes |
|---|---|
| [Ansible — Playbooks guide](https://docs.ansible.com/ansible/latest/playbook_guide/index.html) | Official playbook reference including conditionals, loops, blocks |
| [Ansible module index](https://docs.ansible.com/ansible/latest/collections/index_module.html) | Full module reference — `ansible.builtin.*` is the core set |
| [YAML specification](https://yaml.org/spec/1.2.2/) | Authoritative YAML syntax reference |

---

## Next step

→ [Variables, Templates, and Files](ansible-vars-templates.md)
