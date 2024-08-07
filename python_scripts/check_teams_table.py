'''
This script checks the Teams table to see if it has been populated.
If not, then it imports the team data.
This script is part of the setup script, and should only be run during setup.
'''

import sqlite3
from creating_database import database_path
from manual_import_teams import import_team_data


def check_teams_table_for_data():
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Teams")
    count = cursor.fetchone()[0]

    if count == 0:
        import_team_data()
    connection.close()
