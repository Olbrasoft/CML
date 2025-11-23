#!/usr/bin/env python3
"""
Simple Audio Detection using Cross-Correlation
Detects 1976.wav sound in microphone input
"""

import numpy as np
import speech_recognition as sr
from scipy import signal
from scipy.io import wavfile
import sys

# Load reference audio (1976.wav)
REFERENCE_FILE = "/home/jirka/cml/1976.wav"

def load_reference_audio():
    """Load and prepare the reference audio."""
    rate, data = wavfile.read(REFERENCE_FILE)
    
    # Convert to float and normalize
    if data.dtype == np.uint8:
        data = data.astype(np.float32) - 128
    else:
        data = data.astype(np.float32)
    
    data = data / np.abs(data).max()
    return rate, data

def detect_sound_in_audio(audio_data, sample_rate, reference_data, ref_rate):
    """
    Detect reference sound in audio using cross-correlation.
    Returns correlation score (0.0 to 1.0)
    """
    # Resample if needed
    if sample_rate != ref_rate:
        # Simple resampling
        ratio = ref_rate / sample_rate
        new_length = int(len(audio_data) * ratio)
        audio_data = signal.resample(audio_data, new_length)
        sample_rate = ref_rate
    
    # Convert audio to float and normalize
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32768.0
    elif audio_data.dtype == np.uint8:
        audio_data = audio_data.astype(np.float32) - 128
        audio_data = audio_data / 128.0
    
    # Perform cross-correlation
    correlation = signal.correlate(audio_data, reference_data, mode='valid')
    
    # Normalize correlation
    correlation = correlation / (np.sqrt(np.sum(audio_data**2)) * np.sqrt(np.sum(reference_data**2)))
    
    # Get maximum correlation value
    max_corr = np.abs(correlation).max() if len(correlation) > 0 else 0.0
    
    return max_corr

def listen_for_sound(threshold=0.3, timeout=10):
    """
    Listen for the reference sound.
    Returns True if detected, False if timeout.
    """
    ref_rate, ref_data = load_reference_audio()
    
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print(f"🎧 Listening for sound... (threshold: {threshold})")
    
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=3)
        
        # Get raw audio data
        audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
        sample_rate = audio.sample_rate
        
        # Detect sound
        score = detect_sound_in_audio(audio_data, sample_rate, ref_data, ref_rate)
        
        print(f"📊 Correlation score: {score:.3f}")
        
        if score >= threshold:
            print("✅ Sound detected!")
            return True
        else:
            print("❌ Sound not detected")
            return False
            
    except sr.WaitTimeoutError:
        print("⏰ Timeout - no audio detected")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test mode
    result = listen_for_sound(threshold=0.25, timeout=10)
    sys.exit(0 if result else 1)
