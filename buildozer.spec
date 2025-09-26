[app]

# Application title
title = Remote Shutdown Controller

# Package name (com.domain.appname format)
package.name = remoteshutdown

# Package domain (needed for android packaging)
package.domain = org.example

# Source code where the main.py is located
source.dir = .

# Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# Application versioning (method 1)
version = 1.0

# Application requirements
requirements = python3,kivy,requests,urllib3,certifi

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Android app theme
android.theme = @android:style/Theme.NoTitleBar

# List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Android application meta-data to set
#android.meta_data =

# Android library project to add to the project
#android.add_src =

# Android logcat filters to use
#android.logcat_filters = *:S python:D

# Copy library/jar automatically depending on requirements
android.copy_libs = 1

# The Android arch to build for
android.arch = armeabi-v7a

# The Android API to use
android.api = 31

# The minimum API your APK will support
android.minapi = 21

# The Android NDK version to use
android.ndk = 25b

# The Android SDK version to use
android.sdk = 31

# Python for android recipe to use
#p4a.recipe =

# Whitelist for the python modules and packages to be installed
#p4a.whitelist =

# Bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# Path to build artifact storage
build_dir = ./.buildozer

# Path to build output (apk) storage  
bin_dir = ./bin

# Warn when running as root
warn_on_root = 1