# Lab: Shared Team Directory

**Track:** Onramp
**Estimated time:** 20 minutes
**Topology:** Single VM

---

## Prerequisites

- Completed [Users, Groups, Permissions](../permissions.md) and [ACLs](../acls.md)
- ACL tools installed: `sudo dnf install -y acl`
- A fresh VM snapshot taken

---

## Success criteria

By the end of this lab:

- A shared directory `/srv/teamspace` exists where:
  - Members of group `devteam` can create and edit files
  - User `auditor` has read-only access via ACL
  - New files created inside inherit the group and correct permissions (SGID + default ACL)
- You can demonstrate each access level works correctly

---

## Steps

### 1 — Create users and group

```bash
sudo groupadd devteam
sudo useradd -m -G devteam alice
sudo useradd -m -G devteam bob
sudo useradd -m auditor
```

Set passwords for testing:

```bash
echo "alice:Password1!" | sudo chpasswd
echo "bob:Password1!" | sudo chpasswd
echo "auditor:Password1!" | sudo chpasswd
```

!!! success "Verify"
    ```bash
    getent group devteam
    ```
    Look for: `devteam:x:<GID>:alice,bob`

---

### 2 — Create the shared directory

```bash
sudo mkdir -p /srv/teamspace
sudo chown root:devteam /srv/teamspace
sudo chmod 2775 /srv/teamspace
```

The `2` in `2775` sets the **SGID** bit — new files will inherit the `devteam`
group automatically.

!!! success "Verify"
    ```bash
    ls -ld /srv/teamspace
    ```
    Look for: `drwxrwsr-x` and group `devteam`

---

### 3 — Set default ACL for auditor

```bash
# Grant auditor read access to existing directory
sudo setfacl -m u:auditor:r-x /srv/teamspace

# Default ACL: auditor gets read on all new files/dirs inside
sudo setfacl -m d:u:auditor:r-x /srv/teamspace
```

!!! success "Verify"
    ```bash
    getfacl /srv/teamspace
    ```
    Look for lines:
    ```
    user:auditor:r-x
    default:user:auditor:r-x
    ```

---

### 4 — Test alice (devteam member)

```bash
sudo -u alice bash -c "echo 'alice was here' > /srv/teamspace/alice-file.txt"
```

!!! success "Verify"
    ```bash
    ls -l /srv/teamspace/alice-file.txt
    ```
    Look for: group is `devteam` (SGID inherited)

---

### 5 — Test bob (devteam member)

Bob should be able to read and write alice's file because the group `devteam`
has write permission:

```bash
sudo -u bob bash -c "echo 'bob was here' >> /srv/teamspace/alice-file.txt"
sudo -u bob cat /srv/teamspace/alice-file.txt
```

!!! success "Verify"
    Output contains both lines.

---

### 6 — Test auditor (read-only via ACL)

```bash
sudo -u auditor cat /srv/teamspace/alice-file.txt
```

Expected: file contents displayed — auditor can read.

```bash
sudo -u auditor bash -c "echo 'auditor writes' >> /srv/teamspace/alice-file.txt"
```

Expected: `Permission denied` — auditor cannot write.

---

### 7 — Confirm new files inherit the ACL

Create a new file as alice and check its ACLs:

```bash
sudo -u alice bash -c "echo 'new file' > /srv/teamspace/new-file.txt"
getfacl /srv/teamspace/new-file.txt
```

Look for: `user:auditor:r--` inherited from the default ACL.

---

## Cleanup

```bash
sudo rm -rf /srv/teamspace
sudo userdel -r alice
sudo userdel -r bob
sudo userdel -r auditor
sudo groupdel devteam
```

---

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `getent group devteam` shows no members | User not added to group | `sudo usermod -aG devteam alice` |
| New files do not show `devteam` group | SGID bit not set | `chmod g+s /srv/teamspace` |
| auditor can write | ACL mask too permissive | Re-run `setfacl -m u:auditor:r-x` |
| `setfacl: command not found` | acl package missing | `sudo dnf install -y acl` |

---

## Why this matters in production

Shared project directories in development or CI environments need exactly this
pattern: a group-writable directory where all team members can collaborate, new
files inherit the right group (SGID), and read-only audit or monitoring accounts
can inspect content without write access. Getting this wrong leads to permission
errors, files owned by the wrong user, and security gaps.

---

## Next step

→ [Packages and Repos (dnf)](../../03-rhcsa/packages-dnf.md)
