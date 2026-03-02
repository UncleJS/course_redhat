# Getting Help — man, --help, apropos
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

One of the most important skills on any Linux system is knowing how to find
answers without leaving the terminal.

---
<a name="toc"></a>

## Table of contents

- [The `--help` flag](#the-help-flag)
- [man pages](#man-pages)
  - [Navigating a man page](#navigating-a-man-page)
  - [Man page sections](#man-page-sections)
- [`apropos` — search by keyword](#apropos-search-by-keyword)
- [`info` pages](#info-pages)
- [`/usr/share/doc`](#usrsharedoc)
- [Online resources (official)](#online-resources-official)
- [Quick reference: help commands](#quick-reference-help-commands)


## The `--help` flag

Almost every command accepts `--help`. It shows a short summary of options.

```bash
ls --help
dnf --help
systemctl --help
```

Use `--help` when you just need a quick reminder of a flag.


[↑ Back to TOC](#toc)

---

## man pages

`man` (manual) provides the full reference documentation for commands, config
files, and system calls.

```bash
man ls
man dnf
man 5 fstab     # section 5 = file formats
man 8 firewalld # section 8 = sysadmin commands
```

### Navigating a man page

| Key | Action |
|---|---|
| `j` / `k` or arrow keys | Scroll down / up |
| `Space` / `b` | Page down / page up |
| `/pattern` | Search forward |
| `n` / `N` | Next / previous search match |
| `q` | Quit |

### Man page sections

| Section | Content |
|---|---|
| 1 | User commands |
| 5 | File formats and config files |
| 7 | Overviews, conventions |
| 8 | System administration commands |

```bash
# See all sections available for a keyword
man -k passwd
```


[↑ Back to TOC](#toc)

---

## `apropos` — search by keyword

If you don't know the command name, `apropos` searches man page descriptions:

```bash
apropos firewall
apropos "network interface"
```

> **💡 Update the man database**
> If `apropos` returns nothing useful, update its index:
> ```bash
> sudo mandb
> ```
>


[↑ Back to TOC](#toc)

---

## `info` pages

Some GNU tools have richer documentation in `info` format:

```bash
info coreutils
info bash
```


[↑ Back to TOC](#toc)

---

## `/usr/share/doc`

Package documentation (changelogs, examples, READMEs) lives here:

```bash
ls /usr/share/doc/
ls /usr/share/doc/bash/
```


[↑ Back to TOC](#toc)

---

## Online resources (official)

| Resource | URL |
|---|---|
| RHEL 10 documentation | https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10 |
| Red Hat Knowledgebase | https://access.redhat.com/solutions |
| Package search | https://access.redhat.com/packages |


[↑ Back to TOC](#toc)

---

## Quick reference: help commands

```bash
# Short help
ls --help

# Full manual
man ls

# Config file format
man 5 fstab

# Search all man pages by keyword
apropos partition

# Find which package provides a command
dnf provides /usr/bin/ss
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [The Linux man-pages project](https://www.kernel.org/doc/man-pages/) | Upstream source for all Linux man pages |
| [`info` manual (GNU)](https://www.gnu.org/software/texinfo/manual/info-stnd/info-stnd.html) | Guide to the `info` documentation system |
| [explainshell.com](https://explainshell.com/) | Paste any command and get a breakdown of every flag |
| [TLDR Pages](https://tldr.sh/) | Community-maintained command cheatsheets — fast alternative to man |

---

## Next step

→ [Shell Basics](../02-foundations/01-shell-basics.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
