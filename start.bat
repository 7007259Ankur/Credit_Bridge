@echo off
echo Starting CreditBridge...

REM Ensure backend has access to .env
if exist .env copy /Y .env backend\.env > nul

REM Ensure DB tables exist and dependencies are installed
cd backend
echo Installing Backend Dependencies...
python -m pip install -e .
python create_tables.py
cd ..

REM Start backend in background
start "CreditBridge Backend" cmd /c "cd backend && uvicorn app.main:app --reload --port 8000"

REM Wait 2 seconds for backend to start
timeout /t 2 /nobreak > nul

REM Start frontend
cd frontend
echo Installing Frontend Dependencies (this may take a moment)...
call npm install
echo Starting Frontend...
npm run dev
