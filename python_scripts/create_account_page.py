'''This script create a user account and inputs the data into the
Users, teams, and team_members table'''

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import sqlite3
from creating_database import database_path


class create_account(QDialog):
    def __init__(self, widget):
        super(create_account, self).__init__()
        self.widget = widget
        loadUi("python_scripts/../GUI_files/create_account.ui", self)
        self.create_account_page_create_account_push_button.clicked.connect(
            self.create_account_function)
        self.create_account_page_return_to_login_push_button.clicked.connect(
            self.return_to_login_function)
        self.create_account_page_password_line_edit.setEchoMode(
            QtWidgets.QLineEdit.Password)
        self.create_account_page_confirm_password_line_edit.setEchoMode(
            QtWidgets.QLineEdit.Password)
        self.add_teams_to_drop_down()

    def create_account_function(self):
        first_name = self.create_account_page_first_name_line_edit.text()
        last_name = self.create_account_page_last_name_line_edit.text()
        team_name = self.create_account_page_team_name_combo_box.currentText()
        work_email = self.create_account_page_work_email_line_edit.text()
        password = self.create_account_page_password_line_edit.text()
        confirm_password = self.create_account_page_confirm_password_line_edit.text()

        is_valid = self.validating_fields(
            first_name, last_name, team_name, work_email, password, confirm_password)

        if is_valid == True:
            self.show_message_box("Success", "Your account has been created.")

            if team_name == "Stats Gov":
                role = "admin"
            else:
                role = "user"

            user_id = self.add_user_to_users_table(
                first_name, last_name, team_name, work_email, password, role)

            team_id = self.get_team_id_by_name(team_name)
            self.add_user_to_team_members_table(user_id, team_id)

            self.create_account_page_first_name_line_edit.clear()
            self.create_account_page_last_name_line_edit.clear()
            self.create_account_page_team_name_combo_box.setCurrentIndex(0)
            self.create_account_page_work_email_line_edit.clear()
            self.create_account_page_password_line_edit.clear()
            self.create_account_page_confirm_password_line_edit.clear()

    def return_to_login_function(self):
        from login_page import login
        logins = login(self.widget)
        self.widget.addWidget(logins)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)

    # The following provides basic data validation criteria

    def validating_fields(self, first_name, last_name, team_name, work_email, password, confirm_password):

        minimum_password_length = 5
        maximum_password_length = 15

        if not first_name.strip():
            return False, self.show_message_box("Error", "Please enter your first name.")
        if not last_name.strip():
            return False, self.show_message_box("Error", "Please enter your last name.")
        if team_name == "SELECT TEAM":
            return False, self.show_message_box("Error", "Please select your team.")
        if not work_email.strip():
            return False, self.show_message_box("Error", "Please enter your work email.")
        if not password.strip():
            return False, self.show_message_box("Error", "Please enter your password.")
        if len(password) < minimum_password_length:
            return False, self.show_message_box("Error", "Your password must be at least 5 characters long.")
        if len(password) > maximum_password_length:
            return False, self.show_message_box("Error", "Your password must not be longer than 15 characters.")
        if not confirm_password.strip():
            return False, self.show_message_box("Error", "Please confirm your password.")
        if password != confirm_password:
            return False, self.show_message_box("Error", "Your password and confirm password does not match.")

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT users_id FROM Users WHERE work_email = ?", (work_email,))
        user_id = cursor.fetchone()
        connection.close()

        if user_id is not None:
            return False, self.show_message_box("Error", "The work email you provided is already in use.")

        else:
            return True

    # pops up the message box showing an error.

    def show_message_box(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    # creates the drop down box for the team names, selected form the Teams table in the database
    def add_teams_to_drop_down(self):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute("Select team_name FROM Teams")
        teams = cursor.fetchall()

        for team in teams:
            self.create_account_page_team_name_combo_box.addItem(team[0])

        connection.close

    def add_user_to_users_table(self, first_name, last_name, team_name, work_email, password, role):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute("""INSERT INTO Users (first_name, last_name, team_name, work_email, password, role)
                       VALUES (?,?,?,?,?,?)""", (first_name, last_name, team_name, work_email, password, role))

        user_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return user_id

    def get_team_id_by_name(self, team_name):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT team_id FROM Teams WHERE team_name = ?", (team_name,))
        team_id = cursor.fetchone()[0]

        connection.close()
        return team_id

    # Inputting the user id and team id into the team_members table
    # This is important, since if the user changes team, the team_members table
    # can be updated with the new team_id, and the Users table can be updated accordingly.

    def add_user_to_team_members_table(self, user_id, team_id):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO team_members(team_id, users_id) VALUES (?, ?)", (team_id, user_id))

        connection.commit()
        connection.close()
