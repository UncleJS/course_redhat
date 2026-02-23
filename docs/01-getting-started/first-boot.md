# First Boot Checklist

Run through this checklist immediately after installing RHEL 10.
Each step takes under a minute.

---

## 1 — Confirm you are NOT logged in as root

```bash
$ whoami
```

Expected: your regular username. If it says `root`, log out and log in as your
regular user.

---

## 2 — Check network connectivity

```bash
$ ping -c 3 8.8.8.8
```

Look for: `3 packets transmitted, 3 received`

If this fails, see [NetworkManager (nmcli)](../03-rhcsa/networkmanager-nmcli.md).

---

## 3 — Check DNS resolution

```bash
$ ping -c 2 access.redhat.com
```

Look for: IP address resolved and packets received.

---

## 4 — Register the system (if not done during install)

```bash
sudo subscription-manager register --username <your-redhat-username>
sudo subscription-manager attach --auto
```

---

## 5 — Apply all available updates

```bash
sudo dnf upgrade -y
```

This may take a few minutes on first run. Reboot if the kernel was updated.

```bash
sudo reboot
```

---

## 6 — Confirm SELinux is enforcing

```bash
$ getenforce
```

Expected: `Enforcing`

!!! warning "Do NOT change this"
    Do not set SELinux to `Permissive` or `Disabled`. If something breaks, learn
    to fix it correctly. See [SELinux Fundamentals](../03-rhcsa/selinux-fundamentals.md).

---

## 7 — Confirm firewalld is running

```bash
$ sudo firewall-cmd --state
```

Expected: `running`

---

## 8 — Check system time

```bash
$ timedatectl
```

Look for: `System clock synchronized: yes` and `NTP service: active`

If NTP is not active:

```bash
sudo timedatectl set-ntp true
```

---

## 9 — Set a hostname (if not done during install)

```bash
sudo hostnamectl set-hostname rhel10-lab
```

---

## 10 — Take a VM snapshot

Now is the perfect time to take a clean snapshot before you start making changes.
See [Lab Workflow](../00-preface/labs.md) for instructions.

---

## Next step

→ [Accounts, sudo, and Updates](sudo-updates.md)
