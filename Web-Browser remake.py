import os
import shutil
import sqlite3
import sys

import requests
from PyQt5 import QtWidgets
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit

from Custom_widgets import Settings_combobox, Settings_switch, Settings_button, Settings_interactive


def is_url_correct(url):
    try:
        request = requests.get(url)
        if request.status_code == 200:
            return True
    except:
        return False


class WebEnginePage(QWebEnginePage):  # при клике на ссылку она открывается в новой вкладке
    external_window = None

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        self.url = url
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            if not self.external_window:
                browser.new_tab(str(self.url).split("'")[1])
                browser.update_url()
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.iniUI()

    def iniUI(self):
        self.setGeometry(100, 100, 1000, 600)
        self.start_url = ""
        self.initUI()

    def initUI(self):
        self.tabBarClicked.connect(self.print)
        self.theme = "themes/black_theme"
        self.load_theme()
        self.icons_urls_cash = []
        self.check_list = []
        self.icons_count = 0
        self.setWindowIcon(QIcon("DarkInfinity.png"))
        self.all_tabs = []
        self.setWindowTitle("Web-Browser")
        self.tabCloseRequested.connect(self.close_tab)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setStyleSheet(f"""QTabWidget::pane {{
                                border: 0;
                            }}
                            QTabBar::Tab {{
                                background-color: rgba(32,33,36,255);
                                color: rgb(209, 209, 209);
                                height: 30px;
                            }}
                            QTabBar::Tab:hover {{
                                color: white;
                            }}
                            QTabBar::Tab:selected {{background-color: rgba(53,54,58,255);
                            }}
                            QTabBar {{
                                background-color: rgba(32,33,36,255);}}
                            QTabBar::close-button {{
                                image: url({self.theme}/close.png)
                            }}""")
        # self.setStyleSheet("""background-color: rgba(53,54,58,255);""")
        # self.setStyleSheet("""QTabWidget::pane { border: 0; }""")  # убрать пограничные линии
        self.new_tab("https://www.google.com")
        self.tabBarDoubleClicked.connect(lambda add_new_tab: self.new_tab("https://www.google.com"))
        self.connect_bd()

    def new_tab(self, url):
        self.tab_main_window()
        self.web = QWebEngineView()
        # self.web.loadFinished.connect(lambda y: print(self.web.page().iconUrl()))
        self.web.setPage(WebEnginePage(self))
        # self.web.page().setAudioMuted(True)
        self.web.load(QUrl(url))
        self.web.urlChanged.connect(self.update_url)
        self.web.iconUrlChanged.connect(lambda y: self.download_icons())
        self.web.titleChanged.connect(self.adjustTitle)

        self.toolbar = QToolBar("Navigation", self.mainwindow)
        self.toolbar.setStyleSheet("""
            QToolBar QToolButton:hover {
                background-color: rgba(41,42,45,255);
                height: 5px;
                border-radius: 4px;
            }""")
        self.toolbar.setAllowedAreas(Qt.TopToolBarArea)
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(22, 22))
        self.mainwindow.addToolBar(self.toolbar)

        # self.toolbar.setStyleSheet("""background-color: grey;""")

        self.go_back = QAction(self.icon_back, "go back", self)
        self.toolbar.addAction(self.go_back)

        self.go_forward = QAction(self.icon_forward, "go forward", self)
        self.toolbar.addAction(self.go_forward)

        self.restart_page = QAction(self.icon_restart, "restart page", self)
        self.toolbar.addAction(self.restart_page)

        self.home_page = QAction(self.icon_home, "home page", self)
        self.toolbar.addAction(self.home_page)

        self.search_bar = QLineEdit("")
        self.search_bar.returnPressed.connect(self.url_navigate)
        self.search_bar.setStyleSheet("""
                QLineEdit {
                    border-radius: 10px;
                    background-color: rgba(32,33,36,255);
                    color: white;
                    padding: 8px;
                    font: 12px/14px sans-serif
                    }
                QLineEdit:focus {
                    border: 1px solid rgba(66,133,244,255);
                }
                QLineEdit:hover {
                    background-color: rgba(41,42,45,255);
                }
                """)

        self.settings_menu = QMenu("Настройки", self)
        self.settings_menu.setStyleSheet("""
        QMenu {
            background: rgba(41,42,45,255);
            color: rgb(209, 209, 209);
        }
        QMenu:selected {
            background: rgba(32,33,36,255);
        }
        """)

        self.newtab = QAction("Новая вкладка", self)
        self.newtab.triggered.connect(lambda add_new_tab: self.new_tab("https://www.google.com"))
        self.settings_menu.addAction(self.newtab)

        self.new_window = QAction("Новое окно", self)
        self.new_window.triggered.connect(open_new_window)
        self.settings_menu.addAction(self.new_window)

        self.new_incognito = QAction("Новая вкладка инкогнито", self)
        self.settings_menu.addAction(self.new_incognito)
        self.settings_menu.addSection("1")

        self.history = QAction("История", self)
        self.history.triggered.connect(self.history_tab)
        self.settings_menu.addAction(self.history)

        self.download = QAction("Загрузки", self)
        self.settings_menu.addAction(self.download)

        self.markers = QAction("Закладки", self)
        self.settings_menu.addAction(self.markers)

        self.settings_menu.addSection("2")
        self.browser_settings = QAction("Настройки", self)
        self.browser_settings.triggered.connect(self.settings_tab)
        self.settings_menu.addAction(self.browser_settings)

        self.info = QMenu("Справка", self)
        self.info.setStyleSheet("""
        QMenu {
            background: rgba(41,42,45,255);
            color: rgb(209, 209, 209);
        }
        QMenu:selected {
            background: rgba(32,33,36,255);
        }
        """)
        self.settings_menu.addMenu(self.info)

        self.about = QAction("О браузере", self)
        self.info.addAction(self.about)

        self.support = QAction("Поддержка", self)
        self.info.addAction(self.support)

        self.news = QAction("Что нового ?", self)
        self.info.addAction(self.news)

        self.settings = QToolButton(self)
        self.settings.setPopupMode(QToolButton.InstantPopup)
        self.settings.setIcon(QIcon('icons/settings.png'))
        self.settings.setMenu(self.settings_menu)
        self.toolbar.addWidget(self.search_bar)
        self.toolbar.addWidget(self.settings)

        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.web)

        self.addTab(self.mainwindow, self.web.title())

        self.all_tabs.append(self.web)
        self.setCurrentIndex(len(self.all_tabs) - 1)

    def settings_tab(self):
        self.tab_main_window()
        self.mainwindow.setStyleSheet("""
        QMainWindow {
            background-color: rgba(41,42,45,255);
        }
        QPushButton {
            color: rgb(209, 209, 209);
            background: rgba(53,54,58,255);
            align: left;
            padding: 20px;
            font-size: 15px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background: rgba(32,33,36,255);
        }
        QPushButton:pressed {
            border: 2px solid rgba(66,133,244,255);
        }
        QPushButton:checked {
            border: 2px solid rgba(66,133,244,255);
        }
        QScrollArea {
            background-color: rgba(41,42,45,255);
            border: 0;
        }
        """)

        self.search_settings = QLineEdit(self.mainwindow)
        self.search_settings.setStyleSheet("""
                QLineEdit {
                    border-radius: 10px;
                    background-color: rgba(32,33,36,255);
                    color: white;
                    padding: 8px;
                    font: 12px/14px sans-serif
                    }
                QLineEdit:focus {
                    border: 1px solid rgba(66,133,244,255);
                }
                QLineEdit:hover {
                    background-color: rgba(41,42,45,255);
                }
                """)

        self.search_settings.setPlaceholderText("Найти настройки")
        self.main_layout.addWidget(self.search_settings, 0, 0)

        #  Кнопки настроек
        self.all_settings = QScrollArea(self.mainwindow)

        self.settings_buttons_layout = QGridLayout()
        self.settings_buttons_layout.setSpacing(50)

        self.all_settings.setLayout(self.settings_buttons_layout)

        self.account = QPushButton("Аккаунты")
        self.account.setCheckable(True)
        self.account.clicked.connect(self.accounts)
        self.account.setMaximumWidth(500)

        self.settings_buttons_layout.addWidget(self.account)

        self.confidental = QPushButton("Безопасность")
        self.confidental.clicked.connect(self.safety)
        self.confidental.setCheckable(True)
        self.settings_buttons_layout.addWidget(self.confidental)

        self.themes = QPushButton("Внешний вид")
        self.themes.clicked.connect(self.set_theme)
        self.themes.setCheckable(True)

        self.settings_buttons_layout.addWidget(self.themes)

        self.search_system = QPushButton("Поисковая система")
        self.settings_buttons_layout.addWidget(self.search_system)

        self.start_browser = QPushButton("Параметры запуска")
        self.settings_buttons_layout.addWidget(self.start_browser)

        self.layout = QGridLayout()

        # Настройки темы
        self.set_theme_area = QScrollArea(self.mainwindow)
        self.set_theme_area.setStyleSheet("""
            background: rgba(41,42,45,255);
            border-radius: 10px;
        """)
        self.settings_layout = QGridLayout()
        self.set_theme_area.setLayout(self.settings_layout)
        self.main_layout.addWidget(self.set_theme_area, 1, 1)

        # Ночная тема
        self.dark_theme = Settings_switch("Ночная тема")
        self.settings_layout.addWidget(self.dark_theme)

        # Смена языка
        self.language = Settings_combobox("Выбрать язык", ["Русский", "English"])
        self.settings_layout.addWidget(self.language)

        # Показывать кнопку главная страница
        self.home_button = Settings_switch("Главная страница")
        self.settings_layout.addWidget(self.home_button)

        # Другие темы
        self.any_theme = Settings_button("Другие темы", "Перейти к расширениям")
        self.settings_layout.addWidget(self.any_theme)

        # Смена шрифта
        self.font_family = Settings_combobox("Выбрать шрифт", ["Arial", "Times New Roman"])
        self.settings_layout.addWidget(self.font_family)

        self.set_theme_area.hide()
        #

        # Настройки безопасности

        self.set_confidental_area = QScrollArea(self.mainwindow)

        self.settings_layout1 = QGridLayout()
        self.set_confidental_area.setLayout(self.settings_layout1)

        # Кнопка удаления кэша
        self.delete_cash = Settings_button("Очистить данные", "Очистить историю")
        self.delete_cash.add_button("Очистить кэш")
        self.settings_layout1.addWidget(self.delete_cash)

        self.set_confidental_area.hide()

        #

        # Настройки аккаунтов
        self.set_account_area = QScrollArea(self.mainwindow)

        self.settings_layout2 = QGridLayout()
        self.set_account_area.setLayout(self.settings_layout2)

        # Кнопка удаления кэша
        self.account_info = Settings_interactive("Сменить аккаунт", "mrsldavletov@gmail.com", "account.png")
        self.settings_layout2.addWidget(self.account_info)

        self.set_account_area.hide()


        self.space = QScrollArea(self.mainwindow)
        self.layout.addWidget(self.all_settings, 0, 0)
        self.layout.addWidget(self.space, 0, 1)
        self.layout.addWidget(self.set_theme_area, 0, 1)
        self.layout.addWidget(self.set_confidental_area, 0, 1)
        self.layout.addWidget(self.set_account_area, 0, 1)

        self.main_layout.addLayout(self.layout, 1, 0)
        self.addTab(self.mainwindow, "Настройки")

        self.all_tabs.append(self.mainwindow)
        self.setCurrentIndex(len(self.all_tabs) - 1)
        self.setTabIcon(self.currentIndex(), QIcon("icons/settings.png"))

    def history_tab(self):
        self.tab_main_window()

        self.table = QTableWidget(0, 5)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContentsMargins(100, 100, 100, 100)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setMinimumWidth(100)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
        QTableView {
            border: 0px;
            color: white;
        }
        QTableView::item {
            border-bottom: 1px solid;
        }
        """)

        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(20, 20))
        self.rubbish = QAction(QIcon("icons/rubbish.png"), "Delete", self)
        # self.rubbish.triggered.connect(self.delete)
        self.restart = QAction(QIcon("icons/restart_page.png"), "Restart", self)
        # self.restart.triggered.connect(self.restart_table)

        self.toolbar.addAction(self.rubbish)
        self.toolbar.addAction(self.restart)
        # self.toolbar.addWidget(self.choose_all)
        self.toolbar.setStyleSheet("""spacing: 10px;""")

        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.table)

        # self.addToolBar(self.toolbar)
        self.addTab(self.mainwindow, "История запросов")
        self.all_tabs.append(self.web)
        self.setCurrentIndex(len(self.all_tabs) - 1)
        self.output_in_table()

    def tab_main_window(self):
        self.mainwindow = QMainWindow(self)
        self.mainwindow.setStyleSheet("""
        background-color: rgba(53,54,58,255);""")
        self.centralwidget = QWidget()
        self.mainwindow.setCentralWidget(self.centralwidget)
        self.main_layout = QGridLayout(self.centralwidget)
        self.main_layout.setSpacing(10)

    def close_tab(self, i):  # закрыть вкладку
        if self.count() >= 2:
            self.widget(i).findChildren(QWebEngineView)[0].page().setAudioMuted(True)
            # self.findChildren(QWebEngineView).index(0).page().setAudioMuted(True)
            self.widget(i).close()
            self.removeTab(i)
            del self.all_tabs[i]
        else:
            app.quit()

    def url_navigate(self):
        url = QUrl(self.sender().text())
        if url.scheme() == "":
            url = QUrl("http://www." + self.sender().text())
        if is_url_correct(str(url).split("'")[1]):
            self.currentWidget().findChildren(QWebEngineView)[0].setUrl(url)
            self.sender().clearFocus()

    def update_url(self):
        search_bar = self.currentWidget().findChildren(QLineEdit)[0]
        url = str(self.currentWidget().findChildren(QWebEngineView)[0].url()).split("'")[1]
        search_bar.setText(url)
        search_bar.setCursorPosition(0)
        search_bar.clearFocus()

    def adjustTitle(self):
        self.setTabText(self.currentIndex(), self.web.title())

    def set_theme(self):
        if self.themes.isChecked():
            self.no_checked()
            self.themes.setChecked(True)
            self.hide_all()
            self.set_theme_area.show()
        else:
            self.hide_all()
            self.space.show()

    def safety(self):
        if self.confidental.isChecked():
            self.no_checked()
            self.confidental.setChecked(True)
            self.hide_all()
            self.set_confidental_area.show()
        else:
            self.hide_all()
            self.space.show()

    def accounts(self):
        if self.account.isChecked():
            self.no_checked()
            self.account.setChecked(True)
            self.hide_all()
            self.set_account_area.show()
        else:
            self.hide_all()
            self.space.show()

    def hide_all(self):
        self.set_theme_area.hide()
        self.set_confidental_area.hide()
        self.set_account_area.hide()
        self.space.hide()

    def no_checked(self):
        self.confidental.setChecked(False)
        self.themes.setChecked(False)
        self.account.setChecked(False)

    def language_change(self):
        print(self.languages.currentText())
        self.confidental.setChecked(True)

    def download_icons(self):
        if str(self.web.iconUrl()).split("'")[1] != '':
            url = str(self.web.iconUrl()).split("'")[1]
            icon = requests.get(url).content
            with open(f"cash/icon_web{self.icons_count}.png", mode="wb") as img:
                img.write(icon)

            self.setTabIcon(self.currentIndex(), QIcon(f"cash/icon_web{self.icons_count}.png"))
            self.icons_count += 1

    def closeEvent(self, event):
        path = "cash"
        shutil.rmtree("cash")
        os.mkdir(path)

    def load_theme(self):
        path = self.theme + "/"
        self.icon_restart = QIcon(f"{path}restart_page.png")
        self.icon_home = QIcon(f"{path}home_page.png")
        self.icon_back = QIcon(f"{path}go_back.png")
        self.icon_forward = QIcon(f"{path}go_forward.png")
        self.icon_close = QIcon(f"{path}close.png")
        self.icon_account = QIcon(f"{path}account.png")

    def open_url(self):
        self.new_tab(str(self.table.item(self.findChildren(QPushButton).index(self.sender()), 1).text()))

    def output_in_table(self):  # внести данные в табличку
        result = self.cursor.execute("""SELECT * FROM history""").fetchall()
        self.table.setRowCount(self.count_items)
        for i in range(len(result)):
            for j in range(1, 4):
                self.table.setItem(i, j - 1, QTableWidgetItem(str(result[i][j])))
            self.check = QCheckBox(self)
            self.button = QPushButton("Перейти", self)
            self.button.setStyleSheet("""
            QPushButton {
                color: rgb(209, 209, 209);
                background: rgba(53,54,58,255);
                align: left;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(32,33,36,255);
            }
            QPushButton:pressed {
                border: 2px solid rgba(66,133,244,255);
            }
            QPushButton:checked {
                border: 2px solid rgba(66,133,244,255);
            }
            """)
            self.button.clicked.connect(self.open_url)
            self.widget1 = QWidget()
            self.cell_layout = QHBoxLayout(self.widget1)
            self.cell_layout.setAlignment(Qt.AlignCenter)
            self.cell_layout.setContentsMargins(0, 0, 0, 0)
            self.cell_layout.addWidget(self.check)
            self.widget1.setLayout(self.cell_layout)
            self.table.setCellWidget(i, 3, self.widget1)
            self.table.setCellWidget(i, 4, self.button)
            self.check_list.append(self.check)
            self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.table.horizontalHeader().resizeSection(1, 200)
            self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    def connect_bd(self):  # подключения к бд
        self.bd = sqlite3.connect("browser_bd.db")
        self.cursor = self.bd.cursor()
        try:
            self.count_items = self.cursor.execute("""SELECT COUNT(*) FROM history""").fetchone()[0]
        except sqlite3.OperationalError:  # если бд не найдена, создание новой
            self.cursor.execute("""CREATE TABLE history (id INTEGER PRIMARY KEY, name TEXT, url TEXT, time TEXT)""")
            self.cursor.execute("""CREATE TABLE themes (id INTEGER PRIMARY KEY, name TEXT, value TEXT)""")
            self.cursor.execute("""INSERT INTO themes VALUES (1, 'StartColor', '#d0d0d0'), (2, 'TabsColor', '#d0d0d0'),
             (3, 'TabsShape', '1'), (4, 'StartUrl', 'HomePage'),
              (5, 'ButtonsColor', '#d0d0d0'), (6, 'HomePageImage', '')""")
            self.cursor.execute("""CREATE TABLE promptings (name TEXT, url TEXT, color TEXT)""")
            self.cursor.execute("INSERT INTO promptings VALUES('Google', 'https://www.google.com', 'red')")
            self.bd.commit()

    # def mousePressEvent(self, event):
    #     click = event.button()
    #     if click == Qt.RightButton:
    #         print(1)
    #     print(event.x(), event.y())

    def print(self):
        print(self.frameGeometry())

    def mouseMoveEvent(self, event):
        print(event.x(), event.y())


def open_new_window():
    browser2 = MainWindow()
    browser2.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = MainWindow()
    browser.show()
    sys.exit(app.exec_())
