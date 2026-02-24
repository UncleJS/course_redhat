# Lab: Static IP + DNS Validation

**Track:** RHCSA
**Estimated time:** 25 minutes
**Topology:** Single VM

---

## Prerequisites

- Completed [NetworkManager (nmcli)](../networkmanager-nmcli.md) and [DNS and Name Resolution](../dns-resolution.md)
- Know your VM's current interface name (`ip link show`)
- VM snapshot taken

---

## Success criteria

- VM has a manually configured static IP address
- Default gateway is set correctly
- DNS resolves external names
- `ping access.redhat.com` succeeds
- Configuration survives a reboot

---

## Steps

### 1 — Identify your interface and current connection

```bash
nmcli device status
nmcli connection show
```

Note your interface name (e.g., `ens3`) and active connection name.

### 2 — Choose a static IP

Pick an IP in your VM's subnet. If your VM is using `192.168.122.x` (NAT),
use something like `192.168.122.200/24`. Check for conflicts:

```bash
ping -c 2 192.168.122.200   # should show no response (IP is free)
```

### 3 — Configure static addressing

Replace `<CONNECTION-NAME>` with your actual connection name:

```bash
sudo nmcli connection modify "<CONNECTION-NAME>" \
  ipv4.method manual \
  ipv4.addresses 192.168.122.200/24 \
  ipv4.gateway 192.168.122.1 \
  ipv4.dns "192.168.122.1 8.8.8.8"
```

### 4 — Activate the new config

```bash
sudo nmcli connection up "<CONNECTION-NAME>"
```

> **✅ Verify — IP address**
> ```bash
> ip addr show
> ```
> Look for: `192.168.122.200/24` on your interface.
>

> **✅ Verify — Default gateway**
> ```bash
> ip route show
> ```
> Look for: `default via 192.168.122.1`
>

> **✅ Verify — DNS**
> ```bash
> resolvectl status | grep "DNS Server"
> ```
> Look for: `192.168.122.1` and `8.8.8.8`
>

### 5 — Test connectivity

```bash
ping -c 3 192.168.122.1         # gateway reachable
ping -c 3 8.8.8.8               # internet reachable (IP)
ping -c 3 access.redhat.com     # DNS + internet working
```

All three should succeed.

### 6 — Test persistence across reboot

```bash
sudo reboot
```

After boot, log back in and repeat the verify steps.

---

## Cleanup (restore DHCP)

```bash
sudo nmcli connection modify "<CONNECTION-NAME>" \
  ipv4.method auto \
  ipv4.addresses "" \
  ipv4.gateway "" \
  ipv4.dns ""

sudo nmcli connection up "<CONNECTION-NAME>"
```

---

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| No IP after `connection up` | Wrong interface or connection name | Re-check with `nmcli device status` |
| `ping 8.8.8.8` fails | Wrong gateway | Verify gateway IP matches your network |
| `ping access.redhat.com` fails but `ping 8.8.8.8` works | Wrong DNS | Check `ipv4.dns` setting |
| Settings lost after reboot | Connection not marked auto-connect | `nmcli connection modify ... connection.autoconnect yes` |

---

## Why this matters in production

Servers rarely use DHCP. Static addressing ensures predictable access, stable
DNS PTR records, and no surprise IP changes during DHCP lease expiry. Getting
comfortable with `nmcli` is the foundation for all network configuration
work that follows.

---

## Next step

→ [Lab — Create a systemd Service](systemd-service.md)
