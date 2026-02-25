# SSH — Keys, Server Basics

SSH is how you administer RHEL remotely. This chapter covers key-based
authentication (the right way) and basic server hardening.

---
<a name="toc"></a>

## Table of contents

- [Connect to a remote host](#connect-to-a-remote-host)
- [Key-based authentication](#key-based-authentication)
  - [Generate a key pair](#generate-a-key-pair)
  - [Copy public key to a remote host](#copy-public-key-to-a-remote-host)
  - [Test key login](#test-key-login)
- [SSH config file — `~/.ssh/config`](#ssh-config-file-sshconfig)
- [SSH agent (avoid repeated passphrase entry)](#ssh-agent-avoid-repeated-passphrase-entry)
- [sshd configuration](#sshd-configuration)
  - [Recommended hardening settings](#recommended-hardening-settings)
- [Firewall: allow SSH](#firewall-allow-ssh)
- [SSH tunneling (basics)](#ssh-tunneling-basics)


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


[↑ Back to TOC](#toc)

---

## Key-based authentication

### Generate a key pair

```bash
ssh-keygen -t ed25519 -C "rhel-lab-key"
```

- Private key: `~/.ssh/id_ed25519` — **keep this secret, never share it**
- Public key: `~/.ssh/id_ed25519.pub` — share this freely

> **💡 Key type choices**
> `ed25519` is recommended: modern, fast, small. Avoid `rsa` with keys
> shorter than 3072 bits. Never use `dsa` or `ecdsa` unless required.
>

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


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## SSH agent (avoid repeated passphrase entry)

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```


[↑ Back to TOC](#toc)

---

## sshd configuration

The SSH server is configured in `/etc/ssh/sshd_config`.

> **🚨 Always use sshd -t before restarting**
> ```bash
> sudo sshd -t    # test config syntax
> sudo systemctl restart sshd
> ```
> Restarting sshd with a bad config can lock you out. Always test first.
>

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

> **⚠️ Disable PasswordAuthentication only after keys work**
> Confirm key login works from another terminal before disabling password
> auth. Disabling it without working keys will lock you out.
>
> **If you do get locked out of a lab VM**, recover via the hypervisor console
> (no SSH needed):
> 1. Open the VM console in your hypervisor (virt-manager, VMware, VirtualBox)
> 2. Log in locally as `root` or your admin user
> 3. Re-enable password auth: `sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config`
> 4. Restart sshd: `sudo systemctl restart sshd`
> 5. SSH back in, add your public key correctly, then re-disable password auth
>


[↑ Back to TOC](#toc)

---

## Firewall: allow SSH

SSH is allowed by default in the `public` zone. If you removed it:

```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`sshd_config` man page](https://man.openbsd.org/sshd_config) | Complete server configuration reference |
| [`ssh_config` man page](https://man.openbsd.org/ssh_config) | Client configuration and `~/.ssh/config` options |
| [RHEL 10 — Securing networks: SSH](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/securing_networks/assembly_using-secure-communications-between-two-systems-with-openssh_securing-networks) | RHEL hardening recommendations for OpenSSH |
| [Mozilla SSH Hardening Guide](https://infosec.mozilla.org/guidelines/openssh) | Industry-standard SSH server hardening recommendations |

---

## Next step

→ [SELinux Fundamentals](13-selinux-fundamentals.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
