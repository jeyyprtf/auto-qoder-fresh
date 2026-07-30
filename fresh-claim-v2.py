#!/usr/bin/env python3
"""Qoder Fresh Autoregist v5 - Register + Claim Pro Trial"""
import subprocess
import time
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
    ok = True
    patches = [
        ("register.py", pkg_dir / "register.py"),
        ("cli.py", pkg_dir / "cli.py"),
        ("otp.py", pkg_dir / "otp.py"),
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
    return ok

def warp_switch():
    print("🔄 Switching WARP IP...")
    try: subprocess.run(["warp-cli", "disconnect"], check=True, capture_output=True, timeout=10)
    except: pass
    try: subprocess.run(["warp-cli", "connect"], check=True, capture_output=True, timeout=30)
    except Exception as e: print(f"⚠️ WARP skip: {e}")
    time.sleep(5)
    print("✅ Ready\n")

if __name__ == "__main__":
    if not patch_package():
        sys.exit(1)

    cfg_path = Path(__file__).parent / "config.json"
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception:
        cfg = {}
    count = cfg.get("account_count", 1)

    warp_switch()
    print(f"🚀 Starting {count} account(s)...\n")

    registered = []
    for i in range(1, count + 1):
        print("="*70)
        print(f"Account #{i} / {count}")
        print("="*70)
        print("(Browser will open — solve captcha + click buttons manually)")
        print()

        try:
            subprocess.run([
                "qoder-autopilot", "-n", "1",
                "--format", "json"
            ], check=True, timeout=900)
            print(f"\n✅ Account #{i} registered\n")
            registered.append(i)

        except subprocess.CalledProcessError:
            print(f"❌ FAILED account {i}\n")
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted")
            break

        if i < count:
            delay = 120
            print(f"⏳ Waiting {delay}s before account {i+1}...")
            time.sleep(delay)
            print()

    print("="*70)
    print("  ✅ REGISTRATION DONE")
    print(f"     {len(registered)} accounts saved to qoder_accounts.json")
    print("="*70)
    print()
    print("  ▶️  Next: python3 claim-stored.py")
    print("     (Claims Pro trial for all stored accounts)")
    print()
    print("  Or do it manually:")
    print("  1. qoder-autopilot claim")
    print("  2. https://qoder.com/account/integrations")
    print()