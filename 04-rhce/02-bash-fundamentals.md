
[↑ Back to TOC](#toc)

# Bash Scripting Fundamentals
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Bash scripts let you automate repetitive tasks. This chapter teaches safe,
readable, idempotent patterns — not just "how to write Bash", but how to
write Bash that won't surprise you at 2 AM.

Ansible handles most configuration management, but Bash remains essential in
the RHCE track for tasks that happen *before* Ansible is available (bootstrap
scripts), tasks that are too simple to warrant a playbook (log rotation
one-liners), and tasks that integrate with system facilities Ansible cannot
easily reach (cron jobs, login scripts, init snippets). Understanding Bash
also makes you a better Ansible author: you recognise when a `shell` task is
the wrong tool, and you write better `command` arguments because you
understand exactly what the shell does with them.

The discipline gap in most Bash scripts is error handling. A script that runs
`cp /important/file /backup/ && rm /important/file` with no error check will
silently delete the source if the copy destination is full. `set -euo pipefail`
closes that gap in one line. Combined with a structured logging function and
explicit exit codes, your scripts become as auditable as a playbook.

This chapter is positioned second in the RHCE track deliberately. Before
Ansible, you need enough Bash fluency to write idempotent bootstrap scripts,
parse command output, and build helper tools. The patterns here appear
directly inside Ansible `shell` and `command` tasks, in `pre_tasks`, and in
the `validate` parameters of file modules.

---
<a name="toc"></a>

## Table of contents

- [Script template (always start with this)](#script-template-always-start-with-this)
- [Variables](#variables)
- [Conditionals](#conditionals)
- [Loops](#loops)
- [Functions](#functions)
- [Input validation](#input-validation)
- [Command substitution](#command-substitution)
- [Exit codes](#exit-codes)
- [Idempotent patterns](#idempotent-patterns)
- [Logging output](#logging-output)
- [Worked example](#worked-example)
- [Common mistakes and how to diagnose them](#common-mistakes-and-how-to-diagnose-them)


## Script template (always start with this)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Script: describe-what-it-does.sh
# Usage:  sudo ./describe-what-it-does.sh [args]
# Notes:  Any important context

main() {
  # your logic here
  echo "Done."
}

main "$@"
```

| Header line | Why |
|---|---|
| `#!/usr/bin/env bash` | Portable shebang; finds bash in PATH |
| `set -e` | Exit immediately on error |
| `set -u` | Error on unset variable (catches typos) |
| `set -o pipefail` | Catch failures in pipe chains |


[↑ Back to TOC](#toc)

---

## Variables

```bash
NAME="rhel10-lab"
PORT=8080
LOG_FILE="/var/log/myapp.log"

# Use double quotes around variables (prevent word splitting)
echo "Hostname is: ${NAME}"
echo "Port: ${PORT}"

# Default value if variable is unset
LOG_DIR="${LOG_DIR:-/var/log}"

# Readonly
readonly CONFIG_FILE="/etc/myapp/config"
```


[↑ Back to TOC](#toc)

---

## Conditionals

```bash
# if / elif / else
if [[ -f /etc/myapp.conf ]]; then
  echo "Config exists"
elif [[ -d /etc/myapp ]]; then
  echo "Directory exists, no config"
else
  echo "Neither found"
fi

# Test flags
[[ -f file ]]    # file exists and is a regular file
[[ -d dir ]]     # directory exists
[[ -z "$VAR" ]]  # variable is empty
[[ -n "$VAR" ]]  # variable is non-empty
[[ "$A" == "$B" ]]  # string equality
[[ $N -gt 10 ]]     # numeric greater than
```


[↑ Back to TOC](#toc)

---

## Loops

```bash
# for loop over a list
for HOST in web01 web02 web03; do
  echo "Processing: ${HOST}"
done

# for loop with range
for I in {1..5}; do
  echo "Step ${I}"
done

# while loop
COUNT=0
while [[ $COUNT -lt 5 ]]; do
  echo "Count: ${COUNT}"
  (( COUNT++ ))
done

# Loop over lines of a file
while IFS= read -r line; do
  echo "Line: ${line}"
done < /etc/hosts
```


[↑ Back to TOC](#toc)

---

## Functions

```bash
log() {
  local level="$1"
  local message="$2"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] ${message}"
}

die() {
  log "ERROR" "$1"
  exit 1
}

check_root() {
  if [[ $EUID -ne 0 ]]; then
    die "This script must be run as root (use sudo)"
  fi
}
```


[↑ Back to TOC](#toc)

---

## Input validation

```bash
usage() {
  echo "Usage: $0 <username> <group>"
  exit 1
}

# Check argument count
if [[ $# -ne 2 ]]; then
  usage
fi

USERNAME="$1"
GROUP="$2"

# Validate input
if ! id "${USERNAME}" &>/dev/null; then
  die "User '${USERNAME}' does not exist"
fi
```


[↑ Back to TOC](#toc)

---

## Command substitution

```bash
# Capture command output into a variable
OS_VERSION=$(rpm -q --queryformat '%{VERSION}' redhat-release)
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')

echo "RHEL version: ${OS_VERSION}"
echo "Root disk usage: ${DISK_USAGE}"
```


[↑ Back to TOC](#toc)

---

## Exit codes

```bash
# Exit code 0 = success, non-zero = failure
if ping -c 1 8.8.8.8 &>/dev/null; then
  echo "Network OK"
else
  echo "Network unreachable"
  exit 1
fi

# Check exit code of last command
systemctl is-active sshd
if [[ $? -ne 0 ]]; then
  echo "sshd is not running!"
fi

# Shorthand
systemctl is-active sshd || echo "sshd is not running!"
```


[↑ Back to TOC](#toc)

---

## Idempotent patterns

```bash
# Create directory only if it doesn't exist
[[ -d /etc/myapp ]] || sudo mkdir -p /etc/myapp

# Add a line only if not already present
grep -qxF "ServerName rhel10-lab" /etc/httpd/conf/httpd.conf || \
  echo "ServerName rhel10-lab" | sudo tee -a /etc/httpd/conf/httpd.conf

# Install a package only if not installed
rpm -q vim &>/dev/null || sudo dnf install -y vim
```


[↑ Back to TOC](#toc)

---

## Logging output

```bash
LOGFILE="/var/log/myscript.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOGFILE}"
}

log "INFO" "Script started"
```


[↑ Back to TOC](#toc)

---

## Worked example

### Backup script: log rotation, free-space check, alert on failure

This script demonstrates the full set of patterns from this chapter in a
realistic operations context. It rotates application logs, checks free space
before and after, and sends a syslog alert if anything goes wrong.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Script: rotate-applogs.sh
# Usage:  sudo ./rotate-applogs.sh
# Notes:  Run via cron at 02:00 daily.
#         Requires: /etc/rotate-applogs.conf for APP_LOG_DIR

readonly CONFIG_FILE="/etc/rotate-applogs.conf"
readonly LOGFILE="/var/log/rotate-applogs.log"
readonly MIN_FREE_MB=500
readonly KEEP_DAYS=30

# ── Logging ──────────────────────────────────────────────────────────────────

log() {
  local level="$1"; shift
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] $*"
  echo "${msg}" | tee -a "${LOGFILE}"
}

die() {
  log "ERROR" "$1"
  logger -t rotate-applogs -p user.err "FAILED: $1"
  exit 1
}

# ── Checks ───────────────────────────────────────────────────────────────────

check_root() {
  [[ $EUID -eq 0 ]] || die "Must run as root (sudo $0)"
}

load_config() {
  [[ -f "${CONFIG_FILE}" ]] || die "Config not found: ${CONFIG_FILE}"
  # shellcheck source=/dev/null
  source "${CONFIG_FILE}"
  [[ -n "${APP_LOG_DIR:-}" ]] || die "APP_LOG_DIR not set in ${CONFIG_FILE}"
}

check_free_space() {
  local dir="$1"
  local free_mb
  free_mb=$(df -BM "${dir}" | awk 'NR==2 {gsub(/M/,"",$4); print $4}')
  if [[ ${free_mb} -lt ${MIN_FREE_MB} ]]; then
    die "Insufficient free space on ${dir}: ${free_mb}MB (minimum: ${MIN_FREE_MB}MB)"
  fi
  log "INFO" "Free space on ${dir}: ${free_mb}MB — OK"
}

# ── Rotation ─────────────────────────────────────────────────────────────────

rotate_logs() {
  local log_dir="$1"
  [[ -d "${log_dir}" ]] || die "Log directory not found: ${log_dir}"

  log "INFO" "Starting rotation in ${log_dir}"

  local count=0
  while IFS= read -r -d '' logfile; do
    local archive="${logfile}.$(date '+%Y%m%d').gz"
    if [[ -f "${archive}" ]]; then
      log "INFO" "Already archived today: ${logfile} — skipping"
      continue
    fi
    gzip -c "${logfile}" > "${archive}" || die "Failed to compress ${logfile}"
    truncate -s 0 "${logfile}"
    log "INFO" "Rotated: ${logfile} → ${archive}"
    (( count++ ))
  done < <(find "${log_dir}" -maxdepth 1 -name "*.log" -size +0c -print0)

  log "INFO" "Rotation complete: ${count} file(s) rotated"
}

purge_old_archives() {
  local log_dir="$1"
  local purged=0
  while IFS= read -r -d '' archive; do
    rm -f "${archive}"
    log "INFO" "Purged old archive: ${archive}"
    (( purged++ ))
  done < <(find "${log_dir}" -name "*.log.*.gz" -mtime "+${KEEP_DAYS}" -print0)
  log "INFO" "Purge complete: ${purged} archive(s) removed"
}

# ── Main ─────────────────────────────────────────────────────────────────────

main() {
  check_root
  load_config

  log "INFO" "=== rotate-applogs.sh started ==="

  check_free_space "${APP_LOG_DIR}"
  rotate_logs       "${APP_LOG_DIR}"
  purge_old_archives "${APP_LOG_DIR}"
  check_free_space "${APP_LOG_DIR}"   # confirm space freed

  log "INFO" "=== rotate-applogs.sh finished successfully ==="
}

main "$@"
```

Key patterns demonstrated:

| Pattern | Where used |
|---|---|
| `set -euo pipefail` | Top of script — fail-safe execution |
| `readonly` variables | Config paths, thresholds |
| `log()` / `die()` functions | Consistent output with timestamps |
| `check_root()` | Guard clause before privileged operations |
| `load_config` + `source` | Externally configurable without editing the script |
| `check_free_space()` | Pre- and post-condition checks |
| Idempotent file check (`[[ -f "${archive}" ]]`) | Skip work already done |
| `find -print0` + `read -r -d ''` | Safe loop over filenames with spaces |
| `logger` | Write alerts to syslog (survives log rotation of its own file) |

> **Exam tip:** In the RHCE exam, any Bash task that modifies system state
> should include a guard clause (`[[ -f ]] ||`, `rpm -q || ...`) to make it
> safe to re-run. Examiners run playbooks and scripts multiple times to verify
> idempotence.

[↑ Back to TOC](#toc)

---

## Common mistakes and how to diagnose them

| Mistake | Symptom | Fix |
|---|---|---|
| Missing `set -euo pipefail` | Script continues after a failed step; silently corrupts state | Add to every script's shebang block without exception |
| Unquoted variables | `rm -rf $DIR` deletes `/` when `DIR` is empty (with `-f`) | Always use `"${VAR}"` — double quotes prevent word splitting |
| Using `==` inside `[ ]` (single bracket) | Syntax error on older bash; unpredictable on POSIX sh | Use `[[ ]]` (double brackets) for all conditionals in bash scripts |
| `$?` checked too late | Another command runs between the one you want to check and the `if [[ $? ]]` | Use `if command; then` directly, or capture to a variable immediately |
| Relative paths in scripts | Script fails when run from a different directory | Use `readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` and build all paths from it |
| `echo` used for structured logging | No timestamp; output lost when running non-interactively (cron) | Use a `log()` function that writes to both stdout and a logfile with `tee` |

[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html) | Authoritative reference for all Bash syntax and builtins |
| [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) | Industry-standard conventions for readable shell scripts |
| [ShellCheck](https://www.shellcheck.net/) | Online linter that catches common Bash mistakes |
| [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) | Deep reference; useful once fundamentals are solid |

---


[↑ Back to TOC](#toc)

## Next step

→ [Ansible Setup and Inventory](03-ansible-setup-inventory.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
