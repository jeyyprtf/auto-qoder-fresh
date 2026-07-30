#!/usr/bin/env python3
"""Qoder Fresh Autoregist v2 - Manual captcha mode, robust error handling"""
import subprocess
import time
import os
from pathlib import Path
from datetime import datetime

def warp_switch():
    """Switch WARP IP for new identity"""
    print("🔄 Switching WARP IP...")
    try:
        subprocess.run(["warp-cli", "disconnect"], check=True, capture_output=True, timeout=10)
    except Exception as e:
        print(f"⚠️  Disconnect skip: {e}")
    
    try:
        subprocess.run(["warp-cli", "connect"], check=True, capture_output=True, timeout=30)
        print("✅ WARP connected\n")
    except Exception as e:
        print(f"⚠️  Connect failed (may already connected): {e}\n")
    
    time.sleep(5)

def run_qoder(cmd, desc=""):
    """Run qoder command with timeout and error handling"""
    if desc:
        print(f"   📦 Running: {desc}")
    
    result = subprocess.run(
        cmd, 
        check=False, 
        timeout=600, 
        capture_output=True, 
        text=True,
        env=os.environ.copy()
    )
    
    # Print last 20 lines of output if any
    if result.stdout or result.stderr:
        output = result.stdout + result.stderr
        lines = output.split('\n')[-20:]
        for line in lines:
            if line.strip():
                print(f"      {line[:120]}")
    
    return result.returncode == 0, output

def detect_pat(output):
    """Detect PAT from output"""
    import re
    match = re.search(r'pt-[a-zA-Z0-9_-]+', output)
    return match.group(0) if match else None

if __name__ == "__main__":
    print("="*70)
    print("  QODER FRESH AUTO-REGIST v2")
    print("  Auto register + manual captcha + claim trial")
    print("="*70)
    print()
    
    warp_switch()
    print("🚀 Starting 10 fresh accounts...\n")
    
    success_count = 0
    pat_list = []
    
    for i in range(1, 11):
        print("="*70)
        print(f"  Account #{i} / 10")
        print("="*70)
        
        try:
            # Step 1: Register via browser (manual captcha - MOST RELIABLE)
            print("\n[STEP 1/2] Register account...")
            success, output = run_qoder([
                "qoder-autopilot", "-n", "1", 
                "--manual-captcha",
                "--format", "json"
            ], "Register account")
            
            if not success:
                print(f"❌ Registration failed for account {i}")
                continue
            
            # Check for PAT hint in output
            pat = detect_pat(output)
            if pat:
                pat_list.append(pat)
                print(f"💾 Detected PAT: {pat[:40]}...")
            
            # Step 2: Claim trial
            print("\n[STEP 2/2] Claim trial...")
            success2, output2 = run_qoder(
                ["qoder-autopilot", "claim"],
                "Claim trial"
            )
            
            if success2:
                print(f"\n✅ Account #{i} SUCCESS\n")
                success_count += 1
                
                # Detect PAT after claim too
                pat2 = detect_pat(output2)
                if pat2 and pat2 not in pat_list:
                    pat_list.append(pat2)
                    
            else:
                print(f"❌ Trial claim failed for account {i}")
                print(output2[-500:] if len(output2) > 500 else output2)
                
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT for account {i}")
            continue
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            break
        
        # Delay between accounts (except last one)
        if i < 10:
            delay = 45
            print(f"⏳ Waiting {delay}s before account {i+1}...")
            time.sleep(delay)
            print()
    
    # Final summary
    print("\n" + "="*70)
    print("  ✅ COMPLETED")
    print("="*70)
    print(f"  Total attempts: 10")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {10 - success_count}")
    
    if pat_list:
        print(f"\n💾 PATs collected: {len(pat_list)}")
        print("  Save them at: https://qoder.com/account/integrations")
        for p in pat_list[:5]:
            print(f"    • {p[:40]}...")
    else:
        print("\n💡 No PATs detected yet")
        print("  Manually collect at: https://qoder.com/account/integrations")
    
    print()
