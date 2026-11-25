#!/usr/bin/env python3
"""Deploy the rebuilt EFI and turn the guest network on, in the one order that
leaves the ESP consistent.

  1. the new BOOTX64.EFI goes to F:/EFI/BOOT/
  2. the config is written from the frozen baseline plus the two network words
  3. `stela_version` is set to the new EFI's sha256 prefix, which Stela
     compares against the file it actually finds

Undo:  py -3 baseline.py --restore ; py -3 baseline.py --restore-efi

Run:   py -3 deploy_net.py --dry
       py -3 deploy_net.py --apply
"""
import hashlib
import json
import subprocess
import sys

HERE = "C:/Users/单面本面/WorkBuddy/Claw/.tmp_stela/"
NEW_EFI = HERE + "new_stela_net.efi"
ESP_EFI = "F:/EFI/BOOT/BOOTX64.EFI"
SETUP = "F:/EFI/stela/setup.json"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(*args):
    out = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    sys.stdout.write(out.stdout)
    if out.returncode != 0:
        sys.stderr.write(out.stderr)
        raise SystemExit(f"{args[0]} failed")


def main(argv):
    new = sha(NEW_EFI)
    print(f"new EFI   {new}")
    print(f"version   {new[:16]}")
    print(f"ESP EFI   {sha(ESP_EFI)}")

    if "--apply" not in argv:
        print("(dry run)")
        return 0

    # 1. the EFI
    with open(NEW_EFI, "rb") as src, open(ESP_EFI, "wb") as dst:
        dst.write(src.read())
    got = sha(ESP_EFI)
    assert got == new, (got, new)
    print("ESP EFI written and verified")

    # 2. the config
    run(HERE + "enable_guest_net.py", "--apply")

    # 3. stela_version, which the second step reset to the baseline's EFI
    with open(SETUP, "rb") as f:
        data = f.read()
    doc = json.loads(data.decode("utf-8"))
    old = doc["stela_version"]
    if old.encode() not in data:
        raise SystemExit(f"stela_version {old} not found as written")
    data = data.replace(old.encode(), new[:16].encode(), 1)
    with open(SETUP, "wb") as f:
        f.write(data)
    doc = json.loads(data.decode("utf-8"))
    assert doc["stela_version"] == new[:16], doc["stela_version"]
    print(f"stela_version {old} -> {doc['stela_version']}")

    print("\nfinal")
    print("  options:", doc["options"].strip()[-95:])
    print("  wifi_prompt:", doc["wifi_prompt"])
    print("  volume/bundle:", doc["volume"], doc["bundle_directory"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
