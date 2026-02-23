# ACLs — When and How

Standard Unix permissions give you three permission sets: user, group, other.
**Access Control Lists (ACLs)** extend this by letting you grant permissions
to **any number of specific users or groups** on a single file or directory.

---

## When to use ACLs

Use ACLs when standard permissions are not expressive enough. Examples:

- A shared project directory where two separate groups each need different access
- Grant one specific user read access to a file without changing group ownership
- Set default permissions so all new files in a directory inherit the right ACLs

!!! tip "ACLs don't replace standard permissions"
    ACLs augment standard Unix permissions. The effective permission for a user
    is the **most specific** match (user ACL > group ACL > other). When an ACL
    is present, a **mask** also applies — see below.

---

## Check if ACLs are supported

XFS (the default filesystem on RHEL) supports ACLs natively. No mount options
needed.

```bash
tune2fs -l /dev/vda1 2>/dev/null | grep "Default mount" || echo "XFS - ACLs native"
```

---

## Install ACL tools

```bash
sudo dnf install -y acl
```

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

---

## Remove ACLs

```bash
# Remove a specific user ACL
setfacl -x u:alice /srv/project/report.txt

# Remove all ACLs (reverts to standard permissions)
setfacl -b /srv/project/report.txt
```

---

## The ACL mask

The **mask** limits the maximum effective permissions for named users and groups
(not the owning user or other). It is recalculated automatically when you set
ACLs.

```bash
# Force the mask to a specific value
setfacl -m mask::r-x /srv/project/
```

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

---

## Next step

→ [Lab: Shared Team Directory](labs/shared-team-dir.md)
