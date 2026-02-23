# SSH — Keys, Server Basics

SSH is how you administer RHEL remotely. This chapter covers key-based
authentication (the right way) and basic server hardening.

---

## Connect to a remote host

```bash
# Connect as the same username
ssh 192.168.1.100

# Connect as a specific user
ssh rhel@192.168.1.100

# Connect on a non-default port
ssh -p 2222 rhel@192.168.1.100

# Connect with a specific key
ssh -i ~/.ssh/id_lab rhel@192.168.1.100
```

---

## Key-based authentication

### Generate a key pair

```bash
ssh-keygen -t ed25519 -C "rhel-lab-key"
```

- Private key: `~/.ssh/id_ed25519` — **keep this secret, never share it**
- Public key: `~/.ssh/id_ed25519.pub` — share this freely

!!! tip "Key type choices"
    `ed25519` is recommended: modern, fast, small. Avoid `rsa` with keys
    shorter than 3072 bits. Never use `dsa` or `ecdsa` unless required.

### Copy public key to a remote host

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub rhel@192.168.1.100
```

Or manually:

```bash
# On the remote host
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "<contents of your .pub file>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Test key login

```bash
ssh -i ~/.ssh/id_ed25519 rhel@192.168.1.100
```

---

## SSH config file — `~/.ssh/config`

Saves you from typing options every time:

```
Host lab
    HostName 192.168.1.100
    User rhel
    IdentityFile ~/.ssh/id_ed25519
    Port 22

Host bastion
    HostName 10.0.0.1
    User admin
    IdentityFile ~/.ssh/id_bastion
```

Now connect with:

```bash
ssh lab
```

---

## SSH agent (avoid repeated passphrase entry)

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

## sshd configuration

The SSH server is configured in `/etc/ssh/sshd_config`.

!!! danger "Always use sshd -t before restarting"
    ```bash
    sudo sshd -t    # test config syntax
    sudo systemctl restart sshd
    ```
    Restarting sshd with a bad config can lock you out. Always test first.

### Recommended hardening settings

```bash
sudo vim /etc/ssh/sshd_config
```

Key settings to review and set:

```
# Disable root login (use sudo instead)
PermitRootLogin no

# Disable password auth (force key-only)
PasswordAuthentication no
PubkeyAuthentication yes

# Disable empty passwords
PermitEmptyPasswords no

# Limit which users can log in
AllowUsers rhel admin

# Set a login grace time
LoginGraceTime 30

# Log level for auditing
LogLevel VERBOSE
```

```bash
sudo sshd -t && sudo systemctl restart sshd
```

!!! warning "Disable PasswordAuthentication only after keys work"
    Confirm key login works from another terminal before disabling password
    auth. Disabling it without working keys will lock you out.

---

## Firewall: allow SSH

SSH is allowed by default in the `public` zone. If you removed it:

```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

---

## SSH tunneling (basics)

```bash
# Local port forwarding: forward local 8080 to remote 80
ssh -L 8080:localhost:80 rhel@192.168.1.100

# SOCKS proxy
ssh -D 1080 rhel@192.168.1.100

# Jump host (ProxyJump)
ssh -J admin@bastion.example.com rhel@10.0.0.50
```

---

## Next step

→ [SELinux Fundamentals](selinux-fundamentals.md)
