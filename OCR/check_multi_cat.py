import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_student_categories(df):
    try:
        # Initialize the logging for the processing function
        total_rows = len(df)
        logging.info(f"Starting to process {total_rows} rows.")

        # Ensure 'student - English' is preferred over 'student'
        for idx, row in df.iterrows():
            if row['category'] == 'student' and 'student - English' in df[df['student_id'] == row['student_id']]['category'].values:
                df.at[idx, 'category'] = 'student - English'
            
            # Log progress every 10,000 rows
            if (idx + 1) % 10000 == 0:
                logging.info(f"Processed {idx + 1} of {total_rows} rows.")

        # Drop duplicate categories for each student_id
        df_unique = df.drop_duplicates(subset=['student_id', 'category'])
        return df_unique
    
    except Exception as e:
        logging.error(f"An error occurred while processing the DataFrame: {e}")
        return pd.DataFrame()

def read_and_process_file(file_path):
    try:
        # Read the data from a CSV file
        df = pd.read_csv(file_path)
        
        # Process the DataFrame
        processed_df = process_student_categories(df)
        
        return processed_df
    
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return pd.DataFrame()
    
    except pd.errors.EmptyDataError:
        logging.error(f"No data: {file_path} is empty.")
        return pd.DataFrame()
    
    except pd.errors.ParserError:
        logging.error(f"Parsing error: {file_path} could not be parsed.")
        return pd.DataFrame()
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

def save_to_csv(df, output_file_path):
    try:
        df.to_csv(output_file_path, index=False)
        logging.info(f"Processed data saved to {output_file_path}")
    except Exception as e:
        logging.error(f"An error occurred while saving the DataFrame to CSV: {e}")

# Replace 'input_file.csv' with the actual path to your input CSV file
input_file_path = 'input_file.csv'
# Replace 'output_file.csv' with the desired path for your output CSV file
output_file_path = 'output_file.csv'

# Process the file and save the output
result_df = read_and_process_file(input_file_path)
if not result_df.empty:
    save_to_csv(result_df, output_file_path)
else:
    logging.info("No data to save.")
