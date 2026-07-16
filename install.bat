@echo off
REM One-command setup for Windows.
REM Handles the dlib-bin / face_recognition install order so nobody has to
REM compile dlib from source (which needs Visual Studio Build Tools and can
REM take a long time, or fail outright without the C++ workload installed).

echo === FaceTrack AI ^- setup ===

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Upgrading pip...
pip install --upgrade pip -q

echo Installing dependencies (dlib-bin gives you a precompiled dlib, no Visual Studio Build Tools needed)...
pip install -r requirements.txt

echo Installing face_recognition (--no-deps so it doesn't try to rebuild dlib from source)...
pip install --no-deps face_recognition==1.3.0

echo.
echo === Setup complete ===
echo Run the app with:
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo Then open http://localhost:5000  (default login: admin / Admin@123)
pause
