'''
This script creates the parliamentary_questions database using the 5 sql files listed.
It is unimportant whether this script is run again after setup, as the sql files are set to
only create the tables if the tables do not exist.

For best practise, only run this once during setup.'''

import sqlite3
import os

current_directory = os.path.dirname(__file__)
databases_directory = os.path.join(current_directory, '..', 'databases')
sql_files_directory = os.path.join(current_directory, '..', 'sql_files')
database_path = os.path.join(databases_directory, 'parliamentary_questions.db')


def create_database():

    connection = sqlite3.connect(database_path)

    connection.execute('PRAGMA foreign_keys = ON;')
    connection.execute('PRAGMA defer_foreign_keys = TRUE;')

    cursor = connection.cursor()

    sql_files = ['create_table_deleted_questions.sql',
                 'create_table_teams.sql',
                 'create_table_users.sql',
                 'create_table_questions.sql',
                 'create_table_team_members.sql']

    for sql_file in sql_files:

        sql_file_path = os.path.join(sql_files_directory, sql_file)

        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            cursor.executescript(sql_script)

    connection.commit()
    connection.close()
