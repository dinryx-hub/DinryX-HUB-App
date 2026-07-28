import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
import requests

# Перевіряємо, чи працюємо ми на Android
try:
    from jnius import autoclass
    from android import mActivity
    from android.permissions import request_permissions, Permission
    ANDROID_PLATFORM = True
except ImportError:
    ANDROID_PLATFORM = False

# Розширений каталог програм за категоріями
MOBILE_PROGRAMS = [
    # Месенджери
    {"name": "Telegram", "category": "Месенджери", "desc": "Швидкий та безпечний месенджер", "url": "https://telegram.org/dl/android/apk", "file": "telegram.apk", "is_direct": True},
    {"name": "Discord", "category": "Месенджери", "desc": "Голосовий та текстовий чат", "url": "https://play.google.com/store/apps/details?id=com.discord", "file": "discord.apk", "is_direct": False},
    {"name": "Viber", "category": "Месенджери", "desc": "Дзвінки та повідомлення", "url": "https://play.google.com/store/apps/details?id=com.viber.voip", "file": "viber.apk", "is_direct": False},
    
    # Редактори фото
    {"name": "Snapseed", "category": "Фото", "desc": "Професійний редактор фото від Google", "url": "https://play.google.com/store/apps/details?id=com.niksoftware.snapseed", "file": "snapseed.apk", "is_direct": False},
    {"name": "Picsart", "category": "Фото", "desc": "Фоторедактор та колажі", "url": "https://play.google.com/store/apps/details?id=com.picsart.studio", "file": "picsart.apk", "is_direct": False},

    # Рисовалки
    {"name": "Ibis Paint X", "category": "Рисовалка", "desc": "Популярний додаток для малювання", "url": "https://play.google.com/store/apps/details?id=jp.ne.ibis.ibispaintx.app", "file": "ibispaint.apk", "is_direct": False},
    {"name": "Medibang Paint", "category": "Рисовалка", "desc": "Зручна програма для коміксів та арту", "url": "https://play.google.com/store/apps/details?id=com.medibang.android.paint.tablet", "file": "medibang.apk", "is_direct": False},
]

class DinryXMobileHubApp(App):
    def build(self):
        if ANDROID_PLATFORM:
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        root_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Шапка
        header = Label(
            text="DinryX HUB [Mobile Edition]",
            font_size=20,
            bold=True,
            size_hint=(1, 0.1),
            color=(0.1, 0.8, 1, 1)
        )
        root_layout.add_widget(header)

        # Список програм з прокруткою
        scroll = ScrollView(size_hint=(1, 0.75))
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for prog in MOBILE_PROGRAMS:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=85, padding=5)
            
            # Кнопка програми
            btn_text = f"[b]{prog['name']}[/b] ([i]{prog['category']}[/i])\n[size=12]{prog['desc']}[/size]"
            btn_item = Button(
                text=btn_text,
                markup=True,
                background_color=(0.2, 0.2, 0.25, 1)
            )
            
            # Якщо посилання пряме — завантажуємо APK, якщо ні — відкриваємо браузер/маркет
            if prog['is_direct']:
                btn_item.bind(on_press=lambda instance, p=prog: self.start_download(p))
            else:
                btn_item.bind(on_press=lambda instance, p=prog: self.open_in_browser(p['url']))
                
            card.add_widget(btn_item)
            list_layout.add_widget(card)

        scroll.add_widget(list_layout)
        root_layout.add_widget(scroll)

        # Статус-бар
        self.status_label = Label(
            text="Оберіть додаток із каталогу",
            font_size=13,
            size_hint=(1, 0.15),
            color=(0.8, 0.8, 0.8, 1)
        )
        root_layout.add_widget(self.status_label)

        return root_layout

    def start_download(self, prog):
        self.status_label.text = f"Завантаження {prog['name']}..."
        threading.Thread(target=self.download_and_install, args=(prog,), daemon=True).start()

    def download_and_install(self, prog):
        try:
            if ANDROID_PLATFORM:
                Environment = autoclass('android.os.Environment')
                download_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
            else:
                download_dir = "."

            file_path = os.path.join(download_dir, prog['file'])
            headers = {"User-Agent": "Mozilla/5.0"}
            
            res = requests.get(prog['url'], headers=headers, stream=True, timeout=30)
            if res.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.status_label.text = "Завантажено! Запуск встановлення..."
                self.trigger_apk_install(file_path)
            else:
                self.status_label.text = "Помилка завантаження файлу!"
        except Exception as e:
            self.status_label.text = f"Помилка: {str(e)}"

    def trigger_apk_install(self, path):
        if ANDROID_PLATFORM:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            
            apk_file = File(path)
            context = PythonActivity.mActivity
            
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.fromFile(apk_file), "application/vnd.android.package-archive")
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            
            context.startActivity(intent)
        else:
            self.status_label.text = f"[ПК] Симуляція встановлення: {path}"

    def open_in_browser(self, url):
        self.status_label.text = "Відкриття сторінки додатка..."
        if ANDROID_PLATFORM:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            context = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            context.startActivity(intent)
        else:
            self.status_label.text = f"[ПК] Відкриття посилання: {url}"

if __name__ == '__main__':
    DinryXMobileHubApp().run()