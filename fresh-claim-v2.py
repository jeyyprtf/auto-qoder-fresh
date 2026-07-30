#!/usr/bin/env python3
"""Qoder Fresh Autoregist v3 - Simple & Robust"""
import subprocess
import time

def warp_switch():
    print("🔄 Switching WARP IP...")
    try: subprocess.run(["warp-cli", "disconnect"], check=True, capture_output=True)
    except: pass
    try: subprocess.run(["warp-cli", "connect"], check=True, capture_output=True)
    except Exception as e: print(f"⚠️ WARP skip: {e}")
    time.sleep(5)
    print("✅ Ready\n")

if __name__ == "__main__":
    warp_switch()
    print("🚀 Starting 10 fresh accounts...\n")
    
    for i in range(1, 11):
        print("="*70)
        print(f"Account #{i} / 10")
        print("="*70)
        
        try:
            # Register via browser
            subprocess.run([
                "qoder-autopilot", "-n", "1",
                "--format", "json"
            ], check=True, timeout=600)
            
            # Claim trial  
            subprocess.run(["qoder-autopilot", "claim"], check=True, timeout=600)
            
            print(f"\n✅ Account #{i} SUCCESS\n")
            
        except subprocess.CalledProcessError:
            print(f"❌ FAILED account {i}\n")
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            break
        
        if i < 10:
            delay = 45
            print(f"⏳ Waiting {delay}s before account {i+1}...")
            time.sleep(delay)
            print()
    
    print("="*70)
    print("  ✅ COMPLETED")
    print("="*70)
    print("  Total attempts: 10")
    print("  Save your PATs at: https://qoder.com/account/integrations\n")