# Lab: Resource Triage and tuned
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
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
  - [1 — Baseline triage](#1--baseline-triage)
  - [2 — Generate load and re-check](#2--generate-load-and-re-check)
  - [3 — Switch a tuned profile](#3--switch-a-tuned-profile)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Why this matters in production](#why-this-matters-in-production)
- [Extension tasks](#extension-tasks)
- [Next step](#next-step)


## Prerequisites

- Completed [Resource Triage](../01-resource-triage.md) and [tuned](../02-tuned.md)
- `tuned` installed: `sudo dnf install -y tuned && sudo systemctl enable --now tuned`
- VM snapshot taken


[↑ Back to TOC](#toc)

---

## Background

Capture a quick CPU/mem/IO snapshot, create artificial load, then change the
active `tuned` profile and confirm with `tuned-adm active`.


[↑ Back to TOC](#toc)

---

## Success criteria

- [ ] You recorded load average and top CPU processes under load
- [ ] `tuned-adm active` shows a profile you selected (e.g. `throughput-performance` or `virtual-guest`)
- [ ] Cleanup restored the **saved** previous profile (not a hardcoded name)


[↑ Back to TOC](#toc)

---

## Steps

### 1 — Baseline triage

```bash
uptime
free -h
ps aux --sort=-%cpu | head
tuned-adm active
```

### 2 — Generate load and re-check

```bash
# Short CPU burn (Ctrl-C after a few seconds if needed)
timeout 20 yes > /dev/null &
sleep 2
uptime
ps aux --sort=-%cpu | head
wait 2>/dev/null || true
```

### 3 — Switch a tuned profile

```bash
PREV=$(tuned-adm active | awk -F': ' '{print $2}')
echo "$PREV" | tee /tmp/tuned-prev-profile.txt
echo "Previous profile: $PREV"
sudo tuned-adm profile throughput-performance
tuned-adm active
tuned-adm verify || true
# optional: head /usr/lib/tuned/profiles/throughput-performance/tuned.conf
```


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
# Restore the profile saved in step 3 (do not hardcode virtual-guest)
PREV=$(cat /tmp/tuned-prev-profile.txt 2>/dev/null || true)
if [ -n "$PREV" ]; then
  sudo tuned-adm profile "$PREV"
else
  echo "No saved profile; set one from: tuned-adm list"
fi
tuned-adm active
rm -f /tmp/tuned-prev-profile.txt
```


[↑ Back to TOC](#toc)

---

## Troubleshooting guide

| Symptom | Fix |
|---|---|
| tuned-adm fails | `systemctl status tuned`; install package |
| Profile not found | `tuned-adm list`; use a listed name |


[↑ Back to TOC](#toc)

---

## Why this matters in production

Operators must separate "host is busy" from "host is mis-tuned" before
scaling hardware.


[↑ Back to TOC](#toc)

---

## Extension tasks

- Create a custom profile under `/etc/tuned/profiles/lab-local/` with `include=`
- Correlate `iostat` during a disk write stress


[↑ Back to TOC](#toc)

---

## Next step

→ [Lab Environments Overview](../../../90-labs/01-index.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
