#!/usr/bin/env python3
"""
Test and compare Whisper models (medium vs large)
"""

import os
import sys
import time
import logging

# Setup CUDNN library path for GPU support BEFORE importing WhisperModel
cudnn_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cudnn/lib')
cublas_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cublas/lib')
cuda_runtime_path = os.path.expanduser('~/.local/lib/python3.13/site-packages/nvidia/cuda_runtime/lib')
if os.path.exists(cudnn_path):
    os.environ['LD_LIBRARY_PATH'] = f"{cudnn_path}:{cublas_path}:{cuda_runtime_path}:" + os.environ.get('LD_LIBRARY_PATH', '')

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("ERROR: faster-whisper not installed!")
    print("Run: pip3 install faster-whisper")
    sys.exit(1)

# Configuration
AUDIO_FILE = "/home/jirka/cml/test-recording.wav"
LANGUAGE = "cs"  # Czech

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_model(model_size):
    """Test a Whisper model and measure performance."""
    print(f"\n{'='*60}")
    print(f"Testing {model_size.upper()} model")
    print(f"{'='*60}")
    
    try:
        # Load model
        print(f"⏳ Loading {model_size} model...")
        load_start = time.time()
        
        # Use CPU (GPU has CUDNN issues)
        model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )
        print(f"   Using: CPU")
        
        load_time = time.time() - load_start
        print(f"✅ Model loaded in {load_time:.2f}s")
        
        # Transcribe
        print(f"🔄 Transcribing audio file...")
        transcribe_start = time.time()
        
        segments, info = model.transcribe(
            AUDIO_FILE,
            language=LANGUAGE,
            beam_size=5,
            word_timestamps=True,
            condition_on_previous_text=True,
            vad_filter=True
        )
        
        # Get text
        text = " ".join([segment.text for segment in segments]).strip()
        
        transcribe_time = time.time() - transcribe_start
        total_time = load_time + transcribe_time
        
        # Print results
        print(f"\n📝 Transcription:")
        print(f"   \"{text}\"")
        print(f"\n⏱️  Performance:")
        print(f"   Load time:       {load_time:.2f}s")
        print(f"   Transcribe time: {transcribe_time:.2f}s")
        print(f"   Total time:      {total_time:.2f}s")
        print(f"\n📊 Audio info:")
        print(f"   Language: {info.language}")
        print(f"   Probability: {info.language_probability:.2f}")
        
        return {
            'model': model_size,
            'load_time': load_time,
            'transcribe_time': transcribe_time,
            'total_time': total_time,
            'text': text,
            'language': info.language,
            'language_prob': info.language_probability
        }
        
    except Exception as e:
        print(f"❌ Error testing {model_size} model: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("🎤 Whisper Model Comparison Test")
    print(f"📁 Test file: {AUDIO_FILE}")
    print(f"🌍 Language: {LANGUAGE}")
    
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Error: Audio file not found: {AUDIO_FILE}")
        return
    
    # Test medium model
    print("\n" + "="*60)
    print("STEP 1: Testing MEDIUM model (current)")
    print("="*60)
    medium_result = test_model("medium")
    
    # Test large model
    print("\n" + "="*60)
    print("STEP 2: Testing LARGE model")
    print("="*60)
    print("⚠️  Note: This will download the model if not cached (~3GB)")
    large_result = test_model("large-v3")
    
    # Compare results
    if medium_result and large_result:
        print("\n" + "="*60)
        print("COMPARISON")
        print("="*60)
        
        print(f"\n📊 Speed comparison:")
        print(f"   Medium: {medium_result['total_time']:.2f}s (load: {medium_result['load_time']:.2f}s, transcribe: {medium_result['transcribe_time']:.2f}s)")
        print(f"   Large:  {large_result['total_time']:.2f}s (load: {large_result['load_time']:.2f}s, transcribe: {large_result['transcribe_time']:.2f}s)")
        
        speed_diff = large_result['total_time'] - medium_result['total_time']
        speed_percent = (speed_diff / medium_result['total_time']) * 100
        print(f"\n   Difference: {speed_diff:+.2f}s ({speed_percent:+.1f}%)")
        
        print(f"\n📝 Transcription comparison:")
        print(f"   Medium: \"{medium_result['text']}\"")
        print(f"   Large:  \"{large_result['text']}\"")
        
        if medium_result['text'] == large_result['text']:
            print(f"   ✅ Identical transcriptions")
        else:
            print(f"   ⚠️  Different transcriptions")
        
        print(f"\n🎯 Recommendation:")
        if speed_diff < 0.5 and medium_result['text'] == large_result['text']:
            print(f"   Large model is only {abs(speed_diff):.2f}s slower with same results.")
            print(f"   Consider using large-v3 for better accuracy overall.")
        elif speed_diff < 1.0:
            print(f"   Large model is {speed_diff:.2f}s slower.")
            print(f"   Trade-off: Better accuracy vs. speed.")
        else:
            print(f"   Large model is significantly slower ({speed_diff:.2f}s).")
            print(f"   Stick with medium for real-time voice control.")


if __name__ == "__main__":
    main()
