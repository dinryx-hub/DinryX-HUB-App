import os
import sys
import platform
import threading
import subprocess
import webbrowser
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QTabWidget, QCheckBox,
    QScrollArea, QMessageBox, QComboBox, QTextEdit,
    QProgressBar, QToolButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMetaObject, Q_ARG

CURRENT_VERSION = "v1.4.1"
CURRENT_OS = platform.system()
GITHUB_REPO = "dinryx-hub/DinryX-HUB"
SITE_URL = "https://dinryx-hub.github.io/DinryX-HUB-App/download.html"

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "DinryX_HUB")
os.makedirs(APPDATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
DOWNLOAD_DIR = os.path.join(APPDATA_DIR, "Downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_DOWNLOADS = 3
HTTP_TIMEOUT = (10, 60)

TRANSLATIONS = {
    "English": {
        "tab_apps": "Apps", "tab_tools": "Tools", "tab_settings": "Settings", "tab_about": "About",
        "btn_start": "DOWNLOAD AND INSTALL", "btn_select_all": "Select All", "btn_reset": "Reset",
        "btn_fav": "⭐ Favorites", "cb_silent": "Silent installation (no windows)",
        "cb_clean": "Delete installers after installation",
        "console_title": "💻 Execution log (Console Log)",
        "warn_none": "Please select at least one app!", "done_title": "Done",
        "done_msg": "Download and installation process completed!",
        "log_no_apps": "[!] No apps selected.",
        "log_dl_start": "[*] Downloading: {}...", "log_dl_ok": "[+] Downloaded: {}",
        "log_dl_err": "[X] Download error {}: {}", "log_start_inst": "\n[*] Installing downloaded programs...",
        "log_inst": "[*] Installing: {}...", "log_inst_ok": "[+] Installed: {}",
        "log_inst_err": "[X] Installation error {}: {}",
        "log_linux": "[!] Auto-install on Linux requires manual opening of packages (.deb/.AppImage). Download finished.",
        "log_download_only": "[*] Download only mode (no installation).",
        "tools_title": "Useful system utilities", "tool_cmd": "Open command prompt (CMD)",
        "tool_folder": "Open downloads folder",
        "set_lang": "🌐 Interface language", "set_palette": "🎨 Accent color", "set_theme": "☀️ Theme mode",
        "theme_system": "System", "theme_dark": "Dark", "theme_light": "Light",
        "about_desc": "DinryX HUB — software download manager ({}).\nAutomatically downloads and installs official installers.",
        "about_author": "• Developer: RAIDDARK / DinryX Team\n• App Version: ",
        "btn_site": "🌐 Official Website / Updates",
        "update_found": "Update {} available!",
        "cat_utils": "📦 Utilities & Archivers", "cat_browsers": "🌐 Browsers & Internet",
        "cat_dev": "💻 Development & Code", "cat_media": "🎨 Graphics & Media",
        "cat_games": "🎮 Games & Launchers", "cat_chats": "💬 Messengers",
    },
    "Español": {
        "tab_apps": "Aplicaciones", "tab_tools": "Herramientas", "tab_settings": "Ajustes", "tab_about": "Acerca de",
        "btn_start": "DESCARGAR E INSTALAR", "btn_select_all": "Seleccionar todo", "btn_reset": "Restablecer",
        "btn_fav": "⭐ Favoritos", "cb_silent": "Instalación silenciosa (sin ventanas)",
        "cb_clean": "Eliminar instaladores tras la instalación",
        "console_title": "💻 Registro de ejecución",
        "warn_none": "¡Seleccione al menos una aplicación!", "done_title": "Hecho",
        "done_msg": "¡Proceso de descarga e instalación completado!",
        "log_no_apps": "[!] No se seleccionó ninguna aplicación.",
        "log_dl_start": "[*] Descargando: {}...", "log_dl_ok": "[+] Descargado: {}",
        "log_dl_err": "[X] Error de descarga {}: {}", "log_start_inst": "\n[*] Instalando programas descargados...",
        "log_inst": "[*] Instalando: {}...", "log_inst_ok": "[+] Instalado: {}",
        "log_inst_err": "[X] Error de instalación {}: {}",
        "log_linux": "[!] La autoinstalación en Linux requiere abrir manualmente los paquetes (.deb/.AppImage). Descarga finalizada.",
        "log_download_only": "[*] Modo solo descarga (sin instalación).",
        "tools_title": "Utilidades del sistema útiles", "tool_cmd": "Abrir símbolo del sistema (CMD)",
        "tool_folder": "Abrir carpeta de descargas",
        "set_lang": "🌐 Idioma de la interfaz", "set_palette": "🎨 Color de acento", "set_theme": "☀️ Modo de tema",
        "theme_system": "Sistema", "theme_dark": "Oscuro", "theme_light": "Claro",
        "about_desc": "DinryX HUB — gestor de descarga de software ({}).\nDescarga e instala automáticamente instaladores oficiales.",
        "about_author": "• Desarrollador: RAIDDARK / DinryX Team\n• Versión de la app: ",
        "btn_site": "🌐 Sitio web oficial / Actualizaciones",
        "update_found": "¡Actualización {} disponible!",
        "cat_utils": "📦 Utilidades y Archivadores", "cat_browsers": "🌐 Navegadores e Internet",
        "cat_dev": "💻 Desarrollo y Código", "cat_media": "🎨 Gráficos y Medios",
        "cat_games": "🎮 Juegos y Lanzadores", "cat_chats": "💬 Mensajería",
    },
    "Deutsch": {
        "tab_apps": "Apps", "tab_tools": "Werkzeuge", "tab_settings": "Einstellungen", "tab_about": "Über",
        "btn_start": "HERUNTERLADEN UND INSTALLIEREN", "btn_select_all": "Alle auswählen", "btn_reset": "Zurücksetzen",
        "btn_fav": "⭐ Favoriten", "cb_silent": "Stille Installation (ohne Fenster)",
        "cb_clean": "Installer nach Installation löschen",
        "console_title": "💻 Ausführungsprotokoll",
        "warn_none": "Bitte wählen Sie mindestens eine App aus!", "done_title": "Fertig",
        "done_msg": "Download- und Installationsvorgang abgeschlossen!",
        "log_no_apps": "[!] Keine Apps ausgewählt.",
        "log_dl_start": "[*] Herunterladen: {}...", "log_dl_ok": "[+] Heruntergeladen: {}",
        "log_dl_err": "[X] Download-Fehler {}: {}", "log_start_inst": "\n[*] Heruntergeladene Programme werden installiert...",
        "log_inst": "[*] Installieren: {}...", "log_inst_ok": "[+] Installiert: {}",
        "log_inst_err": "[X] Installationsfehler {}: {}",
        "log_linux": "[!] Die automatische Installation unter Linux erfordert das manuelle Öffnen von Paketen (.deb/.AppImage). Download beendet.",
        "log_download_only": "[*] Nur Download-Modus (keine Installation).",
        "tools_title": "Nützliche Systemprogramme", "tool_cmd": "Eingabeaufforderung öffnen (CMD)",
        "tool_folder": "Downloads-Ordner öffnen",
        "set_lang": "🌐 Schnittstellensprache", "set_palette": "🎨 Akzentfarbe", "set_theme": "☀️ Themenmodus",
        "theme_system": "System", "theme_dark": "Dunkel", "theme_light": "Hell",
        "about_desc": "DinryX HUB — Software-Download-Manager ({}).\nLädt automatisch offizielle Installer herunter und installiert sie.",
        "about_author": "• Entwickler: RAIDDARK / DinryX Team\n• App-Version: ",
        "btn_site": "🌐 Offizielle Website / Updates",
        "update_found": "Update {} verfügbar!",
        "cat_utils": "📦 Dienstprogramme & Archivierer", "cat_browsers": "🌐 Browser & Internet",
        "cat_dev": "💻 Entwicklung & Code", "cat_media": "🎨 Grafik & Medien",
        "cat_games": "🎮 Spiele & Launcher", "cat_chats": "💬 Messenger",
    },
    "Français": {
        "tab_apps": "Apps", "tab_tools": "Outils", "tab_settings": "Paramètres", "tab_about": "À propos",
        "btn_start": "TÉLÉCHARGER ET INSTALLER", "btn_select_all": "Tout sélectionner", "btn_reset": "Réinitialiser",
        "btn_fav": "⭐ Favoris", "cb_silent": "Installation silencieuse (sans fenêtre)",
        "cb_clean": "Supprimer les installeurs après installation",
        "console_title": "💻 Journal d'exécution",
        "warn_none": "Veuillez sélectionner au moins une application !", "done_title": "Terminé",
        "done_msg": "Processus de téléchargement et d'installation terminé !",
        "log_no_apps": "[!] Aucune application sélectionnée.",
        "log_dl_start": "[*] Téléchargement : {}...", "log_dl_ok": "[+] Téléchargé : {}",
        "log_dl_err": "[X] Erreur de téléchargement {}: {}", "log_start_inst": "\n[*] Installation des programmes téléchargés...",
        "log_inst": "[*] Installation : {}...", "log_inst_ok": "[+] Installé : {}",
        "log_inst_err": "[X] Erreur d'installation {}: {}",
        "log_linux": "[!] L'installation automatique sous Linux nécessite l'ouverture manuelle des paquets (.deb/.AppImage). Téléchargement terminé.",
        "log_download_only": "[*] Mode téléchargement uniquement (sans installation).",
        "tools_title": "Utilitaires système utiles", "tool_cmd": "Ouvrir l'invite de commandes (CMD)",
        "tool_folder": "Ouvrir le dossier des téléchargements",
        "set_lang": "🌐 Langue de l'interface", "set_palette": "🎨 Couleur d'accentuation", "set_theme": "☀️ Mode de thème",
        "theme_system": "Système", "theme_dark": "Sombre", "theme_light": "Clair",
        "about_desc": "DinryX HUB — gestionnaire de téléchargement ({}).\nTélécharge et installe automatiquement les installeurs officiels.",
        "about_author": "• Développeur : RAIDDARK / DinryX Team\n• Version de l'application : ",
        "btn_site": "🌐 Site officiel / Mises à jour",
        "update_found": "Mise à jour {} disponible !",
        "cat_utils": "📦 Utilitaires & Archiveurs", "cat_browsers": "🌐 Navigateurs & Internet",
        "cat_dev": "💻 Développement & Code", "cat_media": "🎨 Graphisme & Médias",
        "cat_games": "🎮 Jeux & Lanceurs", "cat_chats": "💬 Messageries",
    },
    "Polski": {
        "tab_apps": "Aplikacje", "tab_tools": "Narzędzia", "tab_settings": "Ustawienia", "tab_about": "O programie",
        "btn_start": "POBIERZ I ZAINSTALUJ", "btn_select_all": "Zaznacz wszystko", "btn_reset": "Resetuj",
        "btn_fav": "⭐ Ulubione", "cb_silent": "Cicha instalacja (bez okien)",
        "cb_clean": "Usuń instalatory po instalacji",
        "console_title": "💻 Dziennik wykonania",
        "warn_none": "Wybierz co najmniej jedną aplikację!", "done_title": "Gotowe",
        "done_msg": "Proces pobierania i instalacji zakończony!",
        "log_no_apps": "[!] Nie wybrano żadnych aplikacji.",
        "log_dl_start": "[*] Pobieranie: {}...", "log_dl_ok": "[+] Pobrano: {}",
        "log_dl_err": "[X] Błąd pobierania {}: {}", "log_start_inst": "\n[*] Instalowanie pobranych programów...",
        "log_inst": "[*] Instalowanie: {}...", "log_inst_ok": "[+] Zainstalowano: {}",
        "log_inst_err": "[X] Błąd instalacji {}: {}",
        "log_linux": "[!] Automatyczna instalacja w systemie Linux wymaga ręcznego otwarcia pakietów (.deb/.AppImage). Pobieranie zakończone.",
        "log_download_only": "[*] Tryb tylko pobierania (bez instalacji).",
        "tools_title": "Przydatne narzędzia systemowe", "tool_cmd": "Otwórz wiersz poleceń (CMD)",
        "tool_folder": "Otwórz folder pobranych plików",
        "set_lang": "🌐 Język interfejsu", "set_palette": "🎨 Kolor akcentu", "set_theme": "☀️ Tryb motywu",
        "theme_system": "Systemowy", "theme_dark": "Ciemny", "theme_light": "Jasny",
        "about_desc": "DinryX HUB — menedżer pobierania oprogramowania ({}).\nAutomatycznie pobiera i instaluje oficjalne instalatory.",
        "about_author": "• Deweloper: RAIDDARK / DinryX Team\n• Wersja aplikacji: ",
        "btn_site": "🌐 Oficjalna strona / Aktualizacje",
        "update_found": "Dostępna aktualizacja {}!",
        "cat_utils": "📦 Narzędzia i Archiwizatory", "cat_browsers": "🌐 Przeglądarki i Internet",
        "cat_dev": "💻 Programowanie i Kod", "cat_media": "🎨 Grafika i Media",
        "cat_games": "🎮 Gry i Launchery", "cat_chats": "💬 Komunikatory",
    },
    "Türkçe": {
        "tab_apps": "Uygulamalar", "tab_tools": "Araçlar", "tab_settings": "Ayarlar", "tab_about": "Hakkında",
        "btn_start": "İNDİR VE YÜKLE", "btn_select_all": "Tümünü Seç", "btn_reset": "Sıfırla",
        "btn_fav": "⭐ Favoriler", "cb_silent": "Sessiz kurulum (penceresiz)",
        "cb_clean": "Kurulumdan sonra yükleyicileri sil",
        "console_title": "💻 Çalıştırma Günlüğü",
        "warn_none": "Lütfen en az bir uygulama seçin!", "done_title": "Tamamlandı",
        "done_msg": "İndirme ve kurulum işlemi tamamlandı!",
        "log_no_apps": "[!] Hiçbir uygulama seçilmedi.",
        "log_dl_start": "[*] İndiriliyor: {}...", "log_dl_ok": "[+] İndirildi: {}",
        "log_dl_err": "[X] İndirme hatası {}: {}", "log_start_inst": "\n[*] İndirilen programlar kuruluyor...",
        "log_inst": "[*] Kuruluyor: {}...", "log_inst_ok": "[+] Kuruldu: {}",
        "log_inst_err": "[X] Kurulum hatası {}: {}",
        "log_linux": "[!] Linux'ta otomatik kurulum paketlerin (.deb/.AppImage) manuel açılmasını gerektirir. İndirme bitti.",
        "log_download_only": "[*] Yalnızca indirme modu (kurulum yok).",
        "tools_title": "Faydalı sistem araçları", "tool_cmd": "Komut İstemini Aç (CMD)",
        "tool_folder": "İndironler klasörünü aç",
        "set_lang": "🌐 Arayüz dili", "set_palette": "🎨 Vurgu rengi", "set_theme": "☀️ Tema modu",
        "theme_system": "Sistem", "theme_dark": "Karanlık", "theme_light": "Aydınlık",
        "about_desc": "DinryX HUB — yazılım indirme yöneticisi ({}).\nResmi yükleyicileri otomatik olarak indirir ve kurar.",
        "about_author": "• Geliştirici: RAIDDARK / DinryX Team\n• Uygulama Sürümü: ",
        "btn_site": "🌐 Resmi Web Sitesi / Güncellemeler",
        "update_found": "Güncelleme {} mevcut!",
        "cat_utils": "📦 Araçlar ve Arşivleyiciler", "cat_browsers": "🌐 Tarayıcılar ve İnternet",
        "cat_dev": "💻 Geliştirme ve Kod", "cat_media": "🎨 Grafikler ve Medya",
        "cat_games": "🎮 Oyunlar ve Başlatıcılar", "cat_chats": "💬 Mesajlaşma",
    },
    "Русский": {
        "tab_apps": "Приложения", "tab_tools": "Инструменты", "tab_settings": "Настройки", "tab_about": "О Приложении",
        "btn_start": "ЗАПУСТИТЬ ЗАГРУЗКУ И УСТАНОВКУ", "btn_select_all": "Выбрать все", "btn_reset": "Сбросить",
        "btn_fav": "⭐ Избранное", "cb_silent": "Тихая установка (без окон)",
        "cb_clean": "Удалить установщики после установки",
        "console_title": "💻 Журнал выполнения (Console Log)",
        "warn_none": "Выберите хотя бы одно приложение!", "done_title": "Готово",
        "done_msg": "Процесс загрузки и установки завершен!",
        "log_no_apps": "[!] Не выбрано ни одного приложения.",
        "log_dl_start": "[*] Загрузка: {}...", "log_dl_ok": "[+] Успешно загружено: {}",
        "log_dl_err": "[X] Ошибка загрузки {}: {}", "log_start_inst": "\n[*] Начало установки загруженных программ...",
        "log_inst": "[*] Установка: {}...", "log_inst_ok": "[+] Установлено: {}",
        "log_inst_err": "[X] Ошибка установки {}: {}",
        "log_linux": "[!] Автоустановка в Linux требует ручного открытия пакетов (.deb/.AppImage). Загрузка завершена.",
        "log_download_only": "[*] Режим только загрузки (без установки).",
        "tools_title": "Полезные системные утилиты", "tool_cmd": "Открыть командную строку (CMD)",
        "tool_folder": "Открыть папку загрузок",
        "set_lang": "🌐 Язык интерфейса", "set_palette": "🎨 Акцентный цвет", "set_theme": "☀️ Тема оформления",
        "theme_system": "Системная", "theme_dark": "Темная", "theme_light": "Светлая",
        "about_desc": "DinryX HUB — менеджер загрузки софта ({}).\nАвтоматически скачивает и устанавливает официальные установщики.",
        "about_author": "• Разработчик: RAIDDARK / DinryX Team\n• Версия приложения: ",
        "btn_site": "🌐 Официальный сайт / Обновления",
        "update_found": "Доступно обновление {}!",
        "cat_utils": "📦 Утилиты и Архиваторы", "cat_browsers": "🌐 Браузеры и Интернет",
        "cat_dev": "💻 Разработка и Код", "cat_media": "🎨 Графика и Медиа",
        "cat_games": "🎮 Игры и Лаунчеры", "cat_chats": "💬 Мессенджеры",
    },
    "Українська": {
        "tab_apps": "Додатки", "tab_tools": "Інструменти", "tab_settings": "Налаштування", "tab_about": "Про Додаток",
        "btn_start": "ЗАПУСТИТИ ЗАВАНТАЖЕННЯ ТА ВСТАНОВЛЕННЯ", "btn_select_all": "Вибрати усе", "btn_reset": "Скинути",
        "btn_fav": "⭐ Обране", "cb_silent": "Тихе встановлення (без вікон)",
        "cb_clean": "Видалити інсталятори після встановлення",
        "console_title": "💻 Журнал виконання (Console Log)",
        "warn_none": "Виберіть хоча б один додаток!", "done_title": "Готово",
        "done_msg": "Процес завантаження та встановлення завершено!",
        "log_no_apps": "[!] Не вибрано жодного додатка.",
        "log_dl_start": "[*] Завантаження: {}...", "log_dl_ok": "[+] Успішно завантажено: {}",
        "log_dl_err": "[X] Помилка завантаження {}: {}", "log_start_inst": "\n[*] Початок встановлення завантажених програм...",
        "log_inst": "[*] Встановлення: {}...", "log_inst_ok": "[+] Встановлено: {}",
        "log_inst_err": "[X] Помилка встановлення {}: {}",
        "log_linux": "[!] Автоматичне встановлення на Linux потребує ручного відкриття пакетів (.deb/.AppImage). Завантаження завершено.",
        "log_download_only": "[*] Режим лише завантаження (без встановлення).",
        "tools_title": "Корисні системні утиліти", "tool_cmd": "Відкрити командний рядок (CMD)",
        "tool_folder": "Відкрити папку завантажень",
        "set_lang": "🌐 Мова інтерфейсу", "set_palette": "🎨 Акцентний колір", "set_theme": "☀️ Тема оформлення",
        "theme_system": "Системна", "theme_dark": "Темна", "theme_light": "Світла",
        "about_desc": "DinryX HUB — менеджер завантаження софту ({}).\nАвтоматично завантажує та встановлює офіційні інсталятори.",
        "about_author": "• Розробник: RAIDDARK / DinryX Team\n• Версія додатка: ",
        "btn_site": "🌐 Офіційний сайт / Оновлення",
        "update_found": "Доступно оновлення {}!",
        "cat_utils": "📦 Утиліти та Архіватори", "cat_browsers": "🌐 Веб-браузери",
        "cat_dev": "💻 Розробка та Код", "cat_media": "🎨 Медіа та Графіка",
        "cat_games": "🎮 Ігри та Лаунчери", "cat_chats": "💬 Месенджери",
    },
    "中文": {
        "tab_apps": "应用", "tab_tools": "工具", "tab_settings": "设置", "tab_about": "关于",
        "btn_start": "下载并安装", "btn_select_all": "全选", "btn_reset": "重置",
        "btn_fav": "⭐ 收藏", "cb_silent": "静默安装（无窗口）",
        "cb_clean": "安装后删除安装包",
        "console_title": "💻 执行日志 (Console Log)",
        "warn_none": "请至少选择一个应用！", "done_title": "完成",
        "done_msg": "下载和安装过程已完成！",
        "log_no_apps": "[!] 未选择任何应用。",
        "log_dl_start": "[*] 正在下载: {}...", "log_dl_ok": "[+] 已下载: {}",
        "log_dl_err": "[X] 下载错误 {}: {}", "log_start_inst": "\n[*] 开始安装已下载的程序...",
        "log_inst": "[*] 正在安装: {}...", "log_inst_ok": "[+] 已安装: {}",
        "log_inst_err": "[X] 安装错误 {}: {}",
        "log_linux": "[!] Linux 上的自动安装需要手动打开包 (.deb/.AppImage)。下载完成。",
        "log_download_only": "[*] 仅下载模式（不安装）。",
        "tools_title": "实用的系统工具", "tool_cmd": "打开命令提示符 (CMD)",
        "tool_folder": "打开下载文件夹",
        "set_lang": "🌐 界面语言", "set_palette": "🎨 主题颜色", "set_theme": "☀️ 主题模式",
        "theme_system": "跟随系统", "theme_dark": "深色", "theme_light": "浅色",
        "about_desc": "DinryX HUB — 软件下载管理器 ({}).\n自动下载并安装官方安装程序。",
        "about_author": "• 开发人员: RAIDDARK / DinryX Team\n• 应用版本: ",
        "btn_site": "🌐 官方网站 / 更新",
        "update_found": "有新版本 {} 可用！",
        "cat_utils": "📦 工具与压缩", "cat_browsers": "🌐 浏览器与网络",
        "cat_dev": "💻 开发与代码", "cat_media": "🎨 图形与媒体",
        "cat_games": "🎮 游戏与启动器", "cat_chats": "💬 通讯软件",
    },
    "日本語": {
        "tab_apps": "アプリ", "tab_tools": "ツール", "tab_settings": "設定", "tab_about": "情報",
        "btn_start": "ダウンロードしてインストール", "btn_select_all": "すべて選択", "btn_reset": "リセット",
        "btn_fav": "⭐ お気に入り", "cb_silent": "サイレントインストール (ウィンドウなし)",
        "cb_clean": "インストール後にインストーラーを削除",
        "console_title": "💻 実行ログ (Console Log)",
        "warn_none": "アプリを少なくとも1つ選択してください！", "done_title": "完了",
        "done_msg": "ダウンロードとインストールのプロセスが完了しました！",
        "log_no_apps": "[!] アプリが選択されていません。",
        "log_dl_start": "[*] 下载中: {}...", "log_dl_ok": "[+] ダウンロード完了: {}",
        "log_dl_err": "[X] 下载エラー {}: {}", "log_start_inst": "\n[*] ダウンロードしたプログラムのインストールを開始...",
        "log_inst": "[*] インストール中: {}...", "log_inst_ok": "[+] インストール完了: {}",
        "log_inst_err": "[X] インストールエラー {}: {}",
        "log_linux": "[!] Linuxでの自動インストールにはパッケージ (.deb/.AppImage) の手動手動起動が必要です。ダウンロード完了。",
        "log_download_only": "[*] ダウンロードのみモード (インストールなし)。",
        "tools_title": "便利なシステムユーティリティ", "tool_cmd": "コマンドプロンプトを開く (CMD)",
        "tool_folder": "ダウンロードフォルダを開く",
        "set_lang": "🌐 インターフェース言語", "set_palette": "🎨 アクセントカラー", "set_theme": "☀️ テーマモード",
        "theme_system": "システム", "theme_dark": "ダーク", "theme_light": "ライト",
        "about_desc": "DinryX HUB — ソフトウェアダウンロードマネージャー ({}).\n公式インストーラーを自動的にダウンロードしてインストールします。",
        "about_author": "• 開発者: RAIDDARK / DinryX Team\n• アプリバージョン: ",
        "btn_site": "🌐 公式ウェブサイト / アップデート",
        "update_found": "アップデート {} が利用可能です！",
        "cat_utils": "📦 ユーティリティ＆解凍", "cat_browsers": "🌐 ブラウザ＆インターネット",
        "cat_dev": "💻 開発＆コード", "cat_media": "🎨 グラフィック＆メディア",
        "cat_games": "🎮 ゲーム＆ランチャー", "cat_chats": "💬 メッセンジャー",
    },
}

COLOR_PALETTES = {
    "Red Edition": "#ff4b2b",
    "Blue Neon": "#1f6aa5",
    "Green Cyber": "#10b981",
    "Purple Violet": "#9b59b6",
}

PROGRAMS_WINDOWS = [
    {"name": "7-Zip", "category": "cat_utils", "desc": "Популярний і швидкий архіватор.", "url": "https://www.7-zip.org/a/7z2408-x64.exe", "file": "7z2408-x64.exe", "silent_args": "/S"},
    {"name": "WinRAR", "category": "cat_utils", "desc": "Класичний архіватор.", "url": "https://www.rarlab.com/rar/winrar-x64-621.exe", "file": "winrar-x64-621.exe", "silent_args": "/S"},
    {"name": "Google Chrome", "category": "cat_browsers", "desc": "Веб-браузер від Google.", "url": "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi", "file": "GoogleChromeStandaloneEnterprise64.msi", "silent_args": "/quiet /qn /norestart"},
    {"name": "Notepad++", "category": "cat_dev", "desc": "Зручний текстовий редактор.", "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6.2/npp.8.6.2.Installer.x64.exe", "file": "npp.8.6.2.Installer.x64.exe", "silent_args": "/S"},
    {"name": "Sublime Text", "category": "cat_dev", "desc": "Швидкий редактор коду.", "url": "https://download.sublimetext.com/Sublime%20Text%20Build%204181%20x64%20Setup.exe", "file": "sublime_text_setup.exe", "silent_args": "/VERYSILENT /NORESTART"},
    {"name": "GIMP", "category": "cat_media", "desc": "Безкоштовний графічний редактор.", "url": "https://download.gimp.org/pub/gimp/v3.0/windows/gimp-3.0.0-setup.exe", "file": "gimp-setup.exe", "silent_args": '/ALLUSERS /DIR="C:\\Program Files\\GIMP 3" /SILENT'},
    {"name": "LibreOffice", "category": "cat_utils", "desc": "Офісний пакет для документів.", "url": "https://download.documentfoundation.org/libreoffice/stable/26.2.4/win/x86_64/LibreOffice_26.2.4_Win_x86-64.msi", "file": "LibreOffice_Win_x86-64.msi", "silent_args": "/quiet /qn /norestart"},
    {"name": "Heroic Games Launcher", "category": "cat_games", "desc": "Лаунчер Epic Games та GOG.", "url": "https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/v2.22.0/Heroic-2.22.0-Setup-x64.exe", "file": "Heroic-Setup-x64.exe", "silent_args": "/S"},
    {"name": "Steam", "category": "cat_games", "desc": "Ігрова платформа.", "url": "https://cdn.fastly.steamstatic.com/client/installer/SteamSetup.exe", "file": "SteamSetup.exe", "silent_args": "/S"},
    {"name": "Game Jolt", "category": "cat_games", "desc": "Ігрова платформа для фанатських ігор.", "url": "https://download.gamejolt.net/7d25fe6eb3c6d11048a290a47084eb3165aa04fd4152ca4e63bedb87976bd77d,1788506930,7/data/games/5/162/362412/files/66bc359fe3e14/gamejoltclientsetup.exe", "file": "gamejoltclientsetup.exe", "silent_args": ""},
    {"name": "Playnite", "category": "cat_games", "desc": "Ігровий Лаунчер для платформ", "url": "https://playnite.link/download/PlayniteInstaller.exe", "file": "PlayniteInstaller.exe", "silent_args": "/S"},
    {"name": "ORACLE | Java JDK 26", "category": "cat_utils", "desc": "Середовище та інструменти Java.", "url": "https://download.oracle.com/java/26/latest/jdk-26_windows-x64_bin.exe", "file": "jdk-26_windows-x64_bin.exe", "silent_args": ""},
    {"name": "Discord", "category": "cat_chats", "desc": "Месенджер для геймерів.", "url": "https://dl.discordapp.net/distro/app/stable/win/x64/1.0.9152/DiscordSetup.exe", "file": "DiscordSetup.exe", "silent_args": "-s"},
    {"name": "Telegram Desktop", "category": "cat_chats", "desc": "Месенджер для ПК.", "url": "https://telegram.org/dl/desktop/win64", "file": "tsetup-x64.exe", "silent_args": "/VERYSILENT /NORESTART"},
    {"name": "Mozilla Firefox", "category": "cat_browsers", "desc": "Швидкий і приватний браузер.", "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=uk", "file": "FirefoxSetup.exe", "silent_args": "-ms"},
    {"name": "Opera", "category": "cat_browsers", "desc": "Браузер зі вбудованим VPN та месенджерами.", "url": "https://get.geo.opera.com/pub/opera/desktop/108.0.5067.43/win/Opera_108.0.5067.43_Setup_x64.exe", "file": "OperaSetup.exe", "silent_args": "/silent /allusers=1"},
    {"name": "Brave", "category": "cat_browsers", "desc": "Фокус на конфіденційність та блокування реклами.", "url": "https://laptop-updates.brave.com/latest/winx64", "file": "BraveBrowserSetup.exe", "silent_args": "--silent --install"},
    {"name": "Zoom", "category": "cat_chats", "desc": "Програма для відеоконференцій та навчання.", "url": "https://zoom.us/client/latest/ZoomInstallerFull.exe", "file": "ZoomInstallerFull.exe", "silent_args": "/silent"},
    {"name": "Viber", "category": "cat_chats", "desc": "Десктопна версія месенджера Viber.", "url": "https://download.cdn.viber.com/desktop/windows/ViberSetup.exe", "file": "ViberSetup.exe", "silent_args": "/verysilent /norestart"},
    {"name": "Visual Studio Code", "category": "cat_dev", "desc": "Легкий редактор коду.", "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user", "file": "VSCodeSetup.exe", "silent_args": "/verysilent /mergetasks=!runcode"},
    {"name": "HWMonitor", "category": "cat_utils", "desc": "Моніторинг температури та стану заліза ПК.", "url": "https://download.cpuid.com/hwmonitor/hwmonitor_1.53.exe", "file": "hwmonitor_setup.exe", "silent_args": "/VERYSILENT"},
    {"name": "Sysinternals Suite", "category": "cat_utils", "desc": "Набір експертних системних утиліт від Microsoft.", "url": "https://live.sysinternals.com/SysinternalsSuite.zip", "file": "SysinternalsSuite.zip", "silent_args": ""},
    {"name": "OBS Studio", "category": "cat_media", "desc": "Програма для стрімінгу та запису екрана.", "url": "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-30.0.2-Full-Installer-x64.exe", "file": "OBSSetup.exe", "silent_args": "/S"},
    {"name": "Spotify", "category": "cat_media", "desc": "Музичний стрімінговий сервіс.", "url": "https://download.scdn.co/SpotifySetup.exe", "file": "SpotifySetup.exe", "silent_args": "/silent"},
]

PROGRAMS_LINUX = [
    {"name": "Google Chrome (.deb)", "category": "cat_browsers", "desc": "Веб-браузер від Google.", "url": "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", "file": "google-chrome-stable_current_amd64.deb", "silent_args": ""},
    {"name": "Mozilla Firefox (.tar.bz2)", "category": "cat_browsers", "desc": "Швидкий і приватний браузер.", "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=uk", "file": "firefox.tar.bz2", "silent_args": ""},
    {"name": "Heroic Games Launcher (.AppImage)", "category": "cat_games", "desc": "Лаунчер Epic Games та GOG.", "url": "https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/v2.22.0/Heroic-2.22.0-Linux-x86_64.AppImage", "file": "Heroic-Linux-x86_64.AppImage", "silent_args": ""},
    {"name": "Steam (.deb)", "category": "cat_games", "desc": "Ігрова платформа.", "url": "https://cdn.fastly.steamstatic.com/client/installer/steam.deb", "file": "steam_latest.deb", "silent_args": ""},
    {"name": "ORACLE | Java JDK 26 (.deb)", "category": "cat_utils", "desc": "Середовище Java.", "url": "https://download.oracle.com/java/26/latest/jdk-26_linux-x64_bin.deb", "file": "jdk-26_linux-x64_bin.deb", "silent_args": ""},
    {"name": "Discord (.deb)", "category": "cat_chats", "desc": "Месенджер.", "url": "https://discord.com/api/download?platform=linux&format=deb", "file": "discord_latest.deb", "silent_args": ""},
    {"name": "Telegram Desktop", "category": "cat_chats", "desc": "Офіційний клієнт Telegram.", "url": "https://telegram.org/dl/desktop/linux", "file": "tsetup.tar.xz", "silent_args": ""},
    {"name": "Visual Studio Code (.deb)", "category": "cat_dev", "desc": "Популярний редактор коду.", "url": "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64", "file": "vscode.deb", "silent_args": ""},
    {"name": "Stacer", "category": "cat_utils", "desc": "Моніторинг та обслуговування Linux.", "url": "https://github.com/oguzhaninan/Stacer/releases/download/v1.1.0/Stacer-1.1.0-x64.AppImage", "file": "Stacer-1.1.0-x64.AppImage", "silent_args": ""},
    {"name": "qBittorrent", "category": "cat_utils", "desc": "Зручний торрент-клієнт.", "url": "https://sourceforge.net/projects/qbittorrent/", "file": "qbittorrent", "silent_args": ""},
    {"name": "Signal Desktop (.deb)", "category": "cat_chats", "desc": "Захищений месенджер.", "url": "https://updates.signal.org/desktop/apt/pools/main/s/signal-desktop/signal-desktop_7.3.0_amd64.deb", "file": "signal-desktop.deb", "silent_args": ""},
    {"name": "Element (.deb)", "category": "cat_chats", "desc": "Децентралізований месенджер.", "url": "https://packages.element.io/debian/pool/main/e/element-desktop/element-desktop_1.11.59_amd64.deb", "file": "element.deb", "silent_args": ""},
    {"name": "Sublime Text (.deb)", "category": "cat_dev", "desc": "Текстовий редактор.", "url": "https://download.sublimetext.com/sublime-text_build-4181_amd64.deb", "file": "sublime-text.deb", "silent_args": ""},
    {"name": "BleachBit (.deb)", "category": "cat_utils", "desc": "Очищення системи від сміття.", "url": "https://sourceforge.net/projects/bleachbit/files/bleachbit/4.6.0/bleachbit_4.6.0-0_all.deb", "file": "bleachbit.deb", "silent_args": ""},
    {"name": "Lutris", "category": "cat_games", "desc": "Платформа для запуску ігор у Linux.", "url": "https://lutris.net/", "file": "lutris", "silent_args": ""},
]

PROGRAMS = PROGRAMS_WINDOWS if CURRENT_OS == "Windows" else PROGRAMS_LINUX

def load_config():
    default = {
        "accent_palette": "Green Cyber",
        "language": "Українська",
        "theme": "System",
        "favorites": [],
        "silent": True,
        "autoclean": False,
    }
    if not os.path.exists(CONFIG_FILE):
        return default
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default
        default.update(data)
        if default["accent_palette"] not in COLOR_PALETTES:
            default["accent_palette"] = "Green Cyber"
        if default["language"] not in TRANSLATIONS:
            default["language"] = "Українська"
        if default["theme"] not in ["System", "Dark", "Light"]:
            default["theme"] = "System"
        return default
    except Exception as exc:
        print(f"Config read error: {exc}")
        return default


def save_config(config):
    try:
        tmp = CONFIG_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        os.replace(tmp, CONFIG_FILE)
    except Exception as exc:
        print(f"Config save error: {exc}")


DARK_STYLE = """
QWidget {
    background-color: #0b0913;
    color: #ffffff;
    font-family: 'Segoe UI';
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #1f1b2e;
    background-color: #0b0913;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #120f1d;
    color: #a09cb0;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: @ACCENT@;
    color: #ffffff;
    font-weight: bold;
}
QPushButton {
    background-color: #161224;
    border: 1px solid #221c35;
    border-radius: 8px;
    color: white;
    padding: 8px 15px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #1f1b2e;
    border: 1px solid @ACCENT@;
}
QPushButton:disabled {
    color: #6c6580;
}
QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #332947;
    background: #161224;
}
QCheckBox::indicator:checked {
    background: @ACCENT@;
    border: 1px solid @ACCENT@;
}
QTextEdit {
    background-color: #07050d;
    border: 1px solid #1f1b2e;
    border-radius: 6px;
    color: @ACCENT@;
    font-family: 'Consolas', 'Courier New';
    font-size: 12px;
}
QProgressBar {
    border: 1px solid #1f1b2e;
    border-radius: 5px;
    background: #07050d;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background-color: @ACCENT@;
    border-radius: 4px;
}
QComboBox {
    background-color: #161224;
    border: 1px solid #221c35;
    border-radius: 6px;
    padding: 6px 10px;
    color: #ffffff;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #161224;
    color: #ffffff;
    selection-background-color: @ACCENT@;
    border: 1px solid #221c35;
}
QScrollArea { background: transparent; border: none; }
QToolButton {
    background-color: #161224;
    border: 1px solid #221c35;
    border-radius: 6px;
    color: #f39c12;
    padding: 2px 6px;
}
QToolButton:hover { border: 1px solid @ACCENT@; }
"""

LIGHT_STYLE = """
QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI';
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    background-color: #f8fafc;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #e2e8f0;
    color: #64748b;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: @ACCENT@;
    color: #ffffff;
    font-weight: bold;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    color: #1e293b;
    padding: 8px 15px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #f1f5f9;
    border: 1px solid @ACCENT@;
}
QPushButton:disabled {
    color: #94a3b8;
}
QCheckBox {
    spacing: 8px;
    color: #334155;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: @ACCENT@;
    border: 1px solid @ACCENT@;
}
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #0f172a;
    font-family: 'Consolas', 'Courier New';
    font-size: 12px;
}
QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    background: #ffffff;
    text-align: center;
    color: #1e293b;
}
QProgressBar::chunk {
    background-color: @ACCENT@;
    border-radius: 4px;
}
QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #1e293b;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1e293b;
    selection-background-color: @ACCENT@;
    border: 1px solid #cbd5e1;
}
QScrollArea { background: transparent; border: none; }
QToolButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #d97706;
    padding: 2px 6px;
}
QToolButton:hover { border: 1px solid @ACCENT@; }
"""


def build_stylesheet(accent, is_dark):
    base = DARK_STYLE if is_dark else LIGHT_STYLE
    return base.replace("@ACCENT@", accent)


class DownloadInstallWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, apps_to_process, options, tr):
        super().__init__()
        self.apps_to_process = apps_to_process
        self.options = options
        self.tr = tr

    def download_file(self, app):
        url = app["url"]
        filename = app["file"]
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        self.log_signal.emit(self.tr("log_dl_start").format(app["name"]))
        try:
            # Маскуємо запит під повноцінний браузер
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Referer": "https://llaun.ch/"
            }
            response = requests.get(url, headers=headers, stream=True, timeout=HTTP_TIMEOUT, allow_redirects=True)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            self.log_signal.emit(self.tr("log_dl_ok").format(app["name"]))
            return app, filepath
        except Exception as e:
            self.log_signal.emit(self.tr("log_dl_err").format(app["name"], str(e)))
            return app, None

    def run(self):
        if not self.apps_to_process:
            self.log_signal.emit(self.tr("log_no_apps"))
            self.finished_signal.emit()
            return

        if self.options.get("download_only"):
            self.log_signal.emit(self.tr("log_download_only"))

        downloaded_apps = []
        with ThreadPoolExecutor(max_workers=MAX_DOWNLOADS) as executor:
            futures = {executor.submit(self.download_file, app): app for app in self.apps_to_process}
            completed_count = 0

            for future in as_completed(futures):
                app, filepath = future.result()
                if filepath:
                    downloaded_apps.append((app, filepath))
                completed_count += 1
                progress = int((completed_count / len(self.apps_to_process)) * 50)
                self.progress_signal.emit(progress)

        if not self.options.get("download_only"):
            if CURRENT_OS == "Windows":
                self.log_signal.emit(self.tr("log_start_inst"))
                total = len(downloaded_apps)
                use_silent = self.options.get("silent", True)
                autoclean = self.options.get("autoclean", False)

                for idx, (app, filepath) in enumerate(downloaded_apps):
                    self.log_signal.emit(self.tr("log_inst").format(app["name"]))
                    silent_args = app.get("silent_args", "")

                    try:
                        if use_silent and silent_args:
                            if filepath.endswith(".msi"):
                                cmd = 'msiexec /i "{}" {}'.format(filepath, silent_args)
                            else:
                                cmd = '"{}" {}'.format(filepath, silent_args)
                            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                                       stderr=subprocess.STDOUT, text=True)
                            process.wait()
                        else:
                            if filepath.endswith(".msi"):
                                subprocess.Popen('msiexec /i "{}"'.format(filepath), shell=True)
                            else:
                                os.startfile(filepath)
                        self.log_signal.emit(self.tr("log_inst_ok").format(app["name"]))

                        if autoclean:
                            try:
                                os.remove(filepath)
                            except OSError:
                                pass
                    except Exception as e:
                        self.log_signal.emit(self.tr("log_inst_err").format(app["name"], str(e)))

                    progress = 50 + int(((idx + 1) / max(total, 1)) * 50)
                    self.progress_signal.emit(progress)
            else:
                for app, filepath in downloaded_apps:
                    if filepath.endswith(".AppImage"):
                        try:
                            os.chmod(filepath, os.stat(filepath).st_mode | 0o111)
                        except OSError:
                            pass
                self.log_signal.emit(self.tr("log_linux"))

        self.progress_signal.emit(100)
        self.finished_signal.emit()


