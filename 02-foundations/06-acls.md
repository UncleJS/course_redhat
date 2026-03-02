# ACLs — When and How
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Standard Unix permissions give you three permission sets: user, group, other.
**Access Control Lists (ACLs)** extend this by letting you grant permissions
to **any number of specific users or groups** on a single file or directory.

---
<a name="toc"></a>

## Table of contents

- [When to use ACLs](#when-to-use-acls)
- [Check if ACLs are supported](#check-if-acls-are-supported)
- [Install ACL tools](#install-acl-tools)
- [View ACLs — `getfacl`](#view-acls-getfacl)
- [Set ACLs — `setfacl`](#set-acls-setfacl)
- [Remove ACLs](#remove-acls)
- [The ACL mask](#the-acl-mask)
- [Preserve ACLs when copying](#preserve-acls-when-copying)


## When to use ACLs

Use ACLs when standard permissions are not expressive enough. Examples:

- A shared project directory where two separate groups each need different access
- Grant one specific user read access to a file without changing group ownership
- Set default permissions so all new files in a directory inherit the right ACLs

> **💡 ACLs don't replace standard permissions**
> ACLs augment standard Unix permissions. The effective permission for a user
> is the **most specific** match (user ACL > group ACL > other). When an ACL
> is present, a **mask** also applies — see below.
>


[↑ Back to TOC](#toc)

---

## Check if ACLs are supported

XFS (the default filesystem on RHEL) supports ACLs natively. No mount options
needed.

```bash
tune2fs -l /dev/vda1 2>/dev/null | grep "Default mount" || echo "XFS - ACLs native"
```


[↑ Back to TOC](#toc)

---

## Install ACL tools

```bash
sudo dnf install -y acl
```


[↑ Back to TOC](#toc)

---

## View ACLs — `getfacl`

```bash
getfacl /srv/project/
```

A file with no ACLs set shows:

```
# file: project/
# owner: root
# group: developers
user::rwx
group::rwx
other::r-x
```

A file with ACLs set shows extra `user:` or `group:` lines plus a `mask::`.


[↑ Back to TOC](#toc)

---

## Set ACLs — `setfacl`

```bash
# Grant user alice read+write on a file
setfacl -m u:alice:rw /srv/project/report.txt

# Grant group qa read-only on a directory
setfacl -m g:qa:r-x /srv/project/

# Set a default ACL (applies to newly created files inside the dir)
setfacl -m d:u:alice:rw /srv/project/

# Recursive — apply to directory and all existing contents
setfacl -R -m u:alice:rw /srv/project/
```


[↑ Back to TOC](#toc)

---

## Remove ACLs

```bash
# Remove a specific user ACL
setfacl -x u:alice /srv/project/report.txt

# Remove all ACLs (reverts to standard permissions)
setfacl -b /srv/project/report.txt
```


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


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Managing file systems: ACLs](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_file_systems/index) | Official ACL management guide for RHEL |
| [`acl` man page](https://man7.org/linux/man-pages/man5/acl.5.html) | POSIX ACL specification and format |
| [`setfacl` / `getfacl` man pages](https://man7.org/linux/man-pages/man1/setfacl.1.html) | Complete option reference |

---

## Next step

→ [Lab: Shared Team Directory](labs/01-shared-team-dir.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
