
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: Shared Team Directory
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** Onramp
**Estimated time:** 20 minutes
**Topology:** Single VM

---
<a name="toc"></a>

## Table of contents

- [Steps](#steps)
  - [1 — Create users and group](#1-create-users-and-group)
  - [2 — Create the shared directory](#2-create-the-shared-directory)
  - [3 — Set default ACL for auditor](#3-set-default-acl-for-auditor)
  - [4 — Test alice (devteam member)](#4-test-alice-devteam-member)
  - [5 — Test bob (devteam member)](#5-test-bob-devteam-member)
  - [6 — Test auditor (read-only via ACL)](#6-test-auditor-read-only-via-acl)
  - [7 — Confirm new files inherit the ACL](#7-confirm-new-files-inherit-the-acl)


## Prerequisites

- Completed [Users, Groups, Permissions](../05-permissions.md) and [ACLs](../06-acls.md)
- ACL tools installed: `sudo dnf install -y acl`
- A fresh VM snapshot taken

---


[↑ Back to TOC](#toc)

## Success criteria

By the end of this lab:

- A shared directory `/srv/teamspace` exists where:
  - Members of group `devteam` can create and edit files
  - User `auditor` has read-only access via ACL
  - New files created inside inherit the group and correct permissions (SGID + default ACL)
- You can demonstrate each access level works correctly

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Create users and group

```bash
sudo groupadd devteam
sudo useradd -m -G devteam alice
sudo useradd -m -G devteam bob
sudo useradd -m auditor
```

Set passwords for testing:

```bash
echo "alice:Password1!" | sudo chpasswd
echo "bob:Password1!" | sudo chpasswd
echo "auditor:Password1!" | sudo chpasswd
```

> **✅ Verify**
> ```bash
> getent group devteam
> ```
> Look for: `devteam:x:<GID>:alice,bob`
>


[↑ Back to TOC](#toc)

---

### 2 — Create the shared directory

```bash
sudo mkdir -p /srv/teamspace
sudo chown root:devteam /srv/teamspace
sudo chmod 2775 /srv/teamspace
```

The `2` in `2775` sets the **SGID** bit — new files will inherit the `devteam`
group automatically.

> **✅ Verify**
> ```bash
> ls -ld /srv/teamspace
> ```
> Look for: `drwxrwsr-x` and group `devteam`
>


[↑ Back to TOC](#toc)

---

### 3 — Set default ACL for auditor

```bash
# Grant auditor read access to existing directory
sudo setfacl -m u:auditor:r-x /srv/teamspace

# Default ACL: auditor gets read on all new files/dirs inside
sudo setfacl -m d:u:auditor:r-x /srv/teamspace
```

> **✅ Verify**
> ```bash
> getfacl /srv/teamspace
> ```
> Look for lines:
> ```
> user:auditor:r-x
> default:user:auditor:r-x
> ```
>


[↑ Back to TOC](#toc)

---

### 4 — Test alice (devteam member)

```bash
sudo -u alice bash -c "echo 'alice was here' > /srv/teamspace/alice-file.txt"
```

> **✅ Verify**
> ```bash
> ls -l /srv/teamspace/alice-file.txt
> ```
> Look for: group is `devteam` (SGID inherited)
>


[↑ Back to TOC](#toc)

---

### 5 — Test bob (devteam member)

Bob should be able to read and write alice's file because the group `devteam`
has write permission:

```bash
sudo -u bob bash -c "echo 'bob was here' >> /srv/teamspace/alice-file.txt"
sudo -u bob cat /srv/teamspace/alice-file.txt
```

> **✅ Verify**
> Output contains both lines.
>


[↑ Back to TOC](#toc)

---

### 6 — Test auditor (read-only via ACL)

```bash
sudo -u auditor cat /srv/teamspace/alice-file.txt
```

Expected: file contents displayed — auditor can read.

```bash
sudo -u auditor bash -c "echo 'auditor writes' >> /srv/teamspace/alice-file.txt"
```

Expected: `Permission denied` — auditor cannot write.


[↑ Back to TOC](#toc)

---

### 7 — Confirm new files inherit the ACL

Create a new file as alice and check its ACLs:

```bash
sudo -u alice bash -c "echo 'new file' > /srv/teamspace/new-file.txt"
getfacl /srv/teamspace/new-file.txt
```

Look for: `user:auditor:r--` inherited from the default ACL.


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
sudo rm -rf /srv/teamspace
sudo userdel -r alice
sudo userdel -r bob
sudo userdel -r auditor
sudo groupdel devteam
```

---


[↑ Back to TOC](#toc)

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `getent group devteam` shows no members | User not added to group | `sudo usermod -aG devteam alice` |
| New files do not show `devteam` group | SGID bit not set | `chmod g+s /srv/teamspace` |
| auditor can write | ACL mask too permissive | Re-run `setfacl -m u:auditor:r-x` |
| `setfacl: command not found` | acl package missing | `sudo dnf install -y acl` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

Shared project directories in development or CI environments need exactly this
pattern: a group-writable directory where all team members can collaborate, new
files inherit the right group (SGID), and read-only audit or monitoring accounts
can inspect content without write access. Getting this wrong leads to permission
errors, files owned by the wrong user, and security gaps.

---


[↑ Back to TOC](#toc)

## Next step

→ [Packages and Repos (dnf)](../../03-rhcsa/01-packages-dnf.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
