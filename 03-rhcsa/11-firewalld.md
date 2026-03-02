# Firewalling with firewalld
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

`firewalld` is the default firewall manager on RHEL 10. It uses the concept
of **zones** to apply rules based on network trust level.

---
<a name="toc"></a>

## Table of contents

- [Core concepts](#core-concepts)
- [Check firewalld status](#check-firewalld-status)
- [Default zone](#default-zone)
- [Allow a service](#allow-a-service)
- [Remove a service](#remove-a-service)
- [Allow a port](#allow-a-port)
- [Remove a port](#remove-a-port)
- [List rules](#list-rules)
- [Predefined services](#predefined-services)
- [Zones in practice](#zones-in-practice)
  - [Assign an interface to a zone](#assign-an-interface-to-a-zone)
- [Rich rules (advanced)](#rich-rules-advanced)
- [Masquerading (NAT for outbound)](#masquerading-nat-for-outbound)


## Core concepts

| Term | Meaning |
|---|---|
| **zone** | A trust level applied to a network interface or source IP |
| **service** | A named rule set (e.g., `ssh`, `http`) defined in XML |
| **port** | A direct port/protocol rule (e.g., `8080/tcp`) |
| **rich rule** | More expressive rule with source/destination/action |
| **runtime** | Currently active rules (lost on reload) |
| **permanent** | Rules saved to disk (survive reload/reboot) |


[↑ Back to TOC](#toc)

---

## Check firewalld status

```bash
sudo firewall-cmd --state          # running or not running
sudo firewall-cmd --list-all       # show active zone + all rules
sudo firewall-cmd --get-zones      # list all available zones
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --get-active-zones
```


[↑ Back to TOC](#toc)

---

## Default zone

The default zone applies to interfaces not explicitly assigned to another zone.
On most RHEL VMs the default zone is `public`.

```bash
sudo firewall-cmd --get-default-zone

# Change default zone
sudo firewall-cmd --set-default-zone=home
```


[↑ Back to TOC](#toc)

---

## Allow a service

```bash
# Runtime only (lost on firewalld reload)
sudo firewall-cmd --add-service=http

# Permanent (survives reload/reboot)
sudo firewall-cmd --permanent --add-service=http

# Both: add permanently AND reload to activate immediately
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

> **💡 Best practice: always use --permanent + --reload**
> Using `--permanent` first and then `--reload` ensures your rules survive
> reboots and avoids confusion between runtime and permanent state.
>


[↑ Back to TOC](#toc)

---

## Remove a service

```bash
sudo firewall-cmd --permanent --remove-service=http
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

## Allow a port

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

## Remove a port

```bash
sudo firewall-cmd --permanent --remove-port=8080/tcp
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

## List rules

```bash
# All rules in the default zone
sudo firewall-cmd --list-all

# Rules in a specific zone
sudo firewall-cmd --list-all --zone=public

# List only services
sudo firewall-cmd --list-services

# List only ports
sudo firewall-cmd --list-ports
```


[↑ Back to TOC](#toc)

---

## Predefined services

```bash
# See all available predefined services
sudo firewall-cmd --get-services

# Where service definitions live
ls /usr/lib/firewalld/services/
ls /etc/firewalld/services/   # custom overrides go here
```


[↑ Back to TOC](#toc)

---

## Zones in practice

Common zones and their default posture:

| Zone | Intended use |
|---|---|
| `public` | Untrusted public networks — only explicitly allowed traffic in |
| `home` | Trusted home network — less restrictive |
| `work` | Work networks |
| `trusted` | All traffic allowed (use with extreme care) |
| `drop` | All inbound traffic silently dropped |
| `block` | All inbound traffic rejected with ICMP unreachable |
| `dmz` | Servers in a DMZ — limited inbound |
| `internal` | Internal network |

### Assign an interface to a zone

> **💡 Find your interface name first**
> Run `nmcli device status` to see your interface name (e.g., `ens3`, `eth0`,
> `enp1s0`). Replace `ens3` below with your actual interface name.

```bash
sudo firewall-cmd --permanent --zone=internal --change-interface=ens3
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

## Rich rules (advanced)

```bash
# Allow SSH from a specific subnet only
sudo firewall-cmd --permanent \
  --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'

# Block a specific IP
sudo firewall-cmd --permanent \
  --add-rich-rule='rule family="ipv4" source address="10.0.0.5" drop'

sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

## Masquerading (NAT for outbound)

```bash
sudo firewall-cmd --permanent --add-masquerade
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

---

> **⚠️ Do NOT do this**
> ```bash
> sudo systemctl stop firewalld
> sudo systemctl disable firewalld
> ```
> Disabling the firewall is not a fix for a connectivity problem. Diagnose
> the correct port or service to open instead.
>

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Using and configuring firewalld](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/securing_networks/using-and-configuring-firewalld_securing-networks) | Official firewalld guide including zones, rich rules, and nftables backend |
| [`firewalld` man page](https://firewalld.org/documentation/man-pages/firewalld.html) | Daemon configuration reference |
| [`firewall-cmd` man page](https://firewalld.org/documentation/man-pages/firewall-cmd.html) | Complete CLI option reference |

---

## Next step

→ [SSH (Keys, Server Basics)](12-ssh.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
