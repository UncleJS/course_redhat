# Accounts, sudo, and Updates
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## User accounts on RHEL

RHEL separates regular users from privileged operations through the `sudo`
mechanism. You should almost never need to log in as `root` directly.

### Key concepts

| Term | Meaning |
|---|---|
| **root** | The superuser — unlimited system access |
| **regular user** | Day-to-day account; limited privileges |
| **sudo** | Run a single command with root privileges |
| **wheel group** | Members of this group can use `sudo` on RHEL |


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [User accounts on RHEL](#user-accounts-on-rhel)
  - [Key concepts](#key-concepts)
- [Check your sudo access](#check-your-sudo-access)
- [Add a user to the wheel group](#add-a-user-to-the-wheel-group)
- [sudo patterns](#sudo-patterns)
- [The sudoers file](#the-sudoers-file)
- [Package updates with dnf](#package-updates-with-dnf)
  - [Check for available updates](#check-for-available-updates)
  - [Apply all updates](#apply-all-updates)
  - [Apply security updates only](#apply-security-updates-only)
  - [Check what changed after an update](#check-what-changed-after-an-update)
- [Automatic updates (optional for a lab VM)](#automatic-updates-optional-for-a-lab-vm)
- [Creating additional user accounts](#creating-additional-user-accounts)
- [Password aging with `chage`](#password-aging-with-chage)


## Check your sudo access

```bash
$ sudo -l
```

Look for a line containing: `(ALL) ALL` — this confirms you can run any command
via sudo.


[↑ Back to TOC](#toc)

---

## Add a user to the wheel group

If you need to grant another user sudo access:

```bash
sudo usermod -aG wheel username
```

> **💡 Verify group membership takes effect**
> The user must log out and back in (or open a new shell) for the new group
> to apply. Check with `groups username`.
>


[↑ Back to TOC](#toc)

---

## sudo patterns

```bash
# Run a single command as root
sudo dnf install -y vim

# Edit a protected file safely
sudo vim /etc/hostname

# Open an interactive root shell (use sparingly)
sudo -i

# Run as a specific user
sudo -u nginx id
```

> **⚠️ sudo -i vs sudo su**
> Prefer `sudo -i` over `sudo su -`. It is audited, respects sudoers policy,
> and does not require the root password.
>


[↑ Back to TOC](#toc)

---

## The sudoers file

The sudoers configuration lives in `/etc/sudoers` and `/etc/sudoers.d/`.

> **🚨 Always use visudo to edit sudoers**
> ```bash
> sudo visudo
> ```
> `visudo` validates syntax before saving. A syntax error in sudoers can
> lock you out of sudo entirely.
>


[↑ Back to TOC](#toc)

---

## Package updates with dnf

### Check for available updates

```bash
sudo dnf check-update
```

### Apply all updates

```bash
sudo dnf upgrade -y
```

### Apply security updates only

```bash
sudo dnf upgrade --security -y
```

### Check what changed after an update

```bash
sudo dnf history
sudo dnf history info <ID>
```


[↑ Back to TOC](#toc)

---

## Automatic updates (optional for a lab VM)

RHEL ships with `dnf-automatic`. For a learning VM, manual updates are
preferable so you control when things change.

```bash
# Install if you want automatic downloads + notifications
sudo dnf install -y dnf-automatic
sudo systemctl enable --now dnf-automatic-install.timer
```


[↑ Back to TOC](#toc)

---

## Creating additional user accounts

```bash
# Create user
sudo useradd -m -c "Full Name" username

# Set password
sudo passwd username

# Lock an account
sudo usermod -L username

# Unlock an account
sudo usermod -U username

# Delete account (keeps home dir)
sudo userdel username

# Delete account AND home dir
sudo userdel -r username
```


[↑ Back to TOC](#toc)

---

## Password aging with `chage`

Password aging policies control how often users must change their password
and when accounts expire.

```bash
# Show password aging info for a user
sudo chage -l username

# Force password change on next login
sudo chage -d 0 username

# Set maximum password age (days)
sudo chage -M 90 username

# Set minimum days before a password can be changed
sudo chage -m 7 username

# Set password expiry warning period (days before expiry)
sudo chage -W 14 username

# Set absolute account expiry date
sudo chage -E 2026-12-31 username
```

> **💡 chage at a glance**
> | Flag | Meaning |
> |---|---|
> | `-l` | List current aging settings |
> | `-d 0` | Expire password immediately (force reset at next login) |
> | `-M` | Max days password is valid |
> | `-m` | Min days before password can be changed |
> | `-W` | Days of warning before expiry |
> | `-E` | Absolute account expiry date (`YYYY-MM-DD` or `-1` to disable) |
>


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring basic system settings: Managing sudo](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_basic_system_settings/index) | Official sudo configuration guide |
| [`sudoers` man page](https://www.sudo.ws/docs/man/sudoers.man/) | Complete `sudoers` syntax reference |
| [RHEL 10 — Updating and patching packages](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_software_with_the_dnf_tool/index) | dnf update workflows and security updates |
| [Red Hat Security Advisories](https://access.redhat.com/security/security-updates/) | Track CVEs and errata for RHEL packages |

---

## Next step

→ [Getting Help](04-help-system.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
