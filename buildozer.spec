[app]

# Application title
title = Remote Shutdown Controller

# Package name (com.domain.appname format)
package.name = remoteshutdown

# Package domain (needed for android packaging)
package.domain = com.tarbunny

# Source code where the main.py is located
source.dir = .

# Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# Application versioning (method 1)
version = 1.0

# Application requirements
requirements = python3,kivy==2.1.0,requests,urllib3,certifi

[android]

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Android app theme
android.theme = @android:style/Theme.NoTitleBar

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Copy library/jar automatically depending on requirements
android.copy_libs = 1

# The Android arch to build for
android.archs = arm64-v8a

# The Android API to use
android.api = 28

# The minimum API your APK will support
android.minapi = 21

# The Android NDK version to use
android.ndk = 21b

# Bootstrap to use for android builds
p4a.bootstrap = sdl2

# Python for android branch to use
p4a.branch = master

# Skip SDK/NDK installation since we pre-installed them
android.skip_update = True

# Use our pre-installed SDK and NDK (via symlink at /app/.buildozer)
android.sdk_path = /app/.buildozer/android/platform/android-sdk
android.ndk_path = /app/.buildozer/android/platform/android-ndk-r21b
android.ant_path = /app/.buildozer/android/platform/apache-ant-1.9.4

# Prevent buildozer from downloading additional components
p4a.source_dir = /app/.buildozer/android/platform/python-for-android

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# Path to build artifact storage
build_dir = ./.buildozer

# Path to build output (apk) storage  
bin_dir = ./bin

# Warn when running as root
warn_on_root = 1