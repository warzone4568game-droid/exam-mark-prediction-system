@echo off
setlocal enabledelayedexpansion

cd /d c:\Users\Ruban\Desktop\projects\finial_pro

echo Checking for Heroku CLI...
where heroku >nul 2>&1
if errorlevel 1 (
  echo.
  echo Heroku CLI was not found.
  echo Install it from: https://devcenter.heroku.com/articles/heroku-cli
  echo Then re-run this script: deploy-heroku.bat
  pause
  exit /b 1
)

echo Heroku CLI found.
heroku --version

echo.
echo Logging in to Heroku...
heroku login
if errorlevel 1 (
  echo Heroku login failed or was canceled.
  pause
  exit /b 1
)

echo.
echo Ensuring Git branch is main...
"C:\Program Files\Git\bin\git" branch -M main

echo.
echo Creating Heroku app...
heroku create exam-mark-prediction-system
if errorlevel 1 (
  echo Custom app name unavailable or create failed.
  echo Creating app with a generated name instead...
  heroku create
  if errorlevel 1 (
    echo Heroku app creation failed.
    pause
    exit /b 1
  )
)

echo.
echo Pushing code to Heroku...
"C:\Program Files\Git\bin\git" push heroku main
if errorlevel 1 (
  echo Git push to Heroku failed.
  echo Make sure your code is committed and the main branch exists.
  pause
  exit /b 1
)

echo.
echo Opening Heroku app in browser...
heroku open

echo.
echo Deployment complete.
pause
