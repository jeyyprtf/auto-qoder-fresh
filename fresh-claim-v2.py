#!/usr/bin/env python3
"""Qoder Fresh Autoregist v2 - Manual captcha mode, auto-config skip"""
import subprocess, time, os

def warp_switch():
    print("🔄 Switching WARP IP...")
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True, capture_output=True)
    except: pass
    try:
        subprocess.run(["warp-cli", "connect"], check=True, capture_output=True)
    except Exception as e:
        print(f"⚠️ WARP skip: {e}")
    time.sleep(5)
    print("✅ Ready\n")

def run_qoder(cmd):
    # Run with environment to skip interactive prompts
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    result = subprocess.run(
        cmd, 
        check=True, 
        timeout=600, 
        capture_output=True, 
        text=True,
        env=env
    )
    return result.stdout + result.stderr

if __name__ == "__main__":
    warp_switch()
    print("🚀 Starting 10 fresh accounts...\n")
    
    for i in range(1, 11):
        print("="*60)
        print(f"Account #{i}")
        print("="*60)
        
        try:
            # Spoof machine
            out = run_qoder(["qoder-autopilot", "-n", "1", "--dry-run"])
            print(out[-200:] if len(out) > 200 else out)
            
            # Register via browser (manual captcha - MOST RELIABLE)
            out = run_qoder([
                "qoder-autopilot", "-n", "1", 
                "--manual-captcha", 
                "--no-headless",
                "--quiet",
                "--format", "json"
            ])
            print(out[-500:] if len(out) > 500 else out)
            
            # Claim trial  
            out = run_qoder(["qoder-autopilot", "claim"])
            print(out[-500:] if len(out) > 500 else out)
            
            print(f"\n✅ Account #{i} DONE\n")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR account {i}: {e}")
            print(e.stderr[-200:] if e.stderr else "")
            continue
        
        if i < 10:
            print(f"⏳ Delay 45s before account {i+1}...")
            time.sleep(45)
    
    print("🎉 ALL ACCOUNTS DONE!")
    print("Save your PATs from: https://qoder.com/account/integrations\n")
