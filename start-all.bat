@echo off
echo ================================================
echo  Personal Finance Assistant - Full Stack Startup
echo ================================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python main.py"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && streamlit run app.py"

echo.
echo ================================================
echo  Servers are starting...
echo ================================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
