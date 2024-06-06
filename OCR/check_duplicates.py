import pandas as pd

# Load the CSV file
df = pd.read_csv("your_file.csv")

filtered_df = df[df["document_category"].isin(["WSE", "WS", "I-589"])]
# Group by student_id and document_category, then count the occurrences
category_counts = (
    filtered_df.groupby(["student_id", "document_category"])
    .size()
    .reset_index(name="count")
)

# Filter to find duplicates (where count > 1)
duplicates = category_counts[category_counts["count"] > 1]

# Calculate the total count of duplicates for each student_id
duplicates["total_duplicates"] = duplicates["count"] - 1

# Sum the total duplicates
total_duplicates = (
    duplicates.groupby("student_id")["total_duplicates"].sum().reset_index()
)

# Display the total duplicates for each student_id
import ace_tools as tools

tools.display_dataframe_to_user(
    name="Total Duplicates by Student ID", dataframe=total_duplicates
)

print(total_duplicates)
