# CML Voice System - Performance Improvements

## 🐛 Problem Found

**Symptom**: "Překládání trvá dlouho"
**Real cause**: Recording waits too long for silence detection

## 📊 Before Optimization

```
Timeline (from 20:09:39 to 20:10:12):
├─ Wake word detected:        0.0s
├─ Recording started:          1.6s  (confirmation "Ano?")
├─ Recording finished:        30.5s  ⚠️ 28.8s of recording!
├─ Whisper model loaded:      31.9s  (1.4s load time)
├─ Transcription done:        32.7s  (0.8s transcribe)
└─ Sent to OpenCode:          33.3s  (0.6s send)

TOTAL: 33.3 seconds
```

**Problem**: 
- Recorded 28.8s of audio
- Only 6.3s was actual speech (22.5s was silence/noise)
- Silence detection too sensitive (threshold=500, wait=2s)

## ✅ After Optimization

**Changes**:
1. `silence_threshold`: 500 → 800 (better noise rejection)
2. `max_silence_chunks`: 30 → 25 (stop after 1.7s silence instead of 2s)
3. Added debug logging for amplitude monitoring

**Expected improvement**:
```
Timeline (estimated):
├─ Wake word detected:        0.0s
├─ Recording started:          1.6s
├─ Recording finished:         9.0s  ✅ ~7.4s of recording
├─ Whisper model loaded:      10.4s  (1.4s load)
├─ Transcription done:        11.2s  (0.8s transcribe)
└─ Sent to OpenCode:          11.8s

TOTAL: ~12 seconds (vs 33 seconds before)
```

**Improvement**: ~21 seconds faster (63% reduction)

## 🧪 Testing

Test the improvements:
1. Start CML: `~/cml/start-cml-voice.sh`
2. Say "CML" wake word
3. After "Ano?", speak a command
4. Check timing in logs

Expected behavior:
- Recording should stop ~1.7s after you finish speaking
- Total time should be under 15 seconds for typical commands

## 🎛️ Fine-tuning

If still too slow/fast, adjust in `cml-voice-to-opencode.py`:

**Line 143**: `silence_threshold`
- Lower (500-700): More sensitive, stops quicker (but may cut off speech)
- Higher (900-1200): Less sensitive, waits longer (better for noisy environments)

**Line 145**: `max_silence_chunks`
- Lower (20): Stops after ~1.3s of silence
- Higher (30): Waits ~2s of silence
