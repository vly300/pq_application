'''
The following script imports the teams_data_manual.csv
into the teams table in the database.

IMPORTANT: This script should only be run once during the setup.
The teams table in the database will change as the application is used.

If the application is run after the teams table has been changed,
the teams table will revert to its original contents 
'''

import csv
import sqlite3
import os
from creating_database import database_path, current_directory

connection = sqlite3.connect(database_path)
cursor = connection.cursor()
csv_path = os.path.join(current_directory, '..',
                        'misc', 'teams_data_manual.csv')


def import_team_data():

    with open(csv_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)

        for row in csvreader:
            cursor.execute("""
                INSERT INTO teams (team_name)
                VALUES (?)
            """, (row[0],))

    connection.commit()
