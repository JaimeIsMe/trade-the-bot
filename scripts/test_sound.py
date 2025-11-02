"""
Test script to play trading sounds
"""
import winsound
import time

print("\n" + "="*60)
print("  TESTING TRADING SOUNDS")
print("="*60 + "\n")

print("Testing BUY/LONG sound (high pitch)...")
print("Playing in 2 seconds...")
time.sleep(2)

try:
    # High pitch for BUY/LONG
    winsound.Beep(1000, 500)  # 1000 Hz for 500ms
    print("[OK] BUY/LONG sound played!")
except Exception as e:
    print(f"[ERROR] Could not play sound: {e}")

print("\nWaiting 2 seconds...\n")
time.sleep(2)

print("Testing SELL/SHORT sound (low pitch)...")
print("Playing in 2 seconds...")
time.sleep(2)

try:
    # Low pitch for SELL/SHORT
    winsound.Beep(500, 500)  # 500 Hz for 500ms
    print("[OK] SELL/SHORT sound played!")
except Exception as e:
    print(f"[ERROR] Could not play sound: {e}")

print("\n" + "="*60)
print("  SOUND TEST COMPLETE")
print("="*60)
print("\nDid you hear both beeps?")
print("  - First beep: HIGH pitch (1000 Hz) - for BUY/LONG")
print("  - Second beep: LOW pitch (500 Hz) - for SELL/SHORT")
print("\nIf you didn't hear anything:")
print("  1. Check your system volume")
print("  2. Make sure speakers/headphones are connected")
print("  3. Try running: winsound.Beep(800, 1000) in Python")
print("="*60 + "\n")

