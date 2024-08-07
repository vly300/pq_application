'''
This script gives functionality to the Login Page of the application.
It compares the inputted Username and Password to that data found in the Users table.
It also has the functionality to navigate to the Create Account page, and Home Screen
'''

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import sqlite3
from creating_database import database_path
from user_session import current_session


class login(QDialog):
    def __init__(self, widget):
        super(login, self).__init__()
        self.widget = widget
        loadUi("python_scripts/../GUI_files/login_page.ui", self)
        self.login_page_login_push_button.clicked.connect(self.login_function)
        self.login_page_password_line_edit.setEchoMode(
            QtWidgets.QLineEdit.Password)
        self.login_page_create_account_push_button.clicked.connect(
            self.go_to_create_account_page)

    def login_function(self):

        email = self.login_page_email_line_edit.text()
        password = self.login_page_password_line_edit.text()

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # The following populate the user_session class with the necessary data
        # The methods in the class help determine the user's role (admin or user) which is used later on
        cursor.execute(
            "SELECT users_id, role, team_name FROM Users WHERE work_email = ? AND password = ?", (email, password))
        result = cursor.fetchone()

        if result is not None:
            user_id, role, team_name = result
            current_session.set_user(user_id, role, team_name)
            print(
                f"Logged in as: ID={current_session.user_id}, Role={current_session.user_role}, Team={current_session.user_team}")
            self.go_to_home_screen_page()
        else:
            self.show_message_box(
                "Invalid Login", "Either the email or the password is incorrect. Try again.")

        connection.close()

    def go_to_create_account_page(self):
        from create_account_page import create_account
        createacc = create_account(self.widget)
        self.widget.addWidget(createacc)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)

    def go_to_home_screen_page(self):
        from home_screen_page import home_screen
        homescreen = home_screen(self.widget)
        self.widget.addWidget(homescreen)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)

    def show_message_box(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()


def start_application():
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    login_window = login(widget)
    widget.addWidget(login_window)
    widget.setMinimumSize(480, 620)
    widget.show()
    sys.exit(app.exec_())
