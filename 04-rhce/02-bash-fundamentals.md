# Bash Scripting Fundamentals

Bash scripts let you automate repetitive tasks. This chapter teaches safe,
readable, idempotent patterns — not just "how to write Bash", but how to
write Bash that won't surprise you at 2 AM.

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

## Further reading

| Resource | Notes |
|---|---|
| [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html) | Authoritative reference for all Bash syntax and builtins |
| [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) | Industry-standard conventions for readable shell scripts |
| [ShellCheck](https://www.shellcheck.net/) | Online linter that catches common Bash mistakes |
| [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) | Deep reference; useful once fundamentals are solid |

---

## Next step

→ [Ansible Setup and Inventory](03-ansible-setup-inventory.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
