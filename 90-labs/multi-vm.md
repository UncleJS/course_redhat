# Multi-VM Lab Setup

## Overview

Some labs require multiple machines: Ansible (controller + managed nodes), networking labs (two hosts to route between), and replication scenarios. This page describes a three-VM setup using KVM/libvirt.

**Topology:**

```
KVM Host
├── controller.lab.local  (4 GB RAM, 20 GB disk) — Ansible control node
├── node1.lab.local       (2 GB RAM, 20 GB disk) — managed node
└── node2.lab.local       (2 GB RAM, 20 GB disk) — managed node
```

All three VMs share a private `labnet` libvirt network (192.168.100.0/24) in addition to the default NAT network for internet access.

---

## Prerequisites

- The single-VM lab setup working and understood
- At least 12 GB RAM free on the KVM host
- 70 GB free disk space
- RHEL 10 ISO available

---

## Step 1 — Create the Private Lab Network

```bash
# Define a host-only network (no NAT, isolated between VMs)
$ sudo tee /tmp/labnet.xml <<'EOF'
<network>
  <name>labnet</name>
  <bridge name="virbr-lab"/>
  <ip address="192.168.100.1" netmask="255.255.255.0">
    <dhcp>
      <range start="192.168.100.10" end="192.168.100.99"/>
      <host mac="52:54:00:ab:cd:01" name="controller" ip="192.168.100.10"/>
      <host mac="52:54:00:ab:cd:02" name="node1"       ip="192.168.100.11"/>
      <host mac="52:54:00:ab:cd:03" name="node2"       ip="192.168.100.12"/>
    </dhcp>
  </ip>
</network>
EOF

$ sudo virsh net-define /tmp/labnet.xml
$ sudo virsh net-start labnet
$ sudo virsh net-autostart labnet

# Verify
$ sudo virsh net-list
 Name      State    Autostart   Persistent
--------------------------------------------
 default   active   yes         yes
 labnet    active   yes         yes
```

---

## Step 2 — Create the Three VMs

