# Editing Files — nano and vim

You will edit configuration files constantly as a RHEL admin. This chapter
covers two editors: **nano** (beginner-friendly) and **vim** (the editor you
will eventually need for speed and remote sessions).

---

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
| `Ctrl+K` | Cut the current line |
| `Ctrl+U` | Paste |
| `Ctrl+G` | Show full help |

> **💡 sudo nano**
> To edit a system file:
> ```bash
> sudo nano /etc/hosts
> ```
>

---

## vim — the editor you will need

vim is installed on virtually every Linux server. Once you learn its basic
modes, it is extremely fast.

### Install vim on a minimal system

```bash
sudo dnf install -y vim
```

### The two modes you must know

| Mode | How to enter | What you can do |
|---|---|---|
| **Normal** | Press `Esc` | Navigate, copy, paste, delete |
| **Insert** | Press `i` | Type text |

vim always starts in **Normal** mode. You cannot type text until you press `i`.

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
| `A` | Insert at end of line |
| `o` | Insert new line below |
| `dd` | Delete (cut) current line |
| `yy` | Yank (copy) current line |
| `p` | Paste after cursor |
| `u` | Undo |
| `Ctrl+R` | Redo |
| `/pattern` | Search forward |
| `n` | Next match |
| `gg` | Go to first line |
| `G` | Go to last line |
| `:<number>` | Go to line number |
| `:w` | Save |
| `:q` | Quit (fails if unsaved changes) |
| `:wq` | Save and quit |
| `:q!` | Quit without saving |

> **💡 Stuck in vim?**
> If you are stuck and see unexpected characters, press `Esc` several times
> then type `:q!` and press `Enter`. This exits without saving.
>

---

## Which editor to use when

| Situation | Recommended |
|---|---|
| Quick config file edit | `nano` |
| Remote sessions where nano is not installed | `vim` |
| Writing scripts or long files | `vim` |
| Sudoedit (editing protected files safely) | `sudo EDITOR=nano visudo` |

---

## Environment variables for editor preference

Set your default editor in `~/.bashrc`:

```bash
echo 'export EDITOR=vim' >> ~/.bashrc
source ~/.bashrc
```

Commands like `crontab -e` and `visudo` will use `$EDITOR` automatically.

---

## Further reading

| Resource | Notes |
|---|---|
| [Vim official documentation](https://www.vim.org/docs.php) | Full vim reference including macros, registers, and plugins |
| [Vim Adventures](https://vim-adventures.com/) | Interactive game for learning vim motions |
| [nano documentation](https://www.nano-editor.org/docs.php) | Official nano manual |
| [vimtutor](https://vimschool.netlify.app/introduction/vimtutor/) | Built-in interactive tutorial; run `vimtutor` in any terminal |

---

## Next step

→ [Users, Groups, Permissions](permissions.md)
