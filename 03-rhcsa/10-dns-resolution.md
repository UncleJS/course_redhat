# DNS and Name Resolution

Understanding how RHEL resolves names is essential for troubleshooting
connectivity issues. The resolution stack on RHEL 10 uses
**systemd-resolved** integrated with **NetworkManager**.

---
<a name="toc"></a>

## Table of contents

- [Resolution order](#resolution-order)
- [`/etc/hosts`](#etchosts)
- [`/etc/resolv.conf`](#etcresolvconf)
- [Check DNS resolution](#check-dns-resolution)
- [`resolvectl` — systemd-resolved control](#resolvectl-systemd-resolved-control)
- [Set DNS servers per connection](#set-dns-servers-per-connection)
- [Search domains](#search-domains)
- [`/etc/nsswitch.conf`](#etcnsswitchconf)
- [Troubleshooting DNS](#troubleshooting-dns)
  - ["Name not resolving"](#name-not-resolving)


## Resolution order

When you `ping hostname`, RHEL checks:

1. `/etc/hosts` (local overrides — checked first)
2. `systemd-resolved` stub resolver (`127.0.0.53`)
3. Upstream DNS servers (from NetworkManager connection config)


[↑ Back to TOC](#toc)

---

## `/etc/hosts`

Local static name-to-IP mappings. Takes priority over DNS.

```bash
cat /etc/hosts
```

```
127.0.0.1   localhost localhost.localdomain
::1         localhost localhost.localdomain
192.168.1.10  app01.lab.local app01
```

To add a local override:

```bash
sudo vim /etc/hosts
```


[↑ Back to TOC](#toc)

---

## `/etc/resolv.conf`

Points to the stub resolver. On RHEL 10 with systemd-resolved this is
managed automatically — do not edit it by hand.

```bash
cat /etc/resolv.conf
```

```
nameserver 127.0.0.53
options edns0 trust-ad
```


[↑ Back to TOC](#toc)

---

## Check DNS resolution

```bash
# Simple lookup
host access.redhat.com

# Detailed A record lookup
dig access.redhat.com

# Specific record type
dig MX redhat.com
dig AAAA access.redhat.com

# Reverse lookup (IP to name)
dig -x 8.8.8.8

# Short answer only
dig +short access.redhat.com

# Query a specific DNS server
dig @8.8.8.8 access.redhat.com
```


[↑ Back to TOC](#toc)

---

## `resolvectl` — systemd-resolved control

```bash
# Show current DNS configuration per interface
resolvectl status

# Query a name (uses systemd-resolved)
resolvectl query access.redhat.com

# Flush the DNS cache
sudo resolvectl flush-caches

# Show statistics
resolvectl statistics
```


[↑ Back to TOC](#toc)

---

## Set DNS servers per connection

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.dns "192.168.1.1 8.8.8.8 2001:4860:4860::8888"

sudo nmcli connection up "Wired connection 1"
```


[↑ Back to TOC](#toc)

---

## Search domains

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.dns-search "lab.local example.com"

sudo nmcli connection up "Wired connection 1"
```

Now `ping app01` resolves to `app01.lab.local` automatically.


[↑ Back to TOC](#toc)

---

## `/etc/nsswitch.conf`

Controls the resolution order for names, passwords, groups, etc.:

```bash
grep hosts /etc/nsswitch.conf
```

```
hosts: files dns myhostname
```

- `files` = `/etc/hosts`
- `dns` = DNS resolver
- `myhostname` = resolve the machine's own hostname


[↑ Back to TOC](#toc)

---

## Troubleshooting DNS

### "Name not resolving"

```bash
# 1. Is it a DNS or routing problem?
ping 8.8.8.8              # if this works, network is up
ping access.redhat.com    # if this fails, DNS is the problem

# 2. Check what DNS server is being used
resolvectl status | grep "DNS Server"

# 3. Test with a known-good resolver
dig @8.8.8.8 access.redhat.com

# 4. Check /etc/hosts for stale entries
grep access.redhat.com /etc/hosts

# 5. Flush cache and retry
sudo resolvectl flush-caches
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`systemd-resolved` man page](https://www.freedesktop.org/software/systemd/man/latest/systemd-resolved.service.html) | Resolved configuration, DNS-over-TLS, LLMNR |
| [`resolved.conf` man page](https://www.freedesktop.org/software/systemd/man/latest/resolved.conf.html) | All configuration knobs for DNS behaviour |
| [RHEL 10 — Managing DNS](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_networking/index) | Official DNS configuration and troubleshooting guide |

---

## Next step

→ [Firewalling (firewalld)](11-firewalld.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
