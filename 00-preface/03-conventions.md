# Conventions

Consistent formatting makes commands safe to copy and easy to understand.
This page defines every convention used throughout the guide.

---
<a name="toc"></a>

## Table of contents

- [Shell prompts](#shell-prompts)
- [Command blocks](#command-blocks)
- [Expected output](#expected-output)
- [File paths and interface names](#file-paths-and-interface-names)
- [Admonition types](#admonition-types)
- [Track badges](#track-badges)
- [Terminology](#terminology)


## Shell prompts

| Prompt | Meaning |
|---|---|
| `$` | Regular (unprivileged) user |
| `#` | Root shell — only when `sudo` is insufficient or impractical |
| `sudo command` | Preferred way to escalate a single command |

**Example:**

```bash
$ whoami        # shows your username
$ sudo whoami   # shows: root
```

We use `sudo command` for isolated privileged operations. We introduce
`sudo -i` (interactive root shell) only in chapters where it's clearly needed,
with an explicit note about why.


[↑ Back to TOC](#toc)

---

## Command blocks

All commands are copy-paste safe. They do **not** include the prompt character
(`$` / `#`) in the text you copy — only in the annotations.

```bash
# Install a package
sudo dnf install -y vim
```

Lines starting with `#` inside a code block are comments — do not run them.


[↑ Back to TOC](#toc)

---

## Expected output

Labs use **"look for a line containing…"** style checks, not brittle full-output
copies. Example:

```bash
sudo systemctl status sshd
```

Look for a line containing: `Active: active (running)`

This is intentional — minor differences (timestamps, PIDs) should not cause
confusion.


[↑ Back to TOC](#toc)

---

## File paths and interface names

| Convention | Reason |
|---|---|
| Network interface shown as `ens3` | Common in QEMU/KVM VMs; yours may differ (check with `ip link`) |
| Disk shown as `/dev/vda` | Common in KVM VMs; bare metal often uses `/dev/sda` |
| Username shown as `rhel` | Replace with your actual username where relevant |

When a command depends on a value you must substitute, it is shown in
angle-bracket uppercase:

```bash
sudo nmcli con mod <CONNECTION-NAME> ipv4.addresses 192.168.1.10/24
```


[↑ Back to TOC](#toc)

---

## Admonition types

> **📝 Note**
> Background context or "good to know" information.
>

> **💡 Pro tip**
> Shortcut, pattern, or insight that experienced admins use.
>

> **⚠️ Do NOT do this**
> A common but incorrect approach. Followed immediately by the correct alternative.
>

> **🚨 Destructive**
> This command modifies disk partitions, erases data, or changes system boot config.
> Take a snapshot first.
>

> **✅ Verify**
> A checkpoint command with expected output. If this fails, stop and troubleshoot
> before continuing.
>


[↑ Back to TOC](#toc)

---

## Track badges

Each chapter title includes a track label:

| Badge | Meaning |
|---|---|
| `(Onramp)` | Absolute beginner content |
| `(RHCSA)` | Day-to-day system administration |
| `(RHCE)` | Automation-first operations |
| `(RHCA)` | Architecture-level depth |


[↑ Back to TOC](#toc)

---

## Terminology

- **host**: the physical or virtual machine running RHEL
- **node**: same as host, used in automation/multi-host context
- **control node**: the machine running Ansible (often your laptop or a jump host)
- **managed node**: a host Ansible configures
- **container**: a rootless Podman container unless stated otherwise


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Google Developer Documentation Style Guide](https://developers.google.com/style) | Industry reference for technical writing conventions |
| [RHEL 10 — Using the command line](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_basic_system_settings/index) | Official RHEL conventions for prompts and notation |

---

## Next step

→ [Install a RHEL 10 Lab VM](../01-getting-started/01-vm-install.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
