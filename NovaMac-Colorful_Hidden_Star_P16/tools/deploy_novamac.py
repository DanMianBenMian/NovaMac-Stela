#!/usr/bin/env python3
"""Deploy the NovaMac EFI with a verified backup and a one-command rollback.

    py -3 deploy_novamac.py --dry
    py -3 deploy_novamac.py --apply [path-to-new-efi]

Rollback (restores both the EFI and its version field):
    py -3 deploy_novamac.py --rollback                       # one step back
    py -3 deploy_novamac.py --rollback BOOTX64.pre-novamac-20261125-172557
"""
import datetime
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_NEW = os.path.join(HERE, "novamac.efi")
ESP_EFI = "F:/EFI/BOOT/BOOTX64.EFI"
SETUP = "F:/EFI/stela/setup.json"
BACKUP_DIR = os.path.join(HERE, "efi_backup")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_setup():
    with open(SETUP, "rb") as f:
        data = f.read()
    return data, json.loads(data.decode("utf-8"))


def main(argv):
    if "--rollback" in argv:
        backups = sorted(
            name for name in os.listdir(BACKUP_DIR)
            if name.startswith("BOOTX64.pre-novamac-") and not name.endswith(".version")
        )
        if not backups:
            raise SystemExit("no NovaMac backup found")
        chosen = [word for word in argv if not word.startswith("--")]
        # Default: the most recent backup, i.e. one step back. Pass an
        # explicit file name to go further back (e.g. to the original Stela).
        latest = chosen[0] if chosen else backups[-1]
        if latest not in backups:
            raise SystemExit(f"unknown backup {latest}; available: {', '.join(backups)}")
        fields = os.path.join(BACKUP_DIR, latest + ".version")
        with open(fields, "r", encoding="utf-8") as f:
            version = f.read().strip()
        efi = os.path.join(BACKUP_DIR, latest)
        print(f"rollback EFI  {efi} sha256={sha(efi)}")
        print(f"rollback version {version}")
        if "--apply" not in argv and "--force" not in argv:
            print("(dry run; pass --force to roll back)")
            return 0
        shutil.copy2(efi, ESP_EFI)
        data, doc = load_setup()
        old = doc["stela_version"]
        data = data.replace(old.encode(), version.encode(), 1)
        with open(SETUP, "wb") as f:
            f.write(data)
        _, after = load_setup()
        assert sha(ESP_EFI) == sha(efi)
        assert after["stela_version"] == version, after["stela_version"]
        print("rolled back and verified")
        return 0

    source = DEFAULT_NEW
    for word in argv:
        if not word.startswith("--"):
            source = word
    new = sha(source)
    data, doc = load_setup()
    print(f"new EFI       {source} sha256={new}")
    print(f"version       {new[:16]}")
    print(f"ESP EFI       {sha(ESP_EFI)}")
    print(f"stela_version {doc['stela_version']}")
    print("options unchanged:", doc["options"].strip()[-80:])

    if "--apply" not in argv:
        print("(dry run)")
        return 0

    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = os.path.join(BACKUP_DIR, f"BOOTX64.pre-novamac-{stamp}")
    shutil.copy2(ESP_EFI, backup)
    assert sha(backup) == sha(ESP_EFI), "backup verification failed"
    with open(backup + ".version", "w", encoding="utf-8") as f:
        f.write(doc["stela_version"])
    print(f"backup        {backup}")

    with open(source, "rb") as src, open(ESP_EFI, "wb") as dst:
        dst.write(src.read())
    assert sha(ESP_EFI) == new, "EFI verification failed"

    old = doc["stela_version"]
    if old.encode() not in data:
        raise SystemExit(f"stela_version {old} not found as written")
    data = data.replace(old.encode(), new[:16].encode(), 1)
    with open(SETUP, "wb") as f:
        f.write(data)
    _, after = load_setup()
    assert after["stela_version"] == new[:16], after["stela_version"]
    assert after["options"] == doc["options"], "options changed unexpectedly"
    print(f"stela_version {old} -> {after['stela_version']}")
    print("deployed and verified; reboot into the boot menu when ready")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
