'''This script allows you to create a csv file containing all the entries in a chosen
table within the database'''

import sqlite3
import csv
import os
from creating_database import database_path, current_directory


def create_csv():
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # Edit to a table of your choice
    cursor.execute('SELECT * FROM Questions')
    rows = cursor.fetchall()

    csv_file_path = os.path.join(
        current_directory, '..', 'misc', 'Question.csv')  # amend the file name to your choice

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(rows)

    connection.close()


create_csv()
