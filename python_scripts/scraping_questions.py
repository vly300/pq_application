'''The following script first moves the non-phs_relevant questions from the Questions table
to the deleted_questions table. This allows for the scraped questions to be compared to the questions
stored in both of those tables. If it is found in either, it does not insert the scraped question
back into the Questions table.'''

import requests
import sqlite3
from datetime import datetime
from creating_database import database_path


def fetch_questions(api_url):
    response = requests.get(api_url)
    # This raises a HTTPError exception if there are issues.
    response.raise_for_status()
    return response.json()


def update_or_insert_questions(questions, database_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO deleted_questions (question_id, reference_id)
        SELECT question_id, reference_id
        FROM Questions
        WHERE phs_relevant = 'No'
    """)

    cursor.execute("""
        DELETE FROM Questions
        WHERE phs_relevant = 'No'
    """)

    insert_query = '''
    INSERT INTO Questions (
        reference_id, date_submitted, question, answer, 
        allocated_status, team_id, advised_action, additional_comments, phs_relevant, is_updated
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    update_query = '''
    UPDATE Questions
    SET answer = ?, is_updated = 1
    WHERE reference_id = ?
    '''

    for q in questions:
        reference_id = q.get('EventID')
        answer_text = q.get('AnswerText')

        cursor.execute(
            'SELECT reference_id FROM deleted_questions WHERE reference_id = ?', (reference_id,))
        deleted_row = cursor.fetchone()

        if deleted_row:
            continue

        cursor.execute(
            'SELECT answer FROM Questions WHERE reference_id = ?', (reference_id,))
        existing_row = cursor.fetchone()

        if existing_row:
            current_answer = existing_row[0]
            if current_answer != answer_text:
                cursor.execute(update_query, (answer_text, reference_id))
        else:
            cursor.execute(insert_query, (
                # reference_id
                reference_id,
                # date_submitted
                q.get('SubmissionDateTime'),
                # question
                q.get('ItemText'),
                # answer
                answer_text,
                # allocated_status (default is unallocated)
                "unallocated",
                # team_id
                None,
                # advised_action
                None,
                # additional_comments
                None,
                # phs_relevant (default value is TBD for new questions)
                "TBD",
                # is_updated (default value)
                0
            ))

    connection.commit()
    connection.close()


def scrape():
    current_year = datetime.now().year
    api_url = f'https://data.parliament.scot/api/motionsquestionsanswersquestions?year={current_year}'

    # Fetch questions data from the API
    questions = fetch_questions(api_url)

    # Insert or update questions data in the database
    update_or_insert_questions(questions, database_path)
