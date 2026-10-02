# Lab: systemd Drop-in and Hardening
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCA
**Estimated time:** 30 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Prerequisites](#prerequisites)
- [Background](#background)
- [Success criteria](#success-criteria)
- [Steps](#steps)
  - [1 — Create a simple oneshot service](#1--create-a-simple-oneshot-service)
  - [2 — Add a drop-in](#2--add-a-drop-in)
  - [3 — Add one sandbox directive](#3--add-one-sandbox-directive)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Why this matters in production](#why-this-matters-in-production)
- [Extension tasks](#extension-tasks)
- [Next step](#next-step)


## Prerequisites

- Completed [Advanced systemd](../02-systemd-advanced.md) and [systemd Hardening](../03-systemd-hardening.md)
- VM snapshot taken


[↑ Back to TOC](#toc)

---

## Background

Practice a drop-in override and a single hardening knob without editing the
vendor unit file in place.


[↑ Back to TOC](#toc)

---

## Success criteria

- [ ] Custom unit runs successfully
- [ ] Drop-in visible in `systemctl cat`
- [ ] `PrivateTmp=yes` (or similar) appears in the effective unit


[↑ Back to TOC](#toc)

---

## Steps

### 1 — Create a simple oneshot service

```bash
sudo tee /etc/systemd/system/lab-hello.service <<'EOF'
[Unit]
Description=Lab hello oneshot

[Service]
Type=oneshot
ExecStart=/usr/bin/echo "hello from lab-hello"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start lab-hello.service
sudo systemctl status lab-hello.service --no-pager
```

### 2 — Add a drop-in

```bash
sudo systemctl edit lab-hello.service
```

Add:

```ini
[Service]
Environment=LAB_TAG=dropin
```

Or non-interactively:

```bash
sudo mkdir -p /etc/systemd/system/lab-hello.service.d
echo -e '[Service]\nEnvironment=LAB_TAG=dropin' \
  | sudo tee /etc/systemd/system/lab-hello.service.d/override.conf
sudo systemctl daemon-reload
systemctl cat lab-hello.service
```

### 3 — Add one sandbox directive

```bash
echo -e '[Service]\nPrivateTmp=yes' \
  | sudo tee /etc/systemd/system/lab-hello.service.d/sandbox.conf
sudo systemctl daemon-reload
systemctl show lab-hello.service -p PrivateTmp
sudo systemd-analyze security lab-hello.service | head
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
sudo systemctl disable --now lab-hello.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/lab-hello.service
sudo rm -rf /etc/systemd/system/lab-hello.service.d
sudo systemctl daemon-reload
```


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Fix |
|---|---|
| Drop-in ignored | Forgot `daemon-reload` |
| edit opens wrong file | Confirm path under `lab-hello.service.d/` |


[↑ Back to TOC](#toc)

---

## Why this matters in production

Drop-ins survive package updates; hardening knobs reduce blast radius when a
service is compromised.


[↑ Back to TOC](#toc)

---

## Extension tasks

- Add `ProtectSystem=strict` and observe a write failure
- Compare `systemd-analyze security` before/after


[↑ Back to TOC](#toc)

---

## Next step

→ [Journald Retention and Forwarding](../04-journald-retention.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
