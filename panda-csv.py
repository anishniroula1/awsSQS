import pandas as pd
import os


def process_csv(file_path):
    try:
        # Check if the file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file at {file_path} does not exist.")

        # Read the CSV file
        df = pd.read_csv(file_path)

        # Check if the required columns exist
        if "student_number" not in df.columns or "date" not in df.columns:
            raise ValueError(
                "The CSV file must contain 'student_number' and 'date' columns."
            )

        # Convert the 'date' column to datetime format
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Drop rows with invalid dates
        df = df.dropna(subset=["date"])

        # Sort by date
        df = df.sort_values(by="date")

        # Drop duplicates to keep the first occurrence (earliest date) for each student number
        unique_students = df.drop_duplicates(subset=["student_number"], keep="first")

        # Select relevant columns
        output_df = unique_students[["student_number", "date"]]

        # Define output file path
        output_file_path = os.path.join(
            os.path.dirname(file_path), "unique_student_numbers_with_dates.csv"
        )

        # Write to a new CSV file
        output_df.to_csv(output_file_path, index=False)

        print(f"Output successfully written to {output_file_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
    except pd.errors.ParserError:
        print("Error: The file is not in a correct CSV format.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Example usage
file_path = "path/to/your/csvfile.csv"
process_csv(file_path)
