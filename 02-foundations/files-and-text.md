# Files and Text — cp, mv, rm, less

---

## Viewing files

```bash
# View a short file
cat /etc/hostname

# View a long file with scrolling (press q to quit)
less /etc/os-release

# First 20 lines
head -n 20 /var/log/messages

# Last 20 lines
tail -n 20 /var/log/messages

# Follow a log in real time (Ctrl+C to stop)
tail -f /var/log/messages
```

---

## Copying files — `cp`

```bash
# Copy a file
cp /etc/hosts /tmp/hosts.bak

# Copy a directory recursively
cp -r /etc/sysconfig /tmp/sysconfig-bak

# Copy and preserve permissions/timestamps
cp -a /etc/hosts /tmp/hosts.bak
```

---

## Moving and renaming — `mv`

```bash
# Move file to another directory
mv /tmp/hosts.bak /home/rhel/

# Rename a file
mv /home/rhel/hosts.bak /home/rhel/hosts.old

# Move directory
mv /tmp/sysconfig-bak /home/rhel/
```

---

## Removing files — `rm`

```bash
# Remove a file
rm /tmp/oldfile.txt

# Remove a directory and its contents
rm -r /tmp/olddir/

# Force removal (no confirmation)
rm -f /tmp/stubborn.txt
```

> **🚨 rm is permanent**
> There is no Trash on the CLI. `rm` deletes immediately.
> Double-check your path before running it, especially with `-r` or wildcards.
>

> **⚠️ Do NOT do this**
> ```bash
> rm -rf /   # destroys the entire system
> rm -rf /*  # also destroys the entire system
> ```
> RHEL has protection against `rm -rf /` but always be careful with `rm -r`.
>

---

## Creating directories — `mkdir`

```bash
# Create one directory
mkdir /tmp/mydir

# Create nested directories in one command
mkdir -p /tmp/project/src/lib
```

---

## Finding files — `find`

```bash
# Find by name
find /etc -name "*.conf"

# Find by type (f=file, d=directory)
find /var/log -type f -name "*.log"

# Find files modified in the last 24 hours
find /etc -mtime -1
```

---

## Searching inside files — `grep`

```bash
# Search for a pattern in a file
grep "PermitRootLogin" /etc/ssh/sshd_config

# Case-insensitive search
grep -i "error" /var/log/messages

# Show line numbers
grep -n "failed" /var/log/secure

# Recursive search in a directory
grep -r "192.168.1" /etc/
```

---

## Counting lines, words, characters — `wc`

```bash
wc -l /etc/passwd        # number of lines
wc -w /etc/hosts         # number of words
```

---

## File details — `stat` and `file`

```bash
# Full metadata (permissions, timestamps, inode)
stat /etc/hosts

# Identify file type regardless of extension
file /usr/bin/bash
file /etc/passwd
```

---

## Next step

→ [Pipes and Redirection](pipes-redirection.md)
