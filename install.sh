#!/usr/bin/env bash
# One-command setup for Linux/macOS.
# Handles the dlib-bin / face_recognition install order so nobody has to
# compile dlib from source (which needs cmake + a C++ compiler and can take
# 10-20+ minutes, or fail outright on some machines).
set -e

echo "=== FaceTrack AI — setup ==="

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip -q

echo "Installing dependencies (dlib-bin gives you a precompiled dlib, no cmake needed)..."
pip install -r requirements.txt

echo "Installing face_recognition (--no-deps so it doesn't try to rebuild dlib from source)..."
pip install --no-deps face_recognition==1.3.0

echo ""
echo "=== Setup complete ==="
echo "Run the app with:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open http://localhost:5000  (default login: admin / Admin@123)"
