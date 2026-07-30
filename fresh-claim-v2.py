#!/usr/bin/env python3
"""Qoder Fresh Autoregist v4 - Slow & Patient"""
import subprocess
import time
import sys
from pathlib import Path

def patch_register_py():
    """Replace installed register.py with our fixed version."""
    script_dir = Path(__file__).parent
    patch_file = script_dir / "register.py"
    if not patch_file.exists():
        print("⚠️ register.py patch not found, skipping")
        return True
    try:
        import qoder_autopilot
        pkg_dir = Path(qoder_autopilot.__file__).parent
        target = pkg_dir / "register.py"
        target.write_bytes(patch_file.read_bytes())
        print(f"✅ Patched {target}")
        return True
    except Exception as e:
        print(f"❌ Patch failed: {e}")
        return False

def warp_switch():
    print("🔄 Switching WARP IP...")
    try: subprocess.run(["warp-cli", "disconnect"], check=True, capture_output=True)
    except: pass
    try: subprocess.run(["warp-cli", "connect"], check=True, capture_output=True)
    except Exception as e: print(f"⚠️ WARP skip: {e}")
    time.sleep(5)
    print("✅ Ready\n")

if __name__ == "__main__":
    if not patch_register_py():
        sys.exit(1)
    warp_switch()
    print("🚀 Starting 5 fresh accounts (slow mode)...\n")
    
    for i in range(1, 6):
        print("="*70)
        print(f"Account #{i} / 5")
        print("="*70)
        print("(Browser will open - solve captcha manually)")
        print()
        
        try:
            # Register via browser - only register, no claim command
            subprocess.run([
                "qoder-autopilot", "-n", "1",
                "--format", "json"
            ], check=True, timeout=900)
            
            print(f"\n✅ Account #{i} registration done\n")
            
        except subprocess.CalledProcessError:
            print(f"❌ FAILED account {i}\n")
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            break
        
        if i < 5:
            delay = 120  # 2 minutes between accounts
            print(f"⏳ Waiting {delay}s before account {i+1}...")
            print("   (This gives time to collect PAT if needed)")
            time.sleep(delay)
            print()
    
    print("="*70)
    print("  ✅ COMPLETED")
    print("="*70)
    print("  Collect PATs at: https://qoder.com/account/integrations")
    print("  Each account needs a PAT created manually.\n")