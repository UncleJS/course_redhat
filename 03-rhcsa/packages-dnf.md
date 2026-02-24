# Packages and Repos — dnf

RHEL uses **dnf** (Dandified YUM) as its package manager. It handles
installing, removing, updating, and searching RPM packages and manages
the repositories that provide them.

---

## Concepts

| Term | Meaning |
|---|---|
| **RPM** | The package format (`.rpm` file with metadata + files) |
| **Repository (repo)** | A server or directory providing packages + metadata |
| **dnf** | The client tool that resolves dependencies and manages RPMs |
| **module stream** | Multiple versions of a package available side-by-side (AppStream) |

---

## Searching for packages

```bash
# Search by name or description
sudo dnf search nginx
sudo dnf search "web server"

# Show full details about a package
sudo dnf info nginx

# Find which package provides a file or command
sudo dnf provides /usr/bin/ss
sudo dnf provides "*/nmap"
```

---

## Installing packages

```bash
# Install a package
sudo dnf install -y nginx

# Install multiple packages
sudo dnf install -y vim git curl

# Install a local .rpm file
sudo dnf install -y /tmp/package.rpm

# Install without confirmation prompt (-y)
sudo dnf install -y htop
```

---

## Removing packages

```bash
# Remove a package (keeps dependencies)
sudo dnf remove nginx

# Remove a package and unused dependencies
sudo dnf autoremove nginx
```

---

## Updating packages

```bash
# Check what updates are available
sudo dnf check-update

# Update a specific package
sudo dnf upgrade nginx

# Update everything
sudo dnf upgrade -y

# Security updates only
sudo dnf upgrade --security -y
```

---

## Package history and rollback

```bash
# View transaction history
sudo dnf history

# Details of a specific transaction
sudo dnf history info 5

# Undo the last transaction
sudo dnf history undo last

# Undo a specific transaction (by ID)
sudo dnf history undo 5
```

> **💡 Rollback limitations**
> `dnf history undo` restores installed packages but does not restore
> modified configuration files. Always back up configs before major updates.
>

---

## Module streams (AppStream)

RHEL 10 provides multiple versions of some software via **AppStream modules**:

```bash
# List available modules
sudo dnf module list

# List streams for a specific module
sudo dnf module list nodejs

# Enable and install a specific stream
sudo dnf module enable nodejs:22
sudo dnf install -y nodejs

# Show currently enabled modules
sudo dnf module list --enabled
```

---

## Repository management

```bash
# List all enabled repositories
sudo dnf repolist

# List all repos (enabled + disabled)
sudo dnf repolist all

# Enable a disabled repo
sudo dnf config-manager --enable <repo-id>

# Disable a repo
sudo dnf config-manager --disable <repo-id>

# Add a repo from a URL
sudo dnf config-manager --add-repo https://example.com/repo.repo
```

Repo configuration files live in `/etc/yum.repos.d/`.

---

## GPG key verification

RHEL automatically verifies package signatures. Do not disable this.

```bash
# View imported GPG keys
rpm -q gpg-pubkey --qf '%{NAME}-%{VERSION}-%{RELEASE}\t%{SUMMARY}\n'
```

---

## RPM quick reference

```bash
# List files installed by a package
rpm -ql nginx

# Find which package owns a file
rpm -qf /usr/bin/vim

# List installed packages
rpm -qa

# Query package info
rpm -qi bash

# Verify package integrity
rpm -V nginx
```

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Managing software with the DNF tool](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_software_with_the_dnf_tool/index) | Official dnf guide — repositories, modules, groups |
| [`dnf` man page](https://dnf.readthedocs.io/en/latest/command_ref.html) | Complete dnf command reference |
| [RPM documentation](https://rpm.org/documentation.html) | Upstream RPM packaging and query reference |
| [RHEL 10 — Content Services (repositories)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_rhel_subscriptions/index) | Subscription and repo management |

---

## Next step

→ [Storage Overview](storage-overview.md)
