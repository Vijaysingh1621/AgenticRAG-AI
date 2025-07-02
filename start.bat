@echo off
echo ===============================================
echo    🧠 Agentic RAG Chatbot - Startup Script
echo ===============================================
echo.

REM Check if Google API key is set
echo 🔍 Checking configuration...
findstr /C:"GOOGLE_API_KEY=your_google_api_key_here" backend\.env >nul
if %errorlevel% == 0 (
    echo ❌ Google API key not configured!
    echo.
    echo Please edit backend\.env and set your Google API key:
    echo 1. Get key from: https://makersuite.google.com/app/apikey
    echo 2. Edit backend\.env
    echo 3. Replace: GOOGLE_API_KEY=your_google_api_key_here
    echo 4. With:    GOOGLE_API_KEY=YOUR_ACTUAL_KEY
    echo.
    pause
    exit /b 1
)

echo ✅ Configuration looks good!
echo.

REM Start backend
echo 🚀 Starting backend server...
start "Agentic RAG Backend" cmd /k "cd /d "%~dp0backend" && "C:/Users/VIJAY SINGH/Desktop/GEN-AI/chatbot-query/.venv/Scripts/python.exe" main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🌐 Starting frontend server...
start "Agentic RAG Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===============================================
echo 🎉 Agentic RAG Chatbot is starting up!
echo.
echo 📍 Backend:  http://localhost:8001
echo 📍 Frontend: http://localhost:5173
echo.
echo Features available:
echo   🎙️  Voice queries (click microphone)
echo   📄  PDF upload with image processing
echo   🌐  Web search integration
echo   ☁️  Google Drive MCP
echo   📊  Smart citations with click-to-view
echo.
echo Press any key to close this window...
echo ===============================================
pause >nul
