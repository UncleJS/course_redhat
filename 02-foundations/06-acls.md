
[↑ Back to TOC](#toc)

# ACLs — When and How
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Standard Unix permissions give you three permission sets: user, group, other.
**Access Control Lists (ACLs)** extend this by letting you grant permissions
to **any number of specific users or groups** on a single file or directory.

ACLs implement **POSIX.1e** access control on Linux. They are stored as extended attributes (`system.posix_acl_access` and `system.posix_acl_default`) on the inode and are fully supported by XFS — the default filesystem on RHEL — without any additional mount options. ext4 also supports ACLs natively on RHEL 10.

The mental model: an ACL is a list of **entries**, each specifying a subject (named user, named group, owning user, owning group, or other) and a permission set. When the kernel evaluates access, it checks the most specific matching ACL entry. A **mask** entry caps the effective permissions of all named users and named groups (but not the owning user or other), making it a single dial to limit ACL scope without modifying individual entries.

The critical insight is that ACLs **augment** standard permissions — they do not replace them. The owning user, owning group, and other bits you see in `ls -l` are still present and are themselves ACL entries. When any named ACL entries exist, `ls -l` appends a `+` to the permission string to indicate that the full picture requires `getfacl`.

---
<a name="toc"></a>

## Table of contents

- [When to use ACLs](#when-to-use-acls)
- [Check if ACLs are supported](#check-if-acls-are-supported)
- [Install ACL tools](#install-acl-tools)
- [View ACLs — `getfacl`](#view-acls-getfacl)
- [Set ACLs — `setfacl`](#set-acls-setfacl)
- [Default ACLs — directory inheritance](#default-acls-directory-inheritance)
- [Remove ACLs](#remove-acls)
- [The ACL mask](#the-acl-mask)
- [Preserve ACLs when copying](#preserve-acls-when-copying)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## When to use ACLs

Use ACLs when standard permissions are not expressive enough. Examples:

- A shared project directory where two separate groups each need different access
- Grant one specific user read access to a file without changing group ownership
- Set default permissions so all new files in a directory inherit the right ACLs
- Give a monitoring or audit account read-only access to log directories without modifying their group ownership

> **💡 ACLs don't replace standard permissions**
> ACLs augment standard Unix permissions. The effective permission for a user
> is the **most specific** match (user ACL > group ACL > other). When an ACL
> is present, a **mask** also applies — see below.
>

> **Exam tip:** `getfacl` and `setfacl` require the `acl` package on RHEL. On RHEL 10 with XFS, ACL support is always on — no `acl` mount option is needed. On older kernels with ext3, you may need to add `acl` to the mount options in `/etc/fstab`.


[↑ Back to TOC](#toc)

---

## Check if ACLs are supported

XFS (the default filesystem on RHEL) supports ACLs natively. No mount options
needed.

```bash
# Check filesystem type
df -T /srv
# /dev/vda3  xfs  ...

# Verify XFS — ACLs are always on
xfs_info /dev/vda3 | grep -i acl
# No output is expected — ACLs are always enabled on XFS

# For ext4, check mount options
mount | grep "on / "
# Look for 'acl' in the options list

# If acl is not in mount options, add it to /etc/fstab:
# UUID=... / ext4 defaults,acl 0 1
# Then remount: sudo mount -o remount /
```


[↑ Back to TOC](#toc)

---

## Install ACL tools

```bash
sudo dnf install -y acl
```

The `acl` package provides `getfacl` and `setfacl`. Verify installation:

```bash
which getfacl setfacl
```


[↑ Back to TOC](#toc)

---

## View ACLs — `getfacl`

```bash
getfacl /srv/project/
```

A file with no ACLs set shows:

```text
# file: project/
# owner: root
# group: developers
user::rwx
group::rwx
other::r-x
```

A file with ACLs set shows extra `user:` or `group:` lines plus a `mask::`.

```text
# file: project/
# owner: root
# group: developers
user::rwx
user:alice:rw-          # named user ACL
group::rwx
group:qa:r-x            # named group ACL
mask::rwx               # effective permission ceiling
other::r-x
default:user::rwx
default:user:alice:rw-
default:group::rwx
default:mask::rwx
default:other::r-x
```

When a `+` appears at the end of `ls -l` permissions, use `getfacl` to see the full access list:

```bash
ls -l /srv/project/
# drwxrwxr-x+ ...
#           ^ the + means ACLs are set
getfacl /srv/project/
```


[↑ Back to TOC](#toc)

---

## Set ACLs — `setfacl`

```bash
# Grant user alice read+write on a file
setfacl -m u:alice:rw /srv/project/report.txt

# Grant group qa read-only on a directory
setfacl -m g:qa:r-x /srv/project/

# Grant user alice execute permission too
setfacl -m u:alice:rwx /srv/project/

# Apply to multiple targets in one command
setfacl -m u:alice:rw,g:qa:r-x /srv/project/report.txt

# Recursive — apply to directory and all existing contents
setfacl -R -m u:alice:rw /srv/project/
```

ACL entry format: `[d:]type:name:perms`

| Type | Meaning |
|---|---|
| `u:name:perms` | Named user ACL |
| `g:name:perms` | Named group ACL |
| `o::perms` | Other |
| `m::perms` | Mask |
| `d:u:name:perms` | Default named user ACL (directory only) |


[↑ Back to TOC](#toc)

---

## Default ACLs — directory inheritance

Default ACLs apply only to directories. When a file or subdirectory is created inside a directory that has default ACLs, the new object inherits those defaults as its access ACL.

```bash
# Set a default ACL (applies to newly created files inside the dir)
setfacl -m d:u:alice:rw /srv/project/

# Set default ACL for a group
setfacl -m d:g:qa:r-x /srv/project/

# View defaults
getfacl /srv/project/
# Look for lines starting with 'default:'

# Test: create a file and verify it inherited the ACL
sudo -u bob touch /srv/project/newfile.txt
getfacl /srv/project/newfile.txt
# Should show user:alice:rw-
```

Default ACLs are the mechanism that makes shared directories work reliably over time — without them, only existing files have the right ACLs and every new file requires manual correction.


[↑ Back to TOC](#toc)

---

## Remove ACLs

```bash
# Remove a specific user ACL
setfacl -x u:alice /srv/project/report.txt

# Remove a specific group ACL
setfacl -x g:qa /srv/project/

# Remove all ACLs (reverts to standard permissions)
setfacl -b /srv/project/report.txt

# Remove all default ACLs only
setfacl -k /srv/project/

# Remove ACLs recursively
setfacl -R -b /srv/project/
```

After `setfacl -b`, the `+` disappears from `ls -l` output, confirming the ACLs are gone.


[↑ Back to TOC](#toc)

---

## The ACL mask

The **mask** limits the maximum effective permissions for named users and groups
(not the owning user or other). It is recalculated automatically when you set
ACLs.

```bash
# Force the mask to a specific value
setfacl -m mask::r-x /srv/project/
```

The mask is recalculated to the union of all named user and group ACL permissions every time you add an ACL. If you explicitly set the mask and then add another ACL, the mask is recalculated again — losing your explicit value. To keep a fixed mask, always set it last.

```bash
# Set ACL, then lock the mask
setfacl -m u:alice:rw /srv/project/report.txt
setfacl -m mask::r-- /srv/project/report.txt
# Now alice's effective permission is r-- (not rw), even though her ACL says rw

# getfacl shows effective permissions clearly:
getfacl /srv/project/report.txt
# user:alice:rw-          #effective:r--
```

> **Exam tip:** When `getfacl` shows `#effective:` after an ACL entry, the mask is reducing the effective permission below what the entry specifies. This is the most common source of confusion when ACLs are set but access is still denied.


[↑ Back to TOC](#toc)

---

## Preserve ACLs when copying

Standard `cp` does not copy ACLs by default:

```bash
# Copy and preserve ACLs
cp -a source/ destination/

# Or explicitly
cp --preserve=all source/ destination/
```

`rsync` with `-A` flag preserves ACLs:

```bash
rsync -aA /srv/project/ /backup/project/
```

`tar` with `--xattrs` and `--acls` preserves extended attributes including ACLs:

```bash
# Create archive preserving ACLs
tar --acls --xattrs -czf /backup/project.tar.gz /srv/project/

# Restore preserving ACLs
tar --acls --xattrs -xzf /backup/project.tar.gz -C /
```


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** Give contractor `contractor1` read-only access to `/var/log/nginx/` without changing the group ownership of that directory (which is owned by `root:root` and managed by the nginx package).

```bash
# 1. Verify current state
ls -ld /var/log/nginx/
# drwx------ 2 nginx nginx ... /var/log/nginx/
getfacl /var/log/nginx/

# 2. Grant contractor1 read+execute on the directory itself
# (execute = enter the directory; read = list its contents)
sudo setfacl -m u:contractor1:r-x /var/log/nginx/

# 3. Grant read access to existing log files
sudo setfacl -R -m u:contractor1:r-- /var/log/nginx/

# 4. Set default ACL so future log files also get read access
sudo setfacl -m d:u:contractor1:r-- /var/log/nginx/

# 5. Verify
getfacl /var/log/nginx/
# user:contractor1:r-x
# default:user:contractor1:r--

# 6. Test read access as contractor1
sudo -u contractor1 ls /var/log/nginx/
sudo -u contractor1 tail /var/log/nginx/access.log
# Both should succeed

# 7. Verify write is denied
sudo -u contractor1 bash -c "> /var/log/nginx/test.log"
# Permission denied

# 8. Verify group ownership is unchanged
ls -ld /var/log/nginx/
# drwx------+ 2 nginx nginx ...
# The + confirms ACL is set but group is still nginx
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely cause | Fix |
|---|---|---|
| Access still denied despite correct ACL | Mask is too restrictive | Run `getfacl` and look for `#effective:` comments; adjust mask with `setfacl -m mask::rwx` |
| New files inside directory do not inherit ACL | Default ACL not set | Add default ACL: `setfacl -m d:u:user:perm /dir` |
| `setfacl: command not found` | `acl` package not installed | `sudo dnf install -y acl` |
| ACL disappears after `chmod` | `chmod` on a file recalculates the mask | Re-apply the ACL after `chmod`; prefer `setfacl` over `chmod` for ACL-managed paths |
| `cp` to a new location loses ACLs | `cp` without `-a` or `--preserve=all` | Use `cp -a` or `rsync -aA` |
| `getfacl` shows no entries on a file that should have ACLs | File was created before default ACL was set | Re-apply explicitly: `setfacl -R -m u:user:perm /dir` |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Managing file systems: ACLs](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_file_systems/index) | Official ACL management guide for RHEL |
| [`acl` man page](https://man7.org/linux/man-pages/man5/acl.5.html) | POSIX ACL specification and format |
| [`setfacl` / `getfacl` man pages](https://man7.org/linux/man-pages/man1/setfacl.1.html) | Complete option reference |

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab: Shared Team Directory](labs/01-shared-team-dir.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
