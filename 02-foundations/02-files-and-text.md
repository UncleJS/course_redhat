
[↑ Back to TOC](#toc)

# Files and Text — cp, mv, rm, less
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

On Linux, **everything is a file** — configuration, devices, processes, sockets. The ability to view, copy, move, search, and inspect files is therefore the most fundamental sysadmin skill. You will use these commands in every troubleshooting session and every change-management window.

The core tools covered here come from **GNU coreutils** (`cp`, `mv`, `rm`, `mkdir`, `wc`, `stat`) and from **util-linux** / **findutils** (`find`). They are always available on a RHEL system, even in minimal installations. `grep` is from **GNU grep** and understands both basic and extended POSIX regular expressions.

The mental model: files exist in a directory tree, each identified by a path. Every file has an **inode** (metadata: permissions, timestamps, ownership) and one or more **directory entries** pointing to it (hard links). Understanding the distinction between a filename and the inode it points to explains why `mv` is instant within a filesystem but `cp` is not, and why `rm` removes a directory entry rather than immediately freeing disk space.

---
<a name="toc"></a>

## Table of contents

- [Viewing files](#viewing-files)
- [Copying files — `cp`](#copying-files-cp)
- [Moving and renaming — `mv`](#moving-and-renaming-mv)
- [Removing files — `rm`](#removing-files-rm)
- [Creating directories — `mkdir`](#creating-directories-mkdir)
- [Creating links — `ln`](#creating-links-ln)
- [Finding files — `find`](#finding-files-find)
- [Searching inside files — `grep`](#searching-inside-files-grep)
- [Counting lines, words, characters — `wc`](#counting-lines-words-characters-wc)
- [File details — `stat` and `file`](#file-details-stat-and-file)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Viewing files

```bash
# View a short file
cat /etc/hostname

# Concatenate and number lines
cat -n /etc/hosts

# View a long file with scrolling (press q to quit)
less /etc/os-release

# First 20 lines
head -n 20 /var/log/messages

# Last 20 lines
tail -n 20 /var/log/messages

# Follow a log in real time (Ctrl+C to stop)
tail -f /var/log/messages

# Follow multiple files simultaneously
tail -f /var/log/messages /var/log/secure
```

`less` key bindings you should know:

| Key | Action |
|---|---|
| `Space` / `f` | Page down |
| `b` | Page up |
| `/pattern` | Search forward |
| `?pattern` | Search backward |
| `n` / `N` | Next / previous match |
| `g` | Go to first line |
| `G` | Go to last line |
| `q` | Quit |
| `-S` (toggle) | Chop long lines instead of wrapping |


[↑ Back to TOC](#toc)

---

## Copying files — `cp`

```bash
# Copy a file
cp /etc/hosts /tmp/hosts.bak

# Copy a directory recursively
cp -r /etc/sysconfig /tmp/sysconfig-bak

# Copy and preserve permissions/timestamps/SELinux context
cp -a /etc/hosts /tmp/hosts.bak

# Copy only if source is newer
cp -u /etc/hosts /tmp/hosts.bak

# Prompt before overwriting
cp -i /etc/hosts /tmp/hosts.bak

# Show each file as it is copied
cp -v /etc/hosts /tmp/hosts.bak
```

> **Exam tip:** `cp -a` (archive mode) is equivalent to `cp -dR --preserve=all`. Use it when copying trees that must retain ownership, permissions, and timestamps — for example, backing up `/etc` before making changes.


[↑ Back to TOC](#toc)

---

## Moving and renaming — `mv`

```bash
# Move file to another directory
mv /tmp/hosts.bak /home/rhel/

# Rename a file
mv /home/rhel/hosts.bak /home/rhel/hosts.old

# Move directory
mv /tmp/sysconfig-bak /home/rhel/

# Prompt before overwriting
mv -i /tmp/hosts.bak /home/rhel/

# Do not overwrite if destination exists
mv -n /tmp/hosts.bak /home/rhel/
```

`mv` within the same filesystem is a metadata-only operation (rename the directory entry); it completes instantly regardless of file size. `mv` across filesystems copies the data and then removes the source — equivalent to `cp` + `rm`.


[↑ Back to TOC](#toc)

---

## Removing files — `rm`

```bash
# Remove a file
rm /tmp/oldfile.txt

# Remove a directory and its contents
rm -r /tmp/olddir/

# Force removal (no confirmation)
rm -f /tmp/stubborn.txt

# Prompt before each removal
rm -i /tmp/oldfile.txt

# Verbose — print each file being removed
rm -v /tmp/oldfile.txt
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

If you need recoverable deletion, use `mv` to a trash directory or install `trash-cli` from EPEL:

```bash
# Safe pattern: move to a scratch area instead of deleting directly
mv /tmp/suspicious-file.txt /tmp/trash-$(date +%s)/
```


[↑ Back to TOC](#toc)

---

## Creating directories — `mkdir`

```bash
# Create one directory
mkdir /tmp/mydir

# Create nested directories in one command
mkdir -p /tmp/project/src/lib

# Create with specific permissions
mkdir -m 750 /srv/private-dir

# Verbose output
mkdir -v /tmp/mydir
```


[↑ Back to TOC](#toc)

---

## Creating links — `ln`

Linux supports two types of links:

| Type | Command | Crosses filesystems? | Survives source deletion? |
|---|---|---|---|
| Hard link | `ln src dst` | No | Yes (inode stays alive) |
| Symbolic (soft) link | `ln -s src dst` | Yes | No (dangling link) |

```bash
# Hard link — both names point to the same inode
ln /etc/hosts /tmp/hosts-hardlink
ls -li /etc/hosts /tmp/hosts-hardlink   # same inode number

# Symbolic link
ln -s /etc/nginx/nginx.conf /tmp/nginx.conf
ls -l /tmp/nginx.conf                   # shows -> target
```

> **Exam tip:** Hard links cannot span filesystem boundaries and cannot link to directories (except by root, which is rarely done). Use symbolic links for cross-filesystem or cross-directory references.


[↑ Back to TOC](#toc)

---

## Finding files — `find`

```bash
# Find by name
find /etc -name "*.conf"

# Case-insensitive name match
find /etc -iname "sshd*"

# Find by type (f=file, d=directory, l=symlink)
find /var/log -type f -name "*.log"

# Find files modified in the last 24 hours
find /etc -mtime -1

# Find files larger than 100 MB
find /var -size +100M

# Find files owned by a specific user
find /home -user alice

# Find files with SUID bit set (security audit)
find / -perm /4000 -type f 2>/dev/null

# Execute a command on each result
find /tmp -name "*.tmp" -exec rm -f {} \;

# Find and delete (more efficient than -exec rm)
find /tmp -name "*.tmp" -delete
```

`find` evaluates expressions left to right and short-circuits on `-a` (AND, default) and `-o` (OR). The `-prune` action skips a directory without descending into it.

```bash
# Skip the /proc filesystem when searching from root
find / -path /proc -prune -o -name "*.conf" -print
```


[↑ Back to TOC](#toc)

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

# Show only the filename (not the matching line)
grep -rl "PermitRootLogin" /etc/

# Invert match — lines that do NOT contain the pattern
grep -v "^#" /etc/ssh/sshd_config

# Extended regex (alternation, + quantifier, etc.)
grep -E "error|warning|critical" /var/log/messages

# Show N lines of context around each match
grep -C 3 "Failed password" /var/log/secure

# Count matching lines
grep -c "Failed" /var/log/secure

# Whole-word match only
grep -w "root" /etc/passwd
```

`grep` understands three regex dialects: BRE (default), ERE (`-E`), and Perl (`-P`). For most sysadmin work ERE (`-E`) is sufficient and more readable.


[↑ Back to TOC](#toc)

---

## Counting lines, words, characters — `wc`

```bash
wc -l /etc/passwd        # number of lines
wc -w /etc/hosts         # number of words
wc -c /etc/hosts         # number of bytes
wc -m /etc/hosts         # number of characters (multibyte-aware)

# Count entries in /etc/passwd
wc -l < /etc/passwd

# Count how many times a string appears in a log
grep -c "Failed password" /var/log/secure
```


[↑ Back to TOC](#toc)

---

## File details — `stat` and `file`

```bash
# Full metadata (permissions, timestamps, inode)
stat /etc/hosts

# Identify file type regardless of extension
file /usr/bin/bash
file /etc/passwd
file /tmp/unknown.bin

# Check if a path is a symlink and where it points
stat -c "%F %N" /etc/localtime
```

`stat` output includes:
- **File** — path
- **Size** — bytes
- **Blocks** — 512-byte disk blocks allocated
- **IO Block** — filesystem block size
- **Inode** — inode number
- **Links** — hard link count
- **Access** — last read time (atime)
- **Modify** — last content change time (mtime)
- **Change** — last metadata change time (ctime)

```bash
# Custom stat format: show only permissions and owner
stat -c "%a %U:%G %n" /etc/hosts
# 644 root:root /etc/hosts
```


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** A developer reports that a configuration file was modified overnight and the service is broken. You need to find what changed.

```bash
# 1. Find files in /etc modified in the last 8 hours
find /etc -mtime -0.33 -type f 2>/dev/null
# Or more precisely, in the last 480 minutes:
find /etc -newer /tmp/reference-timestamp -type f

# Create a reference timestamp file at a known good time
# (Do this BEFORE any changes during a maintenance window)
touch -t 202601150200 /tmp/maintenance-start

# 2. Find recently modified files relative to that timestamp
find /etc -newer /tmp/maintenance-start -type f

# 3. Inspect the suspicious file
stat /etc/ssh/sshd_config
# Check Modify time

# 4. Search for obvious bad values
grep -n "PermitRootLogin yes" /etc/ssh/sshd_config
grep -vE "^#|^$" /etc/ssh/sshd_config | less

# 5. Confirm the file is a text file (not accidentally binary)
file /etc/ssh/sshd_config

# 6. Count lines to compare with backup
wc -l /etc/ssh/sshd_config
wc -l /etc/ssh/sshd_config.rpmsave 2>/dev/null
```


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely cause | Fix |
|---|---|---|
| `cp -r src/ dst/` creates extra nesting | Trailing slash on src copies contents; no slash copies directory itself | Decide: `cp -r src/ dst/` (contents only) vs `cp -r src dst/` (directory inside dst) |
| `mv` fails with "Invalid cross-device link" | Moving across filesystem boundaries without data copy | Use `cp -a` then `rm -r` instead |
| `find` returns "Permission denied" noise | No read access to some directories | Redirect stderr: `find / ... 2>/dev/null` |
| `grep` returns nothing but you are sure the pattern exists | Regex metacharacters not escaped | Quote the pattern; use `-F` for literal strings: `grep -F "1.2.3.4" /etc/hosts` |
| `rm -r` removes more than expected | Shell glob expanded to more than expected | Preview first: `ls /path/to/*.txt` before `rm /path/to/*.txt` |
| `stat` shows ctime changed but mtime unchanged | A permission or ownership change occurred | Separate events: mtime tracks content, ctime tracks metadata |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`find` man page](https://man7.org/linux/man-pages/man1/find.1.html) | Full reference for the most powerful file search tool |
| [`grep` man page](https://man7.org/linux/man-pages/man1/grep.1.html) | Pattern matching reference including regex |
| [GNU coreutils manual](https://www.gnu.org/software/coreutils/manual/coreutils.html) | Authoritative reference for `cp`, `mv`, `rm`, `ln`, and friends |

---


[↑ Back to TOC](#toc)

## Next step

→ [Pipes and Redirection](03-pipes-redirection.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
