# Command Cheatsheets

Quick-reference cards for the most-used command groups. Each section is designed to fit on a single screen.

---

## dnf — Package Management

```bash
# Search and info
dnf search <keyword>
dnf info <package>
dnf provides <file>               # Which package owns a file?
dnf repoquery --list <package>    # List files in a package

# Install / Remove
sudo dnf install -y <package>
sudo dnf remove <package>
sudo dnf reinstall <package>
sudo dnf autoremove               # Remove unneeded dependencies

# Updates
sudo dnf check-update
sudo dnf upgrade -y
sudo dnf upgrade-minimal          # Security patches only

# History and rollback
dnf history list
dnf history info <id>
sudo dnf history undo <id>

# Repositories
dnf repolist
dnf repolist --all
sudo dnf config-manager --enable <repo-id>
sudo dnf config-manager --disable <repo-id>
```

---

## systemctl — Service Management

```bash
# Status and control
systemctl status <unit>
sudo systemctl start <unit>
sudo systemctl stop <unit>
sudo systemctl restart <unit>
sudo systemctl reload <unit>      # Reload config without restart

# Enable / Disable at boot
sudo systemctl enable <unit>
sudo systemctl disable <unit>
sudo systemctl enable --now <unit>   # Enable AND start

# Inspect
systemctl list-units --failed
systemctl list-unit-files --state=enabled
systemctl show <unit>             # All unit properties
systemctl cat <unit>              # Show unit file
sudo systemctl edit <unit>        # Edit drop-in override

# Targets
systemctl get-default
sudo systemctl set-default multi-user.target
sudo systemctl isolate rescue.target

# User services (rootless)
systemctl --user status <unit>
systemctl --user start <unit>
systemctl --user enable <unit>
systemctl --user daemon-reload
```

---

## journalctl — Log Inspection

```bash
# Basic queries
journalctl -u <unit>              # Logs for a service
journalctl -u <unit> -f           # Follow (tail -f equivalent)
journalctl -u <unit> -n 50        # Last 50 lines
journalctl -p err                 # Errors and above
journalctl -p err..warning        # Range of priorities
journalctl -k                     # Kernel messages only
journalctl -b                     # Current boot
journalctl -b -1                  # Previous boot

# Time filtering
journalctl --since "1 hour ago"
journalctl --since "2026-02-01" --until "2026-02-02"
journalctl --since today

# Output formats
journalctl -o json-pretty -u sshd -n 5
journalctl --no-pager > /tmp/journal.txt

# Disk usage and cleanup
journalctl --disk-usage
sudo journalctl --vacuum-size=500M
sudo journalctl --vacuum-time=30d
```

---

## nmcli — Network Management

```bash
# Status
nmcli device status
nmcli connection show
nmcli connection show <name>

# Create a static IPv4 connection
sudo nmcli connection add \
  con-name <name> type ethernet ifname <nic> \
  ipv4.method manual \
  ipv4.addresses 192.168.1.10/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8 1.1.1.1" \
  connection.autoconnect yes

# Modify existing connection
sudo nmcli connection modify <name> ipv4.dns "8.8.8.8"

# Activate / deactivate
sudo nmcli connection up <name>
sudo nmcli connection down <name>
sudo nmcli connection reload

# Delete
sudo nmcli connection delete <name>
```

---

## firewall-cmd — Firewall Management

```bash
# Status
sudo firewall-cmd --state
sudo firewall-cmd --list-all
sudo firewall-cmd --get-active-zones

# Ports
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --remove-port=8080/tcp --permanent
sudo firewall-cmd --list-ports

# Services
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --remove-service=http --permanent
sudo firewall-cmd --list-services

# Apply permanent changes
sudo firewall-cmd --reload

# Rich rules
sudo firewall-cmd --add-rich-rule='rule family=ipv4 source address=10.0.0.0/8 accept' --permanent

# Temporary (testing, no --permanent)
sudo firewall-cmd --add-port=9090/tcp
sudo firewall-cmd --remove-port=9090/tcp
```

---

## SELinux

```bash
# Status
getenforce
sestatus

# Toggle mode
sudo setenforce 1          # enforcing
sudo setenforce 0          # permissive (temporary ONLY — diagnostic use)

# File contexts
ls -Z <path>
ps -Z
id -Z

# Restore default context
sudo restorecon -Rv <path>

# Manage fcontext rules (persistent)
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/web(/.*)?'
sudo restorecon -Rv /srv/web

# Port labels
sudo semanage port -l | grep http
sudo semanage port -a -t http_port_t -p tcp 8080
sudo semanage port -d -t http_port_t -p tcp 8080

# Booleans
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on

# AVC denials
sudo ausearch -m avc -ts recent
sudo audit2why < /var/log/audit/audit.log
sudo audit2allow -a          # REVIEW before applying
```

