@echo off
echo Building Android APK using Docker...

REM Change to the script's directory
cd /d "%~dp0"

REM Clean up any existing image
docker rmi mobile-controller-builder 2>nul

REM Build Docker image
echo Building Docker image...
docker build -t mobile-controller-builder .

if %ERRORLEVEL% neq 0 (
    echo Failed to build Docker image!
    pause
    exit /b 1
)

REM Create bin directory if it doesn't exist
if not exist "bin" mkdir bin

REM Run container and build APK
echo Building APK...
docker run --rm -v "%cd%:/app" mobile-controller-builder

if %ERRORLEVEL% neq 0 (
    echo Failed to build APK!
    pause
    exit /b 1
)

REM Check if APK was created
if exist "bin\*.apk" (
    echo APK built successfully! Check the bin folder.
    dir bin\*.apk
) else (
    echo No APK found in bin folder. Check the build logs above.
)

pause