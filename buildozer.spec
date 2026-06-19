[app]
title = 大乐斗助手
package.name = daledou
package.domain = org.daledou
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,yaml
source.include_patterns = config/*,config/**/*
version = 1.0.0
requirements = python3,kivy==2.3.0,httpx,pyyaml
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
