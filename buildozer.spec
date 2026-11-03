[app]
title = Panchayat App
package.name = panchayatapp
package.domain = com.vaibhav.panchayatapp
source.dir = .
source.include_exts = py,png,jpg,kv
version = 1.0
requirements = python3,kivy==2.3.0,Pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 28c
android.accept_sdk_license_agreement = True

[buildozer]
log_level = 2
warn_on_root = 1
