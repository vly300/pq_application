'''
This script inserts the PQs from January 2024 till the inception of this application's design 
into the Questions table of the database.

It reads in the master_sheet_updated.csv which has been moved to the misc folder to obtain the past PQs.
'''

import sqlite3
import os
import pandas as pd
from creating_database import database_path


def insert_past_pqs_into_questions_table():
    current_directory = os.path.dirname(__file__)
    csv_directory = os.path.join(current_directory, '..', 'misc')
    master_csv_updated_path = os.path.join(
        csv_directory, 'master_sheet_updated.csv')

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    master_df = pd.read_csv(master_csv_updated_path)

    insert_query = """
    INSERT INTO Questions (reference_id, date_submitted, question, allocated_status, team_id, advised_action, additional_comments, phs_relevant, is_updated)
    VALUES (?,?,?,?,?,?,?,?,?)
    """

    # Insert all questions from master_df into the Questions table, avoiding duplicates
    # Skips the rows if the event_id is empty in order to avoid data input errors

    for _, row in master_df.iterrows():
        if pd.isna(row['event_id']) or row['event_id'].strip() == '':
            continue

        # Check if the row already exists in the Questions table
        check_query = """
        SELECT 1 FROM Questions 
        WHERE reference_id = ? AND date_submitted = ? AND question = ? AND allocated_status = ? 
        AND team_id = ? AND phs_relevant = ?
        """
        cursor.execute(check_query, (
            row['event_id'], row['approved_date'], row['item_text'], row['allocated_status'], row[
                'topic_area'], row['phs_relevant']
        ))
        if cursor.fetchone() is None:

            # If the row does not exist, insert it
            cursor.execute(
                insert_query,
                (
                    row['event_id'], row['approved_date'], row['item_text'], row['allocated_status'], row[
                        'topic_area'], row['action'], row['notes'], row['phs_relevant'], 1
                )
            )

    connection.commit()
    connection.close()
