# импортируем систему
import sys

# импортируем время
import time

# импортируем нужные на виджеты и функции
from PyQt6.QtWidgets import (QApplication, 
                             QWidget, QListWidget, QListWidgetItem, 
                             QLabel, QLineEdit,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QMessageBox, 
                             QRadioButton)
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6 import QtGui
from PyQt6.QtCore import Qt

# создаем и описываем окно приложения
class MainWindow(QWidget):
    # создаем переменные для определения размера окна
    window_height = 400
    window_width = 500

    # функция __init__ вызывается сразу после создания объекта
    def __init__(self):
        # функция super() нужна для того, чтобы не изменять полностью функцию __init__ ,
        # ведь класс MainWindow наследуется от QWidget и в нем определена функция __init__
        # Используя функцию super(), мы копируем функцию __init__ из родительского класса в наш класс
        # Затем мы просто добавляем все, что хотим, не боясь полностью переопределить функцию
        super().__init__()

        # задаём начальный язык
        self.language = 'English'

        # создаём виджеты и описываем их свойства
        self.label_word = QLabel("<b>Слова</b>", self)
        self.label_word.setFont(QtGui.QFont('Comic Sans MS', 17))

        self.label_translation = QLabel("<b>Перевод</b>", self)
        self.label_translation.move(250, 140)
        self.label_translation.setFont(QtGui.QFont('Comic Sans MS', 17))

        self.radio_button_eng = QRadioButton('English')
        self.radio_button_eng.setChecked(True)
        self.radio_button_eng.language = 'English'
        self.radio_button_eng.toggled.connect(self.onCliked)
        self.radio_button_eng.setFont(QtGui.QFont('Comic Sans MS', 12))

        self.radio_button_ru = QRadioButton('Русский')
        self.radio_button_ru.language = 'Russian'
        self.radio_button_ru.toggled.connect(self.onCliked)
        self.radio_button_ru.setFont(QtGui.QFont('Comic Sans MS', 12))

        self.words_list = QListWidget(self)
        self.words_list.setFont(QtGui.QFont('Comic Sans MS', 15))
        self.words_list.setStyleSheet("background-color: '#FFFFE0'")

        self.translation_line = QLineEdit(self)
        self.translation_line.setFont(QtGui.QFont('Comic Sans MS', 15))
        self.translation_line.setReadOnly(True)
        self.translation_line.setStyleSheet("background-color: '#FFFFE0'")

        self.delete_word = QPushButton('Удалить слово', self)
        self.delete_word.setFont(QtGui.QFont('Comic Sans MS', 15))
        self.delete_word.move(223 , 230)
        self.delete_word.resize(160, 30)
        self.delete_word.setStyleSheet("background-color: '#FFFFE0'")

        self.label_new_word = QLabel("<b>ДОБАВИТЬ НОВОЕ СЛОВО</b>", self)
        self.label_new_word.setFont(QtGui.QFont("Comic Sans MS", 17))
        self.label_new_word.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.label_add_word = QLabel("Слово:", self)
        self.label_add_word.setFont(QtGui.QFont('Comic Sans MS', 12))

        self.new_word = QLineEdit(self)
        self.new_word.setStyleSheet("background-color: '#FFFFE0'")
        self.new_word.setFont(QtGui.QFont('Comic Sans MS', 12))

        self.label_add_translation = QLabel("Перевод:", self)
        self.label_add_translation.setFont(QtGui.QFont('Comic Sans MS', 12))

        self.new_translation = QLineEdit(self)
        self.new_translation.setStyleSheet("background-color: '#FFFFE0'")
        self.new_translation.setFont(QtGui.QFont('Comic Sans MS', 12))

        self.add_button = QPushButton("Добавить", self)
        self.add_button.setFont(QtGui.QFont('Comic Sans MS', 15))
        self.add_button.setStyleSheet("background-color: '#FFFFE0'")

        # подключаем функции
        self.init_ui()
        self.create_db()
        self.load_words()

        # подключаем кнопки и ListWidget
        self.add_button.clicked.connect(self.add_word)
        self.delete_word.clicked.connect(self.delete)
        self.words_list.clicked.connect(self.translation)

    def init_ui(self):
        # задаём параметры окна
        self.setFixedSize(self.window_height, self.window_width)
        self.setWindowTitle("Словарик")
        vbox = QVBoxLayout()

        # размещаем виджеты 
        hbox = QHBoxLayout()
        hbox.addWidget(self.label_word)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.radio_button_eng, 0)
        hbox.addWidget(self.radio_button_ru, 1)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.words_list)
        hbox.addWidget(self.translation_line)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label_new_word)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label_add_word)
        hbox.addWidget(self.new_word)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label_add_translation)
        hbox.addWidget(self.new_translation)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.add_button)
        vbox.addLayout(hbox)

        # задаем Layout
        self.setLayout(vbox)

    def create_db(self):
        # создаем таблицы в БД
        query = QSqlQuery()
        query.exec(
            """
            CREATE TABLE IF NOT EXISTS words(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            word VARCHAR(255) NOT NULL,
            translation VARCHAR(255) NOT NULL
            );
            """
        )

    def onCliked(self):
        # функция, описывающая действия нажатой RadioButton
        radiobutton = self.sender()
        if radiobutton.isChecked():
            self.language = radiobutton.language
            self.translation_line.setText('')
            self.load_words()

    def load_words(self):
        # загружаем слова в ListWidget
        if self.language == 'English':
            query = QSqlQuery()
            query.exec(
                """
                SELECT *
                from words
                ORDER BY word
                """
            )
            self.all_words = []
            count = query.record().count()
            while query.next():
                temp = []
                for i in range(count):
                    temp.append(query.value(i))
                self.all_words.append(temp)
            self.words_list.clear()
            for word in self.all_words:
                self.words_list.addItem(QListWidgetItem(word[1]))
    
        elif self.language == 'Russian':
            query = QSqlQuery()
            query.exec(
                """
                SELECT *
                from words
                ORDER BY translation
                """
            )
            self.all_words = []
            count = query.record().count()
            while query.next():
                temp = []
                for i in range(count):
                    temp.append(query.value(i))
                self.all_words.append(temp)
            self.words_list.clear()
            for word in self.all_words:
                self.words_list.addItem(QListWidgetItem(word[2]))

    def add_word(self):
        # функция, описывающая добавление слова
        word = self.new_word.text()
        translation = self.new_translation.text()
        # исключаем добавление пустого слова
        if word == '' or translation == '':
            message_box = QMessageBox()
            message_box.setText("Поля не могут быть пустыми!")
            message_box.setWindowTitle("Внимание")
            message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            message_box.show()
            result = message_box.exec()
        else:
            query = QSqlQuery()
            query.exec(
                f"""
                INSERT INTO words (word, translation)
                VALUES  ('{word}', '{translation}');
                """
            )
            self.new_word.setText('')
            self.new_translation.setText('')
        self.load_words()
    
    def translation(self):
        # функция, выдающая перевод
        if self.language == 'English':
            row = self.words_list.currentRow()
            self.translation_line.setText(self.all_words[row][2])
        elif self.language == 'Russian':
            row = self.words_list.currentRow()
            self.translation_line.setText(self.all_words[row][1])
        
    def delete(self):
        # функция удаления слова
            try:
                if self.language == 'English':
                    row = self.words_list.currentRow()
                    word_id = self.all_words[row][0]
                    message_box = QMessageBox()
                    message_box.setText(f'Вы точно хотите удалить слово <b>{self.all_words[row][1]}</b>?')
                    message_box.setWindowTitle('Удалить слово?')
                    message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    message_box.show()
                    result = message_box.exec()
                    if result == QMessageBox.StandardButton.Yes:
                        query = QSqlQuery()
                        query.exec(
                            f"""
                            DELETE FROM words
                            WHERE id={word_id}
                            """
                        )
                        self.translation_line.setText('')
                        self.load_words()
                elif self.language == 'Russian':
                    row = self.words_list.currentRow()
                    word_id = self.all_words[row][0]
                    message_box = QMessageBox()
                    message_box.setText(f'Вы точно хотите удалить слово <b>{self.all_words[row][2]}</b>?')
                    message_box.setWindowTitle('Удалить слово?')
                    message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    message_box.show()
                    result = message_box.exec()
                    if result == QMessageBox.StandardButton.Yes:
                        query = QSqlQuery()
                        query.exec(
                            f"""
                            DELETE FROM words
                            WHERE id={word_id}
                            """
                        )
                        self.translation_line.setText('')
                        self.load_words()
            # исключаем ошибку пустого списка
            except IndexError:
                message_box = QMessageBox()
                message_box.setText('В списке нет слов!')
                message_box.setWindowTitle('Внимание')
                message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                message_box.show()
                result = message_box.exec()

if __name__ == '__main__':
    # подключаемся к базе данных
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("words.sqlite")

    # если база данных не откроется
    if not con.open():
        con_not_open = QMessageBox()
        con_not_open.setText('База данных не открылась!')
        con_not_open.setWindowTitle('Ошибка')
        con_not_open.setStandardButtons(QMessageBox.StandardButton.Ok)
        con_not_open.show()
        result = con_not_open.exec()
        if result == QMessageBox.StandardButton.Ok:
            sys.exit(1)
    # даём Windows понять, что у этого окна не стандартная иконка окна Python
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'ImranCO.Словарик.ПО.1.03'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    
    # создаем экземпляр приложения и даем ему иконку
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.ico'))

    # создаем экземпляр окна и задаем иконку и цвет бекгроунда
    window = MainWindow()
    window.setStyleSheet("background-color: '#98FB98'")
    window.setWindowIcon(QtGui.QIcon('icon.ico'))

    # показываем окно
    window.show()
    
    # запускаем приложение
    app.exec()