# Remote Shutdown Controller Mobile App

A mobile app to remotely shutdown computers via Cloudflare tunnels.

## Features
- 📱 Mobile-optimized touch interface
- 🔒 Secure authentication with admin tokens
- 🌐 Works through Cloudflare tunnels
- ✅ Connection testing before shutdown
- 📋 Built-in setup instructions

## Files
- `main.py` - Main mobile application (Kivy-based)
- `buildozer.spec` - Build configuration for Android APK
- `mobile_requirements.txt` - Python dependencies

## How to Use
1. Run your Cloudflare tunnel on the target computer
2. Enter the tunnel URL in the app (with /shutdown endpoint)
3. Test connection to verify tunnel is working
4. Use the shutdown button to remotely shutdown the target

## Building APK
This repository is configured with GitHub Actions to automatically build Android APK files. The APK will be available as artifacts after each commit.

## Desktop Testing
You can test the mobile app on desktop:
```bash
pip install kivy requests urllib3
python main.py
```