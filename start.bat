@echo off
echo Starting Tekshila Application...
echo.

echo [1/2] Starting FastAPI Backend Server...
start /B "FastAPI" cmd /c "cd /d %~dp0 && .venv\Scripts\python.exe api_bridge.py"

echo [2/2] Starting Vite Frontend Server...
start /B "Vite" cmd /c "cd /d %~dp0 && npm run dev"

echo.
echo ✅ Application started successfully!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🚀 Backend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo Servers stopped.
pause
