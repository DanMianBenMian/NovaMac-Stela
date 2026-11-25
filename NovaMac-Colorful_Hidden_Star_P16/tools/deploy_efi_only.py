#!/usr/bin/env python3
"""Replace only the ESP's BOOTX64.EFI and keep `setup.json` in step with it.

Nothing else on the ESP is written: `stela.cfg`, `choices.cfg` and the rest of
`setup.json` stay byte-identical, so a boot that goes wrong can only be the
image's doing. `stela_version` is the one field that must move, because Stela
compares it with the hash of the file it actually finds and refuses on a
mismatch.

Undo:  py -3 baseline.py --restore-efi   (config is untouched, so no --restore)
       then set `stela_version` back to the baseline prefix with
       `py -3 baseline.py --restore`

Run:   py -3 deploy_efi_only.py --dry
       py -3 deploy_efi_only.py --apply [path-to-efi]
"""
import hashlib
import json
import sys

HERE = "C:/Users/单面本面/WorkBuddy/Claw/.tmp_stela/"
DEFAULT_NEW = HERE + "new_stela_diag.efi"
ESP_EFI = "F:/EFI/BOOT/BOOTX64.EFI"
SETUP = "F:/EFI/stela/setup.json"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_setup():
    with open(SETUP, "rb") as f:
        data = f.read()
    return data, json.loads(data.decode("utf-8"))


def main(argv):
    source = DEFAULT_NEW
    for word in argv:
        if not word.startswith("--"):
            source = word
    new = sha(source)
    data, doc = load_setup()
    print(f"new EFI      {new}")
    print(f"version      {new[:16]}")
    print(f"ESP EFI      {sha(ESP_EFI)}")
    print(f"stela_version {doc['stela_version']}")

    if "--apply" not in argv:
        print("(dry run)")
        return 0

    with open(source, "rb") as src, open(ESP_EFI, "wb") as dst:
        dst.write(src.read())
    got = sha(ESP_EFI)
    assert got == new, (got, new)
    print("ESP EFI written and verified")

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
    print("  options:", after["options"].strip()[-80:])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