---

## LVM

```bash
# Inspect
pvs / vgs / lvs
pvdisplay / vgdisplay / lvdisplay
lsblk

# Create
sudo pvcreate /dev/vdb
sudo vgcreate datavg /dev/vdb
sudo lvcreate -L 5G -n datalv datavg

# Filesystem + mount
sudo mkfs.xfs /dev/datavg/datalv
sudo mkdir /data
echo '/dev/datavg/datalv /data xfs defaults 0 0' | sudo tee -a /etc/fstab
sudo mount -a

# Extend (online, XFS)
sudo lvextend -r -L +2G /dev/datavg/datalv   # -r resizes FS too
# Or explicitly:
sudo lvextend -L +2G /dev/datavg/datalv
sudo xfs_growfs /data

# Snapshots
sudo lvcreate -s -n snap1 -L 1G /dev/datavg/datalv
sudo lvremove /dev/datavg/snap1
```

---

## Podman

```bash
# Images
podman pull docker.io/library/nginx:stable-alpine
podman images
podman rmi <image>
podman image prune -a

# Run
podman run -d --name web -p 8080:80 nginx:stable-alpine
podman run -it --rm alpine sh          # interactive, auto-remove

# Container lifecycle
podman ps
podman ps -a                           # including stopped
podman stop <name>
podman start <name>
podman restart <name>
podman rm <name>

# Inspect and logs
podman logs -f <name>
podman inspect <name>
podman exec -it <name> /bin/sh

# Secrets
printf 'mypassword' | podman secret create db-pass -
podman secret ls
podman secret rm db-pass

# Volumes
podman volume create mydata
podman run -v mydata:/data:Z alpine
podman volume ls
podman volume rm mydata

# Build
podman build -t myapp:latest .
```

---

## Quadlet (systemd container integration)

```bash
# Files location
# User (rootless): ~/.config/containers/systemd/
# Root:            /etc/containers/systemd/

# Minimal .container file
cat > ~/.config/containers/systemd/myapp.container <<'EOF'
[Unit]
Description=My app

[Container]
Image=docker.io/library/nginx:stable-alpine
PublishPort=8080:80
Volume=%h/data:/data:Z

[Service]
Restart=always

[Install]
WantedBy=default.target
EOF

# Reload and manage
systemctl --user daemon-reload
systemctl --user start myapp
systemctl --user enable myapp
systemctl --user status myapp
journalctl --user -u myapp -f
```

---

## SSH

```bash
# Connect
ssh user@host
ssh -p 2222 user@host
ssh -i ~/.ssh/mykey user@host

# Key management
ssh-keygen -t ed25519 -C "label"
ssh-copy-id user@host
ssh-add ~/.ssh/mykey

# Config shortcut (~/.ssh/config)
Host lab
  HostName 192.168.122.10
  User student
  IdentityFile ~/.ssh/id_ed25519

# File transfer
scp localfile user@host:/remote/path
scp user@host:/remote/file .
rsync -avz localdir/ user@host:/remote/

# Tunnels
ssh -L 8080:localhost:80 user@host    # local forward
ssh -R 9090:localhost:9090 user@host  # remote forward

# Server management
sudo sshd -t                           # syntax check (ALWAYS before restart)
sudo systemctl restart sshd
```

---

## Performance Triage Quick Reference

```bash
# Load and CPU
uptime
top -b -n 1 | head -20
ps aux --sort=-%cpu | head -11
mpstat -P ALL 1 3
vmstat 1 5

# Memory
free -m
vmstat 1 5 | awk 'NR>2 {print "si:",$7,"so:",$8}'

# Disk I/O
iostat -x 1 3
sudo iotop -o -b -n 3
df -h && df -i

# Network
ip -s link show ens3
ss -s
ss -tlnp
netstat -s | grep -i retran

# Processes
ps aux | awk '$8=="D"'     # uninterruptible sleep (I/O stuck)
lsof | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
```

---

## tuned Quick Reference

```bash
tuned-adm list
tuned-adm active
sudo tuned-adm profile throughput-performance
sudo tuned-adm recommend
tuned-adm profile_info <name>

# Custom profile
sudo mkdir /etc/tuned/myprofile
sudo tee /etc/tuned/myprofile/tuned.conf <<'EOF'
[main]
include=throughput-performance

[sysctl]
net.core.somaxconn=131072
EOF
sudo tuned-adm profile myprofile
```

---

## Next step

→ [Further Reading](further-reading.md)
