[app]

title = DinryX Mobile HUB

package.name = dinryxhubmobile
package.domain = org.dinryx

source.dir = .

source.include_exts = py,png,jpg,kv,atlas

version = 1.1.0

requirements = python3,kivy,requests

orientation = portrait

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.min_api = 24
android.ndk_api = 24

fullscreen = 0

[buildozer]

log_level = 2
warn_on_root = 1
