#!/bin/bash
echo "🔍 CML Timing Test"
echo "==================="
echo ""
echo "📊 Testing Whisper load time..."
time python3 << 'PYEOF'
import os
cudnn_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cudnn/lib')
cublas_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cublas/lib')
cuda_runtime_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cuda_runtime/lib')
os.environ['LD_LIBRARY_PATH'] = f"{cudnn_path}:{cublas_path}:{cuda_runtime_path}:"

from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cuda', compute_type='float16')
print("✅ Model loaded!")
PYEOF

echo ""
echo "✅ Test complete!"
