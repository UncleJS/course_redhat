# NetworkManager and nmcli

**NetworkManager** is the default network management daemon on RHEL 10.
`nmcli` is its command-line interface — the tool you will use for all
network configuration.

---

## Key concepts

| Term | Meaning |
|---|---|
| **device** | A physical or virtual network interface (e.g., `ens3`) |
| **connection** | A configuration profile tied to a device |
| **active connection** | A connection currently applied to a device |

A device can have multiple connections defined (e.g., home, work, static),
but only one active at a time.

---

## View current state

```bash
# Short overview of devices and their status
nmcli

# Device status
nmcli device status

# Connection profiles (all defined)
nmcli connection show

# Active connections only
nmcli connection show --active

# Details of a specific connection
nmcli connection show "Wired connection 1"
```

---

## Configure a static IP address

```bash
# Step 1 — identify your connection name
nmcli connection show

# Step 2 — modify the connection
sudo nmcli connection modify "Wired connection 1" \
  ipv4.method manual \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "192.168.1.1 8.8.8.8"

# Step 3 — apply changes
sudo nmcli connection up "Wired connection 1"
```

!!! success "Verify"
    ```bash
    ip addr show
    ip route show
    ```
    Look for your new IP and the default gateway route.

---

## Switch back to DHCP

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.method auto \
  ipv4.addresses "" \
  ipv4.gateway "" \
  ipv4.dns ""

sudo nmcli connection up "Wired connection 1"
```

---

## Create a new connection profile

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "static-lab" \
  ifname ens3 \
  ipv4.method manual \
  ipv4.addresses 192.168.1.200/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "192.168.1.1"
```

---

## Bring connections up and down

```bash
sudo nmcli connection up "static-lab"
sudo nmcli connection down "static-lab"

# Bring up default (auto-connect)
sudo nmcli device connect ens3
sudo nmcli device disconnect ens3
```

---

## Delete a connection profile

```bash
sudo nmcli connection delete "static-lab"
```

---

## Set hostname via nmcli

```bash
sudo nmcli general hostname rhel10-lab
sudo hostnamectl set-hostname rhel10-lab   # equivalent
```

---

## DNS configuration

DNS servers are set per connection. After modifying DNS:

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.dns "192.168.1.1 8.8.8.8"
sudo nmcli connection up "Wired connection 1"
```

Check the resolved DNS:

```bash
resolvectl status
cat /etc/resolv.conf
```

---

## Connection file location

NetworkManager stores connection profiles as keyfiles:

```bash
ls /etc/NetworkManager/system-connections/
```

You can edit these directly (then run `sudo nmcli connection reload`), but
nmcli is safer and preferred.

---

## Useful nmcli shortcuts

```bash
# Quick status table
nmcli

# Which IP do I have?
nmcli -f IP4.ADDRESS device show ens3

# All details about device
nmcli device show ens3
```

---

## Next step

→ [DNS and Name Resolution](dns-resolution.md)
