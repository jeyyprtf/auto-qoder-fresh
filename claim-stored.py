#!/usr/bin/env python3
"""Claim Pro trial for all stored accounts (reads from qoder_accounts.json)"""
import subprocess
import sys
import json
from pathlib import Path

def patch_package():
    script_dir = Path(__file__).parent
    try:
        import qoder_autopilot
        pkg_dir = Path(qoder_autopilot.__file__).parent
    except Exception as e:
        print(f"❌ qoder-autopilot not installed: {e}")
        return False
    patches = [
        ("cli.py", pkg_dir / "cli.py"),
        ("cli_login.py", pkg_dir / "auth" / "cli_login.py"),
        ("anti_vm.py", pkg_dir / "infra" / "anti_vm.py"),
        ("machine_spoof.py", pkg_dir / "infra" / "machine_spoof.py"),
    ]
    for src_name, dst_path in patches:
        src = script_dir / src_name
        if not src.exists():
            continue
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.write_bytes(src.read_bytes())
        print(f"✅ Patched {dst_path.relative_to(pkg_dir)}")
    return True

if __name__ == "__main__":
    patch_package()

    accts_file = Path(__file__).parent / "qoder_accounts.json"
    if not accts_file.exists():
        print("❌ qoder_accounts.json not found. Run fresh-claim-v2.py first.")
        sys.exit(1)

    accounts = json.loads(accts_file.read_text())
    if not accounts:
        print("❌ No accounts in qoder_accounts.json")
        sys.exit(1)

    print(f"📋 Found {len(accounts)} accounts in storage")
    print()

    for i, acct in enumerate(accounts, 1):
        email = acct.get("email", "?")
        pat = acct.get("pat", "")
        if pat:
            print(f"  #{i} {email} — already has PAT, skipping")
            continue

        print("="*70)
        print(f"  Account #{i} / {len(accounts)}")
        print(f"  📧 {email}")
        print("="*70)
        print()
        print("  Browser will open for qodercli login.")
        print("  Login with this email to claim Pro trial.")
        print("  Press Ctrl+C after done to skip remaining.")
        print()

        try:
            subprocess.run(["qoder-autopilot", "claim"], check=False, timeout=600)
            print()
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted")
            break

    print("="*70)
    print("  ✅ DONE")
    print("="*70)
    print("  For each claimed account:")
    print("  1. Go to https://qoder.com/account/integrations")
    print("  2. Create PAT")
    print("  3. Add 'pat' field to qoder_accounts.json")
    print()