class DinryXPyQtHUB(QWidget):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self.current_lang = self.config_data["language"]
        self.favorites_filter = False
        self.app_checkboxes = {}
        self.worker = None
        self.initUI()
        self.check_for_updates_async()

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["Українська"]).get(key, key)

    def accent(self):
        return COLOR_PALETTES.get(self.config_data["accent_palette"], COLOR_PALETTES["Green Cyber"])

    def is_dark_theme(self):
        theme_setting = self.config_data.get("theme", "System")
        if theme_setting == "Dark":
            return True
        elif theme_setting == "Light":
            return False
        else:
            if CURRENT_OS == "Windows":
                try:
                    import winreg
                    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return value == 0
                except Exception:
                    pass
            palette = QApplication.palette()
            color = palette.color(palette.Window)
            return color.lightness() < 128

    def initUI(self):
        self.setWindowTitle(f"DinryX HUB [{CURRENT_OS}]")
        self.setGeometry(100, 100, 950, 700)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()
        self.title_label = QLabel(f"DinryX HUB Installer [{CURRENT_OS}]")
        self.version_label = QLabel(f"{CURRENT_VERSION} Ultimate")
        self.version_label.setStyleSheet("color: #6c6580; font-size: 11px;")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.version_label)
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.apply_styles()
        self.rebuild_tabs()

        self._cached_is_dark = self.is_dark_theme()
        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_system_theme_update)
        self.theme_check_timer.start(2000)

    def check_system_theme_update(self):
        if self.config_data.get("theme", "System") == "System":
            current_dark = self.is_dark_theme()
            if current_dark != self._cached_is_dark:
                self._cached_is_dark = current_dark
                self.apply_styles()
                self.rebuild_tabs()

    def apply_styles(self):
        accent = self.accent()
        is_dark = self.is_dark_theme()
        self.setStyleSheet(build_stylesheet(accent, is_dark))
        
        sub_color = "#6c6580" if is_dark else "#64748b"
        self.title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {accent};")
        self.version_label.setStyleSheet(f"color: {sub_color}; font-size: 11px;")

    def rebuild_tabs(self):
        while self.tabs.count():
            w = self.tabs.widget(0)
            self.tabs.removeTab(0)
            w.deleteLater()

        self.tab_apps = QWidget()
        self.tab_tools = QWidget()
        self.tab_settings = QWidget()
        self.tab_about = QWidget()

        self.tabs.addTab(self.tab_apps, self.t("tab_apps"))
        self.tabs.addTab(self.tab_tools, self.t("tab_tools"))
        self.tabs.addTab(self.tab_settings, self.t("tab_settings"))
        self.tabs.addTab(self.tab_about, self.t("tab_about"))

        self.build_apps_tab()
        self.build_tools_tab()
        self.build_settings_tab()
        self.build_about_tab()

    def build_apps_tab(self):
        layout = QHBoxLayout(self.tab_apps)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        ctrl_row = QHBoxLayout()
        self.btn_select_all = QPushButton(self.t("btn_select_all"))
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_reset = QPushButton(self.t("btn_reset"))
        self.btn_reset.clicked.connect(self.reset_selection)
        self.btn_fav = QPushButton(self.t("btn_fav"))
        self.btn_fav.setCheckable(True)
        self.btn_fav.setChecked(self.favorites_filter)
        self.btn_fav.clicked.connect(self.toggle_favorites_filter)
        ctrl_row.addWidget(self.btn_select_all)
        ctrl_row.addWidget(self.btn_reset)
        ctrl_row.addStretch()
        ctrl_row.addWidget(self.btn_fav)
        left_layout.addLayout(ctrl_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.fill_programs_list()

        scroll.setWidget(self.scroll_content)
        left_layout.addWidget(scroll)
        layout.addWidget(left_panel, stretch=2)

        right_layout = QVBoxLayout()

        self.console_lbl = QLabel(self.t("console_title"))
        sub_color = "#a09cb0" if self.is_dark_theme() else "#475569"
        self.console_lbl.setStyleSheet(f"font-weight: bold; color: {sub_color};")
        right_layout.addWidget(self.console_lbl)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("...")
        right_layout.addWidget(self.console_output)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)

        self.cb_silent = QCheckBox(self.t("cb_silent"))
        self.cb_silent.setChecked(self.config_data.get("silent", True))
        self.cb_silent.toggled.connect(lambda v: self.save_option("silent", v))
        right_layout.addWidget(self.cb_silent)

        self.cb_clean = QCheckBox(self.t("cb_clean"))
        self.cb_clean.setChecked(self.config_data.get("autoclean", False))
        self.cb_clean.toggled.connect(lambda v: self.save_option("autoclean", v))
        right_layout.addWidget(self.cb_clean)

        self.btn_install = QPushButton(self.t("btn_start"))
        accent = self.accent()
        self.btn_install.setStyleSheet(
            f"background-color: {accent}; color: white; font-weight: bold; padding: 12px; font-size: 14px;"
        )
        self.btn_install.clicked.connect(self.start_installation)
        right_layout.addWidget(self.btn_install)

        layout.addLayout(right_layout, stretch=3)

    def fill_programs_list(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        self.app_checkboxes.clear()

        favorites_list = self.config_data.get("favorites", [])

        categories = {}
        for app in PROGRAMS:
            if self.favorites_filter and app["name"] not in favorites_list:
                continue
            categories.setdefault(app["category"], []).append(app)

        accent = self.accent()
        for cat_key, apps in categories.items():
            cat_lbl = QLabel(self.t(cat_key))
            cat_lbl.setStyleSheet(f"font-weight: bold; color: {accent}; font-size: 14px; margin-top: 10px;")
            self.scroll_layout.addWidget(cat_lbl)

            for app in apps:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(0, 0, 0, 0)

                cb = QCheckBox(f"{app['name']} — {app['desc']}")

                fav_btn = QToolButton()
                is_fav = app["name"] in favorites_list
                fav_btn.setText("★" if is_fav else "☆")
                fav_btn.setFixedSize(30, 24)
                fav_btn.setStyleSheet("color: #f39c12;" if is_fav else "color: #888888;")
                fav_btn.clicked.connect(lambda _, n=app["name"]: self.toggle_favorite(n))

                dl_btn = QToolButton()
                dl_btn.setText("↓")
                dl_btn.setFixedSize(30, 24)
                dl_btn.setToolTip("Download only")
                dl_btn.clicked.connect(lambda _, a=app: self.download_single(a))

                row.addWidget(cb)
                row.addStretch()
                row.addWidget(fav_btn)
                row.addWidget(dl_btn)
                self.scroll_layout.addWidget(row_widget)

                self.app_checkboxes[app["name"]] = (cb, app)

        self.scroll_layout.addStretch()

    def toggle_favorite(self, prog_name):
        favs = self.config_data.setdefault("favorites", [])
        if prog_name in favs:
            favs.remove(prog_name)
        else:
            favs.append(prog_name)
        save_config(self.config_data)
        self.fill_programs_list()

    def toggle_favorites_filter(self):
        self.favorites_filter = self.btn_fav.isChecked()
        self.fill_programs_list()

    def select_all(self):
        for cb, _ in self.app_checkboxes.values():
            cb.setChecked(True)

    def reset_selection(self):
        for cb, _ in self.app_checkboxes.values():
            cb.setChecked(False)

    def save_option(self, key, value):
        self.config_data[key] = value
        save_config(self.config_data)

    def start_installation(self):
        selected = []
        for cb, app_data in self.app_checkboxes.values():
            if cb.isChecked():
                selected.append(app_data)

        if not selected:
            QMessageBox.warning(self, "⚠", self.t("warn_none"))
            return

        self.run_worker(selected, download_only=False)

    def download_single(self, app):
        self.run_worker([app], download_only=True)

    def run_worker(self, apps, download_only):
        if self.worker is not None and self.worker.isRunning():
            return
        self.btn_install.setEnabled(False)
        self.console_output.clear()
        self.progress_bar.setValue(0)

        options = {
            "silent": self.cb_silent.isChecked(),
            "autoclean": self.cb_clean.isChecked(),
            "download_only": download_only,
        }
        self.worker = DownloadInstallWorker(apps, options, self.t)
        self.worker.log_signal.connect(self.append_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.installation_finished)
        self.worker.start()

    def append_log(self, text):
        self.console_output.append(text)
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

    def installation_finished(self):
        self.btn_install.setEnabled(True)
        QMessageBox.information(self, self.t("done_title"), self.t("done_msg"))

    def build_tools_tab(self):
        layout = QVBoxLayout(self.tab_tools)
        layout.setAlignment(Qt.AlignTop)

        lbl = QLabel(self.t("tools_title"))
        lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {self.accent()}; margin-bottom: 10px;")
        layout.addWidget(lbl)

        def run_local_tool(filename):
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            path = os.path.join(base_dir, filename)
            if CURRENT_OS == "Windows":
                try:
                    os.startfile(path)
                except Exception as e:
                    print(f"Помилка запуску {filename}: {e}")

        tools = [
            (self.t("tool_cmd"), lambda: subprocess.Popen(["start", "cmd"], shell=True) if CURRENT_OS == "Windows" else None),
            (self.t("tool_folder"), lambda: os.startfile(DOWNLOAD_DIR) if CURRENT_OS == "Windows" else subprocess.Popen(["xdg-open", DOWNLOAD_DIR])),
            ("SU.exe", lambda: run_local_tool("SU.exe")),
            ("SystemInformer.exe", lambda: run_local_tool("SystemInformer.exe")),
            ("UninstallTool.exe", lambda: run_local_tool("UninstallTool.exe")),
        ]

        for text, action in tools:
            btn = QPushButton(text)
            btn.setFixedHeight(60)
            btn.setMaximumWidth(700)
            btn.clicked.connect(action)
            layout.addWidget(btn, alignment=Qt.AlignCenter)

    def build_settings_tab(self):
        layout = QVBoxLayout(self.tab_settings)
        layout.setAlignment(Qt.AlignTop)

        self.lbl_lang = QLabel(self.t("set_lang"))
        self.lbl_lang.setStyleSheet(f"font-weight: bold; color: {self.accent()};")
        layout.addWidget(self.lbl_lang)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(list(TRANSLATIONS.keys()))
        self.combo_lang.setCurrentText(self.current_lang)
        self.combo_lang.currentTextChanged.connect(self.change_language)
        layout.addWidget(self.combo_lang)

        layout.addSpacing(15)

        self.lbl_theme = QLabel(self.t("set_theme"))
        self.lbl_theme.setStyleSheet(f"font-weight: bold; color: {self.accent()};")
        layout.addWidget(self.lbl_theme)
        
        self.combo_theme = QComboBox()
        self.theme_map = {
            self.t("theme_system"): "System",
            self.t("theme_dark"): "Dark",
            self.t("theme_light"): "Light"
        }
        inverse_theme_map = {"System": self.t("theme_system"), "Dark": self.t("theme_dark"), "Light": self.t("theme_light")}
        
        self.combo_theme.addItems(list(self.theme_map.keys()))
        current_theme_key = self.config_data.get("theme", "System")
        self.combo_theme.setCurrentText(inverse_theme_map.get(current_theme_key, self.t("theme_system")))
        self.combo_theme.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.combo_theme)

        layout.addSpacing(15)

        self.lbl_palette = QLabel(self.t("set_palette"))
        self.lbl_palette.setStyleSheet(f"font-weight: bold; color: {self.accent()};")
        layout.addWidget(self.lbl_palette)
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(list(COLOR_PALETTES.keys()))
        self.combo_palette.setCurrentText(self.config_data["accent_palette"])
        self.combo_palette.currentTextChanged.connect(self.change_palette)
        layout.addWidget(self.combo_palette)

        layout.addStretch()

    def change_language(self, lang):
        if lang == self.current_lang:
            return
        self.current_lang = lang
        self.config_data["language"] = lang
        save_config(self.config_data)
        if self.worker is not None and self.worker.isRunning():
            return
        self.rebuild_tabs()

    def change_theme(self, theme_label):
        theme_code = self.theme_map.get(theme_label, "System")
        if theme_code == self.config_data.get("theme"):
            return
        self.config_data["theme"] = theme_code
        save_config(self.config_data)
        self.apply_styles()
        self.rebuild_tabs()

    def change_palette(self, palette_name):
        if palette_name == self.config_data["accent_palette"]:
            return
        self.config_data["accent_palette"] = palette_name
        save_config(self.config_data)
        self.apply_styles()
        self.rebuild_tabs()

    def build_about_tab(self):
        layout = QVBoxLayout(self.tab_about)
        layout.setAlignment(Qt.AlignTop)

        desc = QLabel(self.t("about_desc").format(CURRENT_OS))
        layout.addWidget(desc)

        sub_color = "#6c6580" if self.is_dark_theme() else "#64748b"
        author = QLabel(self.t("about_author") + CURRENT_VERSION)
        author.setStyleSheet(f"color: {sub_color}; margin-top: 10px;")
        layout.addWidget(author)

        btn_site = QPushButton(self.t("btn_site"))
        btn_site.setStyleSheet(f"color: {self.accent()}; border: 1px solid {self.accent()}; background: transparent;")
        btn_site.clicked.connect(lambda: webbrowser.open(SITE_URL))
        layout.addWidget(btn_site)

        layout.addStretch()

    def check_for_updates_async(self):
        threading.Thread(target=self._check_updates_logic, daemon=True).start()

    def _check_updates_logic(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            res = requests.get(url, timeout=5, headers={"User-Agent": "DinryX-HUB"})
            res.raise_for_status()
            latest = res.json().get("tag_name", "").strip()
            if latest and self._version_tuple(latest) > self._version_tuple(CURRENT_VERSION):
                self.version_label.setText(self.t("update_found").format(latest))
                accent = self.accent()
                self.version_label.setStyleSheet(f"color: {accent}; font-size: 11px; font-weight: bold;")
        except Exception:
            pass

    @staticmethod
    def _version_tuple(value):
        nums = []
        for part in value.lower().lstrip("v").split("."):
            digits = "".join(c for c in part if c.isdigit())
            nums.append(int(digits or 0))
        return tuple(nums + [0] * (3 - len(nums)))[:3]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DinryXPyQtHUB()
    window.show()
    sys.exit(app.exec_())
