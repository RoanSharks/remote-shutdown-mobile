@echo off
echo Building Android APK using Docker...

REM Build Docker image
docker build -t mobile-controller-builder .

REM Run container and build APK
docker run --rm -v "%cd%:/app" mobile-controller-builder

REM Copy APK from container
echo APK should be in the bin folder!
pause