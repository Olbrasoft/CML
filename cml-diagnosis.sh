#!/bin/bash
# CML Voice System Diagnostic Report

echo "🔍 CML Voice System Diagnostic Report"
echo "======================================"
echo ""

# 1. Check if CML is running
echo "📊 1. Process Status"
echo "-------------------"
CML_PID=$(pgrep -f "cml-voice-to-opencode.py")
if [ -n "$CML_PID" ]; then
    echo "✅ CML is RUNNING (PID: $CML_PID)"
    ps -p $CML_PID -o pid,ppid,cmd,etime,cputime
else
    echo "❌ CML is NOT running"
fi
echo ""

# 2. Check Whisper model cache
echo "📊 2. Whisper Model Cache"
echo "-------------------------"
WHISPER_DIR=~/.cache/huggingface/hub/models--Systran--faster-whisper-medium
if [ -d "$WHISPER_DIR" ]; then
    SIZE=$(du -sh "$WHISPER_DIR" | cut -f1)
    echo "✅ Medium model cached: $SIZE"
else
    echo "❌ Medium model NOT cached (will download on first use)"
fi
echo ""

# 3. Check lock files
echo "📊 3. Lock Files"
echo "----------------"
if [ -f /tmp/microphone-active.lock ]; then
    LOCK_PID=$(cat /tmp/microphone-active.lock)
    echo "⚠️  microphone-active.lock EXISTS (PID: $LOCK_PID)"
    if ps -p $LOCK_PID > /dev/null 2>&1; then
        echo "   Process is ALIVE"
    else
        echo "   Process is DEAD (stale lock!)"
    fi
else
    echo "✅ No microphone lock"
fi
echo ""

# 4. Check OpenCode window
echo "📊 4. OpenCode Window"
echo "---------------------"
if [ -f ~/.opencode-window-id ]; then
    WINDOW_ID=$(cat ~/.opencode-window-id)
    echo "✅ Window ID: $WINDOW_ID"
else
    echo "❌ No OpenCode window ID found"
fi
echo ""

# 5. Test Whisper loading
echo "📊 5. Whisper Load Test"
echo "-----------------------"
echo "Testing model load time..."
export LD_LIBRARY_PATH="$HOME/.local/lib/python3.13/site-packages/nvidia/cudnn/lib:$HOME/.local/lib/python3.13/site-packages/nvidia/cublas/lib:$HOME/.local/lib/python3.13/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"

time python3 << 'PYEOF' 2>&1 | grep -E "(Model loaded|real|user)"
import os
cudnn_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cudnn/lib')
cublas_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cublas/lib')
cuda_runtime_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cuda_runtime/lib')
os.environ['LD_LIBRARY_PATH'] = f"{cudnn_path}:{cublas_path}:{cuda_runtime_path}:"
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cuda', compute_type='float16')
print("Model loaded!")
PYEOF

echo ""
echo "======================================"
echo "✅ Diagnosis complete!"
