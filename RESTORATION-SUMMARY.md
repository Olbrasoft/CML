# CML Voice System Restoration - November 23, 2025

## Problem Found
After attempting to integrate a custom Czech PyTorch wake word model, the system had indentation errors in the main loop that prevented it from running.

## Root Cause
The backup file (`cml-voice-to-opencode.py.backup-1763915449`) contained incomplete code:
- Lines 349-358: Had inline transcription code with wrong indentation
- Missing: Text extraction, file cleanup, sending to OpenCode, stream reopening

## Solution Applied
Replaced the broken inline transcription code with proper function calls:
- Uses existing `transcribe_with_whisper()` function
- Properly handles audio file cleanup
- Correctly sends text to OpenCode
- Reopens audio stream for next wake word

## Fixed Code Structure (lines 346-372)
```python
# Record command
audio_file = record_command_with_pyaudio(porcupine, pa)

if audio_file:
    # Transcribe
    text = transcribe_with_whisper(audio_file)
    
    # Cleanup audio file
    if os.path.exists(audio_file):
        os.remove(audio_file)
    
    # Send to OpenCode
    if text:
        send_to_opencode(text)
    else:
        logging.warning("⚠️  No text to send")
else:
    logging.error("❌ Recording failed")

# Reopen stream for wake word detection
audio_stream = pa.open(
    rate=16000,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

logging.info("🎤 Ready for next wake word...\n")
```

## Verification
✅ Python syntax check passed
✅ All dependencies verified (pvporcupine, pyaudio, faster_whisper)
✅ Porcupine model file exists: `~/oc/porcupine-models/C-M-L_en_linux_v3_0_0.ppn`
✅ System starts successfully: "✅ System ready, listening for wake word..."

## Current Status
**SYSTEM RESTORED** - Using original English "C M L" wake word with Porcupine

## Files Status
- `cml-voice-to-opencode.py` - ✅ **WORKING** (Porcupine with fixes)
- `cml-voice-to-opencode.py.backup-1763915449` - ❌ Had indentation bug
- `cml-voice-to-opencode.py.pytorch-backup` - ⚠️  PyTorch version (false positives)
- `cml-wake-listener-openwakeword.py` - ⚠️  Uses PyTorch model

## Next Steps (Optional)
If you want Czech wake word in the future:
1. Collect 30+ hours of Czech negative audio samples (speech, noise, silence)
2. Retrain model with proper 1:30 positive:negative ratio
3. Use data from Czech Common Voice, podcasts, home recordings
4. Estimated time: ~1 week for proper training

## Lesson Learned
Wake word detection requires massive amounts of **negative training data** (what it's NOT) to avoid false positives. Synthetic-only training doesn't work for real-world deployment.
