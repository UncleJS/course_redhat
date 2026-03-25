
[↑ Back to TOC](#toc)

# Packages and Repos — dnf
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

RHEL uses **dnf** (Dandified YUM) as its package manager. It handles
installing, removing, updating, and searching RPM packages and manages
the repositories that provide them.

Every piece of software on RHEL arrives as one or more **RPM** files — a
self-describing archive containing binaries, configuration templates, man
pages, and scriptlets that run on install or removal. dnf sits on top of
RPM and adds automatic dependency resolution, transaction history, and
multi-repository awareness. Think of RPM as the low-level format and dnf
as the high-level client that uses it.

Repositories are the supply chain. A repository is an HTTP(S) or local
directory tree that holds RPM packages alongside a metadata index. When you
run `dnf install`, dnf reads the metadata, solves the dependency graph, and
downloads only what is needed. On registered RHEL systems, Red Hat's Content
Delivery Network (CDN) is the primary repository source; on air-gapped systems
you replicate that content to a local server (Satellite, or a plain HTTP share).

The **AppStream** repository introduces **module streams** — a mechanism to
deliver multiple versions of a software component (e.g., Node.js 18 and 22)
from the same repo without conflict. You select the stream once and dnf
handles the rest.

---
<a name="toc"></a>

## Table of contents

- [Concepts](#concepts)
- [Searching for packages](#searching-for-packages)
- [Installing packages](#installing-packages)
- [Installing package groups](#installing-package-groups)
- [Removing packages](#removing-packages)
- [Updating packages](#updating-packages)
- [Package history and rollback](#package-history-and-rollback)
- [Module streams (AppStream)](#module-streams-appstream)
- [Repository management](#repository-management)
- [Creating a local offline repository](#creating-a-local-offline-repository)
- [GPG key verification](#gpg-key-verification)
- [RPM quick reference](#rpm-quick-reference)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Concepts

| Term | Meaning |
|---|---|
| **RPM** | The package format (`.rpm` file with metadata + files) |
| **Repository (repo)** | A server or directory providing packages + metadata |
| **dnf** | The client tool that resolves dependencies and manages RPMs |
| **module stream** | Multiple versions of a package available side-by-side (AppStream) |
| **package group** | A named collection of packages installed as a unit |
| **BaseOS** | Core RHEL repo — OS packages with long lifecycle guarantees |
| **AppStream** | Application repo — modules, runtimes, language stacks |


[↑ Back to TOC](#toc)

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

# List all packages matching a glob
sudo dnf list "python3*"

# List only installed packages matching a glob
sudo dnf list installed "python3*"
```

> **Exam tip:** `dnf provides` is the fastest way to answer "which package
> do I install to get this binary?". Use it when the package name and binary
> name differ (e.g., `dnf provides /usr/bin/dig` → `bind-utils`).


[↑ Back to TOC](#toc)

---

## Installing packages

```bash
# Install a package
sudo dnf install -y nginx

# Install multiple packages
sudo dnf install -y vim git curl

# Install a local .rpm file (dnf resolves dependencies from repos)
sudo dnf install -y /tmp/package.rpm

# Install without confirmation prompt (-y)
sudo dnf install -y htop

# Download an RPM without installing
sudo dnf download nginx
```


[↑ Back to TOC](#toc)

---

## Installing package groups

Package groups let you install a curated set of packages in one command.

```bash
# List all available groups
sudo dnf group list

# List hidden groups too
sudo dnf group list --hidden

# Show what a group contains
sudo dnf group info "Development Tools"

# Install a group
sudo dnf group install -y "Development Tools"

# Remove a group
sudo dnf group remove "Development Tools"
```

> **Exam tip:** The RHCSA exam may ask you to install a package group by
> name. Always check `dnf group list` first — group names are case-sensitive
> and must be quoted when they contain spaces.


[↑ Back to TOC](#toc)

---

## Removing packages

```bash
# Remove a package (keeps dependencies)
sudo dnf remove nginx

# Remove a package and unused dependencies
sudo dnf autoremove nginx

# Remove orphaned packages not required by anything
sudo dnf autoremove
```


[↑ Back to TOC](#toc)

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

# List available security advisories
sudo dnf updateinfo list security
```


[↑ Back to TOC](#toc)

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

# Replay a transaction (re-install exactly)
sudo dnf history replay 5
```

> **💡 Rollback limitations**
> `dnf history undo` restores installed packages but does not restore
> modified configuration files. Always back up configs before major updates.
>


[↑ Back to TOC](#toc)

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

# Switch to a different stream (reset first)
sudo dnf module reset nodejs
sudo dnf module enable nodejs:18
sudo dnf distro-sync
```

When you enable a module stream, dnf locks that version — subsequent
`dnf upgrade` runs will not jump to a newer stream automatically. To upgrade
a runtime, explicitly reset and re-enable the new stream, then `distro-sync`.


[↑ Back to TOC](#toc)

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

# Refresh metadata cache
sudo dnf makecache
```

Repo configuration files live in `/etc/yum.repos.d/`. A minimal `.repo` file:

```ini
[myrepo]
name=My Custom Repository
baseurl=http://repo.example.com/rhel10/
enabled=1
gpgcheck=1
gpgkey=http://repo.example.com/RPM-GPG-KEY-myrepo
```


[↑ Back to TOC](#toc)

---

## Creating a local offline repository

Use this pattern on air-gapped systems or for exam lab environments.

```bash
# 1 — Install the createrepo tool
sudo dnf install -y createrepo_c

# 2 — Copy RPMs to a directory
sudo mkdir -p /repo/rhel10
sudo cp /path/to/*.rpm /repo/rhel10/

# 3 — Generate repository metadata
sudo createrepo_c /repo/rhel10/

# 4 — Create a .repo file pointing to the local path
sudo tee /etc/yum.repos.d/local.repo <<'EOF'
[local]
name=Local Repository
baseurl=file:///repo/rhel10/
enabled=1
gpgcheck=0
EOF

# 5 — Verify
sudo dnf repolist
sudo dnf install -y <package-from-repo>
```

> **Exam tip:** On the RHCSA exam you often need to configure a repo from a
> provided ISO or directory. Use `file:///path` as `baseurl` and set
> `gpgcheck=0` for lab repos that lack a GPG key file.


[↑ Back to TOC](#toc)

---

## GPG key verification

RHEL automatically verifies package signatures. Do not disable this.

```bash
# View imported GPG keys
rpm -q gpg-pubkey --qf '%{NAME}-%{VERSION}-%{RELEASE}\t%{SUMMARY}\n'

# Import a GPG key manually
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release

# Verify a specific package's signature
rpm --checksig /tmp/mypackage.rpm
```

Red Hat packages are signed with the Red Hat GPG key. The key is pre-imported
on registered RHEL systems. For third-party repos, import their key using
`rpm --import` before enabling `gpgcheck=1`.


[↑ Back to TOC](#toc)

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

# Verify package integrity (checks checksums, permissions, ownership)
rpm -V nginx

# List config files of a package
rpm -qc nginx

# List documentation files of a package
rpm -qd nginx

# Install RPM directly (bypasses dependency resolution — prefer dnf)
sudo rpm -ivh /tmp/package.rpm
```


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** Set up a locked-down offline lab server. The server has no
internet access. You have an ISO mounted at `/mnt/cdrom` and need to install
the `Development Tools` group plus `git`.

```bash
# 1 — Mount the RHEL ISO (if not already mounted)
sudo mkdir -p /mnt/cdrom
sudo mount -o loop /path/to/rhel10.iso /mnt/cdrom
# Or for a physical/virtual cdrom:
# sudo mount /dev/cdrom /mnt/cdrom

# 2 — Disable all existing repos (they require network/CDN access)
sudo dnf config-manager --disable \*

# 3 — Create repo files for BaseOS and AppStream on the ISO
sudo tee /etc/yum.repos.d/cdrom-baseos.repo <<'EOF'
[cdrom-baseos]
name=RHEL 10 BaseOS (CDROM)
baseurl=file:///mnt/cdrom/BaseOS
enabled=1
gpgcheck=1
gpgkey=file:///mnt/cdrom/RPM-GPG-KEY-redhat-release
EOF

sudo tee /etc/yum.repos.d/cdrom-appstream.repo <<'EOF'
[cdrom-appstream]
name=RHEL 10 AppStream (CDROM)
baseurl=file:///mnt/cdrom/AppStream
enabled=1
gpgcheck=1
gpgkey=file:///mnt/cdrom/RPM-GPG-KEY-redhat-release
EOF

# 4 — Verify repos are visible
sudo dnf repolist

# 5 — Install the package group
sudo dnf group install -y "Development Tools"

# 6 — Install an individual package
sudo dnf install -y git

# 7 — Confirm
git --version
rpm -qi git
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Repo requires subscription but system is unregistered | `Error: Failed to download metadata` | Register with `subscription-manager register` or configure a local repo |
| Wrong `baseurl` path in `.repo` file | `Curl error ... No such file` | Double-check path with `ls`; use `file:///` (three slashes) for local paths |
| `gpgcheck=1` but no key imported | `GPG key retrieval failed` | Import the key with `rpm --import <keyfile>` or set `gpgcheck=0` for trusted internal repos |
| Forgot `dnf makecache` after adding repo | Package not found even though it exists | Run `sudo dnf makecache` to force metadata refresh |
| Enabled wrong module stream — wrong version installed | App behaves unexpectedly or refuses to start | `dnf module reset <name>`, enable the correct stream, run `dnf distro-sync` |
| `dnf remove` pulled out shared dependencies | Other apps stop working | Use `dnf remove` carefully; check `dnf history info` and `dnf history undo` to recover |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Managing software with the DNF tool](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_software_with_the_dnf_tool/index) | Official dnf guide — repositories, modules, groups |
| [`dnf` man page](https://dnf.readthedocs.io/en/latest/command_ref.html) | Complete dnf command reference |
| [RPM documentation](https://rpm.org/documentation.html) | Upstream RPM packaging and query reference |
| [RHEL 10 — Content Services (repositories)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_rhel_subscriptions/index) | Subscription and repo management |

---


[↑ Back to TOC](#toc)

## Next step

→ [Storage Overview](02-storage-overview.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
