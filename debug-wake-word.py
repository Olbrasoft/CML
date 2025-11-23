#!/usr/bin/env python3
"""
Debug version of CML Voice-to-OpenCode
Shows what's happening with wake word detection
"""

import sys
import os
sys.path.insert(0, os.path.expanduser('~/oc/openwakeword-models'))

from wake_word_detector import CMLWakeWordDetector
import pyaudio
import numpy as np
import time

def main():
    print("🔍 CML Wake Word Detector - DEBUG MODE")
    print("="*60)
    print("Listening for 'cé em el' with detailed output...")
    print("Press Ctrl+C to stop\n")
    
    detector = None
    pa = None
    audio_stream = None
    
    try:
        # Initialize detector
        print("⏳ Loading Czech model...")
        detector = CMLWakeWordDetector()
        print("✅ Model loaded!\n")
        
        # IMPORTANT: Increase threshold to reduce false positives
        detector.THRESHOLD = 0.7  # Higher = stricter (was 0.5)
        print(f"🎚️  Detection threshold set to: {detector.THRESHOLD}\n")
        
        # Initialize PyAudio
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=16000
        )
        
        print("✅ Listening started...\n")
        print("Audio Level | Detection Score | Status")
        print("-" * 50)
        
        # Main loop
        chunk_count = 0
        while True:
            # Read audio chunk
            audio_data = audio_stream.read(16000, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # Normalize
            audio_array = audio_array / 32768.0
            
            # Calculate audio level
            audio_level = np.abs(audio_array).max()
            
            # Detect
            detected, score = detector.detect(audio=audio_array)
            
            chunk_count += 1
            status = "🔔 DETECTED!" if detected else "         "
            
            # Show every chunk for debugging
            print(f"{audio_level:8.4f}  |  {score:8.4f}      | {status}")
            
            if detected:
                print("\n" + "="*50)
                print(f"✅ WAKE WORD DETECTED!")
                print(f"   Confidence: {score:.4f}")
                print(f"   Audio level: {audio_level:.4f}")
                print("="*50 + "\n")
                time.sleep(2)  # Wait 2 seconds before listening again
                
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
