# Lab: firewalld Basics
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCSA
**Estimated time:** 25 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Prerequisites](#prerequisites)
- [Background](#background)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Confirm firewalld is running](#1--confirm-firewalld-is-running)
  - [2 — Allow HTTP service permanently](#2--allow-http-service-permanently)
  - [3 — Add a custom port](#3--add-a-custom-port)
  - [4 — Verify runtime and permanent](#4--verify-runtime-and-permanent)
  - [5 — Runtime-only test then discard](#5--runtime-only-test-then-discard)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Why this matters in production](#why-this-matters-in-production)
- [Extension tasks](#extension-tasks)
- [Next step](#next-step)


## Prerequisites

- Completed [Firewalling (firewalld)](../11-firewalld.md)
- Optional: `httpd` installed for a live service test
- VM snapshot taken


[↑ Back to TOC](#toc)

---

## Background

You will open HTTP (service) and TCP/8080 (port) in the default zone, reload,
and confirm both runtime and permanent stores match.


[↑ Back to TOC](#toc)

---

## Success criteria

- [ ] `firewall-cmd --list-all` shows `http` and port `8080/tcp`
- [ ] Same rules appear with `--permanent --list-all`
- [ ] You proved a runtime-only rule disappears after `--reload` without `--permanent`
- [ ] You did **not** disable firewalld or SELinux


[↑ Back to TOC](#toc)

---

## Steps

### 1 — Confirm firewalld is running

```bash
systemctl is-active firewalld
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --list-all
```

### 2 — Allow HTTP service permanently

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
sudo firewall-cmd --list-services
```

### 3 — Add a custom port

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

### 4 — Verify runtime and permanent

```bash
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --list-all
```

### 5 — Runtime-only test then discard

```bash
# Runtime only (no --permanent) — useful for a safe experiment
sudo firewall-cmd --add-port=9090/tcp
sudo firewall-cmd --list-ports | grep 9090

# Reload without saving → runtime-only rule is gone
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports | grep 9090 || echo "9090 cleared (expected)"
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
sudo firewall-cmd --permanent --remove-service=http
sudo firewall-cmd --permanent --remove-port=8080/tcp
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Fix |
|---|---|
| Permanent set but not active | Forgot `--reload` |
| Wrong zone | Check `--get-active-zones`; add `--zone=` |


[↑ Back to TOC](#toc)

---

## Why this matters in production

Use runtime rules (no `--permanent`) to test, then `--permanent` +
`--reload` to make changes durable across reboots. There is no
`firewall-cmd --immediate` flag.


[↑ Back to TOC](#toc)

---

## Extension tasks

- Add a rich rule limiting SSH from a single source CIDR
- Switch the interface to the `work` zone and re-test


[↑ Back to TOC](#toc)

---

## Next step

→ [Lab: SSH Keys and File Transfer](06-ssh-keys-transfer.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
