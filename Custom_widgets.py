import sys

from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication, QWidget
from qtwidgets import AnimatedToggle


class Settings_widgets(QWidget):
    def __init__(self, name):
        super(Settings_widgets, self).__init__()
        self.name = name
        self.widget(self.name)

    def widget(self, name):
        self.main_widget = QWidget(self)
        self.main_widget.setMinimumWidth(400)
        # self.main_widget.resize(400, 100)
        self.main_widget.setStyleSheet("""
            background-color: rgba(53,54,58,255);
            color: white;
            font-size: 20px;
            border-radius: 10px;
        """)
        self.layout = QGridLayout()
        # self.layout.setAlignment(Qt.AlignCenter)
        self.main_widget.setLayout(self.layout)

        self.name = QLabel(self.name)
        self.layout.addWidget(self.name)


class Settings_switch(Settings_widgets):
    def __init__(self, name):
        super(Settings_switch, self).__init__(name)
        self.name = name
        self.widget(self.name)
        self.initUI(self.name)

    def initUI(self, name):
        self.layout.addWidget(name
                              )
        switch_themes = AnimatedToggle(
            checked_color="#202024",
            pulse_checked_color="#4285F4"
        )
        self.layout.addWidget(switch_themes)


class Settings_combobox(Settings_widgets):
    def __init__(self, name, items):
        super(Settings_combobox, self).__init__(name)
        self.name = name
        self.items = items
        self.widget(self.name)
        self.initUI(self.name, self.items)

    def initUI(self, name, items):
        self.languages = QComboBox()
        # self.languages.move(20, 50)
        self.languages.setStyleSheet("""
                QComboBox {
                    color: rgb(209, 209, 209);
                    background: rgba(53,54,58,255);
                    padding: 20px;
                    font-size: 15px;
                }
                QComboBox QAbstractItemView {
                    background: rgba(32,33,36,255);
                    selection-background-color: transparent;
                    color: white;
                    selection-background-color: rgba(66,133,244,255);
                }
        """)
        self.languages.addItems(items)
        self.layout.addWidget(self.languages)


class Settings_button(Settings_widgets):
    def __init__(self, name, button_name):
        super(Settings_button, self).__init__(name)
        self.name = name
        self.button_name = button_name
        self.widget(self.name)
        self.initUI(self.name, self.button_name)

    def initUI(self, name, button_name):
        self.setStyleSheet("""
                QPushButton {
                    color: rgb(209, 209, 209);
                    background: rgba(53,54,58,255);
                    border-radius: 10px;
                    padding: 20px;
                    font-size: 15px;
                }
        """)

        self.link = QPushButton(button_name)
        self.layout.addWidget(self.link)

    def add_button(self, button_name):
        self.link = QPushButton(button_name)
        self.layout.addWidget(self.link)


class Settings_interactive(Settings_widgets):
    def __init__(self, name, account, icon):
        super(Settings_interactive, self).__init__(name)
        self.name = name
        self.account = account
        self.icon = icon
        self.initUI()

    def initUI(self):
        self.pixmap = QPixmap(self.icon)

        self.mail = QLabel(self.account)
        self.mail.setStyleSheet("""color: grey;""")

        self.image = QLabel()
        self.image.setPixmap(self.pixmap)
        self.layout.addWidget(self.mail, 1, 0)
        self.layout.addWidget(self.image, 1, 1, Qt.AlignRight)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 400, 500, 500)

        centralwidget = QWidget()
        self.setCentralWidget(centralwidget)

        layout = QGridLayout(centralwidget)
        self.setLayout(layout)

        # widget1 = Settings_switch("Изменение языка")
        # layout.addWidget(widget1)
        #
        # widget2 = Settings_switch("Включить ночную тему")
        # layout.addWidget(widget2)
        #
        # widget3 = Settings_switch("Показывать кнопку главная страница")
        # layout.addWidget(widget3)
        #
        # widget4 = Settings_combobox("Сменить язык")
        # layout.addWidget(widget4)

        widget4 = Settings_interactive("Сменить аккаунт", "mrsldavletov@gmail.com", "icons/account.png")
        layout.addWidget(widget4)

        widget = QMenu(self)
        name = QAction("123", self)
        widget.addAction(name)
        layout.addWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
