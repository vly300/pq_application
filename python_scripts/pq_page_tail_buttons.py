'''
This script details the tail_buttons_delegate class, as well as gives the functionalities for the 
duplicate and remove buttons, which will appear as th Admin user hovers over the comment section
of the question row.
'''

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QPalette
import sqlite3
from creating_database import database_path


class tail_buttons_delegate(QStyledItemDelegate):
    row_removed = pyqtSignal(int)  # Signal to indicate row removal
    # Signal to indicate row insertion
    row_inserted = pyqtSignal(int, tuple, int)

    def __init__(self, parent=None):
        super(tail_buttons_delegate, self).__init__(parent)
        self.hovered_row = None
        self.clicked_button_index = None
        self.clicked_button_type = None

    def paint(self, painter, option, index):  # Design the buttons looks
        if not index.isValid():
            return

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        widget = option.widget
        style = widget.style() if widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)

        if option.state & (QStyle.State_Selected | QStyle.State_MouseOver):
            duplicate_button_option = QStyleOptionButton()
            duplicate_button_option.text = '➕'
            duplicate_button_option.rect = QRect(option.rect.left() + option.rect.width() - (2 * option.rect.height()),
                                                 option.rect.top(), option.rect.height(), option.rect.height())
            duplicate_button_option.state = QStyle.State_Enabled
            if self.clicked_button_index == index and self.clicked_button_type == 'edit':
                duplicate_button_option.palette.setColor(
                    QPalette.Button, QColor(Qt.yellow))
            style.drawControl(QStyle.CE_PushButton,
                              duplicate_button_option, painter, widget)

            remove_button_option = QStyleOptionButton(duplicate_button_option)
            remove_button_option.text = '❌'
            remove_button_option.rect = QRect(option.rect.left() + option.rect.width() - option.rect.height(),
                                              option.rect.top(), option.rect.height(), option.rect.height())
            if self.clicked_button_index == index and self.clicked_button_type == 'remove':
                remove_button_option.palette.setColor(
                    QPalette.Button, QColor(Qt.red))  # Highlight color
            style.drawControl(QStyle.CE_PushButton,
                              remove_button_option, painter, widget)

    # model argument is not used, but is necessary for the editorEvent method
    # connect the buttons to the functions
    def editorEvent(self, event, model, option, index):
        if not index.isValid():
            return False

        if event.type() == QEvent.MouseButtonRelease:
            if option.rect.contains(event.pos()):
                edit_button_rect = QRect(option.rect.left() + option.rect.width() - (2 * option.rect.height()),
                                         option.rect.top(), option.rect.height(), option.rect.height())
                remove_button_rect = QRect(option.rect.left() + option.rect.width() - option.rect.height(),
                                           option.rect.top(), option.rect.height(), option.rect.height())
                if edit_button_rect.contains(event.pos()):
                    self.clicked_button_index = index
                    self.clicked_button_index = 'edit'
                    self.duplicate_button_function(index)
                    return True
                elif remove_button_rect.contains(event.pos()):
                    self.clicked_button_index = index
                    self.clicked_button_type = 'remove'
                    self.remove_button_clicked(index)
                    return True
        elif event.type() == QEvent.MouseMove:
            if option.rect.contains(event.pos()):
                self.hovered_row = index.row()
                self.parent().viewport().update()
        return False

    def duplicate_button_function(self, index):
        item = self.parent().item(index.row(), index.column())
        question_id = item.data(Qt.UserRole)

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # Fetch the original question's details
        cursor.execute("""
            SELECT reference_id, date_submitted, question, answer, allocated_status, team_id, advised_action, additional_comments, phs_relevant, is_updated
            FROM Questions
            WHERE question_id = ?
        """, (question_id,))
        original_question = cursor.fetchone()

        # Insert the duplicate with the new additional_comments
        duplicate_query = """
        INSERT INTO Questions (reference_id, date_submitted, question, answer, allocated_status, team_id, advised_action, additional_comments, phs_relevant, is_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            duplicate_query, (*original_question,))

        connection.commit()
        new_question_id = cursor.lastrowid

        # Fetch details of the new question
        cursor.execute("""
            SELECT reference_id, date_submitted, question, answer, team_id, advised_action, additional_comments
            FROM Questions
            WHERE question_id = ?;
        """, (new_question_id,))
        new_question = cursor.fetchone()

        connection.close()

        print(
            f"Question {question_id} duplicated successfully as question {new_question_id}.")

        # Emit signal to indicate row insertion
        self.row_inserted.emit(index.row() + 1, new_question, new_question_id)

    def remove_button_clicked(self, index):
        item = self.parent().item(index.row(), index.column())
        question_id = item.data(Qt.UserRole)

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # Inserting the removed Question to the deleted_questions table
        # The entries are later used in the scrape() function to see what PQs have been deleted
        # to avoid reinstertion.

        cursor.execute("""
            INSERT INTO deleted_questions (question_id, reference_id)
            SELECT question_id, reference_id
            FROM Questions
            WHERE question_id = ?
        """, (question_id,))

        cursor.execute("""
            DELETE FROM Questions
            WHERE question_id = ?
        """, (question_id,))

        connection.commit()
        connection.close()

        # Emit the signal to remove the row from the table
        self.row_removed.emit(index.row())

        print(
            f"Remove button clicked for question_id {question_id}. Removed from table.")

    def sizeHint(self, option, index):
        baseSize = QStyledItemDelegate.sizeHint(self, option, index)
        return QSize(baseSize.width() + (2 * baseSize.height()), baseSize.height())
