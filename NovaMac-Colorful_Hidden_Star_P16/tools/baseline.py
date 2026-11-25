#!/usr/bin/env python3
"""Stela ESP baseline: verify, save, restore.

The three files under F:/EFI/stela/ are the only ones whose content can stop
macOS from booting. This script keeps a byte-exact copy of a configuration
that is *known* to reach the desktop, and can prove or restore it in seconds.

  py -3 baseline.py --verify     compare the ESP with the baseline; exit 1 on drift
  py -3 baseline.py --restore    write the baseline config back, then verify
  py -3 baseline.py --restore-efi   put the baseline BOOTX64.EFI back
  py -3 baseline.py --save       adopt the current ESP state as the new baseline
                                 (only after a boot that reached the desktop)

The baseline was captured from boot.log BOOT 23 (22:14:58), which booted
macOS to the desktop with the touchpad working. Do not --save a configuration
that has not itself been seen to boot.
"""
import hashlib
import json
import shutil
import sys

ESP = "F:/EFI/stela/"
EFI = "F:/EFI/BOOT/BOOTX64.EFI"
HERE = "C:/Users/单面本面/WorkBuddy/Claw/.tmp_stela/"
BASE = HERE + "baseline/"
MANIFEST = BASE + "manifest.json"

FILES = ["stela.cfg", "choices.cfg", "setup.json"]


def sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def load_manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(doc):
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")


def verify(quiet=False):
    doc = load_manifest()
    bad = []
    for name in FILES:
        want = doc["files"][name]
        got = sha(ESP + name)
        ok = want == got
        if not ok:
            bad.append(name)
        if not quiet:
            print(f"{'OK  ' if ok else 'DRIFT'} {name:12} {got}")
    efi_want = doc["efi"]["sha256"]
    efi_got = sha(EFI)
    ok = efi_want == efi_got
    if not ok:
        bad.append("BOOTX64.EFI")
    if not quiet:
        print(f"{'OK  ' if ok else 'DRIFT'} {'BOOTX64.EFI':12} {efi_got}")
    return bad


def restore():
    doc = load_manifest()
    for name in FILES:
        shutil.copyfile(BASE + name, ESP + name)
        print(f"restored {name}")
    if sha(EFI) != doc["efi"]["sha256"]:
        print("\n! BOOTX64.EFI does not match the baseline: restore it by hand from")
        print(f"  {doc['efi']['backup']}")
    print()


def save():
    doc = {"note": doc_note(), "files": {}, "efi": {}}
    for name in FILES:
        shutil.copyfile(ESP + name, BASE + name)
        doc["files"][name] = sha(BASE + name)
        print(f"saved {name} {doc['files'][name]}")
    shutil.copyfile(EFI, BASE + "BOOTX64.EFI")
    doc["efi"]["sha256"] = sha(BASE + "BOOTX64.EFI")
    doc["efi"]["backup"] = BASE + "BOOTX64.EFI"
    print(f"saved BOOTX64.EFI {doc['efi']['sha256']}")
    save_manifest(doc)
    print("\nmanifest written")


def restore_efi():
    doc = load_manifest()
    shutil.copyfile(BASE + "BOOTX64.EFI", EFI)
    got = sha(EFI)
    ok = got == doc["efi"]["sha256"]
    print(f"{'OK   ' if ok else 'DRIFT'} BOOTX64.EFI {got}")
    return ok


def doc_note():
    return "Captured from BOOT 23, the last boot seen to reach the macOS desktop."


def main(argv):
    if "--verify" in argv:
        bad = verify()
        print("\ndrift:" if bad else "\nbaseline intact", *bad)
        return 1 if bad else 0
    if "--restore" in argv:
        restore()
        bad = verify()
        print("drift after restore:" if bad else "baseline intact after restore", *bad)
        return 1 if bad else 0
    if "--restore-efi" in argv:
        return 0 if restore_efi() else 1
    if "--save" in argv:
        save()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
