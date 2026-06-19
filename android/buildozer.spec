[app]

# (str) Title of your application
title = Q宠大乐斗助手

# (str) Package name
package.name = daledou

# (str) Package domain (needed for android/ios packaging)
package.domain = org.daledou

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,yaml

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .git, __pycache__, android, .buildozer

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,httpx,pyyaml,plyer

# (str) Supported orientation (landscape, portrait or all)
orientations = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 26d

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning (and auto-close) timeout
warn_on_root = 1
