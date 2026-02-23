# Accounts, sudo, and Updates

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

---

## Check your sudo access

```bash
$ sudo -l
```

Look for a line containing: `(ALL) ALL` — this confirms you can run any command
via sudo.

---

## Add a user to the wheel group

If you need to grant another user sudo access:

```bash
sudo usermod -aG wheel username
```

!!! tip "Verify group membership takes effect"
    The user must log out and back in (or open a new shell) for the new group
    to apply. Check with `groups username`.

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

!!! warning "sudo -i vs sudo su"
    Prefer `sudo -i` over `sudo su -`. It is audited, respects sudoers policy,
    and does not require the root password.

---

## The sudoers file

The sudoers configuration lives in `/etc/sudoers` and `/etc/sudoers.d/`.

!!! danger "Always use visudo to edit sudoers"
    ```bash
    sudo visudo
    ```
    `visudo` validates syntax before saving. A syntax error in sudoers can
    lock you out of sudo entirely.

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

---

## Automatic updates (optional for a lab VM)

RHEL ships with `dnf-automatic`. For a learning VM, manual updates are
preferable so you control when things change.

```bash
# Install if you want automatic downloads + notifications
sudo dnf install -y dnf-automatic
sudo systemctl enable --now dnf-automatic-install.timer
```

---

## Creating additional user accounts

```bash
# Create user
sudo useradd -m -c "Full Name" username

# Set password
sudo passwd username

# Lock an account
sudo usermod -L username

# Delete account (keeps home dir)
sudo userdel username

# Delete account AND home dir
sudo userdel -r username
```

---

## Next step

→ [Getting Help](help-system.md)
