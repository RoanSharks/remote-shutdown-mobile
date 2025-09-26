@echo off
echo Setting up GitHub repository for APK build...
echo.
echo Please follow these steps:
echo.
echo 1. Go to https://github.com and create a new repository called 'remote-shutdown-mobile'
echo 2. Copy the repository URL (like: https://github.com/yourusername/remote-shutdown-mobile.git)
echo 3. Run these commands:
echo.
echo    git remote add origin [YOUR_REPO_URL]
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. After pushing, go to your GitHub repository
echo 5. Click on 'Actions' tab
echo 6. The build will start automatically!
echo 7. Download the APK from the 'Artifacts' section when build completes
echo.
echo Your mobile controller is ready to build!
pause