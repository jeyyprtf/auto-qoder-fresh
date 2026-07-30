#!/usr/bin/env python3
"""Qoder Fresh Autoregist + WARP Auto Switch v2"""
import os, subprocess, time

WARP_CLI = "warp-cli"

def warp_switch():
    print("🔄 Switching WARP IP...")
    subprocess.run([WARP_CLI, "connect"], check=True)
    subprocess.run([WARP_CLI, "set", "warp", "on"], check=True)
    print("✅ WARP connected")

def run_qoder(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, timeout=600)

if __name__ == "__main__":
    warp_switch()
    print("🚀 Starting 10 fresh accounts...")
    
    for i in range(1, 11):
        print(f"\n{'='*60}\nAccount #{i}\n{'='*60}")
        
        # Spoof machine
        run_qoder(["qoder-autopilot", "spoof", "--cli-only"])
        
        # Register via browser
        run_qoder(["qoder-autopilot", "-n", "1", "--manual-captcha", "--no-headless", "--format", "json"])
        
        # Claim trial
        run_qoder(["qoder-autopilot", "claim"])
        
        print(f"✅ Account #{i} done")
        
        if i < 10:
            time.sleep(45)
    
    print("\n🎉 All 10 accounts done!")
    print("   Mint PAT at: https://qoder.com/account/integrations")
