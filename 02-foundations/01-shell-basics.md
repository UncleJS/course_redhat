# Shell Basics — pwd, ls, cd

The shell is your primary interface to RHEL. This chapter covers the commands
you will use every single session.

---
<a name="toc"></a>

## Table of contents

- [The prompt](#the-prompt)
- [Where am I? — `pwd`](#where-am-i-pwd)
- [What is here? — `ls`](#what-is-here-ls)
- [Moving around — `cd`](#moving-around-cd)
- [Absolute vs relative paths](#absolute-vs-relative-paths)
- [Important directories to know](#important-directories-to-know)
- [Useful shortcuts](#useful-shortcuts)


## The prompt

When you log in you see a prompt like:

```
[rhel@rhel10-lab ~]$
```

| Part | Meaning |
|---|---|
| `rhel` | Current username |
| `rhel10-lab` | Hostname |
| `~` | Current directory (`~` = your home directory) |
| `$` | Regular user (would be `#` for root) |


[↑ Back to TOC](#toc)

---

## Where am I? — `pwd`

```bash
$ pwd
```

Output: `/home/rhel` (or wherever you are)

`pwd` = **p**rint **w**orking **d**irectory.


[↑ Back to TOC](#toc)

---

## What is here? — `ls`

```bash
# List current directory
ls

# Long format (permissions, owner, size, date)
ls -l

# Include hidden files (names starting with .)
ls -la

# Human-readable file sizes
ls -lh

# List a specific directory
ls -l /etc
```


[↑ Back to TOC](#toc)

---

## Moving around — `cd`

```bash
# Go to your home directory
cd

# Go to a specific path (absolute)
cd /etc/sysconfig

# Go up one level
cd ..

# Go up two levels
cd ../..

# Go to the previous directory
cd -
```

> **💡 Tab completion**
> Press `Tab` to auto-complete paths and command names. Press `Tab` twice
> to see all options when there are multiple matches. Use it constantly.
>


[↑ Back to TOC](#toc)

---

## Absolute vs relative paths

| Type | Example | Meaning |
|---|---|---|
| Absolute | `/etc/hosts` | Always starts from root `/` |
| Relative | `../hosts` | Relative to your current directory |


[↑ Back to TOC](#toc)

---

## Important directories to know

| Path | Contents |
|---|---|
| `/` | Root of the filesystem |
| `/home` | User home directories |
| `/etc` | System configuration files |
| `/var` | Variable data (logs, spool, databases) |
| `/usr` | Installed programs and libraries |
| `/tmp` | Temporary files (cleared on reboot) |
| `/boot` | Kernel and bootloader files |
| `/dev` | Device files |
| `/proc` | Virtual filesystem for kernel/process info |
| `/sys` | Virtual filesystem for hardware/kernel data |
| `/run` | Runtime data (PIDs, sockets) — cleared on reboot |


[↑ Back to TOC](#toc)

---

## Useful shortcuts

| Shortcut | Effect |
|---|---|
| `Ctrl+C` | Cancel a running command |
| `Ctrl+L` | Clear the screen |
| `Ctrl+A` | Jump to start of line |
| `Ctrl+E` | Jump to end of line |
| `Up arrow` | Previous command |
| `!!` | Repeat last command |
| `!$` | Last argument of previous command |
| `history` | Show command history |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [The Linux Command Line (free book)](https://linuxcommand.org/tlcl.php) | Comprehensive introduction to the Bash shell |
| [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html) | Official GNU Bash documentation |
| [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html) | Defines where everything lives under `/` |

---

## Next step

→ [Files and Text](02-files-and-text.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
