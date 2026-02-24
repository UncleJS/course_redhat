# Users, Groups, and Permissions

Linux uses a permission model based on **users**, **groups**, and a set of
**read/write/execute** bits. Understanding this is essential for everything
that follows.

---

## The permission model

Every file and directory has three permission sets:

```
-rw-r--r--  1  rhel  rhel  1234  Feb 23 10:00  file.txt
│└┬┘└┬┘└┬┘     │     │
│ │   │   │     │     └── Group owner
│ │   │   │     └──────── User owner
│ │   │   └────────────── Other (everyone else)
│ │   └────────────────── Group permissions
│ └────────────────────── User permissions
└──────────────────────── File type (- = file, d = dir, l = symlink)
```

### Permission bits

| Symbol | Numeric | File meaning | Directory meaning |
|---|---|---|---|
| `r` | 4 | Read file contents | List directory contents |
| `w` | 2 | Modify file | Create/delete files inside |
| `x` | 1 | Execute file | Enter (cd into) directory |
| `-` | 0 | Permission not set | Permission not set |

---

## Viewing permissions — `ls -l`

```bash
ls -l /etc/hosts
```

Example output:

```
-rw-r--r--. 1 root root 174 Jan 10 09:00 /etc/hosts
```

The `.` after the permission string indicates an SELinux context is set.

---

## Changing permissions — `chmod`

```bash
# Symbolic form
chmod u+x script.sh        # add execute for user
chmod g-w file.txt         # remove write for group
chmod o= file.txt          # clear all permissions for other
chmod a+r file.txt         # add read for all (user, group, other)

# Numeric (octal) form
chmod 644 file.txt         # rw-r--r--
chmod 755 script.sh        # rwxr-xr-x
chmod 600 private.key      # rw-------
chmod 700 private-dir/     # rwx------
```

### Common permission patterns

| Octal | Pattern | Use case |
|---|---|---|
| `600` | rw------- | Private key, secret file |
| `644` | rw-r--r-- | Config file, web content |
| `664` | rw-rw-r-- | Group-editable file |
| `755` | rwxr-xr-x | Executable script, public directory |
| `750` | rwxr-x--- | Script accessible to group only |
| `700` | rwx------ | Private directory |

---

## Changing ownership — `chown`

```bash
# Change user owner
sudo chown rhel file.txt

# Change user and group owner
sudo chown rhel:developers file.txt

# Change group only
sudo chown :developers file.txt

# Recursive (directory and all contents)
sudo chown -R rhel:developers /srv/project/
```

---

## Changing group — `chgrp`

```bash
sudo chgrp developers file.txt
```

---

## Managing groups

```bash
# Create a group
sudo groupadd developers

# Add a user to a group
sudo usermod -aG developers rhel

# View your groups
groups

# View all groups
getent group
```

> **💡 The -aG flag**
> `-aG` means **append** to groups. Without `-a`, `usermod -G` **replaces**
> all supplementary groups — a common mistake that locks users out.
>

---

## umask — default permissions

`umask` defines permissions that are **removed** from newly created files and
directories.

```bash
umask          # show current umask (default: 0022)
```

With `umask 0022`:
- New files: `0666 - 0022 = 0644` (rw-r--r--)
- New directories: `0777 - 0022 = 0755` (rwxr-xr-x)

---

## Special permission bits

| Bit | On file | On directory |
|---|---|---|
| **SUID** (`4xxx`) | Run as file owner | N/A |
| **SGID** (`2xxx`) | Run as file group | New files inherit group |
| **Sticky** (`1xxx`) | N/A | Only owner can delete their own files |

```bash
# SGID on a shared directory (new files inherit group)
chmod g+s /srv/shared/
# or
chmod 2775 /srv/shared/

# Sticky bit (e.g., /tmp)
ls -ld /tmp
# drwxrwxrwt — the 't' is the sticky bit
```

---

## Next step

→ [ACLs](acls.md)
