#!/usr/bin/env python3
"""
CML Voice-to-OpenCode with Porcupine + Whisper
===============================================
1. Listen for "C M L" wake word using Porcupine (offline)
2. Record command after wake word
3. Transcribe with local Whisper (GPU)
4. Send to OpenCode
"""

import pvporcupine
import pyaudio
import struct
import subprocess
import logging
import os
import sys
import tempfile
import time
import wave
from filelock import FileLock, Timeout

# Setup CUDNN library path for GPU support BEFORE importing WhisperModel
cudnn_path = os.path.expanduser(
    "~/.local/lib/python3.13/site-packages/nvidia/cudnn/lib"
)
cublas_path = os.path.expanduser(
    "~/.local/lib/python3.13/site-packages/nvidia/cublas/lib"
)
cuda_runtime_path = os.path.expanduser(
    "~/.local/lib/python3.13/site-packages/nvidia/cuda_runtime/lib"
)
if os.path.exists(cudnn_path):
    os.environ["LD_LIBRARY_PATH"] = (
        f"{cudnn_path}:{cublas_path}:{cuda_runtime_path}:"
        + os.environ.get("LD_LIBRARY_PATH", "")
    )

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("ERROR: faster-whisper not installed!")
    print("Run: pip3 install faster-whisper")
    sys.exit(1)

import speech_recognition as sr

# Configuration
KEYWORD_PATH = "/home/jirka/oc/porcupine-models/C-M-L_en_linux_v3_0_0.ppn"
ACCESS_KEY = "3yFshBAX2ELWaAic9Z7qSgHfE4ZTYvXjuooTntO+4m8HoyAZFE6cMQ=="
OPENCODE_WINDOW_CLASS = "kitty"
WHISPER_MODEL_SIZE = "medium"  # medium model for better accuracy
WHISPER_LANGUAGE = "cs"  # Czech
CONFIRMATION_SOUND = os.path.expanduser("~/cml/voice-output/cache/ano-cml.mp3")
SPEECH_LOCK_FILE = "/tmp/speech.lock"  # Shared lock file for speech synchronization
AUTO_LISTEN_TRIGGER = (
    "/tmp/cml-auto-listen.trigger"  # Trigger file for auto-listening after questions
)
AUTO_LISTEN_TIMEOUT = 5  # Seconds to wait for user to start speaking after question

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize
recognizer = sr.Recognizer()
recognizer.pause_threshold = 2.5
mic = sr.Microphone()
whisper_model = None


def load_whisper_model():
    """Load Whisper model (lazy loading)."""
    global whisper_model
    if whisper_model is None:
        logging.info(f"🔄 Loading Whisper model ({WHISPER_MODEL_SIZE})...")
        try:
            # Try GPU first
            whisper_model = WhisperModel(
                WHISPER_MODEL_SIZE, device="cuda", compute_type="float16"
            )
            logging.info("✅ Whisper model loaded (GPU)")
        except Exception as e:
            logging.warning(f"⚠️  GPU failed: {e}")
            logging.info("🔄 Falling back to CPU...")
            whisper_model = WhisperModel(
                WHISPER_MODEL_SIZE, device="cpu", compute_type="int8"
            )
            logging.info("✅ Whisper model loaded (CPU)")
    return whisper_model


