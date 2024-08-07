'''
This script takes all past PQs from January 2024 till the inception of this application
creates a dataframe from the csv file before and after allocation
conducts basic data manipulation using pandas, and output the master_sheet_updated.csv
'''
import os
import pandas as pd


def create_csv_of_phs_relevant_past_pqs():
    current_directory = os.path.dirname(__file__)
    csv_directory = os.path.join(
        current_directory, '..', 'misc/past_pq_questions/collated')

    master_csv_path = os.path.join(csv_directory, 'master_sheet_updated.csv')

    if os.path.exists(master_csv_path):
        print(f"{master_csv_path} already exists. Skipping data processing.")
        return

    dataframes = []

    # Reads all the csv files in the collated directory
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(csv_directory, filename)

            # Try reading the CSV file with utf-8 encoding
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                # If utf-8 fails, try reading with ISO-8859-1 encoding
                df = pd.read_csv(file_path, encoding='ISO-8859-1')

            # This creats a column called phs_relevant. If the file is allocated, this means
            # the question was phe_relevant, and becomes 'Yes'
            # Later on, phs_relevant = 'No' questions will be removed

            if 'allocated' in filename:
                df['phs_relevant'] = 'Yes'
            else:
                df['phs_relevant'] = 'No'

            # Set default allocated_status to "unallocated"
            df['allocated_status'] = 'unallocated'

            # Update allocated_status to "allocated" if there is an entry in topic_area
            df.loc[df['topic_area'].notna() & (df['topic_area'] != ''),
                   'allocated_status'] = 'allocated'

            dataframes.append(df)

    master_df = pd.concat(dataframes, ignore_index=True)

    duplicate_groups = master_df.groupby(
        'event_id')['phs_relevant'].transform('nunique') > 1

    filtered_df = master_df[~((duplicate_groups) & (
        master_df['phs_relevant'] == 'No'))]

    filtered_df.to_csv(master_csv_path, index=False)
