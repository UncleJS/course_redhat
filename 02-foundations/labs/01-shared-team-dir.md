
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
  - [8 — Verify SGID persistence](#8-verify-sgid-persistence)
  - [9 — Simulate a permission regression and recover](#9-simulate-a-permission-regression-and-recover)


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

## Background

This lab combines three mechanisms you learned in the previous two sections:

1. **SGID bit** on the directory — ensures new files created inside inherit the `devteam` group rather than the creator's primary group.
2. **Standard group permissions** — gives all `devteam` members read and write access via the group permission bits.
3. **Named user ACL** — gives `auditor` read-only access without adding them to `devteam` and without modifying the group ownership chain.

The pattern is common in practice: development teams, CI pipelines, and shared build directories all require exactly this combination. Getting any one of the three wrong produces subtle, hard-to-debug permission failures.

---

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

> **Exam tip:** `useradd -m` creates the home directory. Without `-m`, no home directory is created and the user cannot log in to a normal session. Always use `-m` unless you have a specific reason not to (e.g., system accounts).


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

Breaking down `2775`:
- `2` — SGID bit
- `7` — user (root): rwx
- `7` — group (devteam): rwx
- `5` — other: r-x (read and enter, but cannot write)

> **✅ Verify**
> ```bash
> ls -ld /srv/teamspace
> ```
> Look for: `drwxrwsr-x` and group `devteam`
>

The `s` in the group execute position confirms SGID is set and the execute bit is also set. An uppercase `S` would mean SGID is set but execute is missing — which would prevent entering the directory.


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

Also confirm `ls -ld` now shows a `+`:

```bash
ls -ld /srv/teamspace
# drwxrwsr-x+ ...
#           ^ plus sign = ACLs are set
```


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

Also verify the ACL was inherited from the default:

```bash
getfacl /srv/teamspace/alice-file.txt
# Should show: user:auditor:r--
```


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

If bob gets "Permission denied", check:
1. Is bob actually in the devteam group? `getent group devteam`
2. Was bob's group membership active? `sudo -u bob groups`
3. Is the file's group actually devteam? `ls -l /srv/teamspace/alice-file.txt`


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

```bash
sudo -u auditor ls /srv/teamspace/
```

Expected: directory listing is shown — auditor can enter and list the directory.

> **✅ Verify all three**
> - Read: succeeds
> - Write: fails with `Permission denied`
> - List directory: succeeds


[↑ Back to TOC](#toc)

---

### 7 — Confirm new files inherit the ACL

Create a new file as alice and check its ACLs:

```bash
sudo -u alice bash -c "echo 'new file' > /srv/teamspace/new-file.txt"
getfacl /srv/teamspace/new-file.txt
```

Look for: `user:auditor:r--` inherited from the default ACL.

Also create a subdirectory and confirm it inherits both the SGID and the default ACL:

```bash
sudo -u alice mkdir /srv/teamspace/reports
ls -ld /srv/teamspace/reports
# Should show drwxrwsr-x+ (SGID inherited, ACL set)
getfacl /srv/teamspace/reports
# Should show default: entries inherited from parent
```


[↑ Back to TOC](#toc)

---

### 8 — Verify SGID persistence

When bob creates a file, it should also belong to `devteam`, not `bob`'s primary group:

```bash
sudo -u bob bash -c "echo 'bob file' > /srv/teamspace/bob-file.txt"
ls -l /srv/teamspace/bob-file.txt
# -rw-rw-r--+ 1 bob devteam ... bob-file.txt
#                   ^^^^^^^
# Group is devteam, not bob's primary group — SGID is working
```

Confirm alice can append to bob's file (group write permission):

```bash
sudo -u alice bash -c "echo 'alice appends' >> /srv/teamspace/bob-file.txt"
cat /srv/teamspace/bob-file.txt
```


[↑ Back to TOC](#toc)

---

### 9 — Simulate a permission regression and recover

This step shows what happens when someone runs `chmod` incorrectly on the directory, and how to recover.

```bash
# Simulate: someone ran chmod 775 (3-digit, strips SGID)
sudo chmod 775 /srv/teamspace
ls -ld /srv/teamspace
# drwxrwxr-x  — SGID gone! No 's' in group position

# Effect: new files no longer inherit devteam group
sudo -u alice bash -c "echo test > /srv/teamspace/regression-test.txt"
ls -l /srv/teamspace/regression-test.txt
# -rw-rw-r--+ 1 alice alice ...
#                     ^^^^^
# Group is alice, not devteam — broken!

# Recovery: restore SGID
sudo chmod g+s /srv/teamspace
ls -ld /srv/teamspace
# drwxrwsr-x  — SGID restored

# Remove the broken file
sudo rm /srv/teamspace/regression-test.txt

# Verify recovery
sudo -u alice bash -c "echo test > /srv/teamspace/recovery-test.txt"
ls -l /srv/teamspace/recovery-test.txt
# -rw-rw-r--+ 1 alice devteam ... — correct
```

> **Exam tip:** This regression (SGID disappearing after `chmod`) is a common exam scenario. Always use 4-digit octal (`chmod 2775`) or the symbolic form (`chmod g+s`) when SGID must be preserved.


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
| `bob` gets "Permission denied" writing to alice's file | Bob's group membership not active | `sudo -u bob groups` — if devteam missing, re-add with `sudo usermod -aG devteam bob` |
| Default ACL not inherited by new files | Default ACL not set on directory | `sudo setfacl -m d:u:auditor:r-x /srv/teamspace` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

Shared project directories in development or CI environments need exactly this
pattern: a group-writable directory where all team members can collaborate, new
files inherit the right group (SGID), and read-only audit or monitoring accounts
can inspect content without write access. Getting this wrong leads to permission
errors, files owned by the wrong user, and security gaps.

In a real environment you would also:
- Set `umask 0002` for users in `devteam` so new files are group-writable by default
- Configure the default ACL on subdirectories recursively if the tree is deep
- Consider SELinux context (`chcon` or `restorecon`) if the directory serves a specific service

---


[↑ Back to TOC](#toc)

## Next step

→ [Packages and Repos (dnf)](../../03-rhcsa/01-packages-dnf.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