Run these in parallel (they don't depend on each other):

```bash
# controller
$ sudo virt-install \
  --name controller \
  --memory 4096 \
  --vcpus 2 \
  --disk size=20,format=qcow2,bus=virtio \
  --cdrom /path/to/rhel-10.x-x86_64-dvd.iso \
  --os-variant rhel10.0 \
  --network network=default,model=virtio \
  --network network=labnet,model=virtio,mac=52:54:00:ab:cd:01 \
  --graphics vnc \
  --noautoconsole

# node1
$ sudo virt-install \
  --name node1 \
  --memory 2048 \
  --vcpus 2 \
  --disk size=20,format=qcow2,bus=virtio \
  --cdrom /path/to/rhel-10.x-x86_64-dvd.iso \
  --os-variant rhel10.0 \
  --network network=default,model=virtio \
  --network network=labnet,model=virtio,mac=52:54:00:ab:cd:02 \
  --graphics vnc \
  --noautoconsole

# node2
$ sudo virt-install \
  --name node2 \
  --memory 2048 \
  --vcpus 2 \
  --disk size=20,format=qcow2,bus=virtio \
  --cdrom /path/to/rhel-10.x-x86_64-dvd.iso \
  --os-variant rhel10.0 \
  --network network=default,model=virtio \
  --network network=labnet,model=virtio,mac=52:54:00:ab:cd:03 \
  --graphics vnc \
  --noautoconsole
```

---

## Step 3 — Install RHEL 10 on Each VM

Open three `virt-manager` console windows and complete the Anaconda installer on each:

| Setting | controller | node1 | node2 |
|---|---|---|---|
| Hostname | `controller.lab.local` | `node1.lab.local` | `node2.lab.local` |
| User | `student` (wheel) | `student` (wheel) | `student` (wheel) |
| Software | Minimal | Minimal | Minimal |
| Disk | Auto partition | Auto partition | Auto partition |

Both network interfaces will be configured post-install.

---

## Step 4 — Configure Static IPs on the lab Network

On **each VM**, configure the second NIC (connected to `labnet`) with a static IP:

**controller:**

```bash
$ sudo nmcli connection add \
    con-name lab-static \
    type ethernet \
    ifname ens4 \
    ipv4.method manual \
    ipv4.addresses 192.168.100.10/24 \
    ipv4.gateway "" \
    connection.autoconnect yes

$ sudo nmcli connection up lab-static
```

**node1:**

```bash
$ sudo nmcli connection add \
    con-name lab-static \
    type ethernet \
    ifname ens4 \
    ipv4.method manual \
    ipv4.addresses 192.168.100.11/24 \
    ipv4.gateway "" \
    connection.autoconnect yes

$ sudo nmcli connection up lab-static
```

**node2:**

```bash
$ sudo nmcli connection add \
    con-name lab-static \
    type ethernet \
    ifname ens4 \
    ipv4.method manual \
    ipv4.addresses 192.168.100.12/24 \
    ipv4.gateway "" \
    connection.autoconnect yes

$ sudo nmcli connection up lab-static
```

---

## Step 5 — /etc/hosts on All Three VMs

Add lab hostnames to `/etc/hosts` so Ansible inventory works without DNS:

```bash
# Run on all three VMs
$ sudo tee -a /etc/hosts <<'EOF'
192.168.100.10  controller.lab.local  controller
192.168.100.11  node1.lab.local       node1
192.168.100.12  node2.lab.local       node2
EOF
```

---

## Step 6 — SSH Key Distribution from controller

Ansible communicates over SSH. Set up passwordless SSH from controller to both nodes:

```bash
# On controller: generate a key
$ ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519

# Copy to node1 and node2
$ ssh-copy-id student@node1
$ ssh-copy-id student@node2

# Test
$ ssh student@node1 hostname
node1.lab.local

$ ssh student@node2 hostname
node2.lab.local
```

---

## Step 7 — Install Ansible on controller

```bash
$ sudo dnf install -y ansible-core

$ ansible --version
ansible [core 2.x.x]
```

---

## Step 8 — Baseline Ansible Inventory

```bash
$ mkdir -p ~/ansible/inventory

$ tee ~/ansible/inventory/lab.ini <<'EOF'
[controller]
controller.lab.local

[nodes]
node1.lab.local
node2.lab.local

[all:vars]
ansible_user=student
ansible_become=true
EOF

# Smoke test
$ ansible all -i ~/ansible/inventory/lab.ini -m ping
node1.lab.local | SUCCESS => ...
node2.lab.local | SUCCESS => ...
controller.lab.local | SUCCESS => ...
```

---

## Step 9 — Snapshot All Three VMs

```bash
$ for vm in controller node1 node2; do
    sudo virsh snapshot-create-as $vm \
      --name "baseline" \
      --description "RHEL 10 minimal + student + lab network configured"
  done

# Verify
$ for vm in controller node1 node2; do
    echo "=== $vm ==="; sudo virsh snapshot-list $vm
  done
```

---

## Quick Reference — Multi-VM Management

```bash
# Start all lab VMs
$ for vm in controller node1 node2; do sudo virsh start $vm; done

# Shutdown all
$ for vm in controller node1 node2; do sudo virsh shutdown $vm; done

# Revert all to baseline
$ for vm in controller node1 node2; do
    sudo virsh snapshot-revert $vm baseline
  done

# Status of all
$ sudo virsh list --all
```

---

## Success Criteria

- [ ] All three VMs boot and reach a login prompt
- [ ] `ping node1` from controller succeeds via the 192.168.100.x network
- [ ] `ansible all -m ping` returns SUCCESS for all three hosts
- [ ] Baseline snapshots exist for all three VMs

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Second NIC not visible as `ens4` | Interface name may differ — check `ip link` and update `nmcli` commands |
| `ansible ping` fails with `UNREACHABLE` | Verify SSH key was copied; test `ssh student@node1` manually |
| VMs can't reach each other on `labnet` | Confirm `sudo virsh net-list` shows labnet active; check `ens4` IP with `ip addr` |
| DHCP not assigning the static MAC address | The MAC in `virt-install` must exactly match the MAC in `labnet.xml` |
| `subscription-manager` needed on all VMs | Register each VM or point all three to a local mirror; automate with Ansible |

---

## Further reading

| Resource | Notes |
|---|---|
| [libvirt networking](https://wiki.libvirt.org/Networking.html) | Virtual network types: NAT, routed, isolated, bridged |
| [Vagrant + libvirt provider](https://vagrant-libvirt.github.io/vagrant-libvirt/) | Scriptable multi-VM environments on KVM |
| [`virsh net-*` reference](https://libvirt.org/manpages/virsh.html) | Managing virtual networks from the command line |

---

## Next step

→ [Back to Contents](../README.md)
