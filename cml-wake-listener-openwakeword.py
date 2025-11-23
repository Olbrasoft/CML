#!/usr/bin/env python3
"""
CML Wake Word Listener using PyTorch Czech Model
Listens for Czech "cé em el" wake word and triggers voice system
"""

import sys
import os
sys.path.insert(0, os.path.expanduser('~/oc/openwakeword-models'))

from wake_word_detector import CMLWakeWordDetector
import pyaudio
import numpy as np
import subprocess

def show_notification(title, message):
    """Show desktop notification"""
    try:
        subprocess.run([
            'notify-send',
            '-u', 'critical',
            '-t', '3000',
            title,
            message
        ])
    except Exception as e:
        print(f"Failed to show notification: {e}")

def trigger_voice_system():
    """Trigger the CML voice-to-opencode system"""
    try:
        subprocess.Popen(['python3', '/home/jirka/CML/cml-voice-to-opencode.py'])
        print("✅ CML voice system triggered!")
    except Exception as e:
        print(f"⚠️ Could not trigger voice system: {e}")

def main():
    print("🎧 CML Wake Word Listener (Czech - PyTorch Model)")
    print("🎤 Listening for 'cé em el'...")
    print("Press Ctrl+C to stop\n")
    
    detector = None
    pa = None
    audio_stream = None
    
    try:
        # Initialize detector
        print("⏳ Loading Czech model...")
        detector = CMLWakeWordDetector()
        detector.THRESHOLD = 0.85  # Zvýšený práh
        print("✅ Model loaded!")
        print(f"🎚️  Detection threshold: {detector.THRESHOLD}\n")
        
        # Setup audio stream (16kHz mono)
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=16000  # 1 second chunks
        )
        
        print("✅ Listening started...\n")
        
        # Main listening loop
        detection_count = 0
        cooldown = 0  # Simple cooldown to avoid multiple detections
        
        while True:
            # Read audio chunk (1 second = 16000 frames at 16kHz)
            audio_data = audio_stream.read(16000, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # Normalize audio to [-1, 1]
            audio_array = audio_array / 32768.0
            
            # Detect wake word
            detected, score = detector.detect(audio=audio_array)
            
            # Apply cooldown
            if cooldown > 0:
                cooldown -= 1
                detected = False
            
            if detected:
                detection_count += 1
                print(f"🔔 WAKE WORD DETECTED #{detection_count}: cé em el (confidence: {score:.4f})")
                show_notification("Wake Word Detected!", "Triggers Czech CML voice system...")
                trigger_voice_system()
                cooldown = 5  # 5 second cooldown before next detection
                
    except KeyboardInterrupt:
        print("\n👋 Stopping listener...")
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
