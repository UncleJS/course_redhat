# Getting Help — man, --help, apropos

One of the most important skills on any Linux system is knowing how to find
answers without leaving the terminal.

---

## The `--help` flag

Almost every command accepts `--help`. It shows a short summary of options.

```bash
ls --help
dnf --help
systemctl --help
```

Use `--help` when you just need a quick reminder of a flag.

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

---

## `info` pages

Some GNU tools have richer documentation in `info` format:

```bash
info coreutils
info bash
```

---

## `/usr/share/doc`

Package documentation (changelogs, examples, READMEs) lives here:

```bash
ls /usr/share/doc/
ls /usr/share/doc/bash/
```

---

## Online resources (official)

| Resource | URL |
|---|---|
| RHEL 10 documentation | https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10 |
| Red Hat Knowledgebase | https://access.redhat.com/solutions |
| Package search | https://access.redhat.com/packages |

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

→ [Shell Basics](../02-foundations/shell-basics.md)
