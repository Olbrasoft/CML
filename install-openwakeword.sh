#!/bin/bash
# Install OpenWakeWord and dependencies on Debian system

set -e  # Exit on error

echo "🔧 Installing OpenWakeWord for Czech CML wake word detection"
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please do not run as root. Use your regular user account."
   exit 1
fi

# Install system dependencies
echo "📦 Step 1: Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-dev portaudio19-dev

echo "✅ System dependencies installed"
echo ""

# Install Python packages
echo "📦 Step 2: Installing Python packages..."
pip3 install --user openwakeword pyaudio numpy

echo "✅ Python packages installed"
echo ""

# Create model directory
echo "📁 Step 3: Creating model directory..."
mkdir -p ~/oc/openwakeword-models

echo "✅ Model directory created: ~/oc/openwakeword-models"
echo ""

# Make the listener script executable
echo "🔧 Step 4: Making listener script executable..."
chmod +x ~/cml/cml-wake-listener-openwakeword.py

echo "✅ Script is now executable"
echo ""

echo "============================================================"
echo "✅ OpenWakeWord installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Train the Czech model using Google Colab:"
echo "      Upload: ~/cml/Czech_CML_Wake_Word_Training.ipynb"
echo ""
echo "   2. Download the trained model (cml_cs.onnx)"
echo ""
echo "   3. Place the model in:"
echo "      ~/oc/openwakeword-models/cml_cs.onnx"
echo ""
echo "   4. Test the wake word listener:"
echo "      ~/cml/cml-wake-listener-openwakeword.py"
echo ""
echo "   5. If it works well, update start-cml-voice.sh to use"
echo "      the new OpenWakeWord listener instead of Porcupine"
echo ""