def play_confirmation():
    """Play confirmation sound."""
    try:
        # Try pre-generated sound first
        if os.path.exists(CONFIRMATION_SOUND):
            subprocess.run(
                ["mpg123", "-q", CONFIRMATION_SOUND],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            # Fallback: use TTS
            subprocess.run(
                [os.path.expanduser("~/cml/voice-output/text-to-speech.sh"), "Ano?"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception as e:
        logging.warning(f"⚠️  Confirmation sound failed: {e}")


def notify_not_understood():
    """Notify user that speech was not understood."""
    try:
        logging.info("🔊 Playing 'not understood' notification...")
        # Vary the message for more natural interaction
        import random

        messages = [
            "Neslyšel jsem.",
            "Ano, ještě jednou.",
            "Nerozuměl jsem, zkuste to znovu.",
            "Prosím, zopakujte.",
        ]
        message = random.choice(messages)
        subprocess.run(
            [os.path.expanduser("~/cml/voice-output/text-to-speech.sh"), message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        logging.warning(f"⚠️  'Not understood' notification failed: {e}")


def process_voice_command_with_retry(
    porcupine, pa, audio_stream, max_attempts=3, initial_confirmation=True
):
    """
    Record and transcribe voice command with retry on failure.

    Args:
        porcupine: Porcupine instance
        pa: PyAudio instance
        audio_stream: Current audio stream (will be stopped/started)
        max_attempts: Maximum number of recording attempts
        initial_confirmation: Whether to play "Ano?" before first attempt

    Returns:
        str: Transcribed text, or empty string if all attempts failed
    """
    lock = FileLock(SPEECH_LOCK_FILE, timeout=10)

    for attempt in range(1, max_attempts + 1):
        logging.info(f"🎤 Attempt {attempt}/{max_attempts}")

        # Play confirmation sound on first attempt (if requested) or retry message
        if attempt == 1 and initial_confirmation:
            try:
                logging.info("🔒 Acquiring lock for confirmation sound...")
                with lock.acquire(timeout=10):
                    logging.info("✅ Playing confirmation 'Ano?'")
                    play_confirmation()
            except Timeout:
                logging.error("❌ Could not acquire lock for confirmation - timeout")
        elif attempt > 1:
            # Play retry message with lock
            try:
                logging.info("🔒 Acquiring lock for retry notification...")
                with lock.acquire(timeout=10):
                    notify_not_understood()
            except Timeout:
                logging.error("❌ Could not acquire lock for retry notification")

        # Stop wake word stream for recording
        audio_stream.stop_stream()

        # Record with lock
        audio_file = None
        try:
            logging.info("🔒 Acquiring lock for recording...")
            with lock.acquire(timeout=10):
                logging.info("✅ Recording user command...")
                audio_file = record_command_with_pyaudio(porcupine, pa)
        except Timeout:
            logging.error("❌ Could not acquire lock for recording - timeout")

        # Restart wake word stream
        audio_stream.start_stream()

        # Process transcription
        if audio_file:
            text = transcribe_with_whisper(audio_file)

            # Cleanup audio file
            if os.path.exists(audio_file):
                os.remove(audio_file)

            # Check if we got valid text
            if text and len(text) > 0:
                logging.info(f"✅ Successfully transcribed on attempt {attempt}")
                return text
            else:
                logging.warning(f"⚠️  Attempt {attempt} failed: no text recognized")
        else:
            logging.error(f"❌ Attempt {attempt} failed: recording error")

        # If not last attempt, continue loop for retry
        if attempt < max_attempts:
            logging.info("🔄 Retrying...")

    # All attempts failed
    logging.error(f"❌ All {max_attempts} attempts failed")
    return ""


def show_notification(title, message):
    """Show desktop notification."""
    try:
        subprocess.run(["notify-send", "-u", "normal", "-t", "2000", title, message])
    except Exception as e:
        logging.warning(f"⚠️  Notification failed: {e}")


def record_command_with_pyaudio(porcupine, pa):
    """Record command using PyAudio (same stream as Porcupine)."""
    logging.info("🎤 Recording command... (speak now)")

    temp_file = None
    frames = []

    try:
        # Open stream for recording
        stream = pa.open(
            rate=16000,  # Standard rate for Whisper
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=1024,
        )

        # Calibrate noise level - sample first 5 chunks (~0.32 seconds)
        # Skip first few to let "Ano?" fade out completely (if wake word was used)
        logging.info("📊 Calibrating noise level...")
        noise_samples = []

        # Discard first 3 chunks (faster startup - 0.19s)
        for _ in range(3):
            stream.read(1024)

        # Now measure actual noise
        for _ in range(5):
            data = stream.read(1024)
            audio_data = struct.unpack(f"{1024}h", data)
            avg_amplitude = sum(abs(x) for x in audio_data) / len(audio_data)
            noise_samples.append(avg_amplitude)

        # Calculate SENSITIVE threshold for better silence detection
        base_noise = sum(noise_samples) / len(noise_samples)
        max_noise = max(noise_samples)
        # Use 2x avg for better sensitivity (lower threshold = detects silence better)
        silence_threshold = base_noise * 2.0
        silence_threshold = max(
            silence_threshold, 300
        )  # Lower minimum for better silence detection
        silence_threshold = min(
            silence_threshold, 1200
        )  # Lower cap - if user stops talking, cut faster
        logging.info(
            f"📊 Avg noise: {base_noise:.0f}, Max noise: {max_noise:.0f}, Silence threshold: {silence_threshold:.0f}"
        )

        # Record for up to 30 seconds or until silence
        silence_chunks = 0
        max_silence_chunks = 47  # ~3 seconds of silence (1024 samples @ 16kHz = ~64ms per chunk, 47*64ms = 3s)
        max_chunks = 469  # ~30 seconds max

        for i in range(max_chunks):
            data = stream.read(1024)
            frames.append(data)

            # Simple silence detection
            audio_data = struct.unpack(f"{1024}h", data)
            avg_amplitude = sum(abs(x) for x in audio_data) / len(audio_data)

            # Debug: print amplitude every 16 chunks (~1 second)
            if i % 16 == 0:
                logging.info(
                    f"🎚️  Amplitude: {avg_amplitude:.0f} (threshold: {silence_threshold:.0f})"
                )

            if avg_amplitude < silence_threshold:
                silence_chunks += 1
                if (
                    silence_chunks > max_silence_chunks and i > 10
                ):  # At least 0.5s of audio
                    logging.info(
                        f"🔇 Silence detected (amplitude: {avg_amplitude:.0f} < {silence_threshold:.0f}), stopping recording"
                    )
                    break
            else:
                silence_chunks = 0

        stream.stop_stream()
        stream.close()

        # Save to WAV file
        temp_file = tempfile.mktemp(suffix=".wav")
        with wave.open(temp_file, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b"".join(frames))

        return temp_file

    except Exception as e:
        logging.error(f"❌ Recording error: {e}")
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
        return None


def transcribe_with_whisper(audio_file):
    """Transcribe audio file with Whisper."""
    try:
        logging.info("🔄 Transcribing with Whisper...")

        model = load_whisper_model()

        # Transcribe with advanced settings (same as Caps Lock system)
        segments, info = model.transcribe(
            audio_file,
            language=WHISPER_LANGUAGE,
            beam_size=5,
            word_timestamps=True,  # Track word timing for better accuracy
            condition_on_previous_text=True,  # Use context from previous text
            vad_filter=True,  # Voice Activity Detection - filter noise and silence
        )

        # Get text
        text = " ".join([segment.text for segment in segments]).strip()

        if text and len(text) >= 3:
            logging.info(f"📝 Transcribed: {text}")
            return text
        else:
            logging.warning("⚠️  Transcription too short or empty")
            return ""  # Return empty string to signal failure (not None)

    except Exception as e:
        logging.error(f"❌ Transcription error: {e}")
        return ""  # Return empty string to signal failure


def find_kitty_socket():
    """Find the correct kitty socket from saved file."""
    try:
        import os

        # Read socket path from file (saved by start-opencode.sh)
        socket_file = os.path.expanduser("~/.opencode-socket")

        if os.path.exists(socket_file):
            with open(socket_file, "r") as f:
                socket_listen_on = f.read().strip()

            # Extract socket path from "unix:/tmp/kitty-socket-xxxxx"
            if socket_listen_on.startswith("unix:"):
                socket_path = socket_listen_on[5:]  # Remove "unix:" prefix
                logging.info(f"✅ Found kitty socket from file: {socket_path}")
                return socket_path

        # Fallback: find any socket
        import glob

        sockets = glob.glob("/tmp/kitty-socket-*")
        if sockets:
            socket_path = sockets[0]
            logging.warning(f"⚠️  Socket file not found, using fallback: {socket_path}")
            return socket_path

        logging.error("❌ No kitty socket found")
        return None

    except Exception as e:
        logging.error(f"❌ Error finding kitty socket: {e}")
        return None


def send_to_opencode(text):
    """Send text to OpenCode using kitten @ and xdotool."""
    try:
        # Find kitty socket
        socket_path = find_kitty_socket()
        if not socket_path:
            return False

        # Read OpenCode window ID from file
        window_id_file = os.path.expanduser("~/.opencode-window-id")

        if not os.path.exists(window_id_file):
            logging.error("❌ OpenCode window ID file not found!")
            logging.error("   Run 'aic' to start OpenCode and save window ID")
            return False

        with open(window_id_file, "r") as f:
            opencode_window_id = f.read().strip()

        if not opencode_window_id:
            logging.error("❌ OpenCode window ID is empty")
            return False

        logging.info(f"✅ Using OpenCode window ID: {opencode_window_id}")

        # Send text to the specific Kitty window
        subprocess.run(
            [
                "kitten",
                "@",
                "--to",
                f"unix:{socket_path}",
                "send-text",
                "--match",
                f"id:{opencode_window_id}",
                text,  # Send text without newline
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Press Enter using send-key
        subprocess.run(
            [
                "kitten",
                "@",
                "--to",
                f"unix:{socket_path}",
                "send-key",
                "--match",
                f"id:{opencode_window_id}",
                "enter",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        logging.info(f"✅ Sent to OpenCode: {text}")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed to send to OpenCode: {e}")
        if e.stderr:
            logging.error(f"   stderr: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"❌ Error sending text: {e}")
        return False


def main():
    print("🎧 CML Voice-to-OpenCode")
    print(f"📁 Wake word model: C M L")
    print(f"🤖 Whisper model: {WHISPER_MODEL_SIZE}")
    print("🎤 Listening for 'C M L'...")
    print("Press Ctrl+C to stop\n")

    porcupine = None
    pa = None
    audio_stream = None
    processing = False  # Flag to prevent multiple wake word detections

    try:
        # Initialize Porcupine
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY, keyword_paths=[KEYWORD_PATH]
        )

        # Initialize PyAudio
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        logging.info("✅ System ready, listening for wake word...\n")

        # Main loop
        while True:
            # Check for auto-listen trigger (question asked by AI)
            if os.path.exists(AUTO_LISTEN_TRIGGER) and not processing:
                processing = True
                logging.info("🔔 AUTO-LISTEN TRIGGER DETECTED (question asked)")

                # Remove trigger file
                try:
                    os.remove(AUTO_LISTEN_TRIGGER)
                except:
                    pass

                # NO confirmation sound for auto-listen (user already heard the question)
                logging.info("⏩ Skipping 'Ano?' - silent auto-listen mode")

                # Use retry mechanism (no initial confirmation, max 3 attempts)
                text = process_voice_command_with_retry(
                    porcupine,
                    pa,
                    audio_stream,
                    max_attempts=3,
                    initial_confirmation=False,
                )

                # Send to OpenCode if we got text
                if text and len(text) > 0:
                    send_to_opencode(text)
                else:
                    logging.error("❌ All retry attempts failed")

                logging.info("🎤 Ready for next wake word...\n")
                processing = False
                continue

            # Listen for wake word (only if not currently processing)
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0 and not processing:
                processing = True  # Block further wake word detections
                logging.info("🔔 WAKE WORD DETECTED: C M L")

                # Try to acquire lock immediately (non-blocking) to check if someone is speaking
                lock = FileLock(SPEECH_LOCK_FILE, timeout=0)
                try:
                    lock.acquire(timeout=0)  # Try immediately
                    lock.release()  # Lock was free, release it
                    logging.info("✅ No one speaking, proceeding normally")
                except Timeout:
                    # Lock is held by someone else (TTS is speaking)
                    logging.warning("⚠️  Speech lock is held - OpenCode is speaking!")
                    logging.info("🛑 Stopping TTS process...")

                    # Kill all audio players that might be playing TTS
                    subprocess.run(["killall", "-9", "mpv"], stderr=subprocess.DEVNULL)
                    subprocess.run(
                        ["killall", "-9", "ffplay"], stderr=subprocess.DEVNULL
                    )
                    subprocess.run(["killall", "-9", "play"], stderr=subprocess.DEVNULL)

                    # Wait longer for processes to die and lock to be released
                    time.sleep(1.0)
                    logging.info("✅ TTS stopped - proceeding with wake word")

                # Use retry mechanism (with initial "Ano?" confirmation, max 3 attempts)
                text = process_voice_command_with_retry(
                    porcupine,
                    pa,
                    audio_stream,
                    max_attempts=3,
                    initial_confirmation=True,
                )

                # Send to OpenCode if we got text
                if text and len(text) > 0:
                    send_to_opencode(text)
                else:
                    logging.error("❌ All retry attempts failed")

                logging.info("🎤 Ready for next wake word...\n")
                processing = False  # Allow wake word detection again

    except KeyboardInterrupt:
        print("\n👋 Stopping listener...")
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if audio_stream is not None:
            try:
                audio_stream.close()
            except:
                pass
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()


if __name__ == "__main__":
    main()
