#!/bin/bash
# Format Samsung HD501LJ (/dev/sdb by-id) as LUKS+ext4 for Nextcloud AIO datadir.
# NEVER touches ST1000 system disk.
set -u

DISK_BYID=/dev/disk/by-id/ata-SAMSUNG_HD501LJ_S0VVJ1PP402262
ST1000_BYID=/dev/disk/by-id/ata-ST1000DM003-1ER162_Z4Y0CBCQ
DISK=$(readlink -f "$DISK_BYID")
ST1000=$(readlink -f "$ST1000_BYID")
ROOT_SRC=$(findmnt -no SOURCE /)

MOUNTPOINT=/mnt/nextcloud-data
KEYDIR=/data/.secrets
KEYFILE=$KEYDIR/nextcloud-data.key
MAPPER=nextcloud_data
LABEL=nextcloud-data

echo "DISK_BYID=$DISK_BYID"
echo "DISK=$DISK"
echo "ST1000=$ST1000"
echo "ROOT_SRC=$ROOT_SRC"

if [ -z "$DISK" ] || [ "$DISK" = "$ST1000" ]; then
  echo "FATAL: Samsung path invalid or equals system disk"
  exit 2
fi
if [ "$DISK" != "/dev/sdb" ]; then
  echo "FATAL: expected Samsung at /dev/sdb, got $DISK"
  exit 2
fi
case "$ROOT_SRC" in
  *sdb*) echo "FATAL: root is on sdb"; exit 2 ;;
esac

# If already provisioned and mounted, exit success
if mountpoint -q "$MOUNTPOINT" 2>/dev/null && [ -b "/dev/mapper/$MAPPER" ]; then
  echo "Already mounted: $MOUNTPOINT"
  df -hT "$MOUNTPOINT"
  exit 0
fi

if findmnt "$DISK" >/dev/null 2>&1 || findmnt "${DISK}1" >/dev/null 2>&1 || findmnt "${DISK}2" >/dev/null 2>&1; then
  echo "Unmounting Samsung partitions if mounted..."
  sudo umount "${DISK}1" 2>/dev/null || true
  sudo umount "${DISK}2" 2>/dev/null || true
fi

echo "=== Ensuring /data mounted for key storage ==="
sudo mkdir -p /data
if ! mountpoint -q /data; then
  sudo cryptsetup status data_crypt >/dev/null 2>&1 || \
    sudo cryptsetup luksOpen UUID=ef1318f4-372f-4547-9748-ab07080fc484 data_crypt
  sudo mount /dev/mapper/data_crypt /data || sudo mount -a
fi
mountpoint -q /data || { echo "FATAL: cannot mount /data for keyfile"; exit 3; }
df -h /data | tail -1

echo "=== Creating keyfile (no secret echoed) ==="
sudo mkdir -p "$KEYDIR"
sudo chmod 700 "$KEYDIR"
if [ ! -f "$KEYFILE" ]; then
  sudo dd if=/dev/urandom of="$KEYFILE" bs=64 count=1 status=none
  sudo chmod 600 "$KEYFILE"
  sudo chown root:root "$KEYFILE"
  echo "keyfile: created"
else
  echo "keyfile: reused existing"
fi

# If LUKS already present on sdb1, open+mount instead of reformatting
EXISTING_TYPE=$(sudo blkid -s TYPE -o value "${DISK}1" 2>/dev/null || true)
if [ "$EXISTING_TYPE" = "crypto_LUKS" ]; then
  echo "=== Existing LUKS on ${DISK}1 — open and mount ==="
  if [ ! -b "/dev/mapper/$MAPPER" ]; then
    sudo cryptsetup luksOpen --key-file "$KEYFILE" "${DISK}1" "$MAPPER"
  fi
  sudo mkdir -p "$MOUNTPOINT"
  sudo mount "/dev/mapper/$MAPPER" "$MOUNTPOINT"
  df -hT "$MOUNTPOINT"
  exit 0
fi

echo "=== Wipe partition table and signatures on Samsung only ==="
sudo wipefs -a "$DISK"
# Clear GPT/MBR backup too
sudo sgdisk --zap-all "$DISK" 2>/dev/null || true
sudo dd if=/dev/zero of="$DISK" bs=1M count=8 status=none
sudo partprobe "$DISK" || true
sleep 1

echo "=== Create single GPT partition ==="
sudo parted -s "$DISK" mklabel gpt
sudo parted -s "$DISK" mkpart primary 1MiB 100%
sudo parted -s "$DISK" name 1 nextcloud-data
sudo parted -s "$DISK" print
sudo partprobe "$DISK"
sleep 2

PART="${DISK}1"
if [ ! -b "$PART" ]; then
  PART=$(lsblk -nrpo NAME,TYPE "$DISK" | awk '$2=="part"{print $1; exit}')
fi
echo "PART=$PART"
[ -b "$PART" ] || { echo "FATAL: partition missing"; exit 4; }

echo "=== LUKS format + open ==="
sudo cryptsetup luksFormat --type luks2 --batch-mode --key-file "$KEYFILE" "$PART"
sudo cryptsetup luksOpen --key-file "$KEYFILE" "$PART" "$MAPPER"
sudo cryptsetup status "$MAPPER"

echo "=== ext4 filesystem ==="
sudo mkfs.ext4 -L "$LABEL" "/dev/mapper/$MAPPER"
sudo mkdir -p "$MOUNTPOINT"
sudo mount "/dev/mapper/$MAPPER" "$MOUNTPOINT"
sudo chmod 755 "$MOUNTPOINT"
df -hT "$MOUNTPOINT" | tail -1

PART_UUID=$(sudo blkid -s UUID -o value "$PART")
FS_UUID=$(sudo blkid -s UUID -o value "/dev/mapper/$MAPPER")
echo "PART_UUID=$PART_UUID"
echo "FS_UUID=$FS_UUID"

echo "=== Persist crypttab + fstab (idempotent) ==="
if ! grep -q "^${MAPPER} " /etc/crypttab 2>/dev/null; then
  echo "${MAPPER} UUID=${PART_UUID} ${KEYFILE} luks,nofail" | sudo tee -a /etc/crypttab >/dev/null
  echo "crypttab: added"
else
  echo "crypttab: entry exists"
fi
if ! grep -q "mapper/${MAPPER}" /etc/fstab 2>/dev/null && ! grep -q "${MOUNTPOINT}" /etc/fstab 2>/dev/null; then
  echo "/dev/mapper/${MAPPER} ${MOUNTPOINT} ext4 defaults,nofail,x-systemd.device-timeout=10s 0 2" | sudo tee -a /etc/fstab >/dev/null
  echo "fstab: added"
else
  echo "fstab: entry exists"
fi

echo "=== Validate ==="
sudo findmnt "$MOUNTPOINT"
sudo lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT "$DISK"
grep -E "nextcloud|data_crypt|mapper" /etc/crypttab /etc/fstab || true
echo "nextcloud-data ready $(date -u +%Y-%m-%dT%H:%M:%SZ)" | sudo tee "$MOUNTPOINT/README-SOLARSEED.txt" >/dev/null

echo "=== SUCCESS ==="
df -hT / "$MOUNTPOINT" /data 2>/dev/null
