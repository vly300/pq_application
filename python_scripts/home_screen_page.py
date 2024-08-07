'''
This script gives functionality to the Home Screen of the app.
'''
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from user_session import current_session


class home_screen(QDialog):
    def __init__(self, widget):
        super(home_screen, self).__init__()
        self.widget = widget
        loadUi("python_scripts/../GUI_files/home_screen.ui", self)
        self.pqs_sorted = 0
        self.home_screen_all_pqs_push_button.clicked.connect(
            self.all_pqs_function)
        self.home_screen_unallocated_pqs_push_button.clicked.connect(
            self.unallocated_pqs_function)
        self.home_screen_allocated_pqs_push_button.clicked.connect(
            self.allocated_pqs_function)
        self.home_screen_useful_documents_push_button.clicked.connect(
            self.useful_documents_function)
        self.home_screen_settings_push_button.clicked.connect(
            self.settings_function)
        self.home_screen_logout_push_button.clicked.connect(
            self.logout_function)

    # The pqs_sorted value will be used in the next pq_page screen to know how the PQs should be shown.
    def all_pqs_function(self):
        self.pqs_sorted = 1  # 1 indicates that all pqs should be shown
        self.navigate_to_pq_page()

    def unallocated_pqs_function(self):
        self.pqs_sorted = 2  # 2 indicates that only unallocated pqs should be shown
        self.navigate_to_pq_page()

    def allocated_pqs_function(self):
        self.pqs_sorted = 3  # 3 indicates that only allocated pqs should be shown
        self.navigate_to_pq_page()

    def useful_documents_function(self):
        print("useful documents")

    def settings_function(self):
        print("settings")

    def logout_function(self):

        current_session.clear_user()

        from login_page import login
        logins = login(self.widget)
        self.widget.addWidget(logins)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def navigate_to_pq_page(self):
        from pq_page import pqs_page
        allpqs = pqs_page(self.widget, self.pqs_sorted)  # Pass pqs_sorted here
        self.widget.addWidget(allpqs)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
