#!/bin/bash
# CML Voice-to-OpenCode Launcher
# Starts the CML wake word listener + voice recognition system

cd ~/cml

echo "🎧 Starting CML Voice-to-OpenCode..."
echo "📝 Say 'C M L' (cé em el) to activate"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Setup GPU library paths (same as dictation-start.sh)
export LD_LIBRARY_PATH="$HOME/.local/lib/python3.13/site-packages/nvidia/cudnn/lib:$HOME/.local/lib/python3.13/site-packages/nvidia/cublas/lib:$HOME/.local/lib/python3.13/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"

# Run the system
python3 cml-voice-to-opencode.py
