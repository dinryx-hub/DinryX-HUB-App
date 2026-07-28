[app]

# Назва твого мобільного додатку
title = DinryX Mobile HUB

# Ім'я пакету (має бути унікальним)
package.name = dinryxhubmobile

# Домен пакету
package.domain = org.dinryx

# Які файли включати у збірку
source.include_exts = py,png,jpg,kv,atlas

# Головний файл скрипту
source.main_file = DinryX HUB Mobile.py

# Версія додатку
version = 1.1.0

# Необхідні бібліотеки для Python
requirements = python3,kivy,requests,urllib3,idna,certifi,charset-normalizer

# Орієнтація екрана (portrait — вертикальна)
orientation = portrait

# Дозволи Android (інтернет потрібен для завантаження софту, сховище — для збереження APK)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Версія Android API за замовчуванням
android.api = 33
android.min_api = 21

[buildozer]
log_level = 2
warn_on_root = 1
