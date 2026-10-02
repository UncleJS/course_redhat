# Time Synchronization — chrony
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Accurate clocks matter for TLS, Kerberos, logs, and Ansible. On RHEL 10 the
default NTP client is **chrony** (`chronyd`). `timedatectl set-ntp true`
enables the systemd-timesyncd/chrony integration path; for exam and production
control you should also know `/etc/chrony.conf` and `chronyc`.

```bash
sudo dnf install -y chrony
sudo systemctl enable --now chronyd
```

---
<a name="toc"></a>

## Table of contents

- [timedatectl basics](#timedatectl-basics)
- [chrony.conf](#chronyconf)
- [chronyc queries](#chronyc-queries)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)
- [Further reading](#further-reading)
- [Next step](#next-step)


## timedatectl basics

```bash
timedatectl
timedatectl status

# Timezone
sudo timedatectl set-timezone America/New_York

# Enable NTP (uses chronyd when installed and preferred)
sudo timedatectl set-ntp true
```


[↑ Back to TOC](#toc)

---

## chrony.conf

Default config: `/etc/chrony.conf`. Common directives:

```bash
sudo cp -a /etc/chrony.conf /etc/chrony.conf.bak
sudo vim /etc/chrony.conf
```

```text
# Prefer pool (multiple servers) or explicit server lines
pool 2.rhel.pool.ntp.org iburst
# server ntp.lab.example iburst

# Allow chronyd to step the clock on large offsets at start
makestep 1.0 3

# Record drift
driftfile /var/lib/chrony/drift
```

```bash
sudo systemctl restart chronyd
```


[↑ Back to TOC](#toc)

---

## chronyc queries

```bash
# Sources and reachability
chronyc sources -v
chronyc sourcestats

# Tracking vs reference
chronyc tracking

# Manual sync attempt (rarely needed)
sudo chronyc -a makestep
```


[↑ Back to TOC](#toc)

---

## Worked example

Point a lab VM at an internal NTP server and verify:

```bash
sudo sed -i 's/^pool /# pool /' /etc/chrony.conf
echo 'server 192.168.122.1 iburst' | sudo tee -a /etc/chrony.conf
sudo systemctl restart chronyd
chronyc sources -v
chronyc tracking | grep -E 'Reference|System time|Leap'
timedatectl | grep -i ntp
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Firewall blocks UDP/123 | Sources unreachable | Allow NTP egress / server ingress |
| Huge offset, no step | Apps fail TLS | `makestep` / `chronyc makestep`; check VM pause/resume |
| Wrong timezone | Local display wrong, UTC OK | `timedatectl set-timezone` |
| chronyd disabled | `NTP: inactive` | `systemctl enable --now chronyd` |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring time synchronization](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_basic_system_settings/assembly_using-chrony-to-configure-ntp_configuring-basic-system-settings) | chrony on RHEL |
| [`chrony.conf` man page](https://chrony-project.org/doc/documentation.html) | Upstream docs |
| [`timedatectl` man page](https://man7.org/linux/man-pages/man1/timedatectl.1.html) | systemd timedatectl |


[↑ Back to TOC](#toc)

---

## Next step

→ [Lab: Static IP + DNS Validation](labs/01-static-ip-dns.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
