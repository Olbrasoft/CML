#!/usr/bin/env python3
"""
CML Wake Word Listener using Porcupine
Listens for "C M L" wake word and shows notification
"""

import pvporcupine
import pyaudio
import struct
import subprocess
import os

# Paths
KEYWORD_PATH = "/home/jirka/oc/porcupine-models/C-M-L_en_linux_v3_0_0.ppn"
ACCESS_KEY = "3yFshBAX2ELWaAic9Z7qSgHfE4ZTYvXjuooTntO+4m8HoyAZFE6cMQ=="

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

def main():
    print("🎧 CML Wake Word Listener")
    print(f"📁 Model: {KEYWORD_PATH}")
    print("🎤 Listening for 'C M L'...")
    print("Press Ctrl+C to stop\n")
    
    # Create Porcupine instance
    porcupine = None
    pa = None
    audio_stream = None
    
    try:
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH]
        )
        
        # Setup audio stream
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print("✅ Listening started...\n")
        
        # Main listening loop
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                print("🔔 WAKE WORD DETECTED: C M L")
                show_notification("Wake Word Detected!", "C M L heard!")
                
    except KeyboardInterrupt:
        print("\n👋 Stopping listener...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()

if __name__ == "__main__":
    main()
