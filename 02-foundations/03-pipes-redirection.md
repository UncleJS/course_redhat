# Pipes and Redirection
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Pipes and redirection let you combine simple commands into powerful workflows.
This is one of the most useful concepts in Linux.

---
<a name="toc"></a>

## Table of contents

- [Output redirection](#output-redirection)
- [Input redirection](#input-redirection)
- [Pipes — `|`](#pipes)
- [Useful commands for pipes](#useful-commands-for-pipes)
  - [`sort`](#sort)
  - [`uniq`](#uniq)
  - [`cut`](#cut)
  - [`awk`](#awk)
  - [`tee`](#tee)
- [Here-strings and here-documents](#here-strings-and-here-documents)


## Output redirection

```bash
# Write stdout to a file (overwrites)
ls -l /etc > /tmp/etc-listing.txt

# Append stdout to a file
echo "new line" >> /tmp/myfile.txt

# Discard output
sudo dnf upgrade -y > /dev/null

# Redirect stderr (error output) to a file
ls /nonexistent 2> /tmp/errors.txt

# Redirect both stdout and stderr to the same file
sudo dnf upgrade -y > /tmp/upgrade.log 2>&1

# Short form (bash 4+)
sudo dnf upgrade -y &> /tmp/upgrade.log
```


[↑ Back to TOC](#toc)

---

## Input redirection

```bash
# Feed a file as input to a command
sort < /etc/passwd
```


[↑ Back to TOC](#toc)

---

## Pipes — `|`

A pipe sends the output of one command as the input to the next.

```bash
# Count lines in a directory listing
ls /etc | wc -l

# Find errors in a log
cat /var/log/messages | grep -i error

# Page through long output
systemctl list-units | less

# Combine multiple pipes
cat /var/log/secure | grep "Failed" | wc -l
```

> **💡 Think of pipes as assembly lines**
> Each command does one small job. Pipes chain them together.
> The UNIX philosophy: do one thing well.
>


[↑ Back to TOC](#toc)

---

## Useful commands for pipes

### `sort`

```bash
# Sort alphabetically
cat /etc/passwd | sort

# Sort by field (delimiter :, field 3 = UID, numeric)
sort -t: -k3 -n /etc/passwd
```

### `uniq`

```bash
# Remove adjacent duplicate lines (usually sort first)
cat /var/log/messages | grep "error" | sort | uniq

# Count occurrences
cat /var/log/messages | grep "error" | sort | uniq -c | sort -rn
```

### `cut`

```bash
# Extract first field (delimiter :)
cut -d: -f1 /etc/passwd

# Extract columns from output
ip addr | grep "inet " | cut -d/ -f1
```

### `awk`

```bash
# Print second column of output
df -h | awk '{print $2}'

# Print lines where field 3 > 1000
awk -F: '$3 >= 1000 {print $1}' /etc/passwd
```

### `tee`

Write to both screen and file simultaneously:

```bash
sudo dnf upgrade -y | tee /tmp/upgrade.log
```


[↑ Back to TOC](#toc)

---

## Here-strings and here-documents

```bash
# Feed a string as stdin
grep "root" <<< "root:x:0:0:root:/root:/bin/bash"

# Feed a multi-line block as stdin (heredoc)
cat <<EOF
Line one
Line two
EOF
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Bash Reference Manual — Redirections](https://www.gnu.org/software/bash/manual/bash.html#Redirections) | Complete redirection syntax including `&>`, `>>`, heredocs |
| [Bash Reference Manual — Pipelines](https://www.gnu.org/software/bash/manual/bash.html#Pipelines) | Pipeline semantics and exit codes |
| [UNIX Power Tools (O'Reilly)](https://www.oreilly.com/library/view/unix-power-tools/0596003307/) | Deep coverage of pipes, filters, and text processing |

---

## Next step

→ [Editing Files](04-editors.md)
---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
