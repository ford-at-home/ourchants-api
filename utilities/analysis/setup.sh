#!/bin/bash

set -e

ENV_NAME="essentia-env"

echo "🔧 Creating virtual environment: $ENV_NAME"
python3 -m venv $ENV_NAME
source $ENV_NAME/bin/activate

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing pip dependencies..."
pip install -r requirements.txt

echo "🧪 Checking for conda..."
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda before continuing."
    exit 1
fi

echo "📚 Installing Essentia (via conda)..."
conda install -y -c conda-forge essentia

echo "🎧 Verifying ffmpeg is available..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ ffmpeg not found. Please install it:"
    echo "Mac: brew install ffmpeg"
    echo "Debian/Ubuntu: sudo apt install ffmpeg"
    exit 1
fi

echo "✅ Setup complete!"

echo ""
echo "🚀 To get started:"
echo "source $ENV_NAME/bin/activate"
echo "python analyze_chant.py <your_file.mp3>"

