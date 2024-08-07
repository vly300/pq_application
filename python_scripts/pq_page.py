'''
This script provide a great amount of functionality for the PQ page.
While I could have made this more modular, a lot of the function interact with eachother
and I feared integration would become an issue if the functions were separated
into different scripts.'''

import csv
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
import sqlite3
from creating_database import database_path
from pq_page_tail_buttons import tail_buttons_delegate
from user_session import current_session


class pqs_page(QDialog):
    def __init__(self, widget, pqs_sorted):
        super(pqs_page, self).__init__()
        self.widget = widget
        self.pqs_sorted = pqs_sorted

        loadUi("python_scripts/../GUI_files/pq_page.ui", self)
        self.pq_page_table.setColumnWidth(0, 250)
        self.pq_page_table.setColumnWidth(1, 100)
        self.pq_page_table.setColumnWidth(2, 350)
        self.pq_page_export_to_csv_push_button.clicked.connect(
            self.export_to_csv)
        self.pq_page_home_push_button.clicked.connect(
            self.return_to_home_screen)
        self.pq_page_logout_push_button.clicked.connect(self.logout)
        self.pq_page_apply_filters_push_button.clicked.connect(
            self.apply_filters)
        self.pq_page_apply_changes_push_button.clicked.connect(
            self.apply_changes)
        self.pq_page_refresh_button.clicked.connect(self.refresh_function)
        self.add_teams_to_combo_box()

        self.action_options = ['None', 'Information', 'Review']

        self.pq_page_table.setMouseTracking(True)
        print("The current user role is: ", current_session.user_role)
        if current_session.user_role == 'admin':
            delegate = tail_buttons_delegate(self.pq_page_table)
            delegate.row_removed.connect(self.remove_row_from_table)
            delegate.row_inserted.connect(self.insert_row_in_table)
            self.pq_page_table.setItemDelegateForColumn(6, delegate)
        else:
            self.pq_page_table.setItemDelegateForColumn(6, None)

        if self.pqs_sorted == 1:
            self.show_all_pqs_function()
        elif self.pqs_sorted == 2:
            self.show_unallocated_pqs_function()
        else:
            self.show_allocated_pqs_function()

    # This function allows users to export whatever they see the pq_page_table widget to a csv file.
    def export_to_csv(self):

        current_date = datetime.now().strftime("%d_%m_%Y")  # Format: dd_MM_yyyy
        default_file_name = f"{current_date}_pqs_.csv"

        # Open the save file dialog
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", default_file_name, "CSV Files (*.csv);;All Files (*)", options=options)

        if file_name:
            if not file_name.lower().endswith('.csv'):
                file_name += '.csv'

            try:
                with open(file_name, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    headers = [self.pq_page_table.horizontalHeaderItem(
                        i).text() for i in range(self.pq_page_table.columnCount())]
                    writer.writerow(headers)

                    for row in range(self.pq_page_table.rowCount()):
                        row_data = [self.pq_page_table.item(row, col).text() if self.pq_page_table.item(
                            row, col) else '' for col in range(self.pq_page_table.columnCount())]
                        writer.writerow(row_data)

                QMessageBox.information(
                    self, "Export Successful", f"Data has been exported to {file_name}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Export Failed", f"An error occurred while exporting data: {str(e)}")

    # This function refreshes what seen in the table. It essentially navigates away from the current screen
    # sorts the PQs into the table widget using the same criteria as before,
    # and then navigates back to the table and page.

    def refresh_function(self):

        self.pq_page_table.setRowCount(0)
        # while disabling updates did not need to be included in this prototype, it is good practise.
        self.pq_page_table.setUpdatesEnabled(False)

        self.return_to_home_screen()
        allpqs = pqs_page(self.widget, self.pqs_sorted)
        self.widget.addWidget(allpqs)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

        if self.pqs_sorted == 1:
            self.show_all_pqs_function()
        elif self.pqs_sorted == 2:
            self.show_unallocated_pqs_function()
        else:
            self.show_allocated_pqs_function()

        self.pq_page_table.setUpdatesEnabled(True)
        self.pq_page_table.resizeRowsToContents()

    def remove_row_from_table(self, row):
        self.pq_page_table.removeRow(row)

    # This function is used when a question has been duplicated and the copy
    # is inserted into the table.

    def insert_row_in_table(self, row, new_question, new_question_id):
        self.pq_page_table.insertRow(row)

        for column_number, data in enumerate(new_question):
            if column_number == 4:  # 'Action' column is index 4
                combo_box = QComboBox()
                combo_box.addItems(self.action_options)
                combo_box.setCurrentText(data if data else 'None')
                self.pq_page_table.setCellWidget(row, column_number, combo_box)
            elif column_number == 5:  # 'Topic Area' column is index 5
                combo_box = QComboBox()
                if current_session.user_role == 'admin':
                    combo_box.addItems(self.team_names)
                    combo_box.setCurrentText(data if data else '')
                    self.pq_page_table.setCellWidget(
                        row, column_number, combo_box)
                else:
                    combo_box.addItem(str(data))
                    combo_box.addItem('None')
                    combo_box.addItem(current_session.user_team)
                    combo_box.setCurrentText(data if data else '')
                    self.pq_page_table.setCellWidget(
                        row, column_number, combo_box)
            else:
                item = QTableWidgetItem(str(data))
                item.setData(Qt.UserRole, new_question_id)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setSizeHint(QSize(0, 100))
                self.pq_page_table.setItem(row, column_number, item)

    def show_all_pqs_function(self):
        print("executed all pqs function")
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT question_id, reference_id, date_submitted, question, answer, advised_action, team_id, additional_comments, phs_relevant, allocated_status FROM Questions"
        )

        questions = cursor.fetchall()
        connection.close()

        self.pq_page_table.setRowCount(0)
        self.pq_page_table.setUpdatesEnabled(False)

        for row_number, row_data in enumerate(questions):
            self.pq_page_table.insertRow(row_number)
            question_id = row_data[0]
            phs_relevant = row_data[8]
            allocated_status = row_data[9]

            for column_number, data in enumerate(row_data[1:8]):
                if column_number == 4:
                    combo_box = QComboBox()
                    combo_box.addItems(self.action_options)
                    combo_box.setCurrentText(data if data else 'None')
                    self.pq_page_table.setCellWidget(
                        row_number, column_number, combo_box)
                elif column_number == 5:
                    combo_box = QComboBox()
                    if current_session.user_role == 'admin':
                        combo_box.addItems(self.team_names)
                        combo_box.setCurrentText(data if data else '')
                        self.pq_page_table.setCellWidget(
                            row_number, column_number, combo_box)
                    else:
                        combo_box.addItem(str(data))
                        combo_box.addItem('None')
                        combo_box.addItem(current_session.user_team)
                    combo_box.setCurrentText(data if data else '')
                    self.pq_page_table.setCellWidget(
                        row_number, column_number, combo_box)
                else:
                    item = QTableWidgetItem(str(data))
                    item.setData(Qt.UserRole, question_id)
                    item.setData(Qt.UserRole + 1, phs_relevant)
                    item.setData(Qt.UserRole + 2, allocated_status)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setSizeHint(QSize(0, 100))
                    self.pq_page_table.setItem(row_number, column_number, item)

        self.pq_page_table.resizeRowsToContents()
        self.pq_page_table.setUpdatesEnabled(True)

    def show_unallocated_pqs_function(self):
        print("executed unallocated pqs function")
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT question_id, reference_id, date_submitted, question, answer, advised_action, team_id, additional_comments, phs_relevant, allocated_status FROM Questions
            WHERE phs_relevant = 'TBD' AND allocated_status = 'unallocated'
        """)

        questions = cursor.fetchall()
        connection.close()

        self.pq_page_table.setRowCount(0)
        self.pq_page_table.setUpdatesEnabled(
            False)

        for row_number, row_data in enumerate(questions):
            self.pq_page_table.insertRow(row_number)
            question_id = row_data[0]
            phs_relevant = row_data[8]
            allocated_status = row_data[9]

            for column_number, data in enumerate(row_data[1:8]):
                if column_number == 4:
                    combo_box = QComboBox()
                    combo_box.addItems(self.action_options)
                    combo_box.setCurrentText(data if data else 'None')
                    self.pq_page_table.setCellWidget(
                        row_number, column_number, combo_box)
                elif column_number == 5:
                    combo_box = QComboBox()
                    if current_session.user_role == 'admin':
                        combo_box.addItems(self.team_names)
                        combo_box.setCurrentText(data if data else '')
                        self.pq_page_table.setCellWidget(
                            row_number, column_number, combo_box)
                    else:
                        combo_box.addItem(str(data))
                        combo_box.addItem('None')
                        combo_box.addItem(current_session.user_team)
                    combo_box.setCurrentText(data if data else '')
                    self.pq_page_table.setCellWidget(
                        row_number, column_number, combo_box)
                else:
                    item = QTableWidgetItem(str(data))
                    item.setData(Qt.UserRole, question_id)
                    item.setData(Qt.UserRole + 1, phs_relevant)
                    item.setData(Qt.UserRole + 2, allocated_status)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setSizeHint(QSize(0, 100))
                    self.pq_page_table.setItem(row_number, column_number, item)

        self.pq_page_table.resizeRowsToContents()
        self.pq_page_table.setUpdatesEnabled(True)

    def show_allocated_pqs_function(self):
        print("executing allocated pqs function")
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT question_id, reference_id, date_submitted, question, answer, advised_action, team_id, additional_comments, phs_relevant, allocated_status FROM Questions
            WHERE phs_relevant = 'Yes' AND allocated_status = 'allocated'
        """)

        questions = cursor.fetchall()
        connection.close()

        self.pq_page_table.setRowCount(0)
        self.pq_page_table.setUpdatesEnabled(
            False)

        for row_number, row_data in enumerate(questions):
            self.pq_page_table.insertRow(row_number)
            question_id = row_data[0]
            phs_relevant = row_data[8]
            allocated_status = row_data[9]

            for column_number, data in enumerate(row_data[1:8]):
                if column_number == 4:
                    combo_box = QComboBox()
                    combo_box.addItems(self.action_options)
                    combo_box.setCurrentText(data if data else 'None')
                    self.pq_page_table.setCellWidget(
                        row_number, column_number, combo_box)
                elif column_number == 5:
                    combo_box = QComboBox()
                    if current_session.user_role == 'admin':
                        combo_box.addItems(self.team_names)
                        combo_box.setCurrentText(data if data else '')
                        self.pq_page_table.setCellWidget(
                            row_number, column_number, combo_box)
                    else:
                        combo_box.addItem(str(data))
                        combo_box.addItem('None')
                        combo_box.addItem(current_session.user_team)
                    combo_box.setCurrentText(data if data else '')
                    self.pq_page_table.setCellWidget(
                        row_number, column_number, combo_box)
                else:
                    item = QTableWidgetItem(str(data))
                    item.setData(Qt.UserRole, question_id)
                    item.setData(Qt.UserRole + 1, phs_relevant)
                    item.setData(Qt.UserRole + 2, allocated_status)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setSizeHint(QSize(0, 100))
                    self.pq_page_table.setItem(row_number, column_number, item)

        self.pq_page_table.resizeRowsToContents()
        self.pq_page_table.setUpdatesEnabled(True)

    def logout(self):

        current_session.clear_user()

        from login_page import login
        logins = login(self.widget)
        self.widget.addWidget(logins)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def return_to_home_screen(self):
        from home_screen_page import home_screen
        home_screen_instance = home_screen(self.widget)
        self.widget.addWidget(home_screen_instance)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def apply_filters(self):
        pq_ref_filter = self.pq_page_pq_ref_line_edit.text().strip()
        date_from_text = self.pq_page_from_date_edit.text().strip()
        date_to_text = self.pq_page_to_date_edit.text().strip()
        keywords_filter = self.pq_page_keywords_line_edit.text().strip()
        status_filter = self.pq_page_select_status_combo_box.currentText().strip()
        action_filter = self.pq_page_select_action_combo_box.currentText().strip()
        topic_area_filter = self.pq_page_select_topic_area_combo_box.currentText().strip()

        date_from = None
        date_to = None

        if date_from_text:
            date_from = QDate.fromString(
                date_from_text, 'yyyy/MM/dd').toString('yyyy-MM-dd')

        if date_to_text:
            date_to = QDate.fromString(
                date_to_text, 'yyyy/MM/dd').toString('yyyy-MM-dd')

        for row in range(self.pq_page_table.rowCount()):
            item_ref = self.pq_page_table.item(row, 0)
            item_date = self.pq_page_table.item(row, 1)
            item_question = self.pq_page_table.item(row, 2)
            item_answer = self.pq_page_table.item(row, 3)
            action_combo = self.pq_page_table.cellWidget(row, 4)
            topic_area_combo = self.pq_page_table.cellWidget(row, 5)

            ref_text = item_ref.text() if item_ref else ""
            date_text = item_date.text() if item_date else ""
            question_text = item_question.text() if item_question else ""
            answer_text = item_answer.text() if item_answer else ""
            action_text = action_combo.currentText() if action_combo else ""
            topic_area_text = topic_area_combo.currentText() if topic_area_combo else ""

            if 'T' in date_text:
                date_text = date_text.split('T')[0]

            hidden = False

            if pq_ref_filter and pq_ref_filter.lower() not in ref_text.lower():
                hidden = True

            if date_from or date_to:
                try:
                    date = QDate.fromString(date_text, 'yyyy-MM-dd')
                    if date_from and date_to:
                        if not (date_from <= date.toString('yyyy-MM-dd') <= date_to):
                            hidden = True
                    elif date_from:
                        if not date_from <= date.toString('yyyy-MM-dd'):
                            hidden = True
                    elif date_to:
                        if not date_to >= date.toString('yyyy-MM-dd'):
                            hidden = True
                except:
                    hidden = True

            if keywords_filter:
                keywords = keywords_filter.split(',')
                if not any(keyword.lower() in question_text.lower() or keyword.lower() in answer_text.lower() for keyword in keywords):
                    hidden = True

            if status_filter != 'SELECT STATUS':
                if status_filter == 'Answered':
                    if not answer_text:
                        hidden = True
                elif status_filter == 'Unanswered':
                    if answer_text:
                        hidden = True

            if action_filter != 'SELECT ACTION':
                if action_filter.lower() != action_text.lower():
                    hidden = True

            if topic_area_filter != 'SELECT TOPIC AREA':
                if topic_area_filter.lower() != topic_area_text.lower():
                    hidden = True

            # Set row visibility based on filter results
            self.pq_page_table.setRowHidden(row, hidden)

    # This function applies the changes made within the table's action and topic area fields,
    # to the Questions table.
    # It also updates the comments/notes fields of the duplicated questions, informing users
    # of which other team has been allocated this question.

    def apply_changes(self):

        response = self.show_message_box(
            "Confirm", "Are you sure you want to apply the changes?")
        if response != QMessageBox.Yes:
            return

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        for row in range(self.pq_page_table.rowCount()):
            question_id_item = self.pq_page_table.item(row, 0)

            if question_id_item is not None:
                question_id = question_id_item.data(Qt.UserRole)

                action_combo = self.pq_page_table.cellWidget(row, 4)
                topic_area_combo = self.pq_page_table.cellWidget(row, 5)

                action_value = action_combo.currentText() if action_combo else ''
                topic_area_value = topic_area_combo.currentText() if topic_area_combo else ''

                if action_value != 'None' and topic_area_value:
                    cursor.execute("""
                        UPDATE Questions
                        SET advised_action = ?, team_id = ?, allocated_status = 'allocated', phs_relevant = 'Yes', is_updated = 1
                        WHERE question_id = ?
                    """, (action_value, topic_area_value, question_id))

                    # Find all related questions (including the current one)
                    cursor.execute("""
                        SELECT question_id, team_id, advised_action
                        FROM Questions
                        WHERE reference_id = (SELECT reference_id FROM Questions WHERE question_id = ?)
                    """, (question_id,))

                    related_questions = cursor.fetchall()

                    # Update additional_comments for all related questions
                    # This allows for multiple duplications to be considered in the additional comments box
                    for current_id, _, _ in related_questions:
                        other_questions = [
                            q for q in related_questions if q[0] != current_id]
                        additional_comments = [
                            f"the {q[1]} team for {q[2]}" for q in other_questions]

                        if additional_comments:
                            if len(additional_comments) == 1:
                                additional_comment = f"This question has also been sent to {additional_comments[0]}."
                            else:
                                last_comment = additional_comments.pop()
                                additional_comment = f"This question has also been sent to {', '.join(additional_comments)}, and {last_comment}."
                        else:
                            additional_comment = ""

                        cursor.execute("""
                            UPDATE Questions
                            SET additional_comments = ?
                            WHERE question_id = ?
                        """, (additional_comment, current_id))

        connection.commit()
        connection.close()

        self.refresh_function()

    def add_teams_to_combo_box(self):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute("SELECT team_name FROM Teams")
        teams = cursor.fetchall()
        self.team_names = [team[0] for team in teams]

        self.pq_page_select_topic_area_combo_box.addItems(self.team_names)

        connection.close()

    def show_message_box(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        response = msg_box.exec()
        return response
