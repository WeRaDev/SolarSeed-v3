#!/bin/bash
# Wipe ST1000 partition sda3 (Data1 NTFS) only. Create LUKS2+ext4 City bulk at /data-bulk.
# NEVER touches sda7 (root), sda8 (swap), sda9 (existing /data LUKS), or Samsung sdb.
set -euo pipefail

ST1000_BYID=/dev/disk/by-id/ata-ST1000DM003-1ER162_Z4Y0CBCQ
SAMSUNG_BYID=/dev/disk/by-id/ata-SAMSUNG_HD501LJ_S0VVJ1PP402262
DISK=$(readlink -f "$ST1000_BYID")
SAMSUNG=$(readlink -f "$SAMSUNG_BYID")
PART="${DISK}3"
ROOT_SRC=$(findmnt -no SOURCE /)

MOUNTPOINT=/data-bulk
KEYDIR=/data/.secrets
KEYFILE=$KEYDIR/data-bulk.key
MAPPER=data_bulk
LABEL=city-bulk

echo "DISK=$DISK PART=$PART ROOT_SRC=$ROOT_SRC SAMSUNG=$SAMSUNG"

if [ "$DISK" != "/dev/sda" ]; then
  echo "FATAL: expected ST1000 at /dev/sda, got $DISK"; exit 2
fi
if [ "$PART" = "$ROOT_SRC" ] || [ "$PART" = "/dev/sda7" ]; then
  echo "FATAL: refusing to wipe root"; exit 2
fi
if [ "$PART" = "/dev/sda9" ] || [ "$PART" = "/dev/sda8" ]; then
  echo "FATAL: refusing to wipe swap or existing city LUKS"; exit 2
fi
case "$PART" in
  "$SAMSUNG"*) echo "FATAL: target on Samsung disk"; exit 2 ;;
esac

# Verify label/size sanity if blkid works
FSTYPE=$(blkid -s TYPE -o value "$PART" 2>/dev/null || true)
LABEL_CUR=$(blkid -s LABEL -o value "$PART" 2>/dev/null || true)
echo "current PART fstype=$FSTYPE label=$LABEL_CUR"
if [ -n "$FSTYPE" ] && [ "$FSTYPE" != "ntfs" ] && [ "$FSTYPE" != "crypto_LUKS" ]; then
  echo "FATAL: unexpected fstype $FSTYPE on $PART"; exit 2
fi
if [ "$FSTYPE" = "ntfs" ] && [ -n "$LABEL_CUR" ] && [ "$LABEL_CUR" != "Data1" ]; then
  echo "FATAL: expected NTFS label Data1, got $LABEL_CUR"; exit 2
fi

if mountpoint -q "$MOUNTPOINT" 2>/dev/null && [ -b "/dev/mapper/$MAPPER" ]; then
  echo "Already mounted: $MOUNTPOINT"
  df -hT "$MOUNTPOINT"
  exit 0
fi

if findmnt "$PART" >/dev/null 2>&1; then
  echo "Unmounting $PART"
  umount "$PART" || true
fi

echo "=== Ensure /data mounted for key storage ==="
mkdir -p /data
if ! mountpoint -q /data; then
  cryptsetup status data_crypt >/dev/null 2>&1 || \
    cryptsetup luksOpen UUID=ef1318f4-372f-4547-9748-ab07080fc484 data_crypt
  mount /dev/mapper/data_crypt /data || mount -a
fi
mountpoint -q /data || { echo "FATAL: /data not mounted"; exit 3; }

echo "=== Keyfile ==="
mkdir -p "$KEYDIR"
chmod 700 "$KEYDIR"
if [ ! -f "$KEYFILE" ]; then
  dd if=/dev/urandom of="$KEYFILE" bs=64 count=1 status=none
  chmod 600 "$KEYFILE"
  chown root:root "$KEYFILE"
  echo "keyfile: created"
else
  echo "keyfile: reused"
fi

EXISTING_TYPE=$(blkid -s TYPE -o value "$PART" 2>/dev/null || true)
if [ "$EXISTING_TYPE" = "crypto_LUKS" ]; then
  echo "=== Existing LUKS on $PART — open+mount ==="
  if [ ! -b "/dev/mapper/$MAPPER" ]; then
    cryptsetup luksOpen --key-file "$KEYFILE" "$PART" "$MAPPER"
  fi
  mkdir -p "$MOUNTPOINT"
  mount "/dev/mapper/$MAPPER" "$MOUNTPOINT"
  df -hT "$MOUNTPOINT"
  exit 0
fi

echo "=== Wipe signatures on $PART only (not whole disk) ==="
wipefs -a "$PART"
# clear start of partition
dd if=/dev/zero of="$PART" bs=1M count=16 status=none
partprobe "$DISK" || true
sleep 1

echo "=== LUKS format + open ==="
cryptsetup luksFormat --type luks2 --batch-mode --key-file "$KEYFILE" "$PART"
cryptsetup luksOpen --key-file "$KEYFILE" "$PART" "$MAPPER"
cryptsetup status "$MAPPER"

echo "=== ext4 ==="
mkfs.ext4 -L "$LABEL" "/dev/mapper/$MAPPER"
mkdir -p "$MOUNTPOINT"
mount "/dev/mapper/$MAPPER" "$MOUNTPOINT"
chmod 755 "$MOUNTPOINT"
# City layout placeholders
mkdir -p "$MOUNTPOINT"/{docker,backups,prometheus,models,containers}
chown root:root "$MOUNTPOINT"
df -hT "$MOUNTPOINT" | tail -1

PART_UUID=$(blkid -s UUID -o value "$PART")
FS_UUID=$(blkid -s UUID -o value "/dev/mapper/$MAPPER")
echo "PART_UUID=$PART_UUID FS_UUID=$FS_UUID"

if ! grep -q "^${MAPPER} " /etc/crypttab 2>/dev/null; then
  echo "${MAPPER} UUID=${PART_UUID} ${KEYFILE} luks,nofail" >> /etc/crypttab
  echo "crypttab: added"
else
  echo "crypttab: exists"
fi
if ! grep -q "mapper/${MAPPER}" /etc/fstab 2>/dev/null && ! grep -q "${MOUNTPOINT}" /etc/fstab 2>/dev/null; then
  echo "/dev/mapper/${MAPPER} ${MOUNTPOINT} ext4 defaults,nofail,x-systemd.device-timeout=10s 0 2" >> /etc/fstab
  echo "fstab: added"
else
  echo "fstab: exists"
fi

findmnt "$MOUNTPOINT"
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT "$PART"
grep -E "data_bulk|data_crypt|nextcloud" /etc/crypttab /etc/fstab || true
echo "city-bulk ready $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$MOUNTPOINT/README-SOLARSEED.txt"
ls -la "$MOUNTPOINT"
echo "=== SUCCESS ==="
df -hT / "$MOUNTPOINT" /data 2>/dev/null
# prove root and sda9 untouched
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT /dev/sda7 /dev/sda8 /dev/sda9
