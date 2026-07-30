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
    for f in ["register.py", "cli.py", "otp.py"]:
        src = script_dir / f
        if not src.exists():
            continue
        dst = pkg_dir / f
        if dst.exists():
            dst.write_bytes(src.read_bytes())
            print(f"✅ Patched {dst.name}")
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
    print(f"🚀 Starting {count} account(s) + claim Pro trial...\n")
    
    accounts = []
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
            accounts.append(i)
            
        except subprocess.CalledProcessError:
            print(f"❌ FAILED account {i}\n")
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            break
        
        if i < count:
            delay = 120
            print(f"⏳ Waiting {delay}s before account {i+1}...")
            time.sleep(delay)
            print()
    
    print("="*70)
    print("  ✅ REGISTRATION DONE")
    print(f"     {len(accounts)} accounts registered")
    print("="*70)
    
    # ── Claim Pro Trial ──
    print("\n" + "="*70)
    print("  🎯 CLAIM PRO TRIAL (300 credits)")
    print("="*70)
    print()
    print("  Running qodercli login to claim trial...")
    print("  (Browser will open or a URL will be printed)")
    print("  Login with your registered email+password")
    print()
    
    try:
        subprocess.run([
            "qoder-autopilot", "claim"
        ], check=False, timeout=600)
        print("\n✅ Claim done!\n")
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted\n")
    
    print("="*70)
    print("  NEXT STEPS:")
    print("  1. Go to: https://qoder.com/account/integrations")
    print("  2. Create a Personal Access Token (PAT)")
    print("  3. Use: export QODER_PERSONAL_ACCESS_TOKEN=<pat>")
    print("="*70)
    print()