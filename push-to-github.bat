@echo off
setlocal enabledelayedexpansion

cd /d c:\Users\Ruban\Desktop\projects\finial_pro

REM Configure git
"C:\Program Files\Git\bin\git" config --global user.name "warzone4568game-droid"
"C:\Program Files\Git\bin\git" config --global user.email "warzone4568game@gmail.com"

REM Initialize git
echo.
echo Initializing Git repository...
"C:\Program Files\Git\bin\git" init

REM Add all files
echo.
echo Adding all files...
"C:\Program Files\Git\bin\git" add .

REM Create commit
echo.
echo Creating first commit...
"C:\Program Files\Git\bin\git" commit -m "Initial commit: Exam Mark Prediction System"

REM Add remote
echo.
echo Adding GitHub remote...
"C:\Program Files\Git\bin\git" remote remove origin 2>nul
"C:\Program Files\Git\bin\git" remote add origin https://github.com/warzone4568game-droid/exam-mark-prediction-system.git

REM Set main branch
echo.
echo Setting main branch...
"C:\Program Files\Git\bin\git" branch -M main

REM Push to GitHub
echo.
echo Pushing to GitHub...
"C:\Program Files\Git\bin\git" push -u origin main

echo.
echo ============================================
echo Push completed!
echo Check your repository at:
echo https://github.com/warzone/exam-mark-prediction-system
echo ============================================
pause
