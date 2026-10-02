# Lab: SSH Keys and File Transfer
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCSA
**Estimated time:** 30 minutes
**Topology:** Single VM (loopback) or two VMs if available

---
<a name="toc"></a>

## Table of contents

- [Prerequisites](#prerequisites)
- [Background](#background)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Generate a key pair](#1--generate-a-key-pair)
  - [2 — Install the public key](#2--install-the-public-key)
  - [3 — Transfer with scp and rsync](#3--transfer-with-scp-and-rsync)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Why this matters in production](#why-this-matters-in-production)
- [Extension tasks](#extension-tasks)
- [Next step](#next-step)


## Prerequisites

- Completed [SSH](../12-ssh.md) (including file transfer section)
- `openssh-clients` installed; sshd running locally
- VM snapshot taken


[↑ Back to TOC](#toc)

---

## Background

Practice key auth and `scp`/`rsync` against `localhost` as `student` (or a
second lab VM if you have Multi-VM ready).


[↑ Back to TOC](#toc)

---

## Success criteria

- [ ] Passwordless `ssh student@127.0.0.1 hostname` works (or remote host)
- [ ] `scp` copied a file successfully
- [ ] `rsync -av -e ssh` synced a directory


[↑ Back to TOC](#toc)

---

## Steps

### 1 — Generate a key pair

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_lab -N ""
```

### 2 — Install the public key

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_lab.pub student@127.0.0.1
ssh -i ~/.ssh/id_ed25519_lab student@127.0.0.1 hostname
```

### 3 — Transfer with scp and rsync

```bash
echo "lab-$(date -Iseconds)" > /tmp/ssh-lab.txt
scp -i ~/.ssh/id_ed25519_lab /tmp/ssh-lab.txt student@127.0.0.1:/tmp/ssh-lab-remote.txt
ssh -i ~/.ssh/id_ed25519_lab student@127.0.0.1 cat /tmp/ssh-lab-remote.txt

mkdir -p /tmp/rsync-src && echo hi > /tmp/rsync-src/a.txt
rsync -av -e "ssh -i $HOME/.ssh/id_ed25519_lab" /tmp/rsync-src/ student@127.0.0.1:/tmp/rsync-dst/
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
rm -f ~/.ssh/id_ed25519_lab ~/.ssh/id_ed25519_lab.pub
# Optionally remove the matching line from ~/.ssh/authorized_keys
```


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Fix |
|---|---|
| Permission denied (publickey) | Check `authorized_keys` mode `600` and `.ssh` mode `700` |
| Host key prompt | Accept once; or use a known lab `known_hosts` |


[↑ Back to TOC](#toc)

---

## Why this matters in production

Key auth and `rsync` over SSH are the foundation of Ansible transport and
safe file movement without interactive passwords.


[↑ Back to TOC](#toc)

---

## Extension tasks

- Disable password authentication in a drop-in and confirm key-only login
- Use `~/.ssh/config` Host alias for the lab target


[↑ Back to TOC](#toc)

---

## Next step

→ [RHCE: Automation Mindset](../../04-rhce/01-automation-mindset.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
