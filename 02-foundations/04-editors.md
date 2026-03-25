
[↑ Back to TOC](#toc)

# Editing Files — nano and vim
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

You will edit configuration files constantly as a RHEL admin. This chapter
covers two editors: **nano** (beginner-friendly) and **vim** (the editor you
will eventually need for speed and remote sessions).

As a sysadmin you will frequently need to change a single line in `/etc/ssh/sshd_config`, uncomment an option in `/etc/fstab`, or write a short shell script. Having a reliable, efficient editor workflow prevents the common failure mode of making incorrect edits and then struggling to recover.

**vim** is the editor you should invest in. It is present on virtually every Linux system — even minimal container images and rescue environments — because it ships as part of the `vim-minimal` package which is installed by default on RHEL. Once the modal editing model becomes muscle memory, vim is dramatically faster than any mouse-driven editor for structured text like configuration files.

**nano** is appropriate for quick edits when you are under time pressure or teaching someone unfamiliar with vim. Its always-visible shortcut bar removes the "how do I save this?" barrier.

The key mental model for vim: the editor has **modes**. In Normal mode, every keystroke is a command. In Insert mode, keystrokes add text. This separation is what makes vim fast — navigation and editing operations require no modifier keys.

---
<a name="toc"></a>

## Table of contents

- [nano — the beginner's editor](#nano-the-beginners-editor)
  - [Key shortcuts](#key-shortcuts)
- [vim — the editor you will need](#vim-the-editor-you-will-need)
  - [Install vim on a minimal system](#install-vim-on-a-minimal-system)
  - [The two modes you must know](#the-two-modes-you-must-know)
  - [Getting started](#getting-started)
  - [Essential Normal mode commands](#essential-normal-mode-commands)
  - [Searching and substituting](#searching-and-substituting)
  - [Working with multiple files](#working-with-multiple-files)
- [Which editor to use when](#which-editor-to-use-when)
- [Environment variables for editor preference](#environment-variables-for-editor-preference)
- [Editing system files safely — visudo and systemctl edit](#editing-system-files-safely)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## nano — the beginner's editor

nano is simple: open a file, type, save. The help bar at the bottom shows all
shortcuts.

```bash
nano /tmp/testfile.txt
```

### Key shortcuts

| Keys | Action |
|---|---|
| `Ctrl+O`, `Enter` | Save the file |
| `Ctrl+X` | Exit |
| `Ctrl+W` | Search |
| `Ctrl+\` | Search and replace |
| `Ctrl+K` | Cut the current line |
| `Ctrl+U` | Paste |
| `Ctrl+G` | Show full help |
| `Ctrl+_` | Go to line number |
| `Alt+U` | Undo |
| `Alt+E` | Redo |
| `Ctrl+C` | Show cursor position |

> **💡 sudo nano**
> To edit a system file:
> ```bash
> sudo nano /etc/hosts
> ```
>


[↑ Back to TOC](#toc)

---

## vim — the editor you will need

vim is installed on virtually every Linux server. Once you learn its basic
modes, it is extremely fast.

### Install vim on a minimal system

```bash
sudo dnf install -y vim
```

`vim-minimal` (which provides `vi`) is installed by default. The full `vim` package adds syntax highlighting, spell check, and plugin support.

### The two modes you must know

| Mode | How to enter | What you can do |
|---|---|---|
| **Normal** | Press `Esc` | Navigate, copy, paste, delete |
| **Insert** | Press `i` | Type text |

vim always starts in **Normal** mode. You cannot type text until you press `i`.

There are additional modes — **Visual** (text selection), **Command-line** (`:` commands), **Replace** (`R`) — but Normal and Insert are sufficient to be productive.

### Getting started

```bash
vim /tmp/testvim.txt
```

1. Press `i` → you are now in Insert mode (you see `-- INSERT --` at the bottom)
2. Type some text
3. Press `Esc` → back to Normal mode
4. Type `:wq` → save and quit

### Essential Normal mode commands

| Command | Action |
|---|---|
| `i` | Insert before cursor |
| `I` | Insert at beginning of line |
| `a` | Append after cursor |
| `A` | Insert at end of line |
| `o` | Insert new line below |
| `O` | Insert new line above |
| `dd` | Delete (cut) current line |
| `D` | Delete from cursor to end of line |
| `dw` | Delete word |
| `yy` | Yank (copy) current line |
| `yw` | Yank word |
| `p` | Paste after cursor |
| `P` | Paste before cursor |
| `u` | Undo |
| `Ctrl+R` | Redo |
| `x` | Delete character under cursor |
| `r` | Replace single character |
| `cw` | Change word (delete and enter Insert mode) |
| `/pattern` | Search forward |
| `?pattern` | Search backward |
| `n` | Next match |
| `N` | Previous match |
| `*` | Search for word under cursor |
| `gg` | Go to first line |
| `G` | Go to last line |
| `:<number>` | Go to line number |
| `w` | Jump forward one word |
| `b` | Jump backward one word |
| `0` | Go to start of line |
| `$` | Go to end of line |
| `%` | Jump to matching bracket |
| `:w` | Save |
| `:q` | Quit (fails if unsaved changes) |
| `:wq` | Save and quit |
| `:q!` | Quit without saving |
| `:x` | Save and quit (only writes if changed) |

> **💡 Stuck in vim?**
> If you are stuck and see unexpected characters, press `Esc` several times
> then type `:q!` and press `Enter`. This exits without saving.
>


[↑ Back to TOC](#toc)

---

### Searching and substituting

vim's `:substitute` command is one of its most powerful features:

```vim
# Replace first occurrence on current line
:s/old/new/

# Replace all occurrences on current line
:s/old/new/g

# Replace all occurrences in entire file
:%s/old/new/g

# Replace with confirmation prompt
:%s/old/new/gc

# Case-insensitive replace
:%s/old/new/gi

# Replace on a range of lines (lines 5 to 20)
:5,20s/old/new/g
```

Practical examples for sysadmin work:

```vim
# Disable PermitRootLogin
:%s/PermitRootLogin yes/PermitRootLogin no/

# Comment out a line containing a pattern
:%s/^MaxAuthTries/#MaxAuthTries/

# Remove all trailing whitespace
:%s/\s\+$//g
```


[↑ Back to TOC](#toc)

---

### Working with multiple files

```bash
# Open two files side by side
vim -O /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Open two files stacked horizontally
vim -o /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
```

Inside vim:

```vim
:e /etc/hosts          " open another file in current window
:sp /etc/hosts         " horizontal split
:vsp /etc/hosts        " vertical split
Ctrl+W then arrow      " move between splits
:wqa                   " save all and quit
```


[↑ Back to TOC](#toc)

---

## Which editor to use when

| Situation | Recommended |
|---|---|
| Quick config file edit | `nano` |
| Remote sessions where nano is not installed | `vim` |
| Writing scripts or long files | `vim` |
| Sudoedit (editing protected files safely) | `sudo EDITOR=nano visudo` |
| Editing systemd unit overrides | `systemctl edit <unit>` |


[↑ Back to TOC](#toc)

---

## Environment variables for editor preference

Set your default editor in `~/.bashrc`:

```bash
echo 'export EDITOR=vim' >> ~/.bashrc
source ~/.bashrc
```

Commands like `crontab -e` and `visudo` will use `$EDITOR` automatically.

`VISUAL` is a second editor variable for full-screen editors (as opposed to line editors). Most tools check `VISUAL` first, then fall back to `EDITOR`.

```bash
echo 'export VISUAL=vim' >> ~/.bashrc
echo 'export EDITOR=vim' >> ~/.bashrc
```


[↑ Back to TOC](#toc)

---

## Editing system files safely

### visudo

Always edit `/etc/sudoers` through `visudo`, which validates the syntax before saving and prevents you from locking yourself out of sudo:

```bash
sudo visudo

# Use a specific editor
sudo EDITOR=vim visudo

# Edit a drop-in file in /etc/sudoers.d/
sudo visudo -f /etc/sudoers.d/developers
```

### systemctl edit

For systemd unit overrides, use `systemctl edit` which creates the correct override path and reloads the daemon:

```bash
# Add an override without replacing the whole unit file
sudo systemctl edit sshd

# Replace the entire unit file
sudo systemctl edit --full sshd
```

This creates files in `/etc/systemd/system/<unit>.d/override.conf` (or replaces the unit in `/etc/systemd/system/`), which survive package updates.

> **Exam tip:** Never edit unit files directly in `/usr/lib/systemd/system/` — package updates overwrite them. Use `systemctl edit` to create overrides in `/etc/systemd/system/`.


[↑ Back to TOC](#toc)

---

## Worked example

**Scenario:** Harden the SSH daemon on a production server by disabling root login and password authentication, then verify the service reloads correctly.

```bash
# 1. Back up the original config
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# 2. Open in vim
sudo vim /etc/ssh/sshd_config

# Inside vim:
# Search for PermitRootLogin
#   /PermitRootLogin  then Enter
# Change the line value:
#   position cursor on "yes", press cw, type "no", press Esc
# Search for PasswordAuthentication:
#   /PasswordAuthentication  then Enter
# Ensure it reads "no":
#   use the substitute command: :s/PasswordAuthentication yes/PasswordAuthentication no/
# Save and exit:
#   :wq

# 3. Validate syntax before restarting
sudo sshd -t
# No output = syntax OK; any output = error that must be fixed

# 4. Reload the service (no dropped connections, unlike restart)
sudo systemctl reload sshd

# 5. Verify the change took effect
sudo sshd -T | grep -E "permitrootlogin|passwordauthentication"
```

If `sshd -t` shows an error, open the backup: `sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config` and start over.


[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Symptom | Likely cause | Fix |
|---|---|---|
| Accidentally typed text in Normal mode | Forgot to press `i` before typing | Press `u` repeatedly to undo, then navigate correctly |
| `:wq` fails with "E45: 'readonly' option is set" | File opened read-only | Reopen with `sudo vim` or use `:w !sudo tee %` to write as root |
| Saved a broken sshd_config and lost SSH access | No syntax check before restart | Always run `sudo sshd -t` before `systemctl restart sshd` |
| nano saves to wrong filename | Pressed wrong key at save prompt | At the "File Name to Write:" prompt, verify the path before Enter |
| vim shows `SWAPFILE already exists` | Previous vim session crashed | Read the recovery options carefully; use `vim -r` to recover, then delete the `.swp` file |
| `visudo` reports syntax error after edit | Typo in sudoers rule | visudo refuses to save — correct the error it highlights before exiting |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Vim official documentation](https://www.vim.org/docs.php) | Full vim reference including macros, registers, and plugins |
| [Vim Adventures](https://vim-adventures.com/) | Interactive game for learning vim motions |
| [nano documentation](https://www.nano-editor.org/docs.php) | Official nano manual |
| [vimtutor](https://vimschool.netlify.app/introduction/vimtutor/) | Built-in interactive tutorial; run `vimtutor` in any terminal |

---


[↑ Back to TOC](#toc)

## Next step

→ [Users, Groups, Permissions](05-permissions.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
