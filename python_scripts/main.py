'''
Main Python script.
All imports are local in order to relate which function is from which script.
'''


def main():
    print("Starting main function.")
    setup_question = input(
        "Is this the first time you are running this application? Y/N: ")

    if setup_question == "Y" or setup_question == "y":

        print("Creating database. Will not create database if the database is present.")
        from creating_database import create_database
        create_database()

        print("Checking teams table for content - will import teams data if not present.")
        from check_teams_table import check_teams_table_for_data
        check_teams_table_for_data()

        print("Inserting pqs into questions table")
        from insert_past_pqs import insert_past_pqs_into_questions_table
        insert_past_pqs_into_questions_table()

    print("Scraping questions and updating the Questions table.")
    from scraping_questions import scrape
    scrape()

    print("Starting application. Welcome.")
    from login_page import start_application
    start_application()


if __name__ == "__main__":
    print("Executing script as main.")
    main()
