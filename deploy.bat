@echo off
echo TermoApp Docker Deployment
echo ========================

:menu
echo.
echo Choose an option:
echo 1. Build Docker image
echo 2. Start application
echo 3. Build and start
echo 4. Stop application
echo 5. View logs
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto build
if "%choice%"=="2" goto start
if "%choice%"=="3" goto buildstart
if "%choice%"=="4" goto stop
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto exit
goto menu

:build
echo Building Docker image...
docker-compose build
echo Build completed!
pause
goto menu

:start
echo Starting application...
docker-compose up -d
echo Application started at http://localhost:5000
pause
goto menu

:buildstart
echo Building and starting application...
docker-compose up --build -d
echo Application started at http://localhost:5000
pause
goto menu

:stop
echo Stopping application...
docker-compose down
echo Application stopped!
pause
goto menu

:logs
echo Showing logs (press Ctrl+C to exit)...
docker-compose logs -f
pause
goto menu

:exit
echo Goodbye!
exit 